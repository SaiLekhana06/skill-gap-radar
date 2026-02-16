import streamlit as st
import pandas as pd
import json
import re
from collections import Counter
from docx import Document
import pdfplumber

st.title("Skill Gap Radar 🚀")
st.write("Upload your resume and see how ready you are for your dream role.")

col1, col2 = st.columns(2)

with col1:
    role_search = st.text_input("Search Target Role", key="role_search")

with col2:
    job_search = st.text_input("Search Job Title", key="job_search")


df = pd.read_csv("job_description_1.csv")
roles = ["-- Select Role (Optional) --"] + sorted(df["role_category"].dropna().unique())

# STEP 1 — Search box
role_search = st.text_input("Search Target Role")

# STEP 2 — Get roles
roles = sorted(df["role_category"].dropna().unique())

# STEP 3 — Apply search filter
if role_search:
    roles = [r for r in roles if role_search.lower() in r.lower()]

# STEP 4 — Add optional first option
roles = ["-- Select Role (Optional) --"] + roles

# STEP 5 — Create dropdown
selected_role = st.selectbox(
    "Target Role (Optional)",
    roles,
    index=0
)



if selected_role != "-- Select Role (Optional) --":
    filtered_jobs = df[df["role_category"] == selected_role]
else:
    filtered_jobs = df


job_search = st.text_input("Search Job Title")

job_titles = sorted(filtered_jobs["job_title"].dropna().unique())

if job_search:
    job_titles = [jt for jt in job_titles if job_search.lower() in jt.lower()]

selected_job_title = st.selectbox("Select Job Title (Required)", job_titles)



uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

def extract_text(file):
    if file.name.endswith(".pdf"):
        with pdfplumber.open(file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + " "
        return text.lower()
    else:
        doc = Document(file)
        text = ""
        for para in doc.paragraphs:
            text += para.text + " "
        return text.lower()

def extract_resume_skills(text, skill_list):
    found = []
    for skill in skill_list:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text):
            found.append(skill)
    return list(set(found))

role_jobs = df[df["role_category"] == selected_role]

role_skills = []

for skills in role_jobs["skills_required"]:
    split = skills.lower().split(",")
    split = [s.strip() for s in split]
    role_skills.extend(split)

role_skill_freq = Counter(role_skills)
required_skills = [skill for skill, _ in role_skill_freq.most_common(10)]

with open("skill_frequency (finn).json", "r") as f:
    skill_freq = json.load(f)
skill_list = list(skill_freq.keys())

if uploaded_file:
    text = extract_text(uploaded_file)
    resume_skills = extract_resume_skills(text, skill_list)
    matched = list(set(required_skills) & set(resume_skills))
    missing = list(set(required_skills) - set(resume_skills))
    score = (len(matched) / len(required_skills)) * 100 if required_skills else 0
    st.subheader("Results")
    st.write("Matched Skills:", matched)
    st.write("Missing Skills:", missing)
    st.progress(int(score))
    st.write("Readiness Score:", round(score, 2), "%")
    
    if missing:
        st.subheader("Recommended Skills to Learn")
        for skill in missing:
            st.write(f"• {skill}")




