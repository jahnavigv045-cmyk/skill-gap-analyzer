import json
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import os
from groq import Groq

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ---------- PDF TEXT EXTRACTION ----------
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


# ---------- SKILL EXTRACTION ----------
def extract_skills_from_text(text):
    common_skills = [
        "python", "sql", "excel", "machine learning",
        "tensorflow", "pytorch", "data analysis",
        "statistics", "java", "c++", "nlp", "deep learning",
        "aws", "gcp", "docker", "kubernetes", "git"
    ]

    found = []
    text_lower = text.lower()

    for skill in common_skills:
        if skill in text_lower:
            found.append(skill.title())

    return list(set(found))


# ---------- NORMALIZATION ----------
def normalize(skill):
    return skill.strip().lower()


# ---------- AI ANALYSIS ----------
def analyze_profile(skills, job_description, resume_text="", timeline="", hours=""):

    def convert_to_weeks(timeline):
        if "month" in timeline:
            num = int(timeline.split()[0])
            return num * 4
        elif "day" in timeline:
            num = int(timeline.split()[0])
            return max(1, num // 7)
        else:
            return 4
        

    weeks = convert_to_weeks(timeline)

    prompt = f"""
You are a STRICT AI career evaluator.

RULES:
- Extract ONLY relevant skills from job description
- DO NOT include skills already present in user skills
- DO NOT repeat skills
- Roadmap MUST be exactly {weeks} weeks
- Each week must include:
    - "week": string (example: "Week 1: Learn Python fundamentals")
    - "days": list of 7 daily tasks

Example format:
"roadmap": [
  {{
    "week": "Week 1: Learn Python fundamentals",
    "days": [
      "Day 1: Learn variables",
      "Day 2: Practice loops",
      "Day 3: Functions basics",
      "Day 4: Solve problems",
      "Day 5: Mini project",
      "Day 6: Practice",
      "Day 7: Revision"
    ]
  }}
]

INPUT:
User Skills: {skills}
Resume: {resume_text}
Job Description: {job_description}
Timeline: {timeline}

RETURN STRICT JSON:
{{
  "jd_skills": [],
  "matched_skills": [],
  "missing_skills": [],
  "readiness_score": 0,
  "skill_gaps": [
    {{
      "skill": "",
      "priority": "High",
      "reason": "",
      "resources": []
    }}
  ],
  "roadmap": [],
  "top_tip": ""
}}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",   # ✅ FIXED MODEL
            messages=[{"role": "user", "content": prompt}],
        )

        output = response.choices[0].message.content

        #  safety: empty output check
        if not output:
            raise Exception("Empty response from Groq")

        return output, "api"

    except Exception as e:
        return f"ERROR: {str(e)}", "error"

# ---------- VALIDATION ----------
def validate_output(data):

    jd_skills = [normalize(s) for s in data.get("jd_skills", [])]

    matched = data.get("matched_skills", [])
    matched_norm = [normalize(s) for s in matched]

    # Fix matched skills
    valid_matched = []
    for skill in matched:
        if normalize(skill) in jd_skills:
            valid_matched.append(skill)

    data["matched_skills"] = list(set(valid_matched))

    # Fix gaps
    valid_gaps = []
    for gap in data.get("skill_gaps", []):
        skill_norm = normalize(gap["skill"])

        if skill_norm in jd_skills and skill_norm not in matched_norm:
            valid_gaps.append(gap)

    data["skill_gaps"] = valid_gaps

    # Remove duplicates safely for dict roadmap
    seen = set()
    unique_roadmap = []

    for item in data.get("roadmap", []):
        key = str(item)
        if key not in seen:
            seen.add(key)
            unique_roadmap.append(item)
    data["roadmap"] = unique_roadmap        

    # Recalculate score
    total = len(jd_skills)
    matched_count = len(valid_matched)

    if total > 0:
        data["readiness_score"] = int((matched_count / total) * 100)

    return data


def generate_pdf(data, filename="report.pdf"):
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("Skill Gap Report", styles["Title"]))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"Readiness Score: {data['readiness_score']}%", styles["Heading2"]))

    content.append(Spacer(1, 10))
    content.append(Paragraph("Strengths:", styles["Heading3"]))
    content.append(Paragraph(", ".join(data["matched_skills"]), styles["Normal"]))

    content.append(Spacer(1, 10))
    content.append(Paragraph("Missing Skills:", styles["Heading3"]))
    content.append(Paragraph(", ".join(data["missing_skills"]), styles["Normal"]))

    content.append(Spacer(1, 10))
    content.append(Paragraph("Skill Gaps:", styles["Heading3"]))

    for gap in data["skill_gaps"]:
        content.append(Paragraph(f"{gap['skill']} - {gap['reason']}", styles["Normal"]))

    content.append(Spacer(1, 10))
    content.append(Paragraph("Roadmap:", styles["Heading3"]))

    for week in data["roadmap"]:
        if isinstance(week, dict):
            content.append(Paragraph(week["week"], styles["Heading4"]))
            for day in week.get("days", []):
                content.append(Paragraph(day, styles["Normal"]))

    content.append(Spacer(1, 10))
    content.append(Paragraph(f"Top Tip: {data['top_tip']}", styles["Italic"]))

    doc.build(content)