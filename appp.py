import streamlit as st
import pandas as pd
import json
import re
from collections import Counter
from docx import Document
import pdfplumber

st.title("Skill Gap Radar 🚀")
st.write("Upload your resume and see how ready you are for your dream role.")

df = pd.read_csv("job_description_1.csv")
roles = df["role_category"].unique()
selected_role = st.selectbox("Select Target Role", roles)

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

with open("skill_frequency.json", "r") as f:
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




