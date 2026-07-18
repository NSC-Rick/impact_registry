import streamlit as st
from datetime import datetime
from database.schema import init_db, get_session, get_engine
from services.repository import Repository
from models.impact import ImpactDTO

st.set_page_config(page_title="Capture Workspace", page_icon="⚡", layout="wide")

engine = init_db()
session = get_session(engine)
repo = Repository(session)

st.title("⚡ Capture Workspace")
st.markdown("### Rapid Impact Capture During Discovery Sessions")

if 'current_project_id' not in st.session_state:
    st.warning("⚠️ Please select or create a project in the Setup page first")
    st.stop()

project_id = st.session_state['current_project_id']
project = repo.get_project(project_id)

if 'carry_forward_settings' not in st.session_state:
    st.session_state['carry_forward_settings'] = {
        'project': True,
        'source_evidence': False,
        'business_process': False,
        'system': False,
        'stakeholder_groups': False,
        'organization_units': False
    }

if 'carried_values' not in st.session_state:
    st.session_state['carried_values'] = {
        'project_id': project_id,
        'source_evidence_type': '',
        'source_evidence_ref': '',
        'business_process_ids': [],
        'system_ids': [],
        'stakeholder_group_ids': [],
        'organization_unit_ids': []
    }

st.info(f"📁 **Project:** {project.name} | **Change Manager:** {project.change_manager or 'Not set'}")

col1, col2 = st.columns([3, 1])

with col2:
    with st.expander("⚙️ Carry Forward Settings", expanded=False):
        st.markdown("**Pin fields to auto-populate:**")
        
        st.session_state['carry_forward_settings']['project'] = st.checkbox(
            "Project (always on)",
            value=True,
            disabled=True
        )
        
        st.session_state['carry_forward_settings']['source_evidence'] = st.checkbox(
            "Source Evidence",
            value=st.session_state['carry_forward_settings']['source_evidence']
        )
        
        st.session_state['carry_forward_settings']['business_process'] = st.checkbox(
            "Business Process",
            value=st.session_state['carry_forward_settings']['business_process']
        )
        
        st.session_state['carry_forward_settings']['system'] = st.checkbox(
            "System",
            value=st.session_state['carry_forward_settings']['system']
        )
        
        st.session_state['carry_forward_settings']['stakeholder_groups'] = st.checkbox(
            "Stakeholder Groups",
            value=st.session_state['carry_forward_settings']['stakeholder_groups']
        )
        
        st.session_state['carry_forward_settings']['organization_units'] = st.checkbox(
            "Organization Units",
            value=st.session_state['carry_forward_settings']['organization_units']
        )
        
        if st.button("🔄 Reset All Carried Values"):
            st.session_state['carried_values'] = {
                'project_id': project_id,
                'source_evidence_type': '',
                'source_evidence_ref': '',
                'business_process_ids': [],
                'system_ids': [],
                'stakeholder_group_ids': [],
                'organization_unit_ids': []
            }
            st.success("Carried values reset")
            st.rerun()

with col1:
    impacts = repo.list_impacts(project_id)
    impact_count = len(impacts)
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Total Impacts", impact_count)
    with col_b:
        draft_count = len([i for i in impacts if i.status == "Draft"])
        st.metric("Draft", draft_count)
    with col_c:
        approved_count = len([i for i in impacts if i.status == "Approved"])
        st.metric("Approved", approved_count)

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["New Impact", "Recent Impacts", "Duplicate Previous"])

