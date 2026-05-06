# AI Skill Gap Analyzer

## Overview

The AI Skill Gap Analyzer is a web-based application that helps users evaluate their readiness for a target job role. It compares user skills with job requirements and provides a structured roadmap to improve missing skills.

The system uses an AI model through the Groq API along with rule-based validation to generate accurate and meaningful results.

---

## Features

* Upload resume (PDF) and extract skills
* Enter target job role and job description
* Identify matched skills and missing skills
* Generate readiness score
* Provide detailed skill gap analysis
* Create a structured weekly and daily learning roadmap
* Re-analyze with updated skills
* Download report option

---

## Tech Stack

Frontend:

* Streamlit

Backend:

* Python

Libraries:

* PyPDF2
* python-dotenv
* groq
* reportlab

---

## Project Structure

app.py – Streamlit user interface
utils.py – Core logic and AI integration
requirements.txt – Dependencies
.gitignore – Ignored files

---

## Setup Instructions

1. Clone the repository
   git clone https://github.com/jahnavigv045-cmyk/skill-gap-analyzer.git

2. Navigate to the project folder
   cd skill-gap-analyzer

3. Install dependencies
   pip install -r requirements.txt

4. Create a .env file and add your API key
   GROQ_API_KEY=your_api_key_here

5. Run the application
   streamlit run app.py

---

## How It Works

1. User inputs skills or uploads resume
2. Job description is analyzed
3. AI compares user skills with required skills
4. Skill gaps and readiness score are generated
5. A structured learning roadmap is created

---

## AI Layer

This project uses the Groq API for fast AI inference and LLaMa. The AI model analyzes job descriptions and generates structured outputs, which are validated using custom logic to ensure correctness.

---

## Security Note

API keys are stored securely using environment variables and are not included in the repository.

---

## Future Enhancements


* Support for multiple job roles comparison
* Enhanced UI design
* Integration with job portals

---



## Author

Jahnavi G V
