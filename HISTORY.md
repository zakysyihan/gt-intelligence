# HISTORY.md — GT Intelligence (Bangunindo Analytics MVP)

> Auto-maintained by Kilo Code. Tracks every decision, step, and context change.
> Review this file to understand the full project history.

---

## Session 1 — Friday Jun 19, 2026

**Goal:** Project kickoff — context loading, rules, research, SPEC.md
**Active time:** ~4.5 hours | **Calendar time:** 14:00 - 23:34
**Break:** 16:30 - 21:00

#### Timeline

| Time | Activity | Duration |
|------|----------|----------|
| 14:00 - 14:45 | Context loading, PDF extraction (pdftotext + PNG visual), cross-referencing | 45 min |
| 14:45 - 15:45 | AGENTS.md rules: compliance, tiers, quotes, timeline | 1 hr |
| 15:45 - 16:00 | Recruiter question sent + response received (AI tools APPROVED) | 15 min |
| 16:00 - 16:30 | Ponytail integration, session tracking rule, research docs rule | 30 min |
| — | **BREAK** (no activity) | — |
| 21:00 - 22:00 | Research docs: AI dev approaches, dataset selection, marketplace scraping | 1 hr |
| 22:00 - 22:30 | Ponytail plugin installed, SPEC.md v1, directory structure created | 30 min |
| 22:30 - 22:59 | Claude Code prompts prepared, SDD research (GitHub Spec Kit found) | 30 min |
| 22:59 - 23:33 | SPEC.md refinements (problem statement, dataset scope, quick actions) | 35 min |

#### Steps Completed

1. PDF extracted and cross-referenced against context file — no gaps
2. AGENTS.md: test case compliance rule, optional plus points, MVP interface tiers, key quotes, timeline
3. Recruiter question sent: "Apakah saya diperbolehkan menggunakan AI coding assistant?" → APPROVED
4. Ponytail plugin installed in Claude Code session
5. 3 research files created with credible sources (AI dev approaches, dataset selection, marketplace scraping)
6. SPEC.md created (13 sections)
7. Project directory structure created
8. SDD authoritative source found: GitHub Spec Kit (114k stars)
9. History.md tracking system created

#### Decisions Made

| # | Decision | Rationale | Status |
|---|----------|-----------|--------|
| 1 | Use SDD-inspired workflow | GitHub Spec Kit methodology adapted for 3-day sprint | Active |
| 2 | Test case = authoritative source | Prevents drift from requirements | Enforced |
| 3 | Ponytail YAGNI principles | Proven tool, aligns with "anti-over-engineering" evaluation (10%) | Applied |
| 4 | 3-day compressed timeline | AI coding accelerates 3-5x | Agreed |
| 5 | Kilo = planning, Claude = code | Clear separation of concerns | Active |
| 6 | AI coding tools approved by recruiter | Claude Code, Cursor, Copilot all allowed | Confirmed |

---

## Session 2 — Saturday Jun 20, 2026

**Goal:** Build data pipeline + UI + LLM research + deploy to VPS
**Active time:** ~8 hours | **Calendar time:** 12:40 - 22:54
**Deadline:** Mon Jun 22, 09:30 WIB | **Hours remaining:** ~10h

#### Timeline (Git timestamps as source of truth)

| Time | Activity | Actor |
|------|----------|-------|
| 12:40 - 12:51 | Business questions refinement → SPEC.md Section 2 rewrite | Kilo |
| 12:51 - 14:00 | SPEC.md full rewrite: business context, 5 analysis categories, 14 fields, MVP interface | Kilo |
| 14:00 - 14:46 | WrenAI decision, GitHub repo created (`gt-intelligence`), initial commit (14:46) | Kilo |
| 14:46 - 16:15 | CLAUDE.md updated, data pipeline prompt written, VPS context added | Kilo |
| 16:15 - 16:18 | 3 commits: CLAUDE.md VPS info, deploy commands, working commands | Kilo |
| 16:18 - 17:16 | VPS provisioned (SumoPod Jakarta), SSH keys set up, Docker installed, repo cloned | Kilo |
| 17:16 | WrenAI + Chainlit decision committed (replaces Streamlit + Vanna) | Kilo |
| 18:25 | SPEC.md fix: stale Streamlit reference, dashboard clarified as live SQL | Kilo |
| 18:35 | Parallel task rules added to AGENTS.md | Kilo |
| ~18:00 | **Claude 1 started:** Data pipeline (scraper → cleaning → validation → SQLite) | Claude 1 |
| 18:47 | **Claude 1 committed:** 672 real Tokopedia products via tokopaedi, 7/7 checks passed | Claude 1 |
| ~19:00 | **Claude 2 started:** WrenAI agent + Chainlit interface | Claude 2 |
| ~20:00 | **Claude 3 started:** Deep LLM research (benchmarks, evals, model comparison) | Claude 3 |
| 20:52 | Claude 3 committed: LLM selection research (first version) | Claude 3 |
| 20:56 | Claude 3 committed: Deep LLM research (tiered strategy, 8 sources) | Claude 3 |
| 21:03 | Claude 2 committed: WrenAI agent + Chainlit interface (app.py, agent.py, charts.py) | Claude 2 |
| 22:12 | Claude 2 fixed: cl.Dataframe requires pandas DataFrame | Claude 2 |
| 22:15 | Claude 3 committed: deep research with BIRD-Interact, GDPval-AA, TokenMix | Claude 3 |
| 22:17 | Kilo: Session recap committed, all 3 Claude outputs validated | Kilo |
| 22:19 | Claude 2 fixed: charts must return plotly.graph_objects.Figure | Claude 2 |
| 22:30 - 22:48 | Kilo: Playwright screenshots taken, UI validated against SPEC | Kilo |
| 22:48 | Session close committed, Streamlit rewrite planned for tomorrow | Kilo |

