# HISTORY.md — Bangunindo Analytics MVP

> Auto-maintained by Kilo Code. Tracks every decision, step, and context change.
> Review this file to understand the full project history.

---

### Session 2 — Saturday Jun 20, 2026 (Day 1)

**Goal:** Build everything — data pipeline, UI agent, LLM research, VPS deployment
**Active time:** ~6 hours (12:40 - 22:15) | **Deadline:** Mon Jun 22, 09:30 WIB
**Hours remaining:** ~22h

#### Timeline (Active Working Periods)

| Time | Activity | Duration |
|------|----------|----------|
| 12:40 - 12:51 | Business questions refinement, SPEC.md update | 11 min |
| 12:51 - 14:00 | SPEC.md rewrite (full), dataset scope, analysis categories | 1h 9m |
| 14:00 - 15:00 | WrenAI decision, Chainlit UI architecture, quick actions | 1h |
| 15:00 - 16:00 | GitHub repo (gt-intelligence), VPS provisioning (SumoPod Jakarta) | 1h |
| 16:00 - 17:00 | VPS setup (Docker, SSH keys, GitHub auth, repo clone) | 1h |
| 17:00 - 18:00 | Claude 1 terminal: data pipeline + Tokopedia scraping (672 products) | 1h (Claude) |
| 18:00 - 19:00 | Claude 2 terminal: WrenAI + Chainlit interface build | 1h (Claude) |
| 19:00 - 20:00 | Claude 3 terminal: deep LLM research (BIRD-Interact, GDPval-AA) | 1h (Claude) |
| 20:00 - 22:15 | Kilo: validate Claude outputs, coordinate, update docs | 2h 15m |

#### Parallel Agent Work

| Agent | Task | Output | Status |
|-------|------|--------|--------|
| **Claude 1** | Data pipeline (scraper → cleaning → validation → SQLite) | 672 real Tokopedia products, 7/7 checks passed | ✅ Done |
| **Claude 2** | WrenAI agent + Chainlit UI | app.py, agent.py, charts.py, docker-compose.yml | ✅ Done |
| **Claude 3** | Deep LLM research (benchmarks, evals, model comparison) | 297-line research with 8 sources | ✅ Done |
| **Kilo** | Coordination, validation, SPEC updates, docs | SPEC.md, HISTORY.md, research/INDEX.md | ✅ Done |

#### Decisions Made

| # | Decision | Rationale | Status |
|---|----------|-----------|--------|
| 9-25 | (see Session 3 for pipeline decisions) | | Applied |
| 26 | WrenAI + Chainlit over Streamlit + Vanna | MDL semantic layer for business-aware LLM | Applied |
| 27 | Drop YAML dashboard customization | Test case says "not over-engineering" (10% weight) | Applied |
| 28 | Dashboard = live SQL, fixed layout | Matches PDF: "one dashboard + one prompt box" | Applied |
| 29 | 6 quick actions mapped to analysis categories | Business team clicks, no code needed | Applied |
| 30 | Tiered LLM: DeepSeek for parser + agent, fallback O3-Mini | Free on SumoPod, simple schema compensates | Applied |
| 31 | Branch rules: every Claude session on feature branch | Prevents conflicts in parallel work | Applied |

#### Key Findings (Claude 3 LLM Research)

- **Our schema is trivial:** 1 table, 14 columns. All models score 94%+ on simple SQL (TokenMix)
- **WrenAI compensates for weaker LLMs:** dry-plan validates SQL, --guided mode forces workflow, MDL constrains the view
- **DeepSeek's BIRD-Interact weakness is real but irrelevant:** The gap measures complex SQL (multi-table JOINs). We have 1 table.
- **Recommendation:** Try DeepSeek V4 Flash (free) → O3-Mini ($0.06) → Gemini 2.5 Pro ($0.04) if needed
- **SLM-SQL paper:** Fine-tuned 1.5B model matches Claude Opus on standalone SQL — but standalone ≠ agentic

#### Steps Completed

1. **SPEC.md Rewritten** — Full rewrite with detailed business context
   - Section 1: What this MVP is (general trade business, product dev team persona)
   - Section 2: 5 analysis categories with business questions mapping to data fields
   - Section 3: Dataset scoped (food & beverage, Java Island, 14 fields including parsed flavor/weight/variant)
   - Section 5: Product spec parsing rules for flavor/weight/variant from titles

