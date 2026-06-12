"""
Email Generator — AI-powered cold email generation, reply classification, and auto-reply drafting.
Uses Groq (Llama 3.3 70B) — free tier, no region restrictions.
"""
import json
import re
from groq import Groq


def _ask_groq(api_key: str, prompt: str, temperature: float = 0.5, max_tokens: int = 1000) -> str:
    """Helper to call Groq and return the raw text response."""
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_completion_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


def _parse_json(text: str) -> dict:
    """Clean markdown fences and parse JSON."""
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
    return json.loads(text)


def guess_hr_email(company_name: str, api_key: str) -> str:
    """Uses AI to find the domain of the company and guess the HR email."""
    prompt = (
        f"Find the official website domain for the company '{company_name}'.\n"
        "Then, return the most likely email address for job applications, HR, "
        "or general contact (e.g., hr@domain.com, careers@domain.com, info@domain.com).\n"
        "Return ONLY the email address string and nothing else."
    )
    try:
        email = _ask_groq(api_key, prompt, temperature=0.2)
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', email)
        if match:
            return match.group(0).lower()
        return f"careers@{company_name.lower().replace(' ', '')}.com"
    except Exception:
        return f"careers@{company_name.lower().replace(' ', '')}.com"


def discover_companies(resume_analysis: dict, api_key: str, batch: int = 1) -> list[dict]:
    """Uses AI to suggest target companies. Calls in batches to get 40-50 total."""
    roles = ", ".join(resume_analysis.get("target_roles", []))
    skills = ", ".join(resume_analysis.get("skills", [])[:10])

    batch_prompts = {
        1: f"""Suggest 15 REAL tech companies (mix of MNCs and well-funded startups) that would hire freshers with these skills.
Include companies like FAANG, product companies, and Series A-D startups.
Target Roles: {roles}
Top Skills: {skills}

Return ONLY a JSON list: [{{"company": "Name", "reason": "Why they fit", "type": "MNC/Startup/Mid-size"}}]""",

        2: f"""Suggest 15 REAL Indian startups and companies that actively hire freshers and interns.
Include YC-backed startups, Bangalore/Delhi/Mumbai tech startups, D2C brands with tech teams, and fintech companies.
Do NOT repeat: Google, Microsoft, Amazon, Meta, Apple, Netflix.
Target Roles: {roles}
Top Skills: {skills}

Return ONLY a JSON list: [{{"company": "Name", "reason": "Why they fit", "type": "Startup/Scale-up"}}]""",

        3: f"""Suggest 15 REAL companies (global remote-friendly companies, open source companies, and lesser-known but great places to work) that hire freshers.
Include companies from Europe, Southeast Asia, and remote-first companies.
Do NOT repeat any well-known FAANG companies.
Target Roles: {roles}
Top Skills: {skills}

Return ONLY a JSON list: [{{"company": "Name", "reason": "Why they fit", "type": "Remote/Global"}}]""",
    }

    prompt = batch_prompts.get(batch, batch_prompts[1])

    try:
        text = _ask_groq(api_key, prompt, temperature=0.7, max_tokens=2000)
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
        return json.loads(text)
    except Exception:
        return [
            {"company": "Razorpay", "reason": "Growing fintech, hires freshers.", "type": "Startup"},
            {"company": "Zerodha", "reason": "Tech-first brokerage.", "type": "Startup"},
            {"company": "Postman", "reason": "API tools company, strong engineering.", "type": "Scale-up"},
        ]


