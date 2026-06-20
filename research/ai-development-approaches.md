# Research: AI-Assisted Development Approaches

> **Topic:** Best practices for building products with AI coding tools
> **Date:** Jun 19, 2026
> **Status:** Final
> **Requested by:** User — "do a research about it and other alternatives on developing product using AI"

---

## Summary

Several proven approaches exist for AI-assisted development. We're adopting a hybrid that fits our constraints: 3-day deadline, must demonstrate understanding, must be explainable.

---

## Approaches Researched

### 1. Spec-Driven Development (SDD) — Our Primary

**What:** Write a detailed specification before any code. AI implements from spec. The spec is the source of truth.

**How it works:**
```
SPEC → RESEARCH → BUILD → VERIFY → DOCUMENT
```

**Key insight:** "If your entire src code was deleted and all your claude memory deleted, you could open a clean claude-code session, point at the spec, and tell claude to implement it." — r/ClaudeCode

**Pros:**
- Prevents scope creep (most common time-waster with AI)
- AI has clear boundaries — less hallucination in code generation
- Documentation writes itself from the spec
- Verification is straightforward — compare output to spec
- If code is lost, spec can regenerate it

**Cons:**
- Requires upfront time investment (2-4 hours for spec)
- Spec can become stale if not maintained
- Over-specifying kills AI creativity
- LLMs are non-deterministic — specs aren't enforced perfectly

**Best for:** Projects with clear requirements and deadline pressure

**Sources:**
- https://github.com/github/spec-kit — **GitHub's official Spec Kit** (114k stars) — THE authoritative source for SDD
- https://www.juststeveking.com/articles/spec-driven-development-with-llms/ — "Spec Driven Development With LLMs"
- https://danielsogl.medium.com/spec-driven-development-sdd-the-evolution-beyond-vibe-coding — "SDD: The Evolution Beyond Vibe Coding"
- https://www.reddit.com/r/ClaudeCode/comments/1rg0b9i/has_anyone_tried_the_spec_driven_development/ — Community discussion

---

### 2. Ponytail / YAGNI — Our Anti-Over-Engineering Layer

**What:** Lazy senior dev philosophy. Don't build what you don't need.

**Ladder:**
```
1. Does this need to exist?   → no: skip it
2. Stdlib does it?            → use it
3. Native platform feature?   → use it
4. Installed dependency?      → use it
5. One line?                  → one line
6. Only then: the minimum that works
```

**Measured impact (from ponytail benchmarks):**
- ~54% less code (up to 94%)
- ~20% cheaper
- ~27% faster
- 100% safety preserved

**Why we use it:** Test case explicitly evaluates "Pragmatism & anti-over-engineering" at 10% weight.

**Source:** https://github.com/DietrichGebert/ponytail

---

### 3. Explore → Plan → Implement — Claude Code's Own Pattern

**What:** Separate research from execution. Don't jump to code.

**Phases:**
1. **Explore** — Read codebase, understand patterns (plan mode)
2. **Plan** — Create implementation plan
3. **Implement** — Code from plan, verify against it
4. **Commit** — Descriptive message, PR

**Key insight from Anthropic:** "Letting Claude jump straight to coding can produce code that solves the wrong problem."

**When to skip planning:** "If you could describe the diff in one sentence, skip the plan."

**Source:** https://docs.anthropic.com/en/docs/claude-code/best-practices

---

### 4. Verification-Driven Development

**What:** Give AI a check it can run. Tests, build, screenshot comparison.

**Why it matters:** "Without a check it can run, 'looks done' is the only signal available, and you become the verification loop."

**Our application:**
- Data quality checks after every pipeline step
- Schema validation
- Output comparison against spec acceptance criteria
- LLM grounding verification (answer must reference data)

**Source:** https://docs.anthropic.com/en/docs/claude-code/best-practices

---

### 5. Interview-First Approach

**What:** Have AI interview you before building. Surfaces things you haven't considered.

**Pattern:**
```
"I want to build [brief description]. Interview me using AskUserQuestion tool.
Ask about technical implementation, UI/UX, edge cases, concerns, and tradeoffs.
Keep interviewing until we've covered everything, then write a complete spec."
```

**Why we didn't use it:** We already have the test case as our "interview." The PDF defines requirements clearly.

**Source:** https://docs.anthropic.com/en/docs/claude-code/best-practices

---

### 6. Writer/Reviewer Pattern

**What:** One AI writes, another reviews in fresh context. No bias from "I wrote this."

**Pattern:**
| Session A (Writer) | Session B (Reviewer) |
|---|---|
| Implement feature | Review diff against plan |
| Receive feedback | Report gaps |
| Fix issues | Re-review |

**Why we might use it:** Evaluation criteria includes "Communication & documentation" (10%). Fresh review catches gaps.

**Source:** https://docs.anthropic.com/en/docs/claude-code/best-practices

---

## Our Hybrid Approach

We're combining elements from multiple approaches:

| Approach | How We Use It |
|----------|---------------|
| SDD-inspired | Primary workflow. Spec drives everything. Adapted from GitHub Spec Kit for 3-day sprint. |
| Ponytail/YAGNI | Anti-over-engineering layer. Mandatory for all code. |
| Explore→Plan→Implement | Kilo explores, writes spec, Claude implements. |
| Verification-Driven | Every feature must have a check Claude can run. |
| Interview-First | Skipped — test case is our interview. |
| Writer/Reviewer | Optional — use if time permits on Day 3. |

---

## Key Differences from Halaqah AI / Latent Signal

| Aspect | Those Projects | This Project |
|--------|---------------|--------------|
| Goal | Working product | Demonstrate understanding |
| Speed | Ship fast | Explain everything |
| Code | Whatever works | Must be explainable |
| Docs | After the fact | Before and during |
| Over-engineering | Optimize later | Must not exist |
| AI role | Build it | Build it AND I must understand it |

---

## Recommendation

**Use SDD-inspired + Ponytail as the core workflow.** Add verification-driven development for quality. Skip Writer/Reviewer unless Day 3 has spare time.

The test case rewards thinking, not just tools. Our approach demonstrates:
- Problem framing (SDD forces this)
- Anti-over-engineering (ponytail enforces this)
- Grounded LLM usage (verification ensures this)
- Clear trade-offs (documentation captures this)
