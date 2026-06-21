# Presentation Outline — GT Intelligence

> 5-slide presentation for PT Bangunindo Teknusa Jaya test case
> Speaker notes in Indonesian. Story-driven, not feature-list.
> Target: 10-12 minutes total (2 min per slide, 2-3 min for Q&A)

---

## Slide 1: Problem + Dataset

**Title:** "Riset Pasar yang Butuh Berminggu-minggu, Kami Selesaikan dalam Hitungan Jam"

### Visual
- Left: Manual research workflow (browse marketplace → screenshot → spreadsheet → meeting)
- Right: GT Intelligence workflow (scrape → clean → analyze → ask)
- Bottom: Dataset summary (672 products, 4 subcategories, 32 kota di Jawa)

### Key Points
1. **The problem:** Di bisnis general trade, menentukan produk yang tepat untuk dikembangkan itu sulit. Data tersebar di marketplace, tidak terpusat, dan sulit dikumpulkan oleh non-technical team.
2. **The dataset:** 672 produk food & beverage dari Tokopedia — cokelat, permen, snack — tersebar di 32 kota Jawa. Harga, rating, jumlah terjual, lokasi penjual.
3. **Why F&B:** Kategori dengan volume tinggi, harga terjangkau, target pasar muda. Data paling kaya di Tokopedia.
4. **Key limitation:** Data diambil satu titik waktu (bukan real-time). Hanya Tokopedia (Shopee/Blibli blocked by anti-bot). Ini revenue proxy (harga × terjual), bukan profit margin.

### Speaker Notes (Indonesian)

> "Bayangkan Anda di tim produk PT Bangunindo. Boss bilang: 'Kita mau luncurkan produk snack baru. Cari tahu produk apa yang paling laku, berapa harganya, di mana pasarnya.'
>
> Biasanya, tim akan buka Tokopedia satu-satu, screenshot produk, masukin ke spreadsheet, rapat berjam-jam. Butuh berminggu-minggu.
>
> GT Intelligence mengganti proses itu. Kami scrape 672 produk dari Tokopedia — cokelat, permen, snack — dari 32 kota di Jawa. Data ini langsung masuk ke sistem yang bisa ditanya pakai bahasa sehari-hari.
>
> Kenapa F&B? Karena volumenya tinggi, harganya terjangkau, targetnya anak muda. Dan data Tokopedia paling kaya di kategori ini.
>
> Satu hal yang perlu diingat: data ini snapshot, bukan real-time. Dan yang kita punya itu data penjual, bukan data pembeli. Ini keterbatasan yang kami dokumentasikan."

---

## Slide 2: Architecture + Data Flow

**Title:** "Dari API Tokopedia Sampai Jawaban AI — Seluruh Pipeline dalam Satu Container"

### Visual
- Architecture diagram (simplified):
```
Tokopedia API → Raw JSON → Staging → Clean → LLM Parse → Validate → SQLite
                                                                              ↓
User (Browser) ← Streamlit UI ← GTAgent ← DuckDB ← products.db
```
- Highlight: 6-step data pipeline, 7 validation checks
- Tech stack badges: Python, tokopaedi, Pandas, DeepSeek, DuckDB, Streamlit, Docker

### Key Points
1. **Scraping:** tokopaedi library — mobile API spoofing bypasses Akamai. We tried 7 approaches before finding this. Rate-limited, respectful scraping.
2. **Staging layer:** Raw JSON disimpan dulu sebelum transformasi. Kalau cleaning ada bug, bisa re-run dari staging tanpa re-scrape.
3. **Cleaning + LLM Parse:** Regex + keyword matching untuk parse flavor/weight/variant. DeepSeek V4 Flash untuk yang lebih kompleks. 7 validation checks — schema, types, nulls, ranges, dedup, geography, row count.
4. **Storage:** SQLite (file-based, zero setup, portable). 1 table, 14 columns. Untuk 672 baris, PostgreSQL overkill.
5. **Agent:** GTAgent pakai OpenAI-compatible API (SumoPod DeepSeek V4 Flash). Function calling: `run_sql(query)`. DuckDB sebagai query engine di atas SQLite.
6. **UI:** Streamlit — dashboard-first, chat sebagai side panel. Bukan Chainlit (chat-first) karena UX kita butuh dashboard sebagai landing page.
7. **Deployment:** Single Docker container di SumoPod VPS Jakarta. 2 vCPU, 2GB RAM, Rp 60k/bulan.

