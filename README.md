# AstroTwin

**Astrology that remembers your life.**

AstroTwin is a deployable AstroHack 2026 prototype for AstroLive. It turns a transactional **Ask → Consult → Pay → Leave** journey into a persistent product relationship built around profile, daily guidance, reflection, memory, sharing and high-intent human consultation.

## Problem

Consultation marketplaces are often episodic: the user arrives with a question, pays for an answer and leaves. The platform loses the context that could make the next interaction more relevant and the product more habit-forming.

## Solution

AstroTwin creates a persistent astrology-inspired identity that remembers goals, concerns, life events, questions and reflections. The experience responsibly presents these as personal guidance and reflection—not scientifically validated prediction.

## Product modules

- **AstroTwin Memory** — persistent profile, goals, events, reflections and conversation context.
- **Cosmic Daily** — repeatable daily scores, personalized guidance, actions and check-ins.
- **AstroCircle** — deterministic, shareable compatibility reflections with a public acquisition page.
- **AstroConnect** — intent-aware recommendations and an end-to-end demo booking flow.

## Product flywheels

```text
Personal Profile → Daily Guidance → Reflection → Better Memory
        ↑                                      ↓
Higher Retention ← More Personalization ← Richer Context
                         ↓
               High-Intent Consultation
```

```text
Existing User → AstroCircle → Compatibility Report → Share
                                                       ↓
New User ← Create AstroTwin ← Friend Opens Public Link
```

## Architecture

```text
astrotwin/
├── frontend/                 Next.js, TypeScript, Tailwind, Framer Motion, Recharts
│   ├── app/                  App Router catch-all and visual system
│   ├── components/           Product views and reusable UI
│   └── lib/                  Typed API client and domain types
├── backend/                  FastAPI, SQLAlchemy, SQLite
│   ├── app/
│   │   ├── main.py           REST API
│   │   ├── models.py         Relational data model
│   │   ├── schemas.py        Validated API request contracts
│   │   ├── seed.py           Complete demo data
│   │   └── services/         AI, intent, cosmic and compatibility engines
│   └── tests/                Critical flow tests
└── docs/                     Hackathon notes and AI disclosure
```

The frontend calls the backend through `NEXT_PUBLIC_API_URL`. SQLAlchemy isolates persistence so `DATABASE_URL` can later point to PostgreSQL/Supabase. AI generation is behind a provider abstraction and silently uses the deterministic demo provider when no external AI key exists.

## Run locally

Requirements: Node.js 20+, npm, Python 3.11+.

### Windows Command Prompt quick start

Open Command Prompt in the repository and start the API:

```cmd
cd backend
py -3.12 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
copy .env.example .env
python -m app.seed
python -m uvicorn app.main:app --reload --port 8000
```

Keep that window running. Open a second Command Prompt in the repository and start the web app:

```cmd
cd frontend
copy .env.example .env.local
npm install
npm run dev
```

Visit `http://localhost:3000` and choose **Explore Demo**. API documentation is available at `http://localhost:8000/docs`.

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m app.seed
uvicorn app.main:app --reload --port 8000
```

API docs: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
copy .env.example .env.local   # Windows
# cp .env.example .env.local   # macOS/Linux
npm install
npm run dev
```

Open `http://localhost:3000`.

## Environment variables

| Variable | Service | Required | Purpose |
|---|---|---:|---|
| `NEXT_PUBLIC_API_URL` | Frontend | Yes | Public FastAPI base URL |
| `NEXT_PUBLIC_APP_URL` | Frontend | Recommended | Canonical frontend URL |
| `DATABASE_URL` | Backend | No | Defaults to local SQLite; supports PostgreSQL URL |
| `FRONTEND_URL` | Backend | Yes in production | CORS origin |
| `AI_PROVIDER` | Backend | No | `demo` by default; provider boundary is extensible |
| `GEMINI_API_KEY` | Backend | No | Reserved for optional Gemini provider |
| `OPENAI_API_KEY` | Backend | No | Reserved for optional OpenAI-compatible provider |
| `OPENAI_BASE_URL` | Backend | No | Optional compatible provider base URL |

