"use strict";

// ── DOM refs ──────────────────────────────────────────────────────────────────
const urlInput    = document.getElementById("url-input");
const depthRange  = document.getElementById("depth-range");
const depthVal    = document.getElementById("depth-val");
const pagesRange  = document.getElementById("pages-range");
const pagesVal    = document.getElementById("pages-val");
const crawlBtn    = document.getElementById("crawl-btn");
const crawlBtnTxt = document.getElementById("crawl-btn-text");
const statusBadge = document.getElementById("status-badge");

const statsBlock  = document.getElementById("stats-block");
const statPages   = document.getElementById("stat-pages");
const statLinks   = document.getElementById("stat-links");
const statChunks  = document.getElementById("stat-chunks");

const sitemapSec  = document.getElementById("sitemap-section");
const sitemapList = document.getElementById("sitemap-list");

const idleScreen       = document.getElementById("idle-screen");
const processingScreen = document.getElementById("processing-screen");
const dashboardScreen  = document.getElementById("dashboard-screen");
const logBody          = document.getElementById("log-body");

const tabBtns = document.querySelectorAll(".tab-btn");

// Overview
const siteTitle   = document.getElementById("site-title");
const siteSummary = document.getElementById("site-summary");
const kvPages     = document.getElementById("kv-pages");
const kvLinks     = document.getElementById("kv-links");
const topicsBlock = document.getElementById("topics-block");
const topicsList  = document.getElementById("topics-list");

// FAQs
const faqLoading  = document.getElementById("faq-loading");
const faqList     = document.getElementById("faq-list");
const faqEmpty    = document.getElementById("faq-empty");

// Chat
const chatHistory = document.getElementById("chat-history");
const chatEmpty   = document.getElementById("chat-empty");
const chatInput   = document.getElementById("chat-input");
const sendBtn     = document.getElementById("send-btn");
const clearBtn    = document.getElementById("clear-btn");

// ── Helpers ───────────────────────────────────────────────────────────────────

