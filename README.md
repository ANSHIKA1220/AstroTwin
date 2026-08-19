# AstroTwin

> Astrology that remembers your life.

AstroTwin is a working product prototype created for **AstroHack 2026: Build the Next Universe**. It extends AstroLive from a transactional consultation marketplace into a persistent astrology companion built around a verified Vedic chart, life context, daily reflection, shareable discovery and well-timed human consultation.

Astrology interpretations in this project are belief-based reflections, not scientifically validated predictions or professional advice.

![AstroTwin — astrology that remembers your life](frontend/public/og.png)

## The opportunity

A consultation marketplace can solve an urgent question, but an isolated **Ask → Consult → Pay → Leave** journey gives users little reason to return between consultations. Context is also lost: goals, milestones and earlier concerns do not naturally improve the next interaction.

AstroTwin creates a persistent astrology identity. It connects a user’s birth chart with the goals, events, memories, questions and reflections they choose to save, producing a compounding engagement loop:

```text
Profile → Guidance → Reflection → Memory → Better Personalization
   ↑                                                  ↓
   └──────── Retention ← Relevance ← More Context ───┘
                                  ↓
                         Human Consultation
```

AstroCircle adds a product-native acquisition loop:

```text
User → Compatibility Reflection → Public Share Link → Friend
  ↑                                                    ↓
  └────────────── New AstroTwin Profile ←──────────────┘
```

## Product experience

- **Authenticated AstroTwin profile** — sign up, sign in, sign out and maintain a private account.
- **Computed Vedic chart** — Lahiri sidereal Lagna, graha positions, whole-sign houses, Janma Nakshatra, pada, current transits and an approximate Vimshottari mahadasha.
- **Ask AstroTwin** — chart-grounded, context-aware conversation using Groq-hosted GPT-OSS 120B, with a deterministic local Vedic fallback.
- **Persistent memory** — user-controlled goals, events, reflections and recent conversation context.
- **Cosmic Daily** — transit-informed daily signals, a recommended action and a resonance check-in.
- **Life Timeline** — upcoming milestones that can personalize relevant guidance.
- **AstroCircle** — deterministic, shareable relationship and team reflection pages designed for organic discovery.
- **AstroConnect** — intent-aware astrologer recommendations and a complete prototype booking flow.
- **Demo Analytics** — clearly labelled illustrative funnel, engagement, retention and virality metrics.

## Judge demo

No credentials are required. Select **Explore Demo** to activate the fictional demo profile **Anshika** with a computed chart, rolling upcoming events, memories, daily guidance, reflections and illustrative analytics.

Recommended three-minute walkthrough:

1. Open the populated dashboard and Vedic Chart.
2. Ask: `What does my Vedic chart suggest for my upcoming interview?`
3. Follow up in the same conversation: `How should I prepare for that pattern?`
4. Open the Life Timeline and inspect the relevant milestone.
5. Generate an AstroCircle report and copy its public link.
6. Ask a high-intent career or relationship question and open the recommended astrologer.
7. Complete the demo booking and view Demo Analytics.

Judges can also create a separate account using their own birth inputs. The demo profile and seeded metrics are explicitly labelled and are never presented as real customer results.

## What is real and what is simulated

| Capability | Implementation |
|---|---|
| Birth chart | Calculated from date, exact time, coordinates and timezone with Swiss Ephemeris in Lahiri sidereal mode |
| Location resolution | Open-Meteo geocoding, with an offline index for common Indian cities |
| Accounts and sessions | Persisted accounts, PBKDF2 password hashes and signed HTTP-only cookies |
| User data | Persisted in SQLAlchemy models backed by SQLite locally or PostgreSQL in deployment |
| AstroTwin conversation | Verified chart JSON interpreted by Groq GPT-OSS 120B; local chart-grounded fallback on provider failure |
| Daily signals | Deterministic signals derived from actual sidereal transit houses; not probability forecasts |
| AstroCircle | Deterministic reflective scoring, not full Vedic synastry or scientific compatibility |
| Booking | Persisted prototype confirmation; no payment, real call or astrologer availability integration |
| Demo analytics | Illustrative assumptions plus recorded prototype events, clearly labelled in the interface |

## Architecture

