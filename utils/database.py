import streamlit as st
from supabase import create_client, Client
import uuid
from typing import Optional

@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def init_db():
    # In Supabase, the schema is managed via the SQL Editor online.
    # We do not run CREATE TABLE scripts from the client SDK.
    pass

# ── User CRUD ─────────────────────────────────────────────

def create_user(email: str, password_hash: str, full_name: str) -> str:
    uid = str(uuid.uuid4())
    data = {
        "id": uid,
        "email": email,
        "password_hash": password_hash,
        "full_name": full_name
    }
    get_supabase().table("users").insert(data).execute()
    return uid

def get_user_by_email(email: str) -> Optional[dict]:
    response = get_supabase().table("users").select("*").eq("email", email).execute()
    return response.data[0] if response.data else None

def get_user_by_id(user_id: str) -> Optional[dict]:
    response = get_supabase().table("users").select("*").eq("id", user_id).execute()
    return response.data[0] if response.data else None

def update_user(user_id: str, **fields):
    get_supabase().table("users").update(fields).eq("id", user_id).execute()

# ── Sent Emails ───────────────────────────────────────────

def save_sent_email(user_id: str, to_email: str, to_name: str, company: str,
                    role: str, subject: str, body: str, message_id: str = "") -> str:
    eid = str(uuid.uuid4())
    data = {
        "id": eid,
        "user_id": user_id,
        "to_email": to_email,
        "to_name": to_name,
        "company": company,
        "role": role,
        "subject": subject,
        "body": body,
        "gmail_message_id": message_id
    }
    get_supabase().table("sent_emails").insert(data).execute()
    return eid

def get_sent_emails(user_id: str) -> list[dict]:
    response = get_supabase().table("sent_emails").select("*").eq("user_id", user_id).order("sent_at", desc=True).execute()
    return response.data

def get_email_by_message_id(message_id: str) -> Optional[dict]:
    response = get_supabase().table("sent_emails").select("*").eq("gmail_message_id", message_id).execute()
    return response.data[0] if response.data else None

# ── Email Replies ─────────────────────────────────────────

def save_reply(sent_email_id: str, from_email: str, subject: str, body: str, classification: str) -> str:
    rid = str(uuid.uuid4())
    data = {
        "id": rid,
        "sent_email_id": sent_email_id,
        "from_email": from_email,
        "subject": subject,
        "body": body,
        "classification": classification
    }
    get_supabase().table("email_replies").insert(data).execute()
    return rid

def get_replies(user_id: str) -> list[dict]:
    # 1. Fetch all sent emails for this user to get their IDs
    emails_response = get_supabase().table("sent_emails").select("id, company, to_email").eq("user_id", user_id).execute()
    emails = emails_response.data
    if not emails:
        return []
        
    email_dict = {e["id"]: e for e in emails}
    email_ids = list(email_dict.keys())
    
    # 2. Fetch all replies that map to these sent_email_ids
    replies = []
    chunk_size = 100
    for i in range(0, len(email_ids), chunk_size):
        chunk = email_ids[i:i+chunk_size]
        resp = get_supabase().table("email_replies").select("*").in_("sent_email_id", chunk).order("received_at", desc=True).execute()
        replies.extend(resp.data)
        
    # 3. Attach the company/to_email metadata
    for r in replies:
        em = email_dict.get(r["sent_email_id"], {})
        r["company"] = em.get("company", "")
        r["to_email"] = em.get("to_email", "")
        
    # Sort them again by received_at just in case the chunks arrived out of order
    replies.sort(key=lambda x: x.get("received_at", ""), reverse=True)
    return replies

def update_reply(reply_id: str, **fields):
    get_supabase().table("email_replies").update(fields).eq("id", reply_id).execute()

# ── Job Board Scraper ─────────────────────────────────────

def save_job(title: str, company: str, location: str, url: str, description: str, source: str):
    jid = str(uuid.uuid4())
    data = {
        "id": jid,
        "title": title,
        "company": company,
        "location": location,
        "url": url,
        "description": description,
        "source": source
    }
    try:
        # insert; if URL already exists, PostgreSQL will throw a duplicate key error which we catch
        get_supabase().table("scraped_jobs").insert(data).execute()
    except Exception:
        pass

def get_jobs() -> list[dict]:
    response = get_supabase().table("scraped_jobs").select("*").order("scraped_at", desc=True).execute()
    return response.data

# ── Skipped Companies ─────────────────────────────────────

def skip_company(user_id: str, company: str):
    try:
        get_supabase().table("skipped_companies").insert({"user_id": user_id, "company": company}).execute()
    except Exception:
        pass

def get_skipped_companies(user_id: str) -> list[str]:
    response = get_supabase().table("skipped_companies").select("company").eq("user_id", user_id).execute()
    return [r["company"] for r in response.data]
