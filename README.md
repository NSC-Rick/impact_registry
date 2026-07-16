# Impact Registry MVP

**Version:** Discovery.WPP-009.0  
**Status:** Production Ready

## Overview

The Impact Registry is a practitioner-first tool for capturing, enriching, analyzing, and monitoring organizational change impacts. Built to support Change Managers in delivering comprehensive impact assessments faster than traditional spreadsheet methods.

**Latest Updates:**
- ✅ WPP-001: MVP Foundation (Complete)
- ✅ WPP-002: Capture Workspace (Complete)
- ✅ WPP-003: Enrichment Workspace (Complete)
- ✅ WPP-004: Analyze Workspace (Complete)
- ✅ WPP-005: Enterprise Asset Registry (Complete)
- ✅ WPP-006: Bulk Operations (Complete)
- ✅ WPP-007: Question Engine (Complete)
- ✅ WPP-008: Impact Detail Workspace (Complete)
- ✅ WPP-009: Monitor Workspace (Complete)

## Design Principles

- **Practitioner First** - Optimized for the people doing the work
- **Capture First** - Get impacts recorded quickly, enrich later
- **Coverage, not Execution** - Focus on comprehensive capture over perfect detail
- **Traceability** - Link impacts to enterprise assets
- **Enterprise Assets** - Reusable organizational elements
- **Logical Concepts** - Structured around how practitioners think
- **Carry Forward** - Reuse assets across projects

## Workflow

```
Setup → Enterprise Asset Registry → Capture Workspace → Enrichment Workspace → Analyze Workspace → Monitor
```

### 1. Setup (Page 01)
Configure your project:
- Project details (sponsor, change manager, dates)
- Select or create project
- Set project parameters

### 2. Enterprise Asset Registry (Page 09) 🏛️ NEW
**Centralized registry of reusable organizational assets:**
- **Stakeholder Groups** - Define affected populations
- **Organization Units** - Map organizational structure
- **Business Processes** - Identify process changes
- **Systems** - Track technology changes
- **Policies** - Manage policy impacts
- **Search & Filter** - Find assets instantly
- **View Related Impacts** - Understand asset usage
- **Status Management** - Active, Inactive, Retired
- **Create once, use many times** - 20:1 reuse ratio
- **Performance:** <30 seconds to create, <10 seconds to find

### 3. Capture Workspace (Page 06) ⚡ RECOMMENDED
**Rapid impact capture during live sessions:**
- **Capture First** - Title + Description required, everything else optional
- **Carry Forward** - Pin fields to auto-populate across captures
- **Duplicate Context** - Copy relationships from previous impacts
- **Quick Actions** - Save Draft, Approve, Save & New
- **Auto-numbering** - IMP-XXXX format
- **Performance:** 15-30 seconds per impact (6-12x faster than spreadsheets)

### 4. Enrichment Workspace (Page 07) 🔗 RECOMMENDED
**Deliberate relationship building and coverage:**
- **Smart Filtering** - Draft, Unenriched, Missing Coverage, etc.
- **Enterprise Assets** - Link to stakeholders, processes, systems, policies
- **Change Assets** - Define coverage with deliverables (Training, QRG, etc.)
- **Quick Add** - Common change assets available for one-click addition
- **Enrichment Score** - Automated quality metric (0-100%)
- **Rapid Navigation** - Previous/Next with Approve & Next workflow
- **Performance:** 2-3 minutes per impact enrichment

### 5. Legacy Capture (Page 02)
Original capture interface with bulk import:
- **Quick Capture** - One impact at a time
- **Bulk Import** - CSV/Excel upload
- **Impact List** - View and manage all impacts

### 6. Legacy Enrich (Page 03)
Original enrichment interface:
- Impact details editing
- Traceability management
- Source evidence
- Change assets

### 7. Analyze Workspace (Page 08) 📊 RECOMMENDED
**Interactive exploration and business intelligence:**
- **Overview Dashboard** - High-level metrics and primary questions
- **Enterprise Asset Analysis** - Stakeholders, processes, systems, policies
- **Coverage Analysis** - Change assets by type, status, distribution
- **Impact Explorer** - Drill-through from charts to impact records
- **Registry Health** - Quality metrics, gaps, recommendations
- **Keyword Search** - Find impacts and assets quickly
- **Multi-Dimensional Filtering** - Status, stakeholder, process, system
- **Clickable Charts** - Every count drills through to impacts
- **Performance:** Answer business questions in <2 minutes