#### Parallel Agent Results

| Agent | Task | Output | Time | Commits |
|-------|------|--------|------|---------|
| **Claude 1** | Data pipeline (scraper → cleaning → validation → SQLite) | 672 real Tokopedia products, 7/7 checks passed | ~1.5h | 64613b2 |
| **Claude 2** | WrenAI agent + Chainlit UI + Docker | app.py (298L), agent.py (406L), charts.py (244L), Dockerfile, docker-compose.yml | ~3h | 3214e1f, 91128f3, ee1a8ae |
| **Claude 3** | Deep LLM research (BIRD-Interact, GDPval-AA, TokenMix) | 297-line research, updated llm_parser.py, updated SPEC.md | ~1.5h | 7e6e2da, 5592ec8, ec7ae0e |
| **Kilo** | Coordination, validation, SPEC updates, docs, screenshots | SPEC.md, HISTORY.md, research/, AGENTS.md, CLAUDE.md | ~5h | 11 commits |

#### Data Pipeline (Claude 1)

- **Scraper:** `tokopaedi` library (mobile API spoofing, bypasses Akamai)
- **Pipeline:** 6 steps — Scrape → Stage → Clean → LLM Parse → Validate → SQLite
- **Results:** 672 products, 3 subcategories (candy 167, chocolate 177, snacks 328)
- **Quality:** 0 nulls in critical fields, all Java Island, avg price Rp 44,743, avg rating 4.41
- **Missing:** `sweets` subcategory (Tokopedia didn't return), `shop_rating` (API doesn't expose)
- **Parsing:** flavor/weight/variant extracted from titles (40-65% null, best-effort)

#### UI Agent (Claude 2)

- **Stack:** Chainlit + Plotly + OpenAI (via SumoPod DeepSeek)
- **Files:** app.py (298L), agent.py (406L), charts.py (244L), mdl_manifest.py (193L), data_loader.py (60L)
- **Deployed:** http://43.133.140.154:8000 (Docker container running)
- **Validated:** Playwright screenshots — dashboard loads, charts render, agent answers questions with SQL + insights
- **Issue:** Chainlit is chat-first; SPEC needs dashboard-first → Streamlit rewrite planned

#### LLM Research (Claude 3)

- **Key finding:** Our schema is trivial (1 table, 14 columns). All models score 94%+ on simple SQL.
- **BIRD-Interact results:** DeepSeek 4.83% agentic SR vs GPT-5 17.00% — but gap measures complex SQL, not our use case
- **GDPval-AA v2:** DeepSeek V4 Flash Elo 1191 (rank 17) — above human baseline
- **WrenAI compensates:** dry-plan validates SQL, --guided mode forces workflow, MDL constrains view
- **Recommendation:** DeepSeek V4 Flash (free) → O3-Mini ($0.06) → Gemini 2.5 Pro ($0.04)
- **Sources:** BIRD-Interact paper, GDPval-AA leaderboard, TokenMix, WrenAI docs, DeepSeek API, SLM-SQL paper

#### UI Validation (Playwright Screenshots)

