import streamlit as st
from database.schema import init_db, get_session, get_engine
from services.repository import Repository
from models.impact import ImpactDTO

st.set_page_config(page_title="Enrich", page_icon="🔗", layout="wide")

engine = init_db()
session = get_session(engine)
repo = Repository(session)

st.title("🔗 Enrich")
st.markdown("### Add Traceability and Context")

if 'current_project_id' not in st.session_state:
    st.warning("⚠️ Please select or create a project in the Setup page first")
    st.stop()

project_id = st.session_state['current_project_id']
project = repo.get_project(project_id)

st.info(f"📁 Current Project: **{project.name}**")

impacts = repo.list_impacts(project_id)

if not impacts:
    st.warning("⚠️ No impacts found. Please capture impacts first in the Capture page.")
    st.stop()

selected_impact_id = st.session_state.get('edit_impact_id', None)

impact_options = {f"{i.impact_number} - {i.description[:60]}...": i.id for i in impacts}
default_index = 0

if selected_impact_id:
    for idx, (label, impact_id) in enumerate(impact_options.items()):
        if impact_id == selected_impact_id:
            default_index = idx
            break

selected_impact_label = st.selectbox(
    "Select Impact to Enrich",
    options=list(impact_options.keys()),
    index=default_index
)

selected_impact_id = impact_options[selected_impact_label]
impact = repo.get_impact(selected_impact_id)

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["Impact Details", "Traceability", "Source Evidence", "Change Assets"])

