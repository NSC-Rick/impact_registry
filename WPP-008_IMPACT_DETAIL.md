# WPP-008: Impact Detail Workspace

**Version:** Discovery.WPP-008.0  
**Status:** Implemented  
**Date:** 2024-07-16

## Objective

Provide a comprehensive workspace for viewing, editing, and understanding a single Change Impact.

**The Impact Detail Workspace serves as the central knowledge page for every registered Change Impact.**

## Design Philosophy

**Every Impact is the center of a network of relationships.**

The practitioner should never have to search for related information.

Everything connected to an Impact should be visible from one location.

## Implementation Summary

### Primary Sections Implemented

✅ **Impact Summary** - ID, title, description, status, dates, metrics  
✅ **Enterprise Assets** - All linked stakeholders, processes, systems, policies  
✅ **Change Assets** - Training, communications, coverage status  
✅ **Source Evidence** - Discovery sessions, workshops, interviews  
✅ **Relationships** - Related impacts, supersession  
✅ **History & Notes** - Audit trail, timeline, notes  

### Navigation Implemented

✅ **Previous Impact** - Navigate to previous in list  
✅ **Next Impact** - Navigate to next in list  
✅ **Impact Selector** - Dropdown to jump to any impact  
✅ **Open Related Impact** - Click to view related impacts  
✅ **Open Enterprise Asset** - Click to view asset details  
✅ **Enrich Button** - Quick access to enrichment  
✅ **Analyze Button** - Quick access to analysis  

## File Structure

```
pages/
└── 12_Impact_Detail.py    # Comprehensive impact knowledge page (600+ lines)
```

## Usage Guide

### Quick Start

1. **Navigate to Impact Detail** (page 12)
2. **Select Impact** - Use dropdown or Previous/Next
3. **Review Summary** - See all key information
4. **Explore Tabs** - Six comprehensive sections
5. **Click Related Objects** - One-click navigation
6. **Enrich** - Add or update information

### Six-Tab Interface

**Tab 1: Summary**
- Impact ID and title
- Description and area of change
- Status with emoji indicator
- Created and updated dates
- Severity, likelihood, readiness, resistance
- Mitigation strategy

**Tab 2: Enterprise Assets**
- Stakeholder Groups (with size, influence)
- Organization Units (with head)
- Business Processes (with owner, criticality)
- Systems (with owner, vendor)
- Policies (with owner)
- Each asset is clickable
- Total asset count

**Tab 3: Change Assets**
- Grouped by asset type
- Asset name, description
- Status (Planned, In Progress, Review, Complete)
- Owner
- Total count, complete count, coverage %
- Quick add button if none exist

**Tab 4: Source Evidence**
- Source type with emoji
- Source name
- Notes
- Date
- URL link (if available)
- Total evidence count
- Quick add button if none exist

**Tab 5: Relationships**
- Related impacts (based on shared assets)
- Similarity score
- Shared stakeholders, processes, systems
- Supersession status
- Click to view related impacts

**Tab 6: History & Notes**
- Created date/time
- Modified date/time
- Approved date/time (if applicable)
- Superseded date/time (if applicable)
- Relationship change summary
- Impact notes (read-only)
- Edit notes button

### Navigation Bar

**Top Navigation:**
```
[⬅️ Previous] [Next ➡️] [Impact Selector Dropdown] [✏️ Enrich] [📊 Analyze]
```

**Features:**
- Previous/Next buttons (disabled at boundaries)
- Dropdown shows all impacts with number and title
- Enrich button → Enrichment Workspace
- Analyze button → Analyze Workspace
- Current position indicator

### Step-by-Step: Understand an Impact

**Scenario: Review Impact IMP-0042**

