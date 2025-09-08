import os
import streamlit as st
import fitz  # PyMuPDF
import json
from dotenv import load_dotenv
import google.generativeai as genai

# NEW IMPORTS for templating and PDF generation
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
from io import BytesIO

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Smart Resume Reviewer",
    page_icon="✨",
    layout="wide",
)

# --- STYLING (CSS FOR DARK MODE) ---
dark_mode_css = """
<style>
    /* --- MODIFIED: General Styles - Blue Dark Mode with new text color --- */
    .stApp { 
        background-color: #0F172A; 
        color: #A5D8FF; /* New vibrant light blue text color */
    }
    h1 { color: #FFFFFF; text-align: center; font-weight: bold; }
    .st-emotion-cache-10trblm { text-align: center; }
    h2 { color: #94A3B8; border-bottom: 2px solid #1E2B3B; padding-bottom: 5px; }
    .stTextInput, .stTextArea, .stFileUploader { background-color: #1E293B; border-radius: 10px; border: 1px solid #334155; padding: 15px; box-shadow: 0 8px 16px rgba(0,0,0,0.2); }
    div[data-testid="stButton"] > button { background: linear-gradient(90deg, #3B82F6, #60A5FA); color: white; border-radius: 10px; padding: 12px 24px; font-size: 18px; font-weight: bold; border: none; box-shadow: 0 4px 14px 0 rgba(59, 130, 246, 0.39); transition: all 0.3s ease; }
    div[data-testid="stButton"] > button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px 0 rgba(59, 130, 246, 0.5); filter: brightness(1.1); }
    div[data-testid="stMetric"] { background-color: #1E293B; border-left: 5px solid #3B82F6; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    [data-testid="stSidebar"] { background-color: #1E293B; border-right: 1px solid #334155; }
    /* --- MODIFIED: Sidebar text color to match new theme --- */
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] .stMarkdown { color: #A5D8FF !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { background-color: transparent; border-radius: 8px; color: #94A3B8; }
    .stTabs [aria-selected="true"] { background-color: #334155; color: #FFFFFF; font-weight: bold; }
    
    /* --- FINAL FIX: Make all radio button labels bright and visible --- */
    div[data-testid="stRadio"] > label {
        font-weight: bold;
        color: #94A3B8 !important; /* Lighter Slate for the label */
        font-size: 1.1em;
    }
    div[data-testid="stRadio"] p {
        color: #A5D8FF !important; /* Vibrant light blue text for the options */
        font-size: 1em;
    }
    
    [data-testid="stHeader"] { background-color: #0F172A; }
    /* --- MODIFIED: Header icons and text color --- */
    [data-testid="stHeader"] [data-testid="stToolbar"] button, [data-testid="stHeader"] a { color: #A5D8FF !important; }
    [data-testid="stHeader"] [data-testid="stToolbar"] button svg { fill: #A5D8FF !important; }
</style>
"""

st.markdown(dark_mode_css, unsafe_allow_html=True)

# --- EXAMPLE CONTENT ---
EXAMPLE_RESUME = """
John Doe
Software Engineer
john.doe@email.com | (123) 456-7890 | linkedin.com/in/johndoe

Summary
Detail-oriented Software Engineer with 3 years of experience in developing and maintaining web applications. Proficient in Python and JavaScript. Seeking to leverage my skills to contribute to a dynamic engineering team.

Experience
Software Engineer | Tech Solutions Inc. | Jan 2022 - Present
- Developed new user-facing features using React.js.
- Built reusable components and front-end libraries for future use.
- Collaborated with other team members and stakeholders.

Education
Bachelor of Science in Computer Science | State University | 2018 - 2022

Skills
Programming Languages: Python, JavaScript, Java
Frameworks: React, Node.js, Flask
Databases: MongoDB, PostgreSQL
"""

EXAMPLE_JOB_ROLE = "Frontend Software Engineer"

