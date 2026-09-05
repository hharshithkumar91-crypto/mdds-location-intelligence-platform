"""
Local Pipeline & Schema Verification Runner
Validates:
1. 3NF Schema integrity (Country -> State -> District -> SubDistrict -> Village)
2. MDDS leading zero preservation (e.g. SubDistrict '03950')
3. Zero-orphan foreign key joins
4. Hierarchical resolution & summary counts
"""

import sqlite3
import pandas as pd
import uuid
import sys
import os

# Ensure safe console output across all Windows encodings
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB_PATH = "test_verification.db"
SAMPLE_DATA_PATH = os.path.join("data", "sample_mdds.csv")


def run_verification():
    print("=" * 70)
    print("STARTING MDDS PIPELINE & RELATIONAL INTEGRITY VERIFICATION")
    print("=" * 70)

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Initialize 3NF Schema
    print("\n[Step 1] Creating 3NF Relational Tables...")
    cursor.executescript("""
        CREATE TABLE countries (
            id TEXT PRIMARY KEY,
            iso_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL
        );

        CREATE TABLE states (
            id TEXT PRIMARY KEY,
            mdds_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            country_id TEXT NOT NULL,
            FOREIGN KEY (country_id) REFERENCES countries(id)
        );

        CREATE TABLE districts (
            id TEXT PRIMARY KEY,
            mdds_code TEXT NOT NULL,
            name TEXT NOT NULL,
            state_id TEXT NOT NULL,
            UNIQUE(state_id, mdds_code),
            FOREIGN KEY (state_id) REFERENCES states(id)
        );

        CREATE TABLE sub_districts (
            id TEXT PRIMARY KEY,
            mdds_code TEXT NOT NULL,
            name TEXT NOT NULL,
            district_id TEXT NOT NULL,
            UNIQUE(district_id, mdds_code),
            FOREIGN KEY (district_id) REFERENCES districts(id)
        );

        CREATE TABLE villages (
            id TEXT PRIMARY KEY,
            mdds_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            sub_district_id TEXT NOT NULL,
            FOREIGN KEY (sub_district_id) REFERENCES sub_districts(id)
        );
    """)
    print("  [OK] Tables initialized: countries, states, districts, sub_districts, villages")

    # 2. Ingest Root Country
    country_id = str(uuid.uuid4())
    cursor.execute("INSERT INTO countries VALUES (?, ?, ?)", (country_id, "IND", "India"))
    conn.commit()
    print(f"  [OK] Root country registered: India (ISO: IND, ID: {country_id[:8]}...)")

    # 3. Read Dataset with strict string typing
    print(f"\n[Step 2] Ingesting test dataset: {SAMPLE_DATA_PATH}...")
    dtype_spec = {
        "MDDS STC": str,
        "STATE NAME": str,
        "MDDS DTC": str,
        "DISTRICT NAME": str,
        "MDDS Sub_DT": str,
        "SUB-DISTRICT NAME": str,
        "MDDS PLCN": str,
        "Area Name": str,
    }
    df = pd.read_csv(SAMPLE_DATA_PATH, dtype=dtype_spec)
    print(f"  ✓ Loaded {len(df)} sample records successfully.")

    state_cache = {}
    dist_cache = {}
    subdist_cache = {}
    villages_inserted = 0

    for _, row in df.iterrows():
        st_code = str(row["MDDS STC"]).strip().zfill(2)
        st_name = str(row["STATE NAME"]).strip().title()

        dt_code = str(row["MDDS DTC"]).strip()
        dt_name = str(row["DISTRICT NAME"]).strip().title()

        sdt_code = str(row["MDDS Sub_DT"]).strip()
        sdt_name = str(row["SUB-DISTRICT NAME"]).strip().title()

        vil_code = str(row["MDDS PLCN"]).strip()
        vil_name = str(row["Area Name"]).strip()

        # State
        if st_code not in state_cache:
            st_id = str(uuid.uuid4())
            cursor.execute("INSERT INTO states VALUES (?, ?, ?, ?)", (st_id, st_code, st_name, country_id))
            state_cache[st_code] = st_id
        else:
            st_id = state_cache[st_code]

        # District
        dist_key = (st_id, dt_code)
        if dist_key not in dist_cache:
            dt_id = str(uuid.uuid4())
            cursor.execute("INSERT INTO districts VALUES (?, ?, ?, ?)", (dt_id, dt_code, dt_name, st_id))
            dist_cache[dist_key] = dt_id
        else:
            dt_id = dist_cache[dist_key]

        # SubDistrict
        sdt_key = (dt_id, sdt_code)
        if sdt_key not in subdist_cache:
            sdt_id = str(uuid.uuid4())
            cursor.execute("INSERT INTO sub_districts VALUES (?, ?, ?, ?)", (sdt_id, sdt_code, sdt_name, dt_id))
            subdist_cache[sdt_key] = sdt_id
        else:
            sdt_id = subdist_cache[sdt_key]

        # Village
        vil_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO villages VALUES (?, ?, ?, ?)", (vil_id, vil_code, vil_name, sdt_id))
        villages_inserted += 1

    conn.commit()
    print(f"  [OK] Ingestion complete: {villages_inserted} villages processed.")

    # 4. Integrity Checks
    print("\n[Step 3] Running Automated Integrity Checks...")

    # Check 1: Leading zero preservation in SubDistrict
    cursor.execute("SELECT mdds_code, name FROM sub_districts WHERE name = 'Akkalkuwa';")
    sub_code, sub_name = cursor.fetchone()
    assert sub_code == "03950", f"Leading zero corrupted! Expected '03950', got '{sub_code}'"
    print(f"  [PASS] Leading Zero Validation: SubDistrict '{sub_name}' code preserved as '{sub_code}'")

    # Check 2: Orphan Records
    cursor.execute("""
        SELECT count(*) FROM villages v
        LEFT JOIN sub_districts sd ON v.sub_district_id = sd.id
        WHERE sd.id IS NULL;
    """)
    orphans = cursor.fetchone()[0]
    assert orphans == 0, f"Integrity Failure: Found {orphans} orphaned villages"
    print("  [PASS] Foreign Key Integrity: 0 orphaned village records")

    # Check 3: Hierarchy Tree Query
    print("\n[Step 4] Querying Resolved Hierarchical Lineage:")
    cursor.execute("""
        SELECT 
            s.name AS state, 
            d.name AS district, 
            sd.mdds_code AS subdist_code,
            sd.name AS subdistrict, 
            v.mdds_code AS village_code,
            v.name AS village
        FROM villages v
        JOIN sub_districts sd ON v.sub_district_id = sd.id
        JOIN districts d ON sd.district_id = d.id
        JOIN states s ON d.state_id = s.id
        ORDER BY s.name, d.name, v.mdds_code;
    """)
    rows = cursor.fetchall()

    print(f"  {'State':<14} | {'District':<12} | {'SubDist (Code)':<22} | {'Village (Code)':<22}")
    print("  " + "-" * 76)
    for r in rows:
        print(f"  {r[0]:<14} | {r[1]:<12} | {r[3]} ({r[2]}){'':<5} | {r[5]} ({r[4]})")

    print("\n[Step 5] Aggregate Entity Verification Counts:")
    cursor.execute("SELECT count(*) FROM states;")
    n_states = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM districts;")
    n_dist = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM sub_districts;")
    n_subdist = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM villages;")
    n_vil = cursor.fetchone()[0]

    print(f"  - Total States Ingested:        {n_states}")
    print(f"  - Total Districts Ingested:     {n_dist}")
    print(f"  - Total Sub-Districts Ingested: {n_subdist}")
    print(f"  - Total Villages Ingested:      {n_vil}")

    conn.close()
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    print("\n" + "=" * 70)
    print("[SUCCESS] ALL INTEGRITY & HIERARCHY VERIFICATION CHECKS PASSED (100%)")
    print("=" * 70)


if __name__ == "__main__":
    run_verification()
