import os
import re
from collections import Counter
import PyPDF2
# import docx  # Uncomment if python-docx is installed and needed

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'txt'}

def extract_text_from_pdf(filepath):
    text = ""
    with open(filepath, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_file(filepath):
    ext = filepath.rsplit('.', 1)[1].lower()
    if ext == 'pdf':
        return extract_text_from_pdf(filepath)
    elif ext == 'txt':
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    # elif ext == 'docx':
    #     doc = docx.Document(filepath)
    #     return "\n".join([para.text for para in doc.paragraphs])
    return ""

def calculate_match_score(resume_text, job_description):
    if not resume_text or not job_description:
        return 0
    
    # Normalize text
    resume_words = set(re.findall(r'\w+', resume_text.lower()))
    job_words = re.findall(r'\w+', job_description.lower())
    
    if not job_words:
        return 0
        
    # Simple keyword matching
    # Filter out common stop words if needed, for now just match all
    # A better approach: match only significant words or skills
    # For this "Major Project", we'll do a simple intersection count / total meaningful job words
    
    # Let's count significant matches
    # We can use a set for job words to avoid double counting same keyword if present multiple times?
    # Or maybe frequency matters. Let's stick to set intersection for "coverage"
    
    job_unique = set(job_words)
    common_words = resume_words.intersection(job_unique)
    
    score = (len(common_words) / len(job_unique)) * 100
    
    return int(score) if score <= 100 else 100
