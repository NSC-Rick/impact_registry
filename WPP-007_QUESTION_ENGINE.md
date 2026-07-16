# WPP-007: Question Engine

**Version:** Discovery.WPP-007.0  
**Status:** Implemented  
**Date:** 2024-07-16

## Objective

Provide a unified interface for exploring the Impact Registry through meaningful business questions rather than reports.

**The Question Engine transforms the registry into an organizational knowledge system.**

## Design Philosophy

**Users should ask questions.**

**The registry should answer them.**

Every Registry Object exists because someone will eventually ask about it.

## Implementation Summary

### Question Categories Implemented

✅ **Impact Questions** - Status, counts, summaries  
✅ **Enterprise Asset Questions** - Systems, stakeholders, processes, policies  
✅ **Coverage Questions** - Change assets, source evidence, gaps  
✅ **Registry Health Questions** - Quality metrics, completeness  
✅ **Relationship Questions** - Cross-entity connections  

### Question Types

**Summary:**
- How many approved impacts exist?
- Which Systems are changing?

**Detail:**
- Which impacts have no Change Assets?
- Which impacts have no Source Evidence?

**Relationship:**
- Which Systems affect Hiring Managers?
- Which Business Processes affect Finance?
- Which Change Assets support Time Approval?

**Coverage:**
- Which impacts have no coverage?
- What percentage of impacts have coverage?

## Navigation Flow

```
Summary
    ↓
Relationship
    ↓
Impact
    ↓
Impact Detail
```

**Every answer supports drill-through:**
- Click "View" → Navigate to Analyze Workspace
- Click "Enrich" → Navigate to Enrichment Workspace
- Results are clickable and explorable

## File Structure

```
pages/
└── 11_Question_Engine.py    # Question-based exploration (500+ lines)
```

## Usage Guide

### Quick Start

1. **Navigate to Question Engine** (page 11)
2. **Browse Questions** - Five category tabs
3. **Click Question** - See answer immediately
4. **Explore Results** - Drill through to details
5. **Pin Favorites** - Save frequently asked questions

### Example Questions Implemented

**Impact Questions:**
- How many approved impacts exist?
- How many draft impacts exist?
- How many impacts are under review?
- How many impacts have been superseded?

**Enterprise Asset Questions:**
- Which Systems are changing?
- Which Stakeholder Groups are most affected?
- Which Policies are changing?
- Which Business Processes have the greatest concentration of impacts?
- Which Organization Units are most impacted?

**Coverage Questions:**
- Which impacts have no Change Assets?
- Which impacts have no Source Evidence?
- Which impacts have no Stakeholder Groups?
- Which impacts have complete coverage?

**Relationship Questions:**
- Which Systems affect [Stakeholder Group]?
- Which Business Processes affect [Stakeholder Group]?
- Which Change Assets support [Business Process]?

### Step-by-Step: Ask a Question

**Scenario: Find out which systems are changing**

```
1. Go to Question Engine
2. Click "Enterprise Asset Questions" tab
3. Click "Which Systems are changing?"
4. View answer: "5 systems are changing"
5. See bar chart of systems by impact count
6. Click "View" next to any system
7. Navigate to Analyze Workspace filtered to that system
8. Time: <30 seconds
```

### Step-by-Step: Find Coverage Gaps

**Scenario: Identify impacts without change assets**

```
1. Go to Question Engine
2. Click "Coverage Questions" tab
3. Click "Which impacts have no Change Assets?"
4. View answer: "12 impacts have no change assets"
5. See list of impacts without coverage
6. Click "Enrich" next to any impact
7. Navigate to Enrichment Workspace
8. Add change assets
9. Time: <1 minute to identify, varies to fix
```

### Step-by-Step: Understand Relationships

**Scenario: Find which systems affect Finance Team**

```
1. Go to Question Engine
2. Click "Relationship Questions" tab
3. Click "Which Systems affect Finance Team?"
4. View answer: "3 systems affect Finance Team"
5. See list: SAP ERP, Workday HCM, Salesforce CRM
6. Understand system-stakeholder relationships
7. Time: <20 seconds
```

## Search Experience

### Keyword Search
- Type keywords in sidebar
- Filters all questions across all categories
- Case-insensitive matching
- Real-time results

### Saved Questions
**Pinned Questions:**
- Click "Pin" button on any answer
- Appears in sidebar "Pinned Questions"
- Quick access to favorites
- Up to 5 shown in sidebar

