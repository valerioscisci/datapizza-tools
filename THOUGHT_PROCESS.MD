# Thought Process

## Visione e Strategia
- Il mercato del lavoro tech sara' stravolto dai workflow agentici (60-70% dei lavori digitali impattati)
- Datapizza deve aiutare gli sviluppatori a navigare questo cambiamento, acquisire nuove competenze e trovare nuovi ruoli
- "Craft Your Developer" come prodotto B2B: aziende progettano percorsi formativi per candidati e li assumono dopo il reskilling

## Scelte Tecniche
- **Monorepo** con pnpm workspaces + Turborepo (CD/CI Vercel ottimizzato)
- **Backend**: FastAPI + SQLAlchemy + SQLite (zero costi fase iniziale, migrabile a PostgreSQL)
- **Frontend**: Next.js 16 + React 19 + Tailwind v4 + next-intl (solo locale italiano)
- **Auth**: NextAuth v5 con Credentials provider — JWT backend + httpOnly cookie frontend (migrato da auth custom con localStorage)
- **Design system**: palette Datapizza (azure-600 #1b64f5), font Oddval + Poppins, solo light mode
- **AI**: Gemini per insight personalizzati, approccio ibrido algoritmico + AI con graceful degradation

## Sviluppo Agenti e Tooling
- 6 agenti specializzati Claude (debugger, feature-builder, code-reviewer per BE e FE)
- Ralph Loop per task lunghi con iterazione sullo stesso prompt
- Pro Workflow plugin per salvare correzioni in SQLite e non ripetere errori
- GitHub Action con Claude Code come agente per fetch notturno contenuti (no scraper fragile)

## Feature Implementate (in ordine cronologico)

### Fase 1 — Scaffolding e Pagine Base
- Homepage ispirata a datapizza.tech (hero, stats, servizi, community, CTA)
- Landing page Craft Your Developer (problema, benefit, 4 step, confronto hiring)
- Job board con filtri work_mode, card dettaglio, paginazione, dialog con Escape/click esterno
- Cleanup generale: link reali footer, social corretti, cursor-pointer ovunque

### Fase 2 — Auth e Candidature
- Sistema auth JWT + bcrypt con modello User completo (skills, experience, availability, reskilling)
- Login/signup con validazione client-side, redirect post-auth
- Navbar con sezione auth (avatar, link candidature, logout)
- Pagina candidature con 4 tab stato, card con info job e recruiter
- Bottone "Candidati" nel job dialog integrato con auth (POST /applications o link esterno)
- Seed: 10 developer italiani + 6 candidature di esempio

### Fase 3 — Code Review e Pulizia
- Review BE+FE con agenti + 17 test Playwright E2E
- Fix: JWT secret env, N+1 query, email validation, token expiry, typed API responses
- Fix: useCallback su auth functions, body scroll lock, shared utility (formatSalary/formatDate)
- Deduplicazione utility BE (safe_parse_json_list) e FE (job-utils.ts)
- Migrazione da auth custom a NextAuth v5

### Fase 4 — News e Corsi
- Backend: modelli News e Course, route con filtri categoria/livello, seed 10+10 items
- Frontend: pagine news e courses (stesso pattern jobs — hero, filtri, griglia, dialog, paginazione)
- Code review: indici DB composite, helper response, TechTag condiviso, a11y fix
- Footer aggiornato con link news e corsi

### Fase 5 — Profilo Utente
- Backend: modelli Experience e Education, 8 endpoint CRUD, 3 campi URL social
- Frontend: pagina profilo completa (header, modal edit, skills inline, CRUD experience/education)
- Code review: fix hook ordering, type safety handleChange, error feedback, guard accessToken
- 6 test Playwright per profilo (redirect, dati, edit modal, skills, experience, education)
- 112 test unitari pytest (auth, jobs, news, courses, profile, applications, schemas, utils)

### Fase 6 — Browse Talents (Marketplace Pubblico)
- Backend: campo is_public, 2 endpoint pubblici con search/filtri, privacy (no email/phone esposti)
- Frontend: lista talenti con ricerca, filtri, card; dettaglio read-only; privacy toggle nel profilo
- Sezione "Scopri i Talenti" nella pagina CYD, link in navbar e footer
- 13 test Playwright (lista, dettaglio, privacy toggle, navigazione)
- Test suite: 134 test BE totali

### Fase 7 — Proposte e Notifiche
- Sistema proposte B2B: aziende creano percorsi formativi per candidati con milestones e corsi
- Notifiche: EmailLog + NotificationPreference, preferenze email/digest/telegram
- Integrazione Telegram: webhook auto-reply Chat ID, wizard 2-step, TelegramService
- Code review: XSS protection con DOMPurify, stale closure fix, mark as read fix
- 33 scenari E2E (talent flow, preferenze, telegram, company user, API edge cases)

### Fase 8 — AI Features
- **AI Job Match**: score matching per job con badge colorati e tooltip motivi
- **AI Career Advisor**: pannello profilo con direzione carriera, competenze, corsi, articoli
- **AI Skills Gap Analyzer**: dashboard /it/skill-gap con 4 sezioni (competenze, mancanze, trend, insight)
  - Backend: conteggio algoritmico domanda da Job.tags + Gemini per insight personalizzati
  - Frontend: auth guard, griglia 2 colonne, banner warning, skeleton loader
  - 41 test dedicati, totale 465 test BE
  - Testato con 3 utenti (2 developer + 1 company) — risultati personalizzati e coerenti

### Fase 9 — Refactoring e Cleanup
- Rimosso clsx (twMerge basta), split models.py in 9 file per-dominio
- Split traduzioni it.json in 13 file domain-based, fix stringhe hardcoded
- Estratte props in file .props.ts separati (~36 componenti)
- Fix formatSalary/workModeLabel con parametro t obbligatorio

### Fase 10 — Pianificazione Nuove Feature
- 4 piani dettagliati in /plans/ (daily digest, skill gap, AI readiness score, reskilling roadmaps)
- Automated Daily Digest implementato: endpoint bulk con API key + GitHub Action cron
- AI Skills Gap Analyzer implementato: dashboard completa con UX polish (auto-add skill, toast, hide existing)

### Fase 11 — AI Agent Readiness Score
- Quiz autovalutazione 8 domande su competenze AI/agentiche (scoring deterministico 0-100%, 4 livelli)
- Modello `AIReadinessAssessment` + 2 colonne denormalizzate su User per filtraggio veloce
- 4 endpoint sotto `profile/ai-readiness/`: quiz metadata, submit, get latest, course suggestions
- Suggerimenti corsi algoritmici basati su weak categories (no dipendenza Gemini)
- Quiz modale multi-step con progress bar, navigazione avanti/indietro, conferma chiusura
- Sezione profilo con progresso circolare SVG, badge livello colorato, suggerimenti corsi
- Marketplace talenti: badge AI Readiness su card e dettaglio, filtro per livello
- Guard company user: sezione nascosta nel profilo, 403 sugli endpoint
- 50 nuovi test unitari (515 totali), ~50 chiavi i18n, 5 scenari Playwright tutti passanti

## Pattern Consolidati
- File `.props.ts` per ogni componente con props
- Traduzioni split per dominio in `messages/it/`
- Modelli DB split per dominio in `api/database/models/`
- Hook custom per feature AI (loadCached on mount, generate on click, enrich data)
- Graceful degradation AI: dati algoritmici sempre, insight AI opzionali
- Test: pytest unitari (mock-only, ~3s) + Playwright E2E (login helper, idempotenti)
