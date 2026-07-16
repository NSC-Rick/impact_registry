import streamlit as st
from datetime import datetime
from database.schema import init_db, get_session, get_engine
from services.repository import Repository

st.set_page_config(page_title="Impact Detail", page_icon="📄", layout="wide")

engine = init_db()
session = get_session(engine)
repo = Repository(session)

st.title("📄 Impact Detail Workspace")
st.markdown("### Comprehensive Impact Knowledge Page")

if 'current_project_id' not in st.session_state:
    st.warning("⚠️ Please select or create a project in the Setup page first")
    st.stop()

project_id = st.session_state['current_project_id']
project = repo.get_project(project_id)

impacts = repo.list_impacts(project_id)

if not impacts:
    st.warning("⚠️ No impacts found. Please capture impacts first.")
    st.stop()

if 'detail_impact_id' not in st.session_state:
    st.session_state['detail_impact_id'] = impacts[0].id

current_impact = repo.get_impact(st.session_state['detail_impact_id'])

if not current_impact:
    st.error("Impact not found")
    st.stop()

current_index = next((i for i, imp in enumerate(impacts) if imp.id == current_impact.id), 0)

col1, col2, col3, col4, col5 = st.columns([1, 1, 3, 1, 1])

with col1:
    if st.button("⬅️ Previous", use_container_width=True, disabled=current_index == 0):
        st.session_state['detail_impact_id'] = impacts[current_index - 1].id
        st.rerun()

with col2:
    if st.button("Next ➡️", use_container_width=True, disabled=current_index == len(impacts) - 1):
        st.session_state['detail_impact_id'] = impacts[current_index + 1].id
        st.rerun()

with col3:
    selected_impact = st.selectbox(
        "Select Impact",
        options=[f"{imp.impact_number} - {imp.title or imp.description[:50]}" for imp in impacts],
        index=current_index,
        label_visibility="collapsed"
    )
    
    if selected_impact:
        selected_index = next((i for i, imp in enumerate(impacts) 
                              if f"{imp.impact_number} - {imp.title or imp.description[:50]}" == selected_impact), 0)
        if selected_index != current_index:
            st.session_state['detail_impact_id'] = impacts[selected_index].id
            st.rerun()

with col4:
    if st.button("✏️ Enrich", use_container_width=True):
        st.session_state['edit_impact_id'] = current_impact.id
        st.switch_page("pages/07_Enrichment_Workspace.py")

with col5:
    if st.button("📊 Analyze", use_container_width=True):
        st.switch_page("pages/08_Analyze_Workspace.py")

st.markdown("---")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📋 Summary",
    "🏢 Enterprise Assets",
    "📦 Change Assets",
    "📚 Source Evidence",
    "🔗 Relationships",
    "📜 History & Notes"
])