def generate_cold_email(
    resume_analysis: dict,
    company: str,
    role: str,
    contact_name: str,
    api_key: str,
    job_description: str = "",
) -> dict:
    """
    Generate a personalized cold email for a company/role based on resume analysis using the user's custom prompt.
    Returns dict with 'subject' and 'body'.
    """
    candidate_name = resume_analysis.get("full_name", "Candidate")
    skills = ", ".join(resume_analysis.get("skills", [])[:10])
    summary = resume_analysis.get("summary", "")
    
    education = resume_analysis.get("education", [])
    college = education[0].get("institution", "University") if education else "University"
    degree = education[0].get("degree", "Degree") if education else "Degree"
    
    projects_list = resume_analysis.get("projects", [])
    projects_str = "\n".join([f"- {p.get('name', '')}: {p.get('description', '')}" for p in projects_list[:2]])
    
    exp_list = resume_analysis.get("experience", [])
    achievements_str = "\n".join([f"- {e.get('title', '')} at {e.get('company', '')}" for e in exp_list[:2]])

    prompt = f"""ROLE:
You are an elite internship outreach specialist.

YOUR GOAL:
Generate cold emails that sound like they were written by a real student, not by AI.

CRITICAL RULES:

1. NEVER use these phrases:
* I hope this email finds you well
* I am writing to express my interest
* innovation
* cutting-edge
* passionate
* excited
* thrilled
* customer-centric
* world-class
* industry-leading
* pushing boundaries
* transformative

2. NEVER praise a company without evidence.
BAD: "I admire Google's innovation."
GOOD: "I recently explored TensorFlow's ecosystem and found it interesting how it simplifies deploying ML models."

3. Every email MUST contain:
* Candidate introduction
* Why this company specifically
* 1-2 relevant projects
* Direct value proposition
* Resume mention
* GitHub link
* LinkedIn link
* Contact information

4. PERSONALIZATION REQUIREMENT:
Use company information provided.
Reference: Product, Engineering blog, Open-source project, Recent feature, Recent funding, Recent launch, Technology stack.
Do not make up facts.

5. PROJECT SECTION:
Instead of listing projects:
BAD: "I built a fraud detection system."
GOOD: "I built a machine-learning-based credit card fraud detection system and a Python network security monitor capable of identifying MITM attacks in real time."

6. TONE: Professional, Confident, Curious, Concise, Human. Do NOT sound desperate.

7. LENGTH: 120-180 words.

INPUTS:
* Candidate Name: {candidate_name}
* College: {college}
* Degree: {degree}
* CGPA: {resume_analysis.get('cgpa', '8.1')}
* Skills: {skills}
* Projects: {projects_str}
* Achievements: {achievements_str}
* Resume Summary: {summary}
* Company Name: {company}
* Company Description: (Use your knowledge of {company})
* Industry: Technology/Software
* Hiring Role: {role}
* Recruiter/Founder Name: {contact_name or 'Hiring Manager'}
* Email: {resume_analysis.get('email', 'N/A')}
* Phone: {resume_analysis.get('phone', 'N/A')}
* GitHub: {resume_analysis.get('github', 'github.com/ayush')}
* LinkedIn: {resume_analysis.get('linkedin', 'linkedin.com/in/ayush')}

8. OUTPUT FORMAT:
Subject: <subject>

Email:
Hi <name>,

<personalized opening>

<candidate introduction>

<relevant projects and skills>

<why candidate can contribute>

<call to action>

Best regards,

{candidate_name}
{degree}
{college}
CGPA: {resume_analysis.get('cgpa', '8.1')}

GitHub: {resume_analysis.get('github', 'github.com/ayush')}
LinkedIn: {resume_analysis.get('linkedin', 'linkedin.com/in/ayush')}
Email: {resume_analysis.get('email', 'N/A')}
Phone: {resume_analysis.get('phone', 'N/A')}

Resume Attached

9. QUALITY CHECK BEFORE RETURNING:
Reject and rewrite the email if:
* It contains generic praise.
* It contains buzzwords.
* It could be sent to any company without changing the text.
* The company name appears only once.
* GitHub or LinkedIn is missing.
* Projects are merely listed without explaining what they do.

Generate only the email and subject line. Do not include explanations, notes, or markdown."""

    try:
        text = _ask_groq(api_key, prompt, temperature=0.6)
        
        # Parse the custom text format robustly
        lines = text.strip().split('\n')
        subject = f"Application for {role} at {company}"
        body_lines = []
        
        for line in lines:
            if line.lower().startswith("subject:"):
                subject = line[8:].strip()
            elif line.strip() == "Email:":
                pass # skip the literal word "Email:" if they included it as a header
            else:
                body_lines.append(line)
                    
        # Remove leading empty lines
        while body_lines and not body_lines[0].strip():
            body_lines.pop(0)
            
        body = "\n".join(body_lines).strip()
        
        return {"subject": subject, "body": body}
    except Exception as e:
        return {
            "subject": f"Application for {role} at {company}",
            "body": f"Hi Team,\n\nI am interested in the {role} position. Please find my resume attached.\n\nBest,\n{candidate_name}\n\n[DEBUG ERROR: {str(e)}]"
        }


