"""
Executive-Grade PowerPoint Generator for Bold Analytics Capstone Phase 1
Produces a 16:9 Widescreen Presentation (.pptx) with modern typography, card containers,
metrics badges, structured tables, and speaker notes.
"""

import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Design Tokens (Slate Navy & Royal Blue Corporate Palette)
COLOR_BG = RGBColor(15, 23, 42)          # #0F172A (Deep Slate)
COLOR_CARD = RGBColor(30, 41, 59)        # #1E293B (Card Slate)
COLOR_CARD_BORDER = RGBColor(51, 65, 85) # #334155
COLOR_PRIMARY = RGBColor(37, 99, 235)    # #2563EB (Electric Royal Blue)
COLOR_ACCENT = RGBColor(96, 165, 250)    # #60A5FA (Light Sky Blue)
COLOR_TEXT_WHITE = RGBColor(248, 250, 252) # #F8FAFC
COLOR_TEXT_MUTED = RGBColor(148, 163, 184) # #94A3B8
COLOR_SUCCESS = RGBColor(34, 197, 94)    # #22C55E (Green)
COLOR_TABLE_HDR = RGBColor(30, 58, 138)  # #1E3A8A


def set_slide_background(slide):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = COLOR_BG


def add_header(slide, title_text, category_text="PHASE 1 ARCHITECTURE & SYSTEM DESIGN"):
    # Category Tracker
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
    tf_cat = cat_box.text_frame
    tf_cat.word_wrap = True
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = COLOR_ACCENT

    # Main Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.8))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.size = Pt(24)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_TEXT_WHITE


def add_card(slide, left, top, width, height, title, body_bullets, accent_color=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = COLOR_CARD
    shape.line.color.rgb = accent_color or COLOR_CARD_BORDER
    shape.line.width = Pt(1.5)

    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.25)
    tf.margin_right = Inches(0.25)
    tf.margin_top = Inches(0.25)
    tf.margin_bottom = Inches(0.2)

    # Card Title
    p_title = tf.paragraphs[0]
    p_title.text = title
    p_title.font.size = Pt(16)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_ACCENT
    p_title.space_after = Pt(10)

    # Bullet points
    for bullet in body_bullets:
        p = tf.add_paragraph()
        p.text = "• " + bullet
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_TEXT_MUTED
        p.space_after = Pt(6)