2. **Business Questions Refined**
   - Dropped "Competition" category (not relevant for product creator role)
   - Added "Product Success Signals" category (flavor, weight, variant)
   - Every question maps to data fields → maps to scraping

3. **Dataset Fields Updated**
   - Added timestamp (for trend analysis), flavor, weight, variant (parsed from title)
   - All 14 fields mapped to analysis categories

4. **Data Pipeline Updated**
   - Made staging layer explicit (Raw → Staging → Transformation → Curated)
   - Added validation rules table (schema, type, null, range, dedup, geography, row count)

5. **MVP vs Production Scope Added**
   - Explicit table documenting what's MVP vs what's production
   - SQLite for MVP, PostgreSQL for production
   - Single VPS + Docker Compose for deployment
   - Test case compliance: "what's POC vs what's not production-ready"

6. **Tech Stack Updated**
   - Added Docker + Docker Compose, VPS deployment
   - Added MVP vs Production table (8 concerns documented)

7. **File Structure Updated**
   - Added Dockerfile, docker-compose.yml, requirements.txt, .env.example
   - Added data/staging/ directory

8. **Database Selection Researched** (research/database-selection.md)
   - SQLite recommended for MVP (zero setup, file-based, 1000 rows)
   - PostgreSQL documented as production choice

9. **GitHub Repo Created**
   - Repo: https://github.com/zakysyihan/gt-intelligence (private)
   - .gitignore excludes data/, .env, __pycache__
   - Initial commit: 23 files

10. **VPS Provisioned (SumoPod)**
    - Host: 43.133.140.154
    - User: ubuntu
    - Specs: 2 vCPU, 2GB RAM, 40GB storage, Ubuntu 24.04
    - Region: Jakarta
    - SSH key: ~/.ssh/gt-intelligence (key-based auth, no passwords)
    - Docker installed (v29.6.0)
    - GitHub SSH key added to VPS (for git clone)
    - Repo cloned at /home/ubuntu/gt-intelligence/

11. **CLAUDE.md Updated**
    - Added VPS connection details and deploy commands
    - Updated tech stack to match SPEC.md
    - Updated file structure

12. **Security Rule Added**
    - NEVER know, handle, or request VPS passwords
    - SSH key-based auth only
    - User handles password auth off-screen

13. **Data Pipeline Prompt Updated**
    - Single prompt covers full pipeline (scraper → staging → cleaning → validation → SQLite)
    - Removed old multi-prompt file (day1-prompts.md)

#### Decisions Made

| # | Decision | Rationale | Status |
|---|----------|-----------|--------|
| 9 | Drop competition analysis category | General trade = product creator, not seller | Applied |
| 10 | Add product spec parsing (flavor/weight/variant) | Product dev team needs detailed specs | Applied |
| 11 | Business questions drive data fields | Prevents scope creep in scraping | Applied |
| 12 | Revenue proxy = price × demand, NOT profit | Cost data not available from scraping | Documented |
| 13 | SQLite for MVP, PostgreSQL for production | MVP scope, 1000 rows, zero setup | Applied |
| 14 | Dockerize all services on single VPS | Bonus point, simple deployment | Planned |
| 15 | Explicit staging layer in pipeline | Data engineering best practice, re-runnable | Applied |
| 16 | VPS: SumoPod Jakarta, 2vCPU/2GB/40GB | Close to data source, cheap, sufficient for MVP | Applied |
| 17 | SSH key-based auth, no passwords | Security — agents never handle passwords | Applied |
| 18 | Pipeline runs on VPS, not local | Don't mess up local laptop | Applied |

---

### Session 3 — Saturday Jun 20, 2026 (Day 1 continued)

**Goal:** Build full data pipeline — scraper, cleaner, validator, SQLite curated layer
**Active time:** ~3 hours (15:55 - 19:00)

#### Steps Completed

1. **Pipeline Architecture Built**
   - `src/pipeline/scraper.py` — Data collection (tokopaedi mobile API)
   - `src/pipeline/cleaner.py` — Cleaning, normalization, spec parsing, computed columns
   - `src/pipeline/validator.py` — 7 data quality checks (schema, types, nulls, ranges, dedup, geography, row count)
   - `src/pipeline/run_pipeline.py` — Main orchestrator (5 steps: scrape → stage → clean → validate → SQLite)
   - `requirements.txt` — tokopaedi, httpx, pandas, pytest

