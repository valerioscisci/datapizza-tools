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
│   │   ├── src/app/[locale]/ # Pages (homepage, craft-your-developer, jobs, news, courses, login, signup, candidature)
│   │   ├── src/components/   # Shared components (Navbar, Footer, TechTag)
│   │   ├── src/lib/auth/      # NextAuth v5 config and useAuth hook
│   │   └── messages/it.json  # Italian translations
│   └── api/                 # FastAPI backend (port 8003)
│       ├── api/routes/       # API endpoints (/api/v1/jobs, /api/v1/auth, /api/v1/applications, /api/v1/news, /api/v1/courses)
│       ├── api/database/     # SQLAlchemy models (Job, User, Application, News, Course), connection, seed
│       ├── api/scrapers/     # Content fetching CLI (insert_content.py — used by GitHub Action agent)
│       ├── api/schemas/      # Pydantic response models
│       └── api/auth.py       # JWT authentication utilities
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
- 10 seeded Italian developer profiles + 6 sample applications
- News Tech page with category filters, cards, detail dialog, pagination
- Courses page with category/level filters, cards, detail dialog, pagination
- News feed API with category filters (AI, tech, careers) and 10 seeded news items
- Courses catalog API with category and level filters and 10 seeded courses
- GitHub Action for nightly content fetching (disabled, showcase) — uses Claude Code agent to fetch from HN, TLDR, Coursera, Udemy

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
```