| Element | Status | Evidence |
|---------|--------|----------|
| Dashboard: 3 charts (price, demand, geo) | ✅ | Screenshots confirm rendering |
| Metric cards: 4 metrics | ✅ | Total Produk 672, Top Subcategory snacks 4.1M, Avg Price Rp 44,743, Java 672 |
| Quick action buttons: 6 | ✅ | All 6 visible and clickable |
| Chat input | ✅ | "Type your message here..." |
| Agent response: SQL + table + insight | ✅ | "Sinyal Sukses Produk" tested — SQL generated, data returned, insight in Indonesian |
| SumoPod DeepSeek working | ✅ | Logs show ai.sumopod.com 200 OK |

#### Decisions Made

| # | Decision | Rationale | Status |
|---|----------|-----------|--------|
| 7 | Scrape Indonesian marketplace (not Kaggle) | User domain expertise in demand forecasting | Applied |
| 8 | Tokopedia + Shopee primary, BPS fallback | 3-layer data source strategy | Applied |
| 9 | Drop competition analysis category | General trade = product creator, not seller | Applied |
| 10 | Add product spec parsing (flavor/weight/variant) | Product dev team needs detailed specs | Applied |
| 11 | Business questions drive data fields | Prevents scope creep in scraping | Applied |
| 12 | Revenue proxy = price × demand, NOT profit | Cost data not available from scraping | Documented |
| 13 | SQLite for MVP, PostgreSQL for production | MVP scope, 1000 rows, zero setup | Applied |
| 14 | Dockerize on single VPS | Bonus point, simple deployment | Applied |
| 15 | Explicit staging layer in pipeline | Data engineering best practice, re-runnable | Applied |
| 16 | SumoPod Jakarta 2vCPU/2GB/40GB | Close to data source, cheap, sufficient | Applied |
| 17 | SSH key-based auth, no passwords | Security — agents never handle passwords | Applied |
| 18 | Pipeline runs on VPS, not local | Don't mess up local laptop | Applied |
| 19 | WrenAI + Chainlit (replaced Streamlit + Vanna) | MDL semantic layer for business-aware LLM | Applied |
| 20 | Drop YAML dashboard customization | Test case: "not over-engineering" (10% weight) | Applied |
| 21 | Dashboard = live SQL, fixed layout | Matches PDF: "one dashboard + one prompt box" | Applied |
| 22 | 6 quick actions mapped to analysis categories | Business team clicks, no code needed | Applied |
| 23 | Tiered LLM: DeepSeek for parser + agent, fallback O3-Mini | Free on SumoPod, simple schema compensates | Applied |
| 24 | Branch rules: every Claude session on feature branch | Prevents conflicts in parallel work | Applied |
| 25 | **UI Rewrite: Chainlit → Streamlit** | Chainlit is chat-first; SPEC needs dashboard-first with tabs + multi-chat | Planned (Day 2) |

#### Open Items (Next: Day 2)

- [ ] **UI Rewrite: Chainlit → Streamlit** — tab-based (Dashboard | Analyst Agent), multi-chat sessions
- [ ] Analytics scripts (5 business questions answered with data)
- [ ] .env.example update (SumoPod DeepSeek, not OpenAI)
- [ ] Integration testing (end-to-end: question → SQL → answer → chart)
- [ ] Architecture doc (3-5 pages, required deliverable)
- [ ] README.md (setup instructions)
- [ ] Presentation (5 slides, required deliverable)
- [ ] Demo video (7-10 min, required deliverable)

---

## Decision History

| # | Date | Decision | Made By | Rationale |
|---|------|----------|---------|-----------|
| 1 | Jun 19 | Use SDD-inspired workflow | Kilo | Prevents scope creep, enables verification |
| 2 | Jun 19 | Test case = authoritative source | Kilo | Prevents drift from requirements |
| 3 | Jun 19 | Use ponytail YAGNI principles | User | Proven tool, aligns with evaluation criteria |
| 4 | Jun 19 | 3-day compressed timeline | User | AI coding acceleration |
| 5 | Jun 19 | Kilo = planning, Claude = code | Kilo | Clear separation of concerns |
| 6 | Jun 19 | AI coding tools approved | Recruiter | Claude Code, Cursor, Copilot all allowed |
| 7 | Jun 19 | Scrape marketplace (not Kaggle) | User | Domain expertise, demonstrates data engineering |
| 8 | Jun 19 | Tokopedia + Shopee primary | Kilo | Largest Indonesian marketplace |
| 9 | Jun 20 | WrenAI + Chainlit over Streamlit + Vanna | User | MDL semantic layer, agent-native chat |
| 10 | Jun 20 | Tiered LLM: DeepSeek free, O3-Mini fallback | Kilo | Free, simple schema compensates |
| 11 | Jun 20 | Branch rules for parallel Claude sessions | Kilo | Prevents conflicts |
| 12 | Jun 20 | Streamlit rewrite for dashboard-first UX | User | Chainlit is chat-first, SPEC needs dashboard-first |

