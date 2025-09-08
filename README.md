✨ Smart Resume Reviewer 

An intelligent web application built for the 

AI AVENGERS hackathon submission, designed to give job seekers a competitive edge by providing instant, AI-powered resume feedback.


(Note: You can replace the screenshot URL above with your own)

🎯 The Problem 

The modern job search is filled with challenges that often lead to a frustrating experience and missed opportunities. We identified three core issues for job seekers:



The Black Hole: A vast majority of resumes are rejected by Applicant Tracking Systems (ATS) before a human ever sees them.


The Tailoring Trap: Crafting a unique, tailored resume for every single job application is exhausting and time-consuming.


The Feedback Barrier: Access to expert, personalized resume feedback is often expensive or unavailable, leaving candidates guessing.

🚀 Our Solution 

The Smart Resume Reviewer is an intelligent platform that provides instant, data-driven feedback by analyzing a user's resume against a specific job role. It helps users create a document that stands out to both recruiters and algorithms, transforming their resumes from good to interview-winning.



✨ Key Features 

Our application is packed with features to streamline the resume optimization process:


Flexible Input: Users can upload a PDF or TXT file, or simply paste text for both their resume and the job description.


Deep AI Analysis: A two-step AI process provides a comprehensive review, including an overall score, key strengths, areas for improvement, and missing keywords.


ATS Compliance Tips: The app provides crucial, expert-level advice on how to optimize the resume to successfully pass through automated screening systems.


Professional PDF Generation: The application generates a beautifully formatted, enhanced resume in a professional template, ready to be downloaded and submitted.

🛠️ How It Works: System Architecture 

The application follows a stable and reliable two-step AI process:


User Input: The user provides their resume and a target job role on the Streamlit frontend.


AI Analysis (Call 1): The backend sends the data to the Gemini API to get a detailed analysis (score, strengths, ATS tips, etc.) as a JSON object.


AI Rewrite (Call 2): The original resume and the AI's analysis are sent back to the Gemini API, which rewrites the resume into a structured JSON format.


PDF Templating: The structured resume data is passed to a Jinja2 HTML template.


PDF Generation: The xhtml2pdf library converts the rendered HTML into a high-quality, downloadable PDF.



Display Results: The complete analysis and PDF download link are presented to the user.

💻 Tech Stack 


AI Engine: Google Gemini 1.5 Flash (with structured JSON output) 

Frontend: Streamlit


Backend & PDF Handling:



PDF Reading: PyMuPDF (fitz) 


PDF Writing: Jinja2 & xhtml2pdf 


Programming Language: Python

⚙️ Setup and Installation
To run this project locally, follow these steps:

1. Prerequisites

Python 3.8+

A Google AI API Key

2. Clone the Repository

Bash

git clone https://github.com/VanshTyagi-ux/smart-resume-reviewer.git
cd smart-resume-reviewer
3. Create a Virtual Environment

Bash

# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
4. Install Dependencies
Create a requirements.txt file with the following content:

streamlit
PyMuPDF
python-dotenv
google-generativeai
Jinja2
xhtml2pdf
Then, install the packages:

Bash

pip install -r requirements.txt
5. Set Up Environment Variables
Create a file named .env in the root of your project folder and add your Google API key:

GOOGLE_API_KEY="YOUR_API_KEY_HERE"
6. Project Structure for Templates
The application requires a templates folder to store the HTML files for PDF generation. Ensure your project structure looks like this:

smart-resume-reviewer/
├── app.py
├── templates/
│   ├── template_dark.html
│   └── template_light.html
└── ... (other files)
7. Run the Application

Bash

streamlit run app.py
🔮 Future Enhancements 

What's next for the Smart Resume Reviewer?


Cover Letter Generation: Automatically create a tailored cover letter based on the resume and job description.


Multi-Language Support: Analyze and improve resumes in other languages.


LinkedIn Profile Optimization: Provide AI-driven suggestions for improving a user's LinkedIn profile.


User Accounts: Allow users to save their resumes, track applications, and view their history.

🏆 The Team: AI AVENGERS 

This project was a hackathon submission by:

.Vaibhav Srivastava

.Vansh Tyagi

.Varun Goel 
