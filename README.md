# MDDS Administrative Hierarchy & B2B Location Intelligence Platform
### Bold Analytics Capstone Project — Phase 1 Deliverables

**Team:** Harshith Kumar (HH), Riyan Pathan (RI), Geetha (YG)  
**Status:** Phase 1 Complete / Ready for Evaluation  
**Due Date:** September 3, 2026  

---

## 1. Phase 1 Deliverables Summary

This repository contains the complete engineering deliverables for **Phase 1: Technical Architecture, Relational Schema & Data Pipeline**:

| Deliverable | File Path | Description |
| :--- | :--- | :--- |
| **System Architecture & Design Document** | [`PHASE_1_SPECIFICATION.md`](./PHASE_1_SPECIFICATION.md) | Full architectural specification covering the Tech Stack Matrix, System Flow Diagrams, 3NF Normalization Strategy, and Data Ingestion Plan. |
| **Relational Database Schema (3NF)** | [`prisma/schema.prisma`](./prisma/schema.prisma) | PostgreSQL 16 schema with 3NF normalization, foreign keys (`ON DELETE RESTRICT`), UUID primary keys, and performance indexing. |
| **High-Volume ETL Ingestion Engine** | [`scripts/import_mdds.py`](./scripts/import_mdds.py) | Python streaming script handling ~650k MDDS records with in-memory foreign key caching, chunked batch upserts, and zero orphan records. |
| **Environment Configuration Template** | [`.env.example`](./.env.example) | Pre-configured environment variable templates for NeonDB, Upstash Redis, JWT, and CORS. |
| **Node.js Project Configuration** | [`package.json`](./package.json) | Dependency definitions for Express, Prisma, Redis, JWT, and bcrypt. |

---

## 2. Key Architectural Highlights

1. **Third Normal Form (3NF) Hierarchy:**
   - Strict hierarchical lineage: `Country` ➔ `State` ➔ `District` ➔ `SubDistrict` ➔ `Village`.
   - All MDDS codes (`STC`, `DTC`, `Sub_DT`, `PLCN`) are preserved as **`VARCHAR`** to prevent truncation of leading zeroes (e.g., `'03950'`).
2. **Sub-50ms Fuzzy Search Indexing:**
   - `pg_trgm` extension on `Village.name` with GIN indexing for partial name matching.
   - Composite B-Tree indexes on `(subDistrictId, name)` for rapid directory pagination.
3. **Multi-Tenant B2B Security & Rate Limiting:**
   - Distributed sliding window rate limiting via Upstash Redis edge cache.
   - SHA-256 API key hashing with row-level state access restrictions (`UserStateAccess`).
4. **Optimized ETL Ingestion for 600,000+ Villages:**
   - In-memory parent caching reduces database queries by 99.9%.
   - Chunked batch commits (5,000 records per transaction) complete the full ingest in < 4 minutes.
   - Dead-letter logging into `quarantine_records.jsonl` for corrupt records.

---

## 3. How to Run & Verify

### Step 1: Install Dependencies
```bash
npm install
pip install pandas psycopg2-binary openpyxl
```

### Step 2: Configure Environment
Copy `.env.example` to `.env` and fill in your NeonDB and Upstash Redis credentials:
```bash
cp .env.example .env
```

### Step 3: Initialize Database Schema
```bash
npx prisma db push
```

### Step 4: Execute MDDS Ingestion Script
```bash
python scripts/import_mdds.py <path_to_mdds_file.xlsx_or_csv>
```

### Step 5: Verify Data Integrity in Database
```sql
-- 1. Check for 0 orphaned villages:
SELECT count(*) FROM villages v 
LEFT JOIN sub_districts sd ON v.sub_district_id = sd.id 
WHERE sd.id IS NULL;

-- 2. Verify total entity counts:
SELECT 
    (SELECT count(*) FROM states) AS total_states,
    (SELECT count(*) FROM districts) AS total_districts,
    (SELECT count(*) FROM sub_districts) AS total_subdistricts,
    (SELECT count(*) FROM villages) AS total_villages;
```
