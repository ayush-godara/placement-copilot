"""
Placement Copilot AI — Cold Email Automation Tool
Premium UI with real cold emailing, auto-reply, and multi-platform job discovery.
"""
import streamlit as st
import json
import bcrypt
from datetime import datetime

from utils.database import (
    create_user, get_user_by_email, get_user_by_id, update_user,
    save_sent_email, get_sent_emails, save_reply, get_replies, update_reply,
    save_job, get_jobs, skip_company, get_skipped_companies,
)
from utils.gmail_service import send_email, fetch_replies, test_connection
from utils.resume_parser import extract_text_from_pdf, analyze_resume
from utils.email_generator import (
    generate_cold_email, classify_reply, generate_auto_reply, generate_follow_up,
    guess_hr_email, discover_companies,
)
from utils.job_scraper import scrape_all_platforms

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Page Config
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.set_page_config(
    page_title="Placement Copilot AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Premium CSS ───────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

:root {
    --bg-primary: #050507;
    --bg-card: rgba(255,255,255,0.03);
    --bg-card-hover: rgba(255,255,255,0.06);
    --border: rgba(255,255,255,0.06);
    --border-hover: rgba(139,92,246,0.3);
    --text-primary: #f0f0f5;
    --text-secondary: #8b8b9e;
    --text-muted: #55556a;
    --accent: #8b5cf6;
    --accent-glow: rgba(139,92,246,0.15);
    --success: #22c55e;
    --warning: #eab308;
    --danger: #ef4444;
    --info: #3b82f6;
}

.stApp {
    background: var(--bg-primary);
    font-family: 'Inter', -apple-system, sans-serif;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0a0f 0%, #0d0d15 100%);
    border-right: 1px solid var(--border);
}

section[data-testid="stSidebar"] .stRadio > label { display: none; }
section[data-testid="stSidebar"] .stRadio > div {
    display: flex; flex-direction: column; gap: 4px;
}
section[data-testid="stSidebar"] .stRadio > div > label {
    padding: 10px 16px; border-radius: 10px; cursor: pointer;
    transition: all 0.2s; font-size: 0.9rem; color: var(--text-secondary);
    border: 1px solid transparent;
}
section[data-testid="stSidebar"] .stRadio > div > label:hover {
    background: var(--bg-card-hover); color: var(--text-primary);
    border-color: var(--border);
}
section[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"],
section[data-testid="stSidebar"] .stRadio > div [aria-checked="true"] {
    background: var(--accent-glow) !important;
    border-color: var(--border-hover) !important;
    color: var(--text-primary) !important;
}

/* Hero Headers */
.hero-title {
    font-size: 2.5rem; font-weight: 800; letter-spacing: -0.03em;
    background: linear-gradient(135deg, #c084fc 0%, #818cf8 30%, #60a5fa 60%, #34d399 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin-bottom: 0; line-height: 1.1;
}
.hero-sub {
    font-size: 1rem; color: var(--text-muted); margin-top: 6px;
    margin-bottom: 2rem; font-weight: 400;
}

/* Glass Cards */
.glass-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px; padding: 24px;
    backdrop-filter: blur(12px);
    transition: all 0.3s ease;
}
.glass-card:hover {
    border-color: var(--border-hover);
    background: var(--bg-card-hover);
    box-shadow: 0 0 40px rgba(139,92,246,0.05);
}

/* Stat Cards */
.stat-card {
    background: linear-gradient(135deg, rgba(139,92,246,0.08) 0%, rgba(59,130,246,0.05) 100%);
    border: 1px solid rgba(139,92,246,0.12);
    border-radius: 16px; padding: 28px 24px; text-align: center;
    position: relative; overflow: hidden;
}
.stat-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, #8b5cf6, transparent);
}
.stat-value {
    font-size: 2.5rem; font-weight: 800; color: var(--text-primary);
    letter-spacing: -0.02em; line-height: 1;
}
.stat-label {
    font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;
    letter-spacing: 0.1em; margin-top: 8px; font-weight: 600;
}

/* Company Cards */
.company-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px; padding: 20px;
    transition: all 0.3s ease; margin-bottom: 10px;
    display: flex; align-items: center; gap: 16px;
}
.company-card:hover {
    border-color: var(--border-hover);
    transform: translateY(-1px);
    box-shadow: 0 8px 32px rgba(139,92,246,0.08);
}
.company-avatar {
    width: 44px; height: 44px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; font-weight: 500; font-family: 'Inter', sans-serif;
    color: #f3f4f6; background: #1f2937; border: 1px solid #374151;
    flex-shrink: 0; box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}