EXAMPLE_JD = """
We are looking for a Frontend Software Engineer to join our team. The ideal candidate will have 2-4 years of experience with React, TypeScript, and modern CSS frameworks.

Responsibilities:
- Develop and maintain user-facing features using React.js and TypeScript.
- Optimize applications for maximum speed and scalability.
- Work with product managers and designers to translate concepts into functional requirements.
- Write clean, maintainable, and well-documented code.

Requirements:
- Strong proficiency in JavaScript, including DOM manipulation and the JavaScript object model.
- Thorough understanding of React.js and its core principles.
- Experience with popular React.js workflows (such as Redux).
- Familiarity with RESTful APIs.
- Experience with TypeScript and Node.js.
"""


# --- SETUP & API CONFIG ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("Google AI API key not found. Please add it to your .env file or Streamlit secrets.")
else:
    genai.configure(api_key=api_key)


# --- HELPER & CORE AI FUNCTIONS ---
def extract_text_from_file(uploaded_file):
    """Extracts text from an uploaded PDF or TXT file."""
    try:
        if uploaded_file.type == "application/pdf":
            pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            text = "".join(page.get_text() for page in pdf_document)
            return text
        elif uploaded_file.type == "text/plain":
            return uploaded_file.read().decode("utf-8")
        else:
            st.error(f"Unsupported file type: {uploaded_file.type}")
            return None
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None

def create_templated_pdf(resume_data):
    """Renders an HTML template with resume data and converts it to a PDF."""
    if not os.path.exists('templates'):
        st.error("The 'templates' folder is missing.")
        return None
        
    env = Environment(loader=FileSystemLoader('templates'))
    template_name = "template_dark.html" # Hardcoded to the dark theme template
    
    try:
        template = env.get_template(template_name)
    except Exception as e:
        st.error(f"Could not load template file: {template_name}. Error: {e}")
        return None

    html_out = template.render(resume=resume_data)
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(BytesIO(html_out.encode("UTF-8")), dest=pdf_buffer)

    if pisa_status.err:
        st.error(f"PDF generation failed: {pisa_status.err}")
        return None
    
    return pdf_buffer.getvalue()

def sanitize_resume_data(resume_json):
    """
    Normalizes keys in the resume JSON from the AI to ensure consistency for the template.
    """
    if 'education' in resume_json and isinstance(resume_json.get('education'), list):
        for item in resume_json['education']:
            if isinstance(item, dict):
                if 'school' in item and 'university' not in item:
                    item['university'] = item.pop('school')
                if 'major' in item and 'degree' not in item:
                    item['degree'] = item.pop('major')

    if 'experience' in resume_json and isinstance(resume_json.get('experience'), list):
        for item in resume_json['experience']:
            if isinstance(item, dict):
                if 'role' in item and 'title' not in item:
                    item['title'] = item.pop('role')

    return resume_json

# --- NEW: Enhanced AI Prompt and Two-Step Process ---
def get_resume_analysis(resume_text, target_job_role, job_description_text):
    """AI Call 1: Get only the analysis as a JSON object, now with ATS tips."""
    
    job_description_section = ""
    if job_description_text and job_description_text.strip():
        job_description_section = f"""
        For a more detailed analysis, here is the specific Job Description:
        ---
        {job_description_text}
        ---
        """
    
    prompt = f"""
    You are an expert career coach and ATS specialist. Analyze the provided resume for the target job role of "{target_job_role}".
    {job_description_section}
    If a job description was provided, tailor your feedback specifically to it. If not, provide general feedback based on industry standards for the role of "{target_job_role}".

    Return ONLY a JSON object with the following keys:
    - "overall_score": An integer score from 0 to 100.
    - "strengths": A list of 3-4 key strengths.
    - "areas_for_improvement": A list of 3-4 specific areas for improvement.
    - "missing_keywords": A list of essential keywords.
    - "formatting_and_clarity": A brief paragraph on the resume's formatting.
    - "ats_compliance_tips": A list of 2-3 tips to make the resume more ATS-friendly.

    Resume:
    ---
    {resume_text}
    ---
    """
    try:
        generation_config = {"response_mime_type": "application/json"}
        model = genai.GenerativeModel('gemini-1.5-flash', generation_config=generation_config)
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        return {"error": f"Failed to get analysis: {e}"}

