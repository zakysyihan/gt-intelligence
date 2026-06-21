/* ---------------------------------------------------------------------------
   GT Intelligence — Frontend App
   Dashboard + Chat with agentic AI
   --------------------------------------------------------------------------- */

const API = '';  // Same origin
let currentSession = null;
let chatOpen = false;

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
    loadSessions();
});

// ---------------------------------------------------------------------------
// Dashboard
// ---------------------------------------------------------------------------

async function loadDashboard() {
    const loading = document.getElementById('dashboard-loading');
    const content = document.getElementById('dashboard-content');

    try {
        const res = await fetch(`${API}/api/dashboard`);
        const dash = await res.json();

        renderMetrics(dash);
        renderSubcategoryChart(dash.subcategory_demand);
        renderPriceChart(dash.price_distribution);
        renderGeoChart(dash.geo_distribution);
        // Quadrant and revenue charts need per-product data — render on demand
        renderPlaceholderCharts();

        loading.style.display = 'none';
        content.style.display = 'block';
    } catch (err) {
        loading.innerHTML = `<p style="color:red;">Gagal memuat dashboard: ${err.message}</p>`;
    }
}

function renderMetrics(dash) {
    const grid = document.getElementById('metrics-grid');
    const topSub = dash.top_subcategory || ['', 0];
    const metrics = [
        { label: '📦 Total Produk', value: (dash.total_products || 0).toLocaleString() },
        { label: '🏆 Subkategori Terlaris', value: topSub[0], delta: `${topSub[1].toLocaleString()} terjual` },
        { label: '🏪 Total Toko', value: (dash.total_shops || 0).toLocaleString() },
        { label: '📍 Total Kota', value: (dash.total_cities || 0).toLocaleString() },
    ];

    grid.innerHTML = metrics.map(m => `
        <div class="metric-card">
            <div class="metric-label">${m.label}</div>
            <div class="metric-value">${m.value}</div>
            ${m.delta ? `<div class="metric-delta">↑ ${m.delta}</div>` : ''}
        </div>
    `).join('');
}

// ---------------------------------------------------------------------------
// Charts (Plotly)
// ---------------------------------------------------------------------------

const CHART_COLORS = ['#2563eb', '#7c3aed', '#ec4899', '#f59e0b', '#10b981', '#ef4444'];
const CHART_LAYOUT = {
    font: { family: 'Inter, sans-serif', size: 12 },
    paper_bgcolor: 'white',
    plot_bgcolor: 'white',
    margin: { l: 50, r: 20, t: 10, b: 40 },
};

function renderSubcategoryChart(data) {
    if (!data || !data.length) return;
    const labels = data.map(r => r[0]);
    const values = data.map(r => r[1]);
    const colors = labels.map((_, i) => CHART_COLORS[i % CHART_COLORS.length]);

    Plotly.newPlot('chart-subcategory', [{
        type: 'bar', x: labels, y: values,
        marker: { color: colors },
        text: values.map(v => v.toLocaleString()),
        textposition: 'outside',
    }], {
        ...CHART_LAYOUT,
        yaxis: { title: 'Total Terjual', gridcolor: '#e2e8f0' },
        showlegend: false,
    }, { responsive: true, displayModeBar: false });
}

function renderPriceChart(data) {
    if (!data || !data.length) return;
    const labels = data.map(r => r[0]);
    const values = data.map(r => r[1]);

    Plotly.newPlot('chart-price', [{
        type: 'bar', x: labels, y: values,
        marker: { color: '#2563eb' },
        text: values,
        textposition: 'outside',
    }], {
        ...CHART_LAYOUT,
        yaxis: { title: 'Jumlah Produk', gridcolor: '#e2e8f0' },
        xaxis: { title: 'Rentang Harga (IDR)' },
        showlegend: false,
    }, { responsive: true, displayModeBar: false });
}

function renderGeoChart(data) {
    if (!data || !data.length) return;
    const top10 = data.slice(0, 10);
    const cities = top10.map(r => r[0]).reverse();
    const counts = top10.map(r => r[1]).reverse();

    Plotly.newPlot('chart-geo', [{
        type: 'bar', y: cities, x: counts,
        orientation: 'h',
        marker: { color: '#059669' },
        text: counts,
        textposition: 'outside',
    }], {
        ...CHART_LAYOUT,
        xaxis: { title: 'Jumlah Penjual', gridcolor: '#e2e8f0' },
        yaxis: { automargin: true },
        height: 350,
        margin: { l: 130, r: 30, t: 10, b: 40 },
    }, { responsive: true, displayModeBar: false });
}

function renderPlaceholderCharts() {
    // Placeholder for quadrant and revenue charts
    // These will be populated by chat agent responses
    ['chart-quadrant', 'chart-revenue'].forEach(id => {
        document.getElementById(id).innerHTML = `
            <div style="display:flex;align-items:center;justify-content:center;height:250px;color:#94a3b8;font-size:0.85rem;">
                💬 Tanya agen untuk analisis ini
            </div>`;
    });
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