with tab1:
    st.subheader("Impact Details")
    
    with st.form("impact_details_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            impact_number = st.text_input("Impact Number", value=impact.impact_number)
            title = st.text_input("Impact Title*", value=impact.title or "")
            description = st.text_area("Description*", value=impact.description, height=100)
            area_of_change = st.selectbox(
                "Area of Change",
                ["", "Process", "People", "Technology", "Policy", "Culture", "Structure", "Data", "Governance"],
                index=["", "Process", "People", "Technology", "Policy", "Culture", "Structure", "Data", "Governance"].index(impact.area_of_change) if impact.area_of_change in ["", "Process", "People", "Technology", "Policy", "Culture", "Structure", "Data", "Governance"] else 0
            )
            severity = st.selectbox(
                "Severity",
                ["", "Low", "Medium", "High", "Critical"],
                index=["", "Low", "Medium", "High", "Critical"].index(impact.severity) if impact.severity in ["", "Low", "Medium", "High", "Critical"] else 0
            )
        
        with col2:
            likelihood = st.selectbox(
                "Likelihood",
                ["", "Low", "Medium", "High"],
                index=["", "Low", "Medium", "High"].index(impact.likelihood) if impact.likelihood in ["", "Low", "Medium", "High"] else 0
            )
            readiness = st.selectbox(
                "Readiness",
                ["", "Low", "Medium", "High"],
                index=["", "Low", "Medium", "High"].index(impact.readiness) if impact.readiness in ["", "Low", "Medium", "High"] else 0
            )
            resistance = st.selectbox(
                "Resistance",
                ["", "Low", "Medium", "High"],
                index=["", "Low", "Medium", "High"].index(impact.resistance) if impact.resistance in ["", "Low", "Medium", "High"] else 0
            )
            status = st.selectbox(
                "Status",
                ["Draft", "Under Review", "Approved", "Superseded"],
                index=["Draft", "Under Review", "Approved", "Superseded"].index(impact.status) if impact.status in ["Draft", "Under Review", "Approved", "Superseded"] else 0
            )
        
        mitigation_strategy = st.text_area(
            "Mitigation Strategy",
            value=impact.mitigation_strategy or "",
            height=100,
            placeholder="Describe how this impact will be addressed..."
        )
        
        notes = st.text_area(
            "Notes",
            value=impact.notes or "",
            height=80,
            placeholder="Additional context or observations..."
        )
        
        if st.form_submit_button("💾 Save Changes", type="primary"):
            updated_impact = ImpactDTO(
                id=impact.id,
                project_id=impact.project_id,
                impact_number=impact_number,
                title=title,
                description=description,
                area_of_change=area_of_change,
                notes=notes,
                severity=severity,
                likelihood=likelihood,
                readiness=readiness,
                resistance=resistance,
                mitigation_strategy=mitigation_strategy,
                status=status,
                stakeholder_group_ids=impact.stakeholder_group_ids,
                organization_unit_ids=impact.organization_unit_ids,
                business_process_ids=impact.business_process_ids,
                system_ids=impact.system_ids,
                policy_ids=impact.policy_ids
            )
            repo.update_impact(updated_impact)
            st.success("✅ Impact updated successfully!")
            st.rerun()

with tab2:
    st.subheader("Traceability")
    st.markdown("Link this impact to enterprise assets to establish traceability.")
    
    stakeholder_groups = repo.list_stakeholder_groups(project_id)
    organization_units = repo.list_organization_units(project_id)
    business_processes = repo.list_business_processes(project_id)
    systems = repo.list_systems(project_id)
    policies = repo.list_policies(project_id)
    
    with st.form("traceability_form"):
        st.markdown("#### Stakeholder Groups")
        if stakeholder_groups:
            sg_options = {sg.name: sg.id for sg in stakeholder_groups}
            selected_sgs = st.multiselect(
                "Affected Stakeholder Groups",
                options=list(sg_options.keys()),
                default=[sg.name for sg in stakeholder_groups if sg.id in impact.stakeholder_group_ids]
            )
        else:
            st.info("No stakeholder groups defined. Add them in the Setup page.")
            selected_sgs = []
        
        st.markdown("#### Organization Units")
        if organization_units:
            ou_options = {ou.name: ou.id for ou in organization_units}
            selected_ous = st.multiselect(
                "Affected Organization Units",
                options=list(ou_options.keys()),
                default=[ou.name for ou in organization_units if ou.id in impact.organization_unit_ids]
            )
        else:
            st.info("No organization units defined. Add them in the Setup page.")
            selected_ous = []
        
        st.markdown("#### Business Processes")
        if business_processes:
            bp_options = {bp.name: bp.id for bp in business_processes}
            selected_bps = st.multiselect(
                "Affected Business Processes",
                options=list(bp_options.keys()),
                default=[bp.name for bp in business_processes if bp.id in impact.business_process_ids]
            )
        else:
            st.info("No business processes defined. Add them in the Setup page.")
            selected_bps = []
        
        st.markdown("#### Systems")
        if systems:
            sys_options = {sys.name: sys.id for sys in systems}
            selected_systems = st.multiselect(
                "Affected Systems",
                options=list(sys_options.keys()),
                default=[sys.name for sys in systems if sys.id in impact.system_ids]
            )
        else:
            st.info("No systems defined. Add them in the Setup page.")
            selected_systems = []
        
        st.markdown("#### Policies")
        if policies:
            pol_options = {pol.name: pol.id for pol in policies}
            selected_policies = st.multiselect(
                "Related Policies",
                options=list(pol_options.keys()),
                default=[pol.name for pol in policies if pol.id in impact.policy_ids]
            )
        else:
            st.info("No policies defined. Add them in the Setup page.")
            selected_policies = []
        
        if st.form_submit_button("🔗 Update Traceability", type="primary"):
            updated_impact = ImpactDTO(
                id=impact.id,
                project_id=impact.project_id,
                impact_number=impact.impact_number,
                description=impact.description,
                category=impact.category,
                severity=impact.severity,
                likelihood=impact.likelihood,
                readiness=impact.readiness,
                resistance=impact.resistance,
                mitigation_strategy=impact.mitigation_strategy,
                status=impact.status,
                stakeholder_group_ids=[sg_options.get(name, 0) for name in selected_sgs] if stakeholder_groups else [],
                organization_unit_ids=[ou_options.get(name, 0) for name in selected_ous] if organization_units else [],
                business_process_ids=[bp_options.get(name, 0) for name in selected_bps] if business_processes else [],
                system_ids=[sys_options.get(name, 0) for name in selected_systems] if systems else [],
                policy_ids=[pol_options.get(name, 0) for name in selected_policies] if policies else []
            )
            repo.update_impact(updated_impact)
            st.success("✅ Traceability updated successfully!")
            st.rerun()

with tab3:
    st.subheader("Source Evidence")
    st.markdown("Document where this impact was identified.")
    
    with st.expander("➕ Add Source Evidence"):
        with st.form("new_source_evidence"):
            source_type = st.selectbox(
                "Source Type",
                ["Workshop", "Interview", "Survey", "Document", "Meeting", "Other"]
            )
            source_reference = st.text_input(
                "Source Reference",
                placeholder="e.g., Workshop with Finance Team - 2024-01-15"
            )
            notes = st.text_area(
                "Notes",
                placeholder="Additional context about this source..."
            )
            
            if st.form_submit_button("Add Evidence"):
                if source_reference:
                    repo.create_source_evidence(impact.id, source_type, source_reference, notes)
                    st.success("✅ Source evidence added!")
                    st.rerun()
    
    evidences = repo.list_source_evidences(impact.id)
    if evidences:
        for evidence in evidences:
            with st.container():
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.caption(f"**{evidence.source_type}**")
                with col2:
                    st.write(evidence.source_reference)
                    if evidence.notes:
                        st.caption(evidence.notes)
                st.markdown("---")
    else:
        st.info("No source evidence recorded yet")

with tab4:
    st.subheader("Change Assets")
    st.markdown("Track deliverables and artifacts needed to address this impact.")
    
    with st.expander("➕ Add Change Asset"):
        with st.form("new_change_asset"):
            col1, col2 = st.columns(2)
            with col1:
                asset_type = st.selectbox(
                    "Asset Type",
                    ["Training", "Communication", "Job Aid", "Process Document", "System Config", "Other"]
                )
                asset_name = st.text_input("Asset Name*", placeholder="e.g., New Approval Process Training")
            with col2:
                status = st.selectbox(
                    "Status",
                    ["Planned", "In Progress", "Review", "Complete"],
                    index=0
                )
                owner = st.text_input("Owner", placeholder="Person responsible")
            
            description = st.text_area("Description", placeholder="Details about this asset...")
            
            if st.form_submit_button("Add Asset"):
                if asset_name:
                    repo.create_change_asset(impact.id, asset_type, asset_name, description, status, owner)
                    st.success("✅ Change asset added!")
                    st.rerun()
    
    assets = repo.list_change_assets(impact.id)
    if assets:
        for asset in assets:
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
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
        st.info("No change assets defined yet")

st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("⬅️ Previous Impact"):
        current_idx = list(impact_options.values()).index(selected_impact_id)
        if current_idx > 0:
            st.session_state['edit_impact_id'] = list(impact_options.values())[current_idx - 1]
            st.rerun()

with col3:
    if st.button("Next Impact ➡️"):
        current_idx = list(impact_options.values()).index(selected_impact_id)
        if current_idx < len(impact_options) - 1:
            st.session_state['edit_impact_id'] = list(impact_options.values())[current_idx + 1]
            st.rerun()
