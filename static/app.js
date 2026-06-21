/* ---------------------------------------------------------------------------
   GT Intelligence — Frontend App
   Dashboard + Chat with agentic AI
   --------------------------------------------------------------------------- */

const API = '';  // Same origin
let currentSession = null;
let chatOpen = false;
let activeFilters = { subcategories: [], province: '' };

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
    loadFilters().then(() => loadDashboard());
    loadSessions();
});

// ---------------------------------------------------------------------------
// Filters
// ---------------------------------------------------------------------------

async function loadFilters() {
    try {
        const res = await fetch(`${API}/api/dashboard/filters`);
        const data = await res.json();
        renderMultiselect(data.subcategories || []);
        const sel = document.getElementById('filter-province');
        if (sel) {
            (data.provinces || []).forEach(p => {
                const opt = document.createElement('option');
                opt.value = p;
                opt.textContent = p;
                sel.appendChild(opt);
            });
        }
    } catch (err) {
        console.error('Failed to load filters:', err);
    }
}

function renderMultiselect(options) {
    const container = document.getElementById('filter-subcategory');
    container.innerHTML = `
        <button class="multiselect-btn" onclick="this.nextElementSibling.classList.toggle('open')">
            <span id="ms-label">Semua</span> <span>▾</span>
        </button>
        <div class="multiselect-dropdown" id="ms-dropdown">
            ${options.map(o => `
                <label class="multiselect-option">
                    <input type="checkbox" value="${o}" onchange="updateMultiselect()"> ${o}
                </label>
            `).join('')}
        </div>
    `;
    // Close dropdown on outside click
    document.addEventListener('click', (e) => {
        if (!container.contains(e.target)) {
            container.querySelector('.multiselect-dropdown')?.classList.remove('open');
        }
    });
}

function updateMultiselect() {
    const checkboxes = document.querySelectorAll('#ms-dropdown input[type="checkbox"]');
    const selected = Array.from(checkboxes).filter(cb => cb.checked).map(cb => cb.value);
    const label = document.getElementById('ms-label');
    label.textContent = selected.length ? selected.join(', ') : 'Semua';
    activeFilters.subcategories = selected;
    applyFilters();
}

function applyFilters() {
    const province = document.getElementById('filter-province').value;
    activeFilters.province = province;
    loadDashboard();
}

function resetFilters() {
    activeFilters = { subcategories: [], province: '' };
    document.querySelectorAll('#ms-dropdown input[type="checkbox"]').forEach(cb => cb.checked = false);
    document.getElementById('ms-label').textContent = 'Semua';
    document.getElementById('filter-province').value = '';
    loadDashboard();
}

function getFilterParams() {
    const params = new URLSearchParams();
    if (activeFilters.subcategories.length) {
        params.set('subcategories', activeFilters.subcategories.join(','));
    }
    if (activeFilters.province) {
        params.set('province', activeFilters.province);
    }
    return params.toString();
}

// ---------------------------------------------------------------------------
// Dashboard
// ---------------------------------------------------------------------------

async function loadDashboard() {
    const loading = document.getElementById('dashboard-loading');
    const content = document.getElementById('dashboard-content');

    try {
        const fp = getFilterParams();
        const qs = fp ? `?${fp}` : '';
        const [dashRes, quadRes, revRes] = await Promise.all([
            fetch(`${API}/api/dashboard${qs}`).then(r => r.json()),
            fetch(`${API}/api/dashboard/quadrant${qs}`).then(r => r.json()),
            fetch(`${API}/api/dashboard/revenue${qs}`).then(r => r.json()),
        ]);

        renderMetrics(dashRes);
        renderSubcategoryChart(dashRes.subcategory_demand);
        renderPriceDemandChart(dashRes.price_demand);
        renderQuadrantChart(quadRes.products || []);
        renderDemandPriceQuadrant(revRes.products || []);

        loading.style.display = 'none';
        content.style.display = 'block';
    } catch (err) {
        loading.innerHTML = `<p style="color:red;">Gagal memuat dashboard: ${err.message}</p>`;
    }
}

