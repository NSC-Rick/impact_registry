import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database.schema import init_db, get_session, get_engine
from services.repository import Repository

st.set_page_config(page_title="Monitor Workspace", page_icon="📊", layout="wide")

engine = init_db()
session = get_session(engine)
repo = Repository(session)

st.title("📊 Monitor Workspace")
st.markdown("### Registry Health & Practitioner Work Queues")

if 'current_project_id' not in st.session_state:
    st.warning("⚠️ Please select or create a project in the Setup page first")
    st.stop()

project_id = st.session_state['current_project_id']
project = repo.get_project(project_id)

st.info(f"📁 **Project:** {project.name}")

impacts = repo.list_impacts(project_id)

if not impacts:
    st.warning("⚠️ No impacts captured yet. Start with the Capture Workspace.")
    st.stop()

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📋 Total Impacts", len(impacts))

with col2:
    draft_count = len([i for i in impacts if i.status == "Draft"])
    st.metric("📝 Draft", draft_count)

with col3:
    approved_count = len([i for i in impacts if i.status == "Approved"])
    st.metric("✅ Approved", approved_count)

with col4:
    superseded_count = len([i for i in impacts if i.status == "Superseded"])
    st.metric("🔄 Superseded", superseded_count)

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "🏥 Registry Health",
    "📦 Coverage Gaps",
    "📋 Work Queue",
    "📈 Progress Tracking"
])

with tab1:
    st.markdown("### Registry Health Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Status Distribution")
        
        status_counts = {}
        for impact in impacts:
            status_counts[impact.status] = status_counts.get(impact.status, 0) + 1
        
        if status_counts:
            df = pd.DataFrame([
                {'Status': k, 'Count': v}
                for k, v in sorted(status_counts.items(), key=lambda x: x[1], reverse=True)
            ])
            
            st.bar_chart(df.set_index('Status'))
            
            for _, row in df.iterrows():
                pct = (row['Count'] / len(impacts)) * 100
                st.caption(f"**{row['Status']}**: {row['Count']} ({pct:.0f}%)")
    
    with col2:
        st.markdown("#### 🕐 Recent Activity")
        
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        
        recently_captured = [i for i in impacts if i.created_at and i.created_at >= week_ago]
        recently_modified = [i for i in impacts if i.updated_at and i.updated_at >= week_ago and i.updated_at != i.created_at]
        recently_approved = [i for i in impacts if i.status == "Approved" and i.updated_at and i.updated_at >= week_ago]
        
        st.metric("📥 Captured (7 days)", len(recently_captured))
        st.metric("✏️ Modified (7 days)", len(recently_modified))
        st.metric("✅ Approved (7 days)", len(recently_approved))
        
        if recently_captured:
            if st.button("🔍 View Recently Captured", use_container_width=True):
                st.session_state['drill_through_filter'] = {'recent_capture': True}
                st.switch_page("pages/08_Analyze_Workspace.py")
    
    st.markdown("---")
    
    st.markdown("#### 📈 Enrichment Quality")
    
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
    
    avg_enrichment = sum(enrichment_scores) / len(enrichment_scores) if enrichment_scores else 0
    
    well_enriched = len([s for s in enrichment_scores if s >= 70])
    partially_enriched = len([s for s in enrichment_scores if 30 <= s < 70])
    unenriched = len([s for s in enrichment_scores if s < 30])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if avg_enrichment >= 70:
            st.metric("Average Enrichment", f"🟢 {avg_enrichment:.0f}%", "Excellent")
        elif avg_enrichment >= 30:
            st.metric("Average Enrichment", f"🟡 {avg_enrichment:.0f}%", "Fair")
        else:
            st.metric("Average Enrichment", f"🔴 {avg_enrichment:.0f}%", "Needs Work")
    
    with col2:
        st.metric("🟢 Well Enriched", well_enriched, f"{(well_enriched/len(impacts)*100):.0f}%")
    
    with col3:
        st.metric("🟡 Partial", partially_enriched, f"{(partially_enriched/len(impacts)*100):.0f}%")
    
    with col4:
        st.metric("🔴 Unenriched", unenriched, f"{(unenriched/len(impacts)*100):.0f}%")

