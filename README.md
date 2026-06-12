<h1 align="center">
  🚀 Placement Copilot AI
</h1>

<p align="center">
  <strong>An autonomous AI agent that automates the entire placement and cold-emailing lifecycle for software engineers.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenAI_/_Groq-412991?style=for-the-badge&logo=openai&logoColor=white" />
</p>

---

## 🌟 Overview

**Placement Copilot** is a full-stack, autonomous career-hunting engine. Instead of manually applying to hundreds of jobs, this application acts as an AI assistant that **reads your resume**, automatically **scrapes job boards** (LinkedIn, Internshala, Naukri) to find companies that match your profile, and **autonomously drafts and sends hyper-personalized cold emails** to recruiters.

It doesn't stop there. When recruiters reply, the Copilot reads their inbox responses, classifies their sentiment (Positive, Neutral, Rejection), and even drafts AI-generated follow-up replies for you.

## ✨ Key Features

- **📄 AI Resume Analysis**: Upload your PDF resume, and the system uses LLMs to extract your core skills, experience, and calculate an ATS score.
- **🕸️ Autonomous Job Scraping**: Multi-platform scraping engine built with `BeautifulSoup` that hunts for exact-match jobs and internships across LinkedIn, Naukri, and Internshala.
- **🎯 Dynamic HR Targeting**: Leverages Groq/Gemini to algorithmically guess the exact email structures of HR managers and recruiters at target companies.
- **📧 Cold Email Automation**: Connects directly to Gmail via SMTP/IMAP. Drafts hyper-personalized emails highlighting exactly why your resume fits their specific job description.
- **🧠 Inbox Sentiment Analysis**: Automatically reads replies from recruiters, classifies them into `Positive`, `Neutral`, or `Rejection`, and immediately alerts you of positive leads.
- **💬 Smart Auto-Replies**: Generates context-aware follow-up emails to recruiter replies based on the conversation history.

## 🏗️ Architecture & Tech Stack

- **Frontend**: Streamlit (with highly customized CSS for a modern, glass-morphic UI).
- **Backend**: Python 3.10+
- **Database**: Supabase (PostgreSQL) via `supabase-py` SDK for permanent cloud storage.
- **AI Models**: Groq API / Google Gemini for high-speed resume parsing, email drafting, and sentiment classification.
- **Web Scraping**: `BeautifulSoup4` and `requests` for robust DOM parsing.

## 🚀 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/placement-copilot.git
   cd placement-copilot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Supabase & Secrets**
   Create a `.streamlit/secrets.toml` file in the root directory:
   ```toml
   SUPABASE_URL = "your-supabase-url"
   SUPABASE_KEY = "your-supabase-anon-key"
   ```

4. **Run the App**
   ```bash
   streamlit run app.py
   ```

## 📸 Screenshots
*(Coming soon: Add your dashboard screenshots here!)*

---
<div align="center">
  Built with ❤️ for engineers tired of manual job applications.
</div>