function renderMetrics(dash) {
    const grid = document.getElementById('metrics-grid');
    const topSub = dash.top_subcategory || ['', 0];
    const harga = dash.harga_diminati || ['-', 0];
    const metrics = [
        { label: '📦 Total Produk', value: (dash.total_products || 0).toLocaleString() },
        { label: '🏪 Total Toko', value: (dash.total_shops || 0).toLocaleString() },
        { label: '📍 Total Kota', value: (dash.total_cities || 0).toLocaleString() },
        { label: '💰 Harga Diminati', value: harga[0] },
    ];

    grid.innerHTML = metrics.map(m => `
        <div class="metric-card">
            <div class="metric-label">${m.label}</div>
            <div class="metric-value">${m.value}</div>
        </div>
    `).join('');

    // Data quality indicator
    const qualityEl = document.getElementById('data-quality');
    if (qualityEl && dash.data_quality_msg) {
        const color = dash.data_quality === 'insufficient' ? '#dc2626' : '#d97706';
        const icon = dash.data_quality === 'insufficient' ? '⚠️' : '⚡'
        qualityEl.innerHTML = `<div style="background:${color}15;border:1px solid ${color}40;border-radius:8px;padding:8px 14px;font-size:0.82rem;color:${color};display:flex;align-items:center;gap:8px;">${icon} ${dash.data_quality_msg}</div>`;
        qualityEl.style.display = 'block';
    } else if (qualityEl) {
        qualityEl.innerHTML = '';
        qualityEl.style.display = 'none';
    }
}

// ---------------------------------------------------------------------------
// Charts (Plotly)
// ---------------------------------------------------------------------------

const CHART_COLORS = ['#2563eb', '#7c3aed', '#ec4899', '#f59e0b', '#10b981', '#ef4444'];
const CHART_LAYOUT = {
    font: { family: 'Inter, sans-serif', size: 12 },
    paper_bgcolor: 'white',
    plot_bgcolor: 'white',
    margin: { l: 50, r: 30, t: 10, b: 40 },
};

// Wrapper: Plotly.newPlot + auto-resize to prevent clipping
function plotChart(divId, data, layout, config) {
    Plotly.newPlot(divId, data, layout, config).then(() => {
        Plotly.Plots.resize(document.getElementById(divId));
    });
}

function renderSubcategoryChart(data) {
    if (!data || !data.length) return;
    const labels = data.map(r => r[0]);
    const values = data.map(r => r[1]);
    const colors = labels.map((_, i) => CHART_COLORS[i % CHART_COLORS.length]);

    plotChart('chart-subcategory', [{
        type: 'bar', x: labels, y: values,
        marker: { color: colors },
        text: values.map(v => v.toLocaleString()),
        textposition: 'outside',
        cliponaxis: false,
    }], {
        ...CHART_LAYOUT,
        yaxis: { title: 'Total Terjual', gridcolor: '#e2e8f0' },
        showlegend: false,
        margin: { l: 50, r: 30, t: 40, b: 40 },
    }, { responsive: true, displayModeBar: false });
}

function renderPriceDemandChart(data) {
    if (!data || !data.length) return;
    const labels = data.map(r => r[0]);
    const demands = data.map(r => r[1]);
    const counts = data.map(r => r[2]);

    plotChart('chart-price', [{
        type: 'bar', x: labels, y: demands,
        marker: { color: '#2563eb' },
        text: demands.map(v => v.toLocaleString()),
        textposition: 'outside',
        cliponaxis: false,
        name: 'Total Demand',
    }], {
        ...CHART_LAYOUT,
        yaxis: { title: 'Total Demand (terjual)', gridcolor: '#e2e8f0' },
        xaxis: { title: 'Rentang Harga (IDR)' },
        showlegend: false,
        height: 300,
        margin: { l: 50, r: 50, t: 40, b: 60 },
    }, { responsive: true, displayModeBar: false });
}

function median(arr) {
    const s = [...arr].sort((a, b) => a - b);
    const mid = Math.floor(s.length / 2);
    return s.length % 2 ? s[mid] : (s[mid - 1] + s[mid]) / 2;
}