with tab2:
    st.markdown("### Coverage Gap Analysis")
    
    st.markdown("**Identify impacts requiring additional enrichment:**")
    
    no_change_assets = []
    no_source_evidence = []
    no_stakeholders = []
    no_business_process = []
    no_system = []
    no_policy = []
    
    for impact in impacts:
        change_assets = repo.list_change_assets(impact.id)
        evidences = repo.list_source_evidences(impact.id)
        
        if len(change_assets) == 0:
            no_change_assets.append(impact)
        if len(evidences) == 0:
            no_source_evidence.append(impact)
        if len(impact.stakeholder_group_ids) == 0:
            no_stakeholders.append(impact)
        if len(impact.business_process_ids) == 0:
            no_business_process.append(impact)
        if len(impact.system_ids) == 0:
            no_system.append(impact)
        if len(impact.policy_ids) == 0:
            no_policy.append(impact)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📦 Change Asset Coverage")
        
        with st.container():
            col_a, col_b = st.columns([3, 1])
            with col_a:
                pct = (len(no_change_assets) / len(impacts)) * 100 if impacts else 0
                if pct > 50:
                    st.error(f"🔴 **{len(no_change_assets)} impacts** without change assets ({pct:.0f}%)")
                elif pct > 20:
                    st.warning(f"🟡 **{len(no_change_assets)} impacts** without change assets ({pct:.0f}%)")
                else:
                    st.success(f"🟢 **{len(no_change_assets)} impacts** without change assets ({pct:.0f}%)")
            with col_b:
                if no_change_assets and st.button("View", key="view_no_assets"):
                    st.session_state['work_queue'] = 'no_change_assets'
                    st.rerun()
        
        st.markdown("#### 📚 Source Evidence")
        
        with st.container():
            col_a, col_b = st.columns([3, 1])
            with col_a:
                pct = (len(no_source_evidence) / len(impacts)) * 100 if impacts else 0
                if pct > 50:
                    st.error(f"🔴 **{len(no_source_evidence)} impacts** without source evidence ({pct:.0f}%)")
                elif pct > 20:
                    st.warning(f"🟡 **{len(no_source_evidence)} impacts** without source evidence ({pct:.0f}%)")
                else:
                    st.success(f"🟢 **{len(no_source_evidence)} impacts** without source evidence ({pct:.0f}%)")
            with col_b:
                if no_source_evidence and st.button("View", key="view_no_evidence"):
                    st.session_state['work_queue'] = 'no_source_evidence'
                    st.rerun()
        
        st.markdown("#### 👥 Stakeholder Groups")
        
        with st.container():
            col_a, col_b = st.columns([3, 1])
            with col_a:
                pct = (len(no_stakeholders) / len(impacts)) * 100 if impacts else 0
                if pct > 50:
                    st.error(f"🔴 **{len(no_stakeholders)} impacts** without stakeholders ({pct:.0f}%)")
                elif pct > 20:
                    st.warning(f"🟡 **{len(no_stakeholders)} impacts** without stakeholders ({pct:.0f}%)")
                else:
                    st.success(f"🟢 **{len(no_stakeholders)} impacts** without stakeholders ({pct:.0f}%)")
            with col_b:
                if no_stakeholders and st.button("View", key="view_no_sg"):
                    st.session_state['work_queue'] = 'no_stakeholders'
                    st.rerun()
    
    with col2:
        st.markdown("#### 🔄 Business Processes")
        
        with st.container():
            col_a, col_b = st.columns([3, 1])
            with col_a:
                pct = (len(no_business_process) / len(impacts)) * 100 if impacts else 0
                if pct > 50:
                    st.error(f"🔴 **{len(no_business_process)} impacts** without business process ({pct:.0f}%)")
                elif pct > 20:
                    st.warning(f"🟡 **{len(no_business_process)} impacts** without business process ({pct:.0f}%)")
                else:
                    st.success(f"🟢 **{len(no_business_process)} impacts** without business process ({pct:.0f}%)")
            with col_b:
                if no_business_process and st.button("View", key="view_no_bp"):
                    st.session_state['work_queue'] = 'no_business_process'
                    st.rerun()
        
        st.markdown("#### 💻 Systems")
        
        with st.container():
            col_a, col_b = st.columns([3, 1])
            with col_a:
                pct = (len(no_system) / len(impacts)) * 100 if impacts else 0
                if pct > 50:
                    st.error(f"🔴 **{len(no_system)} impacts** without system ({pct:.0f}%)")
                elif pct > 20:
                    st.warning(f"🟡 **{len(no_system)} impacts** without system ({pct:.0f}%)")
                else:
                    st.success(f"🟢 **{len(no_system)} impacts** without system ({pct:.0f}%)")
            with col_b:
                if no_system and st.button("View", key="view_no_sys"):
                    st.session_state['work_queue'] = 'no_system'
                    st.rerun()
        
        st.markdown("#### 📋 Policies (Optional)")
        
        with st.container():
            col_a, col_b = st.columns([3, 1])
            with col_a:
                pct = (len(no_policy) / len(impacts)) * 100 if impacts else 0
                st.info(f"ℹ️ **{len(no_policy)} impacts** without policy ({pct:.0f}%)")
                st.caption("Policies are optional for most impacts")
            with col_b:
                if no_policy and st.button("View", key="view_no_pol"):
                    st.session_state['work_queue'] = 'no_policy'
                    st.rerun()
    
    if 'work_queue' in st.session_state:
        st.markdown("---")
        st.markdown(f"### 📋 Work Queue: {st.session_state['work_queue'].replace('_', ' ').title()}")
        
        queue_map = {
            'no_change_assets': no_change_assets,
            'no_source_evidence': no_source_evidence,
            'no_stakeholders': no_stakeholders,
            'no_business_process': no_business_process,
            'no_system': no_system,
            'no_policy': no_policy
        }
        
        queue_impacts = queue_map.get(st.session_state['work_queue'], [])
        
        if queue_impacts:
            st.markdown(f"**{len(queue_impacts)} impacts require attention:**")
            
            for impact in queue_impacts[:20]:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"- **{impact.impact_number}**: {impact.title or impact.description[:60]} ({impact.status})")
                with col2:
                    if st.button("Enrich", key=f"enrich_queue_{impact.id}"):
                        st.session_state['edit_impact_id'] = impact.id
                        st.switch_page("pages/07_Enrichment_Workspace.py")
            
            if len(queue_impacts) > 20:
                st.caption(f"... and {len(queue_impacts) - 20} more")
            
            if st.button("🔙 Back to Coverage Gaps"):
                del st.session_state['work_queue']
                st.rerun()

