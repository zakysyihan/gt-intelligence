# Research: LLM Selection — Eval-Driven Analysis

> **Topic:** Which LLM for each use case in our system
> **Date:** Jun 20, 2026
> **Status:** Final
> **Context:** Two distinct LLM use cases — product name parser (data engineering) and WrenAI text-to-SQL agent (user-facing)

---

## Step 1: What Our LLM Actually Needs to Do

### WrenAI Architecture (from deep-dive)

WrenAI is a **semantic middleware layer**, not an LLM application. The LLM is external, connected via LiteLLM. The pipeline:

```
User question (Indonesian)
  → wren memory recall (retrieve similar past NL-SQL pairs)
  → wren memory fetch (retrieve MDL schema context)
  → LLM writes SQL against MDL objects (NOT raw tables)
  → wren dry-plan (deterministic validation + expansion)
  → wren query (execute against SQLite)
  → LLM interprets results → human-readable answer
  → wren memory store (persist confirmed pair)
```

**Critical details:**
- The LLM writes SQL against **MDL model names**, not raw database tables. `wren dry-plan` expands MDL → executable SQL via wren-core (Rust).
- The LLM **never sees the raw schema**. It only sees the MDL abstraction layer.
- The pipeline is **multi-step** — the LLM must call CLI tools in sequence (memory recall → memory fetch → write SQL → dry-plan → query → interpret).
- **WrenAI has two modes:** `--guided` (forces step-by-step workflow for weaker LLMs) and `--direct` (autonomous for stronger LLMs).
- **Errors are caught by dry-plan**, not by the LLM. If the SQL is wrong, dry-plan fails loudly with actionable errors. The LLM can then retry.

### What the LLM Actually Does (Capability Requirements)

| Capability | Required? | Why |
|-----------|-----------|-----|
| Write simple SQL (SELECT, WHERE, GROUP BY, ORDER BY) | **Yes** | Core task — but MDL constrains what's available |
| Follow structured workflow (Skills/Markdown instructions) | **Yes** | WrenAI Skills tell the agent which tools to call |
| Call CLI tools (function calling) | **Yes** | Agent must invoke `wren` commands |
| Interpret SQL results → human-readable answer | **Yes** | User-facing output |
| Handle Indonesian language | **Yes** | User questions are in Bahasa |
| Error recovery (retry after dry-plan failure) | **Yes** | Pipeline must be resilient |
| Suggest follow-up questions | Nice-to-have | Adds value but not critical |
| Complex SQL (JOINs, CTEs, window functions) | **No** | Our schema is 1 table, 14 columns — no JOINs needed |
| Deep SQL expertise | **No** | MDL constrains the view; dry-plan validates |
| Multi-step chain-of-thought reasoning | **No** | Workflow is broken into discrete tool calls |
| Vision, code execution | **No** | Not needed |

### Key Insight: Our Schema Is Trivial

Our database has **1 table with 14 columns**. The hardest SQL the LLM might write:

```sql
SELECT subcategory, AVG(price) as avg_price, SUM(sold_count) as total_sold
FROM products
WHERE shop_location LIKE '%Bandung%'
GROUP BY subcategory
ORDER BY total_sold DESC
LIMIT 10
```

This is "simple" tier on every benchmark. No JOINs, no subqueries, no window functions, no CTEs.

---

## Step 2: Finding the Right Eval

### Why BIRD-Interact Is the Right Benchmark

| Benchmark | What It Tests | Match to Our Use Case |
|-----------|---------------|----------------------|
| **BIRD-Interact (a-Interact)** | Agentic text-to-SQL with multi-turn interaction | **HIGH** — tests tool calling, autonomous SQL generation, error recovery |
| **GDPval-AA v2** | Real-world agentic tasks (44 occupations) | **HIGH** — tests planning, tool use, autonomy |
| **BIRD standard** | Single-shot text-to-SQL accuracy | MEDIUM — tests SQL generation but not agentic capabilities |
| **TokenMix** | SQL generation by complexity tier | MEDIUM — useful for understanding accuracy cliffs |
| **Spider** | Cross-database text-to-SQL | LOW — tests generalization across DBs, not relevant |
| **Agentic Index** | Composite of GDPval-AA v2 + τ³-Banking | HIGH — but composite scores are behind dynamic JS rendering |

**BIRD-Interact** (ICLR 2026 Oral) is the closest match because it tests:
1. Agentic mode (a-Interact) — model autonomously decides actions
2. Text-to-SQL generation against a database
3. Multi-turn interaction and error recovery
4. Ambiguity resolution (asks clarifying questions)

