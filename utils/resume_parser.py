"""
Resume Parser — Extract text from PDF and analyze with Groq AI (free tier).
Uses Llama 3.3 70B via Groq's ultra-fast inference.
"""
import json
from groq import Groq
from pypdf import PdfReader
import io


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract raw text from a PDF file."""
    reader = PdfReader(io.BytesIO(file_bytes))
    text_parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            text_parts.append(text)
    return "\n".join(text_parts)


def analyze_resume(resume_text: str, api_key: str) -> dict:
    """
    Use Groq (Llama 3.3 70B) to analyze a resume and extract structured information.
    Returns a dict with skills, experience, education, strengths, weaknesses, etc.
    """
    client = Groq(api_key=api_key)

    prompt = f"""You are an expert career advisor and resume analyzer.
Analyze the following resume text and return a JSON object with these exact keys:

{{
    "full_name": "candidate's full name",
    "email": "candidate's email if found",
    "phone": "candidate's phone if found",
    "skills": ["skill1", "skill2", ...],
    "experience": [
        {{"title": "Job Title", "company": "Company Name", "duration": "Duration", "highlights": ["highlight1"]}}
    ],
    "education": [
        {{"degree": "Degree", "institution": "University", "year": "Year"}}
    ],
    "projects": [
        {{"name": "Project Name", "description": "Brief description", "tech": ["tech1"]}}
    ],
    "strengths": ["strength1", "strength2", ...],
    "weaknesses": ["area to improve 1", ...],
    "missing_skills": ["trending skill they should learn", ...],
    "ats_score": 75,
    "summary": "A 2-3 sentence professional summary of this candidate",
    "target_roles": ["role1", "role2", ...]
}}

IMPORTANT: Return ONLY valid JSON. No markdown, no code blocks, just the JSON object.

Resume Text:
{resume_text}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_completion_tokens=2000,
        )
        text = response.choices[0].message.content.strip()
        # Clean up potential markdown code blocks
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "error": "Failed to parse AI response",
            "raw_response": text if 'text' in dir() else "No response",
            "skills": [],
            "strengths": [],
            "weaknesses": [],
            "summary": "Analysis failed - please retry",
            "ats_score": 0,
        }
    except Exception as e:
        return {
            "error": str(e),
            "skills": [],
            "strengths": [],
            "weaknesses": [],
            "summary": "Analysis failed - please retry",
            "ats_score": 0,
        }
