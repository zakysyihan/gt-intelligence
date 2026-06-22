# AGENTS.md — Bangunindo Analytics MVP

> Shared rules for all AI agents working on this project.

## Agent Roles

| Agent | Role | Allowed |
|-------|------|---------|
| **Kilo Code** | Product planning, research, docs, spec writing | Markdown, config files ONLY |
| **Claude Code** | Code implementation, data pipeline, LLM integration | Source code, tests, notebooks |

**Kilo never edits source code.** If Kilo identifies a code improvement, write a prompt for Claude Code instead.

## Spec-Driven Development (SDD)

This project follows an **SDD-inspired** workflow — adapted from GitHub's [Spec-Driven Development](https://github.com/github/spec-kit) methodology for a 3-day sprint. The full Spec Kit tooling (CLI, templates, slash commands) is overkill for our timeline, so we take the core principle — spec as source of truth — and combine it with [Ponytail](https://github.com/DietrichGebert/ponytail) for anti-over-engineering efficiency. Every feature starts with a written specification.

**SDD is NOT:**
- Writing a spec once and never touching it
- A replacement for testing or verification
- A guarantee that AI will follow it perfectly

**SDD IS:**
- Writing a spec, implementing from it, then refining the spec based on what we learn
- The highest-leverage artifact — if code is lost, the spec can regenerate it
- A living document that evolves with the project

### The SDD Cycle

```
┌─────────┐     ┌──────────┐     ┌────────┐     ┌─────────┐
│  SPEC   │────▶│ RESEARCH │────▶│  BUILD │────▶│ VERIFY  │
│ (Kilo)  │     │ (Kilo)   │     │(Claude)│     │(Claude) │
└─────────┘     └──────────┘     └────────┘     └─────────┘
     ▲                                                    │
     └────────────────────────────────────────────────────┘
                    (iterate if verification fails)
```

### Rules for Kilo Code

1. Write SPEC.md before any implementation begins
2. Research datasets, tools, trade-offs → write findings to docs/
3. Define acceptance criteria for each feature
4. Review Claude Code's output against the spec
5. Never skip the spec to "just build it"

### Rules for Claude Code

