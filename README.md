# AI Resume Analyzer with ATS Scoring

This is a Streamlit-based web application that uses Natural Language Processing (NLP) to analyze your PDF resume against various job roles. It calculates an Applicant Tracking System (ATS) score using TF-IDF and keyword matching, identifies missing skills, and provides actionable feedback.

## Features
- **Auto-Detect Job Role**: Uses Cosine Similarity to find the best-matching job title based on your resume content.
- **ATS Score Calculation**: Evaluates your resume against industry-standard keywords.
- **Skill Extraction**: Clear visual indicators for present and missing skills.
- **Dynamic Suggestions**: Actionable steps to improve your resume.

---

## 🚀 How to Install and Run Locally

If you want to install and run this application on your own computer, follow these steps:

### Prerequisites
Make sure you have **Python 3.8+** installed on your system.

### Step 1: Clone or Download the Project
Navigate to the directory where you have saved the project files.

### Step 2: Create a Virtual Environment (Recommended)
Creating a virtual environment ensures that the application's dependencies don't interfere with other Python projects.
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
Install all required libraries such as `streamlit`, `scikit-learn`, and `PyPDF2`.
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
Start the Streamlit server!
```bash
streamlit run app.py
```
After running this command, your browser will automatically open to `http://localhost:8501`.

---

## 🌍 How to Deploy the App Online (Free)

The easiest way to make this app accessible to anyone on the internet is by using **Streamlit Community Cloud**. It is 100% free.

1. **Upload to GitHub**:
   - Create a free account on [GitHub](https://github.com/).
   - Create a new repository and upload all the files (`app.py`, `analyzer.py`, `job_roles.py`, `utils.py`, `requirements.txt`).
   
2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io/) and sign in with your GitHub account.
   - Click **"New app"**.
   - Select the repository you just created.
   - Set the Main file path to `app.py`.
   - Click **Deploy!**

Within 60 seconds, your app will be live and you will get a public link that you can share with anyone!
