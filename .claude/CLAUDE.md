# Claude Code Configuration for Datapizza Tools

## Context Loading

**Before starting any task**, always read these files to load project context:

1. `/Users/valerio/Documents/repositories/datapizza-tools/README.md` — Project overview, features, tech stack
2. `/Users/valerio/Documents/repositories/datapizza-tools/THOUGHT_PROCESS.MD` — Development decisions and thought process

## Using Subagents

When the user asks to launch a subagent or use an agent for a task, **always** choose from the available agents in the `.claude/agents/` folder:

- **datapizza-tools-be-debugger.md** - Backend debugging
- **datapizza-tools-fe-debugger.md** - Frontend debugging
- **datapizza-tools-be-feature-builder.md** - Backend feature building
- **datapizza-tools-fe-feature-builder.md** - Frontend feature building
- **datapizza-tools-be-code-reviewer.md** - Backend code review
- **datapizza-tools-fe-code-reviewer.md** - Frontend code review

Select the appropriate agent based on the task type (debugging, feature building, or code review) and the relevant codebase area (backend or frontend).

**Important**: Always use these agents for implementation tasks without requiring explicit user instruction each time.

## Pro Workflow

### Self-Correction

When corrected or a mistake is discovered, **automatically** save the rule to the SQLite database at `~/.pro-workflow/data.db` with project `datapizza-tools`. No approval needed.

```bash
sqlite3 ~/.pro-workflow/data.db "PRAGMA trusted_schema=ON; INSERT INTO learnings (project, category, rule, mistake, correction) VALUES ('datapizza-tools', '<CATEGORY>', '<RULE>', '<MISTAKE>', '<CORRECTION>');"
```

Categories: Navigation, Editing, Testing, Git, Quality, Context, Architecture, Performance, Claude-Code, Prompting.

### Knowledge Base Protocol

**Before every task**: query the SQLite learnings database for this project and consult MEMORY.md to apply known patterns and avoid repeated mistakes.

```bash
sqlite3 -header -column ~/.pro-workflow/data.db "PRAGMA trusted_schema=ON; SELECT id, category, rule FROM learnings WHERE project='datapizza-tools' OR project IS NULL ORDER BY times_applied DESC, created_at DESC;"
```

### Planning

Multi-file: plan first, wait for "proceed".

### Quality

After edits: lint, typecheck, test.

### Review Checkpoints

Pause for review at: plan completion, >5 file edits, git operations, auth/security code.
Between: proceed with confidence.

## Post-Prompt Routines

After completing each user prompt, perform the following:

1. **README.md** — Update `/Users/valerio/Documents/repositories/datapizza-tools/README.md` with fresh information **if needed** (new features, changed architecture, updated setup instructions, etc.). Skip if nothing relevant changed.

2. **THOUGHT_PROCESS.md** — Append to `/Users/valerio/Documents/repositories/datapizza-tools/THOUGHT_PROCESS.md` a bullet-point summary of the thought process behind the work just completed. **Write it in Italian.**

3. **Agent Updates** — If the Pro Workflow added new knowledge or self-correction learnings during the prompt, propagate relevant information to the appropriate agents in `.claude/agents/` so they stay up to date.

## Playwright & Browser Testing

- **NEVER store screenshots, traces, or any temp files outside `.playwright-mcp/`**
- All Playwright MCP and chrome-devtools MCP output (screenshots, snapshots, recordings) MUST go to `.playwright-mcp/`
- When taking screenshots with `browser_take_screenshot` or `take_screenshot`, always use a filename prefixed with `.playwright-mcp/` (e.g., `filename: ".playwright-mcp/my-screenshot.png"`)
- The `.playwright-mcp/` folder is gitignored — never commit its contents