```
1. Go to Impact Detail
2. Select "IMP-0042" from dropdown
3. Tab 1 (Summary): Review description, status, severity
4. Tab 2 (Enterprise Assets): See affected stakeholders and systems
5. Tab 3 (Change Assets): Check coverage status
6. Tab 4 (Source Evidence): Verify source documentation
7. Tab 5 (Relationships): Explore related impacts
8. Tab 6 (History): Review audit trail
9. Time: ~2-3 minutes for complete understanding
```

### Step-by-Step: Navigate Related Impacts

**Scenario: Explore impacts affecting Finance Team**

```
1. View impact affecting Finance Team
2. Tab 2 (Enterprise Assets): Confirm Finance Team linked
3. Tab 5 (Relationships): See 8 related impacts
4. Click "View" on first related impact
5. Page updates to show that impact
6. Continue exploring related impacts
7. Use Previous/Next to navigate sequentially
```

## Primary Sections Detail

### 1. Impact Summary

**Information Displayed:**
- Impact Number (e.g., IMP-0042)
- Title (if set)
- Description (full text)
- Area of Change
- Status (with emoji: 📝 Draft, 👀 Under Review, ✅ Approved, 🔄 Superseded)
- Created Date/Time
- Updated Date/Time
- Severity (🟢 Low, 🟡 Medium, 🟠 High, 🔴 Critical)
- Likelihood
- Readiness
- Resistance
- Mitigation Strategy

**Layout:**
- Two-column layout
- Left: Title, description, area
- Right: Status, dates
- Bottom: Four-column metrics
- Mitigation strategy full-width

### 2. Enterprise Assets

**Five Asset Types:**

**Stakeholder Groups:**
- Name (clickable)
- Description
- Size
- Influence
- View button → Enterprise Asset Registry

**Organization Units:**
- Name (clickable)
- Description
- Head of Unit
- View button

**Business Processes:**
- Name (clickable)
- Description
- Process Owner
- Criticality
- View button

**Systems:**
- Name (clickable)
- Description
- System Owner
- Vendor
- View button

**Policies:**
- Name (clickable)
- Description
- Policy Owner
- View button

**Summary:**
- Total Enterprise Assets Linked (count)

### 3. Change Assets

**Grouped by Type:**
- Training
- Communication
- QRG
- FAQ
- Job Aid
- Manager Toolkit
- Process Document
- Video
- eLearning
- Other

**For Each Asset:**
- Asset Name
- Description
- Status (📋 Planned, 🔄 In Progress, 👀 Review, ✅ Complete)
- Owner

**Summary Metrics:**
- Total Change Assets
- Complete Count
- Coverage % (complete/total)

**Quick Action:**
- "Add Change Assets" button if none exist

### 4. Source Evidence

**Evidence Types:**
- 🔍 Discovery Session
- 👥 Workshop
- 🎤 Interview
- 📋 Requirements Session
- 🎨 Design Review
- 📅 Meeting
- 📄 Document
- 📌 Other

**For Each Evidence:**
- Source Type (with emoji)
- Source Name
- Notes
- Date
- URL Link (if available)

**Summary:**
- Total Source Evidence count

**Quick Action:**
- "Add Source Evidence" button if none exist

### 5. Relationships

**Related Impacts:**
- Calculated based on shared enterprise assets
- Similarity score (number of shared assets)
- Shows shared stakeholders, processes, systems
- Top 10 most related impacts
- Click "View" to navigate to related impact

**Supersession:**
- Active status indicator
- Warning if superseded
- Explanation of supersession

### 6. History & Notes

**History Events:**
- ➕ Created (date/time)
- ✏️ Modified (date/time)
- ✅ Approved (date/time if applicable)
- 🔄 Superseded (date/time if applicable)

**Relationship Changes:**
- Current enterprise asset count
- Change asset count
- Source evidence count

**Notes:**
- Read-only text area
- Full notes display
- Edit button → Enrichment Workspace

## User Experience Principles

✅ **Every related object should be one click away** - All assets clickable  
✅ **The practitioner should never lose context** - Navigation preserves position  
✅ **Scrolling should tell the complete story** - Six tabs cover everything  

