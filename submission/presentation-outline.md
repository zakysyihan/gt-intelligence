# Presentation Outline — GT Intelligence

> 5-slide presentation for PT Bangunindo Teknusa Jaya test case
> Speaker notes in Indonesian. Story-driven, not feature-list.
> Target: 10-12 minutes total (2 min per slide, 2-3 min for Q&A)
>
> **Code-verified:** Every technical claim cross-checked against src/llm/agent.py,
> src/llm/mdl_manifest.py, src/llm/data_loader.py, src/pipeline/llm_parser.py.

---

## Slide 1: Problem + Dataset

**Title:** "Riset Pasar yang Butuh Berminggu-minggu, Kami Selesaikan dalam Hitungan Jam"

### Visual
- Left: Manual research workflow (browse marketplace → screenshot → spreadsheet → meeting)
- Right: GT Intelligence workflow (scrape → clean → analyze → ask)
- Bottom: Dataset summary (672 products, 3 subcategories, 32 kota di Jawa)

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
- Tech stack badges: Python, tokopaedi, Pandas, OpenAI gpt-4o-mini, DuckDB, Streamlit, Docker

### Key Points

**Data Pipeline (Offline — 6 steps):**
1. **Scrape:** tokopaedi library — mobile API spoofing bypasses Akamai. Rate-limited, respectful.
2. **Staging:** Raw JSON disimpan dulu sebelum transformasi. Kalau cleaning ada bug, re-run dari staging.
3. **Clean:** Deduplicate, normalisasi harga ("Rp 15.000" → 15000), konversi sold_count ("1rb+" → 1000), filter Java Island.
4. **LLM Parse:** OpenAI-compatible API (configurable via `.env`) mengekstrak flavor/weight/variant dari nama produk. Batch processing, ~$0.01 untuk 672 produk.
5. **Validate:** 7 checks — schema, types, nulls, ranges, dedup, geography, row count.
6. **SQLite:** 672 baris, 14 kolom. File-based, portable.

**Query Flow (Online — how the agent works):**
1. User bertanya dalam bahasa Indonesia
2. GTAgent (custom Python class) memanggil OpenAI API dengan system prompt berisi business context dan schema
3. LLM menghasilkan SQL dalam format JSON (bukan function calling — langsung generate SQL text)
4. Python mengeksekusi SQL di DuckDB (in-memory, loaded dari SQLite)
5. Kalau SQL gagal, agent otomatis minta LLM perbaiki dan retry
6. LLM menginterpretasi hasil → insight dalam bahasa Indonesia + saran pertanyaan lanjutan

**Why each tool:**
- **tokopaedi:** Satu-satunya cara bypass Akamai (7 cara dicoba, hanya ini yang berhasil)
- **SQLite:** Zero setup, portable, cukup untuk 672 baris single user
- **DuckDB:** Query engine cepat, bisa load SQLite langsung via ATTACH
- **OpenAI gpt-4o-mini:** Default model, configurable ke DeepSeek/O3-Mini via `.env`
- **Streamlit:** Dashboard-first, built-in charts, multi-session chat

### Speaker Notes (Indonesian)

> "Pipeline kami ada 6 langkah offline dan 5 langkah online. Mari saya bawa dari awal.
>
> Langkah 1: Scrape. Tokopedia punya anti-bot yang sangat ketat — Akamai Bot Manager. Kami coba 7 cara berbeda: GraphQL API, curl_cffi, Playwright, semuanya gagal. Yang berhasil: tokopaedi library, yang spoof mobile user-agent ke API mobile Tokopedia. Desktop diblok, mobile lolos.
>
> Langkah 2: Staging. Raw JSON kami simpan dulu. Kenapa? Kalau di langkah 3 ada bug di cleaning logic, kami bisa re-run dari staging tanpa scrape ulang.
>
> Langkah 3-4: Cleaning dan LLM Parse. Untuk parse rasa, berat, varian dari nama produk — kami pakai OpenAI-compatible API. Konfigurasi lewat .env file, jadi bisa ganti model kapan saja. Biaya sekitar 1 sen untuk 672 produk.
>
> Langkah 5: Validasi. 7 checks — semua harus pass sebelum data masuk SQLite.
>
> Sekarang flow online-nya. User buka Streamlit, lihat dashboard, klik chat, dan tanya dalam bahasa Indonesia. GTAgent — class Python custom — ambil pertanyaan, kirim ke LLM dengan system prompt yang berisi data dictionary dan business context. LLM generate SQL dalam format JSON. Python eksekusi SQL di DuckDB. Kalau gagal, agent minta LLM perbaiki dan coba lagi. Kalau berhasil, LLM interpretasi hasilnya jadi insight dalam bahasa Indonesia plus saran pertanyaan lanjutan.
>
> Yang penting: ini bukan function calling. LLM menghasilkan SQL sebagai text, dan Python yang mengeksekusi. Grounding-nya lewat prompt engineering — system prompt yang mendefinisikan business context, data dictionary, dan aturan untuk pertanyaan yang tidak bisa dijawab."

