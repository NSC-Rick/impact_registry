import streamlit as st
import pandas as pd
from database.schema import init_db, get_session, get_engine
from services.repository import Repository
from models.impact import ImpactDTO

st.set_page_config(page_title="Capture", page_icon="📝", layout="wide")

engine = init_db()
session = get_session(engine)
repo = Repository(session)

st.title("📝 Capture")
st.markdown("### Record Impacts Quickly and Efficiently")

if 'current_project_id' not in st.session_state:
    st.warning("⚠️ Please select or create a project in the Setup page first")
    st.stop()

project_id = st.session_state['current_project_id']
project = repo.get_project(project_id)

st.info(f"📁 Current Project: **{project.name}**")

tab1, tab2, tab3 = st.tabs(["Quick Capture", "Bulk Import", "Impact List"])

with tab1:
    st.subheader("Quick Capture")
    st.markdown("Capture impacts one at a time with minimal friction. Focus on **description first**, enrich later.")
    
    with st.form("quick_capture_form", clear_on_submit=True):
        impact_number = st.text_input(
            "Impact Number (optional)",
            placeholder="Auto-generated if blank",
            help="Leave blank to auto-generate"
        )
        
        title = st.text_input(
            "Impact Title*",
            placeholder="Brief, descriptive title...",
            help="Short summary of the impact"
        )
        
        description = st.text_area(
            "Impact Description*",
            placeholder="Describe the change impact in plain language...",
            height=100,
            help="What is changing? Who is affected? What do they need to do differently?"
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            area_of_change = st.selectbox(
                "Area of Change (optional)",
                ["", "Process", "People", "Technology", "Policy", "Culture", "Structure", "Data", "Governance"]
            )
        with col2:
            severity = st.selectbox(
                "Severity (optional)",
                ["", "Low", "Medium", "High", "Critical"]
            )
        with col3:
            status = st.selectbox(
                "Status",
                ["Draft", "Under Review", "Approved", "Superseded"],
                index=0
            )
        
        notes = st.text_area(
            "Notes (optional)",
            placeholder="Additional context or observations...",
            height=60
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            submit = st.form_submit_button("💾 Capture Impact", type="primary", use_container_width=True)
        with col2:
            if st.form_submit_button("💾 Capture & Add Another", use_container_width=True):
                submit = True
        
        if submit and title and description:
            impacts = repo.list_impacts(project_id)
            if not impact_number:
                impact_number = f"IMP-{len(impacts) + 1:04d}"
            
            impact_dto = ImpactDTO(
                project_id=project_id,
                impact_number=impact_number,
                title=title,
                description=description,
                area_of_change=area_of_change,
                notes=notes,
                severity=severity,
                status=status
            )
            
            new_impact = repo.create_impact(impact_dto)
            st.success(f"✅ Impact {new_impact.impact_number} captured successfully!")
            st.rerun()
        elif submit and (not title or not description):
            st.error("❌ Title and Description are required")

with tab2:
    st.subheader("Bulk Import")
    st.markdown("Import multiple impacts from a CSV or Excel file.")
    
    with st.expander("📋 Template & Instructions"):
        st.markdown("""
        **Required Columns:**
        - `description` - The impact description (required)
        
        **Optional Columns:**
        - `impact_number` - Custom impact number (auto-generated if blank)
        - `category` - Process, People, Technology, Policy, Culture, Structure, Other
        - `severity` - Low, Medium, High, Critical
        - `likelihood` - Low, Medium, High
        - `readiness` - Low, Medium, High
        - `resistance` - Low, Medium, High
        - `mitigation_strategy` - Text description
        - `status` - Draft, Under Review, Approved, Closed
        """)
        
        template_df = pd.DataFrame({
            'impact_number': ['IMP-0001', 'IMP-0002'],
            'description': [
                'Users must learn new approval workflow in SAP',
                'Finance team transitions from Excel to Power BI'
            ],
            'category': ['Process', 'Technology'],
            'severity': ['Medium', 'High'],
            'status': ['Draft', 'Draft']
        })
        
        st.download_button(
            "📥 Download Template",
            template_df.to_csv(index=False),
            "impact_template.csv",
            "text/csv",
            use_container_width=True
        )
    
    uploaded_file = st.file_uploader(
        "Upload CSV or Excel file",
        type=['csv', 'xlsx'],
        help="File must contain at minimum a 'description' column"
    )
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.write(f"**Preview:** {len(df)} rows found")
            st.dataframe(df.head(10), use_container_width=True)
            
            if 'description' not in df.columns:
                st.error("❌ File must contain a 'description' column")
            else:
                if st.button("📤 Import Impacts", type="primary"):
                    imported_count = 0
                    errors = []
                    
                    for idx, row in df.iterrows():
                        try:
                            if pd.isna(row['description']) or str(row['description']).strip() == '':
                                errors.append(f"Row {idx + 2}: Missing description")
                                continue
                            
                            impact_number = row.get('impact_number', '')
                            if pd.isna(impact_number) or str(impact_number).strip() == '':
                                impacts = repo.list_impacts(project_id)
                                impact_number = f"IMP-{len(impacts) + imported_count + 1:04d}"
                            
                            impact_dto = ImpactDTO(
                                project_id=project_id,
                                impact_number=str(impact_number),
                                description=str(row['description']),
                                category=str(row.get('category', '')) if not pd.isna(row.get('category')) else '',
                                severity=str(row.get('severity', '')) if not pd.isna(row.get('severity')) else '',
                                likelihood=str(row.get('likelihood', '')) if not pd.isna(row.get('likelihood')) else '',
                                readiness=str(row.get('readiness', '')) if not pd.isna(row.get('readiness')) else '',
                                resistance=str(row.get('resistance', '')) if not pd.isna(row.get('resistance')) else '',
                                mitigation_strategy=str(row.get('mitigation_strategy', '')) if not pd.isna(row.get('mitigation_strategy')) else '',
                                status=str(row.get('status', 'Draft')) if not pd.isna(row.get('status')) else 'Draft'
                            )
                            
                            repo.create_impact(impact_dto)
                            imported_count += 1
                        except Exception as e:
                            errors.append(f"Row {idx + 2}: {str(e)}")
                    
                    if imported_count > 0:
                        st.success(f"✅ Successfully imported {imported_count} impacts!")
                    
                    if errors:
                        st.warning(f"⚠️ {len(errors)} errors occurred:")
                        for error in errors[:10]:
                            st.text(error)
                        if len(errors) > 10:
                            st.text(f"... and {len(errors) - 10} more errors")
                    
                    if imported_count > 0:
                        st.rerun()
        
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")

with tab3:
    st.subheader("Impact List")
    
    impacts = repo.list_impacts(project_id)
    
    if impacts:
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            st.metric("Total Impacts", len(impacts))
        with col2:
            draft_count = sum(1 for i in impacts if i.status == "Draft")
            st.metric("Draft", draft_count)
        
        st.markdown("---")
        
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        with filter_col1:
            filter_category = st.selectbox(
                "Filter by Category",
                ["All"] + ["Process", "People", "Technology", "Policy", "Culture", "Structure", "Other"]
            )
        with filter_col2:
            filter_severity = st.selectbox(
                "Filter by Severity",
                ["All", "Low", "Medium", "High", "Critical"]
            )
        with filter_col3:
            filter_status = st.selectbox(
                "Filter by Status",
                ["All", "Draft", "Under Review", "Approved", "Closed"]
            )
        
        filtered_impacts = impacts
        if filter_category != "All":
            filtered_impacts = [i for i in filtered_impacts if i.category == filter_category]
        if filter_severity != "All":
            filtered_impacts = [i for i in filtered_impacts if i.severity == filter_severity]
        if filter_status != "All":
            filtered_impacts = [i for i in filtered_impacts if i.status == filter_status]
        
        st.write(f"Showing {len(filtered_impacts)} of {len(impacts)} impacts")
        
        for impact in filtered_impacts:
            with st.expander(f"**{impact.impact_number}** - {impact.description[:80]}..."):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Description:** {impact.description}")
                    if impact.mitigation_strategy:
                        st.markdown(f"**Mitigation:** {impact.mitigation_strategy}")
                
                with col2:
                    if impact.category:
                        st.caption(f"📂 {impact.category}")
                    if impact.severity:
                        severity_emoji = {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}
                        st.caption(f"{severity_emoji.get(impact.severity, '⚪')} {impact.severity}")
                    st.caption(f"📊 {impact.status}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"✏️ Edit", key=f"edit_{impact.id}"):
                        st.session_state['edit_impact_id'] = impact.id
                        st.switch_page("pages/03_Enrich.py")
                with col2:
                    if st.button(f"🔍 Analyze", key=f"analyze_{impact.id}"):
                        st.session_state['analyze_impact_id'] = impact.id
                        st.switch_page("pages/04_Analyze.py")
                with col3:
                    if st.button(f"🗑️ Delete", key=f"delete_{impact.id}"):
                        if repo.delete_impact(impact.id):
                            st.success("Deleted")
                            st.rerun()
    else:
        st.info("No impacts captured yet. Use Quick Capture or Bulk Import to get started.")
        st.markdown("### 💡 Tips for Effective Capture")
        st.markdown("""
        - **Capture first, enrich later** - Focus on getting impacts recorded quickly
        - **Use plain language** - Describe impacts as practitioners would understand them
        - **One impact per entry** - Break complex changes into discrete impacts
        - **Coverage over perfection** - It's better to have 50 rough impacts than 5 perfect ones
        """)
