import streamlit as st
from utils import extract_text_from_pdf, clean_text
from analyzer import get_best_role_match, analyze_resume_for_role, generate_suggestions
from job_roles import JOB_ROLES

# Page Config
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
        color: #1f2937;
    }
    .stProgress .st-bo {
        background-color: #10b981;
    }
    .skill-tag {
        display: inline-block;
        padding: 5px 12px;
        margin: 4px;
        border-radius: 15px;
        font-size: 14px;
        font-weight: 500;
    }
    .present-skill {
        background-color: #d1fae5;
        color: #065f46;
        border: 1px solid #34d399;
    }
    .missing-skill {
        background-color: #fee2e2;
        color: #991b1b;
        border: 1px solid #f87171;
    }
    .metric-label {
        font-size: 1.2rem;
        font-weight: bold;
        color: #4b5563;
    }
    .title-box {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #6366f1, #a855f7);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<div class="title-box"><h1>📄 AI Resume Analyzer with ATS Scoring</h1><p>Optimize your resume for applicant tracking systems.</p></div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.markdown("Select a target role, or let the AI suggest one based on your resume.")
        target_role = st.selectbox("Target Job Role:", ["Auto-Detect"] + list(JOB_ROLES.keys()))
        
        st.markdown("---")
        st.markdown("### How it works")
        st.markdown("""
        1. **Upload** your PDF resume.
        2. **Extract** text is parsed and cleaned.
        3. **Analyze** NLP matches keywords against job requirements.
        4. **Score** Provides an ATS readiness score and recommendations.
        """)

    # Main Content Area
    uploaded_file = st.file_uploader("Upload your resume (PDF format)", type=['pdf'])
    
    if uploaded_file is not None:
        st.success("File uploaded successfully!")
        
        if st.button("Analyze Resume 🚀", use_container_width=True):
            with st.spinner('Extracting text and analyzing with AI...'):
                
                # 1. Extract Text
                raw_text = extract_text_from_pdf(uploaded_file)
                if not raw_text.strip():
                    st.error("Could not extract text from the PDF. It might be image-based.")
                    return
                
                # 2. Clean Text
                clean_resume = clean_text(raw_text)
                
                # 3. Handle Auto-Detect
                suggested_role = None
                if target_role == "Auto-Detect":
                    suggested_role, confidence = get_best_role_match(clean_resume)
                    target_role = suggested_role
                    st.info(f"🤖 **AI Suggestion**: Based on your resume, the best fitting role is **{target_role}** (Confidence: {confidence:.2f})")
                
                # 4. Analyze against chosen role
                analysis_results = analyze_resume_for_role(clean_resume, target_role)
                
                if "error" in analysis_results:
                    st.error(analysis_results["error"])
                    return
                
                score = analysis_results["ats_score"]
                present_skills = analysis_results["present_skills"]
                missing_skills = analysis_results["missing_skills"]
                
                # --- UI Rendering ---
                st.markdown("---")
                st.header(f"📊 Analysis Results: {target_role}")
                
                # Score Section
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric(label="ATS Score", value=f"{score}%")
                with col2:
                    st.markdown("<div class='metric-label'>Resume Match Strength</div>", unsafe_allow_html=True)
                    st.progress(score / 100)
                    
                    if score >= 80:
                        st.success("Excellent! Your resume is highly matching the job role.")
                    elif score >= 50:
                        st.warning("Good, but there is room for optimization. Check missing skills.")
                    else:
                        st.error("Low match. You need to significantly tailor your resume.")

                st.markdown("---")
                
                # Skills Display Section
                col3, col4 = st.columns(2)
                
                with col3:
                    st.subheader("✅ Identified Skills")
                    if present_skills:
                        skills_html = "".join([f'<span class="skill-tag present-skill">{skill.title()}</span>' for skill in present_skills])
                        st.markdown(skills_html, unsafe_allow_html=True)
                    else:
                        st.write("No matching skills found.")
                        
                with col4:
                    st.subheader("⚠️ Missing Skills")
                    if missing_skills:
                        skills_html = "".join([f'<span class="skill-tag missing-skill">{skill.title()}</span>' for skill in missing_skills])
                        st.markdown(skills_html, unsafe_allow_html=True)
                    else:
                        st.write("Perfect! You have all the expected skills.")

                st.markdown("---")
                
                # Suggestions Section
                st.header("💡 Improvement Suggestions")
                suggestions = generate_suggestions(missing_skills, score)
                for i, suggestion in enumerate(suggestions, 1):
                    st.markdown(f"{i}. *{suggestion}*")
                    
                st.markdown("---")
                # Optional: Show extracted text preview
                with st.expander("View Extracted Resume Text"):
                    st.text_area("Raw Text Preview", raw_text, height=200, disabled=True)

if __name__ == '__main__':
    main()