Never place secrets in `NEXT_PUBLIC_*` values.

## Judge demo

No credentials are required. Click **Explore Demo** on the landing page. It activates the seeded user **Anshika** (Career focus) with four memories, three upcoming August 2026 events, seven days of guidance, six prior reflection check-ins and transparent seeded business analytics.

Recommended 2–3 minute flow:

1. Explore Demo → populated dashboard.
2. Ask AstroTwin: “What should I focus on this week?” and show memory context.
3. Open Life Timeline.
4. Create an AstroCircle report for Akshay and copy/share the public link.
5. Ask: “I’m unsure whether I should change jobs.”
6. Open the Career astrologer recommendation and confirm a demo booking.
7. Open **Demo Analytics** from the sidebar.

## What uses persisted data

- Users, profile settings, memories, events, daily guidance and reflection check-ins.
- Conversations and both user/assistant messages.
- Compatibility reports and public share IDs.
- Astrologers, consultations and analytics events.
- CRUD operations for memories and life events.

## Deterministic prototype logic

- Daily scores hash birth date + category + current date into a stable 55–94 range.
- Compatibility hashes both people’s input and relationship type into repeatable metrics.
- The no-key AI fallback selects profile memories and upcoming events, then creates coherent contextual guidance.
- Intent detection uses transparent keyword themes to trigger the right specialization.
- Seed analytics include realistic presentation volume; live interactions add real events.

This logic is intentionally replaceable with a real astrology calculation or AI provider later.

## Business metrics

- **Retention:** D1, D7, daily opens, daily check-ins.
- **Engagement:** questions/user, life events/user, memories/user.
- **Virality:** invites/user, share-link conversion and `K = invites per user × invite conversion rate`.
- **Monetization:** recommendation rate, recommendation → profile click, profile → booking, bookings/active user.

## Tests and build

```bash
cd backend && pytest
cd frontend && npm run typecheck && npm run build
```

Backend tests cover deterministic scoring, repeatable compatibility, memory/event CRUD, request validation, same-day reflection upserts, resonance math, safe-question routing, fallback chat intent and persisted consultation booking.

## Publish to GitHub

Create an empty GitHub repository without adding a README, license or `.gitignore`, then run these commands from the AstroLive repository root:

```cmd
git status
git add .
git commit -m "Initial AstroTwin release"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

Replace `YOUR_USERNAME` and `YOUR_REPOSITORY` with the values from GitHub. Local environment files, virtual environments, dependencies, build output and SQLite databases are excluded by `.gitignore`; the safe `.env.example` templates remain tracked.

## Deployment

### Frontend — Vercel

1. Import the repository in Vercel.
2. Set Root Directory to `frontend`.
3. Set `NEXT_PUBLIC_API_URL` to the public Render backend URL and `NEXT_PUBLIC_APP_URL` to the Vercel URL.
4. Deploy with the standard Next.js preset; `frontend/vercel.json` declares the framework.

### Backend — Render

1. Create a Web Service from the repository or use `backend/render.yaml`.
2. Root Directory: `backend`.
3. Build: `pip install -r requirements.txt`.
4. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
5. Set `FRONTEND_URL` to the Vercel URL.
6. For durable production data, replace ephemeral SQLite with a managed PostgreSQL `DATABASE_URL`.

## Responsible use

AstroTwin provides astrology-based reflective guidance for entertainment and personal exploration. It should not replace professional medical, legal, financial or mental-health advice. The interface avoids guaranteed outcomes and labels “resonance” as subjective guidance alignment.

## Current limitations

- External Gemini/OpenAI adapters are prepared as an abstraction but the shipped implementation uses the complete deterministic fallback.
- Booking is intentionally demo-only and does not collect payment or place a real call.
- Authentication uses a device-local user ID for hackathon speed.
- SQLite on Render is ephemeral unless a persistent disk is attached; PostgreSQL is recommended for production.
- Birth-chart calculations are explicitly prototype personalization scores, not a full astrology engine.