**Recent Questions:**
- Automatically tracks last 10 questions
- Appears in sidebar "Recent Questions"
- One-click to re-ask
- Chronological order

## Practitioner Workflow

```
Ask Question
        ↓
View Results
        ↓
Explore Relationships
        ↓
Open Impact
        ↓
Continue Analysis
```

**Example Session:**
1. Ask: "Which impacts have no Change Assets?"
2. View: 12 impacts listed
3. Click "Enrich" on first impact
4. Add change assets in Enrichment Workspace
5. Return to Question Engine
6. Re-ask question
7. Verify: Now 11 impacts without coverage
8. Continue enrichment

## User Experience Principles

✅ **Questions should require minimal effort** - One-click to ask  
✅ **Search should be forgiving** - Keyword matching across all questions  
✅ **Results should encourage exploration** - Drill-through on every result  
✅ **Every result should be clickable** - Navigate to details or enrichment  

## Acceptance Criteria

✅ **Met:** Using real project data, a practitioner can answer meaningful organizational questions without exporting data to Excel.

### Additional Achievements

- **Five question categories** - Organized by type
- **Drill-through navigation** - Every answer is explorable
- **Pinned questions** - Save favorites
- **Recent questions** - Quick re-access
- **Keyword search** - Find questions fast
- **Visual answers** - Charts and tables
- **Relationship questions** - Dynamic based on data

## Engineering Notes

### Design Decisions

1. **Question-First Interface**
   - Browse questions, not reports
   - Natural language questions
   - Immediate answers
   - Exploration encouraged

2. **Five Category Tabs**
   - Impact Questions
   - Enterprise Asset Questions
   - Coverage Questions
   - Registry Health Questions
   - Relationship Questions
   - Logical grouping

3. **Dynamic Question Generation**
   - Relationship questions generated from data
   - "Which Systems affect [Stakeholder]?"
   - "Which Change Assets support [Process]?"
   - Adapts to project context

4. **Drill-Through Integration**
   - Every answer has "View" or "Enrich" buttons
   - Navigates to appropriate workspace
   - Sets drill-through filters
   - Seamless exploration

5. **Pin and Recent**
   - Session state persistence
   - Up to 10 recent questions
   - Unlimited pinned questions
   - Sidebar quick access

### Technical Implementation

**Question Answering:**
```python
def answer_question(question):
    add_to_recent(question)
    
    if question == "How many approved impacts exist?":
        approved = [i for i in impacts if i.status == "Approved"]
        st.markdown(f"### ✅ Answer: **{len(approved)} approved impacts**")
        
        # Show results with drill-through
        for impact in approved[:10]:
            if st.button("View", key=f"view_{impact.id}"):
                st.session_state['drill_through_filter'] = {'status': 'Approved'}
                st.switch_page("pages/08_Analyze_Workspace.py")
```

**Dynamic Relationship Questions:**
```python
# Generate questions based on actual data
if stakeholder_groups:
    for sg in stakeholder_groups[:5]:
        questions.append(f"Which Systems affect {sg.name}?")
        questions.append(f"Which Business Processes affect {sg.name}?")
```

**Pin/Recent Management:**
```python
def add_to_recent(question):
    if question not in st.session_state['recent_questions']:
        st.session_state['recent_questions'].insert(0, question)
        st.session_state['recent_questions'] = st.session_state['recent_questions'][:10]

def toggle_pin(question):
    if question in st.session_state['pinned_questions']:
        st.session_state['pinned_questions'].remove(question)
    else:
        st.session_state['pinned_questions'].append(question)
```

**Search Filtering:**
```python
filtered_questions = questions
if search_query:
    filtered_questions = [q for q in questions if search_query.lower() in q.lower()]
```

## Future AI Integration

**The Question Engine will become the natural entry point for AI-powered conversational analysis.**

**MVP Implementation:**
- Structured questions
- Pre-defined answers
- Click-based interaction

**Future Releases:**
- Natural language processing
- Conversational interface
- AI-generated insights
- Predictive questions
- Trend analysis

**Foundation for AI:**
- Question-answer pattern established
- Drill-through navigation proven
- User expectations set
- Data relationships mapped

## Integration with Other Workspaces

### Question Engine → Analyze Workspace
- Drill-through from answers
- Sets appropriate filters
- Seamless navigation

