# WPP-009: Monitor Workspace

**Version:** Discovery.WPP-009.0  
**Status:** Implemented  
**Date:** 2024-07-16

## Objective

Provide practitioners and project leadership with continuous visibility into the health, completeness, and maturity of the Impact Registry.

**The Monitor Workspace measures the quality of the registry itself—not project execution.**

## Design Philosophy

**Monitor the registry.**

**Do not monitor people.**

**Do not monitor execution.**

The registry should continuously reveal areas requiring additional practitioner attention.

## Implementation Summary

### Primary Activities Implemented

✅ **Monitor Registry Health** - Status distribution, recent activity, enrichment quality  
✅ **Identify Coverage Gaps** - Missing assets, evidence, relationships  
✅ **Identify Incomplete Impacts** - Needs enrichment, needs coverage  
✅ **Track Registry Growth** - Capture rate, progress metrics  
✅ **Highlight Practitioner Work Queues** - Actionable task lists  

### Four-Tab Interface

**Tab 1: Registry Health**
- Status distribution
- Recent activity (7 days)
- Enrichment quality metrics
- Average enrichment score

**Tab 2: Coverage Gaps**
- Impacts without change assets
- Impacts without source evidence
- Impacts without stakeholders
- Impacts without business process
- Impacts without system
- Impacts without policy (optional)
- Drill-through to work queues

**Tab 3: Work Queue**
- Awaiting approval
- Needs enrichment
- Needs coverage
- Recently added (24h)
- Recently modified (24h)
- Direct enrichment links

**Tab 4: Progress Tracking**
- Capture progress
- Approval progress
- Enrichment progress
- Coverage progress
- Registry completeness score

## File Structure

```
pages/
└── 13_Monitor_Workspace.py    # Registry health monitoring (500+ lines)
```

## Usage Guide

### Quick Start

1. **Navigate to Monitor Workspace** (page 13)
2. **Review Top Metrics** - Total, Draft, Approved, Superseded
3. **Check Registry Health** - Tab 1
4. **Identify Gaps** - Tab 2
5. **Work the Queue** - Tab 3
6. **Track Progress** - Tab 4

### Registry Health Metrics

**Status Distribution:**
- Draft count and percentage
- Under Review count
- Approved count
- Superseded count
- Visual bar chart

**Recent Activity (7 days):**
- Captured impacts
- Modified impacts
- Approved impacts
- Drill-through to view

**Enrichment Quality:**
- Average enrichment score (🟢🟡🔴)
- Well enriched count (≥70%)
- Partially enriched count (30-69%)
- Unenriched count (<30%)

### Coverage Metrics

**Six Coverage Dimensions:**

1. **Change Assets** - Impacts without change assets
2. **Source Evidence** - Impacts without evidence
3. **Stakeholder Groups** - Impacts without stakeholders
4. **Business Processes** - Impacts without processes
5. **Systems** - Impacts without systems
6. **Policies** - Impacts without policies (optional)

**For Each Dimension:**
- Count and percentage
- Color-coded indicator (🟢🟡🔴)
- "View" button to drill through
- Work queue display

### Practitioner Work Queue

**Five Queue Categories:**

**1. Awaiting Approval:**
- Impacts in "Under Review" status
- Review button → Impact Detail
- View all button → Analyze Workspace

**2. Needs Enrichment:**
- Draft impacts missing key relationships
- Enrich button → Enrichment Workspace
- View all button → Analyze Workspace

**3. Needs Coverage:**
- Impacts without change assets
- Add Assets button → Enrichment Workspace
- Top 10 displayed

**4. Recently Added (24h):**
- Impacts created in last 24 hours
- View button → Impact Detail
- Created timestamp

**5. Recently Modified (24h):**
- Impacts updated in last 24 hours
- View button → Impact Detail
- Updated timestamp

### Project Progress

**Four Progress Dimensions:**

**1. Capture Progress:**
- Total impacts captured
- Capture rate (impacts/day)
- Project timeline progress bar

**2. Approval Progress:**
- Approved count
- Approval percentage
- Progress bar with color coding

**3. Enrichment Progress:**
- Average enrichment score
- Well enriched count
- Progress bar with color coding

**4. Coverage Progress:**
- Impacts with coverage
- Coverage percentage
- Progress bar with color coding

**Registry Completeness:**
- Overall completeness score
- Five completeness factors
- Progress bar
- Factor breakdown

## Navigation

**Every metric drills directly into associated Impact records:**

