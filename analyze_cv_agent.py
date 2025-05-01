import os
import fitz  # PyMuPDF
import google.generativeai as genai
import json
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def plot_strength_weakness(data):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.bar(['Strengths', 'Weaknesses'], [len(data["strengths"]), len(data["weaknesses"])])
    ax.set_title("CV Overview")
    return fig

def plot_skill_radar(data):
    import plotly.graph_objects as go
    categories = list(data["skill_categories"].keys())
    values = list(data["skill_categories"].values())

    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself'
    ))
    fig.update_layout(title="Skill Radar", polar=dict(radialaxis=dict(visible=True)))
    return fig

def plot_job_match(data):
    import plotly.express as px
    df = pd.DataFrame(data["job_matches"])
    fig = px.bar(df, x="role", y="match_score", title="Job Role Match Score")
    return fig

def plot_improvement_progress(data):
    import plotly.express as px
    df = pd.DataFrame(data["improvement_plan"])
    fig = px.bar(df, x="task", y="progress", title="Improvement Suggestions Progress", text="progress")
    return fig


def analyze_cv(file):
    import shutil

    # Save the uploaded file
    with open("uploaded_cv.pdf", "wb") as out_file:
        with open(file.name, "rb") as in_file:
            shutil.copyfileobj(in_file, out_file)

    cv_text = extract_text_from_pdf("uploaded_cv.pdf")

    # Improved JSON prompt with clearer instructions
    json_prompt = f"""
You are an AI career coach. Analyze this resume and return ONLY valid JSON with no additional text, comments, or explanations.

The JSON must follow this exact structure:
{{
  "strengths": ["Strength 1", "Strength 2", "Strength 3"],
  "weaknesses": ["Weakness 1", "Weakness 2", "Weakness 3"],
  "skills_detected": ["Skill 1", "Skill 2", "Skill 3"],
  "skills_missing": ["Missing Skill 1", "Missing Skill 2"],
  "job_matches": [
    {{"role": "Job Title 1", "match_score": 85}},
    {{"role": "Job Title 2", "match_score": 78}},
    {{"role": "Job Title 3", "match_score": 62}}
  ],
  "improvement_plan": [
    {{"task": "Task 1", "progress": 40}},
    {{"task": "Task 2", "progress": 60}},
    {{"task": "Task 3", "progress": 20}}
  ],
  "skill_categories": {{
    "Technical": 60,
    "Leadership": 80,
    "Communication": 90,
    "Design": 40
  }}
}}

IMPORTANT: Return ONLY the JSON object. Do not include any explanations, markdown formatting, or additional text before or after the JSON.

Resume:
{cv_text}
"""

    # Text prompt remains the same
    text_prompt = f"""
You are an expert AI career counselor and CV reviewer.
Analyze the following resume and provide a clean, professional, and human-readable feedback with NO asterisks, NO markdown bullets.

Use clear section titles, proper paragraph writing, and bold important keywords only.

Your structure must follow:

## CV Analysis and Optimization

1. Skills Extraction
- Detected Skills: (Write as a sentence or short paragraph, NOT bullet list.)
- Missing High-Demand Skills: (Write as sentences. important skills in italics.)

2. Strengths & Weaknesses
Strengths:
Highlight achievements and strong points in 3-5 bullet points.

Weaknesses:
Identify areas for improvement in 3-5 bullet points.

3. Harvard-Style CV Feedback
- Structure: Comment on overall CV structure clearly.
- Language: Comment on action verbs, active voice usage.
- Formatting: Comment on font consistency, alignment, and 1-page rule.

4. Job Recommendations
- Suggest 20+ potential job titles organized by fields like Marketing, Business, Product, Creative, Other.
- Write it neatly in paragraphs, separating fields clearly.
- Provide career field-specific advice (e.g., certifications, online portfolios) as friendly recommendations.

Resume:
{cv_text}
"""

    try:
        # Use the correct model name
        model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
        
        # First get JSON data for visualizations with improved error handling
        json_response = model.generate_content(json_prompt)
        json_text = json_response.text.strip()
        
        # Clean up the response to ensure it's valid JSON
        # Remove any markdown code block markers
        if json_text.startswith("```json"):
            json_text = json_text.split("```json", 1)[1]
        if json_text.startswith("```"):
            json_text = json_text.split("```", 1)[1]
        if json_text.endswith("```"):
            json_text = json_text.rsplit("```", 1)[0]
        
        json_text = json_text.strip()
        
        # Then get human-readable text
        text_response = model.generate_content(text_prompt)
        
        try:
            # Parse JSON for visualizations
            data = json.loads(json_text)
            
            # Return tuple with both text and visualizations
            return (
                text_response.text,  # Human-readable text
                plot_strength_weakness(data),
                plot_skill_radar(data),
                plot_job_match(data),
                plot_improvement_progress(data)
            )
        except json.JSONDecodeError as e:
            # More detailed error message for debugging
            error_msg = f"❌ JSON Parse Error: {str(e)}\nResponse received: {json_text[:100]}..."
            return (error_msg, None, None, None, None)
    except Exception as e:
        return (f"❌ AI Error: {str(e)}", None, None, None, None)

