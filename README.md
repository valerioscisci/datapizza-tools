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
├── .github/workflows/       # GitHub Actions (fetch-content.yml — disabled nightly scraper)
├── .claude/                 # Claude Code agents and configuration
│   ├── agents/              # Specialized agents (BE/FE debugger, feature-builder, code-reviewer, content-fetcher)
│   └── CLAUDE.md            # Workflow configuration
├── apps/
│   ├── web/                 # Next.js 16 frontend (port 3003)
│   │   ├── src/app/[locale]/ # Pages (homepage, craft-your-developer, jobs, news, courses, login, signup, candidature, profilo, talenti, proposte, azienda/proposte, notifiche)
│   │   ├── src/components/   # Shared components (Navbar, Footer, TechTag)
│   │   ├── src/lib/auth/      # NextAuth v5 config and useAuth hook
│   │   ├── e2e/              # Playwright E2E tests (auth, jobs, applications, profile)
│   │   └── messages/it.json  # Italian translations
│   └── api/                 # FastAPI backend (port 8003)
│       ├── api/routes/       # Domain-driven API endpoints (each feature = folder with router.py + schemas.py, children as subfolders)
│       ├── api/database/     # SQLAlchemy models (Job, User, Application, News, Course, Experience, Education, Proposal, ProposalCourse, ProposalMilestone, ProposalMessage, AICache, EmailLog, NotificationPreference), connection, seed
│       ├── api/services/     # Business logic services (GeminiAdvisor — AI-powered job matching and career recommendations, EmailService — local email notifications, TelegramService — Telegram Bot notification delivery)
│       ├── api/scrapers/     # Content fetching CLI (insert_content.py — used by GitHub Action agent)
│       ├── api/openapi.py     # Custom OpenAPI schema with tags, security, and API docs
│       ├── api/auth.py       # JWT authentication utilities
│       ├── prompts/          # AI prompt templates (job_matcher.md, career_advisor.md)
│       └── tests/            # pytest unit test suite (377 tests)
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
- User authentication (NextAuth v5 with Credentials provider, backend JWT + bcrypt)
- User profiles with skills, experience, availability status
- Job application system (apply in-app, duplicate prevention)
- Applications tracking page with status tabs (Proposte, Da completare, Attive, Archiviate)
- 10 seeded Italian developer profiles (6 public, 4 private) + 6 sample applications
- News Tech page with category filters, cards, detail dialog, pagination
- Courses page with category/level filters, cards, detail dialog, pagination
- News feed API with category filters (AI, tech, careers) and 10 seeded news items
- Courses catalog API with category and level filters and 10 seeded courses
- Profile API with experiences and educations CRUD (8 endpoints: GET/PATCH profile, POST/PATCH/DELETE experiences, POST/PATCH/DELETE educations)
- 13 seeded experiences and 8 educations for the first 5 users
- Profile page (`/it/profilo`) with full profile view, inline editing (bio, skills, experiences, educations, social links), and privacy toggle for public profile visibility
- Public talents marketplace (`/it/talenti`) with search, experience level and availability filters, talent cards with skills pills, and detail pages with full read-only profile view (bio, skills, experiences, educations) and CTA linking to Craft Your Developer
- GitHub Action for nightly content fetching (disabled, showcase) — uses Claude Code agent to fetch from HN, TLDR, Coursera, Udemy
- Public Developer Profiles (Browse Talents) API — GET /talents (list with search, filters, pagination) and GET /talents/{id} (detail with experiences/educations), public endpoints with privacy protection (is_public flag, no email/phone leak, 404 for private users)
- Company Accounts & Contact Flow (Backend) — Dual user types (talent/company), company signup with validation, Proposal and ProposalCourse models, 5 proposal endpoints (POST/GET list/GET detail/PATCH update/PATCH course complete), role-based access control, status transitions (draft/sent/accepted/rejected/completed), auto-complete on all courses done, 3 seeded company users and 3 sample proposals
- **Craft Your Developer Flow Completion (Backend)** — Enhanced training execution with gamification (XP system, milestones for course start/completion/streaks/progress thresholds), course delivery dashboard endpoint, communication system (proposal messages with pagination and role-based access), hire-after-training flow (accepted/completed -> hired status transition with talent availability update). New models: ProposalMilestone, ProposalMessage. New ProposalCourse fields: started_at, talent_notes, company_notes, deadline, xp_earned. New Proposal fields: total_xp, hired_at, hiring_notes. 8 new endpoints across proposals and messages sub-domain. 4 seeded proposals including 1 hired, milestones, and messages. Status transitions now include "hired"
- **AI-Powered Job Matching & Career Recommendations (Backend)** — Gemini-powered AI features via `google-genai` SDK. GeminiAdvisor singleton service with job matching (profile vs jobs scoring 0-100 with reasons) and career recommendations (career direction, course/article suggestions, skill gaps). 4 AI endpoints (POST/GET /ai/job-matches, POST/GET /ai/career-advice) with JWT auth, 24h caching in AICache table, 503 on AI unavailability, Italian prompt templates. New AICache model with user_id, cache_type, content_json, expires_at
- **Swagger / OpenAPI Documentation** — Full Swagger UI at `/docs` with custom OpenAPI schema. 14 tag groups (including Notifications), JWT Bearer security scheme, per-endpoint summaries and error responses, Field descriptions on all Pydantic schemas. Public endpoints marked with `openapi_extra={"security": []}`. Centralized tag metadata and custom schema generator in `api/openapi.py`
- **Backend unit test suite** — 413 pytest tests covering auth, routes (auth, jobs, news, courses, profile, applications, talents, proposals, messages, ai, notifications), schemas, services (GeminiAdvisor, EmailService, TelegramService), and utilities with full mocking (no real DB). All passing
- **Frontend E2E test suite** — Playwright tests covering auth flow, jobs page, applications, profile page, talents marketplace (list, search, filters, detail, privacy, navigation), profile privacy toggle, and company accounts & proposals flow (company signup, login redirects, role-based navbar, talent detail CTA, proposal creation, company/talent proposals dashboards, auth guards) — 65 tests total, verified on both Chromium and Firefox
- **Company Accounts & Contact Flow (Frontend)** — Dual user types (talent/company) with type-aware signup form, login redirect logic, and role-based navigation. Company users see "Le mie Proposte" and can propose training paths to talents. Talent users see received proposals with accept/reject/course-completion flow. Full proposals CRUD: talent proposals page (`/it/proposte`), company proposals page (`/it/azienda/proposte`), proposal creation page (`/it/azienda/proposte/nuova`) with course selection, reordering, message, and budget range. Navbar adapts to user type showing relevant links. Talent detail page shows company-specific CTA "Proponi un Percorso" for authenticated company users
- **AI-Powered Job Matching & Career Advisor (Frontend)** — AI Match button on jobs page (visible for authenticated users) with match score badges on job cards (green >=80%, yellow 60-79%, gray <60%), tooltip with match reasons, "Best Match" sort option, and AI match details in job detail dialog. AI Career Advisor collapsible panel on profile page with career direction, skill gaps (red pills), top 3 recommended courses with level badges and AI reasoning, top 3 recommended articles with source links. Loading skeletons, graceful 503 error handling with retry, and 24 new i18n keys
- **Email Notifications + Daily Digest (Backend)** — Local-only email notification system (no SMTP, stored in DB). New models: EmailLog (recipient, email_type, subject, body_html/text, related_proposal_id, is_read), NotificationPreference (email_notifications, daily_digest, channel, telegram_chat_id, telegram_notifications per user). EmailService with 9 notification methods: proposal received/accepted/rejected, course started/completed, milestone reached, hiring confirmation (both parties), daily digest with AI cache fallback to recent courses. HTML escaping on all user-controlled values (XSS prevention). 10 notification REST endpoints: GET/email list with typed email_type filter, GET email detail (auto-mark read), PATCH mark read (single/all), GET unread count, GET/PATCH preferences (with telegram fields), POST/DELETE telegram/link, POST trigger digest. Route path conflict fix (read-all before {email_id}/read). Integrated into proposals router with try/except wrappers and no duplicate user queries. Composite index on recipient_id+email_type. Seed data: notification preferences for all users + 5 sample email logs
- **Telegram Bot Integration (Backend)** — TelegramService for sending notifications via Telegram Bot API (`httpx`). Dual-channel delivery: after each EmailLog creation, also sends via Telegram if user has it enabled. Link/unlink endpoints (POST/DELETE /notifications/telegram/link) to save chat_id. Graceful degradation: missing TELEGRAM_BOT_TOKEN logs warning and skips, Telegram failures never block the main notification flow (try/except). NotificationPreference model extended with telegram_chat_id and telegram_notifications columns. Channel validation via Literal["email", "telegram", "both"]. 9 new unit tests for TelegramService (397 total)
- **Email Notifications + Daily Digest (Frontend)** — Full notification center page (`/it/notifiche`) with email list, tab filters (All/Unread/Proposals/Courses/Milestones/Hiring/Digest), email detail dialog with HTML body rendering, pagination, mark-as-read (single + batch). Notification preferences collapsible panel with toggle switches for email notifications, daily digest, and Telegram notifications, generate-digest-on-demand button, channel display with dynamic Telegram badge. Telegram Bot integration: link/unlink @datapizza_notify_bot via 3-step setup wizard (search bot, /start, paste Chat ID), toggle Telegram notifications, masked Chat ID display, Scollega button. Auth redirect for unauthenticated users, error banner with retry button. Navbar integration with Bell icon and red unread count badge (60s polling via shared `useUnreadCount` hook). Profile page integration with `NotificationPreferencesSection` card (Telegram toggle if linked, link to notifiche if not). 3 custom hooks (`useEmails`, shared `useUnreadCount`, shared `useNotificationPreferences` with `linkTelegram`/`unlinkTelegram`), 6 components, 70+ i18n keys. Feature-scoped directory structure under `notifiche/` with `_components/`, `_hooks/`, `_utils/`
- **Craft Your Developer Flow Completion (Frontend)** — Enhanced training execution with gamification UI (XP counter, milestone badges per proposal), per-course actions (start course, save talent notes, company instructions with deadlines, "go to course" external link, deadline badges with overdue/warning states). Proposal detail pages with vertical timeline layout for both talent (`/it/proposte/[id]`) and company (`/it/azienda/proposte/[id]`) views. Real-time chat system (ChatSection component with polling, chat bubbles, auto-scroll) available after proposal acceptance. Hire after training flow: company can hire talent via confirmation modal with progress summary, XP display, incomplete course warning, and optional hiring notes; talent sees celebration header with confetti-style gradient on hired status. New "hired" proposal status with emerald badge styling. Navigation links from proposal cards to detail pages. 100+ new i18n translation keys
- **Vercel Deployment** — Both frontend ([web-ten-zeta-68.vercel.app](https://web-ten-zeta-68.vercel.app)) and backend API ([api-three-beta-80.vercel.app](https://api-three-beta-80.vercel.app)) deployed on Vercel. Backend uses `@vercel/python` runtime with bundled SQLite DB auto-copied to `/tmp` for read-write access on Vercel's read-only filesystem. Dynamic CORS via `ALLOWED_ORIGINS` env var. Gemini AI features fully working with `GOOGLE_API_KEY`. E2E verified: jobs, login (talent+company), news, courses, CYD flow (browse talents, create proposal, accept, courses, chat, hire), AI Job Match (Gemini scores on all 10 jobs), AI Career Advisor (career direction, skill gaps, course/article recommendations)

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