2. **Tokopedia Scraping — Extensive Exploration (FAILED approaches)**

   We tried EVERY reasonable approach to scrape Tokopedia:

   | Approach | Result | Why Failed |
   |----------|--------|------------|
   | Direct GraphQL API (httpx) | Empty results (0 products) | API needs browser cookies; query works but returns no data |
   | curl_cffi TLS impersonation | HTTP/2 stream killed | Akamai detects and kills the connection |
   | `X-TKPD-AKAMAI: pdpGetLayout` header | Connection killed | Header triggers Akamai bot detection |
   | Playwright headless browser | JS challenge blocks rendering | Akamai serves challenge page, products never load |
   | Obscura (stealth headless) | Same as Playwright | Akamai JS challenge still blocks |
   | Shopee API | 403 Forbidden | Shopee has its own anti-bot (DataDome) |
   | Blibli backend API | 403 Forbidden | Blibli also has anti-bot protection |
   | Bukalapak | 404/406 | Endpoint deprecated or protected |

3. **Deep Research Phase**
   - Installed `curl_cffi` on VPS — tested all 11 impersonation modes (chrome, safari, edge variants)
   - Installed Playwright + Chromium on VPS — tested with stealth mode
   - Installed Obscura v0.1.8 (Rust headless browser) — tested CDP server mode
   - Tested GraphQL introspection — disabled by Tokopedia
   - Tested every GraphQL query format variation — found that `name`, `url`, `imageUrl`, `originalPrice`, `stock`, `condition`, `rating`, `shop{name city}` work, but `price`, `stats`, `category` fields cause schema errors
   - Researched `nodriver`, `undetected-chromedriver`, `wafer` (Akamai solver), `hyper-sdk` (commercial)
   - Found `tokopaedi` library on PyPI — mobile API spoofing approach

4. **BREAKTHROUGH: tokopaedi library**
   - `pip install tokopaedi` — 0.2.3 (Aug 2025)
   - Uses mobile user-agent spoofing to bypass Akamai's heaviest protections
   - Provides `search(keyword, max_result, debug)` → returns `ProductData` objects
   - Fields: product_name, price, rating, sold_count, shop.name, shop.city, category, url, weight, etc.
   - Successfully scraped 672 real Tokopedia products from Java Island sellers

5. **Pipeline Verified on VPS**
   - All 7/7 validation checks PASSED
   - 672 real products in SQLite database
   - 3 subcategories: candy (167), chocolate (177), snacks (328)
   - Avg price: Rp 44,743, Avg rating: 4.41
   - 374 unique shops across Java Island
   - Top cities: Surabaya (103), Kab. Bandung (72), Jakarta Barat (58)
   - Tested Shopee API: 403 Forbidden
   - Installed Playwright + Chromium on VPS: ERR_HTTP2_PROTOCOL_ERROR (detected)
   - **Conclusion:** Both marketplaces have Akamai bot protection blocking server-side scraping

3. **Synthetic Data Fallback Implemented**
   - Generates 1,000 realistic products based on Indonesian marketplace patterns
   - Real brand names (Chitato, SilverQueen, Mentos, etc.)
   - Real price ranges per subcategory
   - Real Java Island city distribution
   - Log-normal price distribution, Pareto sold count distribution
   - **Trade-off documented** in code and architecture

4. **Bug Fixes**
   - Fixed `normalize_sold_count` parameter name bug (`s` → `sold`)
   - Extended Java Island location list to include all major Java cities

5. **Pipeline Verified on VPS**
   - All 7/7 validation checks PASSED
   - 1,000 products in SQLite database
   - 3 subcategories: candy (300), chocolate (250), snacks (450)
   - Avg price: Rp 18,288, Avg rating: 4.01
   - 819 unique shops across Java Island
   - SQLite indexes on subcategory and shop_location

#### Decisions Made

