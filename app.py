import gradio as gr
from analyze_cv_agent import analyze_cv

iface = gr.Interface(
    fn=analyze_cv,  # Updated to return data + visuals
    inputs=gr.File(label="Upload your CV (PDF)", file_types=[".pdf"]),
    outputs=[
        gr.Textbox(label="AI Summary"),
        gr.Plot(label="Strengths vs Weaknesses"),
        gr.Plot(label="Skill Radar"),
        gr.Plot(label="Job Match"),
        gr.Plot(label="Improvement Plan"),
    ],
    title="CV Analyzer AI",
    description="Upload your CV in PDF format. The AI agent will analyze and provide feedback.",
)


iface.launch()