---

## File Change History

| Date | Time | File | Change | By |
|------|------|------|--------|-----|
| Jun 19 | 14:00-23:33 | AGENTS.md | Rules: compliance, tiers, ponytail, tracking, research, security | Kilo |
| Jun 19 | 14:00-23:33 | SPEC.md | Created, refined, problem statement, dataset scope | Kilo |
| Jun 19 | 21:00 | research/ai-development-approaches.md | 6 approaches researched | Kilo |
| Jun 19 | 21:30 | research/dataset-selection.md | 5 datasets evaluated | Kilo |
| Jun 19 | 22:00 | research/marketplace-scraping.md | 4 sources evaluated | Kilo |
| Jun 19 | 22:30 | HISTORY.md | Created tracking file | Kilo |
| Jun 20 | 12:40 | SPEC.md | Full rewrite — business context, analysis categories, 14 fields | Kilo |
| Jun 20 | 14:46 | CLAUDE.md | VPS info, tech stack, deploy commands | Kilo |
| Jun 20 | 14:46 | .gitignore, .env.example, README.md | Project config | Kilo |
| Jun 20 | 17:16 | SPEC.md | WrenAI + Chainlit tech stack, file structure, MVP vs production | Kilo |
| Jun 20 | 18:25 | SPEC.md | Fixed Streamlit reference, dashboard clarified | Kilo |
| Jun 20 | 18:35 | AGENTS.md | Parallel task rules added | Kilo |
| Jun 20 | 18:47 | src/pipeline/*.py | Pipeline: scraper, cleaner, validator, run_pipeline | Claude 1 |
| Jun 20 | 18:47 | requirements.txt | tokopaedi, httpx, pandas, pytest | Claude 1 |
| Jun 20 | 20:52 | research/llm-selection.md | LLM selection (first version) | Claude 3 |
| Jun 20 | 20:56 | research/llm-selection.md | Deep research tiered strategy | Claude 3 |
| Jun 20 | 21:03 | src/app/app.py, src/llm/*.py | Chainlit app, agent, charts, MDL | Claude 2 |
| Jun 20 | 21:03 | Dockerfile, docker-compose.yml | Docker setup | Claude 2 |
| Jun 20 | 22:12 | src/app/app.py | Fix: cl.Dataframe → pandas DataFrame | Claude 2 |
| Jun 20 | 22:15 | research/llm-selection.md, src/pipeline/llm_parser.py, SPEC.md | BIRD-Interact benchmarks, improved parser | Claude 3 |
| Jun 20 | 22:19 | src/app/charts.py | Fix: charts must return plotly.graph_objects.Figure | Claude 2 |

---

## Session 3 — Sunday Jun 21, 2026 (Day 2)

**Goal:** UI rewrite, analytics, architecture doc, prepare for submission
**Active time:** 0 hours | **Calendar time:** 05:19 - ongoing
**Deadline:** Mon Jun 22, 09:30 WIB | **Hours remaining:** ~18h (minus sleep)

#### Timeline

| Time | Activity | Actor |
|------|----------|-------|
| 05:19 | Session start, HISTORY.md read | Kilo |

#### Open Items (from Session 2)

| Priority | Task | Estimated Hours |
|----------|------|----------------|
| **P0** | UI Rewrite: Chainlit → Streamlit (tab-based, multi-chat) | 3-4h |
| **P0** | Analytics scripts (5 business questions answered with data) | 1-2h |
| **P1** | Architecture doc (3-5 pages, required) | 1-2h |
| **P1** | Integration testing (end-to-end) | 1h |
| **P1** | .env.example update (SumoPod DeepSeek) | 10 min |
| **P2** | README.md | 30 min |
| **P2** | Presentation (5 slides, required) | 1h |
| **P3** | Demo video (7-10 min, required) | 1-2h |

---

### Interview (Jun 11)
- Online interview at 14:00 WIB
- Prepared 6 STAR stories (Evermos RAG, Fraud Detection, Latent Signal, etc.)
- Mapped experience to 8 key themes from JD
- Reviewed 3 interviewers' backgrounds
- Result: Went well, test case received Jun 18

### Profile Strengths for This Role
- 7+ years ML/AI experience
- Built production RAG platform (Evermos, 50+ users, C-level)
- Built fraud detection systems (99.8% loss reduction)
- Led teams of 9 (Telkom Indonesia)
- Teaching experience (Hacktiv8, Binus Center)
- Solo dev products (Halaqah AI, Latent Signal)
- Azure AI Engineer Associate certified