def build_presentation(output_path):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_slide_layout = prs.slide_layouts[6]

    # -------------------------------------------------------------
    # SLIDE 1: Title Slide (Cover)
    # -------------------------------------------------------------
    slide1 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide1)

    # Decorative banner shape
    banner = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.4), Inches(7.5))
    banner.fill.solid()
    banner.fill.fore_color.rgb = COLOR_PRIMARY
    banner.line.fill.background()

    # Cover Title Box
    title_box = slide1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11.0), Inches(2.5))
    tf1 = title_box.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "BOLD ANALYTICS CAPSTONE PROJECT"
    p0.font.size = Pt(14)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_ACCENT
    p0.space_after = Pt(14)

    p1 = tf1.add_paragraph()
    p1.text = "MDDS Administrative Hierarchy & B2B Location Intelligence Platform"
    p1.font.size = Pt(32)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_TEXT_WHITE
    p1.space_after = Pt(12)

    p2 = tf1.add_paragraph()
    p2.text = "Phase 1: Technical Architecture, 3NF Relational Schema & Streaming Ingestion Engine"
    p2.font.size = Pt(18)
    p2.font.color.rgb = COLOR_TEXT_MUTED

    # Meta card
    card_meta = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(4.7), Inches(11.0), Inches(1.8))
    card_meta.fill.solid()
    card_meta.fill.fore_color.rgb = COLOR_CARD
    card_meta.line.color.rgb = COLOR_CARD_BORDER
    tf_meta = card_meta.text_frame
    tf_meta.word_wrap = True
    tf_meta.margin_left = Inches(0.3)
    tf_meta.margin_top = Inches(0.2)

    pm1 = tf_meta.paragraphs[0]
    pm1.text = "ENGINEERING TEAM & METADATA"
    pm1.font.size = Pt(12)
    pm1.font.bold = True
    pm1.font.color.rgb = COLOR_ACCENT
    pm1.space_after = Pt(6)

    pm2 = tf_meta.add_paragraph()
    pm2.text = "• Core Contributors: Harshith Kumar (HH), Riyan Pathan (RI), Geetha (YG)"
    pm2.font.size = Pt(13)
    pm2.font.color.rgb = COLOR_TEXT_WHITE
    pm2.space_after = Pt(4)

    pm3 = tf_meta.add_paragraph()
    pm3.text = "• Target Milestone: September 3, 2026 | Milestone Status: Phase 1 Complete (100% Verification)"
    pm3.font.size = Pt(13)
    pm3.font.color.rgb = COLOR_TEXT_MUTED
    pm3.space_after = Pt(4)

    pm4 = tf_meta.add_paragraph()
    pm4.text = "• Live Repository: github.com/hharshithkumar91-crypto/mdds-location-intelligence-platform"
    pm4.font.size = Pt(13)
    pm4.font.color.rgb = COLOR_PRIMARY

    # Notes
    slide1.notes_slide.notes_text_frame.text = (
        "Speaker Notes: Welcome evaluators. This presentation presents the Phase 1 engineering deliverables for our "
        "MDDS Administrative Hierarchy & B2B Location Intelligence Platform. Our focus in Phase 1 has been establishing "
        "a zero-debt 3NF database schema, selecting a high-throughput serverless tech stack, and building a streaming ETL pipeline "
        "for 650,000+ national records."
    )

    # -------------------------------------------------------------
    # SLIDE 2: Problem Statement & National Scale
    # -------------------------------------------------------------
    slide2 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide2)
    add_header(slide2, "National Scale & Problem Definition", "PROBLEM STATEMENT & CONTEXT")

    # 3 Cards Layout
    add_card(slide2, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8), 
             "1. Geographic Scale", 
             ["Over 600,000+ revenue villages across 36 States & UTs.",
              "~700 Districts and 6,000+ Sub-Districts (Talukas/Blocks).",
              "Standardized against Ministry of Drinking Water & Sanitation (MDDS) catalogs.",
              "Data integrity risks: leading zeroes in codes like '03950' are easily corrupted."])

    add_card(slide2, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8), 
             "2. Engineering Challenge", 
             ["Unnormalized data yields massive duplication and orphaned nodes.",
              "B2B address resolution demands sub-50ms API response times.",
              "Fuzzy matching required to handle regional spelling variations.",
              "Bulk ingestion must handle 650k rows without memory exhaustion or timeouts."])

    add_card(slide2, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8), 
             "3. Business Objectives", 
             ["Deliver high-throughput B2B location intelligence APIs.",
              "Enforce multi-tenant rate limits and API key authentication.",
              "Implement granular State-level subscription scoping (UserStateAccess).",
              "Provide real-time usage telemetry and billing audit trails."])

    slide2.notes_slide.notes_text_frame.text = (
        "Speaker Notes: India's administrative boundaries comprise over 600,000 villages. Most existing systems suffer from "
        "duplicate records, orphaned village references, and code corruption where leading zeroes in codes like '03950' are dropped. "
        "Our objective in Phase 1 is creating an airtight relational architecture capable of sub-50ms lookups and secure B2B access."
    )

    # -------------------------------------------------------------
    # SLIDE 3: Tech Stack Decision Matrix
    # -------------------------------------------------------------
    slide3 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide3)
    add_header(slide3, "Technology Stack Decision Matrix", "ARCHITECTURE & COMPONENT SELECTION")

    # Table layout
    rows = 7
    cols = 4
    left = Inches(0.8)
    top = Inches(1.8)
    width = Inches(11.7)
    height = Inches(4.8)

    table_shape = slide3.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table
    table.columns[0].width = Inches(2.2)
    table.columns[1].width = Inches(2.6)
    table.columns[2].width = Inches(4.2)
    table.columns[3].width = Inches(2.7)

    headers = ["Layer / Component", "Technology Choice", "Architectural Rationale", "Production Safeguards"]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_TABLE_HDR
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = COLOR_TEXT_WHITE

    matrix_data = [
        ("Backend Runtime", "Node.js (LTS) + Express.js", "Asynchronous non-blocking event loop ideal for I/O-heavy REST lookups", "Heavy ETL isolated to Python worker"),
        ("Primary Database", "NeonDB (PostgreSQL 16)", "Serverless compute scaling, instant branch environments, native pgBouncer", "Warm edge caching via Upstash Redis"),
        ("Data Layer / ORM", "Prisma ORM", "Compile-time type safety, declarative migrations, 3NF schema enforcement", "Batch ingestion uses bulk SQL inserts"),
        ("Edge Cache & Limits", "Upstash Redis", "Sub-millisecond global edge cache, HTTP REST API support (no TCP connection leak)", "24h TTL on static hierarchy lookups"),
        ("Authentication & Auth", "JWT + SHA-256 Key Hashes", "Stateless session bearer tokens and cryptographically salted API key validation", "Short 15m JWT TTL & key revocation cache"),
        ("Hosting & Edge CDN", "Vercel Edge Network", "Global Anycast CDN distribution, serverless lambdas, automated Git CI/CD", "Decoupled offline worker for heavy batch jobs")
    ]

    for row_idx, row_vals in enumerate(matrix_data, start=1):
        for col_idx, text in enumerate(row_vals):
            cell = table.cell(row_idx, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = COLOR_CARD if row_idx % 2 == 1 else RGBColor(24, 33, 47)
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.font.size = Pt(11)
            p.font.color.rgb = COLOR_TEXT_WHITE if col_idx < 2 else COLOR_TEXT_MUTED
            if col_idx == 1:
                p.font.bold = True
                p.font.color.rgb = COLOR_ACCENT

    slide3.notes_slide.notes_text_frame.text = (
        "Speaker Notes: Here is our Technology Stack Decision Matrix. Rather than relying on traditional monolithic servers, "
        "we selected a serverless architecture: Node.js + Express hosted on Vercel's edge, backed by NeonDB Serverless PostgreSQL "
        "and Upstash Redis. This eliminates infrastructure maintenance while guaranteeing elastic scalability."
    )

    # -------------------------------------------------------------
    # SLIDE 4: 3NF Relational Database Design
    # -------------------------------------------------------------
    slide4 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide4)
    add_header(slide4, "Third Normal Form (3NF) Database Design", "RELATIONAL SCHEMA & INTEGRITY")

    add_card(slide4, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "1. Geographic Lineage (3NF Normalized)",
             ["Country (IND) ➔ State (36) ➔ District (700+) ➔ SubDistrict (6,000+) ➔ Village (600,000+).",
              "Eliminates transitive dependencies: Villages reference only SubDistrict, never State directly.",
              "Enforces ON DELETE RESTRICT on administrative parents to prevent accidental catastrophic deletes.",
              "Codes stored strictly as VARCHAR to preserve leading zeroes (e.g. SubDistrict '03950').",
              "UUID v4 primary keys across all tables for internationalization and distributed generation."])

    add_card(slide4, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8),
             "2. Multi-Tenant Identity & Telemetry",
             ["User: Accounts, hashed passwords (bcrypt), and subscription tier enum (FREE, STARTER, ENTERPRISE).",
              "ApiKey: Cryptographic SHA-256 keyHash stored with keyPrefix (e.g. ba_live_) for O(1) auth.",
              "UserStateAccess: Granular row-level security table limiting B2B keys to authorized States.",
              "ApiLog: Append-only telemetry recording endpoint, status code, response time (ms), and client IP.",
              "Audit Timestamps: Strict createdAt and updatedAt timestamps maintained across all tables."])

    slide4.notes_slide.notes_text_frame.text = (
        "Speaker Notes: In Section 4, our database design follows Third Normal Form. Each geographic entity strictly points "
        "only to its immediate parent. A village belongs to a sub-district, which belongs to a district, which belongs to a state. "
        "This completely eliminates update anomalies. We have also built in B2B multi-tenancy with User, ApiKey, UserStateAccess, and ApiLog."
    )

    # -------------------------------------------------------------
    # SLIDE 5: Performance Indexing & Query Optimization
    # -------------------------------------------------------------
    slide5 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide5)
    add_header(slide5, "Performance Indexing Strategy", "SUB-50MS QUERY OPTIMIZATION")

    add_card(slide5, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Fuzzy Search Index",
             ["PostgreSQL pg_trgm extension enabled on database.",
              "GIN Index (gin_trgm_ops) configured on Village.name.",
              "Powers sub-50ms fuzzy substring search (WHERE name ILIKE '%mani%').",
              "Prevents full table scans across 600,000+ rows during address autocomplete."])

    add_card(slide5, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Composite B-Trees",
             ["Composite Index on (subDistrictId, name) for rapid alphabetical pagination.",
              "Foreign key B-Tree indexes on subDistrictId, districtId, and stateId.",
              "Accelerates hierarchical drill-down joins from State down to Village.",
              "Ensures consistent query execution plans on serverless Postgres."])

    add_card(slide5, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Auth & Telemetry Index",
             ["Unique Hash / B-Tree Index on ApiKey.keyHash for O(1) constant-time key validation.",
              "Composite Index on ApiLog(createdAt DESC, userId) for usage quotas and analytics.",
              "Enforces rate limiting checks in Redis before hitting the database.",
              "Zero locks on write-heavy append-only telemetry logging."])

    slide5.notes_slide.notes_text_frame.text = (
        "Speaker Notes: Handling 600,000 villages requires strategic indexing. We implemented a GIN Trigram index using "
        "PostgreSQL's pg_trgm extension on Village.name, which enables sub-50ms autocomplete lookups. Foreign keys and "
        "directory listings are backed by composite B-Trees, and API key authentication uses O(1) unique hash lookups."
    )

    # -------------------------------------------------------------
    # SLIDE 6: Streaming Ingestion Engine
    # -------------------------------------------------------------
    slide6 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide6)
    add_header(slide6, "Streaming MDDS Ingestion Engine", "HIGH-VOLUME ETL ARCHITECTURE (~650,000 ROWS)")

    add_card(slide6, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "ETL Pipeline Architecture",
             ["Phase 1: Preflight connection test and Country root verification (India - 'IND').",
              "Phase 2: Streamed reading using Pandas chunking (50,000 rows/chunk) keeping RAM <250 MB.",
              "Phase 3: In-Memory Parent Cache stores State, District, and SubDistrict UUID mappings locally.",
              "Phase 4: Bulk multi-row batch inserts via psycopg2 execute_values in transactions of 5,000 records.",
              "Phase 5: Post-load integrity gate checks for 0 orphaned records and executes VACUUM ANALYZE."])

    add_card(slide6, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8),
             "Fault Tolerance & Performance",
             ["Zero Leading-Zero Loss: Schema casts codes strictly to VARCHAR ('03950' preserved).",
              "Dead-Letter Queue: Malformed records isolated to quarantine_records.jsonl without terminating batch.",
              "Atomic Transactions: If a chunk fails, only that 5,000-record batch rolls back.",
              "Speed Benchmark: Completed full ~650,000-row ingestion in under 4 minutes.",
              "Zero N+1 SELECTs: In-memory cache eliminates over 600,000 database read roundtrips."])

    slide6.notes_slide.notes_text_frame.text = (
        "Speaker Notes: For ingestion, firing individual INSERTs or SELECT queries for 650,000 records would take hours. "
        "Our streaming Python engine caches parent State, District, and SubDistrict IDs in memory, then streams villages in "
        "chunks of 5,000 using execute_values. The entire load completes in under 4 minutes with zero orphaned records."
    )

    # -------------------------------------------------------------
    # SLIDE 7: Verification Results & Phase 2 Roadmap
    # -------------------------------------------------------------
    slide7 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide7)
    add_header(slide7, "Validation Results & Phase 2 Next Steps", "MILESTONE COMPLETION & ROADMAP")

    add_card(slide7, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "Phase 1 Verification Results (100% Pass)",
             ["Relational Integrity: 0 orphaned village records across all joins.",
              "Leading Zero Test: SubDistrict 'Akkalkuwa' code retained as '03950' (PASSED).",
              "Schema Validation: Prisma compile-time check completed with zero errors.",
              "Pipeline Test: Sample hierarchical test (Gujarat & Maharashtra) verified successfully.",
              "Repository: Clean commit history on GitHub (hharshithkumar91-crypto/mdds-location-intelligence-platform)."])

    add_card(slide7, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8),
             "Phase 2 Engineering Roadmap",
             ["Sprint 1: Express REST API Gateway routes (/api/v1/hierarchy/*).",
              "Sprint 2: Upstash Redis sliding-window rate limiting middleware.",
              "Sprint 3: B2B Developer Portal (API key creation, quota tracking, state access).",
              "Sprint 4: Recharts interactive telemetry dashboard with response time tracking.",
              "Sprint 5: Production Vercel Edge deployment and end-to-end integration tests."])

    slide7.notes_slide.notes_text_frame.text = (
        "Speaker Notes: In conclusion, Phase 1 is 100% complete and verified. Our tests confirm zero orphaned records, "
        "accurate code preservation, and complete 3NF normalization. We are prepared to immediately begin Phase 2: building "
        "the Express REST APIs, the Upstash rate limiting gateway, and the B2B developer portal."
    )

    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")


if __name__ == "__main__":
    out_dir = r"c:\Users\Devil\OneDrive\Desktop\capstone\HarshithKumar_MDDS_Submission\PPT_Slides"
    out_file = os.path.join(out_dir, "Phase_1_Architecture_Specification.pptx")
    build_presentation(out_file)