- "View Recently Captured" → Analyze Workspace (filtered)
- "View All Awaiting Approval" → Analyze Workspace (status filter)
- "View All Needing Enrichment" → Analyze Workspace (draft filter)
- Coverage gap "View" → Work queue display
- Work queue "Enrich" → Enrichment Workspace (specific impact)
- Work queue "Review" → Impact Detail (specific impact)
- Recently added/modified "View" → Impact Detail

## User Experience Principles

✅ **The Monitor Workspace should answer one question: "What should I work on next?"**  
✅ **Every indicator should be actionable** - All metrics have drill-through or action buttons  
✅ **No decorative dashboards** - Every element serves a purpose  

## Acceptance Criteria

✅ **Met:** Using real project data, a practitioner can immediately identify the highest-value activities required to improve the quality and completeness of the Impact Registry.

### Additional Achievements

- **Four comprehensive tabs** - Health, Gaps, Queue, Progress
- **Actionable metrics** - Every indicator has action
- **Color-coded indicators** - Visual health signals
- **Work queue display** - Inline task lists
- **Progress tracking** - Multiple dimensions
- **Completeness score** - Overall registry quality

## Engineering Notes

### Design Decisions

1. **Four-Tab Organization**
   - Registry Health (diagnostic)
   - Coverage Gaps (identification)
   - Work Queue (action)
   - Progress Tracking (trends)
   - Logical practitioner workflow

2. **Color-Coded Indicators**
   - 🟢 Green: <20% gap (good)
   - 🟡 Yellow: 20-50% gap (fair)
   - 🔴 Red: >50% gap (needs attention)
   - Visual health signals

3. **Work Queue Integration**
   - Inline display in Coverage Gaps tab
   - Direct enrichment links
   - Top 20 impacts shown
   - Session state management

4. **Progress Bars**
   - Visual progress indicators
   - Percentage display
   - Color-coded thresholds
   - Immediate feedback

5. **Enrichment Score Calculation**
   - Same algorithm as Enrichment Workspace
   - Six dimensions (title, 4 asset types, change assets)
   - Average across all impacts
   - Distribution analysis

6. **Completeness Score**
   - Five factors weighted equally
   - Impacts captured, approval rate, enrichment, coverage, evidence
   - Overall registry quality metric
   - Factor breakdown

### Technical Implementation

**Enrichment Score Calculation:**
```python
enrichment_scores = []
for impact in impacts:
    score = 0
    max_score = 6
    
    if impact.title and impact.title.strip():
        score += 1
    if len(impact.stakeholder_group_ids) > 0:
        score += 1
    if len(impact.organization_unit_ids) > 0:
        score += 1
    if len(impact.business_process_ids) > 0:
        score += 1
    if len(impact.system_ids) > 0:
        score += 1
    
    change_assets = repo.list_change_assets(impact.id)
    if len(change_assets) > 0:
        score += 1
    
    score_pct = (score / max_score) * 100
    enrichment_scores.append(score_pct)

avg_enrichment = sum(enrichment_scores) / len(enrichment_scores)
```

**Coverage Gap Analysis:**
```python
no_change_assets = []
for impact in impacts:
    change_assets = repo.list_change_assets(impact.id)
    if len(change_assets) == 0:
        no_change_assets.append(impact)

pct = (len(no_change_assets) / len(impacts)) * 100
if pct > 50:
    st.error(f"🔴 {len(no_change_assets)} impacts without change assets")
elif pct > 20:
    st.warning(f"🟡 {len(no_change_assets)} impacts without change assets")
else:
    st.success(f"🟢 {len(no_change_assets)} impacts without change assets")
```

**Work Queue Display:**
```python
if 'work_queue' in st.session_state:
    queue_impacts = queue_map.get(st.session_state['work_queue'], [])
    
    for impact in queue_impacts[:20]:
        if st.button("Enrich", key=f"enrich_queue_{impact.id}"):
            st.session_state['edit_impact_id'] = impact.id
            st.switch_page("pages/07_Enrichment_Workspace.py")
```

**Completeness Score:**
```python
completeness_factors = {
    'Impacts Captured': (len(impacts) > 0, 1.0),
    'Approval Rate': (approval_pct >= 50, approval_pct / 100),
    'Enrichment Quality': (avg_enrichment >= 50, avg_enrichment / 100),
    'Coverage Rate': (coverage_pct >= 50, coverage_pct / 100),
    'Source Evidence': (len(no_source_evidence) < len(impacts) * 0.5, 
                       1 - (len(no_source_evidence) / len(impacts)))
}

completeness_score = sum([score for _, score in completeness_factors.values()]) / len(completeness_factors) * 100
```

## Integration with Other Workspaces

### Monitor → Enrichment Workspace
- Work queue "Enrich" buttons
- Direct to specific impact
- Close enrichment loop

