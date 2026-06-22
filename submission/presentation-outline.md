# GT Intelligence — Presentation Outline

5 slides for GT Intelligence presentation. Speaker notes in Indonesian.

---

## Slide 1: Problem + Dataset

**Title:** Riset Pasar yang Butuh Berminggu-minggu, Kami Selesaikan dalam Hitungan Jam

**Bullets:**
- Bisnis general trade sulit menentukan produk tanpa data terpusat
- 1,317 produk F&B dari Tokopedia — cokelat, permen, snack
- 32 kab/kota, 5 provinsi Indonesia
- Data scraping via tokopaedi (mobile API), 6-step pipeline

**Speaker notes:** Jelaskan masalah: tim produk butuh data untuk riset produk, tapi data tersebar di marketplace. Kami scrape dari Tokopedia, bersihkan, dan siap untuk analisis. Keterbatasan: data snapshot, bukan real-time. Revenue proxy, bukan profit margin.

---

## Slide 2: Architecture + Data Flow

**Title:** Dari Tokopedia Sampai Jawaban AI

**Bullets:**
- Pipeline: Tokopedia API → Raw → Staging → Clean → LLM Parse → Validate → SQLite
- 7 data quality checks, product spec parsing via LLM
- Agent: ReAct loop (Reason-Act-Observe), text-to-SQL, grounded answers
- Stack: Python, DeepSeek V4 Flash, DuckDB, FastAPI, Docker, SumoPod VPS

**Speaker notes:** Jelaskan pipeline 6 langkah, termasuk staging layer sebagai backup. Agent pakai prompt engineering untuk grounding — tidak pakai semantic layer karena schema hanya 1 tabel. Model DeepSeek gratis di SumoPod, configurable ke model lain.

---

## Slide 3: Analytics Insights

**Title:** Apa yang Data Ceritakan

**Bullets:**
- Snack mendominasi volume, chocolate sweet spot (demand tinggi + rating bagus)
- Quadrant Kualitas: demand vs rating → temukan Hidden Gem & Winning Formula
- Quadrant Distribusi: demand vs jumlah toko → identifikasi celah pasar
- Peta geografis: Jawa Barat & DKI Jakarta dominan, 5 provinsi

**Speaker notes:** Jelaskan quadrant dari sudut pandang product creator. Hidden Gem = rating tinggi tapi demand belum besar → peluang. Winning Formula → pelajari dan replikasi. Peta menunjukkan konsentrasi seller per kota.

---

## Slide 4: LLM Interface

**Title:** Tanya dalam Bahasa Indonesia, Jawaban Berdasarkan Data

**Bullets:**
- Agent generate SQL → eksekusi ke DuckDB → return data + insight
- ReAct loop: bisa eksplorasi data dulu, tanya balik, chain query
- Unanswerable handling: profit margin, prediksi → ditolak sopan
- Auto-retry jika SQL gagal

**Speaker notes:** Agent tidak bisa jawab tanpa data. Setiap jawaban berbasis SQL yang dieksekusi. Tidak ada halusinasi karena jawaban langsung dari query result. Pertanyaan di luar scope ditolak dengan penjelasan.

---

## Slide 5: Trade-offs, Risks, Next Steps

**Title:** Apa yang Kami Pelajari

**Bullets:**
- Deliberate: SQLite (zero setup), DeepSeek (gratis), prompt engineering (cukup untuk 1 tabel)
- Risiko: data snapshot, single marketplace, tidak ada auth
- Lessons: anti-bot bypass butuh 7 percobaan, prompt engineering cukup untuk schema sederhana
- Next: multi-marketplace, time-series scraping, profit margin estimation

**Speaker notes:** Jelaskan trade-off yang disengaja. Prompt engineering vs semantic layer — untuk 1 tabel, prompt cukup. Anti-bot bypass paling challenging. Kalau lebih banyak waktu: multi-marketplace dan time-series scraping.
