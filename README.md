<div align="center">

# 🤖 AI Lead Qualification System

**Turn every website visitor into a qualified lead — automatically.**

An AI-powered SaaS platform that embeds an intelligent chatbot on any website, engages visitors in natural conversation, extracts lead data, scores them in real-time, and delivers qualified leads to a polished dashboard.

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Railway-0B0D17?style=for-the-badge)](https://ai-lead-qualification-system-production.up.railway.app/dashboard)
[![API Docs](https://img.shields.io/badge/📄_API_Docs-Swagger-85EA2D?style=for-the-badge)](https://ai-lead-qualification-system-production.up.railway.app/docs)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)

</div>

---

## The Problem

Businesses spend thousands on ads driving traffic to their website, but **96% of visitors leave without converting**. Manual live chat doesn't scale, and generic contact forms have <2% conversion rates.

## The Solution

An AI chatbot that **feels like a real conversation** — it greets visitors, understands their needs, collects contact info naturally, and scores them as leads. Business owners get a real-time dashboard with only the leads that matter.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **🤖 AI Chat Engine** | GPT-4o-mini powered conversations that naturally extract lead data (name, email, phone, budget, timeline, requirements) |
| **📊 Real-time Dashboard** | Professional SPA with login/register, live stats, lead tables with scoring, and integration setup |
| **🎨 Customizable Widget** | 2-line embed code. Customize colors, position, header text, welcome message — matches any brand |
| **📈 Intelligent Lead Scoring** | Automated 0-100 scoring based on data completeness, budget signals, and timeline urgency |
| **🏢 Multi-Tenant Architecture** | Each business gets isolated data, unique widget token, and independent settings |
| **🔐 JWT Authentication** | Secure token-based auth with tenant isolation — no data leaks between clients |
| **⚡ Admin API** | Activate/deactivate tenants, manage billing status via protected admin endpoints |
| **📧 Email Notifications** | SMTP-ready alerts when qualified leads come in (configurable per tenant) |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT'S WEBSITE                        │
│                                                             │
│   ┌─────────────────────────────────────┐                   │
│   │      Embeddable Chat Widget         │  ← 2 lines of JS │
│   │   (lead-widget.js + config)         │                   │
│   └──────────────┬──────────────────────┘                   │
└──────────────────┼──────────────────────────────────────────┘
                   │ REST API calls
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│                                                             │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐     │
│  │ Auth &   │  │  Chatbot     │  │  Lead Scoring     │     │
│  │ Tenants  │  │  Engine      │  │  Engine           │     │
│  └──────────┘  └──────┬───────┘  └───────────────────┘     │
│                       │                                     │
│              ┌────────▼────────┐                            │
│              │  OpenAI API     │                            │
│              │  (GPT-4o-mini)  │                            │
│              └─────────────────┘                            │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              PostgreSQL Database                      │   │
│  │  tenants | users | sessions | messages | leads       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              Business Owner Dashboard                        │
│                                                             │
│   📊 Overview Stats  │  👥 Lead Table  │  🔗 Integration   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11, FastAPI, SQLAlchemy ORM, Pydantic v2 |
| **AI Engine** | OpenAI GPT-4o-mini (chat + entity extraction) |
| **Database** | PostgreSQL (Railway-managed) |
| **Auth** | JWT (python-jose), OAuth2 Bearer scheme |
| **Frontend** | Vanilla JavaScript SPA (zero framework dependencies) |
| **Widget** | Self-contained JS file — works on any website |
| **Deployment** | Docker, Railway (auto-deploy on push) |
| **Infrastructure** | Nginx reverse proxy, CORS configured for cross-origin widget |

---

## 📁 Project Structure

```
├── backend/
│   └── app/
│       ├── main.py                    # FastAPI app, CORS, startup migrations
│       ├── api/
│       │   ├── deps.py                # Auth dependencies (JWT extraction)
│       │   └── routes/
│       │       ├── auth.py            # Register + Login (JWT)
│       │       ├── chatbot.py         # Widget session & message endpoints
│       │       ├── leads.py           # Lead CRUD with tenant isolation
│       │       ├── analytics.py       # Dashboard stats aggregation
│       │       ├── tenants.py         # Tenant settings management
│       │       ├── notifications.py   # Email notification endpoints
│       │       └── admin.py           # Tenant activate/deactivate (API key auth)
│       ├── core/
│       │   ├── config.py              # Pydantic Settings (env-driven)
│       │   ├── database.py            # SQLAlchemy engine & session
│       │   └── security.py            # Password hashing, JWT creation
│       ├── models/                    # SQLAlchemy ORM models
│       │   ├── tenant.py              # Multi-tenant with widget_token + is_active
│       │   ├── user.py                # Users with tenant FK
│       │   ├── chat_session.py        # Conversation sessions
│       │   ├── message.py             # Chat messages (user + AI)
│       │   ├── lead.py                # Extracted lead data + score
│       │   └── notification.py        # Lead notification records
│       ├── schemas/                   # Pydantic request/response models
│       └── services/
│           ├── openai_service.py      # GPT-4o-mini chat + entity extraction
│           ├── conversation_service.py # Orchestrates chat → extract → score → notify
│           ├── lead_scoring.py        # Rule-based 0-100 scoring algorithm
│           ├── notification_service.py # SMTP email delivery
│           └── prompt_templates.py    # System prompts for AI behavior
├── frontend/
│   ├── dashboard/
│   │   └── index.html                # Full SPA: login, stats, leads, integration
│   ├── widget/
│   │   ├── lead-widget.js            # Embeddable chat widget (customizable)
│   │   └── demo.html                 # Widget demo page
│   └── landing/
│       ├── index.html                # Product landing page
│       └── style.css
├── docker/
│   └── backend.Dockerfile
├── Dockerfile                         # Production container
├── docker-compose.yml                 # Local dev stack
├── nginx.conf                         # Reverse proxy config
└── .env.example                       # Environment template
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL (or Docker)
- OpenAI API key

### Option 1: Docker (Recommended)

```bash
# Clone the repo
git clone https://github.com/PawanYadavv/ai-lead-qualification-system.git
cd ai-lead-qualification-system

# Configure environment
cp .env.example .env
# Edit .env → set OPENAI_API_KEY

# Start everything
docker-compose up --build
```

Services:
- API: `http://localhost/api/v1`
- Swagger Docs: `http://localhost/docs`
- Dashboard: `http://localhost/dashboard`

### Option 2: Local Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r backend/requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://user:pass@localhost:5432/leadai
export OPENAI_API_KEY=your-key-here
export SECRET_KEY=your-secret-key

# Run
uvicorn backend.app.main:app --reload
```

---

## 🔌 API Reference

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/register` | Register business + admin user → returns JWT + widget token |
| `POST` | `/api/v1/auth/login` | Login → returns JWT |

### Chat Widget (Public — no auth required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/chatbot/session/start` | Start conversation (requires `tenant_token`) |
| `POST` | `/api/v1/chatbot/session/{id}/message` | Send visitor message → get AI response |
| `GET` | `/api/v1/chatbot/session/{id}/messages` | Fetch conversation history |

### Dashboard (JWT required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/leads` | List all leads with scores |
| `GET` | `/api/v1/analytics` | Dashboard stats (total leads, qualified count, avg score) |
| `GET` | `/api/v1/conversations` | All chat sessions |
| `GET` | `/api/v1/notifications` | Lead notifications |
| `GET` | `/api/v1/tenants/me` | Current tenant info |
| `PATCH` | `/api/v1/tenants/me` | Update tenant settings |

### Admin (API Key required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/admin/tenants` | List all tenants |
| `PATCH` | `/api/v1/admin/tenants/{id}/activate` | Activate a tenant |
| `PATCH` | `/api/v1/admin/tenants/{id}/deactivate` | Suspend a tenant |

---

## 🎨 Widget Integration

Embed the AI chatbot on **any website** with just 2 lines:

```html
<script>
  window.AILeadWidgetConfig = {
    apiBaseUrl: "https://your-api-domain.com/api/v1",
    tenantToken: "your-widget-token-here"
  };
</script>
<script src="https://your-api-domain.com/frontend/widget/lead-widget.js"></script>
```

### Customization Options

```html
<script>
  window.AILeadWidgetConfig = {
    apiBaseUrl: "https://your-api-domain.com/api/v1",
    tenantToken: "your-widget-token",
    primaryColor: "#0f766e",       // Widget accent color
    headerText: "Chat with us",    // Chat window title
    position: "right",             // "right" or "left"
    welcomeMessage: "Hi! How can we help you today?"
  };
</script>
<script src="https://your-api-domain.com/frontend/widget/lead-widget.js"></script>
```

---

## 📊 Lead Scoring Algorithm

Leads are scored on a **0–100 scale** based on:

| Factor | Weight | Criteria |
|--------|--------|----------|
| Name provided | 15 pts | Valid name detected |
| Email provided | 20 pts | Valid email format |
| Phone provided | 15 pts | Phone number detected |
| Budget mentioned | 20 pts | Budget/price discussed |
| Timeline given | 15 pts | Timeline or urgency mentioned |
| Requirement shared | 15 pts | Specific need described |

Leads scoring above the tenant's threshold (default: 70) are automatically marked **Qualified** and trigger notifications.

---

## 🚢 Deploy to Railway

1. Fork/push repo to GitHub
2. Create a Railway project → add **PostgreSQL** service
3. Add your API service from GitHub repo
4. Set environment variables:

```env
APP_ENV=production
SECRET_KEY=<random-64-char-string>
OPENAI_API_KEY=<your-openai-key>
OPENAI_MODEL=gpt-4o-mini
DATABASE_URL=${{Postgres.DATABASE_URL}}
DATABASE_SSLMODE=require
ADMIN_API_KEY=<your-admin-secret>
```

5. Generate a public domain in Railway → Settings → Networking
6. Done — auto-deploys on every `git push`

---

## 🗺️ Roadmap

- [x] Multi-tenant architecture with JWT auth
- [x] AI-powered chat with GPT-4o-mini
- [x] Real-time lead extraction (name, email, phone, budget, timeline)
- [x] Automated lead scoring (0-100)
- [x] Client dashboard with login/register
- [x] Embeddable & customizable widget
- [x] Tenant activation/deactivation (billing control)
- [x] Admin API with API key protection
- [ ] CSV/Excel lead export
- [ ] WhatsApp & Slack notifications
- [ ] Custom AI personality per tenant
- [ ] Analytics charts & conversion funnels
- [ ] Stripe billing integration
- [ ] Forgot password / password reset

---

## 📄 License

This project is for portfolio/demonstration purposes.

---

<div align="center">

**Built with FastAPI + OpenAI + PostgreSQL**

If this project helped you, consider giving it a ⭐

</div>

On Windows, you can also double-click:

`scripts/run_smoke_test.bat`

Optional: pass a custom API URL to the batch file:

`scripts/run_smoke_test.bat http://localhost/api/v1`

## Local run (without Docker)

1. Install PostgreSQL and create database `lead_qualification`.
2. Install Python 3.11+ dependencies:

```bash
cd backend
pip install -r requirements.txt
```

3. Set env vars from `.env.example` (especially `DATABASE_URL` and `OPENAI_API_KEY`).
4. Start backend:

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

## Widget setup

Use the embeddable widget script in any website:

```html
<script>
  window.AILeadWidgetConfig = {
    apiBaseUrl: "https://your-api-service.up.railway.app/api/v1",
    tenantToken: "YOUR_WIDGET_TOKEN"
  };
</script>
<script src="/path/to/lead-widget.js"></script>
```

`lead-widget.js` already supports dynamic API routing via `window.AILeadWidgetConfig.apiBaseUrl`.

For local demo, open `frontend/widget/demo.html` and set `tenantToken`.

## SMTP email notifications (Gmail example)

When a lead score crosses the tenant qualification threshold, the system creates a notification record and attempts to send an email.

- On success: notification `status = sent`
- On failure: notification `status = failed` and delivery error is appended in notification body

Configure SMTP in `.env` (or container env vars):

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-16-char-gmail-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_USE_TLS=true
```

Gmail App Password steps:

1. Enable 2-Step Verification on your Google account.
2. Go to Google Account -> Security -> App passwords.
3. Create an app password for "Mail".
4. Use that value in `SMTP_PASS`.

Docker note:

- `docker-compose.yml` already loads `.env` into the API container using `env_file`.
- Nginx listens on port `80` and forwards requests to `api:8000`.
- Uvicorn runs with `--proxy-headers --forwarded-allow-ips=*` so proxy headers are trusted.
- After changing SMTP values, restart API container:

```bash
docker-compose up -d --build
```

## Lead scoring logic

`lead_scoring.py` uses a simple weighted model:

- Contact completion (name/email/phone)
- Budget strength (higher budget => higher score)
- Timeline urgency (soon => higher score)
- Requirement clarity

Leads are marked qualified when score >= `tenant.qualification_threshold`.

## Notes for production hardening

- Add Alembic migrations
- Move rate limiting and bot protection to API gateway
- Add background job queue for notifications and analytics rollups
- Add stronger widget auth (signed session token)
- Add audit logs and tenant role separation
