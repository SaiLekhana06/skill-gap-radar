import streamlit as st
import pandas as pd
import json
import re
from collections import Counter
# --- Page Config ---
st.set_page_config(
    page_title="Skill Gap Radar – Job Readiness Intelligence System",
    page_icon="🎯",
    layout="wide",
)
# --- Custom CSS ---
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
    }
    .search-result-btn button {
        width: 100%;
        text-align: left;
        margin: 2px 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
    .skill-tag-matched {
        display: inline-block;
        background-color: #d4edda;
        color: #155724;
        padding: 4px 12px;
        margin: 3px;
        border-radius: 20px;
        font-size: 0.85rem;
    }
    .skill-tag-missing {
        display: inline-block;
        background-color: #f8d7da;
        color: #721c24;
        padding: 4px 12px;
        margin: 3px;
        border-radius: 20px;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)
# --- Session State Init ---
if "selected_role" not in st.session_state:
    st.session_state.selected_role = None
if "selected_job_title" not in st.session_state:
    st.session_state.selected_job_title = None
# --- Load Data ---
@st.cache_data
def load_job_data():
    df = pd.read_csv("job_description_1.csv")
    return df
@st.cache_data
def load_skill_universe():
    with open("skill_frequency (finn).json", "r") as f:
        data = json.load(f)
    return list(data.keys())
try:
    df = load_job_data()
    skill_universe = load_skill_universe()
except FileNotFoundError as e:
    st.error(f"❌ File not found: {e}. Please ensure data files are in the same directory.")
    st.stop()
# --- Normalize column names ---
df.columns = df.columns.str.strip().str.lower()
# Detect relevant columns
role_col = None
title_col = None
skills_col = None
for col in df.columns:
    if "role" in col and "category" in col:
        role_col = col
    elif "role" in col and role_col is None:
        role_col = col
    if "title" in col or "job" in col and "title" in col:
        title_col = col
    if "skill" in col and "required" in col:
        skills_col = col
if title_col is None:
    for col in df.columns:
        if "title" in col:
            title_col = col
            break
if skills_col is None:
    for col in df.columns:
        if "skill" in col:
            skills_col = col
            break
# --- Header ---
st.markdown("<h1 class='main-header'>🎯 Skill Gap Radar</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:gray;'>Job Readiness Intelligence System</p>", unsafe_allow_html=True)
st.markdown("---")
# --- Layout ---
col_left, col_right = st.columns([1, 1])
# =====================
# LEFT COLUMN: Search
# =====================
with col_left:
    st.subheader("🔍 Search Engine")
    # --- Target Role Search ---
    st.markdown("**Step 1: Search Target Role** *(optional)*")
    role_query = st.text_input(
        "Type to search roles...",
        key="role_search_input",
        placeholder="e.g., Data Science, Engineering...",
    )
    if role_col and role_query.strip():
        all_roles = sorted(df[role_col].dropna().unique().tolist())
        matching_roles = [
            r for r in all_roles if role_query.lower() in str(r).lower()
        ]
        if matching_roles:
            st.markdown(f"*Found {len(matching_roles)} matching role(s):*")
            for i, role in enumerate(matching_roles[:15]):
                if st.button(f"📁 {role}", key=f"role_btn_{i}"):
                    st.session_state.selected_role = role
                    st.rerun()
        else:
            st.info("No matching roles found.")
    if st.session_state.selected_role:
        st.success(f"✅ Selected Role: **{st.session_state.selected_role}**")
        if st.button("❌ Clear Role", key="clear_role_btn"):
            st.session_state.selected_role = None
            st.session_state.selected_job_title = None
            st.rerun()
    st.markdown("---")
    # --- Job Title Search ---
    st.markdown("**Step 2: Search Job Title** *(required)*")
    if title_col is None:
        st.error("❌ Could not detect a job title column in the dataset.")
        st.stop()
    job_query = st.text_input(
        "Type to search job titles...",
        key="job_search_input",
        placeholder="e.g., Data Analyst, Software Engineer...",
    )
    if job_query.strip():
        if st.session_state.selected_role and role_col:
            filtered_df = df[df[role_col] == st.session_state.selected_role]
        else:
            filtered_df = df
        all_titles = sorted(filtered_df[title_col].dropna().unique().tolist())
        matching_titles = [
            t for t in all_titles if job_query.lower() in str(t).lower()
        ]
        if matching_titles:
            st.markdown(f"*Found {len(matching_titles)} matching title(s):*")
            for i, title in enumerate(matching_titles[:15]):
                if st.button(f"💼 {title}", key=f"title_btn_{i}"):
                    st.session_state.selected_job_title = title
                    st.rerun()
        else:
            st.info("No matching job titles found.")
    if st.session_state.selected_job_title:
        st.success(f"✅ Selected Job Title: **{st.session_state.selected_job_title}**")
        if st.button("❌ Clear Job Title", key="clear_title_btn"):
            st.session_state.selected_job_title = None
            st.rerun()
# =====================
# RIGHT COLUMN: Upload & Analysis
# =====================
with col_right:
    st.subheader("📄 Resume Upload & Analysis")
    uploaded_file = st.file_uploader(
        "Upload your resume (PDF or DOCX)",
        type=["pdf", "docx"],
        key="resume_uploader",
    )
    if uploaded_file is not None:
        # --- Extract Text ---
        resume_text = ""
        if uploaded_file.type == "application/pdf":
            try:
                import pdfplumber
                with pdfplumber.open(uploaded_file) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            resume_text += page_text + " "
            except ImportError:
                st.error("❌ pdfplumber not installed. Add it to requirements.txt.")
                st.stop()
        elif uploaded_file.type in [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",
        ]:
            try:
                from docx import Document
                doc = Document(uploaded_file)
                for para in doc.paragraphs:
                    resume_text += para.text + " "
            except ImportError:
                st.error("❌ python-docx not installed. Add it to requirements.txt.")
                st.stop()
        resume_text = resume_text.lower().strip()
        if not resume_text:
            st.warning("⚠️ Could not extract text from your resume.")
        else:
            st.success(f"✅ Resume parsed — {len(resume_text.split())} words extracted.")
            # --- Skill Matching ---
            resume_skills = set()
            for skill in skill_universe:
                pattern = r"\b" + re.escape(skill.lower()) + r"\b"
                if re.search(pattern, resume_text):
                    resume_skills.add(skill.lower())
            # --- Job Skills ---
            if st.session_state.selected_job_title is None:
                st.warning("⚠️ Please select a job title first to run gap analysis.")
            else:
                job_title = st.session_state.selected_job_title
                job_rows = df[df[title_col] == job_title]
                if skills_col is None:
                    st.error("❌ Could not detect a skills column in the dataset.")
                    st.stop()
                all_skills_raw = []
                for val in job_rows[skills_col].dropna():
                    parts = [s.strip().lower() for s in str(val).split(",")]
                    all_skills_raw.extend(parts)
                skill_counter = Counter(all_skills_raw)
                top_required = [s for s, _ in skill_counter.most_common(10)]
                required_set = set(top_required)
                matched = resume_skills.intersection(required_set)
                missing = required_set.difference(resume_skills)
                readiness = (
                    (len(matched) / len(required_set)) * 100 if required_set else 0
                )
                st.markdown("---")
                # --- Display Results ---
                st.markdown("### 📊 Analysis Results")
                if st.session_state.selected_role:
                    st.markdown(
                        f"**🏷️ Role Category:** {st.session_state.selected_role}"
                    )
                st.markdown(f"**💼 Job Title:** {job_title}")
                st.markdown("---")
                # Readiness Score
                st.markdown("#### 🎯 Readiness Score")
                st.progress(min(readiness / 100, 1.0))
                st.markdown(
                    f"<h2 style='text-align:center;'>{readiness:.1f}%</h2>",
                    unsafe_allow_html=True,
                )
                st.markdown("---")
                # Matched Skills
                rcol1, rcol2 = st.columns(2)
                with rcol1:
                    st.markdown("#### ✅ Matched Skills")
                    if matched:
                        tags = "".join(
                            [
                                f"<span class='skill-tag-matched'>{s}</span>"
                                for s in sorted(matched)
                            ]
                        )
                        st.markdown(tags, unsafe_allow_html=True)
                    else:
                        st.info("No matched skills found.")
                with rcol2:
                    st.markdown("#### ❌ Missing Skills")
                    if missing:
                        tags = "".join(
                            [
                                f"<span class='skill-tag-missing'>{s}</span>"
                                for s in sorted(missing)
                            ]
                        )
                        st.markdown(tags, unsafe_allow_html=True)
                    else:
                        st.success("🎉 You have all the required skills!")
                st.markdown("---")
                # Recommended Skills
                st.markdown("#### 📚 Recommended Skills to Learn")
                if missing:
                    for i, skill in enumerate(sorted(missing), 1):
                        st.markdown(f"{i}. **{skill}**")
                else:
                    st.success("You're fully prepared for this role!")
# --- Footer ---
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:gray;font-size:0.85rem;'>"
    "Skill Gap Radar v1.0 | Built with ❤️ using Streamlit"
    "</p>",
    unsafe_allow_html=True,
)