.stipend-badge {
    display: inline-flex; align-items: center; gap: 4px;
    color: #10b981; font-weight: 500; font-size: 0.78rem; margin-top: 4px;
}
.company-info { flex: 1; min-width: 0; }
.company-name { font-size: 0.95rem; font-weight: 600; color: var(--text-primary); }
.company-detail { font-size: 0.78rem; color: var(--text-secondary); margin-top: 2px; }
.company-email { font-size: 0.75rem; color: var(--accent); margin-top: 4px; }
.company-tag {
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: 0.68rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.05em;
}
.tag-startup { background: rgba(234,179,8,0.12); color: #eab308; }
.tag-mnc { background: rgba(59,130,246,0.12); color: #60a5fa; }
.tag-remote { background: rgba(34,197,94,0.12); color: #22c55e; }
.tag-scaleup { background: rgba(244,114,182,0.12); color: #f472b6; }

/* Email Cards */
.email-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 14px; padding: 20px; margin-bottom: 10px;
    transition: all 0.2s;
}
.email-card:hover { border-color: var(--border-hover); }
.email-header { display: flex; justify-content: space-between; align-items: center; }
.email-company { font-weight: 600; color: var(--text-primary); font-size: 0.95rem; }
.email-to { color: var(--text-muted); font-size: 0.8rem; margin-left: 8px; }
.email-subject { color: var(--text-secondary); font-size: 0.85rem; margin-top: 6px; }
.email-date { color: var(--text-muted); font-size: 0.72rem; margin-top: 4px; }

/* Status Badges */
.badge { padding: 4px 12px; border-radius: 20px; font-size: 0.72rem; font-weight: 600; }
.badge-positive { background: rgba(34,197,94,0.12); color: #22c55e; }
.badge-neutral { background: rgba(234,179,8,0.12); color: #eab308; }
.badge-rejection { background: rgba(239,68,68,0.12); color: #ef4444; }
.badge-waiting { background: rgba(139,92,246,0.12); color: #a78bfa; }

/* Skill Tags */
.skill-tag {
    display: inline-block; background: rgba(139,92,246,0.1);
    border: 1px solid rgba(139,92,246,0.15); color: #c4b5fd;
    padding: 4px 12px; border-radius: 8px; font-size: 0.75rem;
    margin: 3px; font-weight: 500;
}

/* Progress Bar */
.progress-container {
    background: rgba(255,255,255,0.03); border-radius: 8px;
    height: 6px; overflow: hidden; margin-top: 10px;
}
.progress-bar {
    height: 100%; border-radius: 8px;
    background: linear-gradient(90deg, #8b5cf6, #3b82f6);
    transition: width 0.5s ease;
}

/* Section Divider */
.section-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 2rem 0;
}

/* Form Styling */
div[data-testid="stForm"] {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 16px; padding: 24px;
}

/* Animations */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
.animate-in { animation: fadeInUp 0.5s ease forwards; }
</style>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Auth Helpers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def check_password(pw: str, hashed: str) -> bool:
    return bcrypt.checkpw(pw.encode(), hashed.encode())

def get_current_user() -> dict | None:
    uid = st.session_state.get("user_id")
    return get_user_by_id(uid) if uid else None

def require_auth():
    if not st.session_state.get("user_id"):
        st.warning("Please log in first.")
        st.stop()

def _company_avatar(name: str):
    """Generate a sleek, minimalist professional avatar initial."""
    letter = name[0].upper() if name else "?"
    return f'<div class="company-avatar">{letter}</div>'


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AUTH PAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def render_auth_page():
    st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1.2, 2, 1.2])
    with col2:
        st.markdown('<div class="hero-title" style="text-align:center">🚀 Placement Copilot AI</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-sub" style="text-align:center">Your AI-powered job hunting machine. Cold emails that get replies.</div>', unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Create Account"])

        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Sign In", use_container_width=True)
                if submitted:
                    if not email or not password:
                        st.error("Please fill in all fields.")
                    else:
                        user = get_user_by_email(email)
                        if user and check_password(password, user["password_hash"]):
                            st.session_state["user_id"] = user["id"]
                            st.rerun()
                        else:
                            st.error("Invalid email or password.")

        with tab2:
            with st.form("register_form"):
                name = st.text_input("Full Name", placeholder="Ayush Godara")
                reg_email = st.text_input("Email", placeholder="you@example.com", key="reg_email")
                reg_pass = st.text_input("Password", type="password", key="reg_pass")
                confirm = st.text_input("Confirm Password", type="password")
                submitted = st.form_submit_button("Create Account", use_container_width=True)
                if submitted:
                    if not all([name, reg_email, reg_pass, confirm]):
                        st.error("Please fill in all fields.")
                    elif reg_pass != confirm:
                        st.error("Passwords don't match.")
                    elif get_user_by_email(reg_email):
                        st.error("Email already registered.")
                    else:
                        uid = create_user(reg_email, hash_password(reg_pass), name)
                        st.session_state["user_id"] = uid
                        st.rerun()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SETUP PAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def render_setup_page():
    require_auth()
    user = get_current_user()

    col_title, col_logout = st.columns([3, 1])
    with col_title:
        st.markdown('<div style="display:flex;align-items:center;gap:16px;margin-bottom:0;"><span style="font-size:2.5rem;line-height:1.1;">⚙️</span><div class="hero-title">Setup & Settings</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-sub">Connect your tools — takes 2 minutes</div>', unsafe_allow_html=True)
    with col_logout:
        if st.button("🚪 Logout from Copilot", use_container_width=True, type="secondary"):
            st.session_state.clear()
            st.session_state["explicitly_logged_out"] = True
            st.rerun()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("#### 📧 Gmail Configuration")
        st.info(
            "**How to get a Gmail App Password:**\n"
            "1. Go to [Google Account](https://myaccount.google.com/)\n"
            "2. Security → 2-Step Verification (enable it)\n"
            "3. Search **App passwords** at the top\n"
            "4. Create one for 'Mail' → Copy the 16-char password"
        )
        with st.form("gmail_form"):
            gmail = st.text_input("Gmail Address", value=user.get("gmail_email", "") or "", placeholder="you@gmail.com")
            app_pass = st.text_input("App Password", type="password", value=user.get("gmail_app_password", "") or "", placeholder="xxxx xxxx xxxx xxxx")
            save_gmail = st.form_submit_button("💾 Save & Test Connection", use_container_width=True)
            if save_gmail:
                if gmail and app_pass:
                    with st.spinner("Testing connection..."):
                        if test_connection(gmail, app_pass):
                            update_user(user["id"], gmail_email=gmail, gmail_app_password=app_pass)
                            st.success("✅ Gmail connected!")
                            st.rerun()
                        else:
                            st.error("❌ Connection failed. Check credentials.")
                else:
                    st.error("Both fields are required.")

    with col2:
        st.markdown("#### 🤖 Groq API Key (Free)")
        st.info("Get your **free** key from **[console.groq.com/keys](https://console.groq.com/keys)** — no credit card needed!")
        with st.form("api_form"):
            api_key = st.text_input("Groq API Key", type="password", value=user.get("gemini_api_key", "") or "", placeholder="gsk_...")
            save_api = st.form_submit_button("💾 Save API Key", use_container_width=True)
            if save_api and api_key:
                update_user(user["id"], gemini_api_key=api_key)
                st.success("✅ API key saved!")
                st.rerun()

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # Resume Upload
    st.markdown("#### 📄 Resume Upload & AI Analysis")
    if user.get("resume_analysis"):
        analysis = json.loads(user["resume_analysis"])
        score = analysis.get("ats_score", 0)

        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"""
            <div class="glass-card">
                <div style="display:flex;align-items:center;justify-content:space-between">
                    <div>
                        <div style="font-size:1.1rem;font-weight:700;color:var(--text-primary)">
                            {analysis.get('full_name', 'Resume')}
                        </div>
                        <div style="color:var(--text-secondary);font-size:0.85rem;margin-top:4px">
                            {analysis.get('summary', '')[:120]}...
                        </div>
                    </div>
                    <div style="text-align:center">
                        <div style="font-size:2rem;font-weight:800;color:{'var(--success)' if score >= 70 else 'var(--warning)'}">{score}</div>
                        <div style="font-size:0.65rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.1em">ATS Score</div>
                    </div>
                </div>
                <div class="progress-container" style="margin-top:16px">
                    <div class="progress-bar" style="width:{score}%"></div>
                </div>
                <div style="margin-top:16px">
                    {"".join(f'<span class="skill-tag">{s}</span>' for s in analysis.get("skills", [])[:12])}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            if st.button("🔄 Re-upload", use_container_width=True):
                update_user(user["id"], resume_text="", resume_analysis="")
                st.rerun()
    else:
        uploaded = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
        if uploaded:
            if not user.get("gemini_api_key"):
                st.error("Please set your Groq API key first.")
            else:
                with st.spinner("🔍 AI is analyzing your resume..."):
                    raw = extract_text_from_pdf(uploaded.getvalue())
                    analysis = analyze_resume(raw, user["gemini_api_key"])
                    if "error" not in analysis or analysis.get("ats_score", 0) > 0:
                        update_user(user["id"], resume_text=raw, resume_analysis=json.dumps(analysis), resume_pdf=uploaded.getvalue())
                        st.success("✅ Resume analyzed and saved!")
                        st.rerun()
                    else:
                        st.error(f"Analysis failed: {analysis.get('error', 'Unknown error')}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DASHBOARD PAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def render_dashboard():
    require_auth()
    user = get_current_user()

    st.markdown('<div style="display:flex;align-items:center;gap:16px;margin-bottom:0;"><span style="font-size:2.5rem;line-height:1.1;">📊</span><div class="hero-title">Dashboard</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-sub">Welcome back, {user["full_name"]} 👋</div>', unsafe_allow_html=True)

    setup_ok = all([user.get("gmail_email"), user.get("gemini_api_key"), user.get("resume_analysis")])
    if not setup_ok:
        st.markdown("""
        <div class="glass-card" style="border-color:rgba(234,179,8,0.2);background:rgba(234,179,8,0.04)">
            <div style="font-size:1.1rem;font-weight:600;color:#eab308">⚠️ Setup Incomplete</div>
            <div style="color:var(--text-secondary);margin-top:6px">
                Head to <strong>⚙️ Setup</strong> to connect Gmail, add your API key, and upload your resume.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    emails = get_sent_emails(user["id"])
    replies_list = get_replies(user["id"])
    total_sent = len(emails)
    total_replies = len(replies_list)
    positive = sum(1 for r in replies_list if r.get("classification") == "Positive")
    rate = f"{(total_replies / total_sent * 100):.0f}%" if total_sent > 0 else "—"

    if "dashboard_tab" not in st.session_state:
        st.session_state["dashboard_tab"] = "Activity"

    c1, c2, c3, c4 = st.columns(4, gap="medium")
    for col, val, label in [(c1, str(total_sent), "EMAILS SENT"), (c2, str(total_replies), "REPLIES"), (c3, rate, "RESPONSE RATE"), (c4, str(positive), "POSITIVE")]:
        with col:
            st.markdown(f'<div class="stat-card" style="margin-bottom:8px"><div class="stat-value">{val}</div><div class="stat-label">{label}</div></div>', unsafe_allow_html=True)
            if st.button(f"View {label.title()}", use_container_width=True, key=f"btn_{label}"):
                st.session_state["dashboard_tab"] = label
                st.rerun()

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    tab = st.session_state["dashboard_tab"]

    if tab == "RESPONSE RATE":
        st.markdown("#### 📊 Response Rate Breakdown")
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-size:1.1rem;font-weight:600;margin-bottom:12px;color:var(--text-primary)">Let's break down your numbers:</div>
            <div style="color:var(--text-secondary);margin-bottom:8px">You have successfully sent <strong style="color:white">{total_sent}</strong> cold emails.</div>
            <div style="color:var(--text-secondary);margin-bottom:16px">You have received <strong style="color:white">{total_replies}</strong> replies from HRs or automated systems.</div>
            <hr style="border-color:var(--border);margin-bottom:16px;">
            <div style="font-size:1.5rem;color:#60a5fa;font-weight:700;">Overall Response Rate: {rate}</div>
        </div>
        """, unsafe_allow_html=True)

    elif tab in ["REPLIES", "POSITIVE"]:
        st.markdown(f"#### {'💬 Received Replies' if tab == 'REPLIES' else '🎉 Positive Replies'}")
        filtered_replies = replies_list if tab == "REPLIES" else [r for r in replies_list if r.get("classification") == "Positive"]
        if not filtered_replies:
            st.markdown("""
            <div class="glass-card" style="text-align:center;padding:48px">
                <div style="font-size:2.5rem;margin-bottom:12px">📭</div>
                <div style="color:var(--text-secondary)">No replies found for this filter.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for i, reply in enumerate(filtered_replies):
                cl = reply.get("classification", "Neutral")
                badge_class = f"badge-{cl.lower()}" if cl in ("Positive", "Neutral", "Rejection") else "badge-neutral"
                st.markdown(f"""
                <div class="email-card" style="margin-bottom: 0; border-bottom-left-radius: 0; border-bottom-right-radius: 0;">
                    <div class="email-header">
                        <div style="display:flex;align-items:center;gap:12px">
                            {_company_avatar(reply.get('company', reply['from_email']))}
                            <div>
                                <div class="email-company">{reply.get('company', 'Company')}</div>
                                <div class="email-to">from {reply['from_email']}</div>
                            </div>
                        </div>
                        <span class="badge {badge_class}">{cl}</span>
                    </div>
                    <div class="email-subject">{reply['subject']}</div>
                </div>
                """, unsafe_allow_html=True)
                with st.expander("👀 View Full Reply Content"):
                    st.text_area("Reply Body", value=reply['body'], height=200, key=f"dash_view_reply_{reply['id']}", disabled=True)
                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    else:
        st.markdown(f"#### {'📤 Sent Emails' if tab == 'EMAILS SENT' else '📬 Recent Activity'}")
        if not emails:
            st.markdown("""
            <div class="glass-card" style="text-align:center;padding:48px">
                <div style="font-size:2.5rem;margin-bottom:12px">📭</div>
                <div style="color:var(--text-secondary)">No emails sent yet. Head to <strong>Cold Emailer</strong> to start hunting!</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for i, em in enumerate(emails):
                badge_class = "badge-waiting"
                badge_text = "Awaiting"
                for r in replies_list:
                    if r.get("sent_email_id") == em["id"]:
                        cl = r.get("classification", "Neutral")
                        badge_text = cl
                        badge_class = f"badge-{cl.lower()}"
                        break
                st.markdown(f"""
                <div class="email-card" style="margin-bottom: 0; border-bottom-left-radius: 0; border-bottom-right-radius: 0;">
                    <div class="email-header">
                        <div style="display:flex;align-items:center;gap:12px">
                            {_company_avatar(em['company'])}
                            <div>
                                <div class="email-company">{em['company']}</div>
                                <div class="email-to">→ {em['to_email']}</div>
                            </div>
                        </div>
                        <span class="badge {badge_class}">{badge_text}</span>
                    </div>
                    <div class="email-subject">{em['subject']}</div>
                    <div class="email-date">{em.get('sent_at', '')[:16]}</div>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("👀 View Sent Email Content"):
                    st.text_area("Body", value=em['body'], height=150, key=f"view_body_{em['id']}", disabled=True)
                
                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COLD EMAILER PAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def render_cold_emailer():
    require_auth()
    user = get_current_user()

    st.markdown('<div style="display:flex;align-items:center;gap:16px;margin-bottom:0;"><span style="font-size:2.5rem;line-height:1.1;">📧</span><div class="hero-title">Cold Emailer</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">AI finds companies, writes emails, you just hit send</div>', unsafe_allow_html=True)

    if not all([user.get("gmail_email"), user.get("gemini_api_key"), user.get("resume_analysis")]):
        st.warning("⚠️ Complete your setup first.")
        return

    resume_analysis = json.loads(user["resume_analysis"])

    tab1, tab2, tab3 = st.tabs(["🤖 Auto-Pilot", "🔍 Job Board Search", "✍️ Manual Entry"])

    # ── AUTO-PILOT TAB ────────────────────────────────────
    with tab1:

        st.markdown("""
        <div class="glass-card" style="margin-bottom:20px">
            <div style="font-size:1.1rem;font-weight:700;color:var(--text-primary)">🚀 Fully Automatic Mode</div>
            <div style="color:var(--text-secondary);margin-top:6px;font-size:0.88rem">
                AI analyzes your resume, discovers <strong>45+ companies</strong> (MNCs, Indian startups, remote companies),
                finds their HR emails, and lets you send personalized cold emails — all in one click.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Discover 45+ Target Companies", use_container_width=True, type="primary"):
            all_companies = []
            progress = st.progress(0, text="🔍 Discovering MNCs & product companies...")

            for batch_num in range(1, 4):
                labels = {1: "🏢 MNCs & product companies", 2: "🚀 Indian startups & scale-ups", 3: "🌍 Remote & global companies"}
                progress.progress(int((batch_num - 1) / 3 * 60), text=f"🔍 Discovering {labels[batch_num]}...")
                batch = discover_companies(resume_analysis, user["gemini_api_key"], batch=batch_num)
                all_companies.extend(batch)

            sent_emails = get_sent_emails(user["id"])
            sent_companies = {em["company"].lower() for em in sent_emails}
            skipped_companies = set(get_skipped_companies(user["id"]))
            
            filtered_new_companies = []
            for c in all_companies:
                if c["company"].lower() not in sent_companies and c["company"].lower() not in skipped_companies:
                    filtered_new_companies.append(c)
            
            all_companies = filtered_new_companies

            progress.progress(65, text="📧 Finding HR emails for all companies...")
            for i, c in enumerate(all_companies):
                pct = 65 + int(i / max(len(all_companies), 1) * 30)
                progress.progress(min(pct, 95), text=f"📧 Finding email for {c['company']}...")
                c["email"] = guess_hr_email(c["company"], user["gemini_api_key"])

            progress.progress(100, text="✅ Done!")
            st.session_state["discovered_companies"] = all_companies
            st.rerun()

        if "discovered_companies" in st.session_state:
            companies = st.session_state["discovered_companies"]
            st.markdown(f"<div style='color:var(--text-secondary);margin-bottom:16px'>Found <strong style=\"color:var(--accent)\">{len(companies)}</strong> companies matching your profile</div>", unsafe_allow_html=True)

            types_found = list(set(c.get("type", "Other") for c in companies))
            filter_type = st.radio("Filter by", ["All"] + types_found, horizontal=True, label_visibility="collapsed")
            filtered = companies if filter_type == "All" else [c for c in companies if c.get("type") == filter_type]

            for idx, c in enumerate(filtered):
                ctype = c.get("type", "Other").lower().replace("/", "-").replace(" ", "-")
                tag_class = "tag-startup" if "startup" in ctype else ("tag-mnc" if "mnc" in ctype else ("tag-remote" if "remote" in ctype or "global" in ctype else "tag-scaleup"))

                col_info, col_btn = st.columns([4, 1])
                with col_info:
                    st.markdown(f"""
                    <div class="company-card">
                        {_company_avatar(c['company'])}
                        <div class="company-info">
                            <div class="company-name">{c['company']}</div>
                            <div class="company-detail">{c.get('reason', '')}</div>
                            <div class="company-email">📧 {c.get('email', 'Finding...')}</div>
                        </div>
                        <span class="company-tag {tag_class}">{c.get('type', 'Other')}</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col_btn:
                    st.write("")
                    if st.button("Draft", key=f"draft_{idx}", use_container_width=True):
                        with st.spinner(f"Writing email for {c['company']}..."):
                            role = resume_analysis.get("target_roles", ["Software Engineer"])[0]
                            result = generate_cold_email(resume_analysis, c["company"], role, "", user["gemini_api_key"])
                        st.session_state["draft_email"] = result
                        st.session_state["draft_meta"] = {"to_email": c["email"], "company": c["company"], "role": role, "contact_name": ""}
                        st.rerun()
                        
                    if st.button("Skip", key=f"skip_{idx}", use_container_width=True, type="secondary"):
                        skip_company(user["id"], c["company"])
                        st.session_state["discovered_companies"] = [x for x in st.session_state["discovered_companies"] if x["company"] != c["company"]]
                        st.rerun()

                if st.session_state.get("draft_meta", {}).get("company") == c["company"]:
                    _render_draft_review(user, resume_analysis, f"auto_{idx}_")

    # ── JOB BOARD SEARCH TAB ──────────────────────────────
    with tab2:

        st.markdown("""
        <div class="glass-card" style="margin-bottom:16px">
            <div style="font-size:1rem;font-weight:600;color:var(--text-primary)">🔍 Multi-Platform Search</div>
            <div style="color:var(--text-secondary);font-size:0.85rem;margin-top:4px">
                Searches <strong>Internshala + Naukri</strong> simultaneously for fresher-friendly positions.
            </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            search_q = st.text_input("Search Role", value=", ".join(resume_analysis.get("target_roles", ["software developer"])[:1]))
        with c2:
            search_loc = st.text_input("Location", placeholder="Delhi, Remote...")
        with c3:
            search_type = st.radio("Search Type", ["Jobs", "Internships"])

        if st.button("🔍 Search All Platforms", use_container_width=True, type="primary"):
            is_internship = (search_type == "Internships")
            with st.spinner("Searching Internshala, Naukri & LinkedIn..."):
                jobs = scrape_all_platforms(search_q, search_loc, is_internship)
                
                # Filter out skipped companies
                skipped_companies = set(get_skipped_companies(user["id"]))
                jobs = [j for j in jobs if j["company"].lower() not in skipped_companies]
                
                if jobs:
                    for j in jobs:
                        save_job(j["title"], j["company"], j["location"], j["url"], j.get("description", ""), j.get("source", ""))
                    st.success(f"Found **{len(jobs)}** listings across all platforms!")
                else:
                    st.warning("No results. Try a different search.")

        stored_jobs = get_jobs()
        if stored_jobs:
            skipped_companies = set(get_skipped_companies(user["id"]))
            stored_jobs = [j for j in stored_jobs if j["company"].lower() not in skipped_companies]

        if stored_jobs:
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            for i, job in enumerate(stored_jobs[:20]):
                col_j, col_b = st.columns([4, 1])
                with col_j:
                    desc_html = f'<div class="stipend-badge"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg> {job["description"]}</div>' if job.get('description') else ''
                    st.markdown(f"""
                    <div class="company-card">
                        {_company_avatar(job['company'])}
                        <div class="company-info">
                            <div class="company-name">{job['title']}</div>
                            <div class="company-detail">{job['company']} • 📍 {job['location']}</div>{desc_html}
                        </div>
                        <span class="company-tag tag-scaleup">{job.get('source', '')}</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col_b:
                    st.write("")
                    if st.button("Email", key=f"job_{job['id']}", use_container_width=True):
                        with st.spinner("Finding email..."):
                            found_email = guess_hr_email(job["company"], user["gemini_api_key"])
                        with st.spinner("Drafting email..."):
                            result = generate_cold_email(resume_analysis, job["company"], job["title"], "", user["gemini_api_key"])
                        st.session_state["draft_email"] = result
                        st.session_state["draft_meta"] = {"to_email": found_email, "company": job["company"], "role": job["title"], "contact_name": ""}
                        st.rerun()
                        
                    if st.button("Skip", key=f"skip_job_{job['id']}", use_container_width=True, type="secondary"):
                        skip_company(user["id"], job["company"])
                        st.rerun()

                if st.session_state.get("draft_meta", {}).get("company") == job["company"]:
                    _render_draft_review(user, resume_analysis, f"job_{job['id']}_")

    # ── MANUAL ENTRY TAB ──────────────────────────────────
    with tab3:
        with st.form("manual_email_form"):
            c1, c2 = st.columns(2)
            with c1:
                company = st.text_input("Company Name", placeholder="Google")
                role = st.text_input("Role", placeholder="Software Engineer")
            with c2:
                contact_name = st.text_input("Contact Name", placeholder="(optional)")
                email_val = st.session_state.get("guessed_email", "")
                to_email = st.text_input("Email", value=email_val, placeholder="hr@company.com")
                auto_find = st.form_submit_button("🪄 Auto-Find Email")
            job_desc = st.text_area("Job Description (optional)", height=100)
            generate_btn = st.form_submit_button("🤖 Generate Email", use_container_width=True)

        if auto_find and company:
            with st.spinner(f"Finding email for {company}..."):
                guessed = guess_hr_email(company, user["gemini_api_key"])
                st.session_state["guessed_email"] = guessed
                st.rerun()

        if generate_btn and company and to_email:
            with st.spinner("🤖 Crafting your email..."):
                result = generate_cold_email(resume_analysis, company, role, contact_name, user["gemini_api_key"], job_desc)
            st.session_state["draft_email"] = result
            st.session_state["draft_meta"] = {"to_email": to_email, "company": company, "role": role, "contact_name": contact_name}

        _render_draft_review(user, resume_analysis, "manual_")

def _render_draft_review(user, resume_analysis, key_prefix=""):
    """Premium inline draft review card — appears right where the user is."""
    if "draft_email" not in st.session_state:
        return

    draft = st.session_state["draft_email"]
    meta = st.session_state["draft_meta"]

    if "draft_version" not in st.session_state:
        st.session_state["draft_version"] = 0
        
    version = st.session_state["draft_version"]

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(139,92,246,0.06) 0%, rgba(59,130,246,0.04) 100%);
        border: 1px solid rgba(139,92,246,0.2);
        border-radius: 20px; padding: 28px; margin-bottom: 24px;
        box-shadow: 0 0 60px rgba(139,92,246,0.06);
    ">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px">
            <div style="
                width:40px;height:40px;border-radius:10px;
                background:linear-gradient(135deg,#8b5cf6,#6366f1);
                display:flex;align-items:center;justify-content:center;
                font-size:1.1rem;color:white;font-weight:700;
            ">{meta['company'][0]}</div>
            <div>
                <div style="font-size:1.05rem;font-weight:700;color:#e0e0f0">✉️ Draft for {meta['company']}</div>
            </div>
        </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    edited_to = st.text_input("To (Edit to send a test to yourself)", value=meta["to_email"], key=f"{key_prefix}draft_to_{version}")
    edited_subject = st.text_input("Subject", value=draft["subject"], key=f"{key_prefix}draft_subject_{version}")
    edited_body = st.text_area("Email Body", value=draft["body"], height=200, key=f"{key_prefix}draft_body_{version}")

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        if st.button("✅  Send Email Now", key=f"{key_prefix}send_btn", use_container_width=True, type="primary"):
            with st.spinner("Sending via Gmail..."):
                try:
                    msg_id = send_email(
                        user["gmail_email"], 
                        user["gmail_app_password"], 
                        edited_to, 
                        edited_subject, 
                        edited_body, 
                        user["full_name"],
                        attachment_bytes=user.get("resume_pdf")
                    )
                    save_sent_email(user["id"], edited_to, meta.get("contact_name", ""), meta["company"], meta.get("role", ""), edited_subject, edited_body, msg_id or "")
                    
                    if "discovered_companies" in st.session_state:
                        st.session_state["discovered_companies"] = [
                            c for c in st.session_state["discovered_companies"] 
                            if c.get("company") != meta["company"]
                        ]
                        
                    del st.session_state["draft_email"]
                    del st.session_state["draft_meta"]
                    st.success("✅ Email sent successfully!")
                    st.balloons()
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
    with c2:
        if st.button("🔄 Rewrite", key=f"{key_prefix}rewrite_btn", use_container_width=True):
            with st.spinner("AI is rewriting..."):
                result = generate_cold_email(resume_analysis, meta["company"], meta.get("role", ""), meta.get("contact_name", ""), user["gemini_api_key"])
            st.session_state["draft_email"] = result
            st.session_state["draft_version"] += 1
            st.rerun()
    with c3:
        if st.button("✕ Discard", key=f"{key_prefix}discard_btn", use_container_width=True):
            del st.session_state["draft_email"]
            del st.session_state["draft_meta"]
            st.rerun()

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AUTO-REPLY PAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def render_auto_reply():
    require_auth()
    user = get_current_user()

    st.markdown('<div style="display:flex;align-items:center;gap:16px;margin-bottom:0;"><span style="font-size:2.5rem;line-height:1.1;">💬</span><div class="hero-title">Auto-Reply Inbox</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">AI reads replies, classifies them, and drafts smart responses</div>', unsafe_allow_html=True)

    if not all([user.get("gmail_email"), user.get("gemini_api_key"), user.get("resume_analysis")]):
        st.warning("⚠️ Complete your setup first.")
        return

    resume_analysis = json.loads(user["resume_analysis"])

    if st.button("🔄 Check for New Replies", use_container_width=True, type="primary"):
        sent_emails = get_sent_emails(user["id"])
        if not sent_emails:
            st.info("No emails sent yet.")
        else:
            subjects = [e["subject"] for e in sent_emails]
            with st.spinner("Checking Gmail inbox..."):
                try:
                    new_replies = fetch_replies(user["gmail_email"], user["gmail_app_password"], subjects, since_days=14)
                    if not new_replies:
                        st.info("No new replies found.")
                    else:
                        added = 0
                        for reply in new_replies:
                            matching = [e for e in sent_emails if e["subject"].lower() == reply["original_subject"].lower()]
                            if not matching:
                                continue
                            sent_em = matching[0]
                            existing = get_replies(user["id"])
                            if any(r["from_email"] == reply["from_email"] and r["subject"] == reply["subject"] for r in existing):
                                continue
                            classification = classify_reply(reply["body"], user["gemini_api_key"])
                            save_reply(sent_em["id"], reply["from_email"], reply["subject"], reply["body"], classification)
                            added += 1
                        if added > 0:
                            st.success(f"Found {added} new replies!")
                            st.rerun()
                        else:
                            st.info("No new replies.")
                except ValueError as e:
                    st.error(str(e))

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    all_replies = get_replies(user["id"])
    if not all_replies:
        st.markdown("""
        <div class="glass-card" style="text-align:center;padding:48px">
            <div style="font-size:2.5rem;margin-bottom:12px">📭</div>
            <div style="color:var(--text-secondary)">No replies yet. Send some cold emails first!</div>
        </div>
        """, unsafe_allow_html=True)
        return

    for i, reply in enumerate(all_replies):
        cl = reply.get("classification", "Neutral")
        badge_class = f"badge-{cl.lower()}" if cl in ("Positive", "Neutral", "Rejection") else "badge-neutral"

        st.markdown(f"""
        <div class="email-card" style="margin-bottom: 0; border-bottom-left-radius: 0; border-bottom-right-radius: 0;">
            <div class="email-header">
                <div style="display:flex;align-items:center;gap:12px">
                    {_company_avatar(reply.get('company', reply['from_email']))}
                    <div>
                        <div class="email-company">{reply.get('company', 'Company')}</div>
                        <div class="email-to">from {reply['from_email']}</div>
                    </div>
                </div>
                <span class="badge {badge_class}">{cl}</span>
            </div>
            <div class="email-subject">{reply['subject']}</div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("👀 View Full Reply Content"):
            st.text_area("Reply Body", value=reply['body'], height=200, key=f"view_reply_{reply['id']}", disabled=True)
            
            import urllib.parse
            if reply.get("gmail_message_id"):
                gmail_link = f"https://mail.google.com/mail/u/0/#all/{urllib.parse.quote(reply['gmail_message_id'])}"
            else:
                gmail_link = f"https://mail.google.com/mail/u/0/#search/from%3A{urllib.parse.quote(reply['from_email'])}"
            st.markdown(f"**[🔗 Open this thread in Gmail]({gmail_link})**")
                
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        if not reply.get("auto_reply_sent"):
            if st.button(f"🤖 Draft & Send Auto-Reply", key=f"auto_{reply['id']}", use_container_width=True):
                sent_emails = get_sent_emails(user["id"])
                matching = [e for e in sent_emails if e["id"] == reply["sent_email_id"]]
                if matching:
                    sent_em = matching[0]
                    with st.spinner("Drafting reply..."):
                        auto = generate_auto_reply(sent_em["subject"], sent_em["body"], reply["body"], cl, resume_analysis, user["gemini_api_key"])
                    st.text_area("Reply", value=auto["body"], height=120, key=f"body_{reply['id']}")
                    if st.button("✅ Send Reply", key=f"send_{reply['id']}", type="primary"):
                        try:
                            send_email(user["gmail_email"], user["gmail_app_password"], reply["from_email"], auto["subject"], auto["body"], user["full_name"])
                            update_reply(reply["id"], auto_reply_sent=1, auto_reply_draft=auto["body"])
                            st.success("✅ Reply sent!")
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))
        else:
            st.caption("✅ Auto-reply already sent")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN APP ROUTING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    if not st.session_state.get("user_id"):
        if not st.session_state.get("explicitly_logged_out"):
            # Auto-login if there is exactly one user registered (ideal for local single-user apps)
            from utils.database import get_connection
            conn = get_connection()
            users = conn.execute("SELECT id FROM users LIMIT 2").fetchall()
            conn.close()
            
            if len(users) == 1:
                st.session_state["user_id"] = users[0][0]
                st.rerun()
                return
                
        render_auth_page()
        return

    user = get_current_user()
    if not user:
        st.session_state.clear()
        st.rerun()
        return

    # Global positive reply notifications
    if "notified_replies" not in st.session_state:
        st.session_state["notified_replies"] = set()
        
    all_reps = get_replies(user["id"])
    for r in all_reps:
        if r.get("classification") == "Positive" and r["id"] not in st.session_state["notified_replies"]:
            company_name = r.get("company", r["from_email"])
            st.toast(f"🎉 Great news! You got a POSITIVE reply from **{company_name}**!", icon="🎉")
            st.session_state["notified_replies"].add(r["id"])

    # Top Navigation (No Sidebar Needed)
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#e5e7eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
            <polyline points="2 17 12 22 22 17"></polyline>
            <polyline points="2 12 12 17 22 12"></polyline>
        </svg>
        <div style="font-size:1.4rem;font-weight:700;color:#f3f4f6;letter-spacing:-0.03em;">
            Placement Copilot
        </div>
    </div>
    <style>
        /* Force segmented control to stretch full width and look like professional tabs */
        div[data-testid="stSegmentedControl"] > div {
            width: 100%;
            display: flex;
        }
        div[data-testid="stSegmentedControl"] label {
            flex: 1;
            justify-content: center;
        }
    </style>
    """, unsafe_allow_html=True)

    if "nav_page" not in st.session_state:
        st.session_state["nav_page"] = "Dashboard"

    page = st.segmented_control("Nav", ["Dashboard", "Setup", "Cold Emailer", "Auto-Reply"], label_visibility="collapsed", key="nav_page", selection_mode="single")
    if not page:
        page = "Dashboard"
    
    st.markdown('<div class="section-divider" style="margin:16px 0 32px 0"></div>', unsafe_allow_html=True)

    if page == "Dashboard":
        render_dashboard()
    elif page == "Setup":
        render_setup_page()
    elif page == "Cold Emailer":
        render_cold_emailer()
    elif page == "Auto-Reply":
        render_auto_reply()


if __name__ == "__main__":
    main()