**GDPval-AA v2** is the best supplementary eval because it tests:
1. Real-world agentic task completion
2. Tool calling and planning
3. 50 models ranked with Elo scores

### What BIRD-Interact Does NOT Test (Limitations)

- Semantic layer (MDL) — BIRD-Interact uses raw SQL, not MDL abstraction
- Simple schema — BIRD-Interact uses complex databases with many tables
- Indonesian language — all questions are in English
- Follow-up question suggestions

**Why this matters:** Our use case is actually **easier** than BIRD-Interact in two ways:
1. MDL constrains what the LLM can see (fewer choices = fewer errors)
2. Our schema is trivial (1 table, 14 columns)

So BIRD-Interact scores are a **lower bound** for our use case — models should perform better on our simple schema.

---

## Step 3: Eval Results (June 2026)

### BIRD-Interact — Agentic Text-to-SQL (ICLR 2026)

**Source:** arXiv:2510.05318v3, 600 tasks, PostgreSQL

#### a-Interact Mode (Agentic — closest to our WrenAI setup)

| Rank | Model | Priority SR | Follow-up SR | Reward | Cost/task |
|------|-------|------------|-------------|--------|-----------|
| 1 | **GPT-5** | 29.17% | 17.00% | 25.52 | $0.24 |
| 2 | **Claude Sonnet 4** | 27.83% | 12.67% | 23.28 | $0.51 |
| 3 | **Gemini 2.5 Pro** | 20.33% | 10.33% | 17.33 | $0.22 |
| 4 | **Claude Sonnet 3.7** | 21.00% | 9.17% | 17.45 | $0.60 |
| 5 | **O3-Mini** | 19.83% | 8.50% | 16.43 | $0.06 |
| 6 | **DeepSeek Chat V3.1** | 17.17% | 4.83% | 13.47 | $0.06 |
| 7 | **Qwen 3 Coder 480B** | 13.33% | 4.17% | 10.58 | $0.07 |

#### c-Interact Mode (Conversational — user drives the conversation)

| Rank | Model | Priority SR | Follow-up SR | Reward | Cost/task |
|------|-------|------------|-------------|--------|-----------|
| 1 | **Gemini 2.5 Pro** | 18.73% | 12.41% | 20.92 | $0.04 |
| 2 | **O3-Mini** | 17.76% | 11.44% | 20.27 | $0.07 |
| 3 | **Claude Sonnet 4** | 16.06% | 10.46% | 18.35 | $0.29 |
| 4 | **Qwen 3 Coder 480B** | 16.30% | 8.03% | 17.75 | $0.11 |
| 5 | **GPT-5** | 9.49% | 5.84% | 12.58 | $0.08 |
| 6 | **DeepSeek Chat V3.1** | 11.44% | 4.62% | 15.15 | $0.12 |
| 7 | **Claude Sonnet 3.7** | 10.71% | 4.62% | 13.87 | $0.29 |

**Key findings:**
- **GPT-5 dominates agentic mode** (17.00% follow-up SR) — 2x better than DeepSeek (4.83%)
- **Gemini 2.5 Pro dominates conversational mode** (12.41% follow-up SR) — and costs only $0.04/task
- **DeepSeek and Qwen are far behind** on both modes — 3-4x worse than frontier models
- **O3-Mini is the best value** — $0.06/task with 8.50% agentic SR (competitive with Claude Sonnet 3.7)
- Even frontier models score below 20% — this is a HARD benchmark

### GDPval-AA v2 — Real-World Agentic Tasks (50 models)

**Source:** artificialanalysis.ai/evaluations/gdpval-aa, Elo ratings from blind pairwise comparisons

