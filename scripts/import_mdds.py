"""
High-Performance MDDS Administrative Hierarchy Ingestion Pipeline
Processes ~650,000 administrative divisions into NeonDB PostgreSQL in Third Normal Form (3NF).
Features:
- Streamed chunking (memory-safe for large CSVs/Excels)
- In-memory hierarchical parent ID caching (zero N+1 lookups)
- Batch multi-row insertions with execute_values
- Quarantine dead-letter log for malformed rows
- Zero leading-zero loss (strict string cast)
"""

import sys
import os
import json
import logging
import time
from typing import Dict, Tuple, Optional
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# -------------------------------------------------------------
# Configuration & Logging
# -------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("mdds_import.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("MDDS_ETL")

QUARANTINE_LOG_PATH = "quarantine_records.jsonl"
BATCH_CHUNK_SIZE = 5000  # Number of village records per bulk INSERT transaction

# Expected column names in MDDS dataset
COL_STATE_CODE = "MDDS STC"
COL_STATE_NAME = "STATE NAME"
COL_DIST_CODE = "MDDS DTC"
COL_DIST_NAME = "DISTRICT NAME"
COL_SUBDIST_CODE = "MDDS Sub_DT"
COL_SUBDIST_NAME = "SUB-DISTRICT NAME"
COL_VILLAGE_CODE = "MDDS PLCN"
COL_VILLAGE_NAME = "Area Name"


def get_db_connection():
    db_url = os.getenv("DIRECT_URL") or os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("Missing DIRECT_URL or DATABASE_URL environment variable.")
    return psycopg2.connect(db_url)


def quarantine_record(row_idx: int, reason: str, record: dict):
    """Write malformed records to dead-letter log."""
    with open(QUARANTINE_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "timestamp": time.time(),
            "row_index": row_idx,
            "error_reason": reason,
            "payload": record
        }) + "\n")


