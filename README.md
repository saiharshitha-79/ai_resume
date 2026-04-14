# AI Resume Analyzer with ATS Scoring

This is a Streamlit-based web application that uses Natural Language Processing (NLP) to analyze your PDF resume against various job roles. It calculates an Applicant Tracking System (ATS) score using TF-IDF and keyword matching, identifies missing skills, and provides actionable feedback.

## Advanced Features Implemented 🚀
- **1. Precise Job Role Targets**: Use TF-IDF Document Cosine Similarity to automatically identify what your historical experience aligns with (Data Scientist, UI/UX, Backend, etc.).
- **2. The Radar Matrix**: Visual analytical `Plotly` graphs that dynamically plot your skill clusters (e.g. Frontend vs Cloud ops).
- **3. Custom JD Matcher**: Trying to beat the specific keyword-filter of your dream job? Paste the exact Job Description into Tab 2, and the system extracts the hardest requirement strings to match you up instantly.
- **4. Grammar & Structural ATS Scanning**: A heuristic engine determines missing mandatory ATS headers and flags weak/cliché resume verbs (e.g. substituting "helped" for "architected").
- **5. Generative AI Rewrite Engine**: Enter a Gemini API Key to natively rewrite poor, low-impact sentences into high-converting quantifiable bullet points natively on the UI!
- **6. Downloadable PDF Reports**: Automatically generate and download a compiled PDF Report of your overall resume health, missing data structures, and verbatim improvement recommendations via `FPDF`.

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