with tab3:
    st.markdown("### Practitioner Work Queue")
    
    st.markdown("**What should I work on next?**")
    
    awaiting_approval = [i for i in impacts if i.status == "Under Review"]
    needs_enrichment = [i for i in impacts if i.status == "Draft" and (
        len(i.stakeholder_group_ids) == 0 or
        len(i.business_process_ids) == 0 or
        len(repo.list_change_assets(i.id)) == 0
    )]
    needs_coverage = no_change_assets[:10]
    
    now = datetime.now()
    day_ago = now - timedelta(days=1)
    recently_added = [i for i in impacts if i.created_at and i.created_at >= day_ago]
    recently_modified = [i for i in impacts if i.updated_at and i.updated_at >= day_ago and i.updated_at != i.created_at]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 👀 Awaiting Approval")
        
        if awaiting_approval:
            st.warning(f"**{len(awaiting_approval)} impacts** awaiting approval")
            
            for impact in awaiting_approval[:5]:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"- **{impact.impact_number}**: {impact.title or impact.description[:50]}")
                with col_b:
                    if st.button("Review", key=f"review_{impact.id}"):
                        st.session_state['detail_impact_id'] = impact.id
                        st.switch_page("pages/12_Impact_Detail.py")
            
            if len(awaiting_approval) > 5:
                st.caption(f"... and {len(awaiting_approval) - 5} more")
                if st.button("🔍 View All Awaiting Approval"):
                    st.session_state['drill_through_filter'] = {'status': 'Under Review'}
                    st.switch_page("pages/08_Analyze_Workspace.py")
        else:
            st.success("✅ No impacts awaiting approval")
        
        st.markdown("#### 🔧 Needs Enrichment")
        
        if needs_enrichment:
            st.warning(f"**{len(needs_enrichment)} draft impacts** need enrichment")
            
            for impact in needs_enrichment[:5]:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"- **{impact.impact_number}**: {impact.title or impact.description[:50]}")
                with col_b:
                    if st.button("Enrich", key=f"enrich_ne_{impact.id}"):
                        st.session_state['edit_impact_id'] = impact.id
                        st.switch_page("pages/07_Enrichment_Workspace.py")
            
            if len(needs_enrichment) > 5:
                st.caption(f"... and {len(needs_enrichment) - 5} more")
                if st.button("🔍 View All Needing Enrichment"):
                    st.session_state['drill_through_filter'] = {'status': 'Draft', 'needs_enrichment': True}
                    st.switch_page("pages/08_Analyze_Workspace.py")
        else:
            st.success("✅ All draft impacts are enriched")
        
        st.markdown("#### 📦 Needs Coverage")
        
        if needs_coverage:
            st.warning(f"**{len(no_change_assets)} impacts** without change assets")
            
            for impact in needs_coverage[:5]:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"- **{impact.impact_number}**: {impact.title or impact.description[:50]}")
                with col_b:
                    if st.button("Add Assets", key=f"coverage_{impact.id}"):
                        st.session_state['edit_impact_id'] = impact.id
                        st.switch_page("pages/07_Enrichment_Workspace.py")
            
            if len(no_change_assets) > 5:
                st.caption(f"... and {len(no_change_assets) - 5} more")
        else:
            st.success("✅ All impacts have change asset coverage")
    
    with col2:
        st.markdown("#### 🆕 Recently Added (24h)")
        
        if recently_added:
            st.info(f"**{len(recently_added)} impacts** added in last 24 hours")
            
            for impact in recently_added[:5]:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"- **{impact.impact_number}**: {impact.title or impact.description[:50]}")
                    st.caption(f"Created: {impact.created_at.strftime('%Y-%m-%d %H:%M')}")
                with col_b:
                    if st.button("View", key=f"view_new_{impact.id}"):
                        st.session_state['detail_impact_id'] = impact.id
                        st.switch_page("pages/12_Impact_Detail.py")
            
            if len(recently_added) > 5:
                st.caption(f"... and {len(recently_added) - 5} more")
        else:
            st.caption("No impacts added in last 24 hours")
        
        st.markdown("#### ✏️ Recently Modified (24h)")
        
        if recently_modified:
            st.info(f"**{len(recently_modified)} impacts** modified in last 24 hours")
            
            for impact in recently_modified[:5]:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"- **{impact.impact_number}**: {impact.title or impact.description[:50]}")
                    st.caption(f"Updated: {impact.updated_at.strftime('%Y-%m-%d %H:%M')}")
                with col_b:
                    if st.button("View", key=f"view_mod_{impact.id}"):
                        st.session_state['detail_impact_id'] = impact.id
                        st.switch_page("pages/12_Impact_Detail.py")
            
            if len(recently_modified) > 5:
                st.caption(f"... and {len(recently_modified) - 5} more")
        else:
            st.caption("No impacts modified in last 24 hours")

