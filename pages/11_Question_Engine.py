import streamlit as st
import pandas as pd
from datetime import datetime
from database.schema import init_db, get_session, get_engine
from services.repository import Repository

st.set_page_config(page_title="Question Engine", page_icon="❓", layout="wide")

engine = init_db()
session = get_session(engine)
repo = Repository(session)

st.title("❓ Question Engine")
st.markdown("### Ask Questions, Get Answers")

if 'current_project_id' not in st.session_state:
    st.warning("⚠️ Please select or create a project in the Setup page first")
    st.stop()

project_id = st.session_state['current_project_id']
project = repo.get_project(project_id)

st.info(f"📁 **Project:** {project.name}")

if 'recent_questions' not in st.session_state:
    st.session_state['recent_questions'] = []

if 'pinned_questions' not in st.session_state:
    st.session_state['pinned_questions'] = []

impacts = repo.list_impacts(project_id)
stakeholder_groups = repo.list_stakeholder_groups(project_id)
organization_units = repo.list_organization_units(project_id)
business_processes = repo.list_business_processes(project_id)
systems = repo.list_systems(project_id)
policies = repo.list_policies(project_id)

st.sidebar.markdown("### 🔍 Search Questions")

search_query = st.sidebar.text_input(
    "Search",
    placeholder="Type keywords...",
    help="Search across all questions"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⭐ Pinned Questions")

if st.session_state['pinned_questions']:
    for q in st.session_state['pinned_questions'][:5]:
        if st.sidebar.button(f"📌 {q}", key=f"pinned_{q}", use_container_width=True):
            st.session_state['selected_question'] = q
            st.rerun()
else:
    st.sidebar.caption("No pinned questions yet")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🕐 Recent Questions")

if st.session_state['recent_questions']:
    for q in st.session_state['recent_questions'][:5]:
        if st.sidebar.button(f"🕐 {q}", key=f"recent_{q}", use_container_width=True):
            st.session_state['selected_question'] = q
            st.rerun()
else:
    st.sidebar.caption("No recent questions yet")

def add_to_recent(question):
    if question not in st.session_state['recent_questions']:
        st.session_state['recent_questions'].insert(0, question)
        st.session_state['recent_questions'] = st.session_state['recent_questions'][:10]

def toggle_pin(question):
    if question in st.session_state['pinned_questions']:
        st.session_state['pinned_questions'].remove(question)
    else:
        st.session_state['pinned_questions'].append(question)

def answer_question(question):
    add_to_recent(question)
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown(f"### Q: {question}")
    
    with col2:
        if question in st.session_state['pinned_questions']:
            if st.button("📌 Unpin", key=f"unpin_{question}"):
                toggle_pin(question)
                st.rerun()
        else:
            if st.button("📌 Pin", key=f"pin_{question}"):
                toggle_pin(question)
                st.rerun()
    
    st.markdown("---")
    
    if question == "How many approved impacts exist?":
        approved = [i for i in impacts if i.status == "Approved"]
        st.markdown(f"### ✅ Answer: **{len(approved)} approved impacts**")
        
        if approved:
            st.markdown("**Approved Impacts:**")
            for impact in approved[:10]:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"- **{impact.impact_number}**: {impact.title or impact.description[:60]}")
                with col2:
                    if st.button("View", key=f"view_{impact.id}"):
                        st.session_state['drill_through_filter'] = {'status': 'Approved'}
                        st.switch_page("pages/08_Analyze_Workspace.py")
            
            if len(approved) > 10:
                st.caption(f"... and {len(approved) - 10} more")
                if st.button("🔍 View All Approved Impacts"):
                    st.session_state['drill_through_filter'] = {'status': 'Approved'}
                    st.switch_page("pages/08_Analyze_Workspace.py")
    
    elif question == "Which Systems are changing?":
        systems_with_impacts = []
        for sys in systems:
            count = sum(1 for i in impacts if sys.id in i.system_ids)
            if count > 0:
                systems_with_impacts.append({'System': sys.name, 'Impact Count': count})
        
        if systems_with_impacts:
            st.markdown(f"### ✅ Answer: **{len(systems_with_impacts)} systems are changing**")
            
            df = pd.DataFrame(systems_with_impacts)
            df = df.sort_values('Impact Count', ascending=False)
            
            st.bar_chart(df.set_index('System'))
            
            st.markdown("**Systems by Impact Count:**")
            for _, row in df.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"- **{row['System']}**: {row['Impact Count']} impacts")
                with col2:
                    if st.button("View", key=f"view_sys_{row['System']}"):
                        st.session_state['drill_through_filter'] = {'system': row['System']}
                        st.switch_page("pages/08_Analyze_Workspace.py")
        else:
            st.markdown("### ✅ Answer: **No systems have been linked to impacts yet**")
    
    elif question == "Which Stakeholder Groups are most affected?":
        sg_impacts = []
        for sg in stakeholder_groups:
            count = sum(1 for i in impacts if sg.id in i.stakeholder_group_ids)
            if count > 0:
                sg_impacts.append({
                    'Stakeholder Group': sg.name,
                    'Impact Count': count,
                    'Size': sg.size or 0,
                    'Influence': sg.influence or 'Not set'
                })
        
        if sg_impacts:
            df = pd.DataFrame(sg_impacts)
            df = df.sort_values('Impact Count', ascending=False)
            
            top_sg = df.iloc[0]
            st.markdown(f"### ✅ Answer: **{top_sg['Stakeholder Group']}** with {top_sg['Impact Count']} impacts")
            
            st.bar_chart(df.set_index('Stakeholder Group')['Impact Count'])
            
            st.markdown("**Top 5 Most Affected:**")
            for _, row in df.head(5).iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"- **{row['Stakeholder Group']}**: {row['Impact Count']} impacts (Size: {row['Size']}, Influence: {row['Influence']})")
                with col2:
                    if st.button("View", key=f"view_sg_{row['Stakeholder Group']}"):
                        st.session_state['drill_through_filter'] = {'stakeholder_group': row['Stakeholder Group']}
                        st.switch_page("pages/08_Analyze_Workspace.py")
        else:
            st.markdown("### ✅ Answer: **No stakeholder groups have been linked yet**")
    
    elif question == "Which Policies are changing?":
        policies_with_impacts = []
        for pol in policies:
            count = sum(1 for i in impacts if pol.id in i.policy_ids)
            if count > 0:
                policies_with_impacts.append({
                    'Policy': pol.name,
                    'Impact Count': count,
                    'Owner': pol.policy_owner or 'Not set'
                })
        
        if policies_with_impacts:
            st.markdown(f"### ✅ Answer: **{len(policies_with_impacts)} policies are changing**")
            
            df = pd.DataFrame(policies_with_impacts)
            df = df.sort_values('Impact Count', ascending=False)
            
            st.markdown("**Policies by Impact Count:**")
            for _, row in df.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"- **{row['Policy']}**: {row['Impact Count']} impacts (Owner: {row['Owner']})")
                with col2:
                    if st.button("View", key=f"view_pol_{row['Policy']}"):
                        st.session_state['drill_through_filter'] = {'policy': row['Policy']}
                        st.switch_page("pages/08_Analyze_Workspace.py")
        else:
            st.markdown("### ✅ Answer: **No policies have been linked to impacts yet**")
    
    elif question == "Which Business Processes have the greatest concentration of impacts?":
        bp_impacts = []
        for bp in business_processes:
            count = sum(1 for i in impacts if bp.id in i.business_process_ids)
            if count > 0:
                bp_impacts.append({
                    'Business Process': bp.name,
                    'Impact Count': count,
                    'Criticality': bp.criticality or 'Not set'
                })
        
        if bp_impacts:
            df = pd.DataFrame(bp_impacts)
            df = df.sort_values('Impact Count', ascending=False)
            
            top_bp = df.iloc[0]
            st.markdown(f"### ✅ Answer: **{top_bp['Business Process']}** with {top_bp['Impact Count']} impacts")
            
            st.bar_chart(df.set_index('Business Process')['Impact Count'])
            
            st.markdown("**Top 5 Processes:**")
            for _, row in df.head(5).iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"- **{row['Business Process']}**: {row['Impact Count']} impacts (Criticality: {row['Criticality']})")
                with col2:
                    if st.button("View", key=f"view_bp_{row['Business Process']}"):
                        st.session_state['drill_through_filter'] = {'business_process': row['Business Process']}
                        st.switch_page("pages/08_Analyze_Workspace.py")
        else:
            st.markdown("### ✅ Answer: **No business processes have been linked yet**")
    
    elif question == "Which impacts have no Change Assets?":
        no_coverage = []
        for impact in impacts:
            assets = repo.list_change_assets(impact.id)
            if len(assets) == 0:
                no_coverage.append(impact)
        
        st.markdown(f"### ✅ Answer: **{len(no_coverage)} impacts** have no change assets")
        
        if no_coverage:
            st.markdown("**Impacts Without Coverage:**")
            for impact in no_coverage[:10]:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"- **{impact.impact_number}**: {impact.title or impact.description[:60]} ({impact.status})")
                with col2:
                    if st.button("Enrich", key=f"enrich_{impact.id}"):
                        st.session_state['edit_impact_id'] = impact.id
                        st.switch_page("pages/07_Enrichment_Workspace.py")
            
            if len(no_coverage) > 10:
                st.caption(f"... and {len(no_coverage) - 10} more")
                if st.button("🔍 View All Impacts Without Coverage"):
                    st.session_state['drill_through_filter'] = {'no_coverage': True}
                    st.switch_page("pages/08_Analyze_Workspace.py")
    
    elif question == "Which impacts have no Source Evidence?":
        no_evidence = []
        for impact in impacts:
            evidences = repo.list_source_evidences(impact.id)
            if len(evidences) == 0:
                no_evidence.append(impact)
        
        st.markdown(f"### ✅ Answer: **{len(no_evidence)} impacts** have no source evidence")
        
        if no_evidence:
            st.markdown("**Impacts Without Evidence:**")
            for impact in no_evidence[:10]:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"- **{impact.impact_number}**: {impact.title or impact.description[:60]} ({impact.status})")
                with col2:
                    if st.button("Enrich", key=f"enrich_ev_{impact.id}"):
                        st.session_state['edit_impact_id'] = impact.id
                        st.switch_page("pages/07_Enrichment_Workspace.py")
            
            if len(no_evidence) > 10:
                st.caption(f"... and {len(no_evidence) - 10} more")
                if st.button("🔍 View All Impacts Without Evidence"):
                    st.session_state['drill_through_filter'] = {'no_evidence': True}
                    st.switch_page("pages/08_Analyze_Workspace.py")
    
    elif "Which Systems affect" in question:
        sg_name = question.replace("Which Systems affect ", "").replace("?", "")
        sg = next((s for s in stakeholder_groups if s.name == sg_name), None)
        
        if sg:
            related_impacts = [i for i in impacts if sg.id in i.stakeholder_group_ids]
            
            systems_set = set()
            for impact in related_impacts:
                for sys_id in impact.system_ids:
                    sys = next((s for s in systems if s.id == sys_id), None)
                    if sys:
                        systems_set.add(sys.name)
            
            st.markdown(f"### ✅ Answer: **{len(systems_set)} systems** affect {sg_name}")
            
            if systems_set:
                st.markdown(f"**Systems affecting {sg_name}:**")
                for sys_name in sorted(systems_set):
                    st.markdown(f"- {sys_name}")
        else:
            st.markdown(f"### ❌ Stakeholder Group '{sg_name}' not found")
    
    elif "Which Change Assets support" in question:
        bp_name = question.replace("Which Change Assets support ", "").replace("?", "")
        bp = next((b for b in business_processes if b.name == bp_name), None)
        
        if bp:
            related_impacts = [i for i in impacts if bp.id in i.business_process_ids]
            
            all_assets = []
            for impact in related_impacts:
                assets = repo.list_change_assets(impact.id)
                for asset in assets:
                    all_assets.append(asset.asset_type)
            
            asset_counts = {}
            for asset_type in all_assets:
                asset_counts[asset_type] = asset_counts.get(asset_type, 0) + 1
            
            st.markdown(f"### ✅ Answer: **{len(asset_counts)} asset types** support {bp_name}")
            
            if asset_counts:
                df = pd.DataFrame([
                    {'Asset Type': k, 'Count': v}
                    for k, v in sorted(asset_counts.items(), key=lambda x: x[1], reverse=True)
                ])
                
                st.bar_chart(df.set_index('Asset Type'))
                st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.markdown(f"### ❌ Business Process '{bp_name}' not found")
    
    elif "Which Business Processes affect" in question:
        sg_name = question.replace("Which Business Processes affect ", "").replace("?", "")
        sg = next((s for s in stakeholder_groups if s.name == sg_name), None)
        
        if sg:
            related_impacts = [i for i in impacts if sg.id in i.stakeholder_group_ids]
            
            bp_counts = {}
            for impact in related_impacts:
                for bp_id in impact.business_process_ids:
                    bp = next((b for b in business_processes if b.id == bp_id), None)
                    if bp:
                        bp_counts[bp.name] = bp_counts.get(bp.name, 0) + 1
            
            st.markdown(f"### ✅ Answer: **{len(bp_counts)} business processes** affect {sg_name}")
            
            if bp_counts:
                df = pd.DataFrame([
                    {'Business Process': k, 'Impact Count': v}
                    for k, v in sorted(bp_counts.items(), key=lambda x: x[1], reverse=True)
                ])
                
                st.bar_chart(df.set_index('Business Process'))
                
                st.markdown(f"**Processes affecting {sg_name}:**")
                for _, row in df.iterrows():
                    st.markdown(f"- **{row['Business Process']}**: {row['Impact Count']} impacts")
        else:
            st.markdown(f"### ❌ Stakeholder Group '{sg_name}' not found")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Impact Questions",
    "🏢 Enterprise Asset Questions",
    "📦 Coverage Questions",
    "🏥 Registry Health Questions",
    "🔗 Relationship Questions"
])

