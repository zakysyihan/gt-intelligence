# Bangunindo Analytics MVP — Full Context

> **Copy this entire file to a new chat session.** It contains everything needed to understand the project, the test case, the development approach, and the timeline.

---

## 1. Company & Role

- **Company:** PT Bangunindo Teknusa Jaya
- **Role:** R&D Specialist (AI & Data)
- **Source:** LinkedIn headhunter outreach → HR interview (Jun 11) → Test case received (Jun 18)
- **Interview:** Done on Jun 11, 14:00 WIB. Went well.
- **Status:** Test case received, deadline Monday Jun 22

### Job Description

- Research and explore emerging technologies to support product development
- Design and evaluate solution architecture for new initiatives
- Build proof-of-concept (POC) to test feasibility, performance, and technical risks
- Identify technical risks early and provide effective solutions that are not over-engineered
- Collaborate with engineering, product, and business teams
- Communicate complex technical concepts simply to both technical and non-technical stakeholders

### Qualifications Match

| Requirement | Your Evidence |
|-------------|---------------|
| High interest in technology | Latent Signal, Halaqah AI, continuous learning |
| Technical research | GenAI evaluation frameworks, RAG research at Evermos |
| System design | RAG platform architecture, fraud detection system |
| Build POC quickly | Latent Signal (rapid prototyping), Halaqah AI (full-stack) |
| Data engineering/analytics/science/AI | All roles cover this breadth |
| Security awareness | Azure OpenAI access control, rate limiting |
| Risk identification & trade-offs | Abuse detection system, model evaluation |
| Pragmatic thinking | OR-Tools optimization (2hrs → 10mins), Metabase dashboards |
| Communication | Teaching/mentoring experience |

---

## 2. Test Case — Full Requirements

### Objective

Build a lightweight MVP within 5 days that demonstrates how you research, design, build, validate, and explain a practical LLM-powered analytics solution.

### What to Build

1. **Data Engineering Pipeline**: Ingest, clean, transform a public dataset → analytics-ready data
2. **Analytics Layer**: Answer at least 5 meaningful business questions
3. **LLM-Powered Prompt Interface**: Users ask natural-language questions, get grounded answers
4. **MVP Interface**: Dashboard + prompt box + clear output

### Dataset Options (Choose One)

| Category | Examples |
|----------|----------|
| Retail / Sales / Customer Behavior | Sales performance, customer segmentation, product analysis, revenue trends |
| Customer Churn / Subscription | Churn analysis, retention risk, subscription performance |
| Operational / IoT / Time-Series | Anomaly detection, equipment monitoring, usage trends |

### Deliverables

| Deliverable | Spec |
|-------------|------|
| Git repository | Source code, README, setup instructions, dataset reference, assumptions, how to run, known limitations |
| Architecture document | 3-5 pages: problem statement, architecture diagram, data flow, tech choices, security, what's POC vs production, future improvements |
| Demo video | 7-10 minutes: dataset + problem, data pipeline, analytics output, LLM interface, risks, what you'd improve |
| Presentation | 5 slides: problem + dataset, architecture, analytics insights, LLM interface, trade-offs/risks/next steps |

### Evaluation Criteria

| Area | Weight |
|------|--------|
| Problem framing & business understanding | 10% |
| Data engineering quality | 15% |
| Analytics quality | 15% |
| Architecture & technical design | 15% |
| LLM/prompt interface | 15% |
| Risk, security & hallucination awareness | 10% |
| Pragmatism & anti-over-engineering | 10% |
| Communication & documentation | 10% |

### What They Explicitly Want

- How you **think**, not just what tools you use
- Understand a business problem from data
- Build a simple but reliable data pipeline
- Generate meaningful insights, not just charts
- Design a practical MVP architecture
- Use LLM in a grounded and responsible way
- Identify risks early
- Explain trade-offs clearly
- Avoid over-engineering
- Communicate complex technical concepts simply

### What They Don't Want

- Don't spend too much time making the UI beautiful
- Don't build a full production system
- Don't let LLM answer without grounding from data
- Don't submit only a notebook without MVP interface
- Don't submit only a dashboard without explaining data pipeline
- Don't just call OpenAI API and claim it as AI analytics
- Don't hide limitations or assumptions
- Don't overbuild features that don't support the core objective

---

## 3. Questions for Recruiter (Ask Today)

Only 3 questions not answered in the PDF:

1. **LLM API** — Which provider? Does the company provide an API key, or should I use my own? Budget cap for API calls during the 5-day build?
2. **AI coding tools** — Am I allowed to use AI coding assistants (Claude Code, Cursor, etc.)? This changes my approach significantly.
3. **Video hosting** — "Demo video link" — where should I host it? YouTube (unlisted)? Google Drive? Loom?

---

## 4. Development Approach: Spec-Driven AI-Assisted Development (SDD)

**Not vibe coding. Not spec-agnostic. Spec-first, AI-assisted.**

```
1. SPEC     → Define what to build, why, and how (before any code)
2. RESEARCH → Investigate dataset, tools, trade-offs
3. PLAN     → Architecture, data flow, tech decisions
4. BUILD    → AI-assisted implementation from spec
5. VERIFY   → Test against spec requirements
6. DOCUMENT → Architecture doc, presentation, video
```

