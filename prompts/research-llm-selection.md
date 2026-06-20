Research the best LLM for our two use cases in this project. Be deep, thorough, and objective. Check everything.

**Use Case 1: LLM Parser** — batch extraction of flavor/weight/variant from 672 Indonesian food product titles. Simple extraction, no reasoning needed.

**Use Case 2: WrenAI Agent** — user-facing text-to-SQL + market intelligence. Needs agentic capabilities, tool calling, business context. Currently configured with SumoPod DeepSeek v4 Flash.

**Research approach:**

1. Check major AI labs and their latest models: OpenAI, Anthropic, Google, DeepSeek, Qwen/Alibaba, Meta, Mistral, MiniMax, Moonshot (Kimi), Zhipu (GLM), Xiaomi (MiMo), Microsoft (Phi), Cohere
2. Check benchmarking sites: artificialanalysis.ai, llm-stats.com, benchlm.ai, codesota.com, LiveBench, SWE-bench, Spider/BIRD text-to-SQL benchmarks
3. Check viral/recent model launches in June 2026 specifically
4. Check SLM options <5B for the parser use case: Phi-4-mini, Qwen3-4B, SmolLM3, Gemma 3 4B, Llama 3.2 3B
5. Check open-source options that could be self-hosted on our VPS (2 vCPU, 2GB RAM — very limited)
6. Check pricing at scale (not just per-token but practical cost for our use volume)
7. Check HuggingFace trending models
8. Check Reddit r/LocalLLaMA for community recommendations on text-to-SQL
9. Check if there are any Indonesian/SEA-specific models that handle Bahasa better

**Output format:** Update research/llm-selection.md with a comprehensive comparison. Include sources for every claim. No unverified statements.