function renderQuadrantChart(products) {
    if (!products || !products.length) return;
    const subcats = [...new Set(products.map(p => p.subcategory))];
    const traces = subcats.map((sc, i) => {
        const pts = products.filter(p => p.subcategory === sc);
        return {
            type: 'scatter', mode: 'markers',
            name: sc,
            x: pts.map(p => p.sold_count),
            y: pts.map(p => p.rating),
            text: pts.map(p => p.name.substring(0, 30)),
            marker: { size: 8, color: CHART_COLORS[i % CHART_COLORS.length], opacity: 0.7 },
        };
    });

    // Dynamic thresholds using median
    const soldCounts = products.map(p => p.sold_count);
    const ratings = products.map(p => p.rating);
    const medX = median(soldCounts);
    const medY = median(ratings);
    const maxX = Math.max(...soldCounts);
    const padX = maxX * 0.05;

    const shapes = [
        { type: 'line', x0: medX, x1: medX, y0: 0, y1: 5.5, line: { color: '#94a3b8', dash: 'dash', width: 1 } },
        { type: 'line', x0: 0, x1: maxX + padX, y0: medY, y1: medY, line: { color: '#94a3b8', dash: 'dash', width: 1 } },
    ];

    // Place labels at the center of each quadrant
    const xMid1 = medX / 2;
    const xMid2 = medX + (maxX - medX) / 2;
    const yMidLow = medY / 2;
    const yMidHigh = medY + (5.5 - medY) / 2;

    const annotations = [
        { x: xMid2, y: yMidHigh, text: '⭐ Winning Formula', showarrow: false, font: { size: 10, color: '#059669' } },
        { x: xMid1, y: yMidHigh, text: '💎 Hidden Gem', showarrow: false, font: { size: 10, color: '#2563eb' } },
        { x: xMid2, y: yMidLow, text: '⚠️ Volume Only', showarrow: false, font: { size: 10, color: '#d97706' } },
        { x: xMid1, y: yMidLow, text: '❌ Avoid', showarrow: false, font: { size: 10, color: '#dc2626' } },
    ];

    plotChart('chart-quadrant', traces, {
        ...CHART_LAYOUT,
        xaxis: { title: 'Demand (sold_count)', gridcolor: '#e2e8f0' },
        yaxis: { title: 'Quality (rating)', range: [0, 5.5], gridcolor: '#e2e8f0' },
        shapes, annotations,
        height: 300,
    }, { responsive: true, displayModeBar: false });
}

function renderDemandPriceQuadrant(products) {
    if (!products || !products.length) return;
    const subcats = [...new Set(products.map(p => p.subcategory))];
    const traces = subcats.map((sc, i) => {
        const pts = products.filter(p => p.subcategory === sc);
        return {
            type: 'scatter', mode: 'markers',
            name: sc,
            x: pts.map(p => p.price),
            y: pts.map(p => p.sold_count),
            text: pts.map(p => p.name.substring(0, 25)),
            marker: { size: 8, color: CHART_COLORS[i % CHART_COLORS.length], opacity: 0.7 },
        };
    });

    const prices = products.map(p => p.price);
    const sold = products.map(p => p.sold_count);
    const medX = median(prices);
    const medY = median(sold);
    const maxX = Math.max(...prices);
    const maxY = Math.max(...sold);
    const padX = maxX * 0.05;

    const shapes = [
        { type: 'line', x0: medX, x1: medX, y0: 0, y1: maxY * 1.05, line: { color: '#94a3b8', dash: 'dash', width: 1 } },
        { type: 'line', x0: 0, x1: maxX + padX, y0: medY, y1: medY, line: { color: '#94a3b8', dash: 'dash', width: 1 } },
    ];

    const xMid1 = medX / 2;
    const xMid2 = medX + (maxX - medX) / 2;
    const yMidLow = medY / 2;
    const yMidHigh = medY + (maxY - medY) / 2;

    const annotations = [
        { x: xMid2, y: yMidHigh, text: '⭐ High Value', showarrow: false, font: { size: 10, color: '#059669' } },
        { x: xMid1, y: yMidHigh, text: '💎 Budget Volume', showarrow: false, font: { size: 10, color: '#2563eb' } },
        { x: xMid2, y: yMidLow, text: '⚠️ Expensive Niche', showarrow: false, font: { size: 10, color: '#d97706' } },
        { x: xMid1, y: yMidLow, text: '❌ Avoid', showarrow: false, font: { size: 10, color: '#dc2626' } },
    ];

    plotChart('chart-distribution', traces, {
        ...CHART_LAYOUT,
        xaxis: { title: 'Harga (IDR)', gridcolor: '#e2e8f0' },
        yaxis: { title: 'Demand (terjual)', gridcolor: '#e2e8f0' },
        shapes, annotations,
        height: 300,
    }, { responsive: true, displayModeBar: false });
}