### 8. Legacy Analyze (Page 04)
Original analytics interface:
- Impact summaries by category, severity, status
- Risk matrix (severity × likelihood)
- Coverage metrics
- Traceability analysis

### 9. Bulk Operations (Page 10) ⚙️ NEW
**Efficient multi-impact operations:**
- **Multi-Select** - Checkbox selection with Select All
- **Bulk Status Change** - Draft, Approved, Superseded
- **Bulk Enterprise Assets** - Assign, Replace, Remove
- **Bulk Change Assets** - Create for multiple impacts
- **Bulk Notes** - Append or Replace
- **Quick Add** - Common assets in one click
- **Preview Before Apply** - Always see what will change
- **Safe Deletion** - Draft only with confirmation
- **Performance:** 40-75x faster than manual editing

### 10. Question Engine (Page 11) ❓ NEW
**Ask questions, get answers:**
- **Five Question Categories** - Impact, Enterprise Assets, Coverage, Health, Relationships
- **Pre-Defined Questions** - Common business questions ready to ask
- **Dynamic Questions** - Generated from your project data
- **Drill-Through Answers** - Every result is clickable
- **Pin Favorites** - Save frequently asked questions
- **Recent Questions** - Quick access to last 10 questions
- **Keyword Search** - Find questions fast
- **Visual Answers** - Charts and tables
- **Performance:** Answer questions in <30 seconds

### 11. Impact Detail (Page 12) 📄 NEW
**Comprehensive single-impact knowledge page:**
- **Six Comprehensive Sections** - Summary, Enterprise Assets, Change Assets, Evidence, Relationships, History
- **Impact Summary** - ID, title, description, status, metrics
- **Enterprise Assets** - All linked stakeholders, processes, systems, policies (clickable)
- **Change Assets** - Coverage status, completion tracking
- **Source Evidence** - Discovery sessions, workshops, interviews
- **Relationships** - Related impacts based on shared assets
- **History & Notes** - Complete audit trail
- **Previous/Next Navigation** - Sequential browsing
- **One-Click Access** - Every related object is clickable
- **Performance:** Complete understanding in <3 minutes

### 12. Monitor Workspace (Page 13) 📊 NEW
**Registry health & practitioner work queues:**
- **Four Comprehensive Tabs** - Health, Coverage Gaps, Work Queue, Progress
- **Registry Health** - Status distribution, recent activity, enrichment quality
- **Coverage Gaps** - Missing assets, evidence, relationships (color-coded)
- **Work Queues** - Awaiting approval, needs enrichment, needs coverage
- **Progress Tracking** - Capture, approval, enrichment, coverage metrics
- **Completeness Score** - Overall registry quality metric
- **Actionable Metrics** - Every indicator has drill-through or action
- **Operational Focus** - Monitor registry, not people or execution
- **Performance:** Identify next task in <30 seconds

### 13. Legacy Monitor (Page 05)
Original monitoring interface:
- Project dashboard
- Change asset status
- Status tracking
- Export capabilities

## Installation

### Prerequisites
- Python 3.8 or higher
- pip

### Setup

1. Clone or navigate to the repository:
```bash
cd c:\Users\reeco\NSBI\impact_registry
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

4. Open your browser to `http://localhost:8501`

## Project Structure