function esc(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

async function post(url, body) {
  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return r.json();
}

async function get(url) {
  const r = await fetch(url);
  return r.json();
}

// ── Screen switching ──────────────────────────────────────────────────────────

function showScreen(name) {
  idleScreen.classList.add("hidden");
  processingScreen.classList.add("hidden");
  dashboardScreen.classList.add("hidden");
  if (name === "idle")       idleScreen.classList.remove("hidden");
  if (name === "processing") processingScreen.classList.remove("hidden");
  if (name === "dashboard")  dashboardScreen.classList.remove("hidden");
}

// ── Status badge ──────────────────────────────────────────────────────────────

function setStatus(s) {
  statusBadge.className = "status-badge";
  if (s === "idle") {
    statusBadge.classList.add("status-idle");
    statusBadge.innerHTML = `<span class="status-dot"></span> Ready`;
  } else if (s === "processing") {
    statusBadge.classList.add("status-process");
    statusBadge.innerHTML = `<span class="status-dot"></span> Processing`;
  } else if (s === "complete") {
    statusBadge.classList.add("status-complete");
    statusBadge.innerHTML = `<span class="status-dot"></span> Complete`;
  }
}

// ── Log window ────────────────────────────────────────────────────────────────

let _logStart = Date.now();

function addLog(msg, type = "info") {
  const elapsed = ((Date.now() - _logStart) / 1000).toFixed(1).padStart(5, "0");
  const line = document.createElement("p");
  line.className = "log-line";
  line.innerHTML =
    `<span class="log-ts">${elapsed}s</span>` +
    `<span class="log-tag ${type}">${type.toUpperCase()}</span>` +
    `<span class="log-msg">${esc(msg)}</span>`;
  logBody.appendChild(line);
  logBody.scrollTop = logBody.scrollHeight;
}

// Fake progress logs while the real request runs
const LOG_STEPS = [
  [0,    "info",    "Initialising crawler…"],
  [1200, "info",    "Fetching seed URL…"],
  [2500, "info",    "Parsing HTML with BeautifulSoup…"],
  [3800, "info",    "Extracting internal links…"],
  [5200, "info",    "Crawling discovered pages…"],
  [7000, "warn",    "Some pages may require auth — skipping…"],
  [8500, "info",    "Cleaning and normalising text…"],
  [10000,"info",    "Splitting text into chunks (800 chars, 150 overlap)…"],
  [12000,"info",    "Loading SentenceTransformer all-MiniLM-L6-v2…"],
  [14000,"info",    "Generating 384-dim embeddings (batch size 32)…"],
  [17000,"info",    "Storing vectors in ChromaDB…"],
  [19000,"info",    "Building HNSW cosine-similarity index…"],
];

function startFakeLogs() {
  logBody.innerHTML = "";
  _logStart = Date.now();
  LOG_STEPS.forEach(([delay, type, msg]) => {
    setTimeout(() => addLog(msg, type), delay);
  });
}

// ── Range sliders ─────────────────────────────────────────────────────────────

depthRange.addEventListener("input", () => { depthVal.textContent = depthRange.value; });
pagesRange.addEventListener("input", () => { pagesVal.textContent = pagesRange.value; });

// ── Sitemap ───────────────────────────────────────────────────────────────────

function renderSitemap(pages) {
  sitemapList.innerHTML = "";
  pages.forEach(p => {
    const li = document.createElement("li");
    li.dataset.depth = p.depth;
    const label = p.title || p.url;
    li.innerHTML = `<a href="${esc(p.url)}" target="_blank" title="${esc(p.url)}">${esc(label)}</a>`;
    sitemapList.appendChild(li);
  });
  sitemapSec.classList.remove("hidden");
}

// ── Tabs ──────────────────────────────────────────────────────────────────────

tabBtns.forEach(btn => {
  btn.addEventListener("click", () => {
    tabBtns.forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    const target = btn.dataset.tab;
    document.querySelectorAll(".tab-panel").forEach(p => p.classList.add("hidden"));
    document.getElementById(`tab-${target}`).classList.remove("hidden");
    if (target === "faqs") loadFaqs();
  });
});

function resetTabs() {
  tabBtns.forEach((b, i) => b.classList.toggle("active", i === 0));
  document.querySelectorAll(".tab-panel").forEach((p, i) => p.classList.toggle("hidden", i !== 0));
}

// ── Overview ──────────────────────────────────────────────────────────────────

async function loadSummary() {
  siteTitle.textContent = "Generating AI summary…";
  siteSummary.textContent = "";
  kvPages.textContent = "…";
  kvLinks.textContent = "…";
  topicsBlock.classList.add("hidden");
  topicsList.innerHTML = "";

  const data = await get("/api/summary");
  if (data.error) {
    siteTitle.textContent = "Website Overview";
    siteSummary.textContent = data.error;
    return;
  }

  siteTitle.textContent   = data.title   || "Website Overview";
  siteSummary.textContent = data.summary || "";
  kvPages.textContent     = data.pages_indexed ?? "—";
  kvLinks.textContent     = data.total_links   ?? "—";

  if (data.topics?.length) {
    topicsList.innerHTML = "";
    data.topics.forEach(t => {
      const span = document.createElement("span");
      span.className = "topic-tag";
      span.textContent = t;
      topicsList.appendChild(span);
    });
    topicsBlock.classList.remove("hidden");
  }
}

// ── FAQs ──────────────────────────────────────────────────────────────────────

let _faqsLoaded = false;

async function loadFaqs() {
  if (_faqsLoaded) return;
  faqLoading.classList.remove("hidden");
  faqList.innerHTML = "";
  faqEmpty.classList.add("hidden");

  const data = await get("/api/faqs");
  faqLoading.classList.add("hidden");

  if (data.error || !data.faqs?.length) {
    faqEmpty.classList.remove("hidden");
    return;
  }

  data.faqs.forEach(faq => {
    const item = document.createElement("div");
    item.className = "faq-item";
    item.innerHTML = `
      <div class="faq-question">
        <span>Q: ${esc(faq.question)}</span>
        <span class="faq-chevron">▼</span>
      </div>
      <div class="faq-answer">
        ${esc(faq.answer)}
        <span class="faq-source">// source: ${esc(faq.source || "")}</span>
      </div>`;
    item.querySelector(".faq-question").addEventListener("click", () => item.classList.toggle("open"));
    faqList.appendChild(item);
  });

  _faqsLoaded = true;
}

// ── Chat ──────────────────────────────────────────────────────────────────────

function syncChatEmpty() {
  const hasBubbles = chatHistory.querySelector(".bubble");
  chatEmpty.classList.toggle("hidden", !!hasBubbles);
}

function appendBubble(role, text, sources) {
  chatEmpty.classList.add("hidden");

  const div = document.createElement("div");
  const cls = role === "user" ? "bubble-user" : "bubble-bot";
  div.className = `bubble ${cls}`;

  const label = role === "user" ? "you" : "assistant";
  let html = `<div class="bubble-label">${label}</div>${esc(text)}`;

  if (sources?.length) {
    const tags = sources.map(s => `<span class="source-tag">${esc(s)}</span>`).join("");
    html += `<div class="sources-row">${tags}</div>`;
  }

  div.innerHTML = html;
  chatHistory.appendChild(div);
  chatHistory.scrollTop = chatHistory.scrollHeight;
}

function appendError(msg) {
  const div = document.createElement("div");
  div.className = "bubble bubble-error";
  div.innerHTML = `<div class="bubble-label">error</div>${esc(msg)}`;
  chatHistory.appendChild(div);
  chatHistory.scrollTop = chatHistory.scrollHeight;
}

async function sendMessage() {
  const q = chatInput.value.trim();
  if (!q) return;
  chatInput.value = "";
  appendBubble("user", q);
  sendBtn.disabled = true;
  sendBtn.textContent = "…";

  const data = await post("/api/chat", { question: q });
  sendBtn.disabled = false;
  sendBtn.textContent = "Send";

  if (data.error) { appendError(data.error); return; }
  appendBubble("assistant", data.answer, data.sources);
}

sendBtn.addEventListener("click", sendMessage);
chatInput.addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});

