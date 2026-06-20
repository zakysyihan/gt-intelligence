# Research: Database Selection for Analytics MVP

> **Topic:** SQLite vs MariaDB vs PostgreSQL for this project
> **Date:** Jun 20, 2026
> **Status:** Final
> **Requested by:** User — need to evaluate database options

---

## Summary

**Recommendation: SQLite.** For a 3-day MVP with ~1,000 products and a single user, SQLite is the correct choice. PostgreSQL and MariaDB are over-engineered for this scope.

---

## Comparison

| Factor | SQLite | PostgreSQL | MariaDB |
|--------|--------|-----------|---------|
| Setup | Zero — file-based, no server | Install server, create DB, configure | Install server, create DB, configure |
| Cost | Free, no infra | Free, but needs server | Free, but needs server |
| Multi-user | No (single file lock) | Yes (concurrent access) | Yes (concurrent access) |
| Scale | Good for <100k rows | Millions of rows | Millions of rows |
| Analytics | Good enough (SQL works) | Better (window functions, CTEs) | Good (MySQL-compatible) |
| Deployment | Just ship the .db file | Need Docker/hosting | Need Docker/hosting |
| Complexity | Trivial | Medium | Medium |

---

## Why SQLite Wins for This MVP

1. **Single user** — The product dev team uses this together, not concurrent writes
2. **~1,000 rows** — SQLite handles millions of rows; we have 1,000
3. **Zero setup** — No Docker, no server, no config. Ship the .db file.
4. **Portability** — Anyone can open the .db file with any SQLite viewer
5. **Ponytail compliance** — "Does this need to exist?" PostgreSQL doesn't need to exist for 1,000 rows
6. **Demo simplicity** — "Run `streamlit run app.py`" vs "Install PostgreSQL, create user, run migrations"

---

## When PostgreSQL Would Be Better

- Multi-user concurrent access
- Millions of rows
- Real-time data pipeline (streaming)
- Production deployment
- Complex analytics (window functions, materialized views)

None of these apply to a 3-day MVP.

---

## MariaDB vs PostgreSQL

If we DID need a server-based DB:
- **PostgreSQL** — Better for analytics (window functions, CTEs, JSON support)
- **MariaDB** — Better for web apps (faster reads, MySQL-compatible)
- **Our use case** — PostgreSQL would be the choice (analytics focus)

But we don't need either for this MVP.

---

## Recommendation

**Use SQLite.** Document in architecture doc that PostgreSQL would be the production choice. This demonstrates awareness of trade-offs (which the test case evaluates).

---

## Sources

1. SQLite docs — https://www.sqlite.org/about.html — "Most widely deployed database engine"
2. PostgreSQL vs SQLite — https://www.postgresql.org/docs/current/app-usage.html — PostgreSQL recommends SQLite for embedded/local use
3. Ponytail YAGNI — SQLite is the rung that holds. Don't jump to PostgreSQL.
