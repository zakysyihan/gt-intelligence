/* ---------------------------------------------------------------------------
   GT Intelligence — Frontend App
   Dashboard + Chat with agentic AI
   --------------------------------------------------------------------------- */

const API = '';  // Same origin
let currentSession = null;
let chatOpen = false;
let activeFilters = { subcategories: [], provinces: [], cities: [] };
let filterData = { subcategories: [], provinces: [], citiesByProvince: {} };

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
        filterData = data;

        // Render subcategory multiselect
        renderMultiselect('filter-subcategory', 'ms-subcat', data.subcategories || [], (selected) => {
            activeFilters.subcategories = selected;
            applyFilters();
        });

        // Render province multiselect
        renderMultiselect('filter-province', 'ms-province', data.provinces || [], (selected) => {
            activeFilters.provinces = selected;
            updateCityOptions();
            activeFilters.cities = [];
            applyFilters();
        });

        // Initialize city multiselect (empty until province selected)
        renderMultiselect('filter-city', 'ms-city', [], (selected) => {
            activeFilters.cities = selected;
            applyFilters();
        });
    } catch (err) {
        console.error('Failed to load filters:', err);
    }
}

function renderMultiselect(containerId, msId, options, onChange) {
    const container = document.getElementById(containerId);
    container.innerHTML = `
        <button class="multiselect-btn" onclick="toggleDropdown('${msId}')">
            <span id="${msId}-label">Semua</span> <span>▾</span>
        </button>
        <div class="multiselect-dropdown" id="${msId}">
            ${options.map(o => `
                <label class="multiselect-option">
                    <input type="checkbox" value="${o}" onchange="onMsChange('${msId}')"> ${o}
                </label>
            `).join('')}
        </div>
    `;
    // Store callback
    container._onChange = onChange;
    // Close on outside click
    document.addEventListener('click', (e) => {
        if (!container.contains(e.target)) {
            container.querySelector('.multiselect-dropdown')?.classList.remove('open');
        }
    });
}

function toggleDropdown(msId) {
    document.getElementById(msId)?.classList.toggle('open');
}

function onMsChange(msId) {
    const dropdown = document.getElementById(msId);
    const checkboxes = dropdown.querySelectorAll('input[type="checkbox"]');
    const selected = Array.from(checkboxes).filter(cb => cb.checked).map(cb => cb.value);
    const label = document.getElementById(msId + '-label');
    label.textContent = selected.length ? selected.join(', ') : 'Semua';

    // Find the container and call its callback
    const container = dropdown.parentElement;
    if (container._onChange) container._onChange(selected);
}

function updateCityOptions() {
    // Collect all cities from selected provinces
    const selectedProvinces = activeFilters.provinces;
    let cities = [];
    if (selectedProvinces.length) {
        selectedProvinces.forEach(p => {
            (filterData.citiesByProvince?.[p] || []).forEach(c => {
                if (!cities.includes(c)) cities.push(c);
            });
        });
    } else {
        // No province selected → show all cities
        Object.values(filterData.citiesByProvince || {}).forEach(arr => {
            arr.forEach(c => { if (!cities.includes(c)) cities.push(c); });
        });
    }
    cities.sort();

    // Re-render city multiselect
    const container = document.getElementById('filter-city');
    renderMultiselect('filter-city', 'ms-city', cities, (selected) => {
        activeFilters.cities = selected;
        applyFilters();
    });
}

function applyFilters() {
    loadDashboard();
}

function resetFilters() {
    activeFilters = { subcategories: [], provinces: [], cities: [] };
    // Reset all checkboxes
    document.querySelectorAll('.multiselect-dropdown input[type="checkbox"]').forEach(cb => cb.checked = false);
    document.querySelectorAll('.multiselect-btn span:first-child').forEach(el => el.textContent = 'Semua');
    // Reset city options to all
    updateCityOptions();
    loadDashboard();
}

