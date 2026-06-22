# Finalization Checklist — GT Intelligence

> **Deadline:** Monday Jun 22, 09:30 WIB
> **Current:** Sunday Jun 21, 17:20 WIB
> **Time remaining:** ~16 hours

---

## Smoke Test

- [ ] Open https://gt-intelligence.biz.id
- [ ] Dashboard loads with all 8 widgets
- [ ] Metric cards show correct data (672 products, avg price Rp 44K, etc.)
- [ ] Filters work (subcategory, location, price range)
- [ ] Charts render correctly (demand, price, geo, quadrant, revenue, trends)
- [ ] Chat panel opens/closes (collapsible side panel)
- [ ] Ask a question in Indonesian → SQL + table + chart + insight
- [ ] Follow-up suggestions appear after answer
- [ ] Click chart in chat → expands full-screen
- [ ] Unanswerable question handled gracefully (e.g., "profit margin?")
- [ ] Multiple chat sessions work (create new, revisit previous)
- [ ] Responsive at different screen sizes
- [ ] **Report issues below:**

### Issues Found

| # | Issue | Severity | Fixed? |
|---|-------|----------|--------|
| | | | |

---

## Git Repo

- [ ] All code on main branch
- [ ] No untracked files
- [ ] No stale branches
- [ ] README.md exists and is accurate
- [ ] .env.example matches VPS format
- [ ] requirements.txt has all dependencies
- [ ] Dockerfile builds successfully
- [ ] docker-compose.yml works

---

## Architecture Doc (docs/ARCHITECTURE.md)

- [ ] 3-5 pages (currently 217 lines ✅)
- [ ] Problem statement matches SPEC.md
- [ ] Architecture diagram is accurate
- [ ] Data flow matches actual pipeline
- [ ] Tech stack matches actual implementation
- [ ] MVP vs Production table is complete
- [ ] Known limitations are documented
- [ ] No stale references (Streamlit → FastAPI, etc.)

---

## Presentation (submission/presentation-outline.md)

- [ ] 5 slides (currently 5 ✅)
- [ ] Slide 1: Problem + Dataset — story-driven
- [ ] Slide 2: Architecture + Data Flow — matches actual code
- [ ] Slide 3: Analytics Insights — quadrant, trends, geography
- [ ] Slide 4: LLM Interface — code-verified claims
- [ ] Slide 5: Trade-offs — honest, documented
- [ ] Speaker notes in Indonesian
- [ ] **Create slides** (external tool — Claude or Gemini)

---

## Demo Video (submission/demo-video-script.md)

- [ ] Script reviewed (68 lines ✅)
- [ ] Timestamps match (0:00 - 9:00)
- [ ] All demo steps covered (pipeline, dashboard, chat, limitations)
- [ ] **Record video** (7-10 min, screen recording + voiceover)
- [ ] Upload to hosting (YouTube unlisted / Google Drive)
- [ ] Link added to submission

---

## Final Submission Items

| Deliverable | Status | Link/Location |
|------------|--------|---------------|
| Git repository | ✅ | https://github.com/zakysyihan/gt-intelligence |
| Architecture document | ✅ | docs/ARCHITECTURE.md |
| Demo video | ⏳ | (record + upload) |
| Presentation | ⏳ | submission/ (create slides from outline) |
| Live demo | ✅ | https://gt-intelligence.biz.id |

---

## Notes

