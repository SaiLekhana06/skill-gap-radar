import streamlit as st
import pandas as pd
import json
import re
from collections import Counter
import pdfplumber
from docx import Document

# Page configuration
st.set_page_config(page_title="Skill Gap Radar", page_icon="🚀", layout="wide")

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
    with open("skill_frequency (finn).json", "r") as f:
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
            text += page.extract_text() or ""
    return text.lower()

# Extract text from DOCX
def extract_text_from_docx(file):
    doc = Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text.lower()

# UI - Search bars side by side
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 Search Target Role")
    role_search = st.text_input("Type to filter roles", "", key="role_search")
    
    # Get unique roles and sort
    all_roles = sorted(df['role_category'].unique().tolist())
    
    # Filter roles based on search
    if role_search:
        filtered_roles = [role for role in all_roles if role_search.lower() in role.lower()]
    else:
        filtered_roles = all_roles
    
    # Add optional placeholder
    role_options = ["-- Select Role (Optional) --"] + filtered_roles
    selected_role = st.selectbox("Select Role Category", role_options, key="role_select")

with col2:
    st.subheader("💼 Search Job Title")
    job_search = st.text_input("Type to filter job titles", "", key="job_search")
    
    # Filter job titles based on selected role
    if selected_role != "-- Select Role (Optional) --":
        filtered_df = df[df['role_category'] == selected_role]
    else:
        filtered_df = df
    
    # Get unique job titles and sort
    all_jobs = sorted(filtered_df['job_title'].unique().tolist())
    
    # Filter jobs based on search
    if job_search:
        filtered_jobs = [job for job in all_jobs if job_search.lower() in job.lower()]
    else:
        filtered_jobs = all_jobs
    
    selected_job = st.selectbox("Select Job Title (Required)", filtered_jobs, key="job_select")

st.markdown("---")

# Resume upload
st.subheader("📄 Upload Your Resume")
uploaded_file = st.file_uploader("Upload PDF or DOCX", type=["pdf", "docx"], key="resume_upload")

if uploaded_file and selected_job:
    
    # Extract text from resume
    try:
        if uploaded_file.type == "application/pdf":
            resume_text = extract_text_from_pdf(uploaded_file)
        else:
            resume_text = extract_text_from_docx(uploaded_file)
        
        # Extract skills from resume
        resume_skills = extract_skills(resume_text, skill_list)
        
        # Get required skills for selected job
        job_row = df[df['job_title'] == selected_job].iloc[0]
        required_skills_raw = job_row['skills_required']
        
        # Parse and normalize required skills
        required_skills_list = [s.strip().lower() for s in str(required_skills_raw).split(',')]
        
        # Get top 10 most frequent required skills
        skill_counter = Counter(required_skills_list)
        top_10_skills = [skill for skill, count in skill_counter.most_common(10)]
        required_skills = set(top_10_skills)
        
        # Gap analysis
        matched_skills = resume_skills.intersection(required_skills)
        missing_skills = required_skills - resume_skills
        
        # Calculate readiness score
        if len(required_skills) > 0:
            readiness_score = (len(matched_skills) / len(required_skills)) * 100
        else:
            readiness_score = 0
        
        # Display results
        st.markdown("---")
        st.subheader("📊 Analysis Results")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("#### ✅ Matched Skills")
            if matched_skills:
                for skill in sorted(matched_skills):
                    st.success(f"✓ {skill}")
            else:
                st.info("No matching skills found")
        
        with col_b:
            st.markdown("#### ❌ Missing Skills")
            if missing_skills:
                for skill in sorted(missing_skills):
                    st.error(f"✗ {skill}")
            else:
                st.info("No missing skills")
        
        # Progress bar and score
        st.markdown("---")
        st.markdown("#### 🎯 Job Readiness Score")
        st.progress(readiness_score / 100)
        st.metric("Readiness", f"{readiness_score:.1f}%")
        
        # Recommendations
        if missing_skills:
            st.markdown("---")
            st.markdown("#### 💡 Recommended Skills to Learn")
            st.warning("Focus on acquiring these skills to improve your job readiness:")
            for skill in sorted(missing_skills):
                st.write(f"- {skill}")
    
    except Exception as e:
        st.error(f"Error processing resume: {e}")

elif not selected_job:
    st.info("👆 Please select a job title to begin analysis")
elif not uploaded_file:
    st.info("👆 Please upload your resume to analyze skill gaps")