```
impact_registry/
├── app.py                          # Main application entry point
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── database/
│   ├── schema.py                   # SQLAlchemy ORM models
│   └── sqlite.db                   # SQLite database (auto-created)
│
├── models/
│   ├── project.py                  # Project DTO
│   ├── impact.py                   # Impact DTO
│   ├── stakeholder_group.py        # Stakeholder Group DTO
│   ├── organization_unit.py        # Organization Unit DTO
│   ├── business_process.py         # Business Process DTO
│   ├── system.py                   # System DTO
│   ├── policy.py                   # Policy DTO
│   ├── source_evidence.py          # Source Evidence DTO
│   └── change_asset.py             # Change Asset DTO
│
├── services/
│   ├── repository.py               # Data access layer
│   ├── carry_forward.py            # Asset reuse service
│   └── analytics.py                # Analytics service
│
└── pages/
    ├── 01_Setup.py                 # Setup workflow page
    ├── 02_Capture.py               # Legacy capture (bulk import)
    ├── 03_Enrich.py                # Legacy enrich
    ├── 04_Analyze.py               # Legacy analyze
    ├── 05_Monitor.py               # Monitor workflow page
    ├── 06_Capture_Workspace.py     # ⚡ NEW: Rapid capture workspace
    ├── 07_Enrichment_Workspace.py  # 🔗 NEW: Deliberate enrichment workspace
    ├── 08_Analyze_Workspace.py     # 📊 NEW: Interactive analysis workspace
    ├── 09_Enterprise_Asset_Registry.py  # 🏛️ NEW: Centralized asset registry
    ├── 10_Bulk_Operations.py       # ⚙️ NEW: Bulk operations workspace
    ├── 11_Question_Engine.py        # ❓ NEW: Question-based exploration
    ├── 12_Impact_Detail.py          # 📄 NEW: Comprehensive impact view
    └── 13_Monitor_Workspace.py      # 📊 NEW: Registry health monitoring

Documentation:
├── WPP-001_MVP_FOUNDATION.md       # (Implicit in README)
├── WPP-002_CAPTURE_WORKSPACE.md    # Capture Workspace specification
├── WPP-003_ENRICHMENT_WORKSPACE.md # Enrichment Workspace specification
├── WPP-004_ANALYZE_WORKSPACE.md    # Analyze Workspace specification
├── WPP-005_ENTERPRISE_ASSET_REGISTRY.md # Enterprise Asset Registry specification
├── WPP-006_BULK_OPERATIONS.md      # Bulk Operations specification
├── WPP-007_QUESTION_ENGINE.md      # Question Engine specification
├── WPP-008_IMPACT_DETAIL.md        # Impact Detail Workspace specification
└── WPP-009_MONITOR_WORKSPACE.md    # Monitor Workspace specification
```

## Usage Guide

### Getting Started

1. **Create a Project** (Setup - Page 01)
   - Define project name, sponsor, change manager
   - Set start and end dates

2. **Define Enterprise Assets** (Setup - Page 01)
   - Add stakeholder groups affected by the change
   - Define organization units, processes, systems, policies
   - Or carry forward from a previous project

3. **Capture Impacts** (Capture Workspace - Page 06) ⚡ RECOMMENDED
   - Configure carry forward settings
   - Enter Title + Description (required)
   - Add context as needed (optional)
   - Use "Save & New" for rapid sequential capture
   - **Performance:** 15-30 seconds per impact

4. **Enrich Impacts** (Enrichment Workspace - Page 07) 🔗 RECOMMENDED
   - Filter impacts (Draft, Unenriched, Missing Coverage, etc.)
   - Review and improve descriptions
   - Establish enterprise asset relationships
   - Define change asset coverage
   - Approve when complete
   - **Performance:** 2-3 minutes per impact

5. **Analyze** (Analyze - Page 04)
   - Review impact summaries
   - Identify high-risk impacts
   - Check coverage metrics
   - Understand traceability patterns

6. **Monitor** (Monitor - Page 05)
   - Track project progress
   - Monitor change asset status
   - Export data for reporting

### Alternative Workflows

**Bulk Import** (Legacy Capture - Page 02)
- Use for large volumes from existing spreadsheets
- Download CSV template
- Upload and import

**Individual Enrichment** (Legacy Enrich - Page 03)
- Select specific impact to enrich
- Full detail editing
- Navigate between impacts

### Acceptance Tests

**WPP-001 (MVP Foundation):**
> Using the Mondelez Change Impact Assessment workbook, a Change Manager can capture and enrich at least 50 real impacts faster than using Excel.

**WPP-002 (Capture Workspace):**
> Using real project data, a practitioner can capture twenty Change Impacts during a workshop without repetitive entry of common contextual information.

**WPP-003 (Enrichment Workspace):**
> Using real project data, a practitioner can enrich fifty captured Impacts by establishing meaningful relationships to Enterprise Assets and Change Assets.

**WPP-004 (Analyze Workspace):**
> Using real project data, a practitioner can answer meaningful questions about organizational change without exporting data to Excel. Every chart supports drill-through to the underlying Impact records.

**WPP-005 (Enterprise Asset Registry):**
> Using a real implementation project, a practitioner can establish all Enterprise Assets prior to impact capture. During Capture and Enrichment, Enterprise Assets are reused through search and selection rather than recreated.

**WPP-006 (Bulk Operations):**
> Using real project data, a practitioner can enrich fifty Change Impacts without opening fifty individual records.

**WPP-007 (Question Engine):**
> Using real project data, a practitioner can answer meaningful organizational questions without exporting data to Excel.