with tab4:
    st.markdown("### Project Progress Tracking")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📥 Capture Progress")
        
        total_impacts = len(impacts)
        st.metric("Total Impacts Captured", total_impacts)
        
        if project.start_date and project.end_date:
            project_duration = (project.end_date - project.start_date).days
            days_elapsed = (datetime.now().date() - project.start_date).days
            
            if days_elapsed > 0 and project_duration > 0:
                capture_rate = total_impacts / days_elapsed
                st.metric("Capture Rate", f"{capture_rate:.1f} impacts/day")
                
                progress_pct = min((days_elapsed / project_duration) * 100, 100)
                st.progress(progress_pct / 100)
                st.caption(f"Project {progress_pct:.0f}% complete by time")
        
        st.markdown("#### ✅ Approval Progress")
        
        approval_pct = (approved_count / total_impacts * 100) if total_impacts else 0
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Approved", approved_count)
        with col_b:
            st.metric("Approval %", f"{approval_pct:.0f}%")
        
        st.progress(approval_pct / 100)
        
        if approval_pct >= 80:
            st.success("🟢 Excellent approval rate")
        elif approval_pct >= 50:
            st.warning("🟡 Fair approval rate")
        else:
            st.error("🔴 Low approval rate - review needed")
    
    with col2:
        st.markdown("#### 🔗 Enrichment Progress")
        
        avg_enrichment = sum(enrichment_scores) / len(enrichment_scores) if enrichment_scores else 0
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Avg Enrichment", f"{avg_enrichment:.0f}%")
        with col_b:
            st.metric("Well Enriched", well_enriched)
        
        st.progress(avg_enrichment / 100)
        
        if avg_enrichment >= 70:
            st.success("🟢 Excellent enrichment quality")
        elif avg_enrichment >= 30:
            st.warning("🟡 Fair enrichment quality")
        else:
            st.error("🔴 Low enrichment quality - work needed")
        
        st.markdown("#### 📦 Coverage Progress")
        
        with_coverage = len(impacts) - len(no_change_assets)
        coverage_pct = (with_coverage / len(impacts) * 100) if impacts else 0
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("With Coverage", with_coverage)
        with col_b:
            st.metric("Coverage %", f"{coverage_pct:.0f}%")
        
        st.progress(coverage_pct / 100)
        
        if coverage_pct >= 80:
            st.success("🟢 Excellent coverage")
        elif coverage_pct >= 50:
            st.warning("🟡 Fair coverage")
        else:
            st.error("🔴 Low coverage - assets needed")
    
    st.markdown("---")
    
    st.markdown("#### 📊 Registry Completeness")
    
    completeness_factors = {
        'Impacts Captured': (len(impacts) > 0, 1.0),
        'Approval Rate': (approval_pct >= 50, approval_pct / 100),
        'Enrichment Quality': (avg_enrichment >= 50, avg_enrichment / 100),
        'Coverage Rate': (coverage_pct >= 50, coverage_pct / 100),
        'Source Evidence': (len(no_source_evidence) < len(impacts) * 0.5, 1 - (len(no_source_evidence) / len(impacts)))
    }
    
    completeness_score = sum([score for _, score in completeness_factors.values()]) / len(completeness_factors) * 100
    
    st.metric("Overall Registry Completeness", f"{completeness_score:.0f}%")
    st.progress(completeness_score / 100)
    
    st.markdown("**Completeness Factors:**")
    for factor, (passing, score) in completeness_factors.items():
        emoji = "✅" if passing else "⚠️"
        st.caption(f"{emoji} {factor}: {score * 100:.0f}%")

st.markdown("---")
st.markdown("### 💡 Monitor Workspace Tips")
st.markdown("""
- **Check daily** - Monitor registry health regularly
- **Work the queue** - Focus on highest-value activities
- **Drill through** - Click metrics to see specific impacts
- **Track progress** - Monitor enrichment and coverage trends
- **Identify gaps** - Use coverage analysis to prioritize work
- **Operational focus** - This workspace is for practitioners, not executives
""")
