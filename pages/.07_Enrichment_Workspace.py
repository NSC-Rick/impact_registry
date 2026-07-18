import streamlit as st
from datetime import datetime
from database.schema import init_db, get_session, get_engine
from services.repository import Repository
from services.analytics import AnalyticsService
from models.impact import ImpactDTO

st.set_page_config(page_title="Enrichment Workspace", page_icon="🔗", layout="wide")

engine = init_db()
session = get_session(engine)
repo = Repository(session)
analytics = AnalyticsService(session)

st.title("🔗 Enrichment Workspace")
st.markdown("### Transform Captured Impacts into Organizational Knowledge")

if 'current_project_id' not in st.session_state:
    st.warning("⚠️ Please select or create a project in the Setup page first")
    st.stop()

project_id = st.session_state['current_project_id']
project = repo.get_project(project_id)

st.info(f"📁 **Project:** {project.name}")

impacts = repo.list_impacts(project_id)

if not impacts:
    st.warning("⚠️ No impacts found. Please capture impacts first in the Capture Workspace.")
    st.stop()

def calculate_enrichment_score(impact):
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
    
    return (score / max_score) * 100

def get_filter_counts(impacts):
    draft = len([i for i in impacts if i.status == "Draft"])
    approved = len([i for i in impacts if i.status == "Approved"])
    superseded = len([i for i in impacts if i.status == "Superseded"])
    
    unenriched = len([i for i in impacts if calculate_enrichment_score(i) < 30])
    
    missing_coverage = 0
    for impact in impacts:
        change_assets = repo.list_change_assets(impact.id)
        if len(change_assets) == 0:
            missing_coverage += 1
    
    missing_source = 0
    for impact in impacts:
        evidences = repo.list_source_evidences(impact.id)
        if len(evidences) == 0:
            missing_source += 1
    
    missing_stakeholders = len([i for i in impacts if len(i.stakeholder_group_ids) == 0])
    
    return {
        'draft': draft,
        'approved': approved,
        'superseded': superseded,
        'unenriched': unenriched,
        'missing_coverage': missing_coverage,
        'missing_source': missing_source,
        'missing_stakeholders': missing_stakeholders
    }

counts = get_filter_counts(impacts)

col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### 🔍 Filters")
    
    filter_options = st.multiselect(
        "Show Impacts:",
        options=[
            f"Draft ({counts['draft']})",
            f"Approved ({counts['approved']})",
            f"Superseded ({counts['superseded']})",
            f"Unenriched <30% ({counts['unenriched']})",
            f"Missing Coverage ({counts['missing_coverage']})",
            f"Missing Source Evidence ({counts['missing_source']})",
            f"Missing Stakeholder Groups ({counts['missing_stakeholders']})"
        ],
        default=[f"Draft ({counts['draft']})"]
    )
    
    filtered_impacts = impacts.copy()
    
    if filter_options:
        temp_filtered = []
        
        for option in filter_options:
            if option.startswith("Draft"):
                temp_filtered.extend([i for i in impacts if i.status == "Draft"])
            elif option.startswith("Approved"):
                temp_filtered.extend([i for i in impacts if i.status == "Approved"])
            elif option.startswith("Superseded"):
                temp_filtered.extend([i for i in impacts if i.status == "Superseded"])
            elif option.startswith("Unenriched"):
                temp_filtered.extend([i for i in impacts if calculate_enrichment_score(i) < 30])
            elif option.startswith("Missing Coverage"):
                for impact in impacts:
                    change_assets = repo.list_change_assets(impact.id)
                    if len(change_assets) == 0:
                        temp_filtered.append(impact)
            elif option.startswith("Missing Source"):
                for impact in impacts:
                    evidences = repo.list_source_evidences(impact.id)
                    if len(evidences) == 0:
                        temp_filtered.append(impact)
            elif option.startswith("Missing Stakeholder"):
                temp_filtered.extend([i for i in impacts if len(i.stakeholder_group_ids) == 0])
        
        filtered_impacts = list({i.id: i for i in temp_filtered}.values())
    
    st.markdown(f"**Showing:** {len(filtered_impacts)} of {len(impacts)}")
    
    if st.button("🔄 Refresh Filters", use_container_width=True):
        st.rerun()
    
    st.markdown("---")
    
    st.markdown("### 📊 Quick Stats")
    avg_enrichment = sum([calculate_enrichment_score(i) for i in impacts]) / len(impacts) if impacts else 0
    st.metric("Avg Enrichment", f"{avg_enrichment:.0f}%")
    
    coverage_pct = ((len(impacts) - counts['missing_coverage']) / len(impacts) * 100) if impacts else 0
    st.metric("Coverage", f"{coverage_pct:.0f}%")