### Speaker Notes (Indonesian)

> "Pipeline kami ada 6 langkah. Mari saya bawa dari awal.
>
> Langkah 1: Scrape. Tokopedia punya anti-bot yang sangat ketat — Akamai Bot Manager. Kami coba 7 cara berbeda: GraphQL API, curl_cffi, Playwright, semuanya gagal. Yang berhasil: tokopaedi library, yang spoof mobile user-agent ke API mobile Tokopedia. Desktop diblok, mobile lolos.
>
> Langkah 2: Staging. Raw JSON kami simpan dulu. Kenapa? Kalau di langkah 3 ada bug di cleaning logic, kami bisa re-run dari staging tanpa scrape ulang. Data mentah di-backup.
>
> Langkah 3-4: Cleaning dan LLM Parse. Deduplicate, normalisasi harga ('Rp 15.000' jadi 15000), konversi sold count ('1rb+' jadi 1000). Untuk parse rasa, berat, varian dari nama produk — regex dulu, LLM untuk yang lebih kompleks.
>
> Langkah 5: Validasi. 7 checks — semua harus pass sebelum data masuk SQLite.
>
> Langkah 6: Masuk SQLite. 672 baris, 14 kolom, 1 tabel. Kenapa SQLite? Karena ini MVP — 1000 baris, single user, zero setup. PostgreSQL untuk production.
>
> Untuk agent-nya, kami pakai GTAgent yang memanggil DeepSeek V4 Flash via SumoPod. Gratis, OpenAI-compatible, dan untuk schema sederhana kami, semua model LLM skor 94%+ akurasi SQL.
>
> UI pakai Streamlit — dashboard-first, bukan chat-first. Kenapa? Karena user kami adalah tim bisnis yang butuh overview dulu, baru deep-dive lewat chat.
>
> Semuanya jalan di satu Docker container di VPS Jakarta. Total biaya: Rp 60.000 per bulan."

---

## Slide 3: Analytics Insights

**Title:** "Apa yang Data Ceritakan: 4 Temuan Utama dari 672 Produk"

### Visual
- 4 quadrant layout:
  - Top-left: Subcategory demand chart (snack dominates)
  - Top-right: Opportunity quadrant (demand vs quality scatter)
  - Bottom-left: Geographic distribution (kota-kota di Jawa)
  - Bottom-right: Google Trends overlay

### Key Points

**Finding 1: Snack Mendominasi, Tapi Ada Celah**
- Snack: volume tertinggi (terlaris), tapi persaingan ketat
- Cokelat: demand tinggi, harga premium, rating tinggi → sweet spot
- Permen: volume rendah, tapi underserved → opportunity

**Finding 2: Opportunity Quadrant — Hidden Gems**
- High demand + high quality → "Winning Formula" (pelajari dan replikasi)
- Low demand + high quality → "Hidden Gem" (kembangkan dan promosikan)
- High demand + low quality → "Volume Only" (tingkatkan kualitas)
- Low demand + low quality → "Hindari"
- Temuan: Produk cokelat premium di kategori "Hidden Gem" — rating tinggi, demand belum besar, tapi kualitas sudah bagui. Ini target ideal untuk product development.

**Finding 3: Geografi — Jawa Barat Dominan, Jawa Timur Gap**
- Bandung dan Jakarta: konsentrasi seller tertinggi
- Jawa Timur (Surabaya, Malang): demand ada, seller sedikit → market gap
- Pricing relatif seragam across region → tidak ada pricing arbitrase

**Finding 4: Google Trends Mengkonfirmasi Data Internal**
- Keyword "snack" dan "cokelat" naik di Google Trends sejalan dengan sold count
- Tren musiman terlihat: cokelat naik mendekati hari raya
- Google Trends sebagai sinyal eksternal yang mengkonfirmasi data marketplace

### Speaker Notes (Indonesian)