def classify_reply(reply_body: str, api_key: str) -> str:
    """Classify an email reply as: Positive, Neutral, or Rejection."""
    prompt = f"""Classify this email reply to a job application cold email.
Return ONLY one word: "Positive", "Neutral", or "Rejection"

- Positive: They want to schedule a call, interview, or learn more
- Neutral: Auto-reply, acknowledgment, "we'll get back to you", forwarded to HR
- Rejection: Not hiring, position filled, not a fit, no openings

Email reply:
{reply_body}
"""
    try:
        result = _ask_groq(api_key, prompt, temperature=0.1).strip('"').strip("'")
        if result in ("Positive", "Neutral", "Rejection"):
            return result
        return "Neutral"
    except Exception:
        return "Neutral"


def generate_auto_reply(
    original_email_subject: str,
    original_email_body: str,
    reply_body: str,
    classification: str,
    resume_analysis: dict,
    api_key: str,
) -> dict:
    """Generate an appropriate reply based on the classification of the incoming email."""
    candidate_name = resume_analysis.get("full_name", "the candidate")

    if classification == "Rejection":
        prompt = f"""Write a brief, graceful reply to a job rejection email.
- Thank them for their time
- Express interest in future opportunities
- Keep it under 50 words
- Be professional and positive

Their reply: {reply_body}

Return ONLY a JSON object: {{"subject": "Re: ...", "body": "reply text"}}
"""
    elif classification == "Positive":
        prompt = f"""Write a reply to a positive response from a hiring manager who wants to schedule a call/interview.
- Express enthusiasm
- Offer flexible availability (next week, any day)
- Be specific and professional
- Keep it under 80 words

Their reply: {reply_body}
Candidate name: {candidate_name}

Return ONLY a JSON object: {{"subject": "Re: ...", "body": "reply text"}}
"""
    else:  # Neutral
        prompt = f"""Write a brief, professional follow-up reply to an acknowledgment email.
- Thank them for the acknowledgment
- Reiterate your interest briefly
- Keep it under 50 words

Their reply: {reply_body}
Candidate name: {candidate_name}

Return ONLY a JSON object: {{"subject": "Re: ...", "body": "reply text"}}
"""

    try:
        text = _ask_groq(api_key, prompt, temperature=0.5)
        result = _parse_json(text)
        result["subject"] = f"Re: {original_email_subject}"
        return result
    except Exception:
        return {
            "subject": f"Re: {original_email_subject}",
            "body": (
                f"Thank you for your response. I appreciate your time and "
                f"look forward to hearing more.\n\nBest regards,\n{candidate_name}"
            ),
        }


def generate_follow_up(
    original_subject: str,
    original_body: str,
    company: str,
    days_since: int,
    resume_analysis: dict,
    api_key: str,
) -> dict:
    """Generate a follow-up email if no reply after N days."""
    candidate_name = resume_analysis.get("full_name", "the candidate")

    prompt = f"""Write a brief follow-up email for a cold outreach that got no reply.
- Reference the original email
- Add one new piece of value (a new achievement, article, or insight about the company)
- Keep it under 80 words
- Don't be pushy

Original subject: {original_subject}
Company: {company}
Days since sent: {days_since}
Candidate: {candidate_name}

Return ONLY a JSON object: {{"subject": "Re: ...", "body": "follow-up text"}}
"""

    try:
        text = _ask_groq(api_key, prompt, temperature=0.5)
        return _parse_json(text)
    except Exception:
        return {
            "subject": f"Re: {original_subject}",
            "body": (
                f"Hi,\n\nJust following up on my previous email about opportunities "
                f"at {company}. I remain very interested and would love to connect.\n\n"
                f"Best,\n{candidate_name}"
            ),
        }
