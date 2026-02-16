import streamlit as st
import pandas as pd
import json
import re
from collections import Counter
import pdfplumber
from docx import Document

# Page configuration
st.set_page_config(page_title="Skill Gap Radar", page_icon="🚀", layout="wide")

# Custom CSS for search dropdown styling
st.markdown("""
<style>
    .search-result-item {
        padding: 10px;
        margin: 5px 0;
        background-color: #262730;
        border-radius: 5px;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    .search-result-item:hover {
        background-color: #3d3d4d;
    }
    .selected-item {
        padding: 10px;
        margin: 10px 0;
        background-color: #1e4d2b;
        border-radius: 5px;
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("Skill Gap Radar 🚀")
st.markdown("### Job Readiness Intelligence System")
st.markdown("---")

# Load datasets
@st.cache_data
def load_data():
    # Load job descriptions
    df = pd.read_csv("job_description_1.csv")
    
    # Load skill universe
    with open("skill_frequency (finn).json", "r", encoding="utf-8") as f:
        skill_freq = json.load(f)
    
    skill_list = list(skill_freq.keys())
    
    return df, skill_list

try:
    df, skill_list = load_data()
except Exception as e:
    st.error(f"Error loading data files: {e}")
    st.stop()

# Extract skills from text using regex
def extract_skills(text, skill_list):
    text_lower = text.lower()
    found_skills = set()
    
    for skill in skill_list:
        skill_lower = skill.lower()
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.add(skill_lower)
    
    return found_skills

# Extract text from PDF
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text.lower()

# Extract text from DOCX
def extract_text_from_docx(file):
    doc = Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text.lower()

# Initialize session state
if 'selected_role' not in st.session_state:
    st.session_state.selected_role = None
if 'selected_job_title' not in st.session_state:
    st.session_state.selected_job_title = None
if 'role_search' not in st.session_state:
    st.session_state.role_search = ""
if 'job_search' not in st.session_state:
    st.session_state.job_search = ""

# UI Layout
col1, col2 = st.columns(2)

# Target Role Section
with col1:
    st.subheader("🎯 Target Role")
    
    # Search input for role
    role_search_input = st.text_input(
        "Search for a role category",
        value=st.session_state.role_search,
        key="role_search_input_key",
        placeholder="Type to search roles..."
    )
    
    # Update search state
    st.session_state.role_search = role_search_input
    
    # Get all unique roles and sort alphabetically
    all_roles = sorted(df['role_category'].dropna().unique().tolist())
    
    # Show results only if user is typing
    if role_search_input:
        # Filter roles based on search input in real-time
        filtered_roles = [role for role in all_roles if role_search_input.lower() in role.lower()]
        
        if filtered_roles:
            st.markdown("**Matching Roles:**")
            # Create a container with max height for scrolling
            with st.container():
                for idx, role in enumerate(filtered_roles[:8]):  # Show top 8 matches
                    col_btn = st.columns([1])
                    with col_btn[0]:
                        if st.button(
                            f"📁 {role}",
                            key=f"role_btn_{idx}_{role}",
                            use_container_width=True,
                            type="secondary"
                        ):
                            st.session_state.selected_role = role
                            st.session_state.role_search = role
                            st.rerun()
        else:
            st.info("No matching roles found")
    
    # Show selected role
    if st.session_state.selected_role:
        st.markdown("**Selected Role:**")
        st.success(f"✓ {st.session_state.selected_role}")
        if st.button("✕ Clear Role", key="clear_role_btn", type="secondary"):
            st.session_state.selected_role = None
            st.session_state.role_search = ""
            st.rerun()

# Job Title Section
with col2:
    st.subheader("💼 Job Title")
    
    # Search input for job title
    job_search_input = st.text_input(
        "Search for a job title",
        value=st.session_state.job_search,
        key="job_search_input_key",
        placeholder="Type to search job titles..."
    )
    
    # Update search state
    st.session_state.job_search = job_search_input
    
    # Filter dataframe based on selected role
    if st.session_state.selected_role:
        role_filtered_df = df[df['role_category'] == st.session_state.selected_role]
    else:
        role_filtered_df = df
    
    # Get all unique job titles from filtered dataframe and sort alphabetically
    all_job_titles = sorted(role_filtered_df['job_title'].dropna().unique().tolist())
    
    # Show results only if user is typing
    if job_search_input:
        # Filter job titles based on search input in real-time
        filtered_job_titles = [job for job in all_job_titles if job_search_input.lower() in job.lower()]
        
        if filtered_job_titles:
            st.markdown("**Matching Job Titles:**")
            # Create a container with max height for scrolling
            with st.container():
                for idx, job in enumerate(filtered_job_titles[:8]):  # Show top 8 matches
                    col_btn = st.columns([1])
                    with col_btn[0]:
                        if st.button(
                            f"💼 {job}",
                            key=f"job_btn_{idx}_{job}",
                            use_container_width=True,
                            type="secondary"
                        ):
                            st.session_state.selected_job_title = job
                            st.session_state.job_search = job
                            st.rerun()
        else:
            st.info("No matching job titles found")
    
    # Show selected job title
    if st.session_state.selected_job_title:
        st.markdown("**Selected Job Title:**")
        st.success(f"✓ {st.session_state.selected_job_title}")
        if st.button("✕ Clear Job Title", key="clear_job_btn", type="secondary"):
            st.session_state.selected_job_title = None
            st.session_state.job_search = ""
            st.rerun()

st.markdown("---")

# Resume Upload Section
st.subheader("📄 Upload Your Resume")
uploaded_file = st.file_uploader(
    "Upload your resume (PDF or DOCX format)",
    type=["pdf", "docx"],
    key="resume_uploader_key"
)

# Process when both job title is selected and resume is uploaded
if uploaded_file and st.session_state.selected_job_title:
    
    try:
        # Extract text from uploaded resume
        if uploaded_file.type == "application/pdf":
            resume_text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            resume_text = extract_text_from_docx(uploaded_file)
        else:
            st.error("Unsupported file format")
            st.stop()
        
        # Extract skills from resume
        resume_skills = extract_skills(resume_text, skill_list)
        
        # Get required skills for selected job title
        job_data = df[df['job_title'] == st.session_state.selected_job_title].iloc[0]
        required_skills_raw = job_data['skills_required']
        
        # Parse and normalize required skills
        if pd.notna(required_skills_raw):
            required_skills_list = [s.strip().lower() for s in str(required_skills_raw).split(',') if s.strip()]
        else:
            required_skills_list = []
        
        # Get top 10 most frequent required skills using Counter
        skill_counter = Counter(required_skills_list)
        top_10_required = [skill for skill, count in skill_counter.most_common(10)]
        required_skills = set(top_10_required)
        
        # Gap Analysis
        matched_skills = resume_skills.intersection(required_skills)
        missing_skills = required_skills - resume_skills
        
        # Calculate readiness score
        if len(required_skills) > 0:
            readiness_score = (len(matched_skills) / len(required_skills)) * 100
        else:
            readiness_score = 0
        
        # Display Results
        st.markdown("---")
        st.subheader("📊 Analysis Results")
        
        # Display matched and missing skills side by side
        result_col1, result_col2 = st.columns(2)
        
        with result_col1:
            st.markdown("#### ✅ Matched Skills")
            if matched_skills:
                for skill in sorted(matched_skills):
                    st.success(f"✓ {skill.title()}")
            else:
                st.info("No matching skills found")
        
        with result_col2:
            st.markdown("#### ❌ Missing Skills")
            if missing_skills:
                for skill in sorted(missing_skills):
                    st.error(f"✗ {skill.title()}")
            else:
                st.info("No missing skills - You have all required skills!")
        
        # Display progress bar and readiness score
        st.markdown("---")
        st.markdown("#### 🎯 Job Readiness Score")
        st.progress(readiness_score / 100)
        
        score_col1, score_col2, score_col3 = st.columns(3)
        with score_col1:
            st.metric("Readiness Score", f"{readiness_score:.1f}%")
        with score_col2:
            st.metric("Matched Skills", len(matched_skills))
        with score_col3:
            st.metric("Missing Skills", len(missing_skills))
        
        # Recommendations section
        if missing_skills:
            st.markdown("---")
            st.markdown("#### 💡 Recommended Skills to Learn")
            st.warning("Focus on acquiring these skills to improve your job readiness:")
            
            for idx, skill in enumerate(sorted(missing_skills), 1):
                st.write(f"{idx}. **{skill.title()}**")
        
    except Exception as e:
        st.error(f"Error processing resume: {e}")

elif not st.session_state.selected_job_title:
    st.info("👆 Please search and select a job title to begin analysis")
elif not uploaded_file:
    st.info("👆 Please upload your resume to analyze skill gaps")