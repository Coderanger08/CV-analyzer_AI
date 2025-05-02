import os
import fitz
import google.generativeai as genai
from datetime import datetime
import json
import plotly.graph_objects as go
import plotly.express as px
from dotenv import load_dotenv
import pandas as pd
import numpy as np

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def plot_strength_weakness(data):
    strengths = data["strengths"]
    weaknesses = data["weaknesses"]
    strength_score = data.get("score_strengths", 75)
    weakness_score = data.get("score_weaknesses", 45)

    fig = go.Figure()

    # Left (Strengths)
    fig.add_trace(go.Pie(
        values=[strength_score, 100 - strength_score],
        hole=0.6,
        marker_colors=["#F97316", "#F3F4F6"],
        domain={'x': [0.05, 0.45]},
        textinfo='none',
        hoverinfo='skip',
        showlegend=False,
        sort=False
    ))

    # Right (Weaknesses)
    fig.add_trace(go.Pie(
        values=[weakness_score, 100 - weakness_score],
        hole=0.6,
        marker_colors=["#1E3A8A", "#F3F4F6"],
        domain={'x': [0.55, 0.95]},
        textinfo='none',
        hoverinfo='skip',
        showlegend=False,
        sort=False
    ))
    

    # Annotations: Titles + Summary Labels
    annotations = [
        dict(x=0.25, y=0.5, xanchor="center", yanchor="middle",
             text="<b>Strengths</b>", showarrow=False,
             font=dict(size=22, color="black", family="Arial")),
        dict(x=0.75, y=0.5, xanchor="center", yanchor="middle",
             text="<b>Weaknesses</b>", showarrow=False,
             font=dict(size=22, color="black", family="Arial"))
    ]

    for i, s in enumerate(strengths):
        y = 0.8 - i * 0.2
        annotations.append(dict(
            x=0.25 + (0.25 if i % 2 == 0 else -0.25),
            y=y,
            text=f"<span style='color:#000'>{s['name']}</span>",
            hovertext=s['description'],
            showarrow=False,
            font=dict(size=12, color="#000"),
            bgcolor="white",
            bordercolor="#F97316",
            borderwidth=1,
            borderpad=4
        ))

    for i, w in enumerate(weaknesses):
        y = 0.8 - i * 0.2
        annotations.append(dict(
            x=0.75 + (0.25 if i % 2 == 0 else -0.25),
            y=y,
            text=f"<span style='color:#000'>{w['name']}</span>",
            hovertext=w['description'],
            showarrow=False,
            font=dict(size=12, color="#000"),
            bgcolor="white",
            bordercolor="#1E3A8A",
            borderwidth=1,
            borderpad=4
        ))

    fig.update_layout(annotations=annotations)
    return fig



    
def plot_skill_radar(data): 
    import plotly.graph_objects as go
    import markdown

    categories = list(data["skill_categories"].keys())  
    values = list(data["skill_categories"].values())  

    fig = go.Figure(
        data=go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            line=dict(color=px.colors.sequential.Turbo[3], width=2),
            fillcolor="#6BAA9F",
            opacity=0.8,
            name='Skills',
            hoverinfo='r+theta',
            hovertemplate="<b>%{theta}</b>: %{r}",
            showlegend=False
        )
    )

    # Create the hover points
    for i, (category, value) in enumerate(zip(categories, values)):
        fig.add_trace(
            go.Scatterpolar(
                r=[value],
                theta=[category],
                mode="markers",
                marker=dict(
                    size=10,
                    color=px.colors.sequential.Turbo[7],
                    line=dict(color=px.colors.sequential.Turbo[9], width=2)
                ),
                showlegend=False,
                hoverinfo='text',
                hovertext=f"<b>{category}</b>: {value}",
            )
        )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],  
                color='#E0E0E0',
                gridcolor='#505050',
                gridwidth=1.5,
                linewidth=1.5,
                angle=45
            ),
            angularaxis=dict(color='#E0E0E0', gridcolor='#505050', gridwidth=1.5, linewidth=1.5, direction="clockwise")
        ),
        title="Skill Radar",
        showlegend=False
    )
    detected_skills_md = "## Detected Skills\n" + "\n".join([f"- **{skill['name']}**: {skill['details']}" for skill in data['skills_detected']])
    missing_skills_md = "## Missing Skills\n" + "\n".join([f"- **{skill['name']}**: {skill['why']}" for skill in data['skills_missing']])
    md_text= f"{detected_skills_md}\n{missing_skills_md}"

    return fig, md_text