| # | Decision | Rationale | Status |
|---|----------|-----------|--------|
| 19 | Use synthetic data as fallback | Tokopedia/Shopee have Akamai bot protection blocking server scraping | Superseded |
| 20 | Document scraping limitation explicitly | Test case rewards transparency about trade-offs | Applied |
| 21 | Install Playwright on VPS | Attempt headless browser scraping (proved insufficient) | Applied |
| 22 | Extend Java Island city list | Synthetic data uses city names, not just province names | Applied |
| 23 | Use tokopaedi library for Tokopedia | Mobile API spoofing bypasses Akamai; actively maintained PyPI package | Applied ✓ |
| 24 | Install Obscura v0.1.8 on VPS | Stealth headless browser — still blocked by Akamai JS challenge | Applied (failed) |
| 25 | Install curl_cffi on VPS | TLS fingerprint impersonation — HTTP/2 stream killed by Akamai | Applied (failed) |

#### Files Changed

| File | Change |
|------|--------|
| src/pipeline/scraper.py | Built: API scraper + synthetic data generator |
| src/pipeline/cleaner.py | Built: cleaning, normalization, spec parsing, computed columns |
| src/pipeline/validator.py | Built: 7 data quality checks |
| src/pipeline/run_pipeline.py | Built: 5-step pipeline orchestrator |
| requirements.txt | Created: httpx, pandas, pytest |
| src/__init__.py | Created: Python package init |
| src/pipeline/__init__.py | Created: Python package init |

#### VPS Deployment

- All files deployed to `/home/ubuntu/gt-intelligence/`
- Dependencies installed: httpx, pandas, pytest, playwright
- Chromium browser installed for Playwright
- Pipeline runs successfully: `python3 -m src.pipeline.run_pipeline`
- Output files verified: raw JSON, staging backup, cleaned CSV, SQLite DB

#### Open Items

- [x] Data pipeline built and verified (672 products)
- [x] WrenAI + Chainlit interface built
- [x] Deep LLM research completed
- [ ] Analytics scripts (5 business questions) — needed
- [ ] Dockerfile (docker-compose.yml exists, Dockerfile missing) — needed
- [ ] mdl/ directory (MDL configuration) — needed
- [ ] .env.example — needed
- [ ] Integration testing (WrenAI + real data) — needed
- [ ] Architecture doc (3-5 pages) — needed
- [ ] README.md — needed
- [ ] Presentation (5 slides) — needed
- [ ] Demo video (7-10 min) — needed

---

## Session Log

### Session 1 — Friday Jun 19, 2026

**Goal:** Project kickoff — context loading, rule setup, approach definition, dataset decision
**Active time:** ~4.5 hours | **Calendar time:** 14:00 - 23:34

#### Timeline (Active Working Periods)

| Time | Activity | Duration |
|------|----------|----------|
| 14:00 - 14:45 | Context loading, PDF extraction, cross-referencing | 45 min |
| 14:45 - 15:45 | AGENTS.md rules (compliance, tiers, quotes, timeline) | 1 hr |
| 15:45 - 16:00 | Recruiter question + response received | 15 min |
| 16:00 - 16:30 | Ponytail integration, session tracking rule | 30 min |
| — | **BREAK** (no activity) | — |
| 21:00 - 22:00 | Research docs (AI approaches, dataset selection) | 1 hr |
| 22:00 - 22:30 | Ponytail plugin install, SPEC.md v1, directory structure | 30 min |
| 22:30 - 22:59 | Claude Code prompts, SDD research (GitHub Spec Kit) | 30 min |
| 22:59 - 23:33 | SPEC.md refinements (problem statement, dataset scope) | 35 min |

#### Steps Completed

1. **Context Loading**
   - Read `README.md`, `CLAUDE.md`, `AGENTS.md` (existing files)
   - Loaded `context_from_other_chat_session.md` — full project context from previous chat
   - Extracted PDF via `pdftotext` + visual inspection (4 pages converted to PNG)
   - Cross-referenced PDF against context file — no gaps found

2. **Test Case Compliance Rule Added** (AGENTS.md:70-95)
   - Every request must be checked against the official test case before execution
   - Contradictions get notified and blocked until clarified
   - Hard gate, not a suggestion

3. **Optional Plus Points Added** (AGENTS.md:97-112)
   - 10 bonus items from the PDF
   - Rule: core deliverables first, stretch goals only if solid

4. **MVP Interface Tiers Added** (AGENTS.md:114-122)
   - Minimum / Better / Excellent levels from the PDF
   - Target: "Better" baseline, "Excellent" if time permits