with tab1:
    st.markdown("### Impact Questions")
    
    questions = [
        "How many approved impacts exist?",
        "How many draft impacts exist?",
        "How many impacts are under review?",
        "How many impacts have been superseded?"
    ]
    
    filtered_questions = questions
    if search_query:
        filtered_questions = [q for q in questions if search_query.lower() in q.lower()]
    
    for question in filtered_questions:
        if st.button(f"❓ {question}", key=f"q1_{question}", use_container_width=True):
            st.session_state['selected_question'] = question
    
    if 'selected_question' in st.session_state and st.session_state['selected_question'] in questions:
        st.markdown("---")
        answer_question(st.session_state['selected_question'])

with tab2:
    st.markdown("### Enterprise Asset Questions")
    
    questions = [
        "Which Systems are changing?",
        "Which Stakeholder Groups are most affected?",
        "Which Policies are changing?",
        "Which Business Processes have the greatest concentration of impacts?",
        "Which Organization Units are most impacted?"
    ]
    
    if stakeholder_groups:
        for sg in stakeholder_groups[:5]:
            questions.append(f"Which Systems affect {sg.name}?")
            questions.append(f"Which Business Processes affect {sg.name}?")
    
    filtered_questions = questions
    if search_query:
        filtered_questions = [q for q in questions if search_query.lower() in q.lower()]
    
    for question in filtered_questions:
        if st.button(f"❓ {question}", key=f"q2_{question}", use_container_width=True):
            st.session_state['selected_question'] = question
    
    if 'selected_question' in st.session_state and st.session_state['selected_question'] in questions:
        st.markdown("---")
        answer_question(st.session_state['selected_question'])

