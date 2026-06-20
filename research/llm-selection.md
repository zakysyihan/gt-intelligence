# Research: LLM Selection for WrenAI

> **Topic:** Which LLM to use for text-to-SQL + market intelligence
> **Date:** Jun 20, 2026
> **Status:** Final
> **Context:** User has SumoPod AI (DeepSeek v4 Flash). WrenAI supports OpenAI-compatible endpoints via LiteLLM.

---

## Summary

**Use SumoPod AI (DeepSeek v4 Flash) as primary.** It's free for us, OpenAI-compatible, and benchmarks show DeepSeek generates adequate SQL at 10x lower cost than GPT-4. If quality is insufficient, fall back to GPT-4o-mini ($0.15/$0.60 per 1M tokens).

---

## LLM Options

| Model | Input $/1M | Output $/1M | Text-to-SQL Quality | WrenAI Compatible | Cost for 672 products |
|-------|-----------|-------------|---------------------|-------------------|----------------------|
| **SumoPod DeepSeek v4 Flash** | Free (our platform) | Free | Adequate | ✅ (OpenAI-compatible) | $0 |
| **GPT-4o-mini** | $0.15 | $0.60 | Good | ✅ (recommended) | ~$0.01 |
| **DeepSeek V3.2** (direct API) | $0.28 | $0.42 | Good | ✅ (OpenAI-compatible) | ~$0.003 |
| **GPT-4o** | $2.50 | $10.00 | Best | ✅ (recommended) | ~$0.02 |
| **Claude Sonnet 4** | $3.00 | $15.00 | Best | ✅ (via LiteLLM) | ~$0.03 |

## Key Findings

1. **WrenAI recommends:** OpenAI o3-mini, GPT-4o, or GPT-4o-mini (docs.getwren.ai)
2. **WrenAI uses LiteLLM:** Any OpenAI-compatible endpoint works (Ollama, DeepSeek, custom)
3. **DeepSeek V4 generates adequate SQL** at 10x lower cost than GPT-4 (tokenmix.ai benchmark)
4. **Text-to-SQL benchmark (llm-benchmark.tinybird.live):** 19 models tested on 200M rows — DeepSeek performed well for standard SQL generation
5. **Our use case is simple:** Single table, ~1,000 rows, standard SQL (GROUP BY, ORDER BY, aggregate functions). No complex joins or subqueries needed.

## Decision

**Primary: SumoPod DeepSeek v4 Flash** — free, already configured, good enough for our simple schema.

**Fallback: GPT-4o-mini** — if DeepSeek SQL quality is insufficient (bad syntax, wrong column names), switch to GPT-4o-mini. Still cheap ($0.01 for full demo).

**How to switch:** WrenAI config uses OpenAI-compatible endpoint. Change one env var:
```
LLM_MODEL=deepseek/deepseek-chat  →  LLM_MODEL=gpt-4o-mini
LLM_API_BASE=https://sumopod/v1    →  LLM_API_BASE=https://api.openai.com/v1
```

---

## Sources

1. https://docs.getwren.ai/oss/ai_service/guide/custom_llm — WrenAI recommends OpenAI models
2. https://tokenmix.ai/blog/best-llm-for-sql-generation — "DeepSeek V4 generates adequate SQL at 10x lower cost"
3. https://www.tinybird.co/blog/which-llm-writes-the-best-sql — 19-model SQL benchmark
4. https://benchlm.ai/blog/posts/llm-pricing-2026 — LLM pricing comparison 2026
5. https://research.aimultiple.com/text-to-sql/ — Text-to-SQL LLM accuracy comparison
