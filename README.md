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
| **Backend** | FastAPI | Fast development, deployable on AWS or Vercel |
| **Database** | SQLite (local) | Convenience, no hosting needed at this stage |
| **Styling** | Tailwind CSS v4 | Utility-first, rapid UI development |
| **Language** | TypeScript (FE) / Python (BE) | Type safety on frontend, rapid prototyping on backend |

> **Note on Python version**: The FastAPI version was chosen for compatibility with the Python version currently used across other projects, avoiding unnecessary Python upgrades.

## Project Structure

```
datapizza-tools/
├── .claude/                 # Claude Code agents and configuration
│   ├── agents/              # Specialized agents (BE/FE debugger, feature-builder, code-reviewer)
│   └── CLAUDE.md            # Workflow configuration
├── apps/
│   ├── web/                 # Next.js 16 frontend (port 3003)
│   │   ├── src/app/[locale]/ # Pages (homepage, craft-your-developer, jobs)
│   │   ├── src/components/   # Shared components (Navbar, Footer)
│   │   └── messages/it.json  # Italian translations
│   └── api/                 # FastAPI backend (port 8003)
│       ├── api/routes/       # API endpoints (/api/v1/jobs)
│       ├── api/database/     # SQLAlchemy models, connection, seed
│       └── api/schemas/      # Pydantic response models
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