| Rank | Model | Elo | Release |
|------|-------|-----|---------|
| 1 | Claude Fable 5 (Opus 4.8 Fallback) | 1783 | Jun 2026 |
| 2 | Claude Opus 4.8 | 1615 | May 2026 |
| 3 | GLM-5.2 (max) | 1524 | Jun 2026 |
| 4 | Claude Opus 4.7 | 1512 | Apr 2026 |
| 5 | GPT-5.5 (xhigh) | 1509 | Apr 2026 |
| 6 | GPT-5.5 (high) | 1479 | Apr 2026 |
| 7 | MiniMax-M3 | 1408 | Jun 2026 |
| 8 | GPT-5.4 (xhigh) | 1401 | Mar 2026 |
| 9 | Claude Sonnet 4.6 | 1395 | Feb 2026 |
| 10 | Gemini 3.5 Flash (high) | 1357 | May 2026 |
| 11 | **DeepSeek V4 Pro (Reasoning)** | 1318 | Apr 2026 |
| 12 | Qwen3.7 Max | 1289 | May 2026 |
| 13 | MiMo-V2.5-Pro | 1277 | Apr 2026 |
| 14 | GLM-5.1 (Reasoning) | 1268 | Apr 2026 |
| 15 | Kimi K2.6 | 1200 | Apr 2026 |
| 16 | Kimi K2.7 Code | 1199 | Jun 2026 |
| 17 | **DeepSeek V4 Flash (Reasoning)** | 1191 | Apr 2026 |
| 18 | GPT-5.4 mini (xhigh) | 1179 | Mar 2026 |
| 19 | Nemotron 3 Ultra 550B | 1174 | Jun 2026 |
| 20 | MiniMax-M2.7 | 1171 | Mar 2026 |

**Human baseline: 1000 Elo.** 28 of 50 models are above human baseline.

**Key findings:**
- **Anthropic dominates** — top 2, 4 of top 9
- **DeepSeek V4 Pro at rank 11** (Elo 1318) — above human baseline, solid mid-frontier
- **DeepSeek V4 Flash at rank 17** (Elo 1191) — above human baseline, but significantly behind frontier
- **GPT-5.4 mini at rank 18** (Elo 1179) — comparable to DeepSeek V4 Flash
- The gap between rank 1 (1783) and rank 17 (1191) is **592 Elo points** — massive

### BIRD Standard — Standalone Text-to-SQL Accuracy

**Source:** bird-bench.github.io, test execution accuracy

| Model | Test EX% |
|-------|----------|
| Claude Opus 4.6 | 70.15 |
| Qwen3-Coder-480B-A35B | 68.14 |
| Claude 4.5 Sonnet | 66.85 |
| GLM-4.7 | 62.94 |
| DeepSeek-R1 | 60.93 |
| Kimi-K2-Thinking | 59.87 |
| DeepSeek (236B) | 56.68 |
| GPT-4 (baseline) | 54.89 |

**Trained/fine-tuned models (top):**

| Model | Size | Test EX% |
|-------|------|----------|
| Gemini-SQL2 | UNK | 80.04 |
| Arctic-Text2SQL-R1-14B | 14B | 72.22 |
| SLM-SQL + Qwen2.5-Coder-1.5B | 1.5B | 70.49 |

**Key insight:** A fine-tuned 1.5B model (SLM-SQL) matches Claude Opus 4.6 (70.15%) on standalone SQL generation. But standalone SQL ≠ agentic capability.

### TokenMix — SQL Accuracy by Complexity

**Source:** tokenmix.ai, 15,000 queries

| Model | Simple | Moderate | Complex | Expert | Stability (σ) |
|-------|--------|----------|---------|--------|---------------|
| GPT-5.4 | 97.8% | 95.5% | 94.2% | 87.8% | 1.8 |
| Claude Sonnet 4.6 | 97.2% | 95.8% | 95.1% | 90.5% | 2.4 |
| DeepSeek V4 | 94.5% | 89.8% | 85.3% | 74.2% | 4.6 |
| Gemini 2.5 Pro | 96.1% | 93.2% | 91.8% | 84.1% | — |

**Our use case is "Simple" tier** — single table, WHERE, GROUP BY, ORDER BY. All models score 94%+ here. The accuracy cliff only matters for complex schemas.

---

## Step 4: Recommendation

### The Honest Assessment

**The data shows two realities:**

**Reality 1: DeepSeek and Qwen are far behind on agentic text-to-SQL.**
- BIRD-Interact a-Interact: DeepSeek 4.83% vs GPT-5 17.00% (3.5x gap)
- GDPval-AA v2: DeepSeek V4 Flash Elo 1191 vs Claude Opus 4.8 Elo 1615 (424 point gap)
- These are hard benchmarks with complex databases

**Reality 2: Our use case is much simpler than these benchmarks.**
- 1 table, 14 columns, no JOINs — "Simple" tier on TokenMix (all models 94%+)
- MDL constrains the LLM's view — fewer choices = fewer errors
- dry-plan validates SQL before execution — errors are caught deterministically
- `--guided` mode forces step-by-step workflow — compensates for weaker agentic capability
- Memory recall provides few-shot examples — reduces SQL generation difficulty

