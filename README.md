# Bangunindo LLM Analytics MVP — Test Case

**Company:** PT Bangunindo Teknusa Jaya
**Role:** R&D Specialist
**Type:** Take-home case study (5 days)
**Status:** In progress

---

## Test Case Summary

Build a lightweight MVP that demonstrates how you research, design, build, validate, and explain a practical LLM-powered analytics solution.

**Core deliverables:**
1. Data engineering pipeline (raw → clean → analytics-ready)
2. Analytics layer (5+ business questions answered)
3. LLM-powered prompt interface (grounded in data, not hallucinating)
4. MVP interface (dashboard + prompt box)
5. Git repo + Architecture doc (3-5 pages) + Demo video (7-10 min) + Presentation (5 slides)

**Dataset:** Choose from Kaggle (Retail/Sales, Customer Churn, or Operational/IoT)

**Evaluation criteria:**
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

**Timeline:** 5 days from receiving (deadline: Monday June 22)

---

## Questions for Recruiter (Ask Today — Friday)

**Only 3 questions not answered in the PDF:**

1. **LLM API** — Which provider? Does the company provide an API key, or should I use my own? Budget cap for API calls during the 5-day build?

2. **AI coding tools** — Am I allowed to use AI coding assistants (Claude Code, Cursor, etc.)? This changes my approach significantly.

3. **Video hosting** — "Demo video link" — where should I host it? YouTube (unlisted)? Google Drive? Loom? Does the team have a preferred platform?

**Everything else is already in the PDF:**
- Dataset: Kaggle (Retail, Churn, or IoT)
- Tech stack: Flexible (Python, Streamlit, Superset, etc.)
- Deployment: Optional
- Deliverables: Git + architecture doc + demo video + presentation
- Timeline: 5 days from receiving
- Evaluation: 8 criteria, weighted 10-15% each

---

## Folder Structure (Planned)

```
bangunindo-analytics-mvp/
├── CLAUDE.md                 # Claude Code context
├── AGENTS.md                 # Kilo Code + Claude Code rules
├── SPEC.md                   # Technical specification (drives everything)
├── docs/
│   ├── CASE-STUDY.md         # Extracted test case requirements
│   ├── ARCHITECTURE.md       # 3-5 page architecture doc
│   └── ASSESSMENT.md         # Dataset analysis + business framing
├── data/
│   ├── raw/                  # Original dataset
│   ├── cleaned/              # Transformed data
│   └── analytics/            # Analytics-ready data
├── src/
│   ├── pipeline/             # Data ingestion + cleaning + transformation
│   ├── analytics/            # Business questions + insights
│   ├── llm/                  # LLM interface + grounding
│   └── app/                  # MVP interface (Streamlit or similar)
├── prompts/                  # LLM prompt templates
├── notebooks/                # Exploratory analysis
├── tests/                    # Data quality + integration tests
└── submission/
    ├── architecture.pdf      # 3-5 page architecture doc
    ├── presentation.pdf      # 5 slides
    └── demo-video.mp4        # 7-10 min walkthrough
```

---

## Development Approach: Spec-Driven AI-Assisted Development

**Not vibe coding. Not spec-agnostic. Spec-first, AI-assisted.**

The pattern:

```
1. SPEC    → Define what to build, why, and how (before any code)
2. RESEARCH → Investigate dataset, tools, trade-offs
3. PLAN    → Architecture, data flow, tech decisions
4. BUILD   → AI-assisted implementation from spec
5. VERIFY  → Test against spec requirements
6. DOCUMENT → Architecture doc, presentation, video
```

**Why this works for a 5-day deadline:**
- Spec prevents scope creep (most common time-waster)
- AI accelerates implementation (3-5x faster than manual)
- Verification catches drift from requirements
- Documentation writes itself from the spec