## Acceptance Criteria

✅ **Met:** Using real project data, a practitioner can fully understand the organizational significance of a Change Impact from a single workspace.

✅ **Met:** No additional navigation is required to understand the Impact and its relationships.

### Additional Achievements

- **Six comprehensive sections** - Complete impact story
- **One-click navigation** - Every object is clickable
- **Related impact discovery** - Automatic similarity calculation
- **Enrichment score** - Quality metric displayed
- **Quick actions** - Enrich and Analyze buttons
- **Previous/Next** - Sequential navigation
- **Audit trail** - Complete history

## Engineering Notes

### Design Decisions

1. **Six-Tab Organization**
   - Summary, Enterprise Assets, Change Assets, Evidence, Relationships, History
   - Logical grouping
   - Complete coverage
   - No scrolling required

2. **Navigation Bar**
   - Previous/Next buttons
   - Impact selector dropdown
   - Quick action buttons (Enrich, Analyze)
   - Always visible at top

3. **Clickable Assets**
   - Every enterprise asset has "View" button
   - Navigates to Enterprise Asset Registry
   - Maintains context

4. **Related Impact Calculation**
   - Shared stakeholder groups
   - Shared business processes
   - Shared systems
   - Similarity score = sum of shared assets
   - Top 10 displayed

5. **Enrichment Score**
   - Same algorithm as Enrichment Workspace
   - Displayed at bottom
   - Visual indicator (🟢🟡🔴)

6. **History Timeline**
   - Created, Modified, Approved, Superseded
   - Emoji indicators
   - Date/time stamps
   - Relationship change summary

### Technical Implementation

**Navigation:**
```python
# Previous/Next buttons
current_index = next((i for i, imp in enumerate(impacts) if imp.id == current_impact.id), 0)

if st.button("⬅️ Previous", disabled=current_index == 0):
    st.session_state['detail_impact_id'] = impacts[current_index - 1].id
    st.rerun()
```

**Related Impact Calculation:**
```python
for impact in impacts:
    if impact.id != current_impact.id:
        shared_sgs = set(impact.stakeholder_group_ids) & set(current_impact.stakeholder_group_ids)
        shared_bps = set(impact.business_process_ids) & set(current_impact.business_process_ids)
        shared_systems = set(impact.system_ids) & set(current_impact.system_ids)
        
        if shared_sgs or shared_bps or shared_systems:
            similarity_score = len(shared_sgs) + len(shared_bps) + len(shared_systems)
            related_impacts.append((impact, similarity_score, shared_sgs, shared_bps, shared_systems))

related_impacts.sort(key=lambda x: x[1], reverse=True)
```

**Enrichment Score:**
```python
enrichment_score = 0
max_score = 6

if current_impact.title and current_impact.title.strip():
    enrichment_score += 1
if len(current_impact.stakeholder_group_ids) > 0:
    enrichment_score += 1
# ... similar for other dimensions

score_pct = (enrichment_score / max_score) * 100
```

## Integration with Other Workspaces

### Enrichment Workspace → Impact Detail
- After enriching, view complete impact
- Verify all relationships
- Check enrichment score

### Analyze Workspace → Impact Detail
- Drill through from analysis
- View specific impact details
- Understand context

### Question Engine → Impact Detail
- Answer leads to impact list
- Click impact to view details
- Complete understanding

### Impact Detail → Enterprise Asset Registry
- Click any enterprise asset
- View asset details
- Understand asset usage

### Impact Detail → Enrichment Workspace
- Click "Enrich" button
- Add or update information
- Return to detail view

## Testing Checklist

- [x] Navigate with Previous/Next
- [x] Select impact from dropdown
- [x] View impact summary
- [x] View enterprise assets
- [x] Click enterprise asset "View" button
- [x] View change assets
- [x] View source evidence
- [x] View related impacts
- [x] Click related impact "View" button
- [x] View history timeline
- [x] View notes
- [x] Click "Enrich" button
- [x] Click "Analyze" button
- [x] View enrichment score
- [x] Navigate to related impact