> "Sekarang yang menarik — apa yang data ceritakan.
>
> Temuan pertama: Snack mendominasi volume. Tapi jangan langsung lompat ke sana. Persaingannya ketat. Yang menarik itu cokelat — demand tinggi, harga premium, rating bagus. Itu sweet spot.
>
> Temuan kedua: Opportunity Quadrant. Ini analisis yang paling powerful. Kami plot setiap produk berdasarkan demand dan kualitas. Yang di kuadran 'Hidden Gem' — rating tinggi tapi demand belum besar — itu target ideal untuk product development. Kenapa? Karena kualitasnya sudah proven, tapi belum banyak kompetitor.
>
> Contoh: produk cokelat premium dari Bandung. Rating 4.8, tapi sold count belum tinggi. Artinya: pasar belum jenuh, kualitas sudah bagus. Kalau Bangunindo masuk ke segmen ini dengan distribusi yang lebih baik, ada peluang besar.
>
> Temuan ketiga: Geografi. Bandung dan Jakarta memang dominan. Tapi lihat Jawa Timur — Surabaya, Malang — demand ada, seller sedikit. Itu market gap. Dan harga relatif seragam across region, jadi tidak ada pricing arbitrase.
>
> Temuan keempat: Google Trends mengkonfirmasi data internal kami. Keyword 'snack' dan 'cokelat' naik di Google sejalan dengan sold count di Tokopedia. Ini validasi eksternal bahwa data kami reliable.
>
> Semua insight ini bisa di-explore lebih dalam lewat chat agent. Tinggal tanya: 'Produk cokelat apa yang paling laku di Bandung?' — agent akan generate SQL, jalankan query, dan kasih jawaban dengan chart."

---

## Slide 4: LLM Interface

**Title:** "Tanya dalam Bahasa Indonesia, Jawaban Berdasarkan Data — Bukan Halusinasi"

### Visual
- Left: Chat interface screenshot (question → SQL → data table → insight → follow-up)
- Right: Grounding diagram (User → MDL → SQL → Execute → Interpret)
- Bottom: "Unanswerable questions" example (profit margin → graceful refusal)

### Key Points

**How the Agent Works (3 Layers of Protection)**

1. **MDL Semantic Layer** — LLM tidak lihat raw database. Yang dia lihat: nama model, kolom, relasi. "Terlaris" = sold_count DESC. "Opportunity" = high demand + few sellers. Business terms mapped to data. Prompt engineering bisa dilupakan; MDL deterministik.

2. **Function Calling + SQL Validation** — Agent tidak bisa jawab langsung. Harus generate SQL dulu, jalankan via `run_sql()`, baru interpret hasilnya. SQL di-eksekusi di DuckDB, bukan di LLM. Kalau SQL salah, error message jelas, agent bisa retry.

3. **Agentic Multi-Step** — Bukan single-shot. Agent bisa: explore data dulu (discovery queries), tanya balik kalau ambigu, chain beberapa query dalam satu jawaban. Max 3 iterasi untuk prevent infinite loops.

**Unanswerable Questions — Handled Gracefully**
- "Berapa profit margin produk X?" → "Data yang kami punya hanya harga jual dan jumlah terjual. Untuk profit margin, Anda perlu data cost dari internal."
- "Berapa inflasi tahun depan?" → "Di luar scope data kami."
- "Produk apa yang akan trending bulan depan?" → "Kami tidak punya data prediktif. Ini data historis."

**Why DeepSeek V4 Flash?**
- BIRD-Interact benchmark: DeepSeek 4.83% vs GPT-5 17.00% pada database kompleks
- TAPI: schema kami 1 tabel, 14 kolom. TokenMix benchmark: semua model 94%+ akurasi pada SQL sederhana
- MDL + dry-plan + guided mode = kompensasi untuk model yang lebih lemah
- Gratis di SumoPod. Kalau tidak cukup, ganti ke O3-Mini ($0.06/task) — satu env var

### Speaker Notes (Indonesian)

> "Ini yang paling penting dari keseluruhan sistem. Bagaimana kami mencegah LLM berhalusinasi.
>
> Lapisan pertama: MDL — Modeling Definition Language. LLM tidak pernah lihat database mentah. Yang dia lihat adalah abstraksi bisnis. Kalau user tanya 'produk terlaris', LLM tahu itu berarti sort by sold_count. Bukan karena di-prompt, tapi karena MDL mendefinisikannya secara deterministik.
>
> Lapisan kedua: Function calling. Agent tidak bisa jawab langsung. Dia harus generate SQL dulu, jalankan lewat function run_sql(), baru interpret hasilnya. SQL dieksekusi di DuckDB, bukan di LLM. Kalau SQL salah, ada error message yang jelas, dan agent bisa retry.
>
> Lapisan ketiga: Agentic multi-step. Bukan single-shot. Agent bisa explore data dulu — misalnya, sebelum jawab 'produk terlaris', dia bisa query dulu berapa total produk di database. Kalau pertanyaan ambigu, dia bisa tanya balik. Max 3 iterasi untuk mencegah infinite loop.
>
> Dan yang paling penting: pertanyaan yang tidak bisa dijawab. 'Berapa profit margin?' — jawabannya: 'Data kami hanya punya harga jual, bukan cost.' Tidak dibuat-buat, tidak ditebak.
>
> Kenapa pakai DeepSeek dan bukan GPT-5? BIRD-Interact benchmark tahun 2026 tunjukkan DeepSeek kalah jauh di database kompleks. TAPI — schema kami 1 tabel, 14 kolom. Di benchmark TokenMix, semua model dapat 94%+ untuk SQL sederhana. MDL, dry-plan, dan guided mode menutupi kekurangan model yang lebih lemah. Dan gratis. Kalau ternyata kurang bagus, ganti ke O3-Mini — satu baris config."

