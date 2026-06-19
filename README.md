# ResumeIQ - AI Resume Screening & Job Match Analyzer

## Overview

ResumeIQ is a local AI-powered application that analyzes resumes against job descriptions. It calculates a match score, identifies missing skills, and generates personalized improvement suggestions using Llama 3 running locally through Ollama.

## Features

* Resume PDF Upload
* Job Description PDF Upload
* Skill Extraction
* Resume-JD Matching
* Skill Gap Analysis
* AI Feedback Generation

## Tech Stack

* Python
* Streamlit
* Ollama
* Llama 3
* Sentence Transformers
* Scikit-learn
* PyPDF

## Project Structure

ResumeIQ/

* app.py
* requirements.txt
* README.md
* modules/

  * parser.py
  * matcher.py
  * skill_gap.py
  * ai_feedback.py

## How to Run

1. Activate virtual environment
2. Install requirements:
   pip install -r requirements.txt
3. Start Ollama and ensure Llama 3 is installed:
   ollama run llama3
4. Run Streamlit:
   streamlit run app.py

## Future Enhancements

* ATS Score Prediction
* Multi-Resume Ranking
* Resume Improvement Reports
* Support for DOCX files

## Author

Nived Krishnan J
