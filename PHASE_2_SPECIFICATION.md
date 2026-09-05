# Engineering Design Document: Phase 2 API Development, Dashboard & Portal Specification

**Project:** MDDS Administrative Hierarchy & B2B Location Intelligence Platform  
**Document Version:** 2.0.0  
**Phase:** Phase 2 — API Gateway, Admin Panel, B2B Portal & Demo Client  
**Due Date:** September 11, 2026  
**Status:** In Progress (Active)  
**Assigned Engineers:** Harshith Kumar (HH), Riyan Pathan (RI), Geetha (YG)

---

## 6. API Development Specifications

### 6.1 Base URL Topology
| Environment | Base URL | Purpose |
| :--- | :--- | :--- |
| **Production** | `https://api.villageapi.com/v1/` | High-availability global Anycast edge deployment |
| **Staging** | `https://staging-api.villageapi.com/v1/` | Pre-release QA and integration testing |
| **Local Development** | `http://localhost:3000/v1/` | Local serverless mock and test environment |

### 6.2 Authentication & Security Credentials
- **Public & Read Endpoints:** Requires header `X-API-Key: {api_key}`.
- **Write Operations (POST, PUT, DELETE, PATCH):** Requires both:
  - Header: `X-API-Key: {api_key}`
  - Header: `X-API-Secret: {api_secret}`
- **Key Syntax:**
  - API Key: `ak_[32 hex characters]` (e.g. `ak_a1b2c3d4e5f67890abcdef12345678`)
  - API Secret: `as_[32 hex characters]` (e.g. `as_1234567890abcdef1234567890abcdef`)
- **Presentation Demo Key:** `demo_public_key_for_presentations` (Read-only, 100 req/day quota, scoped strictly to Maharashtra state data).

### 6.3 Standard JSON Response Envelope
Every 2xx API response adheres strictly to this uniform envelope:
```json
{
  "success": true,
  "count": 25,
  "data": [ ... ],
  "meta": {
    "requestId": "req_ad7b5b3fb8bd",
    "responseTime": 12,
    "rateLimit": {
      "remaining": 4850,
      "limit": 5000,
      "reset": "2026-09-12T00:00:00.000Z"
    }
  }
}
```

### 6.4 API Endpoints Specification
| HTTP Method | Endpoint | Query Parameters | Description |
| :--- | :--- | :--- | :--- |
| **GET** | `/v1/search` | `q` (min 2 chars), `state`, `district`, `subDistrict`, `limit` | Full-text and filtered search across all revenue villages. |
| **GET** | `/v1/states` | None | Lists all states and union territories with codes and country identifiers. |
| **GET** | `/v1/states/{id}/districts` | None | Resolves administrative districts belonging to a specific state. |
| **GET** | `/v1/districts/{id}/subdistricts`| None | Resolves Talukas / Tehsils / Blocks within a district. |
| **GET** | `/v1/subdistricts/{id}/villages` | `page`, `limit` | Paginated revenue villages within a sub-district. |
| **GET** | `/v1/autocomplete` | `q` (min 2 chars), `hierarchyLevel` | High-speed typeahead endpoint returning structured dropdown objects. |

### 6.5 Response Format for UI Drop-Down Menus
The `/v1/autocomplete` endpoint formats response objects specifically for frontend select components:
```json
{
  "value": "vil_525002",
  "label": "Manibeli",
  "fullAddress": "Manibeli, Akkalkuwa, Nandurbar, Maharashtra, India",
  "hierarchy": {
    "village": "Manibeli",
    "subDistrict": "Akkalkuwa",
    "district": "Nandurbar",
    "state": "Maharashtra",
    "country": "India"
  }
}
```

### 6.6 Standardized Error Handling Matrix
Failed requests return an appropriate HTTP status code and structured JSON error envelope:
```json
{
  "success": false,
  "error": {
    "code": "INVALID_QUERY",
    "message": "Search query too short or invalid. Minimum 2 characters required."
  },
  "meta": {
    "requestId": "req_8e4b10fa",
    "responseTime": 2
  }
}
```

| HTTP Status | Error Code | Trigger Condition & Description |
| :--- | :--- | :--- |
| **400 Bad Request** | `INVALID_QUERY` | Search parameter `q` is missing or shorter than 2 characters. |
| **401 Unauthorized** | `INVALID_API_KEY` | `X-API-Key` is missing, inactive, revoked, or format is invalid. |
| **403 Forbidden** | `ACCESS_DENIED` | Client API key is not entitled to access the requested State via `UserStateAccess`. |
| **404 Not Found** | `NOT_FOUND` | Requested geographic entity identifier does not exist. |
| **429 Too Many Requests** | `RATE_LIMITED` | Daily quota exceeded or burst limit (>100 req/min) violated. |
| **500 Internal Error** | `INTERNAL_ERROR` | Unhandled server-side exception; sanitized error returned to client. |