def plot_job_match(data):
    job_matches = data["job_matches"]
    roles = [j["role"] for j in job_matches]
    match_scores = [j["match_score"] for j in job_matches]
    job_descriptions = [j["description"] for j in job_matches]
    job_requirements = [j["requirements"] for j in job_matches]
    
    hover_texts = [f"<b>Description:</b> {desc}<br><b>Requirements:</b> {req}" 
                   for desc, req in zip(job_descriptions, job_requirements)]
    
    fig = go.Figure([go.Bar(x=roles, y=match_scores, 
                             text=match_scores, 
                             hovertext=hover_texts,
                             marker_color='#FFB668')])
    fig.update_layout(title="Job Role Match Score")
    return fig
"""
def plot_experience_timeline(data):
    today = datetime.today().strftime('%Y-%m-%d')
    df = pd.DataFrame(data['experience'])
    df['start_date'] = pd.to_datetime(df['start_date'])

    df['end_date'] = df['end_date'].apply(lambda x: today if pd.isna(x) else x)
    df['end_date'] = df['end_date'].replace('present', today)
    df['end_date'] = pd.to_datetime(df['end_date']) 



    fig = px.timeline(df, x_start="start_date", x_end="end_date", y="company", color="role")
    
    fig.update_traces(hovertemplate="<b>%{y}</b><br><b>Role:</b> %{text}<br><b>Start:</b> %{x}<br><b>End:</b> %{x}",
                      text=df["role"])
    
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        title="Experience Timeline",
        plot_bgcolor='#222222',
        paper_bgcolor='#121212',
        font=dict(color="#E0E0E0"),
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Rockwell"),
        transition=dict(duration=500, easing="cubic-in-out"),
        yaxis=dict(
            showgrid=False,
            zeroline=False
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False
        )
    )
    
    fig.update_xaxes(
        dtick="M12", 
        tickformat="%Y", 
        ticklabelmode="period"
    )

    fig.update_xaxes(tickangle=45)

    return fig

def plot_improvement_progress(data): 
    tasks = [t["task"] for t in data["improvement_plan"]]
    progress = [t["progress"] for t in data["improvement_plan"]]
    deadlines = [t["deadline"] for t in data["improvement_plan"]]
    hover_texts = [f"<b>Deadline:</b> {deadline}" for deadline in deadlines]

    fig = go.Figure()

    # Add the main bars
    fig.add_trace(
        go.Bar(
            x=tasks,
            y=progress,
            text=progress,
            textposition="outside",
            hovertext=hover_texts,
            marker=dict(color='#FFB703', line=dict(color='black', width=2)),  # Darker orange
            opacity=0.8
        )
    )

    # Add the hover points
    for i, (task, prog) in enumerate(zip(tasks, progress)):
        fig.add_trace(
            go.Scatter(
                x=[task],
                y=[prog],
                mode='markers',
                marker=dict(size=10, color='#FFB703', line=dict(color='black', width=2)),  # Darker orange
                hoverinfo='text',
                hovertext=f"<b>Task:</b> {task}<br><b>Progress:</b> {prog}%",
                showlegend=False
            )
        )
    fig.update_layout(
        title="Improvement Suggestions Progress",
        plot_bgcolor='#222222',
        paper_bgcolor='#121212',
        font=dict(color="#E0E0E0"),
        yaxis=dict(range=[0, 100]),
        transition=dict(duration=500, easing="cubic-in-out"),


    )
    return fig
"""


