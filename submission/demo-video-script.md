# Demo Video Script — GT Intelligence

> 7-10 minutes. Screen recording + voiceover. Indonesian.

---

## Opening (0:00 - 0:30)

"Assalamualaikum. Nama saya Zaky Syihan. Ini adalah demo GT Intelligence — sistem market intelligence yang membantu tim produk general trade menentukan produk yang tepat untuk dikembangkan."

## Problem (0:30 - 1:30)

"Bisnis general trade punya masalah: data produk tersebar di marketplace, tidak terpusat, dan sulit dikumpulkan oleh non-technical team. Tim produk butuh berminggu-minggu untuk riset manual. Kami selesaikan dalam hitungan jam."

Show: Tokopedia manual browsing (the "before" experience)

## Data Pipeline (1:30 - 3:00)

Show terminal:
```bash
python3 -m src.pipeline.run_pipeline
```

"Pipeline kami: scrape dari Tokopedia pakai tokopaedi library — mobile API spoofing yang bypass anti-bot Akamai. 672 produk food & beverage dari 32 kota di Jawa. Setiap produk: nama, harga, rating, jumlah terjual, lokasi penjual, dan spesifikasi produk."

Show: raw data → cleaned data → SQLite

## Dashboard (3:00 - 5:00)

Open https://gt-intelligence.biz.id

"Dashboard menampilkan overview pasar. 672 produk, total demand, harga rata-rata. Chart per subkategori — snack mendominasi. Distribusi harga — sweet spot di 15K-30K. Geographic — Surabaya dan Bandung dominan."

Show: hover over charts, filter by subcategory

"Yang menarik: quadrant analysis. Demand vs Quality. Di sini kita bisa lihat produk mana yang punya demand tinggi tapi rating rendah — ini peluang untuk bikin produk yang lebih baik."

## AI Analyst Agent (5:00 - 7:00)

Open side panel chat.

"Tanya dalam bahasa Indonesia."

Type: "Produk cokelat apa yang paling laku di Jakarta?"

Show: SQL generated → data table → chart → insight in Indonesian

"Agent generate SQL, eksekusi ke database, dan kasih jawaban dengan data. Bukan halusinasi — semua berdasarkan data yang ada."

Type: "Apa spesifikasi yang harus kami kembangkan?"

Show: agent analyzes specs (flavor, weight) and recommends

"Follow-up suggestions muncul setelah setiap jawaban."

## Limitations & Trade-offs (7:00 - 8:30)

"Beberapa limitasi yang perlu diketahui:"
- "Data snapshot — bukan real-time"
- "Hanya Tokopedia — Shopee dan Blibli blocked by anti-bot"
- "Revenue proxy, bukan profit margin — cost data tidak tersedia"
- "Spec parsing best-effort — 60% akurasi"

"Trade-off yang disengaja: SQLite untuk MVP, DeepSeek karena gratis dan cukup untuk schema sederhana, prompt engineering karena 1 tabel 14 kolom tidak butuh semantic layer."

## Closing (8:30 - 9:00)

"GT Intelligence membuktikan bahwa dengan data engineering yang solid, LLM yang grounded, dan UI yang sederhana, tim produk bisa membuat keputusan berbasis data — bukan asumsi. Terima kasih."
