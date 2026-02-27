# Datapizza Tools

A platform to help developers navigate the rapidly changing tech job market driven by AI and agentic workflows. Built as an evolution of [Datapizza Jobs](https://jobs.datapizza.tech/).

## Vision

The tech job market is about to undergo a massive transformation in the next 6-12 months. The widespread adoption of agentic workflows will fundamentally change how developers work and their role within companies. An estimated 60-70% of digital jobs could be impacted by the introduction of AI tools in the workplace.

[Datapizza](https://datapizza.tech/it) is already a reference point in the Italian tech job market. This project aims to position Datapizza as **the main resource for developers** to:

- Navigate the new AI-driven job market
- Acquire new skills and reskill where needed
- Transition to new roles if affected by layoffs or job reductions

## Features (Planned)

### Jobs Board
Replicate and enhance the existing [Datapizza Jobs Board](https://jobs.datapizza.tech/?page=1) with improved search, filtering, and AI-powered job matching.

### Candidate Profiles
- Create a personal profile with current tech stack and skills
- Receive personalized recommendations for the job market
- Daily notifications with suggested AI courses and reskilling resources (via newsletter or Telegram bot, based on user preference)
- Opt-in settings for course suggestions and reskilling project alerts

### "Craft Your Developer" (B2B)
A new paid product for companies (see [Datapizza for Companies](https://datapizza.tech/it) - "Per le Aziende" section):

- Browse candidates currently searching for work
- Design a custom training program for a specific developer
- Reskill candidates with targeted courses and AI knowledge
- Hire the developer after the training program is completed

### Email Notifications + Daily Digest
- Full email notification system for platform events (proposals, courses, milestones, hiring)
- Notification center page (`/it/notifiche`) with tab filters (All, Unread, Proposals, Courses, Milestones, Hiring, Digest), email detail dialog, pagination, mark-as-read (single + all)
- Notification preferences with toggles for email notifications and daily digest, generate-on-demand digest trigger
- Telegram Bot integration: link/unlink @datapizza_notify_bot, toggle Telegram notifications, masked Chat ID display, 3-step setup wizard
- Navbar badge showing unread notification count with 60s polling
- Profile page integration with quick notification preferences section and Telegram status

### Planned Features (with implementation plans in `/plans/`)

- ~~**AI Skills Gap Analyzer**~~ (`plans/02-ai-skills-gap-dashboard.md`) — **Implemented** (see Development Status below)
- ~~**AI Agent Readiness Score**~~ (`plans/03-ai-readiness-score.md`) — **Implemented** (see Development Status below)
- **Reskilling Roadmaps** (`plans/04-reskilling-roadmaps.md`) — AI-generated learning paths for career transitions (e.g., "From Java Backend Dev to AI/ML Engineer" — 12-week plan). Browse pre-generated roadmaps, enroll, track progress week by week with XP gamification. Nightly GitHub Action (disabled, demo) generates/updates popular roadmaps

### TODO
- **Automated Payment System** — Allow companies to automatically disburse budget to candidates to fund the courses selected in their training program (e.g. Stripe Connect / escrow model with per-course or milestone-based payouts)

## Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Frontend** | Next.js (App Router) + React | Go-to stack for new projects; App Router is stable and production-ready |
| **Auth** | NextAuth v5 (Auth.js) | Industry-standard, secure session in httpOnly cookies, Credentials provider wrapping backend |
| **Backend** | FastAPI | Fast development, deployable on AWS or Vercel |
| **Database** | SQLite (local) | Convenience, no hosting needed at this stage |
| **Styling** | Tailwind CSS v4 | Utility-first, rapid UI development |
| **Language** | TypeScript (FE) / Python (BE) | Type safety on frontend, rapid prototyping on backend |

> **Note on Python version**: The FastAPI version was chosen for compatibility with the Python version currently used across other projects, avoiding unnecessary Python upgrades.

## Project Structure

```
datapizza-tools/
├── .github/workflows/       # GitHub Actions (fetch-content.yml — disabled nightly scraper, daily-digest.yml — disabled daily digest cron)
├── .claude/                 # Claude Code agents and configuration
│   ├── agents/              # Specialized agents (BE/FE debugger, feature-builder, code-reviewer, content-fetcher)
│   └── CLAUDE.md            # Workflow configuration
├── apps/
│   ├── web/                 # Next.js 16 frontend (port 3003)
│   │   ├── src/app/[locale]/ # Pages (homepage, craft-your-developer, jobs, news, courses, login, signup, candidature, profilo, talenti, proposte, azienda/proposte, notifiche, skill-gap)
│   │   ├── src/components/   # Shared components (Navbar, Footer, TechTag)
│   │   ├── src/lib/auth/      # NextAuth v5 config and useAuth hook
│   │   ├── e2e/              # Playwright E2E tests (auth, jobs, applications, profile, talents, proposals)
│   │   └── messages/it/     # Italian translations (domain-based split: common, auth, home, jobs, courses, profile, proposals, notifications, etc.)
│   └── api/                 # FastAPI backend (port 8003)
│       ├── api/routes/       # Domain-driven API endpoints (each feature = folder with router.py + schemas.py, children as subfolders)
│       ├── api/database/models/ # Per-domain SQLAlchemy models (user.py, jobs.py, proposals.py, notifications.py, etc.) with __init__.py re-exports
│       ├── api/database/     # Database connection, seed
│       ├── api/services/     # Business logic services (GeminiAdvisor — AI-powered job matching and career recommendations, EmailService — local email notifications, TelegramService — Telegram Bot notification delivery)
│       ├── api/scrapers/     # Content fetching CLI (insert_content.py — used by GitHub Action agent)
│       ├── api/openapi.py     # Custom OpenAPI schema with tags, security, and API docs
│       ├── api/auth.py       # JWT authentication utilities
│       ├── prompts/          # AI prompt templates (job_matcher.md, career_advisor.md)
│       └── tests/            # pytest unit test suite (515 tests)
├── THOUGHT_PROCESS.MD       # Development thought process log (in Italian)
└── README.md
```

## AI-Assisted Development Workflow

This project uses a structured AI-assisted development workflow to maximize productivity and code quality:

- **Ralph Loop** — Used for long-running tasks to iteratively improve output and maintain context across multiple rounds of work
- **Specialized Agents** — A set of focused agents (BE/FE debugger, feature-builder, code-reviewer) to save context window and deliver precise results on small, well-scoped tasks
- **Pro Workflow Plugin** — Persistent self-correction database that captures LLM hallucination fixes and context-rot issues, so corrections are applied automatically without repeating them each session

## Development Status

**Phase**: MVP Development

- Homepage with hero, stats, services, community sections
- Craft Your Developer B2B landing page
- Jobs Market with API integration and filtering
- 10 seeded job listings in SQLite
- User authentication (NextAuth v5 + backend JWT/bcrypt)
- User profiles with skills, experience, education, privacy toggle
- Job applications with duplicate prevention and status tracking
- 10 seeded Italian developer profiles + 6 sample applications
- News Tech page with category filters and pagination
- Courses catalog with category/level filters and pagination
- Profile CRUD (bio, skills, experiences, educations, social links)
- Public talents marketplace with search, filters, and detail pages
- Company accounts with role-based navigation and proposal flow
- Craft Your Developer full flow (proposals, courses, milestones, XP, chat, hiring)
- AI Job Matching with Gemini (scoring 0-100, match reasons, best-match sort)
- AI Career Advisor (career direction, skill gaps, course/article recommendations)
- AI Skills Gap Analyzer dashboard (demand status, missing skills, market trends, personalized insights)
- AI Agent Readiness Score (8-question self-assessment quiz, score on profile/marketplace, course suggestions, level filters)
- Auto-add missing skills to profile from skill gap analysis
- Email notifications + daily digest (in-DB, 9 notification types)
- Telegram bot integration (dual-channel delivery, link/unlink flow)
- Notification center with filters, preferences, and unread badge
- Automated daily digest endpoint with GitHub Action trigger
- Swagger/OpenAPI docs at `/docs` with 14 tag groups
- GitHub Action for nightly content fetching (disabled, showcase)
- 515 backend unit tests + 65 frontend E2E Playwright tests
- Vercel deployment (frontend + backend API with Gemini AI)

## Getting Started

```bash
# Install FE dependencies
pnpm install

# Install BE dependencies
cd apps/api && pip3 install -r requirements.txt

# Seed the database
cd apps/api && python3 -m api.database.seed

# Start BE (port 8003)
cd apps/api && python3 run_api.py

# Start FE (port 3003)
pnpm --filter datapizza-web dev

# Run BE tests
cd apps/api && python3 -m pytest tests/ -v

# Run FE E2E tests (requires BE + FE running)
cd apps/web && npx playwright test e2e/ --reporter=list
```

### AI Features Setup (Google Gemini)

The AI-powered job matching and career advisor features require a Google Gemini API key. Without it, the app still works — AI endpoints gracefully return 503 and the frontend shows a "service unavailable" message with retry.

To enable AI features:

1. Go to [Google AI Studio](https://aistudio.google.com/apikey) and create an API key
2. Create the backend env file:
   ```bash
   echo 'GOOGLE_API_KEY=your-api-key-here' > apps/api/.env
   ```
3. (Optional) Customize the model by adding to the same `.env`:
   ```bash
   GEMINI_MODEL=gemini-2.0-flash
   ```
   Default model is `gemini-2.0-flash` if not specified.

4. Restart the backend — AI endpoints will now return real Gemini-powered results, cached for 24h per user.

### Telegram Bot Notifications (Optional)

The platform supports sending notifications via the **@datapizza_notify_bot** Telegram Bot. Without configuration, this feature is silently disabled — no errors, the app works normally.

#### Backend setup

1. The bot token is already configured in `apps/api/.env`. If you need to recreate the bot:
   - Open Telegram and search for [@BotFather](https://t.me/BotFather)
   - Send `/newbot`, choose a name and a username (must end in `bot`)
   - Copy the token and add it to `apps/api/.env`:
     ```
     TELEGRAM_BOT_TOKEN=your-bot-token-here
     ```
2. Restart the backend — Telegram delivery is now active

#### How users activate Telegram notifications

From the **Notification Center** (`/it/notifiche`) or **Profile** page, users follow a simple 2-step wizard:

1. **Open** `@datapizza_notify_bot` on Telegram (or visit [t.me/datapizza_notify_bot](https://t.me/datapizza_notify_bot)) and press **Start** — the bot replies with your Chat ID
2. **Paste** the Chat ID into the link form on the platform and toggle **Telegram notifications** on

The bot auto-replies with the Chat ID via a webhook endpoint — no third-party bots needed.

#### Webhook setup (after deploy)

The bot uses a webhook to auto-reply with the user's Chat ID on `/start`. Register it once after deploying the backend:

```bash
curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://api-three-beta-80.vercel.app/api/v1/notifications/telegram/webhook", "allowed_updates": ["message"]}'
```

Optionally, add a secret token for webhook validation:
```bash
# Add TELEGRAM_WEBHOOK_SECRET to Vercel env vars, then:
curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://api-three-beta-80.vercel.app/api/v1/notifications/telegram/webhook", "allowed_updates": ["message"], "secret_token": "your-secret-here"}'
```

#### API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/notifications/telegram/webhook` | Telegram Bot webhook (public, no auth) |
| `POST` | `/api/v1/notifications/telegram/link` | Link Telegram account (body: `{ "chat_id": "..." }`) |
| `DELETE` | `/api/v1/notifications/telegram/link` | Unlink Telegram account |
| `PATCH` | `/api/v1/notifications/preferences` | Toggle `telegram_notifications` on/off |

#### Architecture notes

- **Dual-channel delivery**: every notification is saved as an EmailLog (in-app) first, then also sent via Telegram if the user has it enabled
- **Webhook**: `POST /telegram/webhook` receives Telegram updates and auto-replies to `/start` with the user's Chat ID — stateless, no DB access
- **Graceful degradation**: if `TELEGRAM_BOT_TOKEN` is missing, a warning is logged and Telegram is skipped. If the Telegram API call fails, it never blocks the main notification flow (try/except)
- **Service**: `TelegramService` in `apps/api/api/services/telegram_service.py` uses `httpx` with a 10s timeout

### Vercel Deployment

Both frontend and backend are deployed on Vercel:

- **Frontend**: [web-ten-zeta-68.vercel.app](https://web-ten-zeta-68.vercel.app)
- **Backend API**: [api-three-beta-80.vercel.app](https://api-three-beta-80.vercel.app)

The backend uses `@vercel/python` runtime with SQLite. On Vercel's read-only filesystem, the bundled `datapizza.db` is automatically copied to `/tmp` for read-write access. Environment variables (`JWT_SECRET`, `ALLOWED_ORIGINS`, `GOOGLE_API_KEY`) are configured via the Vercel project settings.

To redeploy:
```bash
# Backend
cd apps/api && vercel --prod

# Frontend
cd apps/web && vercel --prod
```