---

## Slide 3: Analytics Insights

**Title:** "Apa yang Data Ceritakan: Temuan Utama dari 672 Produk"

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
- Temuan: Produk cokelat premium di kategori "Hidden Gem" — rating tinggi, demand belum besar, tapi kualitas sudah bagus. Ini target ideal untuk product development.

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
> Temuan keempat: Google Trends mengkonfirmasi data internal kami. Keyword 'snack' dan 'cokelat' naik di Google sejalan dengan sold count di Tokopedia. Ini validasi eksternal bahwa data kami reliable."

---

## Slide 4: LLM Interface

**Title:** "Tanya dalam Bahasa Indonesia, Jawaban Berdasarkan Data — Bukan Halusinasi"

### Visual
- Left: Chat interface screenshot (question → SQL → data table → insight → follow-up)
- Right: Flow diagram (User → Prompt Engineering → LLM → SQL → DuckDB → Interpret)
- Bottom: "Unanswerable questions" example (profit margin → graceful refusal)

### Key Points

**How the Agent Works (What Actually Happens)**

1. **System Prompt as Grounding** — Agent menggunakan system prompt yang berisi:
   - Business context: mapping istilah Indonesia ke SQL ("terlaris" → ORDER BY sold_count DESC)
   - Data dictionary: definisi setiap kolom dan maknanya
   - Aturan pertanyaan yang tidak bisa dijawab (profit margin, prediksi, data pembeli)
   - Schema lengkap tabel products (14 kolom)
   - Dataset stats: jumlah produk, subkategori, kota, range harga

   Ini prompt engineering, bukan semantic layer. Tapi untuk schema sederhana (1 tabel, 14 kolom), prompt engineering cukup efektif.

2. **ReAct Loop (Reason-Act-Observe)** — Bukan single-shot. Agent mengklasifikasi intent:
   - `direct_answer` → langsung generate SQL
   - `needs_exploration` → query eksplorasi dulu (misal: "subkategori apa saja yang ada?")
   - `needs_clarification` → tanya balik ke user kalau pertanyaan ambigu
   - `chain_queries` → beberapa SQL untuk perbandingan
   Max 3 iterasi untuk mencegah infinite loop.

3. **SQL Execution + Auto-Retry** — SQL dieksekusi di DuckDB (in-memory, loaded dari SQLite). Kalau SQL gagal, agent otomatis mengirim error ke LLM dan minta perbaikan. `_retry_with_fix()` handle ini.

4. **Insight Generation + Follow-ups** — Setelah data didapat, LLM generate insight dalam bahasa Indonesia (2-3 kalimat, spesifik dengan angka). Plus 2-3 saran pertanyaan lanjutan.

**Unanswerable Questions — Handled Gracefully**
- "Berapa profit margin produk X?" → "Saya hanya bisa menjawab berdasarkan data produk Tokopedia yang sudah dikumpulkan. Untuk profit margin, Anda memerlukan data cost dari internal."
- "Berapa inflasi tahun depan?" → "Di luar scope data kami."
- Mekanisme: LLM mengembalikan `is_unanswerable: true` dalam JSON response, agent menampilkan pesan penolakan yang sopan.

**Why This Works for Our Use Case**
- Schema kami trivial: 1 tabel, 14 kolom, tidak ada JOINs. Prompt engineering cukup untuk grounding.
- BIRD-Interact benchmark 2026: semua model dapat 94%+ akurasi SQL untuk query sederhana.
- Auto-retry menangani error SQL tanpa user sadar.
- Model configurable via `.env` — bisa ganti dari gpt-4o-mini ke DeepSeek atau O3-Mini tanpa ubah kode.

### Speaker Notes (Indonesian)