clearBtn.addEventListener("click", async () => {
  await post("/api/chat/clear", {});
  chatHistory.innerHTML = "";
  syncChatEmpty();
});

// ── Crawl ─────────────────────────────────────────────────────────────────────

crawlBtn.addEventListener("click", async () => {
  const url = urlInput.value.trim();
  if (!url) { urlInput.focus(); urlInput.style.borderColor = "var(--red)"; return; }
  urlInput.style.borderColor = "";

  crawlBtn.disabled = true;
  crawlBtnTxt.textContent = "⏳ Crawling…";
  setStatus("processing");
  showScreen("processing");
  startFakeLogs();
  _faqsLoaded = false;

  const data = await post("/api/crawl", {
    url,
    max_depth: +depthRange.value,
    max_pages: +pagesRange.value,
  });

  crawlBtn.disabled = false;
  crawlBtnTxt.textContent = "🚀 Start Crawling";

  if (data.error) {
    addLog("Crawl failed: " + data.error, "warn");
    setStatus("idle");
    setTimeout(() => showScreen("idle"), 1800);
    return;
  }

  addLog(`Done — ${data.pages_indexed} pages, ${data.chunks_total} chunks`, "success");

  // Update sidebar stats
  setStatus("complete");
  statPages.textContent  = data.pages_indexed ?? "—";
  statLinks.textContent  = data.total_links   ?? "—";
  statChunks.textContent = data.chunks_total  ?? "—";
  statsBlock.classList.remove("hidden");

  renderSitemap(data.sitemap || []);

  // Small delay so user sees the last log line
  await new Promise(r => setTimeout(r, 900));

  showScreen("dashboard");
  resetTabs();
  chatHistory.innerHTML = "";
  syncChatEmpty();
  loadSummary();
});

// ── Init ──────────────────────────────────────────────────────────────────────

(async () => {
  const s = await get("/api/status");
  if (s.status === "complete") {
    setStatus("complete");
    if (s.pages)  { statPages.textContent  = s.pages; statsBlock.classList.remove("hidden"); }
    if (s.links)  { statLinks.textContent  = s.links; }
    showScreen("dashboard");
    resetTabs();
    syncChatEmpty();
    loadSummary();
  } else {
    setStatus("idle");
    showScreen("idle");
  }
})();