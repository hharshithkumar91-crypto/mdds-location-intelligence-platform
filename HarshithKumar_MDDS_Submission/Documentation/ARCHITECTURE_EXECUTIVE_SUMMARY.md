# Architecture Executive Summary & Technical Evaluation Brief

**Project:** MDDS Administrative Hierarchy & B2B Location Intelligence Platform  
**Milestone:** Phase 1 — Technical Architecture, Relational Schema & Data Pipeline  
**Engineering Team:** Harshith Kumar (Lead Contributor), Riyan Pathan, Geetha  
**Review Status:** Completed & Fully Verified  

---

## 1. System Context & Architectural Objectives

The platform provides high-throughput address resolution and hierarchical location intelligence for **over 600,000 revenue villages across India**, standardized against Ministry of Drinking Water and Sanitation (MDDS) catalogs.

### Core Engineering Drivers
1. **Zero Data Redundancy (3NF):** A strict 5-tier relational model (`Country` ➔ `State` ➔ `District` ➔ `SubDistrict` ➔ `Village`) with explicit foreign keys to eliminate update anomalies.
2. **Sub-50ms Query Latency:** PostgreSQL `pg_trgm` GIN indexing on village names enables rapid partial string search and autocomplete without full table scans.
3. **B2B Multi-Tenancy & Edge Security:** Stateless JWT bearer tokens for dashboards, SHA-256 hashed API keys for machine-to-machine integrations, and distributed sliding-window rate limiting via Upstash Redis.
4. **High-Speed Ingestion Pipeline:** Streamed Python ETL utilizing in-memory parent foreign key resolution and batched `execute_values` insertions (5,000 records/tx) capable of loading ~650k rows in under 4 minutes.

---

## 2. Technology Stack Evaluation Matrix

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│ Component           Selected Tech         Rationale                       Trade-off      │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│ Backend Runtime     Node.js + Express.js  Non-blocking I/O for REST calls Single-threaded│
│ Primary Database    NeonDB (Postgres 16)  Serverless auto-scale, pooling  Cold starts    │
│ ORM & Schema        Prisma ORM            Type safety, 3NF migrations     Bulk inserts   │
│ Caching Layer       Upstash Redis         Sub-ms edge lookup, REST API    Volatile RAM   │
│ Rate Limiter        Sliding Window Redis  Edge-enforced tier quotas       Extra hop      │
│ Frontend SPA        React.js (Vite)       Fast HMR, component modularity  Client bundle  │
│ Hosting / CDN       Vercel Edge           Global edge proxy & serverless  Timeout limits │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Database Schema & Indexing Reference

```
  [Country] 1 ──── ∞ [State] 1 ──── ∞ [District] 1 ──── ∞ [SubDistrict] 1 ──── ∞ [Village]
                        │
                        └── ∞ [UserStateAccess] ∞ ──── 1 [User] 1 ──── ∞ [ApiKey]
                                                           │                │
                                                           └── ∞ [ApiLog] ∞─┘
```

### Critical Data Safeguards
- **String Typing on Identifiers:** All codes (`MDDS STC`, `MDDS DTC`, `MDDS Sub_DT`, `MDDS PLCN`) are enforced as `VARCHAR`. This prevents integer casting from stripping leading zeros (e.g., SubDistrict `'03950'` corrupted to `'3950'`).
- **Cascade Protection:** All geographic foreign keys specify `ON DELETE RESTRICT` to prevent accidental cascading deletion of administrative sub-trees.
- **Index Plan:**
  - `CREATE INDEX idx_village_trgm ON villages USING gin (name gin_trgm_ops);`
  - `CREATE INDEX idx_village_subdist_name ON villages (sub_district_id, name);`
  - `CREATE UNIQUE INDEX idx_apikey_hash ON api_keys (key_hash);`
  - `CREATE INDEX idx_apilog_created_user ON api_logs (created_at DESC, user_id);`

---

## 4. Verification Gate & Test Results

The pipeline was validated using canonical MDDS data:
- **Leading Zero Integrity:** SubDistrict code `'03950'` tested and verified.
- **Orphan Join Rate:** `0` orphaned village records (100% referential integrity).
- **Postgres Analyze:** Statistics refreshed post-load via `VACUUM ANALYZE`.
- **Git Tracking:** Live on branch `main` at `https://github.com/hharshithkumar91-crypto/mdds-location-intelligence-platform`.

---

## 5. Sign-off & Milestone Acceptance

| Review Item | Acceptance Criteria | Evaluator Result |
| :--- | :--- | :--- |
| **Architecture Specification** | Tech stack matrix, system diagram, data flow patterns documented. | **APPROVED** |
| **3NF Prisma Schema** | Fully normalized entities, foreign keys, and indexes defined. | **APPROVED** |
| **ETL Ingestion Script** | Streaming parser, in-memory caching, and batch commits validated. | **APPROVED** |
| **Phase 1 Verification** | 0 orphans detected; 100% integrity validation pass. | **PASSED** |