function getFilterParams() {
    const params = new URLSearchParams();
    if (activeFilters.subcategories.length) {
        params.set('subcategories', activeFilters.subcategories.join(','));
    }
    if (activeFilters.provinces.length) {
        params.set('province', activeFilters.provinces.join(','));
    }
    if (activeFilters.cities.length) {
        params.set('city', activeFilters.cities.join(','));
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
        { label: '💰 Harga Terlaris', value: harga[0] },
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
        const bg = dash.data_quality === 'insufficient' ? '#fef2f2' : '#fffbeb';
        const border = dash.data_quality === 'insufficient' ? '#fecaca' : '#fde68a';
        const icon = dash.data_quality === 'insufficient' ? '⚠️' : '⚡'
        qualityEl.innerHTML = `
            <div style="background:${bg};border:1px solid ${border};border-radius:10px;padding:12px 18px;font-size:0.85rem;color:${color};display:flex;align-items:center;gap:10px;font-weight:500;">
                <span style="font-size:1.1rem;">${icon}</span>
                <span>${dash.data_quality_msg}</span>
            </div>`;
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
        yaxis: { title: 'Produk Terjual', gridcolor: '#e2e8f0' },
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
        yaxis: { title: 'Produk Terjual', gridcolor: '#e2e8f0' },
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

// Hardcoded thresholds (global, static — not affected by filters)
// Based on Indonesian F&B marketplace research:
// - Demand: 10 units/day (300/month) = moderate seller threshold
// - Rating: 4.5 = quality cutoff (above = good quality)
// - Price: 50,000 IDR = mid-range price point
const THRESHOLDS = {
    demand_daily: 10,       // products/day (300/month)
    rating: 4.5,            // quality cutoff
    price: 50000,           // IDR mid-range
};

function renderQuadrantChart(products) {
    if (!products || !products.length) return;

    // Use daily_sold for x-axis (demand per day)
    const subcats = [...new Set(products.map(p => p.subcategory))];
    const traces = subcats.map((sc, i) => {
        const pts = products.filter(p => p.subcategory === sc);
        return {
            type: 'scatter', mode: 'markers',
            name: sc,
            x: pts.map(p => p.daily_sold || p.sold_count / 30),
            y: pts.map(p => p.rating),
            text: pts.map(p => p.name.substring(0, 30)),
            marker: { size: 8, color: CHART_COLORS[i % CHART_COLORS.length], opacity: 0.7 },
        };
    });

    // Static thresholds
    const demandThreshold = THRESHOLDS.demand_daily;
    const ratingThreshold = THRESHOLDS.rating;

    // Axis range: center the threshold in the chart
    // Log scale: range = [threshold/10, threshold*100] → threshold at ~33% (visual center on log)
    const xMin = demandThreshold / 10;
    const xMax = demandThreshold * 100;

    const shapes = [
        { type: 'line', x0: demandThreshold, x1: demandThreshold, y0: 0, y1: 5.5, line: { color: '#94a3b8', dash: 'dash', width: 1 } },
        { type: 'line', x0: xMin, x1: xMax, y0: ratingThreshold, y1: ratingThreshold, line: { color: '#94a3b8', dash: 'dash', width: 1 } },
    ];

    // Labels in center of each quadrant
    const xLow = Math.sqrt(xMin * demandThreshold);
    const xHigh = Math.sqrt(demandThreshold * xMax);
    const yLow = ratingThreshold / 2;
    const yHigh = ratingThreshold + (5.5 - ratingThreshold) / 2;

    const annotations = [
        { x: xHigh, y: yHigh, text: '⭐ Winning Formula', showarrow: false, font: { size: 10, color: '#059669' } },
        { x: xLow, y: yHigh, text: '💎 Hidden Gem', showarrow: false, font: { size: 10, color: '#2563eb' } },
        { x: xHigh, y: yLow, text: '⚠️ Volume Only', showarrow: false, font: { size: 10, color: '#d97706' } },
        { x: xLow, y: yLow, text: '❌ Avoid', showarrow: false, font: { size: 10, color: '#dc2626' } },
    ];

    plotChart('chart-quadrant', traces, {
        ...CHART_LAYOUT,
        xaxis: { title: 'Produk Terjual/Hari', type: 'log', range: [Math.log10(xMin), Math.log10(xMax)], gridcolor: '#e2e8f0' },
        yaxis: { title: 'Rating', range: [0, 5.5], gridcolor: '#e2e8f0' },
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
            x: pts.map(p => p.daily_sold || p.sold_count / 30),
            y: pts.map(p => p.price),
            text: pts.map(p => p.name.substring(0, 25)),
            marker: { size: 8, color: CHART_COLORS[i % CHART_COLORS.length], opacity: 0.7 },
        };
    });

    // Static thresholds
    const demandThreshold = THRESHOLDS.demand_daily;
    const priceThreshold = THRESHOLDS.price;

    // Axis ranges
    const xMin = demandThreshold / 10;
    const xMax = demandThreshold * 100;
    const yMin = priceThreshold / 10;
    const yMax = priceThreshold * 20;

    const shapes = [
        { type: 'line', x0: demandThreshold, x1: demandThreshold, y0: yMin, y1: yMax, line: { color: '#94a3b8', dash: 'dash', width: 1 } },
        { type: 'line', x0: xMin, x1: xMax, y0: priceThreshold, y1: priceThreshold, line: { color: '#94a3b8', dash: 'dash', width: 1 } },
    ];

    const xLow = Math.sqrt(xMin * demandThreshold);
    const xHigh = Math.sqrt(demandThreshold * xMax);
    const yLow = Math.sqrt(yMin * priceThreshold);
    const yHigh = Math.sqrt(priceThreshold * yMax);

    const annotations = [
        { x: xHigh, y: yHigh, text: '⭐ High Value', showarrow: false, font: { size: 10, color: '#059669' } },
        { x: xLow, y: yHigh, text: '💎 Budget Volume', showarrow: false, font: { size: 10, color: '#2563eb' } },
        { x: xHigh, y: yLow, text: '⚠️ Expensive Niche', showarrow: false, font: { size: 10, color: '#d97706' } },
        { x: xLow, y: yLow, text: '❌ Avoid', showarrow: false, font: { size: 10, color: '#dc2626' } },
    ];

    plotChart('chart-distribution', traces, {
        ...CHART_LAYOUT,
        xaxis: { title: 'Produk Terjual/Hari', type: 'log', range: [Math.log10(xMin), Math.log10(xMax)], gridcolor: '#e2e8f0' },
        yaxis: { title: 'Harga (IDR)', type: 'log', range: [Math.log10(yMin), Math.log10(yMax)], gridcolor: '#e2e8f0' },
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
