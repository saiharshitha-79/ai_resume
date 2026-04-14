import streamlit as st
import plotly.express as px
from utils import extract_text_from_pdf, clean_text
from analyzer import (
    get_best_role_match, analyze_resume_for_role, generate_suggestions,
    analyze_custom_jd, evaluate_structure, analyze_action_verbs, generate_radar_chart_data
)
from job_roles import JOB_ROLES
from llm_helper import rewrite_bullet_points

# Page Config
st.set_page_config(
    page_title="AI Resume Analyzer v2",
    page_icon="📄",
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
    .title-box { text-align: center; padding: 2rem; background: linear-gradient(135deg, #2563eb, #9333ea); color: white; border-radius: 10px; margin-bottom: 2rem; }
    </style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<div class="title-box"><h1>📄 Advanced AI Resume Analyzer</h1><p>Optimize your resume with standard ATS rules, custom JDs, and Generative AI.</p></div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        target_role = st.selectbox("Target Job Role (For Tab 1):", ["Auto-Detect"] + list(JOB_ROLES.keys()))
        
        st.markdown("---")
        st.header("🤖 AI Settings")
        st.markdown("To enable the AI Bullet Rewriter, enter your **Gemini API Key**:")
        api_key_input = st.text_input("Gemini API Key:", type="password", placeholder="AIzaSy...")
        st.caption("Get a free key from Google AI Studio")

    # Main Content Area
    uploaded_file = st.file_uploader("Upload your resume (PDF format)", type=['pdf'])
    
    if uploaded_file is not None:
        raw_text = extract_text_from_pdf(uploaded_file)
        if not raw_text.strip():
            st.error("Could not extract text from the PDF. It might be image-based.")
            return
        
        clean_resume = clean_text(raw_text)
        
        # Determine actual role
        suggested_role = None
        if target_role == "Auto-Detect":
            suggested_role, confidence = get_best_role_match(clean_resume)
            actual_role = suggested_role
        else:
            actual_role = target_role

        st.success("Resume loaded! Explore the advanced analysis tabs below:")
        
        # Create Tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "🎯 Role Match", 
            "📋 Custom JD Match", 
            "⚕️ Health & Structure", 
            "✨ AI Rewriter"
        ])
        
        # --- TAB 1: Role Match ---
        with tab1:
            if target_role == "Auto-Detect":
                st.info(f"🤖 **AI Suggestion**: Best fitting standard role is **{actual_role}** (Confidence: {confidence:.2f})")
            
            analysis_results = analyze_resume_for_role(clean_resume, actual_role)
            if "error" not in analysis_results:
                score = analysis_results["ats_score"]
                present_skills = analysis_results["present_skills"]
                missing_skills = analysis_results["missing_skills"]
                
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
                    else:
                        st.write("Not enough standard skills to generate radar chart.")
                
                st.markdown("---")
                col3, col4 = st.columns(2)
                with col3:
                    st.subheader("✅ Identified Skills")
                    if present_skills:
                        skills_html = "".join([f'<span class="skill-tag present-skill">{skill.title()}</span>' for skill in present_skills])
                        st.markdown(skills_html, unsafe_allow_html=True)
                with col4:
                    st.subheader("⚠️ Missing Skills")
                    if missing_skills:
                        skills_html = "".join([f'<span class="skill-tag missing-skill">{skill.title()}</span>' for skill in missing_skills])
                        st.markdown(skills_html, unsafe_allow_html=True)

        # --- TAB 2: Custom JD Match ---
        with tab2:
            st.header("Match against a specific Job Description")
            custom_jd = st.text_area("Paste the exact Job Description here:", height=200)
            
            if st.button("Analyze Custom JD"):
                if not custom_jd.strip():
                    st.warning("Please paste a job description first.")
                else:
                    with st.spinner("Analyzing Custom JD..."):
                        jd_results = analyze_custom_jd(clean_resume, custom_jd)
                        st.metric("JD Match Score", f"{jd_results['ats_score']}%")
                        
                        colA, colB = st.columns(2)
                        with colA:
                            st.markdown("**Matched Critical Keywords**")
                            st.write(", ".join(jd_results['present_skills']) if jd_results['present_skills'] else "None found")
                        with colB:
                            st.markdown("**Missing Critical Keywords**")
                            st.write(", ".join(jd_results['missing_skills']) if jd_results['missing_skills'] else "None missing")

        # --- TAB 3: Health & Structure ---
        with tab3:
            st.header("Resume Health Check")
            structure = evaluate_structure(raw_text)
            
            colX, colY = st.columns(2)
            with colX:
                st.subheader("Section Detection")
                st.write("**Found Sections:**", ", ".join(structure["found_sections"]) if structure["found_sections"] else "None identified")
                if structure["missing_sections"]:
                    st.error(f"**Missing Critical Sections:** {', '.join(structure['missing_sections'])}")
                else:
                    st.success("All critical sections found!")
            
            with colY:
                st.subheader("Text Density")
                st.metric("Word Count", structure["word_count"])
                if "Too" in structure["length_feedback"]:
                    st.warning(structure["length_feedback"])
                else:
                    st.success(structure["length_feedback"])

            st.markdown("---")
            st.subheader("Action Verb Analysis")
            st.write("ATS systems highly rank resumes that use strong action verbs ('Architected') over weak ones ('Helped').")
            verbs = analyze_action_verbs(clean_resume)
            
            if verbs["strong_verbs"]:
                st.markdown("**Great Action Verbs Found:** " + "".join([f'<span class="skill-tag strong-verb">{v}</span>' for v in set(verbs["strong_verbs"])]), unsafe_allow_html=True)
            if verbs["weak_verbs"]:
                st.markdown("**Weak Verbs Detected (Consider Replacing):** " + "".join([f'<span class="skill-tag weak-verb">{v}</span>' for v in set(verbs["weak_verbs"])]), unsafe_allow_html=True)

        # --- TAB 4: AI Rewriter ---
        with tab4:
            st.header("Generative AI Bullet Rewriter")
            st.write("Paste a weak bullet point from your resume, and let the Gemini AI rewrite it into a strong, impactful statement.")
            
            bullet_point = st.text_area("Your Bullet Point:", placeholder="e.g., I helped fix bugs in the database.", height=100)
            
            if st.button("Rewrite Bullet 🪄"):
                if not api_key_input:
                    st.error("Please enter your Gemini API Key in the sidebar first!")
                elif not bullet_point:
                    st.warning("Please enter a bullet point to rewrite.")
                else:
                    with st.spinner("Thinking..."):
                        response = rewrite_bullet_points(bullet_point, api_key_input)
                        if "error" in response:
                            st.error(response["error"])
                        else:
                            st.success("Rewritten Bullet Point:")
                            st.markdown(f"**{response['result']}**")
                            st.info("Remember to adjust any specific numbers/metrics to be historically accurate.")

if __name__ == '__main__':
    main()