def get_improved_resume(resume_text, analysis):
    """AI Call 2: Rewrite the resume based on the analysis."""
    # --- FINAL FIX: Added explicit instructions to preserve all content ---
    prompt = f"""
    You are an expert resume writer. Your task is to rewrite the 'Original Resume' into a structured JSON object.
    
    CRITICAL INSTRUCTION: You MUST transfer ALL information (personal details, every job experience, every education entry, every skill, and all achievements) from the original resume into the final JSON. DO NOT discard or omit any details. Your goal is to reformat and enhance the phrasing, not to summarize or remove content.

    Based on the 'Original Resume' and the provided 'Analysis and Feedback', create a JSON object with the keys: "personal_details", "summary", "experience", "education", and "skills".

    - For the 'experience' section, rephrase the original bullet points to be more impactful, using action verbs and quantifying results where possible.
    - For the 'education' section, ensure all details like degree, university, and dates are included.

    Original Resume:
    ---
    {resume_text}
    ---
    Analysis and Feedback:
    ---
    {json.dumps(analysis, indent=2)}
    ---
    """
    try:
        generation_config = {"response_mime_type": "application/json"}
        model = genai.GenerativeModel('gemini-1.5-flash', generation_config=generation_config)
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        return {"error": f"Failed to rewrite resume: {e}"}

# --- NEW: Functions for State Management ---
def clear_results():
    """Clears previous results from the session state."""
    if 'feedback_data' in st.session_state:
        del st.session_state.feedback_data

def load_example():
    """Loads example content into the session state for text areas."""
    st.session_state.target_job_role_input = EXAMPLE_JOB_ROLE
    st.session_state.jd_pasted_text = EXAMPLE_JD
    st.session_state.resume_text_pasted = EXAMPLE_RESUME
    clear_results()

# --- STREAMLIT USER INTERFACE ---
with st.sidebar:
    st.markdown("---")
    st.header("About This Project")
    st.markdown(
        """
        This project was created by **Team AI AVENGERS** for our hackathon.
        **Team Members:**
        - VAIBHAV SRIVASTAVA
        - VANSH TYAGI
        - VARUN GOEL
        """
    )
    st.markdown("---")
    st.button("Load Example", on_click=load_example, help="Load a sample resume and job description to test the app.")

st.title("✨ Smart Resume Reviewer ✨")
st.write("Upload your resume and a job description to get instant, AI-powered feedback and a rewritten resume tailored for the role.")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.header("📄 Your Resume")
    resume_input_method = st.radio(
        "Select Resume Input Method",
        ("Upload a File (PDF or TXT)", "Paste Text"),
        key="resume_input_method",
        label_visibility="collapsed"
    )

    uploaded_file = None
    resume_text_pasted = ""

    if resume_input_method == "Upload a File (PDF or TXT)":
        uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "txt"], on_change=clear_results, label_visibility="collapsed")
    else:
        resume_text_pasted = st.text_area("Paste your resume text here", height=200, key="resume_text_pasted", on_change=clear_results)


with col2:
    st.header("🎯 Target Job")
    target_job_role_input = st.text_input("Enter the Target Job Role (e.g., Data Scientist)", key="target_job_role_input", on_change=clear_results)
    
    jd_input_method = st.radio(
        "Optional: Provide Full Job Description",
        ("Paste Text", "Upload a File (PDF or TXT)"),
        key="jd_input_method"
    )

    jd_uploaded_file = None
    jd_pasted_text = ""

    if jd_input_method == "Upload a File (PDF or TXT)":
        jd_uploaded_file = st.file_uploader("Upload Job Description", type=["pdf", "txt"], on_change=clear_results, label_visibility="collapsed")
    else:
        jd_pasted_text = st.text_area("Paste the job description here...", height=195, key="jd_pasted_text", on_change=clear_results)