---

## 7. Frontend Dashboard Architecture

### 7.1 Technology Stack Selection
- **Framework:** React 18+ with TypeScript for strict type checking on API contracts.
- **Build Tool:** Vite for lightning-fast HMR and optimized tree-shaking.
- **Styling:** Tailwind CSS for design system consistency and minimal bundle footprint.
- **Data Visualization:** Recharts for declarative, responsive SVG charts.
- **Global State:** Zustand for lightweight, boilerplate-free state stores.
- **Server Cache:** TanStack React Query with automated background refetching and request deduplication.

### 7.2 UI Layout & Navigation Architecture
```
┌────────────────────────────────────────────────────────────────────────┐
│ Top Bar: [Logo / Breadcrumb]                [Notifications] [User Profile] │
├───────────────┬────────────────────────────────────────────────────────┤
│ Collapsible   │ Main Viewport:                                         │
│ Sidebar:      │ ┌────────────────────────────────────────────────────┐ │
│ • Analytics   │ │ Metric Summary Cards (Active Users, Quotas, P95)   │ │
│ • Users       │ └────────────────────────────────────────────────────┘ │
│ • State Access│ ┌────────────────────────────────────────────────────┐ │
│ • Village Data│ │ Recharts Visualizations (Area / Bar / Line Charts) │ │
│ • API Logs    │ └────────────────────────────────────────────────────┘ │
│ • Key Manager │ ┌────────────────────────────────────────────────────┐ │
│ • Settings    │ │ Data Table (Sortable, Filterable, CSV Export)      │ │
│               │ └────────────────────────────────────────────────────┘ │
└───────────────┴────────────────────────────────────────────────────────┘
```

### 7.3 Performance SLA Standards
- **Initial First Contentful Paint (FCP):** < 1.5 seconds.
- **Chart Re-render Latency:** < 500ms on viewport resize.
- **Table Pagination & Filtering:** < 300ms via React Query in-memory cache.
- **Optimistic UI:** Instant toggle states on user approvals and key revocations.

---

## 8. Admin Panel Specifications

### 8.1 Dashboard Analytics Visualizations (Recharts)
| Chart Component | Data Displayed | Aggregation / Update Frequency |
| :--- | :--- | :--- |
| **Bar Chart** | Top 10 States ranked by total revenue village count | Daily batch aggregation |
| **Line Chart** | 30-Day API traffic volume trends | Real-time / hourly rolling |
| **Pie / Donut Chart** | B2B User distribution across tiers (Free, Premium, Pro, Unlimited) | Hourly sync |
| **Area Chart** | Latency trends (p95 and p99 response time in ms) | Real-time rolling 24-hour window |
| **Stacked Bar Chart** | Request breakdown grouped by endpoint (`/search`, `/autocomplete`, etc.) | Daily |
| **Usage Heatmap** | Request concentration by hour of day (00:00 - 23:00) | Real-time sliding window |

### 8.2 User Approval & Account Lifecycle
1. **Self-Registration Submission:** User registers with validated corporate email.
2. **Pending Queue:** Account initialized with status `PENDING_APPROVAL`; key creation locked.
3. **Admin Review Interface:** Admin reviews business registration, company name, and GST.
4. **Approval Action:** Admin clicks Approve; user status transitions to `ACTIVE`, and automated onboarding email triggers.
5. **Key Generation Unlocked:** User can now access the portal and generate production credentials.

### 8.3 State Access Matrix (Regional Entitlement)
Admin can scope client keys using three operational modes:
- **Mode 1 (Full Access):** Grant access to all 36 States/UTs.
- **Mode 2 (Granular Selection):** Select specific States (e.g. Maharashtra, Gujarat, Karnataka).
- **Mode 3 (Regional Bundles):** Grant by geographical zones (North, South, East, West).

### 8.4 Village Master Browser (Administrative Explorer)
- Dependent dropdown hierarchy: `State` ➔ `District` ➔ `SubDistrict` ➔ `Village`.
- Pagination configurations: `500`, `5,000`, `10,000` rows per page.
- Direct CSV / Excel export of filtered administrative lists.

### 8.5 Telemetry & API Log Viewer
- Columns: Timestamp (ISO), Masked Key (`ak_****abcd`), User Organization, Endpoint, Latency (ms), HTTP Status, Client IP (masked).
- Filtering: By status code ranges (`2xx`, `4xx`, `5xx`), endpoint path, latency thresholds, and date ranges.

---

## 9. B2B User Portal Specifications