with tab1:
    st.markdown("### 📝 New Impact")
    st.markdown("**Capture First** - Enter title and description, enrich later")
    
    with st.form("new_impact_form", clear_on_submit=False):
        auto_impact_number = f"IMP-{impact_count + 1:04d}"
        
        col1, col2 = st.columns([2, 1])
        with col1:
            impact_number = st.text_input(
                "Impact Number",
                value=auto_impact_number,
                help="Auto-generated, can be customized"
            )
        with col2:
            area_of_change = st.selectbox(
                "Area of Change",
                ["", "Process", "People", "Technology", "Policy", "Culture", "Structure", "Data", "Governance"],
                help="Optional categorization"
            )
        
        title = st.text_input(
            "Impact Title* (Required)",
            placeholder="Brief, descriptive title...",
            help="Short summary of the impact"
        )
        
        description = st.text_area(
            "Impact Description* (Required)",
            placeholder="What is changing? Who is affected? What do they need to do differently?",
            height=120,
            help="Detailed description of the change impact"
        )
        
        st.markdown("#### 🔗 Context & Traceability")
        
        stakeholder_groups = repo.list_stakeholder_groups(project_id)
        organization_units = repo.list_organization_units(project_id)
        business_processes = repo.list_business_processes(project_id)
        systems = repo.list_systems(project_id)
        policies = repo.list_policies(project_id)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if business_processes:
                bp_options = {bp.name: bp.id for bp in business_processes}
                default_bps = []
                if st.session_state['carry_forward_settings']['business_process']:
                    default_bps = [bp.name for bp in business_processes 
                                  if bp.id in st.session_state['carried_values']['business_process_ids']]
                
                selected_bps = st.multiselect(
                    "Business Process",
                    options=list(bp_options.keys()),
                    default=default_bps,
                    help="Affected business processes"
                )
            else:
                selected_bps = []
                st.info("No business processes defined")
            
            if systems:
                sys_options = {sys.name: sys.id for sys in systems}
                default_systems = []
                if st.session_state['carry_forward_settings']['system']:
                    default_systems = [sys.name for sys in systems 
                                      if sys.id in st.session_state['carried_values']['system_ids']]
                
                selected_systems = st.multiselect(
                    "System",
                    options=list(sys_options.keys()),
                    default=default_systems,
                    help="Affected systems"
                )
            else:
                selected_systems = []
                st.info("No systems defined")
            
            if policies:
                pol_options = {pol.name: pol.id for pol in policies}
                selected_policies = st.multiselect(
                    "Policy",
                    options=list(pol_options.keys()),
                    help="Related policies"
                )
            else:
                selected_policies = []
        
        with col2:
            if stakeholder_groups:
                sg_options = {sg.name: sg.id for sg in stakeholder_groups}
                default_sgs = []
                if st.session_state['carry_forward_settings']['stakeholder_groups']:
                    default_sgs = [sg.name for sg in stakeholder_groups 
                                  if sg.id in st.session_state['carried_values']['stakeholder_group_ids']]
                
                selected_sgs = st.multiselect(
                    "Stakeholder Groups",
                    options=list(sg_options.keys()),
                    default=default_sgs,
                    help="Affected stakeholder groups"
                )
            else:
                selected_sgs = []
                st.info("No stakeholder groups defined")
            
            if organization_units:
                ou_options = {ou.name: ou.id for ou in organization_units}
                default_ous = []
                if st.session_state['carry_forward_settings']['organization_units']:
                    default_ous = [ou.name for ou in organization_units 
                                  if ou.id in st.session_state['carried_values']['organization_unit_ids']]
                
                selected_ous = st.multiselect(
                    "Organization Units",
                    options=list(ou_options.keys()),
                    default=default_ous,
                    help="Affected organization units"
                )
            else:
                selected_ous = []
                st.info("No organization units defined")
        
        st.markdown("#### 📌 Source Evidence")
        
        col1, col2 = st.columns(2)
        with col1:
            default_source_type = ""
            if st.session_state['carry_forward_settings']['source_evidence']:
                default_source_type = st.session_state['carried_values']['source_evidence_type']
            
            source_type_idx = 0
            source_types = ["", "Workshop", "Interview", "Survey", "Document", "Meeting", "Other"]
            if default_source_type in source_types:
                source_type_idx = source_types.index(default_source_type)
            
            source_type = st.selectbox(
                "Source Type",
                source_types,
                index=source_type_idx
            )
        
        with col2:
            default_source_ref = ""
            if st.session_state['carry_forward_settings']['source_evidence']:
                default_source_ref = st.session_state['carried_values']['source_evidence_ref']
            
            source_reference = st.text_input(
                "Source Reference",
                value=default_source_ref,
                placeholder="e.g., Design Workshop - 2024-01-15"
            )
        
        notes = st.text_area(
            "Notes (Optional)",
            placeholder="Additional context, observations, or follow-up items...",
            height=80
        )
        
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            save_draft = st.form_submit_button(
                "💾 Save Draft",
                type="secondary",
                use_container_width=True,
                help="Save as Draft (Ctrl+Enter)"
            )
        
        with col2:
            save_approved = st.form_submit_button(
                "✅ Approve",
                type="primary",
                use_container_width=True,
                help="Save as Approved"
            )
        
        with col3:
            save_and_new = st.form_submit_button(
                "💾 Save & New",
                use_container_width=True,
                help="Save and create another"
            )
        
        with col4:
            clear_form = st.form_submit_button(
                "🔄 Clear",
                use_container_width=True,
                help="Clear form"
            )
        
        if (save_draft or save_approved or save_and_new) and title and description:
            status = "Approved" if save_approved else "Draft"
            
            impact_dto = ImpactDTO(
                project_id=project_id,
                impact_number=impact_number,
                title=title,
                description=description,
                area_of_change=area_of_change,
                notes=notes,
                status=status,
                stakeholder_group_ids=[sg_options.get(name, 0) for name in selected_sgs] if stakeholder_groups else [],
                organization_unit_ids=[ou_options.get(name, 0) for name in selected_ous] if organization_units else [],
                business_process_ids=[bp_options.get(name, 0) for name in selected_bps] if business_processes else [],
                system_ids=[sys_options.get(name, 0) for name in selected_systems] if systems else [],
                policy_ids=[pol_options.get(name, 0) for name in selected_policies] if policies else []
            )
            
            new_impact = repo.create_impact(impact_dto)
            
            if source_type and source_reference:
                repo.create_source_evidence(new_impact.id, source_type, source_reference, "")
            
            if st.session_state['carry_forward_settings']['business_process']:
                st.session_state['carried_values']['business_process_ids'] = [bp_options.get(name, 0) for name in selected_bps] if business_processes else []
            
            if st.session_state['carry_forward_settings']['system']:
                st.session_state['carried_values']['system_ids'] = [sys_options.get(name, 0) for name in selected_systems] if systems else []
            
            if st.session_state['carry_forward_settings']['stakeholder_groups']:
                st.session_state['carried_values']['stakeholder_group_ids'] = [sg_options.get(name, 0) for name in selected_sgs] if stakeholder_groups else []
            
            if st.session_state['carry_forward_settings']['organization_units']:
                st.session_state['carried_values']['organization_unit_ids'] = [ou_options.get(name, 0) for name in selected_ous] if organization_units else []
            
            if st.session_state['carry_forward_settings']['source_evidence']:
                st.session_state['carried_values']['source_evidence_type'] = source_type
                st.session_state['carried_values']['source_evidence_ref'] = source_reference
            
            st.success(f"✅ Impact {new_impact.impact_number} saved as {status}!")
            
            if save_and_new:
                st.info("Form ready for next impact (carried values preserved)")
            
            st.rerun()
        
        elif (save_draft or save_approved or save_and_new) and (not title or not description):
            st.error("❌ Title and Description are required")
        
        if clear_form:
            st.rerun()

