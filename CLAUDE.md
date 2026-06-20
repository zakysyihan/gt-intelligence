# CLAUDE.md — GT Intelligence

> Claude Code context for this project.

## Project

GT Intelligence — LLM-powered market intelligence for general trade businesses.
Take-home case study for PT Bangunindo Teknusa Jaya (R&D Specialist role).

**Deadline:** Monday June 22, 2026

## Development Approach

**Spec-Driven Development (SDD) + Ponytail (Anti-Over-Engineering)**

This is NOT vibe coding. Every feature starts with a spec, not a prompt.

### Workflow

1. **SPEC.md** is the source of truth. Read it before any implementation.
2. **Research** — investigate dataset, tools, trade-offs. Write findings to research/.
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
7. **Ponytail YAGNI ladder** — before writing code, ask: does this need to exist?

### Tech Stack

| Layer | Tool | Why |
|-------|------|-----|
| Scraping | Python + httpx + BeautifulSoup | Lightweight, no heavy frameworks |
| Data storage | SQLite | File-based, no server needed |
| Data processing | Pandas | Industry standard, easy to explain |
| LLM | OpenAI API (gpt-4o-mini) | Cost-effective, reliable |
| Interface | Streamlit | Fast to build, clean UI |
| Containerization | Docker + Docker Compose | Single container for all services |
| Deployment | SumoPod VPS (Jakarta) | Single VPS for all services |

## VPS

- **Host:** 43.133.140.154
- **User:** ubuntu
- **SSH key:** ~/.ssh/gt-intelligence
- **Deploy path:** /home/ubuntu/gt-intelligence/
- **OS:** Ubuntu 24.04 LTS
- **Specs:** 2 vCPU, 2GB RAM, 40GB storage
- **Docker:** v29.6.0

### Working on VPS

ALL code runs on VPS, not locally. To run commands on VPS:

```bash
ssh -i ~/.ssh/gt-intelligence ubuntu@43.133.140.154 "cd /home/ubuntu/gt-intelligence && <command>"
```

### First-Time VPS Setup

```bash
ssh -i ~/.ssh/gt-intelligence ubuntu@43.133.140.154 "cd /home/ubuntu/gt-intelligence && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
```

### Deploy Commands

```bash
# Push from local
git add -A && git commit -m "message" && git push origin main

# Pull and restart on VPS
ssh -i ~/.ssh/gt-intelligence ubuntu@43.133.140.154 \
  "cd /home/ubuntu/gt-intelligence && git pull origin main && docker compose up -d --build"
```

## File Structure

```
gt-intelligence/
├── CLAUDE.md          ← this file
├── AGENTS.md          ← agent rules
├── SPEC.md            ← technical specification (source of truth)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── src/               ← source code
│   ├── pipeline/      ← scraping + cleaning + validation
│   ├── analytics/     ← business questions
│   ├── llm/           ← LLM grounding
│   └── app/           ← Streamlit UI
├── data/              ← datasets (gitignored)
├── docs/              ← architecture doc
├── research/          ← research docs
├── prompts/           ← LLM prompt templates
├── tests/             ← validation tests
└── submission/        ← final deliverables
```