with col2:
    if not filtered_impacts:
        st.info("No impacts match the selected filters")
    else:
        if 'enrichment_current_index' not in st.session_state:
            st.session_state['enrichment_current_index'] = 0
        
        if st.session_state['enrichment_current_index'] >= len(filtered_impacts):
            st.session_state['enrichment_current_index'] = 0
        
        current_impact = filtered_impacts[st.session_state['enrichment_current_index']]
        
        col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
        with col_nav1:
            if st.button("⬅️ Previous", use_container_width=True):
                if st.session_state['enrichment_current_index'] > 0:
                    st.session_state['enrichment_current_index'] -= 1
                    st.rerun()
        
        with col_nav2:
            st.markdown(f"**Impact {st.session_state['enrichment_current_index'] + 1} of {len(filtered_impacts)}**")
        
        with col_nav3:
            if st.button("Next ➡️", use_container_width=True):
                if st.session_state['enrichment_current_index'] < len(filtered_impacts) - 1:
                    st.session_state['enrichment_current_index'] += 1
                    st.rerun()
        
        enrichment_score = calculate_enrichment_score(current_impact)
        
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            st.metric("Impact #", current_impact.impact_number)
        with col_b:
            st.metric("Status", current_impact.status)
        with col_c:
            color = "🟢" if enrichment_score >= 70 else "🟡" if enrichment_score >= 40 else "🔴"
            st.metric("Enrichment", f"{color} {enrichment_score:.0f}%")
        with col_d:
            change_assets = repo.list_change_assets(current_impact.id)
            st.metric("Coverage", len(change_assets))
        
        st.markdown("---")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "📝 Review & Improve", 
            "🏢 Enterprise Assets", 
            "📦 Change Assets",
            "📊 Coverage Summary"
        ])
        
        with tab1:
            st.markdown("### Review & Improve Impact")
            
            with st.form("improve_impact_form"):
                title = st.text_input(
                    "Impact Title*",
                    value=current_impact.title or "",
                    help="Brief, descriptive summary"
                )
                
                description = st.text_area(
                    "Impact Description*",
                    value=current_impact.description,
                    height=120,
                    help="Clear, detailed description of the change impact"
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    area_of_change = st.selectbox(
                        "Area of Change",
                        ["", "Process", "People", "Technology", "Policy", "Culture", "Structure", "Data", "Governance"],
                        index=["", "Process", "People", "Technology", "Policy", "Culture", "Structure", "Data", "Governance"].index(current_impact.area_of_change) if current_impact.area_of_change in ["", "Process", "People", "Technology", "Policy", "Culture", "Structure", "Data", "Governance"] else 0
                    )
                    
                    severity = st.selectbox(
                        "Severity",
                        ["", "Low", "Medium", "High", "Critical"],
                        index=["", "Low", "Medium", "High", "Critical"].index(current_impact.severity) if current_impact.severity in ["", "Low", "Medium", "High", "Critical"] else 0
                    )
                
                with col2:
                    likelihood = st.selectbox(
                        "Likelihood",
                        ["", "Low", "Medium", "High"],
                        index=["", "Low", "Medium", "High"].index(current_impact.likelihood) if current_impact.likelihood in ["", "Low", "Medium", "High"] else 0
                    )
                    
                    status = st.selectbox(
                        "Status",
                        ["Draft", "Under Review", "Approved", "Superseded"],
                        index=["Draft", "Under Review", "Approved", "Superseded"].index(current_impact.status) if current_impact.status in ["Draft", "Under Review", "Approved", "Superseded"] else 0
                    )
                
                notes = st.text_area(
                    "Notes",
                    value=current_impact.notes or "",
                    height=80,
                    placeholder="Additional context, observations, or follow-up items..."
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True):
                        updated_impact = ImpactDTO(
                            id=current_impact.id,
                            project_id=current_impact.project_id,
                            impact_number=current_impact.impact_number,
                            title=title,
                            description=description,
                            area_of_change=area_of_change,
                            notes=notes,
                            severity=severity,
                            likelihood=likelihood,
                            readiness=current_impact.readiness,
                            resistance=current_impact.resistance,
                            mitigation_strategy=current_impact.mitigation_strategy,
                            status=status,
                            stakeholder_group_ids=current_impact.stakeholder_group_ids,
                            organization_unit_ids=current_impact.organization_unit_ids,
                            business_process_ids=current_impact.business_process_ids,
                            system_ids=current_impact.system_ids,
                            policy_ids=current_impact.policy_ids
                        )
                        repo.update_impact(updated_impact)
                        st.success("✅ Impact updated!")
                        st.rerun()
                
                with col2:
                    if st.form_submit_button("✅ Save & Approve", use_container_width=True):
                        updated_impact = ImpactDTO(
                            id=current_impact.id,
                            project_id=current_impact.project_id,
                            impact_number=current_impact.impact_number,
                            title=title,
                            description=description,
                            area_of_change=area_of_change,
                            notes=notes,
                            severity=severity,
                            likelihood=likelihood,
                            readiness=current_impact.readiness,
                            resistance=current_impact.resistance,
                            mitigation_strategy=current_impact.mitigation_strategy,
                            status="Approved",
                            stakeholder_group_ids=current_impact.stakeholder_group_ids,
                            organization_unit_ids=current_impact.organization_unit_ids,
                            business_process_ids=current_impact.business_process_ids,
                            system_ids=current_impact.system_ids,
                            policy_ids=current_impact.policy_ids
                        )
                        repo.update_impact(updated_impact)
                        st.success("✅ Impact approved!")
                        st.rerun()
        
        with tab2:
            st.markdown("### Establish Enterprise Asset Relationships")
            st.markdown("*An Impact may relate to zero, one, or many Enterprise Assets*")
            
            stakeholder_groups = repo.list_stakeholder_groups(project_id)
            organization_units = repo.list_organization_units(project_id)
            business_processes = repo.list_business_processes(project_id)
            systems = repo.list_systems(project_id)
            policies = repo.list_policies(project_id)
            
            with st.form("enterprise_assets_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Stakeholder Groups")
                    if stakeholder_groups:
                        sg_options = {sg.name: sg.id for sg in stakeholder_groups}
                        selected_sgs = st.multiselect(
                            "Affected Stakeholder Groups",
                            options=list(sg_options.keys()),
                            default=[sg.name for sg in stakeholder_groups if sg.id in current_impact.stakeholder_group_ids],
                            help="Who is affected by this change?"
                        )
                    else:
                        selected_sgs = []
                        st.info("No stakeholder groups defined")
                    
                    st.markdown("#### Business Processes")
                    if business_processes:
                        bp_options = {bp.name: bp.id for bp in business_processes}
                        selected_bps = st.multiselect(
                            "Affected Business Processes",
                            options=list(bp_options.keys()),
                            default=[bp.name for bp in business_processes if bp.id in current_impact.business_process_ids],
                            help="Which processes are impacted?"
                        )
                    else:
                        selected_bps = []
                        st.info("No business processes defined")
                    
                    st.markdown("#### Policies")
                    if policies:
                        pol_options = {pol.name: pol.id for pol in policies}
                        selected_policies = st.multiselect(
                            "Related Policies",
                            options=list(pol_options.keys()),
                            default=[pol.name for pol in policies if pol.id in current_impact.policy_ids],
                            help="Which policies are relevant?"
                        )
                    else:
                        selected_policies = []
                
                with col2:
                    st.markdown("#### Organization Units")
                    if organization_units:
                        ou_options = {ou.name: ou.id for ou in organization_units}
                        selected_ous = st.multiselect(
                            "Affected Organization Units",
                            options=list(ou_options.keys()),
                            default=[ou.name for ou in organization_units if ou.id in current_impact.organization_unit_ids],
                            help="Which departments/teams are affected?"
                        )
                    else:
                        selected_ous = []
                        st.info("No organization units defined")
                    
                    st.markdown("#### Systems")
                    if systems:
                        sys_options = {sys.name: sys.id for sys in systems}
                        selected_systems = st.multiselect(
                            "Affected Systems",
                            options=list(sys_options.keys()),
                            default=[sys.name for sys in systems if sys.id in current_impact.system_ids],
                            help="Which systems are involved?"
                        )
                    else:
                        selected_systems = []
                        st.info("No systems defined")
                
                if st.form_submit_button("🔗 Update Relationships", type="primary", use_container_width=True):
                    updated_impact = ImpactDTO(
                        id=current_impact.id,
                        project_id=current_impact.project_id,
                        impact_number=current_impact.impact_number,
                        title=current_impact.title,
                        description=current_impact.description,
                        area_of_change=current_impact.area_of_change,
                        notes=current_impact.notes,
                        severity=current_impact.severity,
                        likelihood=current_impact.likelihood,
                        readiness=current_impact.readiness,
                        resistance=current_impact.resistance,
                        mitigation_strategy=current_impact.mitigation_strategy,
                        status=current_impact.status,
                        stakeholder_group_ids=[sg_options.get(name, 0) for name in selected_sgs] if stakeholder_groups else [],
                        organization_unit_ids=[ou_options.get(name, 0) for name in selected_ous] if organization_units else [],
                        business_process_ids=[bp_options.get(name, 0) for name in selected_bps] if business_processes else [],
                        system_ids=[sys_options.get(name, 0) for name in selected_systems] if systems else [],
                        policy_ids=[pol_options.get(name, 0) for name in selected_policies] if policies else []
                    )
                    repo.update_impact(updated_impact)
                    st.success("✅ Relationships updated!")
                    st.rerun()
        
        with tab3:
            st.markdown("### Establish Change Asset Relationships")
            st.markdown("*Relate Impacts to logical Change Assets (deliverables)*")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                with st.expander("➕ Add Change Asset", expanded=True):
                    with st.form("new_change_asset"):
                        asset_type = st.selectbox(
                            "Asset Type*",
                            ["Training", "QRG", "Communication", "FAQ", "Job Aid", "Manager Toolkit", "Process Document", "Video", "eLearning", "Other"]
                        )
                        
                        asset_name = st.text_input(
                            "Asset Name*",
                            placeholder="e.g., Manager Training - New Approval Process"
                        )
                        
                        description = st.text_area(
                            "Description",
                            placeholder="Brief description of this deliverable...",
                            height=60
                        )
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            status = st.selectbox(
                                "Status",
                                ["Planned", "In Progress", "Review", "Complete"],
                                index=0
                            )
                        with col_b:
                            owner = st.text_input("Owner", placeholder="Person responsible")
                        
                        if st.form_submit_button("➕ Add Asset", type="primary"):
                            if asset_name:
                                repo.create_change_asset(
                                    current_impact.id,
                                    asset_type,
                                    asset_name,
                                    description,
                                    status,
                                    owner
                                )
                                st.success(f"✅ Added {asset_type}: {asset_name}")
                                st.rerun()
                            else:
                                st.error("Asset name is required")
            
            with col2:
                st.markdown("#### Common Assets")
                st.markdown("Quick add:")
                
                quick_assets = [
                    ("Training", "End User Training"),
                    ("Training", "Manager Training"),
                    ("QRG", "Quick Reference Guide"),
                    ("Communication", "Change Announcement"),
                    ("FAQ", "Frequently Asked Questions"),
                    ("Job Aid", "Step-by-Step Guide")
                ]
                
                for asset_type, asset_name in quick_assets:
                    if st.button(f"+ {asset_name}", key=f"quick_{asset_type}_{asset_name}", use_container_width=True):
                        repo.create_change_asset(
                            current_impact.id,
                            asset_type,
                            asset_name,
                            "",
                            "Planned",
                            ""
                        )
                        st.success(f"✅ Added {asset_name}")
                        st.rerun()
            
            st.markdown("---")
            st.markdown("#### Current Change Assets")
            
            change_assets = repo.list_change_assets(current_impact.id)
            
            if change_assets:
                for asset in change_assets:
                    with st.container():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.write(f"**{asset.asset_name}**")
                            if asset.description:
                                st.caption(asset.description)
                        with col2:
                            st.caption(f"Type: {asset.asset_type}")
                            st.caption(f"Status: {asset.status}")
                        with col3:
                            if asset.owner:
                                st.caption(f"Owner: {asset.owner}")
                        st.markdown("---")
            else:
                st.info("No change assets defined yet. Add assets to establish coverage.")
        
        with tab4:
            st.markdown("### Coverage Summary")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Enterprise Asset Relationships")
                
                relationship_count = (
                    len(current_impact.stakeholder_group_ids) +
                    len(current_impact.organization_unit_ids) +
                    len(current_impact.business_process_ids) +
                    len(current_impact.system_ids) +
                    len(current_impact.policy_ids)
                )
                
                st.metric("Total Relationships", relationship_count)
                
                if current_impact.stakeholder_group_ids:
                    st.write("**Stakeholder Groups:**")
                    for sg in stakeholder_groups:
                        if sg.id in current_impact.stakeholder_group_ids:
                            st.write(f"- {sg.name}")
                
                if current_impact.business_process_ids:
                    st.write("**Business Processes:**")
                    for bp in business_processes:
                        if bp.id in current_impact.business_process_ids:
                            st.write(f"- {bp.name}")
                
                if current_impact.system_ids:
                    st.write("**Systems:**")
                    for sys in systems:
                        if sys.id in current_impact.system_ids:
                            st.write(f"- {sys.name}")
            
            with col2:
                st.markdown("#### Change Asset Coverage")
                
                change_assets = repo.list_change_assets(current_impact.id)
                st.metric("Total Assets", len(change_assets))
                
                if change_assets:
                    by_type = {}
                    for asset in change_assets:
                        by_type[asset.asset_type] = by_type.get(asset.asset_type, 0) + 1
                    
                    st.write("**By Type:**")
                    for asset_type, count in by_type.items():
                        st.write(f"- {asset_type}: {count}")
                    
                    by_status = {}
                    for asset in change_assets:
                        by_status[asset.status] = by_status.get(asset.status, 0) + 1
                    
                    st.write("**By Status:**")
                    for status, count in by_status.items():
                        st.write(f"- {status}: {count}")
                else:
                    st.info("No change assets defined")
            
            st.markdown("---")
            
            evidences = repo.list_source_evidences(current_impact.id)
            
            st.markdown("#### Source Evidence")
            if evidences:
                for evidence in evidences:
                    st.write(f"**{evidence.source_type}:** {evidence.source_reference}")
                    if evidence.notes:
                        st.caption(evidence.notes)
            else:
                st.warning("⚠️ No source evidence documented")
                
                with st.expander("➕ Add Source Evidence"):
                    with st.form("quick_source_evidence"):
                        source_type = st.selectbox(
                            "Source Type",
                            ["Workshop", "Interview", "Survey", "Document", "Meeting", "Other"]
                        )
                        source_reference = st.text_input(
                            "Source Reference",
                            placeholder="e.g., Design Workshop - 2024-01-15"
                        )
                        
                        if st.form_submit_button("Add Evidence"):
                            if source_reference:
                                repo.create_source_evidence(current_impact.id, source_type, source_reference, "")
                                st.success("✅ Source evidence added!")
                                st.rerun()
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("⬅️ Previous Impact", use_container_width=True):
                if st.session_state['enrichment_current_index'] > 0:
                    st.session_state['enrichment_current_index'] -= 1
                    st.rerun()
        
        with col2:
            if current_impact.status == "Draft":
                if st.button("✅ Approve & Next", type="primary", use_container_width=True):
                    current_impact.status = "Approved"
                    repo.update_impact(current_impact)
                    if st.session_state['enrichment_current_index'] < len(filtered_impacts) - 1:
                        st.session_state['enrichment_current_index'] += 1
                    st.rerun()
        
        with col3:
            if st.button("Next Impact ➡️", use_container_width=True):
                if st.session_state['enrichment_current_index'] < len(filtered_impacts) - 1:
                    st.session_state['enrichment_current_index'] += 1
                    st.rerun()

st.markdown("---")
st.markdown("### 💡 Enrichment Best Practices")
st.markdown("""
- **Review in batches** - Filter by Draft, enrich 10-20 at a time
- **Establish relationships deliberately** - Each relationship should enable future analysis
- **Coverage over perfection** - Focus on meaningful assets, not exhaustive lists
- **Use quick add** - Common change assets available for rapid assignment
- **Approve when ready** - Move impacts to Approved status after enrichment
""")