with tab2:
    st.markdown("### 📋 Recent Impacts")
    st.markdown("Last 10 impacts captured in this session")
    
    recent_impacts = sorted(impacts, key=lambda x: x.created_at or datetime.min, reverse=True)[:10]
    
    if recent_impacts:
        for impact in recent_impacts:
            with st.expander(f"**{impact.impact_number}** - {impact.title or impact.description[:50]}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if impact.title:
                        st.markdown(f"**Title:** {impact.title}")
                    st.markdown(f"**Description:** {impact.description}")
                    if impact.notes:
                        st.markdown(f"**Notes:** {impact.notes}")
                
                with col2:
                    st.caption(f"Status: {impact.status}")
                    if impact.area_of_change:
                        st.caption(f"Area: {impact.area_of_change}")
                    if impact.created_at:
                        st.caption(f"Created: {impact.created_at.strftime('%H:%M')}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"✏️ Edit", key=f"edit_{impact.id}"):
                        st.session_state['edit_impact_id'] = impact.id
                        st.switch_page("pages/03_Enrich.py")
                
                with col2:
                    if impact.status == "Draft" and st.button(f"✅ Approve", key=f"approve_{impact.id}"):
                        impact.status = "Approved"
                        repo.update_impact(impact)
                        st.success("Approved!")
                        st.rerun()
                
                with col3:
                    if st.button(f"📋 Duplicate", key=f"dup_{impact.id}"):
                        st.session_state['duplicate_impact_id'] = impact.id
                        st.rerun()
    else:
        st.info("No impacts captured yet. Use the 'New Impact' tab to get started.")

with tab3:
    st.markdown("### 📋 Duplicate Previous Impact Context")
    st.markdown("Copy context from a previous impact to speed up capture")
    
    if impacts:
        impact_options = {f"{i.impact_number} - {i.title or i.description[:50]}": i.id for i in impacts}
        
        selected_impact_label = st.selectbox(
            "Select Impact to Duplicate",
            options=list(impact_options.keys())
        )
        
        if selected_impact_label:
            source_impact_id = impact_options[selected_impact_label]
            source_impact = repo.get_impact(source_impact_id)
            
            st.markdown("#### Preview")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Title:** {source_impact.title}")
                st.markdown(f"**Description:** {source_impact.description}")
            with col2:
                st.caption(f"Area: {source_impact.area_of_change or 'Not set'}")
                st.caption(f"Status: {source_impact.status}")
            
            if st.button("📋 Duplicate Context to New Impact", type="primary"):
                st.session_state['carried_values']['business_process_ids'] = source_impact.business_process_ids
                st.session_state['carried_values']['system_ids'] = source_impact.system_ids
                st.session_state['carried_values']['stakeholder_group_ids'] = source_impact.stakeholder_group_ids
                st.session_state['carried_values']['organization_unit_ids'] = source_impact.organization_unit_ids
                
                evidences = repo.list_source_evidences(source_impact.id)
                if evidences:
                    st.session_state['carried_values']['source_evidence_type'] = evidences[0].source_type
                    st.session_state['carried_values']['source_evidence_ref'] = evidences[0].source_reference
                
                st.session_state['carry_forward_settings']['business_process'] = True
                st.session_state['carry_forward_settings']['system'] = True
                st.session_state['carry_forward_settings']['stakeholder_groups'] = True
                st.session_state['carry_forward_settings']['organization_units'] = True
                st.session_state['carry_forward_settings']['source_evidence'] = True
                
                st.success("✅ Context duplicated! Switch to 'New Impact' tab to create impact with carried context.")
                st.rerun()
    else:
        st.info("No impacts available to duplicate")

st.markdown("---")
st.markdown("### ⌨️ Keyboard Shortcuts")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("- **Tab** - Navigate fields")
    st.markdown("- **Ctrl+Enter** - Save Draft")
with col2:
    st.markdown("- **Shift+Enter** - Approve")
    st.markdown("- **Alt+N** - New Impact")
with col3:
    st.markdown("- **Alt+C** - Clear Form")
    st.markdown("- **Alt+D** - Duplicate")