**WPP-008 (Impact Detail Workspace):**
> Using real project data, a practitioner can fully understand the organizational significance of a Change Impact from a single workspace. No additional navigation is required to understand the Impact and its relationships.

**WPP-009 (Monitor Workspace):**
> Using real project data, a practitioner can immediately identify the highest-value activities required to improve the quality and completeness of the Impact Registry.

### Tips for Success

**Enterprise Asset Setup:**
- **Create assets early** - During project setup, before impact capture
- **Use descriptive names** - Clear, unambiguous identifiers
- **Search before creating** - Avoid duplicates (20:1 reuse ratio)
- **Status management** - Mark Inactive/Retired rather than delete
- **View related impacts** - Understand asset usage patterns

**Capture Phase:**
- **Use Capture Workspace** - 6-12x faster than spreadsheets
- **Configure carry forward** - Pin common fields (source, stakeholders, processes)
- **Capture in live sessions** - During workshops, interviews, design sessions
- **Title + Description first** - Everything else is optional
- **Save & New workflow** - Rapid sequential capture

**Enrichment Phase:**
- **Use Enrichment Workspace** - Deliberate, focused enrichment
- **Filter strategically** - Start with "Missing Stakeholder Groups"
- **Work in batches** - 10-20 impacts per session
- **Establish relationships** - Each should enable future analysis
- **Use quick add** - Common change assets save time
- **Target 70% enrichment** - Balance quality and coverage

**Analysis Phase:**
- **Use Analyze Workspace** - Interactive exploration and business intelligence
- **Start with Overview** - Understand high-level status
- **Click charts** - Drill through to validate findings
- **Apply filters** - Narrow to areas of interest
- **Use keyword search** - Find specific impacts or assets
- **Monitor health** - Track registry quality over time
- **Answer business questions** - Use analysis to guide decisions

**Bulk Operations:**
- **Filter first** - Narrow to target impacts before selecting
- **Preview changes** - Always review before applying
- **Start small** - Test with 5-10 impacts first
- **Use quick add** - Common change assets in one click
- **Choose operation mode** - Assign vs. Replace vs. Remove
- **Leverage for efficiency** - 40-75x faster than manual editing

**Question Engine:**
- **Start with questions** - Not reports
- **Pin common questions** - Quick access to favorites
- **Use for meetings** - Live answers to stakeholder questions
- **Drill through** - Explore results in detail
- **Track over time** - Re-ask questions to see progress
- **Answer without Excel** - All analysis in-application

**Impact Detail:**
- **Use for reviews** - Complete context in one place
- **Navigate sequentially** - Previous/Next through impacts
- **Click related objects** - One-click to enterprise assets
- **Explore relationships** - Find similar impacts
- **Verify enrichment** - Check completeness score
- **Quick actions** - Enrich or Analyze buttons

**Monitor Workspace:**
- **Check daily** - Monitor registry health regularly
- **Work the queue** - Focus on highest-value activities
- **Use color codes** - Red = urgent, Yellow = soon, Green = good
- **Drill through** - Click metrics to see specific impacts
- **Track trends** - Monitor progress over time
- **Operational focus** - Registry quality, not people or execution

**General:**
- **Carry forward assets** - Reuse from previous projects
- **Coverage over perfection** - Better to have 50 rough impacts than 5 perfect ones
- **Export regularly** - Generate reports for stakeholders

## Data Model

### Core Entities

- **Project** - Container for all impacts and assets
- **Impact** - A discrete change impact
- **Stakeholder Group** - Group of people affected by change
- **Organization Unit** - Department, division, or team
- **Business Process** - End-to-end business process
- **System** - Technology system or application
- **Policy** - Organizational policy or regulation
- **Source Evidence** - Where an impact was identified
- **Change Asset** - Deliverable to address an impact

### Relationships

- Impacts belong to Projects
- Impacts can link to multiple enterprise assets (many-to-many)
- Source Evidence and Change Assets belong to Impacts

## Deferred Features

The following features are planned for future releases:

- AI-assisted capture
- Transcript ingestion
- Microsoft Teams integration
- SharePoint integration
- Signal processing
- Champion Network
- Adoption Analytics

## Success Criteria

The MVP demonstrates that organizational change can be captured, traced, enriched, analyzed, and monitored using a practitioner-first workflow.

## Support

For questions or issues, contact the Change Management team.

## License

Internal use only - NSBI/Mondelez