with tab3:
    st.markdown("### Coverage Questions")
    
    questions = [
        "Which impacts have no Change Assets?",
        "Which impacts have no Source Evidence?",
        "Which impacts have no Stakeholder Groups?",
        "Which impacts have complete coverage?"
    ]
    
    if business_processes:
        for bp in business_processes[:5]:
            questions.append(f"Which Change Assets support {bp.name}?")
    
    filtered_questions = questions
    if search_query:
        filtered_questions = [q for q in questions if search_query.lower() in q.lower()]
    
    for question in filtered_questions:
        if st.button(f"❓ {question}", key=f"q3_{question}", use_container_width=True):
            st.session_state['selected_question'] = question
    
    if 'selected_question' in st.session_state and st.session_state['selected_question'] in questions:
        st.markdown("---")
        answer_question(st.session_state['selected_question'])

with tab4:
    st.markdown("### Registry Health Questions")
    
    questions = [
        "What is the overall registry health score?",
        "How many impacts have titles?",
        "How many impacts are enriched?",
        "What percentage of impacts have coverage?"
    ]
    
    filtered_questions = questions
    if search_query:
        filtered_questions = [q for q in questions if search_query.lower() in q.lower()]
    
    for question in filtered_questions:
        if st.button(f"❓ {question}", key=f"q4_{question}", use_container_width=True):
            st.session_state['selected_question'] = question

with tab5:
    st.markdown("### Relationship Questions")
    
    st.markdown("**Ask about relationships between:**")
    st.markdown("- Systems and Stakeholder Groups")
    st.markdown("- Business Processes and Stakeholder Groups")
    st.markdown("- Change Assets and Business Processes")
    st.markdown("- Policies and Organization Units")
    
    st.markdown("---")
    st.markdown("**Example Questions:**")
    
    if stakeholder_groups and systems:
        sg = stakeholder_groups[0]
        st.markdown(f"- Which Systems affect {sg.name}?")
    
    if stakeholder_groups and business_processes:
        sg = stakeholder_groups[0]
        st.markdown(f"- Which Business Processes affect {sg.name}?")
    
    if business_processes:
        bp = business_processes[0]
        st.markdown(f"- Which Change Assets support {bp.name}?")

st.markdown("---")
st.markdown("### 💡 Question Engine Tips")
st.markdown("""
- **Browse questions** - Organized by category
- **Search questions** - Type keywords to filter
- **Pin questions** - Save frequently asked questions
- **Drill through** - Click results to explore details
- **Ask relationships** - Understand how things connect
- **Use for reporting** - Answer stakeholder questions quickly
""")
