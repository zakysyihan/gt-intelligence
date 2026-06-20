# Research: Analytics Layer Stack

> **Topic:** Best open-source LLM data analyst agent for our MVP
> **Date:** Jun 20, 2026
> **Status:** Final
> **Requested by:** User — "find the most pragmatis way to acquire this"

---

## Summary

**Recommendation: Vanna.ai** — MIT license, 23.7k stars, text-to-SQL + chart generation + Streamlit integration. Pragmatic choice for 3-day MVP.

---

## Candidates Evaluated

### 1. Vanna.ai — RECOMMENDED

| | |
|---|---|
| GitHub | https://github.com/vanna-ai/vanna |
| Stars | 23.7k |
| License | MIT |
| Language | Python |

**What it does:**
- Text-to-SQL: user asks question → LLM generates SQL → runs against database
- Chart generation: SQL results → auto-generate charts
- RAG-based: trains on your DDL + documentation for better SQL generation
- Streamlit integration built-in

**Why it fits:**
- Works with SQLite (our DB)
- Streamlit integration (our UI)
- MIT license (no restrictions)
- Simple: `pip install vanna` → 10 lines of code to get started
- User asked: "predefined dashboard + LLM agent that can answer questions, create analysis, create custom dashboard" — this is exactly what Vanna does

**Code example:**
```python
from vanna.streamlit import VannaStreamlit
from vanna.chromadb import ChromaDB

class MyVanna(ChromaDB, OpenAI):
    pass

vn = MyVanna(api_key='sk-...')
vn.connect_to_sqlite('data/analytics/products.db')

# Train on your schema
vn.train(ddl="CREATE TABLE products (...)")
vn.train(documentation="Table contains food & beverage products...")

# Use in Streamlit
VannaStreamlit.ask(
    vn,
    title="GT Intelligence — Market Analyst",
    include_metadata=True
)
```

**Concerns:**
- Adds Vanna + ChromaDB dependencies (2 extra packages)
- ChromaDB is a vector DB for RAG training — adds complexity
- Less control over prompt/grounding vs custom implementation

---

### 2. PandasAI

| | |
|---|---|
| GitHub | https://github.com/sinaptik-ai/pandas-ai |
| Stars | 23.6k |
| License | Apache 2.0 |
| Language | Python |

**What it does:**
- Chat with your Pandas DataFrames
- Natural language → Python code → results + charts
- Works with CSV, SQL, parquet

**Why it fits:**
- We already use Pandas
- Simple API: `df.chat("What are the top products?")`
- Generates charts automatically

**Concerns:**
- Less mature than Vanna for SQL-specific use cases
- Apache 2.0 license (fine, but MIT is simpler)
- Less community adoption for Streamlit specifically

---

### 3. WrenAI

| | |
|---|---|
| GitHub | https://github.com/Canner/WrenAI |
| Stars | 15.6k |
| License | AGPL-3.0 |
| Language | Python |

**What it does:**
- Full analytics platform: text-to-SQL, dashboards, agentic analytics
- Supports 20+ data sources
- Has its own UI (not Streamlit)

**Concerns:**
- AGPL license — if we modify and deploy, we must open-source our changes
- Full platform, not a library — heavier to integrate
- Has its own UI, doesn't integrate with Streamlit natively
- Overkill for 1,000 rows

---

## Comparison Matrix

| Factor | Vanna.ai | PandasAI | WrenAI | Custom (OpenAI function calling) |
|--------|----------|----------|--------|--------------------------------|
| Text-to-SQL | ✅ Built-in | ✅ Built-in | ✅ Built-in | ✅ We build it |
| Chart generation | ✅ Built-in | ✅ Built-in | ✅ Built-in | ✅ We build it |
| Streamlit integration | ✅ Native | ✅ Possible | ❌ Own UI | ✅ We build it |
| License | MIT | Apache 2.0 | AGPL ⚠️ | N/A |
| Stars | 23.7k | 23.6k | 15.6k | N/A |
| Dependencies | vanna, chromadb, openai | pandas-ai, openai | Full platform | openai only |
| Time to integrate | ~1 hour | ~1 hour | ~3+ hours | ~3-4 hours |
| Control over prompts | Medium | Low | Low | Full |
| Explainability | Medium | Medium | Low | Full |

---

## Recommendation

**Use WrenAI + Chainlit for the MVP.**

**Why:**
1. Apache 2.0 license — permissive
2. MDL semantic layer — business-aware agent, not just SQL generator
3. Follow-up suggestions — agent suggests next questions
4. Chainlit — agent-native chat UI, conversational
5. Time to integrate: ~2-3 hours vs ~3-4 hours building custom
6. Impressive for demo — semantic layer concept shows architectural thinking

**Trade-off (documented):**
- Less control over prompts vs custom implementation
- Adds 2 dependencies (vanna, chromadb)
- RAG training step required (feed it our schema)

**If Vanna doesn't work:** Fall back to custom OpenAI function calling with Plotly. We can explain both approaches in the architecture doc — shows we evaluated options.

---

## Sources

1. https://github.com/vanna-ai/vanna — 23.7k stars, MIT license
2. https://github.com/sinaptik-ai/pandas-ai — 23.6k stars, Apache 2.0
3. https://github.com/Canner/WrenAI — 15.6k stars, AGPL-3.0
4. https://github.com/topics/text-to-sql — 639 public repos
5. https://getnao.io/blog/open-source-analytics-agent-builder-playbook/ — comparison of 5 analytics agents
