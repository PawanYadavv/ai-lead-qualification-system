# AI Lead Qualification System (MVP)

A production-structured FastAPI MVP that lets businesses embed an AI chatbot on their website, qualify visitors into leads, score them automatically, and notify the business when a lead is hot.

## What this MVP includes

- Multi-tenant architecture (per-business tenant configuration)
- Embeddable chat widget (plain JavaScript)
- AI conversation engine via OpenAI API
- Lead data capture: name, email, phone, budget, timeline, requirement
- Rule-based lead scoring with tenant threshold
- Qualified lead notifications (email + dashboard record)
- Admin APIs for leads, conversations, analytics
- PostgreSQL persistence with SQLAlchemy ORM
- Optional Qdrant integration switch for vector support
- Docker and docker-compose setup

## Project structure

```text
backend/
  app/
    main.py
    api/
      deps.py
      routes/
        auth.py
        tenants.py
        chatbot.py
        leads.py
        notifications.py
        analytics.py
    core/
      config.py
      database.py
      security.py
    models/
      base.py
      tenant.py
      user.py
      chat_session.py
      message.py
      lead.py
      notification.py
    schemas/
      auth.py
      tenant.py
      chatbot.py
      lead.py
      notification.py
      analytics.py
    services/
      prompt_templates.py
      openai_service.py
      lead_scoring.py
      conversation_service.py
      notification_service.py
      qdrant_service.py
    utils/
frontend/
  landing/
    index.html
    style.css
  widget/
    lead-widget.js
    demo.html
Dockerfile
docker/
  backend.Dockerfile
nginx.conf
docker-compose.yml
.env.example
README.md
```

## Backend modules

- `auth`: JWT auth, tenant+admin registration, login
- `tenants`: manage tenant chatbot settings and threshold
- `chatbot`: public session/message APIs + admin conversations API
- `leads`: list leads and scores per tenant
- `notifications`: dashboard notifications per tenant
- `analytics`: lead and conversation summary metrics

## Core API endpoints

Base URL (via Nginx): `http://localhost/api/v1`

### Auth

- `POST /auth/register`
- `POST /auth/login`

### Public chatbot (for website widget)

- `POST /chatbot/session/start`
- `POST /chatbot/session/{session_id}/message`
- `GET /chatbot/session/{session_id}/messages?tenant_token=...`

### Admin (JWT required)

- `GET /tenants/me`
- `PATCH /tenants/me`
- `GET /leads`
- `GET /conversations`
- `GET /analytics`
- `GET /notifications`

## Deploy on Railway (exact steps)

1. Push the repository to GitHub.
2. Open Railway and create a new project from the GitHub repository.
3. Add a PostgreSQL service in the same Railway project.
4. Open the API service in Railway and confirm it builds using the root `Dockerfile`.
5. In the API service `Variables` tab, set these values:

```env
APP_ENV=production
API_V1_PREFIX=/api/v1
SECRET_KEY=replace-with-a-long-random-secret
ACCESS_TOKEN_EXPIRE_MINUTES=1440
OPENAI_API_KEY=replace-with-your-openai-key
OPENAI_MODEL=gpt-4o-mini
DATABASE_URL=${{Postgres.DATABASE_URL}}
DATABASE_SSLMODE=require
USE_QDRANT=false
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASS=
SMTP_FROM_EMAIL=noreply@example.com
SMTP_USE_TLS=true
FRONTEND_BASE_URL=https://your-frontend-domain.com
BACKEND_CORS_ORIGINS=https://your-frontend-domain.com
```

6. Deploy the API service. Railway injects `PORT` automatically, and the container command already binds to `0.0.0.0:${PORT}`.
7. Go to `Settings -> Networking` for the API service and click `Generate Domain` to make it publicly accessible.
8. Copy the generated public URL, then set:

```env
API_BASE_URL=https://your-api-service.up.railway.app
```

9. Redeploy once after setting `API_BASE_URL`.
10. Validate production endpoints:

```bash
curl https://your-api-service.up.railway.app/health
curl https://your-api-service.up.railway.app/docs
```

11. Register a tenant to get a `widget_token`:

```bash
curl -X POST https://your-api-service.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "business_name": "Acme Solar",
    "full_name": "Owner",
    "email": "owner@acme.com",
    "password": "StrongPass123",
    "notification_email": "owner@acme.com"
  }'
```

12. In widget config, set:

```js
window.AILeadWidgetConfig = {
  apiBaseUrl: "https://your-api-service.up.railway.app/api/v1",
  tenantToken: "YOUR_WIDGET_TOKEN"
};
```

13. If your frontend is hosted on Railway too, set `FRONTEND_BASE_URL` and `BACKEND_CORS_ORIGINS` to that public frontend domain.

## Local run (Docker)

1. Create `.env` from `.env.example` and set:

```env
APP_ENV=production
API_BASE_URL=http://localhost
FRONTEND_BASE_URL=http://localhost:8080
NGINX_HOST_PORT=80
OPENAI_API_KEY=
```

Production CORS behavior:

- If `BACKEND_CORS_ORIGINS` is explicitly set, it is used.
- Otherwise in `APP_ENV=production`, allowed origins are derived from `FRONTEND_BASE_URL` and `API_BASE_URL`.
2. Start services:

```bash
docker-compose up --build
```

3. API will be available via Nginx:

- `http://localhost`
- Swagger docs: `http://localhost/docs`
- API base URL: `http://localhost/api/v1`
- PostgreSQL host port: `localhost:${POSTGRES_HOST_PORT}` (default: `5432`)
- Backend stays internal as `api:8000` (not published directly).

If host port `80` is restricted on your machine, set `NGINX_HOST_PORT` to another value (for example `8081`) and use `http://localhost:8081`.

4. Register a tenant/admin user:

```bash
curl -X POST http://localhost/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "business_name": "Acme Solar",
    "full_name": "Owner",
    "email": "owner@acme.com",
    "password": "StrongPass123",
    "notification_email": "owner@acme.com"
  }'
```

The response includes `tenant.widget_token` to use in the widget config.

## Easy testing (no PowerShell)

If PowerShell API calls feel difficult, use the included one-command smoke test.

### Option A: Single-click HTML dashboard (zero terminal commands)

1. Ensure Docker services are running.
2. Open this URL in browser:

`http://localhost/test-dashboard` (or `http://localhost:<NGINX_HOST_PORT>/test-dashboard` if overridden)

3. Click `Run Full Test` (or test individual endpoint buttons).

Optional Windows launcher:

`scripts/open_test_dashboard.bat`

1. Keep Docker services running:

```bash
docker-compose up -d
```

2. Run the automated end-to-end test:

```bash
python scripts/easy_test.py --base-url http://localhost/api/v1
```

This test automatically verifies:

- `/health`
- register + login
- chatbot session start + message
- `/leads`, `/conversations`, `/analytics`, `/notifications`

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