// ---------------------------------------------------------------------------
// Chat
// ---------------------------------------------------------------------------

function toggleChat() {
    chatOpen = !chatOpen;
    const panel = document.getElementById('chat-panel');
    const btn = document.getElementById('chat-toggle');
    const layout = document.getElementById('main-layout');

    if (chatOpen) {
        panel.style.display = 'flex';
        btn.textContent = '✕ Tutup Chat';
        layout.style.display = 'flex';
    } else {
        panel.style.display = 'none';
        btn.textContent = '💬 Buka Chat';
    }

    // Trigger Plotly resize after layout change
    setTimeout(() => window.dispatchEvent(new Event('resize')), 200);
}

async function loadSessions() {
    try {
        const res = await fetch(`${API}/api/sessions`);
        const data = await res.json();
        const select = document.getElementById('session-select');
        select.innerHTML = data.sessions.map(s =>
            `<option value="${s.id}" ${s.id === currentSession ? 'selected' : ''}>${s.title}</option>`
        ).join('');

        if (!currentSession && data.sessions.length) {
            currentSession = data.sessions[0].id;
            loadSessionHistory(currentSession);
        }
    } catch (err) {
        console.error('Failed to load sessions:', err);
    }
}

async function loadSessionHistory(sessionId) {
    try {
        const res = await fetch(`${API}/api/sessions/${sessionId}`);
        const data = await res.json();
        const container = document.getElementById('chat-messages');

        if (!data.messages.length) {
            container.innerHTML = `
                <div class="empty-state">
                    <p>💬 Tanya tentang data pasar Indonesia</p>
                    <p class="text-muted">Contoh: "Produk mana yang paling menguntungkan?"</p>
                </div>`;
            return;
        }

        container.innerHTML = '';
        data.messages.forEach(msg => appendMessage(msg));
        container.scrollTop = container.scrollHeight;
    } catch (err) {
        console.error('Failed to load session:', err);
    }
}

async function newSession() {
    try {
        const res = await fetch(`${API}/api/sessions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: 'Sesi Baru' }),
        });
        const data = await res.json();
        currentSession = data.session_id;
        await loadSessions();
        document.getElementById('chat-messages').innerHTML = `
            <div class="empty-state">
                <p>💬 Tanya tentang data pasar Indonesia</p>
                <p class="text-muted">Contoh: "Produk mana yang paling menguntungkan?"</p>
            </div>`;
    } catch (err) {
        console.error('Failed to create session:', err);
    }
}

async function switchSession(sessionId) {
    currentSession = sessionId;
    await loadSessionHistory(sessionId);
}

function askQuick(prompt) {
    document.getElementById('chat-input').value = prompt;
    sendMessage();
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const msg = input.value.trim();
    if (!msg) return;

    if (!currentSession) await newSession();

    input.value = '';
    appendMessage({ role: 'user', content: msg });
    scrollToBottom();

    // Show loading
    const loadingId = showLoading();

    try {
        const res = await fetch(`${API}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: currentSession, message: msg }),
        });
        const data = await res.json();

        removeLoading(loadingId);
        appendMessage(data.message);
        scrollToBottom();

        // Update session title
        if (data.title) {
            const select = document.getElementById('session-select');
            const opt = select.querySelector(`option[value="${currentSession}"]`);
            if (opt) opt.textContent = data.title;
        }
    } catch (err) {
        removeLoading(loadingId);
        appendMessage({ role: 'assistant', error: `Gagal: ${err.message}` });
        scrollToBottom();
    }
}

