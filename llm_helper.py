import google.generativeai as genai

def rewrite_bullet_points(text, api_key):
    """
    Uses the Google Gemini API to rewrite poorly worded resume bullet points
    into strong, quantifiable, ATS-optimized action statements.
    """
    if not api_key:
        return {"error": "API key is required to use this feature."}

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = (
            "You are an expert technical resume writer. Your task is to rewrite the "
            "following resume bullet point into a strong, quantifiable, ATS-optimized "
            "action statement. Use strong action verbs and emphasize impact. "
            "Return ONLY the rewritten bullet point, without any filler text or 'Sure'.\n\n"
            f"Original Bullet Point:\n{text}"
        )
        
        response = model.generate_content(prompt)
        return {"result": response.text.strip()}
    except Exception as e:
        return {"error": f"An error occurred while calling the AI: {str(e)}"}

def generate_cover_letter(resume_text, job_description, api_key):
    """Generates a tailored cover letter from the resume targeting the JD."""
    if not api_key:
        return {"error": "API key is required."}
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (
            "You are a professional career coach. Write a highly tailored, compelling, "
            "and professional 3-paragraph Cover Letter. Use the details from the candidate's "
            f"resume:\n\n{resume_text}\n\n"
            f"Address the Cover Letter targeting this exact Job Description:\n\n{job_description}\n\n"
            "Do not include brackets like [Your Name], use realistic placeholders if necessary, "
            "but mostly focus on creating a powerful narrative matching the resume to the JD."
        )
        response = model.generate_content(prompt)
        return {"result": response.text.strip()}
    except Exception as e:
        return {"error": str(e)}

def generate_interview_questions(missing_skills, role, api_key):
    """Generates tough interview questions targeting the candidate's missing skills."""
    if not api_key:
        return {"error": "API key is required."}
    if not missing_skills:
        return {"result": "You have all the required skills! Standard behavioral preparation is recommended."}
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        skills_str = ", ".join(missing_skills)
        prompt = (
            f"A candidate is interviewing for a {role} position. Their resume "
            f"appears to be missing or weak in these critical skills: {skills_str}. "
            "As an expert technical recruiter, generate the Top 3 toughest interview questions "
            "you would ask to test them on these missing areas. For each question, provide a short "
            "'How to answer if you lack direct experience' tip."
        )
        response = model.generate_content(prompt)
        return {"result": response.text.strip()}
    except Exception as e:
        return {"error": str(e)}