### Question Engine → Enrichment Workspace
- "Enrich" buttons on gap questions
- Direct to specific impact
- Close enrichment loop

### Question Engine → Enterprise Asset Registry
- Relationship questions
- Asset usage understanding
- Cross-reference validation

## Testing Checklist

- [x] Ask impact questions
- [x] Ask enterprise asset questions
- [x] Ask coverage questions
- [x] Ask relationship questions
- [x] Search questions by keyword
- [x] Pin question
- [x] Unpin question
- [x] Access recent questions
- [x] Drill through to Analyze Workspace
- [x] Drill through to Enrichment Workspace
- [x] View bar charts
- [x] View data tables
- [x] Dynamic question generation

## Success Metrics

**Adoption:**
- Question Engine used for >50% of exploratory analysis
- Average questions per session: 3-5
- Pinned questions per user: 2-4

**Efficiency:**
- Time to answer question: <30 seconds
- Questions answered without Excel: >90%
- Drill-through usage: >60%

**Quality:**
- Question relevance: >95%
- Answer accuracy: 100%
- User satisfaction: High

## Best Practices

### For Change Managers

1. **Start with questions** - Not reports
2. **Pin common questions** - Quick access
3. **Use for stakeholder meetings** - Live answers
4. **Explore relationships** - Understand connections
5. **Drill through** - Validate findings
6. **Share insights** - Question-based reporting

### For Project Teams

1. **Establish question library** - Common questions for project
2. **Use in status meetings** - Live data exploration
3. **Track over time** - Re-ask questions to see progress
4. **Identify gaps** - Coverage questions highlight work needed
5. **Understand relationships** - System-stakeholder connections

## Common Question Patterns

### Pattern 1: Status Summary
```
Question: "How many approved impacts exist?"
Answer: "34 approved impacts"
Action: View list, drill through to details
Use: Status reporting, progress tracking
```

### Pattern 2: Asset Analysis
```
Question: "Which Systems are changing?"
Answer: "5 systems are changing" + bar chart
Action: View impacts per system
Use: Technology impact assessment
```

### Pattern 3: Gap Identification
```
Question: "Which impacts have no Change Assets?"
Answer: "12 impacts have no change assets"
Action: Enrich impacts to add coverage
Use: Quality assurance, completeness checking
```

### Pattern 4: Relationship Exploration
```
Question: "Which Systems affect Finance Team?"
Answer: "3 systems: SAP ERP, Workday HCM, Salesforce CRM"
Action: Understand stakeholder-system connections
Use: Stakeholder analysis, communication planning
```

## Example Session Transcript

**Scenario: Executive Briefing Preparation**

```
1. Ask: "How many approved impacts exist?"
   Answer: "34 approved impacts"
   Pin question for future reference

2. Ask: "Which Stakeholder Groups are most affected?"
   Answer: "Finance Team with 18 impacts"
   Note top 3 groups for briefing

3. Ask: "Which Systems are changing?"
   Answer: "5 systems are changing"
   Review bar chart, note SAP ERP has most impacts

4. Ask: "Which impacts have no Change Assets?"
   Answer: "12 impacts have no change assets"
   Flag for follow-up enrichment

5. Ask: "Which Business Processes have the greatest concentration?"
   Answer: "Order to Cash with 26 impacts"
   Drill through to view specific impacts

Total time: ~5 minutes
Result: Complete briefing data without Excel
```

## Conclusion

WPP-007 successfully implements a Question Engine that transforms the Impact Registry into an organizational knowledge system. The engine enables practitioners to explore data through meaningful business questions rather than static reports, providing immediate answers with drill-through navigation for deeper exploration.

**Key Achievement:** Practitioners can answer meaningful organizational questions without exporting data to Excel, meeting the acceptance criteria and providing a natural, question-based interface for registry exploration.

**Design Philosophy Realized:** "Users should ask questions. The registry should answer them." The Question Engine embodies this philosophy by providing a question-first interface that encourages exploration and discovery rather than passive report consumption.

**Future Foundation:** The Question Engine establishes the pattern and user expectations for future AI-powered conversational analysis, providing a structured foundation that can evolve into natural language processing while maintaining the core question-answer paradigm.

The implementation meets all acceptance criteria and provides a public face for the Impact Registry that emphasizes questions over charts, exploration over reports, and organizational knowledge over raw data.