1. Read SPEC.md before every session
2. Implement exactly what the spec says
3. If spec is ambiguous, ask for clarification (don't guess)
4. Write tests that verify spec requirements
5. Document trade-offs in code comments
6. One feature per commit — atomic, testable, revertable

## Ponytail — Anti-Over-Engineering (MANDATORY)

Adopted from [Ponytail](https://github.com/DietrichGebert/ponytail). All code agents must follow this.

> You are a lazy senior developer. Lazy means efficient, not careless. The best code is the code never written.

Before writing any code, stop at the first rung that holds:

```
1. Does this need to be built at all? (YAGNI)
2. Does the standard library already do this? Use it.
3. Does a native platform feature cover it? Use it.
4. Does an already-installed dependency solve it? Use it.
5. Can this be one line? Make it one line.
6. Only then: write the minimum code that works.
```

**Rules:**
- No abstractions that weren't explicitly requested.
- No new dependency if it can be avoided.
- No boilerplate nobody asked for.
- Deletion over addition. Boring over clever. Fewest files possible.
- Question complex requests: "Do you actually need X, or does Y cover it?"
- Pick the edge-case-correct option when two stdlib approaches are the same size.
- Lazy code without its check is unfinished: non-trivial logic leaves ONE runnable check behind.
- Mark intentional simplifications with a `ponytail:` comment. If the shortcut has a known ceiling, the comment names the ceiling and the upgrade path.

**NOT lazy about:** input validation at trust boundaries, error handling that prevents data loss, security, accessibility, anything explicitly requested.

**Critical difference from Halaqah AI / Latent Signal:**
- Those projects: "build working product fast, optimize later"
- This project: "build simple, explain everything, demonstrate understanding"

**Tech choice rules for this project:**
- Prefer Python stdlib (csv, json, sqlite3) over heavy frameworks
- Pandas over Polars (more common, easier to explain)
- OpenAI API direct over LangChain (simpler, fewer abstractions)
- SQLite over PostgreSQL (no infra needed)
- Every tech choice must be explainable in 1-2 sentences

## Prompt Rules (Kilo → Claude Code)

When writing prompts for Claude Code:

1. **Describe the problem, not the solution**
2. **Reference SPEC.md sections** — "Implement section 3.2 per SPEC.md"
3. **Include acceptance criteria** — "Verify: output matches expected schema"
4. **Keep prompts under 10 lines**
5. **One feature per prompt**

## Parallel Tasks (Multiple Claude Sessions)

**Claude Code MUST always work on a feature branch. NEVER work on `main`.**

This is not optional. Every task gets its own branch, automatically. The human never needs to ask for this — it's the default behavior.

### Rules

1. **Create a branch for every task.** Before writing any code, create a branch: `git checkout -b feat/<task-name>` or `fix/<task-name>`. Derive the name from the task description.
2. **Never push to main.** Push to your branch only: `git push origin <branch-name>`.
3. **Auto-merge when done.** After finishing all work, merge your branch to main: `git checkout main && git merge feat/<task-name> && git push origin main`.
4. **Deploy only from main.** After merging, deploy from `main`. Never from a feature branch.
5. **Sequential deploys.** If multiple sessions deploy, merge one at a time (merge → deploy → merge → deploy).
6. **Each session reads SPEC.md and updates docs as needed.** Every Claude session must update any docs affected by their changes (SPEC.md schema, ARCHITECTURE.md, CLAUDE.md, etc.) before merging to main. Docs and code ship together.
7. **Every branch must be merged to main before session ends.** Every task we give Claude is finished and deliverable. No orphan branches. Merge to main, push, done.

### What Kilo Does

Merges branches to main in order (backend first, then frontend). Deploys from main only. Updates HISTORY.md after each merge.

## Security

- NEVER read or display `.env` files
- NEVER expose API keys in code or logs
- Use environment variables for all secrets
- NEVER know, handle, or request VPS passwords — use SSH key-based auth only
- User sets up SSH keys manually, agents use key-based SSH commands only
- If password auth is required, user handles it off-screen

## Data Safety

- Validate data at every pipeline step
- Log data quality metrics
- Handle missing values explicitly
- Document all transformations

## Test Case Compliance (MANDATORY)

The official test case PDF (`LLM_Powered_Analytics_MVP_Case_Study_Instructions_5_Days.pdf`) is the **authoritative source** for all requirements, deliverables, and evaluation criteria.

### Rule

**Every request, prompt, feature, or decision MUST be checked against the official test case before execution.** If a request contradicts the test case rules, scope, deliverables, or evaluation criteria:

1. **NOTIFY the user** — State what contradicts and why
2. **DO NOT execute** — Block the action until clarified
3. **Suggest alternatives** — Propose a compliant approach

This applies to:
- Kilo Code prompts to Claude Code
- User requests to either agent
- Architecture or tech stack decisions
- Scope changes or feature additions

**Example violations to catch:**
- Building features not evaluated (e.g., spending too much time on UI)
- Skipping deliverables (e.g., no architecture doc, no demo video)
- Letting LLM answer without data grounding
- Over-engineering beyond MVP scope
- Using tools not aligned with evaluation criteria

**This is a hard gate. Not a suggestion.**

### Optional Plus Points (Bonus, Not Required)

These are explicitly listed in the test case as bonus. **Do not prioritize these over core deliverables.** Only pursue if core is solid.

- Simple AI agent workflow
- Suggested follow-up questions
- SQL or dataframe tool-calling
- Data quality monitoring
- LLM response evaluation or hallucination checks
- Dockerized setup
- Architecture diagram
- Simple deployment link
- Exportable insight summary
- Security/privacy design (masking, access control assumptions, safe logging)

**Rule:** Core deliverables (4) + evaluation criteria (8) come first. Optional plus points are stretch goals only.

### MVP Interface Tiers (From Test Case)

The PDF defines three quality tiers for the MVP Interface. **Target "Better" as baseline, "Excellent" if time permits.**

| Tier | Requirements |
|------|-------------|
| **Minimum** | Dashboard/analytics page + prompt box + clear output + short explanation of how answer was generated |
| **Better** | + Suggested questions + data/metric references + error handling |
| **Excellent** | + Simple agent that can query data, read summaries, generate charts, suggest follow-up analysis |

### Key Quotes (Evaluation-Relevant)

- *"This is an MVP case study. It is acceptable to make shortcuts as long as you clearly explain the trade-offs and limitations."*
- *"We care about how you think, not just what tools you use."*
- *"A simple but well-scoped and well-explained MVP is better than an overbuilt but unfinished system."*
- *"You must explain why you chose that approach or platform."* (for analytics layer)
- *"You must explain how the LLM accesses the data, how hallucination is reduced, how answers are validated, what happens when a question cannot be answered, and what security/privacy risks should be considered."*

## Verification

**After every feature, Claude MUST verify:**

1. Run data quality checks (schema, nulls, types)
2. Run any associated tests
3. Compare output against spec acceptance criteria
4. Log verification result

Kilo reviews against SPEC.md when user brings feedback. May also spot-check independently.

**Never claim "done" without verification evidence.**

## Session Tracking (MANDATORY)

`HISTORY.md` is the project's audit trail. It must be updated at two points:

1. **Session start** — Read HISTORY.md to understand where we left off
2. **Session end** — Append a new entry under "Session Log" with:
   - What was discussed/decided
   - What files were changed (and why)
   - What's open/next
   - Any blockers or waiting items

**Rules:**
- Every session gets a numbered entry (Session 1, Session 2, ...)
- **Record actual active working time**, not calendar time — track start/end of each working block, note breaks
- Decisions go in the "Decision History" table
- File changes go in the "File Change History" table
- Never delete old entries — only append
- If a session has no meaningful output, log it anyway ("No changes — waiting on X")
- **Session end trigger:** User says "end session", "done for today", or "let's continue tomorrow" → update HISTORY.md before stopping
- **Session start trigger:** New session begins → read HISTORY.md first, then append new session entry

## Research Documentation (MANDATORY)

All research, analysis, and technical decisions MUST be documented in markdown files under `research/`. This includes:
- Dataset analysis and selection rationale
- Tool/library comparisons
- Architecture decisions with trade-offs
- Cost analysis
- Benchmark results

**Structure:**
```
research/
├── INDEX.md          # Master index — skim this first
├── dataset-selection.md
├── tech-stack-comparison.md
├── architecture-decisions.md
└── ... (one file per topic)
```

**Rules:**
- Update `research/INDEX.md` when adding new research files
- Each research file must have: Topic, Date, Status (Draft/Final), Summary, Findings, Recommendation
- Kilo writes research. Claude Code reads it before implementing.
- When revisiting a topic, UPDATE the existing file — don't create a new one
- **Sources are mandatory.** Every claim must cite a credible source with a link. No unsourced claims.
- **Source hierarchy:** Official docs > vendor docs > academic papers > reputable blogs > community posts
- **What counts as credible:** Official documentation (Anthropic, OpenAI, Kaggle), GitHub repos with stars, academic papers, established tech blogs (RealPython, Towards Data Science)
- **What doesn't count:** Stack Overflow answers without context, random Medium posts, AI-generated content without verification

## Timeline (3 Days with AI)

| Day | Focus | Hours | Deliverable |
|-----|-------|-------|-------------|
| **Day 1 (Sat Jun 20)** | Dataset selection, problem framing, architecture, SPEC.md | 4-5 hr | SPEC.md + dataset + architecture draft |
| **Day 2 (Sun Jun 21)** | Data pipeline + cleaning + analytics + LLM interface | 5-6 hr | Working MVP |
| **Day 3 (Mon Jun 22)** | Documentation + demo video + presentation + submission | 5-6 hr | All deliverables submitted |

**Confidence note:** With AI coding, data pipeline + FastAPI + HTML/CSS/JS + LLM interface is a 2-day build. Day 3 is docs + polish. Not 5 days.

**Deadline:** Monday June 22, 2026 (EOD)