```text
Browser
  │
  ▼
Next.js 15 + TypeScript                         Vercel
  │ credentialed REST requests
  ▼
FastAPI + Pydantic + SQLAlchemy                 Render
  ├── Authentication and ownership checks
  ├── Swiss Ephemeris Vedic calculation engine
  ├── Memory, events, chat, sharing and analytics
  ├── Groq provider → GPT-OSS 120B
  └── Deterministic Vedic fallback
  │
  ▼
Managed PostgreSQL                              Render Postgres
```

Repository layout:

```text
AstroLive/
├── frontend/                 Next.js application and typed API client
├── backend/
│   ├── app/                  API, models, schemas, seed and services
│   └── tests/                Core product and security-flow tests
├── docs/                     Report notes and AI usage disclosure
├── render.yaml               Backend and PostgreSQL infrastructure blueprint
└── .env.example              Safe configuration template
```

## Technology

- Frontend: Next.js, React, TypeScript, Framer Motion, Recharts and Lucide.
- Backend: FastAPI, Pydantic, SQLAlchemy and psycopg.
- Astrology: Swiss Ephemeris with Lahiri ayanamsa and whole-sign houses.
- AI interpretation: Groq Chat Completions with `openai/gpt-oss-120b`.
- Persistence: SQLite for local development; managed PostgreSQL for deployment.
- Hosting: Vercel frontend; Render API and Render PostgreSQL.

## Responsible design and data handling

- The interface avoids guaranteed outcomes and presents astrology as reflective guidance.
- Medical emergencies, self-harm, legal crises and guaranteed financial-return requests are routed away from astrology advice.
- Users can inspect, add, edit and delete their stored memories and events.
- Private API records are checked against the authenticated account.
- Passwords are never stored directly; PBKDF2-HMAC-SHA256 hashes use unique salts.
- Production sessions use signed, expiring, HTTP-only, secure cookies.
- When Groq is enabled, relevant computed chart fields, the question and selected user context are sent to Groq for interpretation. The API key remains server-side. Without a key—or if Groq is unavailable—the local provider remains functional.
- Public AstroCircle links should contain only information the user deliberately chooses to share.

See the [AI usage disclosure](docs/AI_DISCLOSURE.md) for the final submission disclosure.

## Local development

Prerequisites:

- Python 3.11 or newer
- Node.js 20 or newer
- Corepack/pnpm, or another package manager capable of installing the committed lockfile

### Backend

From the repository root:

```cmd
cd backend
py -3.12 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
copy .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

For hosted conversation, configure `backend/.env`:

```env
DATABASE_URL=sqlite:///./astrotwin.db
FRONTEND_URL=http://localhost:3000
SESSION_SECRET=replace-with-a-long-random-secret
SESSION_COOKIE_SECURE=false
GROQ_API_KEY=your-groq-key
GROQ_MODEL=openai/gpt-oss-120b
GROQ_BASE_URL=https://api.groq.com/openai/v1
```

The API is available at `http://localhost:8000`; interactive documentation is at `http://localhost:8000/docs`.

### Frontend

Open a second terminal from the repository root:

```cmd
cd frontend
copy .env.example .env.local
corepack pnpm install --frozen-lockfile
corepack pnpm dev
```

`frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

Open `http://localhost:3000`.

## Configuration

### Backend

| Variable | Required in production | Purpose |
|---|---:|---|
| `DATABASE_URL` | Yes | PostgreSQL connection string; injected automatically by the Render Blueprint |
| `FRONTEND_URL` | Yes | Exact Vercel production origin used by CORS |
| `SESSION_SECRET` | Yes | Signs session cookies; generated automatically by the Blueprint |
| `SESSION_COOKIE_SECURE` | Yes | Must be `true` for the HTTPS deployment |
| `GROQ_API_KEY` | Recommended | Enables richer hosted AstroTwin conversation |
| `GROQ_MODEL` | No | Defaults to `openai/gpt-oss-120b` |
| `GROQ_BASE_URL` | No | Defaults to `https://api.groq.com/openai/v1` |

### Frontend

| Variable | Required | Purpose |
|---|---:|---|
| `NEXT_PUBLIC_API_URL` | Yes | Public HTTPS URL of the Render API, without a trailing slash |
| `NEXT_PUBLIC_APP_URL` | Recommended | Canonical Vercel production URL |

