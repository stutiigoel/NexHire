import re
from pathlib import Path
from io import BytesIO
import fitz
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SKILLS = ["python", "java", "javascript", "sql", "excel", "power bi", "tableau", "machine learning", "deep learning", "nlp", "natural language processing", "data analysis", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "react", "html", "css", "git", "docker", "aws", "azure", "linux", "testing", "automation", "selenium", "communication", "project management", "fastapi", "flask", "streamlit", "statistics", "c++", "node.js"]

def extract_skills(text):
    normalized = text.lower()
    return sorted([s for s in SKILLS if re.search(r'(?<!\w)' + re.escape(s) + r'(?!\w)', normalized)])

def parse_resume(upload):
    data = upload.getvalue()
    if len(data) > 5 * 1024 * 1024:
        raise ValueError("Maximum resume size is 5 MB")
    ext = Path(upload.name).suffix.lower()
    if ext == '.pdf':
        with fitz.open(stream=data, filetype='pdf') as doc:
            if len(doc) > 20:
                raise ValueError('Maximum 20 PDF pages')
            text = '\n'.join(page.get_text() for page in doc)
    elif ext == '.docx':
        text = '\n'.join(p.text for p in Document(BytesIO(data)).paragraphs)
    else:
        raise ValueError('Upload a PDF or DOCX file')
    if not text.strip():
        raise ValueError('No extractable text found. Scanned PDFs are not supported in this version.')
    return text

def rank_jobs(resume, jobs):
    if not jobs:
        return []
    descriptions = [j['description'] + ' ' + j['skills'] for j in jobs]
    vectors = TfidfVectorizer(stop_words='english', ngram_range=(1, 2)).fit_transform([resume] + descriptions)
    similarities = cosine_similarity(vectors[0:1], vectors[1:]).ravel()
    resume_skills = set(extract_skills(resume))
    ranked = []
    for job, similarity in zip(jobs, similarities):
        required = set(extract_skills(job['skills']))
        matched = sorted(required & resume_skills)
        missing = sorted(required - resume_skills)
        coverage = len(matched) / len(required) if required else 0
        score = round(100 * (0.6 * float(similarity) + 0.4 * coverage), 1)
        ranked.append({**job, 'score': score, 'similarity': round(float(similarity), 3), 'matched': matched, 'missing': missing})
    return sorted(ranked, key=lambda j: j['score'], reverse=True)

def answer_question(question, ranked, resume_skills):
    q = question.lower()
    if not ranked:
        return 'Please upload your resume and run job matching first.'
    top = ranked[0]
    if any(x in q for x in ['best', 'suitable', 'recommend', 'match', 'job']):
        return 'Your highest-ranked role is **{}** at **{}** (match score: {}%). This is a text-based estimate, not a hiring probability. {}'.format(top['title'], top['company'], top['score'], 'Matched skills: ' + ', '.join(top['matched']) if top['matched'] else 'No listed required skills were detected in the resume.')
    if any(x in q for x in ['missing', 'gap', 'learn', 'improve', 'skill']):
        return 'For **{}**, missing skills detected from the resume: **{}**. Verify these against the job description; a missing mention does not prove you lack the skill.'.format(top['title'], ', '.join(top['missing']) if top['missing'] else 'none of the listed skills')
    if any(x in q for x in ['have', 'know', 'my skills']):
        return 'Skills detected in your resume: ' + (', '.join(resume_skills) if resume_skills else 'none from the current skill dictionary')
    if any(x in q for x in ['why', 'reason', 'score']):
        return 'The score combines TF-IDF text similarity (60%) and explicitly listed required-skill coverage (40%). For **{}**, text similarity is {} and matched skills are {}.'.format(top['title'], top['similarity'], ', '.join(top['matched']) or 'none')
    return 'I can explain your best job match, match score, detected skills, or skill gaps. Try asking: “Why is my top job recommended?”'
