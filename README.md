# Namma Ooru Jobs

An AI-powered part-time job platform connecting **Owners** (who post jobs) with
**Students** (who discover, apply for, and take them), built with Django.

The site's name, tagline, home page banners, and About page content are all
editable from the Admin Panel — nothing in this README is hardcoded into the
brand, so "Namma Ooru Jobs" is just the default the app ships with.

## Features

- Role-based accounts: Owner and Student, each with their own profile and dashboard
- Owners: post, edit, and close job listings; review and manage applicants
- Students: browse/search jobs, apply, and track application status
- **AI features** (via the Anthropic Claude API, with automatic non-AI fallback if no key is set):
  - AI-assisted job posting — turns a rough idea into a structured listing
  - AI job matching & applicant ranking — scores relevance between jobs and student profiles, with a plain-language reason shown alongside the score
  - AI applicant summarization — a one-line summary for owners reviewing applicants
  - AI natural-language search — "evening jobs near campus" → structured filters
  - AI business blurb assistant — owners describe their shop in a few words, AI writes the "about" text students see on job posts
  - AI profile tips — students get short, actionable suggestions to strengthen their profile
- Business identity throughout the app — shop name, avatar initial, location and short "about" blurb shown on job cards, job detail, and applicant lists
- A designed home page with an auto-rotating, illustrated hero banner cycling through job categories (retail, tutoring, events, delivery), a category strip, and a "how it works" walkthrough
- A public **About** page, and a clean top nav (Home / Browse Jobs / About / Login / Sign Up)
- **Dynamic UI everywhere**: scroll-reveal animations, a sticky navbar that elevates on scroll, animated counters, a live client-side filter on Browse Jobs, an interactive star-rating widget, auto-dismissing alerts, and character counters on AI draft boxes
- Dynamic split-screen **Login** and **Sign up** pages with an illustrated side panel and rotating feature highlights
- A full multi-column **footer** on every page
- Post-completion ratings & reviews between owners and students
- A custom-built **Admin Panel** (`/manage/`) — separate from Django's built-in admin — with a dashboard (stats, category breakdown, recent activity) and full create/edit/delete control over Users, Jobs, Applications, Categories, and Reviews
- **Site Content is fully admin-editable, no code changes needed**: site name/tagline, footer text, support contact, About page mission/college copy (`Site Settings`), the home page's rotating banner slides — text, color theme, and an optional uploaded image per slide (`Hero Banners`), and the About page's three feature cards (`About Features`)
- An **AI help chatbot** (bottom-right on every page) that answers questions about using the site — posting jobs, applying, how matching works — backed by the Claude API with a built-in FAQ fallback if no key is set
- Django's built-in admin (`/admin/`) is still available for low-level/database-style moderation, and the new Site Content models are registered there too

## Project layout

```
jobconnect/        # settings, root urls
accounts/          # custom User model, StudentProfile, OwnerProfile, auth views
jobs/               # JobCategory, Job, posting/browsing/search views
applications/       # Application model, apply/status/applicant views
reviews/            # Review model, review flow
ai_assist/          # services.py — all AI calls (incl. the chatbot) live here; views.py exposes /ai/chat/
core/                # home/about pages, SiteSettings/HeroSlide/AboutFeature models, dashboard redirect, formutils.py
adminpanel/          # custom admin dashboard & CRUD at /manage/ (staff-only), incl. Site Content editing
templates/           # base.html (shared layout), _footer.html, _chatbot.html (floating AI widget)
static/css/          # style.css (full design system)
static/js/           # app.js (all front-end interactivity)
static/img/          # original SVG illustrations (hero banners, about, auth)
```

## Setup

1. **Create a virtual environment and install dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate        # Windows (PowerShell): .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Configure the AI key (optional but recommended)**
   ```bash
   cp .env.example .env
   # edit .env and add your ANTHROPIC_API_KEY
   ```
   Without a key, every AI feature falls back to a simple non-AI heuristic
   (see `ai_assist/services.py`) so the app still runs and is fully testable.

   To actually load `.env`, either `export $(cat .env | xargs)` before running
   `manage.py`, or add `from dotenv import load_dotenv; load_dotenv()` at the
   top of `jobconnect/settings.py` (python-dotenv is already in requirements.txt).
   **Never commit your real `.env`** — only `.env.example` should be checked in.