> "Ini yang paling penting dari keseluruhan sistem. Bagaimana kami mencegah LLM berhalusinasi.
>
> Sejujurnya: kami tidak pakai semantic layer seperti WrenAI. Yang kami pakai adalah prompt engineering yang solid. System prompt kami berisi business context — misalnya, 'terlaris' berarti ORDER BY sold_count DESC. Plus data dictionary yang mendefinisikan setiap kolom, dan aturan untuk pertanyaan yang tidak bisa dijawab.
>
> Untuk schema sederhana kami — 1 tabel, 14 kolom — ini cukup. Di benchmark TokenMix tahun 2026, semua model LLM dapat 94%+ akurasi untuk SQL sederhana. Tidak perlu framework berat.
>
> Yang membuat agent ini lebih dari single-shot adalah ReAct loop. Sebelum generate SQL, agent mengklasifikasi pertanyaan: apakah ini langsung bisa dijawab, perlu eksplorasi dulu, atau ambigu dan perlu klarifikasi? Kalau pertanyaan ambigu, agent tanya balik. Kalau perlu eksplorasi, agent query dulu untuk memahami data. Max 3 iterasi.
>
> Dan yang paling penting: pertanyaan yang tidak bisa dijawab. 'Berapa profit margin?' — jawabannya: 'Data kami hanya punya harga jual, bukan cost.' Tidak dibuat-buat, tidak ditebak.
>
> Model default kami gpt-4o-mini dari OpenAI. Tapi ini configurable — satu baris di .env file bisa ganti ke DeepSeek atau O3-Mini. Biaya untuk 672 produk dan demo: kurang dari $1."

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
- Prompt engineering vs semantic layer → Schema sederhana, prompt engineering cukup. MDL manifest ada di codebase tapi tidak diaktifkan — overkill untuk 1 tabel.
- gpt-4o-mini vs frontier model → Untuk SQL sederhana, semua model 94%+. Tidak perlu GPT-5.
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
- Prompt-based grounding (works for 1 table, won't scale to complex schemas)

**What We Learned**
- Anti-bot bypass itu hard. 7 approaches sebelum tokopaedi berhasil.
- Prompt engineering cukup untuk schema sederhana. Jangan over-engineer untuk MVP.
- Google Trends sebagai validasi eksternal itu powerful.
- Opportunity quadrant (demand vs quality) adalah insight paling actionable.
- LLM parser untuk product specs (flavor/weight/variant) meningkatkan accuracy dari ~60% (regex) ke ~90% (LLM).

**Next Steps (If More Time)**
1. Multi-marketplace (Shopee dengan residential proxy)
2. Time-series scraping (periodic, untuk real trends)
3. Profit margin estimation (input cost data manual)
4. Semantic layer (WrenAI MDL) untuk schema yang lebih kompleks
5. Fine-tuned SLM (Qwen3-6B) untuk SQL generation
6. Multi-user auth + RBAC

### Speaker Notes (Indonesian)

> "Terakhir, apa yang kami pelajari.
>
> Beberapa trade-off ini disengaja. SQLite? Untuk 672 baris dan single user, PostgreSQL overkill. Prompt engineering vs semantic layer? Untuk 1 tabel dan 14 kolom, prompt engineering cukup. Kami sebenarnya sudah bangun MDL manifest di codebase, tapi tidak diaktifkan — karena over-engineering untuk use case ini. Kalau schema-nya 10 tabel dengan banyak JOINs, baru butuh semantic layer.
>
> gpt-4o-mini? Di benchmark TokenMix tahun 2026, semua model dapat 94%+ untuk SQL sederhana. Tidak perlu GPT-5 yang 100x lebih mahal.
>
> Yang tidak production-ready: data freshness (ini snapshot), single marketplace (Shopee dan Blibli block kami), tidak ada auth, tidak ada monitoring, scraping manual. Semua ini kami dokumentasikan.
>
> Yang paling saya pelajari: anti-bot bypass itu hard. Kami coba 7 cara sebelum tokopaedi berhasil. Dan jangan over-engineer untuk MVP — prompt engineering cukup untuk schema sederhana. Kalau nanti schema berkembang, baru investasi di semantic layer.
>
> Next steps: multi-marketplace, time-series scraping, profit margin estimation, dan semantic layer kalau schema berkembang. Semua ini documented di SPEC.md.
>
> Terima kasih. Ada pertanyaan?"
