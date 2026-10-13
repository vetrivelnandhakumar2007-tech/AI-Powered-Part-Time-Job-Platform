"""
AI service layer for Namma Ooru Jobs.

Every function here degrades gracefully: if ANTHROPIC_API_KEY is not set
(settings.AI_FEATURES_ENABLED is False), each function falls back to a
simple non-AI heuristic instead of raising an error, so the rest of the
app keeps working without an API key during development.

Wire a real key via:  export ANTHROPIC_API_KEY="sk-ant-..."
"""
import json
import logging
import re

from django.conf import settings

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    """Lazily create the Anthropic client so importing this module never
    requires the package/key to be configured."""
    global _client
    if _client is None and settings.AI_FEATURES_ENABLED:
        import anthropic
        _client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


def _ask_json(prompt, max_tokens=500):
    """Call the model and parse a JSON object from its response.
    Returns None on any failure (missing key, bad JSON, API error)."""
    client = _get_client()
    if client is None:
        return None
    try:
        msg = client.messages.create(
            model=settings.AI_MODEL,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in msg.content if block.type == "text")
        text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
        return json.loads(text)
    except Exception:
        logger.exception("AI call failed; falling back to heuristic.")
        return None


def _ask_text(messages, system=None, max_tokens=400):
    """Call the model with a message list and return the raw text reply.
    Returns None on any failure (missing key, API error)."""
    client = _get_client()
    if client is None:
        return None
    try:
        kwargs = {"model": settings.AI_MODEL, "max_tokens": max_tokens, "messages": messages}
        if system:
            kwargs["system"] = system
        msg = client.messages.create(**kwargs)
        return "".join(block.text for block in msg.content if block.type == "text").strip()
    except Exception:
        logger.exception("AI chat call failed; falling back to heuristic.")
        return None


# ---------------------------------------------------------------------------
# 1. AI-assisted job posting
# ---------------------------------------------------------------------------

def enhance_job_posting(raw_idea):
    """Owner's rough idea -> structured draft dict matching JobForm fields."""
    prompt = f"""A part-time job platform owner typed this rough idea for a job posting:

"{raw_idea}"

Turn it into a structured job listing. Respond with ONLY a JSON object, no
other text, with these exact keys:
{{
  "title": "short job title",
  "description": "2-4 sentence clear description",
  "required_skills": "comma-separated skills, e.g. 'communication, punctuality'",
  "pay_rate": a reasonable number (numeric, no currency symbol),
  "pay_type": "hourly" or "fixed"
}}"""
    result = _ask_json(prompt)
    if result:
        return result

    # Fallback heuristic: no AI available — just title-case the raw idea.
    return {
        "title": raw_idea.strip()[:60].title() or "Part-Time Opportunity",
        "description": raw_idea.strip(),
        "required_skills": "",
        "pay_rate": "",
        "pay_type": "hourly",
    }


def extract_tags(text):
    """Extract a short list of keyword tags from job text, for matching."""
    prompt = f"""Extract up to 8 short keyword tags (skills, category words) from
this part-time job text. Respond with ONLY a JSON array of lowercase strings.

Text: "{text}" """
    result = _ask_json(prompt)
    if isinstance(result, list):
        return result

    # Fallback: naive keyword split.
    words = re.findall(r"[a-zA-Z]{4,}", text.lower())
    stopwords = {"this", "that", "with", "from", "will", "have", "your", "need", "part", "time"}
    tags = [w for w in dict.fromkeys(words) if w not in stopwords]
    return tags[:8]


# ---------------------------------------------------------------------------
# 2. AI matching & ranking
# ---------------------------------------------------------------------------

def _skill_overlap_heuristic(job, student_profile):
    job_skills = {s.strip().lower() for s in job.required_skills.split(',') if s.strip()}
    student_skills = {s.strip().lower() for s in student_profile.skills.split(',') if s.strip()}
    if not job_skills:
        score = 50.0
        overlap_list = []
    else:
        overlap = job_skills & student_skills
        overlap_list = sorted(overlap)
        score = round(100 * len(overlap) / len(job_skills), 1)

    if overlap_list:
        reason = f"Shares {', '.join(overlap_list)} with what the job needs."
    elif student_profile.availability:
        reason = f"Matches on availability ({student_profile.availability})."
    else:
        reason = "Open match — add skills to your profile for sharper recommendations."
    return score, reason