if st.button("🚀 Enhance My Resume", use_container_width=True, type="primary"):
    resume_text = ""
    if resume_input_method == "Upload a File (PDF or TXT)" and uploaded_file:
        resume_text = extract_text_from_file(uploaded_file)
    elif resume_input_method == "Paste Text" and resume_text_pasted:
        resume_text = resume_text_pasted

    target_role = st.session_state.target_job_role_input
    
    jd_text = ""
    if jd_input_method == "Upload a File (PDF or TXT)" and jd_uploaded_file:
        jd_text = extract_text_from_file(jd_uploaded_file)
    elif jd_input_method == "Paste Text" and jd_pasted_text:
        jd_text = jd_pasted_text

    if not resume_text:
        st.error("Please provide your resume using the selected method (Upload or Paste).")
    elif not target_role:
        st.error("Please enter the Target Job Role.")
    else:
        st.session_state.feedback_data = {}
        
        with st.spinner("Step 1/2: Analyzing your resume... 🧐"):
            analysis_data = get_resume_analysis(resume_text, target_role, jd_text)
        
        if "error" in analysis_data:
            st.error(f"Analysis Failed: {analysis_data['error']}")
        else:
            with st.spinner("Step 2/2: Rewriting your resume... ✍️"):
                improved_resume_data = get_improved_resume(resume_text, analysis_data)

            if "error" in improved_resume_data:
                st.error(f"Rewrite Failed: {improved_resume_data['error']}")
                st.session_state.feedback_data = {"analysis": analysis_data, "improved_resume": {}}
                st.warning("Could not rewrite the resume, but the analysis is available in the dashboard.")
            else:
                sanitized_resume_data = sanitize_resume_data(improved_resume_data)
                st.success("Your resume review and rewrite is complete!")
                st.session_state.feedback_data = {
                    "analysis": analysis_data,
                    "improved_resume": sanitized_resume_data
                }

# --- RESULTS DISPLAY (using TABS for better organization) ---
if 'feedback_data' in st.session_state and st.session_state.feedback_data:
    data = st.session_state.feedback_data
    analysis = data.get("analysis", {})
    improved_resume_data = data.get("improved_resume", {})

    tab1, tab2, tab3 = st.tabs(["📊 Feedback Dashboard", "📝 Improved Resume", "🔍 Detailed Analysis"])

    with tab1:
        st.header("Feedback Dashboard")
        if analysis:
            score_col, strength_col = st.columns(2)
            with score_col:
                st.metric(label="**Overall Resume Score**", value=f"{analysis.get('overall_score', 0)}/100")
            with strength_col:
                st.success("**✅ Key Strengths**")
                for item in analysis.get("strengths", []):
                    st.markdown(f"- {item}")

            st.warning("**⚠️ Areas for Improvement**")
            for item in analysis.get("areas_for_improvement", []):
                st.markdown(f"- {item}")
        else:
            st.info("No analysis data available.")

    with tab2:
        st.header("Your New Professional Resume")
        if improved_resume_data:
            st.info("Use the download button to get the beautifully formatted PDF.")
            # --- MODIFIED: PDF is now always generated with the dark mode template ---
            pdf_output = create_templated_pdf(improved_resume_data) 
            
            if pdf_output:
                st.download_button(
                    label="📄 Download Formatted Resume (PDF)",
                    data=pdf_output,
                    file_name=f"Improved_Resume_{improved_resume_data.get('personal_details', {}).get('name', 'Applicant').replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary"
                )
            st.markdown("---")
            with st.expander("Show Raw JSON Data for Nerds 🤓"):
                st.json(improved_resume_data)
        else:
            st.error("Could not generate the improved resume data to create a PDF.")

    with tab3:
        st.header("Detailed Analysis")
        if analysis:
            st.info("**🔑 Missing Keywords**")
            st.write(", ".join(analysis.get("missing_keywords", ["None found."])))
            st.markdown("---")
            st.info("**🤖 ATS Compliance Tips**")
            for item in analysis.get("ats_compliance_tips", []):
                st.markdown(f"- {item}")
            st.markdown("---")
            with st.expander("**Formatting & Clarity Feedback**"):
                st.write(analysis.get("formatting_and_clarity", "N_A"))
        else:
            st.info("No analysis data available.")