5. **Key Quotes Added** (AGENTS.md:124-130)
   - 5 exact quotes from PDF relevant to evaluation scoring

6. **Timeline Updated** (AGENTS.md:143-153)
   - 3-day compressed timeline with AI (not 5 days)
   - Deadline: Monday June 22, 2026 (EOD)

7. **Recruiter Question Prepared**
   - Question: "Apakah saya diperbolehkan menggunakan AI coding assistant (seperti Claude Code, Cursor, GitHub Copilot) selama pengerjaan test case?"
   - Sent to panel

8. **Recruiter Response Received** (15:45)
   - AI coding tools APPROVED — Claude Code, Cursor, Copilot all allowed

9. **Ponytail Integration** (AGENTS.md:47-86)
   - Installed ponytail anti-over-engineering ruleset (manual merge for Kilo Code)
   - All code agents must follow YAGNI ladder
   - Verified: no contradictions with workflow

10. **Session Tracking Rule Added** (AGENTS.md)
    - HISTORY.md must be updated at session start and end
    - Every session gets a numbered entry

11. **Research Documentation Rule Added** (AGENTS.md)
    - All research documented in `research/` folder
    - INDEX.md maintained as master index

12. **Research: AI Development Approaches** (research/ai-development-approaches.md)
    - Researched 6 approaches: SDD, Ponytail, Explore→Plan→Implement, Verification-Driven, Interview-First, Writer/Reviewer
    - Recommended hybrid: SDD + Ponytail + Verification-Driven

13. **Research: Dataset Selection** (research/dataset-selection.md)
    - Evaluated 5 datasets across 3 categories
    - Recommended: Brazilian E-Commerce (Olist)
    - Rationale: rich data, real business, 5+ questions, good for LLM grounding

14. **Context File Moved**
    - `context_from_other_chat_session.md` → `docs/archived/context-from-previous-sessions.md`
    - Content now absorbed into AGENTS.md, HISTORY.md, and research files

15. **Ponytail Plugin Installation**
    - Commands provided: `/plugin marketplace add DietrichGebert/ponytail` then `/plugin install ponytail@ponytail`
    - To be run in Claude Code session
    - AGENTS.md updated with installation instructions

16. **Dataset Decision Changed: Kaggle → Scraping**
    - Original recommendation: Brazilian E-Commerce (Olist) from Kaggle
    - New decision: Scrape Indonesian marketplace data (Tokopedia primary)
    - Rationale: User has 6 months domain expertise in demand forecasting
    - Demonstrates real data engineering (scraping pipeline)
    - Fits "Retail / Sales / Customer Behavior" category
    - BPS (Statistics Indonesia) as fallback

17. **Research: Marketplace Scraping** (research/marketplace-scraping.md)
    - Evaluated 4 sources: Tokopedia, Shopee, Bukalapak, BPS
    - Recommended: Tokopedia GraphQL API primary, BPS fallback
    - Time estimate: 1-2 hours scraping, 1 hour cleaning

18. **Ponytail Plugin Installed** (15:50)
    - Plugin installed in Claude Code session
    - AGENTS.md cleaned up (removed install instructions)

19. **Research: Sources Added**
    - All research files now have credible sources with links
    - AGENTS.md updated with source requirements rule

20. **SPEC.md Created** (22:30)
    - Full technical specification (13 sections)
    - Problem statement, dataset, pipeline, analytics, LLM, interface
    - Acceptance criteria, file structure, risks, limitations

21. **Project Directory Structure Created** (22:30)
    - data/{raw,cleaned,analytics}
    - src/{pipeline,analytics,llm,app}
    - notebooks/, tests/, submission/, docs/

22. **Claude Code Prompts Prepared** (prompts/day1-prompts.md)
    - 3 prompts ready: scraper, cleaning, analytics
    - Follow AGENTS.md prompt rules (problem, reference, acceptance criteria)