def score_job_for_student(job, student_profile):
    """Return {'score': 0-100, 'reason': short string} for one job + student."""
    if student_profile is None:
        return {"score": None, "reason": ""}

    prompt = f"""Score how well this student fits this part-time job, from 0-100,
and give ONE short reason (under 15 words) a student would find useful.

Job: {job.title} — {job.description}
Required skills: {job.required_skills}
Location: {job.location}

Student skills: {student_profile.skills}
Student availability: {student_profile.availability}
Student bio: {student_profile.bio}

Respond with ONLY a JSON object: {{"score": <integer 0-100>, "reason": "..."}}"""
    result = _ask_json(prompt, max_tokens=100)
    if result and "score" in result:
        try:
            return {"score": float(result["score"]), "reason": result.get("reason", "")}
        except (TypeError, ValueError):
            pass

    score, reason = _skill_overlap_heuristic(job, student_profile)
    return {"score": score, "reason": reason}


def match_score(job, student_profile):
    """Return just the 0-100 relevance score (used where the reason isn't needed)."""
    return score_job_for_student(job, student_profile)["score"]


def rank_jobs_for_student(jobs, student_profile):
    """Sort Job objects by relevance to a student profile (best first).
    Attaches `ai_score` and `ai_reason` attributes to each job for display."""
    scored = []
    for job in jobs:
        result = score_job_for_student(job, student_profile)
        job.ai_score = result["score"] or 0
        job.ai_reason = result["reason"]
        scored.append(job)
    scored.sort(key=lambda j: j.ai_score, reverse=True)
    return scored


# ---------------------------------------------------------------------------
# 3. Applicant summarization
# ---------------------------------------------------------------------------

def summarize_applicant(student_user, student_profile, application_message):
    """Return a 1-2 line summary of an applicant for the owner to skim."""
    if student_profile is None:
        return ""

    prompt = f"""Summarize this job applicant for a busy owner in 1-2 short
sentences — no fluff, just the facts that matter for hiring.

Name: {student_user.get_full_name() or student_user.username}
College: {student_profile.college}
Year: {student_profile.year_of_study}
Skills: {student_profile.skills}
Availability: {student_profile.availability}
Bio: {student_profile.bio}
Note to owner: {application_message}

Respond with ONLY a JSON object: {{"summary": "..."}}"""
    result = _ask_json(prompt, max_tokens=150)
    if result and "summary" in result:
        return result["summary"]

    # Fallback: assemble a plain summary from the fields directly.
    parts = []
    if student_profile.college:
        parts.append(student_profile.college)
    if student_profile.year_of_study:
        parts.append(student_profile.year_of_study)
    if student_profile.availability:
        parts.append(f"available {student_profile.availability}")
    if student_profile.skills:
        parts.append(f"skills: {student_profile.skills}")
    return ", ".join(parts) or "No profile details provided."


# ---------------------------------------------------------------------------
# 4. Natural-language search
# ---------------------------------------------------------------------------

def parse_search_query(query_text):
    """Parse a free-text search into {'keywords': [...], 'location': str|None}."""
    prompt = f"""Parse this part-time job search query into structured filters.
Query: "{query_text}"

Respond with ONLY a JSON object:
{{"keywords": ["...", "..."], "location": "..." or null}}"""
    result = _ask_json(prompt, max_tokens=150)
    if result:
        return result

    # Fallback: treat the whole query as keywords, no location extraction.
    words = [w for w in re.findall(r"[a-zA-Z]{3,}", query_text.lower())]
    return {"keywords": words, "location": None}


# ---------------------------------------------------------------------------
# 5. Owner business blurb assistant
# ---------------------------------------------------------------------------