Never put `GROQ_API_KEY`, `SESSION_SECRET` or `DATABASE_URL` in a `NEXT_PUBLIC_*` variable.

## Verification

Run before every release:

```cmd
cd backend
python -m pytest -q -p no:cacheprovider

cd ..\frontend
corepack pnpm typecheck
corepack pnpm build
```

The backend suite covers chart calculation, demo freshness, authentication, HTTP-only cookies, account isolation, memory and event CRUD, conversation ownership, provider selection, compatibility, reflections, safety routing, chart-grounded responses and booking.

## Recommended deployment

The repository is prepared for:

- **Frontend:** Vercel
- **Backend:** Render Web Service
- **Database:** Render managed PostgreSQL

This keeps the API and database in the same Singapore region and connects them through Render’s private database URL. The root [`render.yaml`](render.yaml) is the infrastructure definition.

### 1. Deploy the backend and database on Render

1. Push this repository to a public GitHub repository.
2. In Render, choose **New → Blueprint** and connect the repository.
3. Render detects `render.yaml` and creates `astrotwin-api` plus `astrotwin-db`.
4. When prompted, enter:
   - `FRONTEND_URL`: the expected final Vercel origin, such as `https://your-project.vercel.app`; correct it after Vercel deploys if necessary.
   - `GROQ_API_KEY`: the secret Groq key. Do not commit it.
5. Wait for deployment and open `https://YOUR-API.onrender.com/api/health`.
6. Confirm the response reports `status: ok`, `provider: groq` and `model: openai/gpt-oss-120b`.

The Blueprint injects `DATABASE_URL`, generates `SESSION_SECRET` and enables secure cookies. No database credentials belong in GitHub.

Render’s free PostgreSQL database currently has 1 GB storage and expires after 30 days. That covers the hackathon judging period, but upgrade or migrate it for a durable public product.

### 2. Deploy the frontend on Vercel

1. In Vercel, import the same GitHub repository.
2. Set **Root Directory** to `frontend`.
3. Keep the detected Next.js build settings.
4. Add production variables:

```env
NEXT_PUBLIC_API_URL=https://YOUR-API.onrender.com
NEXT_PUBLIC_APP_URL=https://YOUR-PROJECT.vercel.app
```

5. Deploy and copy the final Vercel URL.
6. Return to Render, set `FRONTEND_URL` to that exact Vercel origin—no path and no trailing slash—and redeploy the API.

### 3. Deployment smoke test

Use an incognito/private browser window:

1. Confirm the landing page loads without authentication.
2. Activate Explore Demo and open the dashboard.
3. Open Vedic Chart and confirm computed placements appear.
4. Ask two connected questions and confirm **Groq conversational AI** appears.
5. Create an account, sign out and sign back in.
6. Refresh and confirm the account and chart persist.
7. Generate an AstroCircle link and open it in a second private window.
8. Complete the demo booking flow.
9. Verify there are no CORS, cookie or mixed-content errors.
10. Verify the Vercel URL and repository open without requesting access.

## Success metrics

- Retention: D1/D7 return, guidance opens and reflection completion.
- Engagement: questions per user, memories per user and life events per user.
- Virality: shares per user, share-open conversion and profile creation from public reports.
- Monetization: recommendation rate, astrologer-profile click-through and booking conversion.

Seeded metrics are illustrative demo assumptions. Production targets require baseline data and experiments.

## Prototype limitations

- Astrology interpretations are belief-based and cannot guarantee outcomes.
- Vimshottari boundaries are approximate at day precision; divisional charts, yogas, shadbala and rectification are outside this prototype.
- AstroCircle is deterministic reflection, not complete Vedic synastry.
- Booking does not collect payment or create a real call/chat session.
- Groq’s free tier is rate-limited; the local Vedic provider handles outages or exhausted quota.
- Render free web services can cold-start, and free Render PostgreSQL expires after 30 days.

## Hackathon submission

The Unstop submission requires both:

1. A publicly accessible working prototype URL.
2. A cited project-report PDF of at least eight pages, named `AstroLive_TeamName_LeaderName.pdf`.

The report should cover the problem statement, AstroLive teardown, proposed solution, expected impact, success metrics, limitations, external sources and every AI tool used to create the prototype or report.