23. **SDD Authoritative Source Found** (22:59)
    - Found GitHub Spec Kit (https://github.com/github/spec-kit) — 114k stars
    - This is the official definition of Spec-Driven Development
    - Updated AGENTS.md and research with proper source

#### Decisions Made

| Decision | Rationale | Status |
|----------|-----------|--------|
| Use ponytail (YAGNI principles) | Proven tool, aligns with test case's "anti-over-engineering" evaluation (10% weight) | Applied |
| 3-day timeline (not 5) | AI coding accelerates 3-5x. Day 1: spec, Day 2: build, Day 3: docs | Agreed |
| Spec-Driven Development | Prevents scope creep, enables verification, documentation writes itself | Active |
| Kilo = planning, Claude = code | Clear separation of concerns, prevents context pollution | Active |
| Test case = authoritative source | Prevents drift from requirements, catches violations early | Enforced |

#### Open Items

- [x] ~~Awaiting recruiter response~~ ✅ APPROVED (Jun 19, 15:45)
- [x] SPEC.md created and refined
- [x] Dataset scoped — Tokopedia + Shopee, food & beverage, Java Island, ~1000 products
- [x] Ponytail plugin installed
- [ ] Build Tokopedia + Shopee scraper — **Day 1**
- [ ] Architecture doc draft — **Day 1**

#### Session Summary

**Session 1 completed.** All planning and research done. Ready for Day 1 implementation.

**Working hours:** ~4.5 hours active (14:00-16:30, 21:00-23:33)
**Break:** ~4.5 hours (16:30-21:00)

**What was accomplished:**
- Full project context loaded and cross-referenced
- AGENTS.md with all rules (SDD, Ponytail, Compliance, Research, Tracking)
- 3 research files with credible sources
- Dataset decision made (Tokopedia + Shopee scraping, food & beverage on Java Island)
- SPEC.md created and refined (problem statement, dataset scope, analytics)
- Recruiter approval received (AI tools allowed)
- Ponytail plugin installed
- Claude Code prompts prepared
- HISTORY.md tracking system operational

**Next session (Day 1):**
- Build Tokopedia + Shopee scraper
- Collect ~1,000 products (food & beverage, Java Island)
- Data cleaning pipeline
- Architecture doc draft

---

## Decision History

| # | Date | Decision | Made By | Rationale |
|---|------|----------|---------|-----------|
| 1 | Jun 19 | Use SDD (Spec-Driven Development) | Kilo | Prevents scope creep, enables verification |
| 2 | Jun 19 | Test case = authoritative source | Kilo | Prevents drift from requirements |
| 3 | Jun 19 | Use ponytail YAGNI principles | User | Proven tool, aligns with evaluation criteria |
| 4 | Jun 19 | 3-day compressed timeline | User | AI coding acceleration, not 5 days |
| 5 | Jun 19 | Kilo = planning only, Claude = code only | Kilo | Clear separation, prevents context pollution |
| 6 | Jun 19 | AI coding tools approved by recruiter | Recruiter | Claude Code, Cursor, Copilot all allowed |
| 7 | Jun 19 | Scrape Indonesian marketplace (not Kaggle) | User | Domain expertise in demand forecasting, demonstrates data engineering |
| 8 | Jun 19 | Tokopedia as primary scraping target | Kilo | GraphQL API accessible, structured JSON, largest Indonesian marketplace |
| 9 | Jun 20 | Synthetic data fallback for scraping | Claude | Tokopedia/Shopee have Akamai bot protection, documented trade-off |
| 10 | Jun 20 | Install Playwright on VPS | Claude | Attempt headless browser scraping (still blocked by anti-bot) |
| 11 | Jun 20 | Extend Java Island city list | Claude | Synthetic data uses city names, not just province names |

---

## File Change History

| Date | File | Change | By |
|------|------|--------|----|
| Jun 19 | AGENTS.md | Added Test Case Compliance rule | Kilo |
| Jun 19 | AGENTS.md | Added Optional Plus Points | Kilo |
| Jun 19 | AGENTS.md | Added MVP Interface Tiers | Kilo |
| Jun 19 | AGENTS.md | Added Key Quotes | Kilo |
| Jun 19 | AGENTS.md | Updated Timeline to 3 days | Kilo |
| Jun 19 | AGENTS.md | Added Ponytail rules | Kilo |
| Jun 19 | HISTORY.md | Created tracking file | Kilo |
| Jun 19 | AGENTS.md | Added Session Tracking rule | Kilo |
| Jun 19 | AGENTS.md | Added Research Documentation rule | Kilo |
| Jun 19 | research/INDEX.md | Created research index | Kilo |
| Jun 19 | research/ai-development-approaches.md | Researched 6 AI dev approaches | Kilo |
| Jun 19 | research/dataset-selection.md | Evaluated 5 datasets, recommend Olist | Kilo |
| Jun 19 | context_from_other_chat_session.md | Moved to docs/archived/ | Kilo |
| Jun 19 | research/marketplace-scraping.md | Researched Indonesian marketplace scraping | Kilo |
| Jun 19 | research/INDEX.md | Updated with scraping research, marked Olist as superseded | Kilo |
| Jun 19 | AGENTS.md | Added ponytail plugin installation instructions | Kilo |
| Jun 19 | AGENTS.md | Removed ponytail install instructions (plugin installed) | Kilo |
| Jun 19 | AGENTS.md | Added research source requirements | Kilo |
| Jun 19 | research/marketplace-scraping.md | Added sources section | Kilo |
| Jun 19 | research/ai-development-approaches.md | Updated sources with links | Kilo |
| Jun 19 | research/dataset-selection.md | Added sources section | Kilo |
| Jun 19 | SPEC.md | Created full technical specification | Kilo |
| Jun 19 | prompts/day1-prompts.md | Created Claude Code prompts for Day 1 | Kilo |
| Jun 19 | data/, src/, notebooks/, tests/, submission/ | Created project directories | Kilo |
| Jun 19 | AGENTS.md | Updated SDD with GitHub Spec Kit source | Kilo |
| Jun 19 | AGENTS.md | Renamed to SDD-inspired, adapted for 3-day sprint | Kilo |
| Jun 19 | AGENTS.md | Simplified verification section | Kilo |
| Jun 19 | SPEC.md | Updated problem statement (general trade business) | Kilo |
| Jun 19 | SPEC.md | Scoped dataset (food & beverage, Java Island, ~1000 products) | Kilo |
| Jun 19 | SPEC.md | Updated LLM prompt (market intelligence analyst role) | Kilo |
| Jun 19 | SPEC.md | Updated analytics questions (scoped to subcategories) | Kilo |
| Jun 19 | prompts/day1-prompts.md | Updated prompts (scoped keywords, Java Island filter) | Kilo |
| Jun 19 | AGENTS.md | Added active working time tracking rule | Kilo |
| Jun 20 | SPEC.md | Full rewrite — business context, 5 analysis categories, 14 fields mapped | Kilo |
| Jun 20 | SPEC.md | Updated data pipeline — explicit staging layer, validation rules | Kilo |
| Jun 20 | SPEC.md | Added MVP vs Production scope table | Kilo |
| Jun 20 | SPEC.md | Added Docker + VPS deployment to tech stack | Kilo |
| Jun 20 | SPEC.md | Updated file structure (Dockerfile, docker-compose, .env.example) | Kilo |
| Jun 20 | SPEC.md | Added deployment acceptance criteria | Kilo |
| Jun 20 | research/database-selection.md | Researched SQLite vs PostgreSQL vs MariaDB | Kilo |
| Jun 20 | research/INDEX.md | Added database selection research | Kilo |
| Jun 20 | CLAUDE.md | Updated with VPS info, tech stack, deploy commands | Kilo |
| Jun 20 | CLAUDE.md | Removed old "tentative" language | Kilo |
| Jun 20 | prompts/day1-prompts.md | Deleted (outdated, replaced by data-pipeline.md) | Kilo |
| Jun 20 | prompts/day1-data-pipeline.md | Updated with VPS context | Kilo |
| Jun 20 | AGENTS.md | Added VPS password security rule | Kilo |
| Jun 20 | src/pipeline/scraper.py | Built: tokopaedi mobile API scraper (real data) | Claude |
| Jun 20 | src/pipeline/cleaner.py | Built: cleaning, normalization, spec parsing | Claude |
| Jun 20 | src/pipeline/validator.py | Built: 7 data quality checks | Claude |
| Jun 20 | src/pipeline/run_pipeline.py | Built: 5-step pipeline orchestrator | Claude |
| Jun 20 | requirements.txt | Created: tokopaedi, httpx, pandas, pytest | Claude |
| Jun 20 | SPEC.md | Updated: data sources, tech stack, pipeline steps | Claude |

---

## Context from Previous Sessions

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
