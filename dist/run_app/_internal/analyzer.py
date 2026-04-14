import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from job_roles import JOB_ROLES

def get_best_role_match(clean_resume_text):
    role_names = list(JOB_ROLES.keys())
    role_docs = [" ".join(JOB_ROLES[role]) for role in role_names]
    documents = role_docs + [clean_resume_text]
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)
    cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    
    best_match_idx = cosine_sim[0].argmax()
    best_score = cosine_sim[0][best_match_idx]
    
    if best_score < 0.05:
        return "General/Undetermined", 0.0
    return role_names[best_match_idx], best_score

def analyze_resume_for_role(clean_resume_text, target_role):
    if target_role not in JOB_ROLES:
        return {"error": "Role not found in configuration."}
        
    target_skills = JOB_ROLES[target_role]
    target_skills_lower = [skill.lower() for skill in target_skills]
    
    present_skills = []
    missing_skills = []
    for skill in target_skills_lower:
        if f"{skill}" in clean_resume_text:
            present_skills.append(skill)
        else:
            missing_skills.append(skill)
            
    score_percentage = (len(present_skills) / len(target_skills)) * 100
    return {
        "ats_score": round(score_percentage, 1),
        "present_skills": present_skills,
        "missing_skills": missing_skills
    }

def analyze_custom_jd(clean_resume_text, custom_jd):
    """
    Analyzes resume against a custom job description using TF-IDF cosine similarity.
    Extracts high-value words from the JD and checks presence.
    """
    documents = [custom_jd, clean_resume_text]
    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform(documents)
        cosine_sim = cosine_similarity(tfidf_matrix[1], tfidf_matrix[0])[0][0]
    except ValueError:
        cosine_sim = 0.0
        
    # Extract top keywords from JD
    feature_names = vectorizer.get_feature_names_out()
    jd_vector = tfidf_matrix[0].toarray()[0]
    jd_keyword_scores = pd.Series(jd_vector, index=feature_names).sort_values(ascending=False)
    # Taking top 20 keywords
    top_jd_keywords = jd_keyword_scores.head(20).index.tolist()
    
    present_keywords = [kw for kw in top_jd_keywords if kw in clean_resume_text]
    missing_keywords = [kw for kw in top_jd_keywords if kw not in clean_resume_text]
    
    # Calculate score based on actual similarity
    score_percentage = min(100.0, cosine_sim * 100 * 2) # Multiplier for typical TF-IDF ranges
    
    return {
        "ats_score": round(score_percentage, 1),
        "present_skills": present_keywords,
        "missing_skills": missing_keywords
    }

def evaluate_structure(raw_text):
    """
    Detects if major sections are present and checks word count limits.
    """
    results = {}
    word_count = len(raw_text.split())
    results["word_count"] = word_count
    
    if word_count < 200:
        results["length_feedback"] = "Too Short (Consider expanding on your experiences)"
    elif word_count > 1000:
        results["length_feedback"] = "Too Long (Consider trimming to 1-2 pages)"
    else:
        results["length_feedback"] = "Optimal Length"
        
    sections_to_check = ["experience", "education", "skills"]
    found_sections = []
    missing_sections = []
    
    text_lower = raw_text.lower()
    for sec in sections_to_check:
        if sec in text_lower:
            found_sections.append(sec.title())
        else:
            missing_sections.append(sec.title())
            
    results["found_sections"] = found_sections
    results["missing_sections"] = missing_sections
    return results

def analyze_action_verbs(clean_text):
    """
    Scans for weak verbs versus strong action verbs.
    """
    weak_verbs = ["helped", "worked on", "responsible for", "assisted", "was tasked with", "did", "made"]
    strong_verbs = [
        "architected", "spearheaded", "optimized", "developed", "managed", "led",
        "engineered", "streamlined", "implemented", "designed", "orchestrated",
        "accelerated", "maximized", "transformed"
    ]
    
    found_weak = [verb for verb in weak_verbs if verb in clean_text]
    found_strong = [verb for verb in strong_verbs if verb in clean_text]
    
    return {
        "weak_verbs": found_weak,
        "strong_verbs": found_strong
    }

def generate_suggestions(missing_skills, ats_score):
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

def generate_radar_chart_data(present_skills, target_role="Auto"):
    """
    Groups matched skills into categories for Plotly radar charts.
    """
    categories = {"Backend": 0, "Frontend": 0, "Data": 0, "Cloud/Ops": 0, "Management": 0}
    
    mapping = {
        "python": "Backend", "java": "Backend", "c++": "Backend", "node.js": "Backend", "go": "Backend",
        "html": "Frontend", "css": "Frontend", "javascript": "Frontend", "react": "Frontend", "vue": "Frontend",
        "sql": "Data", "machine learning": "Data", "pandas": "Data", "statistics": "Data", "deep learning": "Data",
        "docker": "Cloud/Ops", "kubernetes": "Cloud/Ops", "aws": "Cloud/Ops", "ci/cd": "Cloud/Ops", "linux": "Cloud/Ops",
        "agile": "Management", "scrum": "Management", "jira": "Management", "product strategy": "Management"
    }
    
    for skill in present_skills:
        cat = mapping.get(skill)
        if cat:
            categories[cat] += 1
            
    # Scale to 0-5
    for cat in categories:
        categories[cat] = min(5, categories[cat])
        
    # Return formatted dataframe
    import pandas as pd
    df = pd.DataFrame(dict(
        r=list(categories.values()),
        theta=list(categories.keys())
    ))
    return df