def analyze_cv(file):
    experience_data = [
    {"company": "Company A", "role": "Software Engineer", "start_date": "2020-01-01", "end_date": "2022-06-30"},
    {"company": "Company B", "role": "Senior Engineer", "start_date": "2022-07-01", "end_date": "2023-12-31"},
    {"company": "Company C", "role": "Lead Engineer", "start_date": "2024-01-01", "end_date": "2024-05-25"},
    
    ]

    # Example of how to use the function
    #plot_experience_timeline(experience_data)

    import shutil
    
    # Save the uploaded file
    with open("uploaded_cv.pdf", "wb") as out_file:
        with open(file.name, "rb") as in_file:
            shutil.copyfileobj(in_file, out_file)

    cv_text = extract_text_from_pdf("uploaded_cv.pdf")

    # Improved JSON prompt with clearer instructions
    json_prompt = f"""You are an AI career coach. Analyze this resume and return ONLY valid JSON with no additional text, comments, or explanations.

Here are the Rules for \"experience\": [
            {{}},
            {{}}
        ]
        - If the person is currently working in a job, just omit the end_date field.
        - if not, provide the end_date in this format YYYY-MM-DD.

Return **only valid JSON** following the structure below. Do not include comments or extra text.
The JSON must follow this structure exactly:
{{
  "strengths": [
    {{"name": "Strength 1", "description": "Detailed description of Strength 1"}},
    {{"name": "Strength 2", "description": "Detailed description of Strength 2"}},
    {{"name": "Strength 3", "description": "Detailed description of Strength 3"}}
  ],
  "weaknesses": [
    {{"name": "Weakness 1", "description": "Detailed description of Weakness 1"}},
    {{"name": "Weakness 2", "description": "Detailed description of Weakness 2"}},
    {{"name": "Weakness 3", "description": "Detailed description of Weakness 3"}}
  ],
  "skills_detected": [
    {{"name": "Skill 1", "details": "Detailed description of Skill 1"}},
    {{"name": "Skill 2", "details": "Detailed description of Skill 2"}},
    {{"name": "Skill 3", "details": "Detailed description of Skill 3"}}
  ],
  "skills_missing": [
    {{"name": "Missing Skill 1", "why": "Explanation of why Missing Skill 1 is missing"}},
    {{"name": "Missing Skill 2", "why": "Explanation of why Missing Skill 2 is missing"}}
  ],
  "job_matches": [
    {{"role": "Job Title 1", "match_score": 85, "description": "Detailed description of Job Title 1", "requirements": "Requirements for Job Title 1"}},
    {{"role": "Job Title 2", "match_score": 78, "description": "Detailed description of Job Title 2", "requirements": "Requirements for Job Title 2"}},
    {{"role": "Job Title 3", "match_score": 62, "description": "Detailed description of Job Title 3", "requirements": "Requirements for Job Title 3"}}
  ],
  #"improvement_plan": [
    #{{"task": "Task 1", "progress": 40, "deadline": "2024-12-31"}},
    #{{"task": "Task 2", "progress": 60, "deadline": "2024-11-15"}},
    #{{"task": "Task 3", "progress": 20, "deadline": "2024-10-30"}}
  #],
    "experience": [
        {{"company": "Company X", "role": "Junior Developer", "start_date": "2022-01-01"}}, // if the person is currently working, omit end_date
        {{"company": "Company Y", "role": "Senior Developer", "start_date": "2023-07-01", "end_date": "2024-05-25"}},// if not, provide the end_date YYYY-MM-DD format
    ],
    "skill_categories": {{
    "Technical": 60,
    "Leadership": 80,
    "Communication": 90,
    "Design": 40
  }}
}} 

IMPORTANT: Return ONLY the JSON object. No explanations, markdown, or extra text.

Resume:
{cv_text}
"""

    # Text prompt remains the same
    text_prompt = f"""
You are an expert AI career counselor and CV reviewer.
Provide a professional, clean, and human-readable analysis using short paragraphs and structured sections.  
Keep the tone warm and constructive. Avoid markdown symbols (like *, -, #, etc.).

Use this format exactly:

---
## CV Analysis and Optimization

1. Skills Extraction
- Detected Skills: (Write important skills in 3-5 bullet points)
- Missing High-Demand Skills: (Write important mssing skills in 3-5 bullet points)

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
- Suggest 10+ potential job titles organized by fields like Marketing, Business, Product, Creative, Other.
- Write the job titles in bullet points
- Provide career field-specific advice (e.g., certifications, online portfolios) as friendly recommendations in a separate paragraph

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
                plot_strength_weakness(data), # strengths plot
                plot_skill_radar(data)[0], # skills radar
                plot_job_match(data), # job match
                #plot_improvement_progress(data), #improvement
                plot_skill_radar(data)[1], # skills text
                #plot_experience_timeline(data)
            )
        except json.JSONDecodeError as e:
            # More detailed error message for debugging
            error_msg = f"❌ JSON Parse Error: {str(e)}\nResponse received: {json_text[:100]}..."
            return (error_msg, None, None, None, None)
    except Exception as e:
        return (f"❌ AI Error: {str(e)}", None, None, None, None)

