import gradio as gr
from analyze_cv_agent import analyze_cv
import plotly.express as px
from markdown import markdown


with gr.Blocks(theme=gr.themes.Default(), css="footer {visibility: hidden}") as iface:
    
    # Custom CSS for modern styling
    custom_css = """
        .gradio-container {background-color: #f8f8f8; font-family: 'Arial', sans-serif;}
        .main-header {background-color: #3498db; color: white; padding: 20px; text-align: center; margin-bottom: 20px;}
        .main-title {font-size: 2.5em; font-weight: bold;}
        .section-title {font-size: 1.8em; color: #333; margin-top: 20px;}
        .gr-button {background-color: #2ecc71; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;}
        .gr-button:hover {background-color: #27ae60;}
        .gr-file-upload {border: 2px dashed #bbb; padding: 20px; border-radius: 10px;}
        .gr-input, .gr-textbox {border: 1px solid #ccc; border-radius: 5px; padding: 10px;}
        .gr-plot-container {box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); margin: 20px 0;}
    """

    with gr.Row(elem_classes=["main-header"]):
        gr.Markdown(f"<h1 class='main-title'>CV Analyzer AI</h1>")
    
    gr.Markdown("Upload your CV in PDF format. The AI agent will analyze and provide feedback.", elem_classes=["section-title"])
    
    # Define the markdown output
    skills_markdown = gr.Markdown()
    
    with gr.Row():
        with gr.Column():
            file_input = gr.File(label="Upload your CV (PDF)", file_types=[".pdf"], type="filepath", elem_classes=["gr-file-upload"])
        with gr.Column():
            btn = gr.Button("Analyze", variant="primary", size="lg", interactive=True, elem_classes=["gr-button"])
    
    with gr.Tabs():
        with gr.TabItem("Summary", id="summary_tab"):
            summary_output = gr.Textbox(label="AI Summary", lines=5, elem_classes=["gr-textbox"])
        with gr.TabItem("Strengths vs Weaknesses", id="strengths_tab"):
            strengths_weaknesses_plot = gr.Plot(label="Strengths vs Weaknesses", elem_classes=["gr-plot-container"])
        with gr.TabItem("Skill Radar", id="skills_tab"):
            skill_radar_plot = gr.Plot(label="Skill Radar", elem_classes=["gr-plot-container"])
        with gr.TabItem("Job Match", id="job_match_tab"):
            job_match_plot = gr.Plot(label="Job Match", elem_classes=["gr-plot-container"])
        #with gr.TabItem("Improvement Plan", id="improvement_tab"):
            #improvement_plan_plot = gr.Plot(label="Improvement Plan", elem_classes=["gr-plot-container"])

    btn.click(fn=analyze_cv, inputs=[file_input], outputs=[summary_output, strengths_weaknesses_plot, skill_radar_plot, job_match_plot])



iface.launch()