def run_pipeline(source_file_path: str):
    start_time = time.time()
    logger.info(f"Initiating MDDS Data Ingestion from: {source_file_path}")

    conn = get_db_connection()
    conn.autocommit = False
    cursor = conn.cursor()

    try:
        # Phase 1: Ensure Country (India) Exists
        logger.info("Verifying country root record (India)...")
        cursor.execute("""
            INSERT INTO countries (iso_code, name, created_at, updated_at)
            VALUES ('IND', 'India', NOW(), NOW())
            ON CONFLICT (iso_code) DO UPDATE SET updated_at = NOW()
            RETURNING id;
        """)
        country_id = cursor.fetchone()[0]
        conn.commit()
        logger.info(f"Country initialized with ID: {country_id}")

        # In-Memory Cache for Foreign Key Resolution:
        # state_code -> state_uuid
        state_cache: Dict[str, str] = {}
        # (state_uuid, dist_code) -> dist_uuid
        dist_cache: Dict[Tuple[str, str], str] = {}
        # (dist_uuid, subdist_code) -> subdist_uuid
        subdist_cache: Dict[Tuple[str, str], str] = {}

        # Warm caches if existing records exist
        cursor.execute("SELECT mdds_code, id FROM states WHERE country_id = %s;", (country_id,))
        for row in cursor.fetchall():
            state_cache[str(row[0]).strip()] = row[1]

        cursor.execute("SELECT state_id, mdds_code, id FROM districts;")
        for row in cursor.fetchall():
            dist_cache[(row[0], str(row[1]).strip())] = row[2]

        cursor.execute("SELECT district_id, mdds_code, id FROM sub_districts;")
        for row in cursor.fetchall():
            subdist_cache[(row[0], str(row[1]).strip())] = row[2]

        logger.info(f"Pre-cached: {len(state_cache)} States, {len(dist_cache)} Districts, {len(subdist_cache)} SubDistricts")

        # Phase 2 & 3: Streamed Reading & Hierarchical Load
        logger.info("Reading dataset with string dtype to preserve leading zeros...")
        dtype_spec = {
            COL_STATE_CODE: str,
            COL_STATE_NAME: str,
            COL_DIST_CODE: str,
            COL_DIST_NAME: str,
            COL_SUBDIST_CODE: str,
            COL_SUBDIST_NAME: str,
            COL_VILLAGE_CODE: str,
            COL_VILLAGE_NAME: str,
        }

        # Handle CSV or Excel
        if source_file_path.endswith(('.xlsx', '.xls')):
            df_full = pd.read_excel(source_file_path, dtype=dtype_spec)
            chunks = [df_full]
        else:
            chunks = pd.read_csv(source_file_path, dtype=dtype_spec, chunksize=50000, low_memory=False)

        total_villages_inserted = 0
        village_batch_buffer = []

        for chunk_idx, df in enumerate(chunks):
            logger.info(f"Processing chunk {chunk_idx + 1} with {len(df)} rows...")

            for idx, row in df.iterrows():
                # Extract & clean codes
                st_code = str(row.get(COL_STATE_CODE, '')).strip().zfill(2)
                st_name = str(row.get(COL_STATE_NAME, '')).strip().title()

                dt_code = str(row.get(COL_DIST_CODE, '')).strip()
                dt_name = str(row.get(COL_DIST_NAME, '')).strip().title()

                sdt_code = str(row.get(COL_SUBDIST_CODE, '')).strip()
                sdt_name = str(row.get(COL_SUBDIST_NAME, '')).strip().title()

                vil_code = str(row.get(COL_VILLAGE_CODE, '')).strip()
                vil_name = str(row.get(COL_VILLAGE_NAME, '')).strip()

                # Basic validation
                if not vil_code or not vil_name or vil_code == 'nan' or vil_name == 'nan':
                    quarantine_record(idx, "MISSING_VILLAGE_IDENTIFIER", row.to_dict())
                    continue

                # 1. State Resolution
                if st_code not in state_cache:
                    cursor.execute("""
                        INSERT INTO states (mdds_code, name, country_id, created_at, updated_at)
                        VALUES (%s, %s, %s, NOW(), NOW())
                        ON CONFLICT (mdds_code) DO UPDATE SET name = EXCLUDED.name, updated_at = NOW()
                        RETURNING id;
                    """, (st_code, st_name, country_id))
                    state_id = cursor.fetchone()[0]
                    state_cache[st_code] = state_id
                else:
                    state_id = state_cache[st_code]

                # 2. District Resolution
                dist_key = (state_id, dt_code)
                if dist_key not in dist_cache:
                    cursor.execute("""
                        INSERT INTO districts (mdds_code, name, state_id, created_at, updated_at)
                        VALUES (%s, %s, %s, NOW(), NOW())
                        ON CONFLICT (mdds_code) DO UPDATE SET name = EXCLUDED.name, updated_at = NOW()
                        RETURNING id;
                    """, (dt_code, dt_name, state_id))
                    dist_id = cursor.fetchone()[0]
                    dist_cache[dist_key] = dist_id
                else:
                    dist_id = dist_cache[dist_key]

                # 3. SubDistrict Resolution
                subdist_key = (dist_id, sdt_code)
                if subdist_key not in subdist_cache:
                    cursor.execute("""
                        INSERT INTO sub_districts (mdds_code, name, district_id, created_at, updated_at)
                        VALUES (%s, %s, %s, NOW(), NOW())
                        ON CONFLICT (mdds_code) DO UPDATE SET name = EXCLUDED.name, updated_at = NOW()
                        RETURNING id;
                    """, (sdt_code, sdt_name, dist_id))
                    subdist_id = cursor.fetchone()[0]
                    subdist_cache[subdist_key] = subdist_id
                else:
                    subdist_id = subdist_cache[subdist_key]

                # 4. Village Buffer
                village_batch_buffer.append((vil_code, vil_name, subdist_id))

                # Flush Village batch
                if len(village_batch_buffer) >= BATCH_CHUNK_SIZE:
                    execute_values(cursor, """
                        INSERT INTO villages (mdds_code, name, sub_district_id, created_at, updated_at)
                        VALUES %s
                        ON CONFLICT (mdds_code) DO UPDATE 
                        SET name = EXCLUDED.name, sub_district_id = EXCLUDED.sub_district_id, updated_at = NOW();
                    """, [(v[0], v[1], v[2]) for v in village_batch_buffer], template="(%s, %s, %s, NOW(), NOW())")
                    conn.commit()
                    total_villages_inserted += len(village_batch_buffer)
                    village_batch_buffer.clear()
                    logger.info(f"Committed {total_villages_inserted} village records...")

        # Flush residual villages
        if village_batch_buffer:
            execute_values(cursor, """
                INSERT INTO villages (mdds_code, name, sub_district_id, created_at, updated_at)
                VALUES %s
                ON CONFLICT (mdds_code) DO UPDATE 
                SET name = EXCLUDED.name, sub_district_id = EXCLUDED.sub_district_id, updated_at = NOW();
            """, [(v[0], v[1], v[2]) for v in village_batch_buffer], template="(%s, %s, %s, NOW(), NOW())")
            conn.commit()
            total_villages_inserted += len(village_batch_buffer)
            village_batch_buffer.clear()

        # Phase 4: Verification & Query Optimization
        logger.info("Executing post-ingestion verification check...")
        cursor.execute("""
            SELECT count(*) FROM villages v
            LEFT JOIN sub_districts sd ON v.sub_district_id = sd.id
            WHERE sd.id IS NULL;
        """)
        orphans = cursor.fetchone()[0]
        if orphans > 0:
            logger.error(f"Integrity Alert: {orphans} orphaned villages detected!")
        else:
            logger.info("Integrity Verified: 0 orphaned village records.")

        logger.info("Updating PostgreSQL optimizer statistics (ANALYZE)...")
        cursor.execute("ANALYZE villages;")
        cursor.execute("ANALYZE sub_districts;")
        conn.commit()

        elapsed = time.time() - start_time
        logger.info(f"ETL Execution Successfully Completed in {elapsed:.2f}s.")
        logger.info(f"Summary: {len(state_cache)} States | {len(dist_cache)} Districts | {len(subdist_cache)} SubDistricts | {total_villages_inserted} Villages")

    except Exception as e:
        conn.rollback()
        logger.exception(f"Fatal exception encountered during ETL: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_mdds.py <path_to_mdds_file.csv_or_xlsx>")
        sys.exit(1)
    run_pipeline(sys.argv[1])
