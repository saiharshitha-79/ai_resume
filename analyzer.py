from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from job_roles import JOB_ROLES

def get_best_role_match(clean_resume_text):
    """
    Uses TF-IDF Vectorization and Cosine Similarity to find the best matching
    job role based on the resume content.
    """
    role_names = list(JOB_ROLES.keys())
    # Create a string of target keywords for each role to act as the "document" to match against
    role_docs = [" ".join(JOB_ROLES[role]) for role in role_names]
    
    # Add the resume as the last document
    documents = role_docs + [clean_resume_text]
    
    # Vectorize
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)
    
    # Calculate cosine similarity between the resume (last element) and the roles
    cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    
    # Get the index of the highest similarity score
    best_match_idx = cosine_sim[0].argmax()
    best_score = cosine_sim[0][best_match_idx]
    
    # If the score is very low, it might not match any role perfectly
    if best_score < 0.05:
        return "General/Undetermined", 0.0
        
    return role_names[best_match_idx], best_score

def analyze_resume_for_role(clean_resume_text, target_role):
    """
    Analyzes the resume specifically against the chosen target_role.
    Calculates an ATS score based on keyword matching, and identifies
    present and missing skills.
    """
    if target_role not in JOB_ROLES:
        return {"error": "Role not found in configuration."}
        
    target_skills = JOB_ROLES[target_role]
    
    # Normalize skills for exact matching
    target_skills_lower = [skill.lower() for skill in target_skills]
    
    present_skills = []
    missing_skills = []
    
    # Simple word matching - checking if skill keyword exists in text
    # (In a production system, we'd use SpaCy or Regex for n-gram exact bounds)
    for skill in target_skills_lower:
        if f"{skill}" in clean_resume_text:
            present_skills.append(skill)
        else:
            missing_skills.append(skill)
            
    # Calculate ATS Score (Percentage of keywords found)
    score_percentage = (len(present_skills) / len(target_skills)) * 100
    
    return {
        "ats_score": round(score_percentage, 1),
        "present_skills": present_skills,
        "missing_skills": missing_skills
    }

def generate_suggestions(missing_skills, ats_score):
    """
    Generates actionable improvement suggestions based on the ATS score
    and missing skills.
    """
    suggestions = []
    
    if ats_score < 50:
        suggestions.append("Your ATS score is low. You need to heavily tailor your resume to the job description.")
        suggestions.append("Consider adding a 'Projects' section to showcase practical experience with missing tools.")
    elif ats_score < 80:
        suggestions.append("Your resume is good, but missing a few key skills. Try to incorporate them naturally.")
    else:
        suggestions.append("Great resume! Ensure your experience descriptions highlight the impact of your skills with metrics (e.g., 'Improved efficiency by 20%').")
        
    if len(missing_skills) > 0:
        suggestions.append(f"Consider learning or emphasizing these skills: {', '.join(missing_skills[:3])}.")
        
    suggestions.append("Make sure your resume format is standard (no complex tables or graphics) so ATS bots can parse it perfectly.")
    
    return suggestions
