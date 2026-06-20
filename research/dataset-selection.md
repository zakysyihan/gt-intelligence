# Research: Dataset Selection

> **Topic:** Kaggle dataset evaluation for LLM-Powered Analytics MVP
> **Date:** Jun 19, 2026
> **Status:** Final
> **Requested by:** User — "do a research about it"

---

## Summary

Evaluated 5 datasets across the 3 categories from the test case. **Recommended: Brazilian E-Commerce (Olist)** for its richness, real business context, and suitability for LLM grounding.

---

## Selection Criteria (From Test Case)

The PDF requires:
1. Public dataset from Kaggle or another public source
2. Must fit one of: Retail/Sales, Customer Churn, Operational/IoT
3. Must support 5+ meaningful business questions
4. Must explain: why chosen, business problem, assumptions/limitations, questions users may ask
5. Must be clean enough for a 3-day sprint
6. Must be suitable for LLM grounding (answer grounded in data)

---

## Datasets Evaluated

### 1. Brazilian E-Commerce (Olist) — RECOMMENDED

**Category:** Retail / Sales / Customer Behavior
**Kaggle:** https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
**Size:** 100k+ orders (2016-2018), 8 connected tables

**Tables:**
- `orders` — order status, timestamps, delivery
- `order_items` — products, sellers, prices
- `order_payments` — payment methods, installments, values
- `order_reviews` — review scores, comments
- `products` — category, dimensions, weight
- `customers` — location (city, state)
- `sellers` — location
- `geolocation` — coordinates

**Why this dataset:**
- **Rich:** Multiple dimensions (time, geography, product, payment, reviews)
- **Real business:** Actual Brazilian e-commerce, not synthetic
- **5+ questions possible:** Revenue trends, top categories, customer segmentation, delivery performance, review analysis, payment patterns, geographic insights
- **LLM grounding:** Can answer specific questions with data references ("Orders from São Paulo had 3.8 avg review score")
- **Clean enough:** Well-structured, documented, moderate size

**Business problems it represents:**
- Sales performance across regions and categories
- Customer satisfaction and delivery reliability
- Payment behavior and installment patterns
- Seller performance and market dynamics

**Assumptions & limitations:**
- Brazilian market only (not global)
- 2016-2018 data (may be dated)
- No customer demographics beyond location
- Reviews may have language barrier (Portuguese)

**Sample questions users may ask:**
1. What are the top 5 product categories by revenue?
2. Which states have the highest average order value?
3. How does delivery time affect review scores?
4. What payment methods are most popular?
5. Which sellers have the best review ratings?
6. What's the trend of orders over time?
7. Which product categories have the most delayed deliveries?

---

### 2. Telco Customer Churn — STRONG ALTERNATIVE

**Category:** Customer Churn / Subscription
**Kaggle:** https://www.kaggle.com/datasets/blastchar/telco-customer-churn
**Size:** 7,043 customers, 21 features

**Features:** tenure, MonthlyCharges, TotalCharges, Contract type, PaymentMethod, OnlineSecurity, TechSupport, etc.

**Pros:**
- Classic, well-documented dataset
- Clear business problem (churn prediction)
- Good for LLM grounding ("Customers with month-to-month contracts churn 3x more")

**Cons:**
- Single table, limited dimensions
- Only 7k rows (might be too small)
- Fewer analytics angles than Olist
- Might feel "textbook" — less impressive

---

### 3. UK Online Retail — DECENT ALTERNATIVE

**Category:** Retail / Sales / Customer Behavior
**Kaggle:** https://www.kaggle.com/datasets/carrie1/ecommerce-data
**Size:** 541k transactions, 12-month period (2010-2011)

**Pros:**
- Good for RFM (Recency, Frequency, Monetary) analysis
- Customer segmentation possible
- International customers

**Cons:**
- Some data quality issues (cancelled transactions, missing customer IDs)
- Single table (less interesting for data engineering)
- UK-only

---

### 4. Superstore Sales — TOO SIMPLE

**Category:** Retail / Sales
**Size:** ~10k rows

**Pros:**
- Very clean, easy to analyze
- Clear business context

**Cons:**
- Too small and simple for meaningful data engineering
- Limited analytics depth
- Feels like a homework dataset, not real business data
- Won't demonstrate "light-to-medium data engineering"

---

### 5. NYC Taxi Trip Data — TOO LARGE

**Category:** Operational / IoT / Time-Series
**Size:** Millions of rows

**Pros:**
- Rich time-series data
- Interesting patterns (rush hours, weather effects)

**Cons:**
- Very large (millions of rows) — slow processing
- Limited business context (just trips)
- Fewer meaningful business questions for LLM grounding
- Overkill for a 3-day MVP

---

## Recommendation

**Use Brazilian E-Commerce (Olist).**

| Criteria | Olist | Telco Churn | UK Retail | Superstore | NYC Taxi |
|----------|-------|-------------|-----------|------------|----------|
| Data richness | ★★★★★ | ★★★ | ★★★★ | ★★ | ★★★★ |
| Business context | ★★★★★ | ★★★★ | ★★★ | ★★★ | ★★ |
| 5+ questions | ★★★★★ | ★★★ | ★★★★ | ★★ | ★★★ |
| LLM grounding | ★★★★★ | ★★★★ | ★★★ | ★★★ | ★★ |
| Clean enough | ★★★★ | ★★★★★ | ★★★ | ★★★★★ | ★★★ |
| Data engineering depth | ★★★★★ | ★★ | ★★★ | ★★ | ★★★★ |
| Impression factor | ★★★★★ | ★★★ | ★★★★ | ★★ | ★★★★ |

**Why Olist wins:**
1. Multiple tables = demonstrates data engineering (ingestion, joining, cleaning)
2. Real business data = demonstrates understanding
3. Rich dimensions = 5+ meaningful questions easily
4. Good for LLM grounding = specific, data-backed answers
5. Not too large = completable in 3 days
6. Well-documented = easier to explain trade-offs

---

## Next Steps

1. ~~Download Olist dataset from Kaggle~~ Superseded by marketplace scraping
2. ~~Explore data quality (nulls, types, distributions)~~
3. Write problem framing in SPEC.md
4. Design data pipeline architecture

---

## Sources

1. **Brazilian E-Commerce (Olist)** — https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce — Kaggle dataset, 100k+ orders, 8 tables
2. **Telco Customer Churn** — https://www.kaggle.com/datasets/blastchar/telco-customer-churn — Kaggle dataset, 7k customers, 21 features
3. **UK Online Retail** — https://www.kaggle.com/datasets/carrie1/ecommerce-data — Kaggle dataset, 541k transactions
4. **Ponytail Benchmarks** — https://github.com/DietrichGebert/ponytail#numbers — Measured impact of YAGNI principles on code volume