3. **Run migrations and seed data**
   ```bash
   python3 manage.py migrate
   python3 manage.py seed_categories     # job categories only
   python3 manage.py seed_site_content   # default site settings, hero banners, about features
   python3 manage.py seed_demo           # 10 owners, 10 students, 15 jobs, sample applications
   ```
   `seed_demo` calls `seed_site_content` and creates its own categories
   automatically, so running it alone is enough for a fully populated demo —
   `seed_categories` and `seed_site_content` are only needed if you want
   those without any demo accounts. All seeded accounts share the password
   `demo1234` (e.g. username `rajesh_stationery` or `arun_kumar`). All three
   commands are safe to re-run — they won't create duplicates.

4. **Create an admin account**
   ```bash
   python3 manage.py createsuperuser
   ```
   A superuser automatically gets `is_staff=True`, which unlocks the **Admin
   Panel** link in the nav bar and access to `/manage/`. To give an existing
   seeded account admin access instead, open `/admin/` (Django admin) with a
   superuser and tick "Staff status" on that user, or use `/manage/users/`
   once you have at least one admin account.

5. **Run the dev server**
   ```bash
   python3 manage.py runserver
   ```
   Visit `http://127.0.0.1:8000/`.

## Trying it out

1. Sign up as an **Owner**, fill in your business profile, then "Post a Job" —
   try the "✨ AI Draft Assistant" box to auto-generate a listing from a rough idea.
2. Sign up as a **Student** (use a second browser or incognito window), fill in
   skills/availability, then browse jobs — they'll be sorted by AI match score,
   and you can also try the live filter box at the top of Browse Jobs.
3. Apply to a job. Log back in as the Owner and open "Applicants" on that job to
   see the AI-generated one-line summary and match score per applicant.
4. Accept the applicant, mark the job "Completed", then leave a review using
   the interactive star-rating widget.
5. Log in as your superuser and open **Admin Panel** in the nav (or go to
   `/manage/`) — the dashboard shows platform-wide stats, and every section
   (Users, Jobs, Applications, Categories, Reviews) supports search/filter,
   edit, and delete.
6. In the Admin Panel, open **Site Settings** and change the site name or
   tagline — it updates instantly in the nav, footer, and page titles across
   the whole site. Then try **Hero Banners** to edit or reorder the home page
   slides (optionally uploading your own image per slide), and **About
   Features** to edit the three cards on the About page.
7. Click the chat bubble in the bottom-right corner on any page and ask
   something like "how do I post a job?" — it answers from the Claude API if
   `ANTHROPIC_API_KEY` is set, or a built-in FAQ fallback if not.

## Notes on the AI layer

All AI calls are isolated in `ai_assist/services.py` behind these functions:
`enhance_job_posting`, `score_job_for_student` / `match_score` /
`rank_jobs_for_student`, `summarize_applicant`, `parse_search_query`,
`generate_business_blurb`, `profile_tips`, and `chat_reply` (the help
chatbot, POSTed to from `/ai/chat/`). Each one calls the Claude API for a
response and falls back to a plain heuristic (keyword overlap, naive text
parsing, rule-based checks, or a keyword-matched FAQ for chat) if
`ANTHROPIC_API_KEY` isn't set or the call fails — so you can develop and
grade the rest of the app without needing an API key, and swap in real AI
output any time by setting the key.

## Notes on the Admin Panel

`/manage/` is guarded by `adminpanel/decorators.py::admin_required`, which
requires `request.user.is_staff` (or `is_superuser`) — anyone else is
redirected back to their normal dashboard. It's a fully separate, custom-built
interface (sidebar layout, its own dashboard, search/filter bars, styled
tables) rather than a reskin of Django's built-in admin, which remains
available at `/admin/` if you prefer the standard interface for quick
database-level edits.

## Next steps / ideas

- Move AI calls to Celery + Redis so posting/applying doesn't wait on the API
- Add in-app notifications (new applicant, status change)
- Add a REST API (Django REST Framework) if a separate frontend is wanted later
- Deploy to Render/Railway with a managed Postgres database
- Add pagination and bulk actions (bulk delete/approve) to the Admin Panel tables