### Monitor → Impact Detail
- Work queue "Review" buttons
- Recently added/modified "View" buttons
- Detailed impact review

### Monitor → Analyze Workspace
- "View All" buttons
- Drill-through with filters
- Broader analysis

## Testing Checklist

- [x] View registry health metrics
- [x] View status distribution
- [x] View recent activity
- [x] View enrichment quality
- [x] View coverage gaps
- [x] Click coverage gap "View" button
- [x] View work queue inline
- [x] Click "Enrich" from work queue
- [x] View awaiting approval queue
- [x] Click "Review" from queue
- [x] View recently added impacts
- [x] View recently modified impacts
- [x] View capture progress
- [x] View approval progress
- [x] View enrichment progress
- [x] View coverage progress
- [x] View registry completeness score

## Success Metrics

**Adoption:**
- Monitor Workspace checked daily by practitioners
- Work queue used for >60% of enrichment activities
- Coverage gaps addressed within 48 hours

**Efficiency:**
- Time to identify next task: <30 seconds
- Work queue completion rate: >70%
- Registry health improvement: measurable

**Quality:**
- Average enrichment score: trending up
- Coverage gaps: trending down
- Completeness score: >70%

## Best Practices

### For Change Managers

1. **Check daily** - Monitor registry health regularly
2. **Work the queue** - Focus on highest-value activities
3. **Track trends** - Monitor progress over time
4. **Address gaps** - Use coverage analysis to prioritize
5. **Celebrate progress** - Acknowledge improvements

### For Practitioners

1. **Start with work queue** - Know what to work on
2. **Drill through** - Click metrics to see details
3. **Enrich systematically** - Work through queues
4. **Check completeness** - Aim for >70% score
5. **Use color codes** - Red = urgent, Yellow = soon, Green = good

## Common Workflows

### Workflow 1: Daily Health Check

```
Scenario: Daily registry monitoring

1. Navigate to Monitor Workspace
2. Review top metrics (Total, Draft, Approved)
3. Tab 1: Check enrichment quality
4. Tab 2: Review coverage gaps
5. Tab 3: Identify work queue priorities
6. Tab 4: Track progress trends
7. Time: 2-3 minutes
8. Result: Clear understanding of registry health
```

### Workflow 2: Work Queue Processing

```
Scenario: Address coverage gaps

1. Go to Monitor Workspace
2. Tab 2 (Coverage Gaps): See 15 impacts without change assets
3. Click "View" button
4. Work queue displays 15 impacts
5. Click "Enrich" on first impact
6. Add change assets in Enrichment Workspace
7. Return to Monitor Workspace
8. Repeat for remaining impacts
9. Result: Coverage gap reduced
```

### Workflow 3: Approval Processing

```
Scenario: Process pending approvals

1. Go to Monitor Workspace
2. Tab 3 (Work Queue): See 8 impacts awaiting approval
3. Click "Review" on first impact
4. Impact Detail opens
5. Review completeness
6. Return to Enrichment Workspace to approve
7. Repeat for remaining impacts
8. Result: Approval queue cleared
```

## Explicitly Out of Scope

- ❌ People monitoring
- ❌ Execution tracking
- ❌ Resource allocation
- ❌ Budget tracking
- ❌ Timeline management
- ❌ Stakeholder engagement metrics

**Rationale:** Monitor Workspace focuses on registry quality, not project execution. Executive reporting belongs in Analyze Workspace.

## Future Enhancements (Deferred)

- Trend charts over time
- Automated alerts
- Email notifications
- Custom work queues
- Team assignments
- SLA tracking
- Quality gates
- Automated recommendations

## Conclusion

WPP-009 successfully implements a Monitor Workspace that provides continuous visibility into registry health, completeness, and maturity. The workspace enables practitioners to immediately identify highest-value activities through actionable metrics, work queues, and progress tracking.

**Key Achievement:** Practitioners can immediately identify the highest-value activities required to improve registry quality and completeness, meeting the acceptance criteria and providing operational monitoring focused on the registry itself.

**Design Philosophy Realized:** "Monitor the registry. Do not monitor people. Do not monitor execution." The Monitor Workspace focuses exclusively on registry quality, providing actionable insights without tracking individual performance or project execution.

**Operational Focus:** The workspace is designed for practitioners and change managers, providing daily operational visibility. Executive reporting and strategic analysis remain in the Analyze Workspace, maintaining clear separation of concerns.

The implementation meets all acceptance criteria and provides the operational monitoring foundation that enables continuous registry improvement through clear, actionable work queues and health metrics.