### 9.1 Corporate Self-Registration Guardrails
- **Disposable Email Filter:** Free domains (`@gmail.com`, `@yahoo.com`, `@hotmail.com`) are rejected at form validation.
- **Business Details:** Company Name, Phone, and optional GSTIN.
- **Password Strength:** Minimum 8 characters with lowercase, uppercase, number, and special character requirements.

### 9.2 Cryptographic API Key Management
- **One-Time Secret Display:** Upon generation, the secret (`as_[32 hex]`) is displayed once in a modal with an explicit warning.
- **Bcrypt Hashing:** Secrets are hashed with bcrypt (cost factor 10) prior to storage; plaintext secrets are never written to disk or logs.
- **Key Limits:** Maximum 5 active keys per organization.
- **Instant Revocation:** Revoking a key sets `is_active = false` and evicts the key from the Upstash Redis cache immediately.

---

## 10. Authentication & Security Architecture

### 10.1 Multi-Layer Authentication Stack
| Layer | Authentication Mechanism | TTL / Rotation Policy |
| :--- | :--- | :--- |
| **Portal Sessions** | Stateless JWT (RS256 / HS256) | 24-hour expiration; refreshed via secure HTTP-only cookies |
| **B2B Programmatic API** | `X-API-Key` + `X-API-Secret` | API keys persistent until revoked; secret verified via bcrypt |
| **Admin Operations** | JWT + TOTP Two-Factor Authentication (2FA) | Mandatory for user approvals, plan overrides, and global deletions |

### 10.2 Mandatory Security Headers
Every response includes hardened HTTP headers:
```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
```

---

## 11. Rate Limiting & Tier Management

### 11.1 Tier Matrix & Quotas
| Tier | Pricing | Daily Quota | Burst Limit (/min) | Permitted Scope |
| :--- | :--- | :--- | :--- | :--- |
| **Free** | $0/mo | 5,000 req/day | 100 req/min | Single State access |
| **Premium** | $49/mo | 50,000 req/day | 500 req/min | Up to 5 States |
| **Pro** | $199/mo | 300,000 req/day | 2,000 req/min | All States, Priority SLA |
| **Unlimited** | $499/mo | 1,000,000 req/day | 5,000 req/min | Dedicated compute, custom SLA |
| *Demo Key* | Public | 100 req/day | 30 req/min | Maharashtra State only |

### 11.2 Rate Limit Headers
```http
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 4850
X-RateLimit-Reset: 1705276800
```

---

## 12. Deployment Topology (Vercel & NeonDB)

### 12.1 Project Directory Structure
```
project-root/
├── api/
│   └── index.js              # Vercel serverless function entrypoint
├── src/
│   ├── server.js             # Core Express application
│   ├── middleware/           # auth, rateLimit, security, responseEnvelope
│   └── routes/               # hierarchy, admin, auth, b2b
├── demo-client/
│   └── index.html            # Standalone B2B contact form reference app
├── prisma/
│   └── schema.prisma         # 3NF Database Schema
└── vercel.json               # Serverless rewrites and header definitions
```

### 12.2 Multi-Stage Environment Progression
1. **Preview Deployments:** Automatic deployment on every GitHub Pull Request (`{pr}.vercel.app`).
2. **Staging Environment:** Target `staging-api.villageapi.com` for pre-release integration tests.
3. **Production Anycast Edge:** Target `api.villageapi.com` connected to NeonDB pooled connection string.

---

## 13. Reference Implementation: Demo Client Project

A separate, standalone customer-facing web application located in `demo-client/index.html` showcases address auto-completion:
1. User types in the **Village / Locality** input field (minimum 2 characters).
2. The client queries `GET /v1/autocomplete?q={query}` using the public demo key (`demo_public_key_for_presentations`).
3. The dropdown displays matching options: `Manibeli (Akkalkuwa, Nandurbar, Maharashtra, India)`.
4. Upon selection, **Sub-District**, **District**, **State**, and **Country** auto-fill instantly.
5. Form submission sends clean, standardized geographic coordinates and codes.

---

## 14. Phase 2 Verification & Acceptance Gate

- [x] All 6 core endpoints implemented and tested (`/states`, `/districts`, `/subdistricts`, `/villages`, `/search`, `/autocomplete`).
- [x] Standard response envelope validated with `requestId`, `responseTime`, and `rateLimit`.
- [x] Section 6.5 Dropdown Autocomplete Schema verified with exact field structure.
- [x] Error status codes (400, 401, 403, 404, 429) verified with automated test suite.
- [x] Security headers and rate limiting headers validated.
- [x] Demo client reference implementation built and ready to demonstrate live.
- [x] Automated test runner (`python scripts/test_phase2_apis.py`) passes with **100% success**.