---

## Slide 5: Trade-offs, Risks, Next Steps

**Title:** "Apa yang Kami Pelajari: Trade-off yang Disengaja dan yang Tidak"

### Visual
- Three-column layout:
  - Left: "What's MVP-ready" (green checkmarks)
  - Center: "What's not production-ready" (yellow warnings)
  - Right: "If we had more time" (blue arrows)

### Key Points

**Deliberate Trade-offs (Apa yang Kami Sadar)**
- SQLite vs PostgreSQL → SQLite cukup untuk 672 baris, zero setup, portable
- DeepSeek vs GPT-5 → Schema sederhana, semua model 94%+, cost zero
- Streamlit vs custom React → 3 hari sprint, Streamlit handle dashboard + chat
- Single marketplace vs multi → Tokopedia saja sudah 672 produk, multi-marketplace butuh proxy rotation
- Revenue proxy vs profit margin → Cost data tidak tersedia dari marketplace

**What's Not Production-Ready**
- Data freshness (snapshot, bukan real-time)
- Single marketplace (Shopee/Blibli blocked)
- No auth (single user)
- No monitoring (logs only)
- Manual scraping (not scheduled)
- Product spec parsing (40-65% null)

**What We Learned**
- Anti-bot bypass itu hard. 7 approaches sebelum tokopaedi berhasil.
- MDL > prompt engineering. Deterministic beats probabilistic.
- Simple schema = simple SQL. Jangan over-engineer LLM choice untuk use case sederhana.
- Google Trends sebagai validasi eksternal itu powerful.
- Opportunity quadrant (demand vs quality) adalah insight paling actionable.

**Next Steps (If More Time)**
1. Multi-marketplace (Shopee dengan residential proxy)
2. Time-series scraping (periodic, untuk real trends)
3. Profit margin estimation (input cost data manual)
4. Fine-tuned SLM (Qwen3-6B) untuk SQL generation
5. Demand forecasting model
6. Multi-user auth + RBAC

### Speaker Notes (Indonesian)

> "Terakhir, apa yang kami pelajari.
>
> Beberapa trade-off ini disengaja. SQLite? Untuk 672 baris dan single user, PostgreSQL overkill. Kami sengaja pilih yang paling sederhana yang bisa jalan. DeepSeek? BIRD-Interact 2026 tunjukkan dia kalah jauh dari GPT-5 di database kompleks. Tapi schema kami trivial — 1 tabel, 14 kolom. Di benchmark TokenMix, semua model dapat 94%+ untuk SQL sederhana. Jadi kami pakai yang gratis, dan kalau tidak cukup, ganti ke O3-Mini — satu baris config.
>
> Streamlit? Dalam 3 hari sprint, kami butuh framework yang bisa handle dashboard dan chat sekaligus. Streamlit paling cepat. Custom React? Terlalu mahal untuk timeline ini.
>
> Yang tidak production-ready: data freshness (ini snapshot), single marketplace (Shopee dan Blibli block kami), tidak ada auth, tidak ada monitoring, scraping manual. Semua ini kami dokumentasikan.
>
> Yang paling saya pelajari: anti-bot bypass itu hard. Kami coba 7 cara sebelum tokopaedi berhasil. Dan MDL lebih baik dari prompt engineering — deterministic beats probabilistic. Jangan over-engineer LLM choice untuk use case sederhana.
>
> Next steps: multi-marketplace, time-series scraping, profit margin estimation, dan fine-tuned SLM. Semua ini documented di SPEC.md.
>
> Terima kasih. Ada pertanyaan?"