function appendMessage(msg) {
    const container = document.getElementById('chat-messages');
    const emptyState = container.querySelector('.empty-state');
    if (emptyState) emptyState.remove();

    const div = document.createElement('div');

    if (msg.role === 'user') {
        div.className = 'msg msg-user';
        div.textContent = msg.content;
    } else if (msg.error) {
        div.className = 'msg msg-error';
        div.innerHTML = `<div class="msg-label">🤖 Analis</div>${msg.error}`;
    } else {
        div.className = 'msg msg-assistant';
        let html = '<div class="msg-label">🤖 Analis</div>';

        // SQL (collapsible)
        if (msg.sql) {
            html += `<div class="sql-block collapsed" onclick="this.classList.toggle('expanded');this.classList.toggle('collapsed')">${escapeHtml(msg.sql)}</div>`;
        }

        // Data table
        if (msg.data && msg.data.length) {
            html += renderTable(msg.data, msg.columns);
        }

        // Insight
        if (msg.insight) {
            html += `<div class="insight-box">💡 ${msg.insight}</div>`;
        }

        // Chart button
        if (msg.data && msg.chart_type && msg.chart_type !== 'table') {
            const chartId = 'chat-chart-' + Date.now();
            html += `<button class="chart-expand-btn" onclick="expandChart('${chartId}', '${msg.chart_type}', '${escapeAttr(msg.content || '')}')">📊 Tampilkan Chart</button>`;
            html += `<div id="${chartId}" style="display:none;"></div>`;
        }

        // Follow-ups
        if (msg.follow_ups && msg.follow_ups.length) {
            html += '<div class="followups">';
            msg.follow_ups.forEach(fu => {
                html += `<button class="followup-btn" onclick="askQuick('${escapeAttr(fu)}')">➡️ ${escapeHtml(fu)}</button>`;
            });
            html += '</div>';
        }

        div.innerHTML = html;
    }

    container.appendChild(div);
}

function renderTable(data, columns) {
    if (!data || !data.length) return '';
    const cols = columns || Object.keys(data[0]);
    let html = '<div style="max-height:180px;overflow-y:auto;margin:8px 0;border:1px solid #e2e8f0;border-radius:8px;">';
    html += '<table class="data-table"><thead><tr>';
    cols.forEach(c => html += `<th>${escapeHtml(c.replace(/_/g, ' '))}</th>`);
    html += '</tr></thead><tbody>';
    data.slice(0, 20).forEach(row => {
        html += '<tr>';
        cols.forEach(c => {
            let val = row[c];
            if (typeof val === 'number') val = val.toLocaleString();
            html += `<td>${escapeHtml(String(val ?? ''))}</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody></table></div>';
    return html;
}

function expandChart(containerId, chartType, question) {
    const container = document.getElementById(containerId);
    if (container.style.display !== 'none') {
        container.style.display = 'none';
        return;
    }
    container.style.display = 'block';
    // Placeholder — real chart data comes from chat response
    container.innerHTML = '<div style="text-align:center;padding:20px;color:#94a3b8;">📊 Chart akan muncul di sini</div>';
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function showLoading() {
    const container = document.getElementById('chat-messages');
    const id = 'loading-' + Date.now();
    const div = document.createElement('div');
    div.id = id;
    div.className = 'msg msg-assistant';
    div.innerHTML = '<div class="spinner-small" style="margin-right:8px;"></div> Menganalisis data...';
    container.appendChild(div);
    scrollToBottom();
    return id;
}

function removeLoading(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function scrollToBottom() {
    const container = document.getElementById('chat-messages');
    container.scrollTop = container.scrollHeight;
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function escapeAttr(str) {
    return str.replace(/'/g, "\\'").replace(/"/g, '&quot;');
}