## Success Metrics

**Adoption:**
- Impact Detail used for >70% of impact reviews
- Average time on page: 2-3 minutes
- Navigation to related impacts: >40%

**Efficiency:**
- Time to understand impact: <3 minutes
- Clicks to related objects: 1 click
- Context switches: 0 (everything on one page)

**Quality:**
- Complete understanding: >95%
- Additional navigation needed: <5%
- User satisfaction: High

## Best Practices

### For Change Managers

1. **Start with Summary** - Understand the basics
2. **Review Enterprise Assets** - See organizational impact
3. **Check Coverage** - Verify change assets
4. **Validate Evidence** - Confirm source documentation
5. **Explore Relationships** - Understand connections
6. **Review History** - Track evolution

### For Project Teams

1. **Use for impact reviews** - Complete context in one place
2. **Navigate related impacts** - Understand patterns
3. **Verify enrichment** - Check completeness
4. **Update via Enrich** - Quick access to editing
5. **Share with stakeholders** - Single source of truth

## Example Scenarios

### Scenario 1: Impact Review

```
Objective: Review IMP-0042 for completeness

1. Navigate to Impact Detail
2. Select IMP-0042
3. Tab 1: Verify description and status
4. Tab 2: Check all enterprise assets linked
5. Tab 3: Verify change assets defined
6. Tab 4: Confirm source evidence
7. Tab 5: Review related impacts
8. Tab 6: Check history and notes
9. Result: Complete understanding in 2 minutes
```

### Scenario 2: Relationship Exploration

```
Objective: Find all impacts affecting SAP ERP

1. View any SAP ERP impact
2. Tab 5 (Relationships): See 12 related impacts
3. All share SAP ERP system
4. Click first related impact
5. Review that impact
6. Click next related impact
7. Continue exploring
8. Result: Understand SAP ERP change scope
```

### Scenario 3: Quality Check

```
Objective: Verify impact enrichment

1. View impact
2. Tab 1: Check title, description, metrics
3. Tab 2: Verify enterprise assets (should have ≥3)
4. Tab 3: Verify change assets (should have ≥2)
5. Tab 4: Verify source evidence (should have ≥1)
6. Bottom: Check enrichment score (should be ≥70%)
7. If gaps: Click "Enrich" to add information
8. Result: Quality assurance in 1 minute
```

## Explicitly Out of Scope

- ❌ Document Management
- ❌ Workflow Approvals
- ❌ Versioned Attachments
- ❌ Discussion Threads

**Rationale:** Impact Detail focuses on viewing and understanding. Editing is delegated to Enrichment Workspace. Document management is a separate concern.

## Future Enhancements (Deferred)

- Impact version history
- Inline editing
- Comment threads
- Attachment management
- Approval workflow
- Change notifications
- Impact templates
- AI-suggested relationships

## Conclusion

WPP-008 successfully implements a comprehensive Impact Detail Workspace that serves as the central knowledge page for every registered Change Impact. The workspace provides complete context in one location, with every related object one click away, enabling practitioners to fully understand the organizational significance of any impact without additional navigation.

**Key Achievement:** Practitioners can fully understand the organizational significance of a Change Impact from a single workspace, meeting the acceptance criteria and providing a "single source of truth" for each impact.

**Design Philosophy Realized:** "Every Impact is the center of a network of relationships." The Impact Detail Workspace visualizes this network comprehensively, showing all connections, relationships, and context in six organized tabs.

**Integration:** The workspace serves as a convergence point for the entire registry, with navigation to and from Enrichment, Analysis, Question Engine, and Enterprise Asset Registry, creating a cohesive exploration experience.

The implementation meets all acceptance criteria and provides the definitive view of each Change Impact, supporting understanding, validation, and exploration without requiring practitioners to search for related information across multiple locations.
