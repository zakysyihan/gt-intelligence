# CLAUDE.md — Bangunindo Analytics MVP

> Claude Code context for this project.

## Project

LLM-Powered Analytics MVP — take-home case study for PT Bangunindo Teknusa Jaya (R&D Specialist role).

**Deadline:** Monday June 22, 2026
**Time remaining:** ~3 days (if starting Saturday)

## Development Approach

**Spec-Driven AI-Assisted Development (SDD)**

This is NOT vibe coding. Every feature starts with a spec, not a prompt.

### Workflow

1. **SPEC.md** is the source of truth. Read it before any implementation.
2. **Research** — investigate dataset, tools, trade-offs. Write findings to docs/.
3. **Plan** — architecture, data flow, tech decisions. Write to SPEC.md.
4. **Build** — implement from spec. One feature at a time.
5. **Verify** — test against spec requirements. Run data quality checks.
6. **Document** — architecture doc, presentation, video.

### Rules

1. **Read SPEC.md before every session.** Never code from memory.
2. **One feature per commit.** Atomic, testable, revertable.
3. **Data quality first.** Every pipeline step must validate output.
4. **LLM grounding is mandatory.** Never let LLM answer freely — always ground in data.
5. **Pragmatism over perfection.** This is an MVP. Shortcuts are fine if documented.
6. **Explain trade-offs.** The evaluation specifically rewards this.

### Tech Stack (Tentative)

| Layer | Tool | Why |
|-------|------|-----|
| Data pipeline | Python (pandas/polars) | Industry standard, fast |
| Data storage | SQLite or DuckDB | Lightweight, no infra needed |
| Analytics | Python notebook + Streamlit | Interactive, presentable |
| LLM | OpenAI API (gpt-4o-mini) | Cost-effective, reliable |
| Interface | Streamlit | Fast to build, clean UI |
| Deployment | Streamlit Cloud or Vercel | Free, instant |

### File Structure

```
bangunindo-analytics-mvp/
├── CLAUDE.md          ← this file
├── AGENTS.md          ← agent rules
├── SPEC.md            ← technical specification
├── src/               ← source code
├── data/              ← datasets
├── docs/              ← architecture, assessment
├── prompts/           ← LLM prompts
├── tests/             ← validation tests
└── submission/        ← final deliverables
```