**Why this works for a 5-day deadline:**
- Spec prevents scope creep (most common time-waster)
- AI accelerates implementation (3-5x faster than manual)
- Verification catches drift from requirements
- Documentation writes itself from the spec

---

## 5. Tech Stack (Tentative)

| Layer | Tool | Why |
|-------|------|-----|
| Data pipeline | Python (pandas/polars) | Industry standard, fast |
| Data storage | SQLite or DuckDB | Lightweight, no infra needed |
| Analytics | Python notebook + Streamlit | Interactive, presentable |
| LLM | OpenAI API (gpt-4o-mini) | Cost-effective, reliable |
| Interface | Streamlit | Fast to build, clean UI |
| Deployment | Streamlit Cloud | Free, instant |

---

## 6. Timeline (3 Days with AI)

| Day | Focus | Hours | Deliverable |
|-----|-------|-------|-------------|
| **Day 1 (Sat Jun 20)** | Dataset selection, problem framing, architecture, SPEC.md | 4-5 hr | SPEC.md + dataset + architecture draft |
| **Day 2 (Sun Jun 21)** | Data pipeline + cleaning + analytics + LLM interface | 5-6 hr | Working MVP |
| **Day 3 (Mon Jun 22)** | Documentation + demo video + presentation + submission | 5-6 hr | All deliverables submitted |

**Confidence note:** With AI coding, data pipeline + Streamlit + LLM interface is a 2-day build. Day 3 is docs + polish. Not 5 days.

---

## 7. Agent Rules

| Agent | Role | Allowed |
|-------|------|---------|
| **Kilo Code** | Product planning, research, docs, spec writing | Markdown, config files ONLY |
| **Claude Code** | Code implementation, data pipeline, LLM integration | Source code, tests, notebooks |

**Kilo never edits source code.** If Kilo identifies a code improvement, write a prompt for Claude Code instead.

### SDD Cycle

```
┌─────────┐     ┌──────────┐     ┌────────┐     ┌─────────┐
│  SPEC   │────▶│ RESEARCH │────▶│  BUILD │────▶│ VERIFY  │
│ (Kilo)  │     │ (Kilo)   │     │(Claude)│     │(Claude) │
└─────────┘     └──────────┘     └────────┘     └─────────┘
     ▲                                                    │
     └────────────────────────────────────────────────────┘
                    (iterate if verification fails)
```

### Rules

1. **Read SPEC.md before every session.** Never code from memory.
2. **One feature per commit.** Atomic, testable, revertable.
3. **Data quality first.** Every pipeline step must validate output.
4. **LLM grounding is mandatory.** Never let LLM answer freely — always ground in data.
5. **Pragmatism over perfection.** This is an MVP. Shortcuts are fine if documented.
6. **Explain trade-offs.** The evaluation specifically rewards this.
7. **Verify before claiming done.** Run data quality checks, tests, compare against spec.

---

## 8. Folder Structure

```
bangunindo-analytics-mvp/
├── CLAUDE.md            # Claude Code context
├── AGENTS.md            # Kilo Code + Claude Code rules
├── SPEC.md              # Technical specification (source of truth)
├── docs/
│   ├── ARCHITECTURE.md  # 3-5 page architecture doc
│   └── ASSESSMENT.md    # Dataset analysis + business framing
├── data/
│   ├── raw/             # Original dataset
│   ├── cleaned/         # Transformed data
│   └── analytics/       # Analytics-ready data
├── src/
│   ├── pipeline/        # Data ingestion + cleaning + transformation
│   ├── analytics/       # Business questions + insights
│   ├── llm/             # LLM interface + grounding
│   └── app/             # MVP interface (Streamlit)
├── prompts/             # LLM prompt templates
├── notebooks/           # Exploratory analysis
├── tests/               # Data quality + integration tests
└── submission/
    ├── architecture.pdf # 3-5 page architecture doc
    ├── presentation.pdf # 5 slides
    └── demo-video.mp4   # 7-10 min walkthrough
```

---

## 9. Context from Previous Sessions

### Interview (Jun 11)
- Online interview at 14:00 WIB
- Prepared 6 STAR stories (Evermos RAG, Fraud Detection, Latent Signal, etc.)
- Mapped experience to 8 key themes from JD
- Reviewed 3 interviewers' backgrounds
- Result: Went well, test case received Jun 18

### Your Profile Strengths for This Role
- 7+ years ML/AI experience
- Built production RAG platform (Evermos, 50+ users, C-level)
- Built fraud detection systems (99.8% loss reduction)
- Led teams of 9 (Telkom Indonesia)
- Teaching experience (Hacktiv8, Binus Center)
- Solo dev products (Halaqah AI, Latent Signal)
- Azure AI Engineer Associate certified

---

## 10. What to Do First in New Session

1. **Read this file** (CONTEXT.md)
2. **Read SPEC.md** (if exists) or create it
3. **Select dataset** — Kaggle, choose from Retail/Churn/IoT
4. **Write problem framing** — why this dataset, what business problem, assumptions
5. **Design architecture** — data flow, tech decisions, LLM grounding strategy
6. **Start building** — Day 1 scope

**Priority:** Spec → Dataset → Architecture → Build. Don't skip steps.
