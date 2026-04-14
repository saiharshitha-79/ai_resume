import streamlit as st
import plotly.express as px
import pandas as pd
import re
from utils import extract_text_from_pdf, clean_text, generate_pdf_report
from analyzer import (
    get_best_role_match, analyze_resume_for_role, generate_suggestions,
    analyze_custom_jd, evaluate_structure, analyze_action_verbs, generate_radar_chart_data
)
from job_roles import JOB_ROLES
from llm_helper import rewrite_bullet_points, generate_cover_letter, generate_interview_questions
import auth

# Page Config
st.set_page_config(
    page_title="AI Resume SaaS",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; color: #1f2937; }
    .stProgress .st-bo { background-color: #10b981; }
    .skill-tag { display: inline-block; padding: 5px 12px; margin: 4px; border-radius: 15px; font-size: 14px; font-weight: 500; }
    .present-skill { background-color: #d1fae5; color: #065f46; border: 1px solid #34d399; }
    .missing-skill { background-color: #fee2e2; color: #991b1b; border: 1px solid #f87171; }
    .weak-verb { background-color: #fef08a; color: #854d0e; border: 1px solid #facc15; }
    .strong-verb { background-color: #e0e7ff; color: #3730a3; border: 1px solid #818cf8; }
    .metric-label { font-size: 1.2rem; font-weight: bold; color: #4b5563; }
    .title-box { text-align: center; padding: 2rem; background: linear-gradient(135deg, #1e293b, #3b82f6); color: white; border-radius: 10px; margin-bottom: 2rem; }
    .login-box { max-width: 400px; margin: auto; padding: 30px; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

# ----------------- SESSION STATE -----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# ----------------- AUTHENTICATION UI -----------------
if not st.session_state.logged_in:
    st.markdown('<div class="title-box"><h1>🔒 Enterprise Resume Analyzer</h1><p>Please log in to access the SaaS AI Platform.</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            l_username = st.text_input("Username", key="l_user")
            l_password = st.text_input("Password", type="password", key="l_pass")
            if st.button("Secure Login"):
                if l_username and l_password:
                    success, msg = auth.login_user(l_username, l_password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.username = l_username
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Enter both fields.")
                    
        with tab2:
            r_username = st.text_input("New Username", key="r_user")
            r_password = st.text_input("New Password", type="password", key="r_pass")
            if st.button("Create Account"):
                if r_username and r_password:
                    success, msg = auth.register_user(r_username, r_password)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.warning("Enter both fields.")
    st.stop()


# --------------------- MAIN APP ---------------------
def main():
    st.markdown('<div class="title-box"><h1>🚀 Premium AI Resume Analyzer</h1><p>SaaS Dashboard: Optimize, Track, and Generate using Advanced NLP.</p></div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header(f"👤 Welcome, {st.session_state.username}!")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()
            
        st.markdown("---")
        st.header("⚙️ Configuration")
        target_role = st.selectbox("Target Job Role (For Tab 2):", ["Auto-Detect"] + list(JOB_ROLES.keys()))
        
        st.markdown("---")
        st.header("🤖 AI Settings")
        api_key_input = st.text_input("Gemini API Key (Required for AI Toolkit):", type="password")

    # Main Content Area
    uploaded_file = st.file_uploader("Upload your resume (PDF format)", type=['pdf'])
    
    if uploaded_file is not None:
        raw_text = extract_text_from_pdf(uploaded_file)
        if not raw_text.strip():
            st.error("Could not extract text. It might be image-based.")
            return
        
        clean_resume = clean_text(raw_text)
        
        # Determine actual role
        suggested_role = None
        if target_role == "Auto-Detect":
            suggested_role, confidence = get_best_role_match(clean_resume)
            actual_role = suggested_role
        else:
            actual_role = target_role
            
        # Analyze globally accessible data needed for multiple tabs
        analysis_results = analyze_resume_for_role(clean_resume, actual_role)
        score = analysis_results.get("ats_score", 0)
        present_skills = analysis_results.get("present_skills", [])
        missing_skills = analysis_results.get("missing_skills", [])
        
        # Action Handler: Save score on initial upload evaluation
        if "last_analyzed_file" not in st.session_state or st.session_state.last_analyzed_file != uploaded_file.name:
            auth.save_score(st.session_state.username, actual_role, score)
            st.session_state.last_analyzed_file = uploaded_file.name

        st.success("Resume loaded! Explore your SaaS tools below:")
        
        # Create Tabs
        t_dash, t_role, t_jd, t_health, t_ai = st.tabs([
            "📊 Dashboard & History",
            "🎯 Role Match", 
            "📋 Custom JD Match", 
            "⚕️ Health & Structure", 
            "✨ AI Toolkit"
        ])
        
        # --- TAB 1: DASHBOARD HISTORY ---
        with t_dash:
            st.header("Your ATS Progression")
            history = auth.get_user_history(st.session_state.username)
            if history:
                df = pd.DataFrame(history)
                # Convert timestamp for better plotting
                df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%m-%d %H:%M')
                fig = px.line(df, x='timestamp', y='score', color='target_role', markers=True, title="Historical ATS Score Trends")
                fig.update_layout(yaxis=dict(range=[0, 100]))
                st.plotly_chart(fig, use_container_width=True)
                
                with st.expander("View Raw Logs"):
                    st.dataframe(df)
            else:
                st.info("Upload more resumes to build your history chart!")

        # --- TAB 2: ROLE MATCH ---
        with t_role:
            if target_role == "Auto-Detect":
                st.info(f"🤖 **AI Suggestion**: Best fitting standard role is **{actual_role}**")
            
            if "error" not in analysis_results:
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric(label="ATS Score (Standard Check)", value=f"{score}%")
                    st.markdown("<div class='metric-label'>Resume Match Strength</div>", unsafe_allow_html=True)
                    st.progress(score / 100)
                
                with col2:
                    st.markdown("### Profile Radar Mapping")
                    radar_df = generate_radar_chart_data(present_skills, actual_role)
                    if radar_df['r'].sum() > 0:
                        fig = px.line_polar(radar_df, r='r', theta='theta', line_close=True, range_r=[0,5])
                        fig.update_traces(fill='toself')
                        st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                col3, col4 = st.columns(2)
                with col3:
                    st.subheader("✅ Identified Skills")
                    if present_skills:
                        st.markdown("".join([f'<span class="skill-tag present-skill">{skill.title()}</span>' for skill in present_skills]), unsafe_allow_html=True)
                with col4:
                    st.subheader("⚠️ Missing Skills")
                    if missing_skills:
                        st.markdown("".join([f'<span class="skill-tag missing-skill">{skill.title()}</span>' for skill in missing_skills]), unsafe_allow_html=True)
                        
                st.markdown("---")
                suggestions = generate_suggestions(missing_skills, score)
                report_path = generate_pdf_report(score, present_skills, missing_skills, actual_role, suggestions)
                with open(report_path, "rb") as pdf_file:
                    st.download_button("📥 Download ATS Health Report (PDF)", data=pdf_file, file_name="ATS_Analysis_Report.pdf", mime="application/pdf", type="primary")

        # --- TAB 3: CUSTOM JD MATCH ---
        with t_jd:
            st.header("Custom Keyword Optimization")
            linkedin_url = st.text_input("Enter your LinkedIn URL (Bonus ATS Points):")
            if linkedin_url:
                if re.match(r"^https?://(www\.)?linkedin\.com/in/.*$", linkedin_url):
                    st.success("Valid LinkedIn URL detected! +5 ATS Visibility Points.")
                else:
                    st.warning("Invalid formatting. Use: https://linkedin.com/in/yourprofile")
                    
            custom_jd = st.text_area("Paste the exact Job Description here:", height=150)
            if st.button("Analyze JD Accuracy"):
                if custom_jd.strip():
                    with st.spinner("Analyzing Custom JD..."):
                        jd_results = analyze_custom_jd(clean_resume, custom_jd)
                        st.metric("JD Targeted Match", f"{jd_results['ats_score']}%")
                        colA, colB = st.columns(2)
                        colA.markdown(f"**Matched:** {', '.join(jd_results['present_skills'])}")
                        colB.markdown(f"**Missing:** {', '.join(jd_results['missing_skills'])}")
                else:
                    st.warning("Paste a JD.")

        # --- TAB 4: HEALTH & STRUCTURE ---
        with t_health:
            st.header("Semantic Resume Health")
            structure = evaluate_structure(raw_text)
            
            colX, colY = st.columns(2)
            with colX:
                st.subheader("ATS Section Integrity")
                if structure["missing_sections"]:
                    st.error(f"**Missing Critical Sections:** {', '.join(structure['missing_sections'])}")
                else:
                    st.success("All critical ATS sections found!")
            with colY:
                st.metric("Total Word Density", structure["word_count"])
                st.caption(structure["length_feedback"])

            st.markdown("---")
            verbs = analyze_action_verbs(clean_resume)
            st.subheader("Action Verb Optimization")
            if verbs["strong_verbs"]:
                st.markdown("**Strong Impact Verbs:** " + "".join([f'<span class="skill-tag strong-verb">{v}</span>' for v in set(verbs["strong_verbs"])]), unsafe_allow_html=True)
            if verbs["weak_verbs"]:
                st.markdown("**Weak/Cliché Verbs (REPLACE THESE):** " + "".join([f'<span class="skill-tag weak-verb">{v}</span>' for v in set(verbs["weak_verbs"])]), unsafe_allow_html=True)

        # --- TAB 5: AI TOOLKIT ---
        with t_ai:
            st.header("✨ Master AI Toolkit")
            st.markdown("Automate your job applications using Contextual Generative AI.")
            
            inner1, inner2, inner3 = st.tabs(["Rewrite Bullet", "Draft Cover Letter", "Interview Prep"])
            
            with inner1:
                st.subheader("Transform Weak Bullets")
                bullet = st.text_area("Boring Bullet Point:")
                if st.button("Rewrite ✏️"):
                    if not api_key_input: st.error("Inject API Key in Sidebar")
                    else:
                        with st.spinner("Rewriting..."):
                            res = rewrite_bullet_points(bullet, api_key_input)
                            st.success(res.get("result", res.get("error")))
            
            with inner2:
                st.subheader("Contextual Cover Letter Generator")
                cl_jd = st.text_area("Job Description (For the Cover Letter):", height=100)
                if st.button("Draft Cover Letter ✉️"):
                    if not api_key_input: st.error("Inject API Key in Sidebar")
                    else:
                        with st.spinner("Drafting professional letter... (Takes 5-10s)"):
                            res = generate_cover_letter(raw_text, cl_jd, api_key_input)
                            if "result" in res:
                                st.markdown(res['result'])
                                st.download_button("Download Text", data=res['result'], file_name="CoverLetter.txt")
                            else:
                                st.error(res["error"])
                                
            with inner3:
                st.subheader("Defense Prep: Overcoming Weaknesses")
                st.write(f"Based on your scan, you are missing these skills for {actual_role}: **{', '.join(missing_skills)}**")
                if st.button("Generate Interrogation Prep 🎙️"):
                    if not api_key_input: st.error("Inject API Key in Sidebar")
                    else:
                        with st.spinner("Predicting technical questions..."):
                            res = generate_interview_questions(missing_skills, actual_role, api_key_input)
                            st.markdown(res.get("result", res.get("error")))

if __name__ == '__main__':
    main()