with tab1:
    st.markdown("### Impact Summary")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"#### {current_impact.impact_number}")
        
        if current_impact.title:
            st.markdown(f"**{current_impact.title}**")
        
        st.markdown("**Description:**")
        st.write(current_impact.description)
        
        if current_impact.area_of_change:
            st.caption(f"**Area of Change:** {current_impact.area_of_change}")
    
    with col2:
        status_emoji = {
            "Draft": "📝",
            "Under Review": "👀",
            "Approved": "✅",
            "Superseded": "🔄"
        }
        st.metric("Status", f"{status_emoji.get(current_impact.status, '📄')} {current_impact.status}")
        
        if current_impact.created_at:
            st.caption(f"**Created:** {current_impact.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        if current_impact.updated_at:
            st.caption(f"**Updated:** {current_impact.updated_at.strftime('%Y-%m-%d %H:%M')}")
    
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if current_impact.severity:
            severity_emoji = {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}
            st.metric("Severity", f"{severity_emoji.get(current_impact.severity, '⚪')} {current_impact.severity}")
        else:
            st.caption("Severity: Not set")
    
    with col2:
        if current_impact.likelihood:
            st.metric("Likelihood", current_impact.likelihood)
        else:
            st.caption("Likelihood: Not set")
    
    with col3:
        if current_impact.readiness:
            st.metric("Readiness", current_impact.readiness)
        else:
            st.caption("Readiness: Not set")
    
    with col4:
        if current_impact.resistance:
            st.metric("Resistance", current_impact.resistance)
        else:
            st.caption("Resistance: Not set")
    
    if current_impact.mitigation_strategy:
        st.markdown("---")
        st.markdown("**Mitigation Strategy:**")
        st.write(current_impact.mitigation_strategy)

with tab2:
    st.markdown("### Enterprise Assets")
    
    stakeholder_groups = repo.list_stakeholder_groups(project_id)
    organization_units = repo.list_organization_units(project_id)
    business_processes = repo.list_business_processes(project_id)
    systems = repo.list_systems(project_id)
    policies = repo.list_policies(project_id)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 👥 Stakeholder Groups")
        
        if current_impact.stakeholder_group_ids:
            linked_sgs = [sg for sg in stakeholder_groups if sg.id in current_impact.stakeholder_group_ids]
            
            for sg in linked_sgs:
                with st.container():
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.markdown(f"**{sg.name}**")
                        if sg.description:
                            st.caption(sg.description)
                        st.caption(f"Size: {sg.size or 'Not set'} | Influence: {sg.influence or 'Not set'}")
                    with col_b:
                        if st.button("View", key=f"view_sg_{sg.id}"):
                            st.switch_page("pages/09_Enterprise_Asset_Registry.py")
                    st.markdown("---")
        else:
            st.info("No stakeholder groups linked")
        
        st.markdown("#### 🔄 Business Processes")
        
        if current_impact.business_process_ids:
            linked_bps = [bp for bp in business_processes if bp.id in current_impact.business_process_ids]
            
            for bp in linked_bps:
                with st.container():
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.markdown(f"**{bp.name}**")
                        if bp.description:
                            st.caption(bp.description)
                        st.caption(f"Owner: {bp.process_owner or 'Not set'} | Criticality: {bp.criticality or 'Not set'}")
                    with col_b:
                        if st.button("View", key=f"view_bp_{bp.id}"):
                            st.switch_page("pages/09_Enterprise_Asset_Registry.py")
                    st.markdown("---")
        else:
            st.info("No business processes linked")
        
        st.markdown("#### 📋 Policies")
        
        if current_impact.policy_ids:
            linked_pols = [pol for pol in policies if pol.id in current_impact.policy_ids]
            
            for pol in linked_pols:
                with st.container():
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.markdown(f"**{pol.name}**")
                        if pol.description:
                            st.caption(pol.description)
                        st.caption(f"Owner: {pol.policy_owner or 'Not set'}")
                    with col_b:
                        if st.button("View", key=f"view_pol_{pol.id}"):
                            st.switch_page("pages/09_Enterprise_Asset_Registry.py")
                    st.markdown("---")
        else:
            st.info("No policies linked")
    
    with col2:
        st.markdown("#### 🏛️ Organization Units")
        
        if current_impact.organization_unit_ids:
            linked_ous = [ou for ou in organization_units if ou.id in current_impact.organization_unit_ids]
            
            for ou in linked_ous:
                with st.container():
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.markdown(f"**{ou.name}**")
                        if ou.description:
                            st.caption(ou.description)
                        st.caption(f"Head: {ou.head_of_unit or 'Not set'}")
                    with col_b:
                        if st.button("View", key=f"view_ou_{ou.id}"):
                            st.switch_page("pages/09_Enterprise_Asset_Registry.py")
                    st.markdown("---")
        else:
            st.info("No organization units linked")
        
        st.markdown("#### 💻 Systems")
        
        if current_impact.system_ids:
            linked_systems = [sys for sys in systems if sys.id in current_impact.system_ids]
            
            for sys in linked_systems:
                with st.container():
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.markdown(f"**{sys.name}**")
                        if sys.description:
                            st.caption(sys.description)
                        st.caption(f"Owner: {sys.system_owner or 'Not set'} | Vendor: {sys.vendor or 'Not set'}")
                    with col_b:
                        if st.button("View", key=f"view_sys_{sys.id}"):
                            st.switch_page("pages/09_Enterprise_Asset_Registry.py")
                    st.markdown("---")
        else:
            st.info("No systems linked")
    
    total_assets = (
        len(current_impact.stakeholder_group_ids) +
        len(current_impact.organization_unit_ids) +
        len(current_impact.business_process_ids) +
        len(current_impact.system_ids) +
        len(current_impact.policy_ids)
    )
    
    st.markdown("---")
    st.metric("Total Enterprise Assets Linked", total_assets)

with tab3:
    st.markdown("### Change Assets")
    
    change_assets = repo.list_change_assets(current_impact.id)
    
    if change_assets:
        asset_types = {}
        for asset in change_assets:
            if asset.asset_type not in asset_types:
                asset_types[asset.asset_type] = []
            asset_types[asset.asset_type].append(asset)
        
        for asset_type, assets in sorted(asset_types.items()):
            st.markdown(f"#### {asset_type}")
            
            for asset in assets:
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{asset.asset_name}**")
                        if asset.description:
                            st.caption(asset.description)
                    
                    with col2:
                        status_emoji = {
                            "Planned": "📋",
                            "In Progress": "🔄",
                            "Review": "👀",
                            "Complete": "✅"
                        }
                        st.caption(f"{status_emoji.get(asset.status, '📄')} {asset.status}")
                    
                    with col3:
                        if asset.owner:
                            st.caption(f"Owner: {asset.owner}")
                    
                    st.markdown("---")
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Change Assets", len(change_assets))
        
        with col2:
            complete = len([a for a in change_assets if a.status == "Complete"])
            st.metric("Complete", complete)
        
        with col3:
            coverage_pct = (complete / len(change_assets) * 100) if change_assets else 0
            st.metric("Coverage %", f"{coverage_pct:.0f}%")
    else:
        st.info("No change assets defined")
        
        if st.button("➕ Add Change Assets"):
            st.session_state['edit_impact_id'] = current_impact.id
            st.switch_page("pages/07_Enrichment_Workspace.py")

with tab4:
    st.markdown("### Source Evidence")
    
    evidences = repo.list_source_evidences(current_impact.id)
    
    if evidences:
        for evidence in evidences:
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    source_emoji = {
                        "Discovery Session": "🔍",
                        "Workshop": "👥",
                        "Interview": "🎤",
                        "Requirements Session": "📋",
                        "Design Review": "🎨",
                        "Meeting": "📅",
                        "Document": "📄",
                        "Other": "📌"
                    }
                    st.markdown(f"{source_emoji.get(evidence.source_type, '📌')} **{evidence.source_type}**")
                    
                    if evidence.source_name:
                        st.write(f"*{evidence.source_name}*")
                    
                    if evidence.notes:
                        st.caption(evidence.notes)
                    
                    if evidence.source_date:
                        st.caption(f"Date: {evidence.source_date.strftime('%Y-%m-%d')}")
                
                with col2:
                    if evidence.source_url:
                        st.link_button("🔗 Open", evidence.source_url)
                
                st.markdown("---")
        
        st.metric("Total Source Evidence", len(evidences))
    else:
        st.info("No source evidence documented")
        
        if st.button("➕ Add Source Evidence"):
            st.session_state['edit_impact_id'] = current_impact.id
            st.switch_page("pages/07_Enrichment_Workspace.py")

with tab5:
    st.markdown("### Relationships")
    
    st.markdown("#### 🔗 Related Impacts")
    
    related_impacts = []
    for impact in impacts:
        if impact.id != current_impact.id:
            shared_sgs = set(impact.stakeholder_group_ids) & set(current_impact.stakeholder_group_ids)
            shared_bps = set(impact.business_process_ids) & set(current_impact.business_process_ids)
            shared_systems = set(impact.system_ids) & set(current_impact.system_ids)
            
            if shared_sgs or shared_bps or shared_systems:
                similarity_score = len(shared_sgs) + len(shared_bps) + len(shared_systems)
                related_impacts.append((impact, similarity_score, shared_sgs, shared_bps, shared_systems))
    
    related_impacts.sort(key=lambda x: x[1], reverse=True)
    
    if related_impacts:
        st.markdown(f"**Found {len(related_impacts[:10])} related impacts** (showing top 10)")
        
        for impact, score, shared_sgs, shared_bps, shared_systems in related_impacts[:10]:
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**{impact.impact_number}**: {impact.title or impact.description[:60]}")
                    
                    relationships = []
                    if shared_sgs:
                        sg_names = [sg.name for sg in stakeholder_groups if sg.id in shared_sgs]
                        relationships.append(f"Stakeholders: {', '.join(sg_names[:2])}")
                    if shared_bps:
                        bp_names = [bp.name for bp in business_processes if bp.id in shared_bps]
                        relationships.append(f"Processes: {', '.join(bp_names[:2])}")
                    if shared_systems:
                        sys_names = [sys.name for sys in systems if sys.id in shared_systems]
                        relationships.append(f"Systems: {', '.join(sys_names[:2])}")
                    
                    st.caption(" | ".join(relationships))
                
                with col2:
                    if st.button("View", key=f"view_related_{impact.id}"):
                        st.session_state['detail_impact_id'] = impact.id
                        st.rerun()
                
                st.markdown("---")
    else:
        st.info("No related impacts found based on shared enterprise assets")
    
    st.markdown("#### 🔄 Supersession")
    
    if current_impact.status == "Superseded":
        st.warning("⚠️ This impact has been superseded")
        st.caption("This impact is no longer active and has been replaced by a newer version")
    else:
        st.info("This impact is active")

with tab6:
    st.markdown("### History & Notes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📜 History")
        
        history_events = []
        
        if current_impact.created_at:
            history_events.append({
                'Event': 'Created',
                'Date': current_impact.created_at.strftime('%Y-%m-%d %H:%M'),
                'Icon': '➕'
            })
        
        if current_impact.updated_at and current_impact.updated_at != current_impact.created_at:
            history_events.append({
                'Event': 'Modified',
                'Date': current_impact.updated_at.strftime('%Y-%m-%d %H:%M'),
                'Icon': '✏️'
            })
        
        if current_impact.status == "Approved":
            history_events.append({
                'Event': 'Approved',
                'Date': current_impact.updated_at.strftime('%Y-%m-%d %H:%M') if current_impact.updated_at else 'Unknown',
                'Icon': '✅'
            })
        
        if current_impact.status == "Superseded":
            history_events.append({
                'Event': 'Superseded',
                'Date': current_impact.updated_at.strftime('%Y-%m-%d %H:%M') if current_impact.updated_at else 'Unknown',
                'Icon': '🔄'
            })
        
        for event in history_events:
            st.markdown(f"{event['Icon']} **{event['Event']}** - {event['Date']}")
        
        st.markdown("---")
        
        st.markdown("**Relationship Changes:**")
        
        total_relationships = (
            len(current_impact.stakeholder_group_ids) +
            len(current_impact.organization_unit_ids) +
            len(current_impact.business_process_ids) +
            len(current_impact.system_ids) +
            len(current_impact.policy_ids)
        )
        
        st.caption(f"Current: {total_relationships} enterprise asset relationships")
        st.caption(f"Change Assets: {len(change_assets)}")
        st.caption(f"Source Evidence: {len(evidences)}")
    
    with col2:
        st.markdown("#### 📝 Notes")
        
        if current_impact.notes:
            st.text_area(
                "Impact Notes",
                value=current_impact.notes,
                height=200,
                disabled=True,
                label_visibility="collapsed"
            )
        else:
            st.info("No notes added")
        
        if st.button("✏️ Edit Notes"):
            st.session_state['edit_impact_id'] = current_impact.id
            st.switch_page("pages/07_Enrichment_Workspace.py")

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    enrichment_score = 0
    max_score = 6
    
    if current_impact.title and current_impact.title.strip():
        enrichment_score += 1
    if len(current_impact.stakeholder_group_ids) > 0:
        enrichment_score += 1
    if len(current_impact.organization_unit_ids) > 0:
        enrichment_score += 1
    if len(current_impact.business_process_ids) > 0:
        enrichment_score += 1
    if len(current_impact.system_ids) > 0:
        enrichment_score += 1
    if len(change_assets) > 0:
        enrichment_score += 1
    
    score_pct = (enrichment_score / max_score) * 100
    
    if score_pct >= 70:
        score_emoji = "🟢"
        score_status = "Well Enriched"
    elif score_pct >= 30:
        score_emoji = "🟡"
        score_status = "Partially Enriched"
    else:
        score_emoji = "🔴"
        score_status = "Unenriched"
    
    st.metric("Enrichment Score", f"{score_emoji} {score_pct:.0f}%", score_status)

with col2:
    st.metric("Enterprise Assets", total_assets)

with col3:
    st.metric("Change Assets", len(change_assets))

st.markdown("---")
st.markdown("### 💡 Impact Detail Tips")
st.markdown("""
- **Navigate** - Use Previous/Next or dropdown to explore impacts
- **One-click access** - Every related object is clickable
- **Complete context** - All relationships visible from one page
- **Enrich** - Click "Enrich" to add or update information
- **Analyze** - Click "Analyze" to see this impact in context
- **Understand relationships** - See which impacts share enterprise assets
""")
