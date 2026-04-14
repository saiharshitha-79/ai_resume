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
        model = genai.GenerativeModel('gemini-pro')
        
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
