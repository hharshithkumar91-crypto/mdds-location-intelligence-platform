# Bold Analytics Capstone: Submission Format & Structure Guidelines

This document outlines the evaluation rubric, directory hierarchy, and formatting guidelines for **Phase 1 Capstone Submission**.

---

## 1. Master Directory Hierarchy

Your Google Drive folder must be named **`HarshithKumar_MDDS_Submission`** and contain the following **5 required sub-folders**:

```
HarshithKumar_MDDS_Submission/
├── 📁 Source Code/
│   ├── source_code.zip                      # Compressed archive of complete clean source code
│   ├── GITHUB_REPOSITORY_LINK.txt           # Verified public GitHub repository URL
│   ├── package.json                         # Node.js backend configuration and dependencies
│   ├── .env.example                         # Environment configuration template
│   ├── .gitignore                           # Git ignore rules
│   ├── README.md                            # Comprehensive project overview and setup instructions
│   ├── prisma/
│   │   └── schema.prisma                    # 3NF normalized PostgreSQL schema with indexes
│   └── scripts/
│       ├── import_mdds.py                   # High-speed streaming ETL ingestion engine
│       └── verify_pipeline.py               # Automated relational integrity verification runner
│
├── 📁 Datasets/
│   ├── sample_mdds.csv                      # Canonical test dataset (Maharashtra & Gujarat hierarchy)
│   └── DATASET_OVERVIEW.md                  # Column mappings, code formats, and volume metrics
│
├── 📁 Documentation/
│   ├── PHASE_1_TECHNICAL_SPECIFICATION.md   # Complete 25-page System Architecture & Design Document
│   └── ARCHITECTURE_EXECUTIVE_SUMMARY.md    # 2-page executive summary and evaluation brief
│
├── 📁 PPT / Slides/                         (named PPT_Slides on local disk)
│   ├── Phase_1_Architecture_Specification.pptx # Native 16:9 widescreen PowerPoint deck with notes
│   ├── Phase_1_Presentation_Deck.html       # Responsive HTML slide deck (Printable to PDF)
│   └── Phase_1_Presentation_Deck.md         # Markdown slide outline for Google Slides / Canva
│
└── 📁 Demo Video/
    ├── DEMO_VIDEO_RECORDING_KIT.md          # 90-second word-for-word spoken script with timestamps
    ├── VERIFICATION_TERMINAL_OUTPUT.txt     # Raw console output confirming 100% test pass
    └── HarshithKumar_Phase1_Demo_Walkthrough.mp4 (Upload your recorded video or Loom link here)
```

---

## 2. Deliverable Quality Criteria & Rubric

### Sub-Folder 1: `Source Code`
- **Criteria:** Clean, compilable, zero build errors, fully documented.
- **Includes:**
  - `prisma/schema.prisma`: All 5 hierarchical levels (`Country`, `State`, `District`, `SubDistrict`, `Village`) and multi-tenant security entities (`User`, `ApiKey`, `UserStateAccess`, `ApiLog`).
  - `scripts/import_mdds.py`: Memory-safe streaming with Pandas chunking, in-memory parent foreign key cache, and batch `execute_values`.
  - `source_code.zip`: Enables evaluators to download and inspect code offline with 1 click.

### Sub-Folder 2: `Datasets`
- **Criteria:** Representative test data demonstrating all edge cases.
- **Includes:**
  - `sample_mdds.csv`: Includes Maharashtra and Gujarat records, testing leading-zero retention (e.g. SubDistrict `'03950'`) and multi-village resolution.
  - `DATASET_OVERVIEW.md`: Detailed specification of column names, data types, and scale (~650k rows).

### Sub-Folder 3: `Documentation`
- **Criteria:** Exhaustive, professional System Design Document (SDD).
- **Includes:**
  - Complete Technology Decision Matrix with production trade-offs.
  - C4-style architectural diagrams and data flow sequence diagrams.
  - 3NF normalization justification and database indexing plan (GIN Trigram + composite B-Trees).
  - High-volume ETL ingestion workflow and failure mode quarantine design.

### Sub-Folder 4: `PPT / Slides`
- **Criteria:** 16:9 widescreen, clean visual hierarchy, executive dark-slate theme, speaker notes on every slide.
- **Includes:**
  - Native `.pptx` PowerPoint file generated specifically for this project.
  - Browser-viewable `.html` slides with Print-to-PDF support.
  - Markdown slide source for easy editing in Google Slides.

### Sub-Folder 5: `Demo Video`
- **Criteria:** Clear, articulate screen walkthrough showing live code execution and test verification.
- **Includes:**
  - Word-for-word 90-second spoken script with window layout instructions.
  - Pre-generated terminal output proving zero orphaned records and 100% test pass.

---

## 3. Google Drive Sharing Settings Checklist
- [ ] Upload master folder `HarshithKumar_MDDS_Submission` to Google Drive.
- [ ] Rename `PPT_Slides` to **`PPT / Slides`** inside Google Drive.
- [ ] Right-click `HarshithKumar_MDDS_Submission` ➔ **Share** ➔ Set General Access to **"Anyone with the link"** ➔ Role: **Viewer**.
- [ ] Copy the link and paste into the portal field: `Your Google Drive Folder Link *`.