def generate_business_blurb(business_name, raw_details):
    """A few keywords about the business -> a short, friendly 'about' blurb
    students see on job listings and the business profile."""
    prompt = f"""Write a short, friendly "about this business" blurb (1-2
sentences, under 40 words) for a part-time job platform, based on these notes.
Speak as the business, in plain, welcoming language — no marketing fluff.

Business name: {business_name}
Notes: {raw_details}

Respond with ONLY a JSON object: {{"blurb": "..."}}"""
    result = _ask_json(prompt, max_tokens=150)
    if result and "blurb" in result:
        return result["blurb"]

    # Fallback: lightly clean up the raw notes as the blurb.
    text = raw_details.strip()
    return text[0].upper() + text[1:] if text else f"{business_name} is hiring on Namma Ooru Jobs."


# ---------------------------------------------------------------------------
# 6. Student profile tips
# ---------------------------------------------------------------------------

def profile_tips(student_profile):
    """1-3 short, actionable tips to strengthen a student's profile."""
    if student_profile is None:
        return []

    prompt = f"""Give up to 3 short, actionable tips (under 12 words each) to
help this student's profile get noticed by owners on a part-time job platform.
Only mention things that are actually missing or thin below.

College: {student_profile.college}
Year: {student_profile.year_of_study}
Skills: {student_profile.skills}
Availability: {student_profile.availability}
Bio: {student_profile.bio}
Has resume uploaded: {bool(student_profile.resume)}

Respond with ONLY a JSON array of strings, e.g. ["...", "..."]. If the
profile is already strong, respond with an empty array []."""
    result = _ask_json(prompt, max_tokens=200)
    if isinstance(result, list):
        return result

    # Fallback: rule-based checks on empty/short fields.
    tips = []
    if not student_profile.skills:
        tips.append("Add your skills so owners can find you.")
    if not student_profile.availability:
        tips.append("Add your availability (e.g. weekends, evenings).")
    if not student_profile.bio:
        tips.append("Write a short bio introducing yourself.")
    if not student_profile.resume:
        tips.append("Upload a resume to stand out.")
    return tips[:3]


# ---------------------------------------------------------------------------
# 7. Site help chatbot
# ---------------------------------------------------------------------------

_CHAT_SYSTEM_PROMPT = """You are the friendly help assistant embedded on Namma
Ooru Jobs, a platform where local business owners post part-time jobs and
students apply for them, with AI helping match, draft, and summarize.
Answer briefly (2-4 sentences) and only about using this site: signing up,
posting jobs, applying, AI matching, applicant review, and reviews. If asked
something unrelated, politely redirect to site topics. Never invent features
that were not described to you."""

_FAQ_FALLBACKS = [
    (("post", "job"), "Owners can post a job from 'Post a Job' in the nav — fill in the details, or type a rough idea into the AI Draft Assistant box and it'll write the listing for you."),
    (("apply", "application"), "Students can browse or search jobs from 'Browse Jobs', open one, and click 'Apply Now'. You can track your applications under 'My Applications'."),
    (("match", "recommend", "ai score", "percent"), "Every job is scored against your profile's skills and availability — the percentage and short reason you see is generated by AI, or a simple skill-overlap check if AI isn't configured."),
    (("review", "rating", "star"), "Once a job is marked 'Completed', both the owner and student can leave each other a star rating and short review."),
    (("sign up", "signup", "register", "account"), "Click 'Sign Up' in the top right, choose whether you're an Owner or a Student, and fill in your details — you'll be asked to complete your profile right after."),
    (("admin", "manage"), "Site admins can manage users, jobs, applications, categories, reviews, and even the home page banners from the Admin Panel, linked in the nav for staff accounts."),
    (("profile",), "You can edit your profile — skills and availability as a student, or business details as an owner — from the 'Profile' link in the nav."),
]


def chat_reply(message, history=None):
    """Reply to a chatbot message. `history` is a list of
    {'role': 'user'|'assistant', 'content': str} dicts (most recent last)."""
    history = history or []
    messages = history + [{"role": "user", "content": message}]
    reply = _ask_text(messages, system=_CHAT_SYSTEM_PROMPT, max_tokens=300)
    if reply:
        return reply

    # Fallback: simple keyword-matched FAQ answers.
    lower = message.lower()
    for keywords, answer in _FAQ_FALLBACKS:
        if any(kw in lower for kw in keywords):
            return answer
    return ("I can help with signing up, posting or finding jobs, how AI matching works, "
            "or reviews. Could you tell me a bit more about what you're trying to do?")
