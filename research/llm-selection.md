# Research: LLM Selection (Revised) — Two Use Cases

> **Topic:** Which LLM for each use case in our system
> **Date:** Jun 20, 2026
> **Status:** Final
> **Context:** User identified two distinct LLM use cases requiring different model capabilities

---

## Summary

Two use cases, two different LLM requirements. **Use a tiered approach** — SLM for the parser, frontier model for the agent.

---

## Use Case 1: LLM Parser (Data Engineering)

**Task:** Extract flavor, weight, variant from 672 product titles. E.g., "Chitato Sapi Panggang 68g" → flavor: sapi panggang, weight: 68g

**Requirements:**
- Simple extraction (no reasoning, no tool calling)
- Batch processing (672 products, not real-time)
- Needs: good at Indonesian language + product naming conventions
- Doesn't need: agentic capabilities, multi-step reasoning, chart generation

**Recommendation: SumoPod DeepSeek v4 Flash (free)**
- Already configured, zero cost
- Good at structured extraction tasks
- Fast enough for batch processing
- No need for frontier model here

**Alternative if quality is poor:** Phi-4-mini (3.8B) — runs locally, 67.3% MMLU, strong at structured tasks. Could even run on VPS with 2GB RAM.

---

## Use Case 2: Market Intelligence Agent (WrenAI)

**Task:** Natural language → SQL → results → insights → follow-up suggestions. User-facing, needs quality answers.

**Requirements:**
- Text-to-SQL (understands schema, generates correct SQL)
- Agentic capabilities (tool calling, multi-step reasoning)
- Business context understanding (via MDL)
- Chart generation (text-to-chart)
- Follow-up suggestions

### 2026 LLM Landscape for Agentic SQL

| Tier | Models | SQL Quality | Agentic | Price/1M | Notes |
|------|--------|-------------|---------|----------|-------|
| **Frontier** | GPT-5.4, Claude Opus 4.7 | ★★★★★ | ★★★★★ | $2.50-30 | Overkill for our simple schema |
| **High** | DeepSeek V4 Pro, Qwen 3.6 Plus | ★★★★ | ★★★★ | $0.27-2.00 | Best value for agentic |
| **Mid** | DeepSeek V4 Flash, Qwen3-Coder-Next | ★★★★ | ★★★ | $0.14-0.28 | Good enough for our use case |
| **SLM** | Phi-4-mini (3.8B), Qwen3-4B, SmolLM3 (3B) | ★★★ | ★★ | Free (local) | Text-to-SQL: 56-67% accuracy |

### Key Research Findings

1. **SLM-SQL paper (arXiv 2025):** 0.5B model reached 56.87% execution accuracy, 1.5B reached 67.08% on BIRD benchmark. Impressive but not reliable enough for production.

2. **Qwen3-4B rivals Qwen2.5-72B** through strong-to-weak distillation (2026 benchmark). A 4B model matching a 72B model is insane.

3. **WrenAI recommends OpenAI models** but supports any OpenAI-compatible endpoint via LiteLLM.

4. **DeepSeek V4 generates adequate SQL at 10x lower cost** than GPT-4 (tokenmix.ai).

5. **Finetuned Qwen3-6B beats GPT-4o on Text-to-SQL** (YouTube demonstration, May 2025).

---

## Recommendation: Tiered LLM Strategy

| Use Case | Model | Cost | Why |
|----------|-------|------|-----|
| **Parser** (batch, extraction) | SumoPod DeepSeek v4 Flash | Free | Simple task, no agentic needed |
| **WrenAI Agent** (user-facing SQL) | SumoPod DeepSeek v4 Flash | Free | Try first, has agentic capabilities |
| **WrenAI Agent** (fallback) | GPT-4o-mini | ~$0.01/demo | If DeepSeek SQL quality is insufficient |
| **WrenAI Agent** (stretch) | DeepSeek V4 Pro | ~$0.003/demo | Best open-source agentic if budget allows |

### Why this works:
1. **Parser doesn't need a brain** — just pattern extraction. DeepSeek v4 Flash is overkill already.
2. **Agent needs agentic capabilities** — DeepSeek V4 Flash has tool calling. Try it first.
3. **WrenAI uses LiteLLM** — switching models is one env var change.
4. **Cost is near-zero** regardless of choice — 672 products, simple SQL, minimal tokens.

### What about SLMs for the agent?
**Not recommended for MVP.** SLMs (Phi-4-mini, Qwen3-4B) achieve 56-67% SQL accuracy on benchmarks. Our simple schema might work, but:
- WrenAI recommends OpenAI models specifically
- SLMs need local hosting (Ollama) — adds complexity
- No agentic capabilities at 3-4B scale
- Time risk: debugging SLM integration eats into build time

**Future consideration:** If we self-host on VPS with GPU, a finetuned Qwen3-6B could replace the API call entirely.

---

## Sources

1. https://arxiv.org/html/2507.22478v1 — SLM-SQL: 0.5B→56.87%, 1.5B→67.08% EX on BIRD
2. https://docs.getwren.ai/oss/ai_service/guide/custom_llm — WrenAI recommends OpenAI, supports LiteLLM
3. https://tokenmix.ai/blog/best-llm-for-sql-generation — DeepSeek V4: adequate SQL at 10x lower cost
4. https://huggingface.co/blog/daya-shankar/open-source-llms — DeepSeek V4: frontier-level agentic
5. https://www.bentoml.com/blog/the-best-open-source-small-language-models — Phi-4-mini (3.8B), Qwen3-4B, SmolLM3
6. https://blog.premai.io/prem-1b-sql-fully-local-performant-slm-for-text-to-sql/ — Prem-1B-SQL: fine-tuned SLM for SQL
7. https://www.datacamp.com/blog/top-small-language-models — Top 15 SLMs ranked
8. https://benchlm.ai/blog/posts/llm-pricing-2026 — LLM pricing comparison 2026
