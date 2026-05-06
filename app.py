import streamlit as st
import json
from utils import (
    extract_text_from_pdf,
    extract_skills_from_text,
    analyze_profile,
    validate_output
)

st.set_page_config(page_title="AI Skill Gap Analyzer", layout="wide")

st.title(" AI Skill Gap Analyzer")

# ---------- STEP 0 ----------
st.subheader("STEP 0 — Upload Resume (Optional)")

uploaded_file = st.file_uploader("Upload PDF Resume", type="pdf")

resume_text = ""
extracted_skills = []

if uploaded_file:
    resume_text = extract_text_from_pdf(uploaded_file)
    extracted_skills = extract_skills_from_text(resume_text)

    st.success("Resume processed")

    if extracted_skills:
        st.write("🔍 Extracted Skills:")
        st.write(", ".join(extracted_skills))


# ---------- STEP 1 ----------
st.subheader("STEP 1 — Target Role")

col1, col2 = st.columns(2)

with col1:
    job_title = st.text_input("Job Title")

with col2:
    experience = st.selectbox("Experience Level", ["Entry", "Mid", "Senior"])

industry = st.text_input("Industry (optional)")


# ---------- STEP 2 ----------
st.subheader("STEP 2 — Your Skills")

default_skills = ", ".join(extracted_skills) if extracted_skills else ""

skills_input = st.text_input("Enter skills", value=default_skills)

background = st.text_area("Background (optional)")


# ---------- STEP 3 ----------
st.subheader("STEP 3 — Timeline")

col3, col4 = st.columns(2)

with col3:
    hours = st.selectbox("Hours/week", ["5-10", "10-20", "20+"])

with col4:
    st.write("Timeline")

    timeline_option = st.selectbox(
        "Select predefined timeline",
        ["1 month", "3 months", "6 months", "Custom"]
    )

    if timeline_option == "Custom":
        custom_days = st.number_input(
            "Enter number of days",
            min_value=1,
            max_value=365,
            value=30
        )
        timeline = f"{custom_days} days"
    else:
        timeline = timeline_option


# ---------- JOB DESCRIPTION ----------
st.subheader("Job Description")
job_description = st.text_area("Paste job description here")


# ---------- ANALYZE ----------
if st.button("🚀 Analyze Skill Gap"):

    skills = [s.strip() for s in skills_input.split(",") if s.strip()]

    if not skills or not job_description:
        st.warning("Fill required fields")

    else:
        result, source = analyze_profile(
            skills,
            job_description,
            resume_text,
            timeline,
            hours
        )
        st.write("DEBUG OUTPUT:")
        st.write(result)
        # HANDLE API ERROR
        if source == "error":
            st.error(result)
            st.stop()

        #  CLEAN RESPONSE
        cleaned = result.replace("```json", "").replace("```", "").strip()

        #  EMPTY RESPONSE CHECK
        if not cleaned:
            st.error(" Empty response from AI")
            st.stop()

        try:
            data = json.loads(cleaned)
    
        except:
            st.error(" Invalid JSON from AI")
            st.write("RAW OUTPUT:")
            st.write(cleaned)
            st.stop()

        #  VALIDATE
        data = validate_output(data)
    
    
    
        cleaned = result.replace("```json", "").replace("```", "").strip()
        data = json.loads(cleaned)
        data = validate_output(data)

        st.session_state["data"] = data
        st.session_state["skills"] = skills_input
        st.session_state["job_description"] = job_description
        st.session_state["resume_text"] = resume_text
        st.session_state["timeline"] = timeline
        st.session_state["hours"] = hours
        st.session_state["source"] = source

        st.rerun()


# ---------- RESULTS ----------
if "data" in st.session_state:

    data = st.session_state["data"]

    if st.session_state.get("source") == "api":
        st.success("✅ Using Groq AI")
    else:
        st.warning("⚠️ Using fallback mode")

    st.subheader("📊 Readiness Score")
    st.progress(data["readiness_score"] / 100)
    st.write(f"{data['readiness_score']}%")

    st.subheader(" Strengths")
    for s in data["matched_skills"]:
        st.write(f"✔ {s}")

    st.subheader("⚠️ Skill Gaps")
    for gap in data["skill_gaps"]:
        with st.expander(gap["skill"]):
            st.write(f"Priority: {gap['priority']}")
            st.write(gap["reason"])
            for r in gap["resources"]:
                st.write(f"- {r}")

    st.subheader("🗺️ Roadmap")

    def format_week_label(week):
        w = week.get("week", "Unknown")
    
        try:
            w = int(str(w).replace("Week", "").strip())
            return f"Week {w}"
        
        except:
            return f"Week {w}"
        
    
    for week in data["roadmap"]:
        if isinstance(week, dict):
         # Directly print week title (already contains description)
            st.markdown(f"### {week['week']}")
        #  print days
            for day in week.get("days", []):
                st.write(f"- {day}")


    st.subheader("Top Tip")
    st.info(data["top_tip"])


# ---------- DOWNLOAD REPORT ----------
from utils import generate_pdf
import os

if st.button("📄 Generate PDF Report"):

    generate_pdf(st.session_state["data"])

    with open("report.pdf", "rb") as f:
        st.download_button(
            label="⬇ Download PDF",
            data=f,
            file_name="skill_gap_report.pdf",
            mime="application/pdf"
        )

# ---------- FEEDBACK LOOP ----------
if "data" in st.session_state:

    st.markdown("---")
    st.subheader("🔁 Improve Your Analysis")

    edited_skills = st.text_input(
        "Edit skills and re-analyze",
        value=st.session_state.get("skills", "")
    )

    if st.button("Re-analyze", key="re_analyze"):

        new_skills = [s.strip() for s in edited_skills.split(",") if s.strip()]

        result, source = analyze_profile(
            new_skills,
            st.session_state["job_description"],
            st.session_state["resume_text"],
            st.session_state["timeline"],
            st.session_state["hours"]
        )
        if source == "error":
            st.error(result)
            st.stop()
    
    
        cleaned = result.replace("```json", "").replace("```", "").strip()
        data = json.loads(cleaned)
        data = validate_output(data)

        st.session_state["data"] = data
        st.session_state["skills"] = edited_skills
        st.session_state["source"] = source

        st.rerun()