**The gap between DeepSeek and GPT-5 on BIRD-Interact is real, but it measures performance on complex databases. Our simple schema + MDL + dry-plan changes the calculus.**

### Recommendation: Start with DeepSeek, Upgrade if Needed

| Use Case | Model | Cost | Why |
|----------|-------|------|-----|
| **Parser** (batch extraction) | SumoPod DeepSeek V4 Flash | Free | Simple task, already configured |
| **WrenAI Agent** (try first) | SumoPod DeepSeek V4 Flash | Free | Simple schema compensates for lower agentic capability |
| **WrenAI Agent** (fallback) | GPT-4o-mini or O3-Mini | ~$0.01-0.06/task | If DeepSeek fails on real questions |
| **WrenAI Agent** (stretch) | Gemini 2.5 Pro | ~$0.04/task | Best cost/performance ratio on BIRD-Interact |

### Why Start with DeepSeek (Despite Lower Benchmarks)

1. **Our schema is trivial.** All models score 94%+ on simple SQL. The BIRD-Interact gap measures complex SQL performance.
2. **MDL constrains the view.** The LLM only sees model names and relationships, not raw tables. This eliminates a major source of errors.
3. **dry-plan catches errors.** If the SQL is wrong, it fails before execution. The LLM can retry.
4. **`--guided` mode compensates.** Weaker LLMs get a forced step-by-step workflow.
5. **Memory recall provides few-shot examples.** After a few successful queries, the system has examples to guide future queries.
6. **Cost is zero on SumoPod.** No risk in trying.
7. **Switching is one env var.** If it doesn't work, change `~/.wrenai/config.yaml` and restart.

### When to Upgrade

Upgrade from DeepSeek if:
- SQL generation fails on >30% of real user questions
- dry-plan validation errors are frequent and not self-correcting
- Agent can't follow the guided workflow
- Indonesian language questions produce incorrect SQL

### Cost-Performance Ranking (for our simple use case)

| Model | BIRD-Interact a-Interact SR | GDPval-AA Elo | Cost/task | Our Assessment |
|-------|---------------------------|---------------|-----------|----------------|
| GPT-5 | 17.00% | — | $0.24 | Overkill for 1-table schema |
| Claude Sonnet 4 | 12.67% | 1395 | $0.51 | Overkill, expensive |
| Gemini 2.5 Pro | 10.33% | 1357 | $0.22 | Best value if we need frontier |
| O3-Mini | 8.50% | — | $0.06 | Great value, WrenAI recommended |
| DeepSeek V4 Pro | — | 1318 | ~$0.06 | Good agentic, free on SumoPod |
| **DeepSeek V4 Flash** | **4.83%** | **1191** | **Free** | **Try first — simple schema compensates** |
| GPT-4o-mini | — | 1179 | ~$0.01 | Budget fallback |
| Qwen 3 Coder 480B | 4.17% | 1289 | $0.07 | Weakest on agentic, strong on standalone SQL |

### Parser Recommendation (Unchanged)

| Priority | Model | Cost | Why |
|----------|-------|------|-----|
| **Primary** | SumoPod DeepSeek V4 Flash | Free | Already configured, good at extraction |
| **Fallback** | Qwen3.5-4B (local) | Free | Best multilingual if quality is poor |

---

## Sources

1. [BIRD-Interact Paper](https://arxiv.org/html/2510.05318v3) — ICLR 2026 Oral, agentic text-to-SQL evaluation, 7 models tested
2. [GDPval-AA v2 Leaderboard](https://artificialanalysis.ai/evaluations/gdpval-aa) — 50 models, Elo ratings, real-world agentic tasks
3. [Agentic Index](https://artificialanalysis.ai/models/capabilities/agentic) — Composite of GDPval-AA v2 + τ³-Banking
4. [BIRD Benchmark](https://bird-bench.github.io/) — Standalone text-to-SQL accuracy
5. [TokenMix SQL Benchmark](https://tokenmix.ai/blog/best-llm-for-sql-generation) — 15K queries, accuracy by complexity tier
6. [WrenAI Custom LLM Guide](https://docs.getwren.ai/oss/ai_service/guide/custom_llm) — LiteLLM integration
7. [DeepSeek API Pricing](https://api-docs.deepseek.com/quick_start/pricing) — V4 Flash/Pro pricing
8. [SLM-SQL Paper](https://arxiv.org/html/2507.22478v1) — 1.5B model reaches 70.49% on BIRD test
