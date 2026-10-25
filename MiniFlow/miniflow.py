
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from datetime import datetime
import json
import re
import threading
import time
import webbrowser

# =========================
# MINIFLOW CONFIGURATION
# =========================

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "input.txt"
REPORT_FILE = BASE_DIR / "report.txt"
HISTORY_FILE = BASE_DIR / "execution_history.json"

HOST = "127.0.0.1"
PORT = 8001
LOCK = threading.Lock()


# =========================
# DASHBOARD
# =========================

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MiniFlow | Automation Studio</title>

<style>
:root {
    color-scheme: dark;
    --bg: #0b1020;
    --panel: #121a2d;
    --line: #303d56;
    --text: #eef3ff;
    --muted: #94a3bd;
    --cyan: #5de0d0;
    --green: #4adea5;
    --purple: #a78bfa;
}

* { box-sizing: border-box; }

body {
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font: 15px/1.6 "Segoe UI", Arial, sans-serif;
}

button, textarea { font: inherit; }
button { cursor: pointer; }

button:disabled {
    opacity: .6;
    cursor: wait;
}

.app {
    display: grid;
    grid-template-columns: 230px minmax(0, 1fr);
    min-height: 100vh;
}

.sidebar {
    background: #0d1425;
    border-right: 1px solid var(--line);
    padding: 25px 15px;
}

.brand {
    font-size: 23px;
    font-weight: 800;
    margin: 5px 10px 35px;
}

.brand span { color: var(--cyan); }

.nav {
    display: block;
    width: 100%;
    text-align: left;
    color: var(--muted);
    background: transparent;
    border: 1px solid transparent;
    border-radius: 10px;
    padding: 12px;
    margin: 6px 0;
}

.nav:hover, .nav.active {
    background: #1b2940;
    border-color: #40536d;
    color: var(--cyan);
}

.sidebar-note {
    margin: 45px 8px 0;
    padding: 14px;
    border: 1px solid var(--line);
    border-radius: 12px;
    color: var(--muted);
    font-size: 12px;
}

main {
    width: 100%;
    max-width: 1600px;
    margin: auto;
    padding: 30px;
}

.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 15px;
    flex-wrap: wrap;
}

.eyebrow {
    color: var(--cyan);
    letter-spacing: 2px;
    font-size: 11px;
    font-weight: bold;
}

h1 { margin: 5px 0; font-size: clamp(26px, 3vw, 38px); }
h2 { font-size: 17px; margin: 0; }
p { color: var(--muted); }
.sub { margin-top: 4px; }

.engine {
    border: 1px solid var(--line);
    background: var(--panel);
    padding: 10px 15px;
    border-radius: 25px;
    color: var(--green);
    font-size: 12px;
}

.stats {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 14px;
    margin: 25px 0;
}

.panel, .stat {
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 15px;
    padding: 20px;
    min-width: 0;
}

.stat-label { color: var(--muted); font-size: 12px; }
.stat-number { font-size: 30px; font-weight: 800; margin-top: 8px; }
.stat-note { color: var(--muted); font-size: 11px; }

.content {
    display: grid;
    grid-template-columns: minmax(0, 1.2fr) minmax(260px, .8fr);
    gap: 16px;
}

.panel { margin-bottom: 16px; }

.panel-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 15px;
}

.panel-sub { margin: 4px 0 0; font-size: 12px; }

label {
    display: block;
    font-size: 13px;
    font-weight: bold;
    margin-bottom: 8px;
}

textarea {
    display: block;
    width: 100%;
    min-height: 170px;
    resize: vertical;
    padding: 14px;
    color: var(--text);
    background: #080e1b;
    border: 1px solid #45536e;
    border-radius: 10px;
    line-height: 1.6;
}

textarea:focus {
    outline: 2px solid var(--cyan);
    border-color: var(--cyan);
}

textarea::placeholder { color: #73819b; }

.input-foot {
    display: flex;
    justify-content: space-between;
    color: var(--muted);
    font-size: 11px;
    margin-top: 7px;
}

.actions { display: flex; flex-wrap: wrap; gap: 9px; margin-top: 15px; }

.btn {
    padding: 10px 13px;
    border: 1px solid #40506b;
    border-radius: 9px;
    color: var(--text);
    background: #202c43;
    font-size: 12px;
    font-weight: bold;
}

.btn:hover { filter: brightness(1.2); }

.primary {
    background: var(--cyan);
    color: #07131b;
    border-color: var(--cyan);
}

.task {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    margin: 10px 0;
    border: 1px solid var(--line);
    border-radius: 10px;
    background: #0e1729;
}

.task-num {
    display: grid;
    place-items: center;
    width: 36px;
    height: 36px;
    flex-shrink: 0;
    background: #26334f;
    color: var(--purple);
    border-radius: 9px;
    font-weight: bold;
}

.task-info { flex: 1; min-width: 0; }
.task-name { font-weight: bold; font-size: 13px; }
.task-desc { color: var(--muted); font-size: 11px; }

.task-status {
    font-size: 10px;
    padding: 4px 7px;
    border-radius: 7px;
    background: #253149;
    color: var(--muted);
}

.task-status.done { background: #12382e; color: var(--green); }
.task-status.error { background: #49212b; color: #ff9eaa; }

.progress-label {
    display: flex;
    justify-content: space-between;
    color: var(--muted);
    font-size: 11px;
    margin: 15px 0 7px;
}

.progress {
    height: 7px;
    border-radius: 10px;
    background: #28344b;
    overflow: hidden;
}

.progress-bar {
    height: 100%;
    width: 0;
    background: linear-gradient(90deg, var(--purple), var(--cyan));
    transition: width .2s;
}

.result {
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    background: #080e1b;
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 14px;
    min-height: 65px;
    font: 12px/1.7 Consolas, monospace;
}

.result-label { margin: 14px 0 7px; color: var(--muted); font-size: 11px; }

.page { display: none; }
.page.active { display: block; }

.history-item {
    border-bottom: 1px solid var(--line);
    padding: 14px 0;
    overflow-wrap: anywhere;
}

.history-item:last-child { border-bottom: 0; }
.history-title { font-weight: bold; font-size: 13px; }
.history-meta { color: var(--muted); font-size: 11px; }
.empty { color: var(--muted); padding: 18px 0; font-size: 13px; }

.toast {
    position: fixed;
    bottom: 20px;
    right: 20px;
    max-width: calc(100vw - 40px);
    background: #243550;
    border: 1px solid #536985;
    border-radius: 10px;
    padding: 13px 17px;
    display: none;
    z-index: 10;
}

.toast.show { display: block; }

@media(max-width: 950px) {
    .app { grid-template-columns: 1fr; }
    .sidebar { padding: 12px; display: flex; align-items: center; gap: 5px; flex-wrap: wrap; }
    .brand { margin: 5px 10px; font-size: 18px; }
    .nav { width: auto; margin: 0; }
    .sidebar-note { display: none; }
    main { padding: 18px; }
    .content { grid-template-columns: 1fr; }
}

@media(max-width: 520px) {
    .stats { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 9px; }
    .stat { padding: 13px; }
    .stat-number { font-size: 24px; }
    .panel { padding: 14px; }
    .task { flex-wrap: wrap; }
}
</style>
</head>

<body>
<div class="app">
    <aside class="sidebar">
        <div class="brand"><span>↗</span> MiniFlow</div>
        <button class="nav active" data-page="dashboard">▦ &nbsp; Dashboard</button>
        <button class="nav" data-page="history">◷ &nbsp; Run History</button>
        <button class="nav" data-page="reports">▤ &nbsp; Reports</button>
        <div class="sidebar-note">
            <strong style="color:#4adea5">● Engine Ready</strong><br>
            Python-powered workflow execution.<br>
            Your data stays in your project folder.
        </div>
    </aside>

    <main>
        <header class="topbar">
            <div>
                <div class="eyebrow">WORKSPACE / AUTOMATION</div>
                <h1 id="pageTitle">Workflow Dashboard</h1>
                <p class="sub" id="pageSubtitle">Enter text and run your automation pipeline.</p>
            </div>
            <div class="engine">● LOCAL ENGINE</div>
        </header>

        <section id="dashboard" class="page active">
            <div class="stats">
                <div class="stat">
                    <div class="stat-label">Total runs</div>
                    <div class="stat-number" id="totalRuns">0</div>
                    <div class="stat-note">Saved executions</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Successful</div>
                    <div class="stat-number" id="successRuns">0</div>
                    <div class="stat-note">Completed workflows</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Words cleaned</div>
                    <div class="stat-number" id="wordsCleaned">0</div>
                    <div class="stat-note">Latest result</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Latest duration</div>
                    <div class="stat-number" id="duration">—</div>
                    <div class="stat-note">Milliseconds</div>
                </div>
            </div>

            <div class="content">
                <div>
                    <section class="panel">
                        <div class="panel-head">
                            <div>
                                <h2>Input Workspace</h2>
                                <p class="panel-sub">Type or paste your text below.</p>
                            </div>
                            <span class="engine">LIVE INPUT</span>
                        </div>

                        <label for="inputText">Your raw text</label>
                        <textarea id="inputText"
                            placeholder="Type or paste text here...

Example:   Hello     world!
This   text will be cleaned."></textarea>

                        <div class="input-foot">
                            <span id="charCount">0 characters</span>
                            <span id="wordCount">0 words</span>
                        </div>

                        <div class="actions">
                            <button class="btn primary" id="runBtn">▶ Run Workflow</button>
                            <button class="btn" id="sampleBtn">✦ Try sample</button>
                            <button class="btn" id="clearBtn">Clear input</button>
                        </div>
                        <p class="panel-sub">Input and report files are saved locally in your MiniFlow folder.</p>
                    </section>

                    <section class="panel">
                        <div class="panel-head">
                            <div>
                                <h2>Workflow Pipeline</h2>
                                <p class="panel-sub">Tasks update after execution.</p>
                            </div>
                            <span class="engine" id="pipelineTag">READY</span>
                        </div>

                        <div class="task">
                            <div class="task-num">01</div>
                            <div class="task-info"><div class="task-name">Save Input</div><div class="task-desc">Write text to input.txt</div></div>
                            <span class="task-status" id="s1">WAITING</span>
                        </div>
                        <div class="task">
                            <div class="task-num">02</div>
                            <div class="task-info"><div class="task-name">Validate Input</div><div class="task-desc">Check input content</div></div>
                            <span class="task-status" id="s2">WAITING</span>
                        </div>
                        <div class="task">
                            <div class="task-num">03</div>
                            <div class="task-info"><div class="task-name">Clean Text</div><div class="task-desc">Remove extra spaces and blank lines</div></div>
                            <span class="task-status" id="s3">WAITING</span>
                        </div>
                        <div class="task">
                            <div class="task-num">04</div>
                            <div class="task-info"><div class="task-name">Analyze Text</div><div class="task-desc">Count words, characters and lines</div></div>
                            <span class="task-status" id="s4">WAITING</span>
                        </div>
                        <div class="task">
                            <div class="task-num">05</div>
                            <div class="task-info"><div class="task-name">Generate Report</div><div class="task-desc">Save results to report.txt</div></div>
                            <span class="task-status" id="s5">WAITING</span>
                        </div>

                        <div class="progress-label">
                            <span id="progressText">Waiting for your first run</span>
                            <span id="progressPercent">0%</span>
                        </div>
                        <div class="progress"><div class="progress-bar" id="progressBar"></div></div>
                    </section>
                </div>

                <div>
                    <section class="panel">
                        <div class="panel-head"><h2>Cleaned Output</h2></div>
                        <div id="cleanedOutput" class="result">Your cleaned text will appear here.</div>
                        <div class="result-label">ANALYSIS SUMMARY</div>
                        <div id="analysisOutput" class="result">No analysis yet.</div>
                        <div class="actions">
                            <button class="btn" id="copyBtn">Copy cleaned text</button>
                            <button class="btn" id="downloadBtn">Download report</button>
                        </div>
                    </section>

                    <section class="panel">
                        <div class="panel-head">
                            <div><h2>Recent Activity</h2><p class="panel-sub">Latest executions</p></div>
                            <button class="btn" id="viewHistoryBtn">View all ↗</button>
                        </div>
                        <div id="recentActivity" class="empty">No runs yet.</div>
                    </section>
                </div>
            </div>
        </section>

        <section id="history" class="page">
            <section class="panel">
                <div class="panel-head">
                    <div><h2>Run History</h2><p class="panel-sub">Previously saved executions.</p></div>
                    <button class="btn primary" id="refreshHistoryBtn">↻ Refresh History</button>
                </div>
                <div id="historyList" class="empty">Loading history...</div>
                <p id="historyStatus" class="panel-sub">History comes from execution_history.json.</p>
            </section>
        </section>

        <section id="reports" class="page">
            <section class="panel">
                <div class="panel-head">
                    <div><h2>Generated Report</h2><p class="panel-sub">The latest report saved by MiniFlow.</p></div>
                    <button class="btn primary" id="refreshReportBtn">↻ Refresh Report</button>
                </div>
                <pre id="reportOutput" class="result">No report generated yet.</pre>
                <div class="actions"><button class="btn" id="downloadReportBtn">Download report</button></div>
            </section>
        </section>
    </main>
</div>

<div id="toast" class="toast"></div>

<script>
const $ = id => document.getElementById(id);
let latestCleaned = "";
let latestReport = "";

const sample = `   MiniFlow    is my first Python automation project.

I am learning    workflow automation.

   This text   has extra spaces.   `;

function toast(message) {
    const el = $("toast");
    el.textContent = message;
    el.classList.add("show");
    setTimeout(() => el.classList.remove("show"), 2800);
}

function countInput() {
    const text = $("inputText").value;
    $("charCount").textContent = text.length + " characters";
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    $("wordCount").textContent = words + " words";
}

$("inputText").addEventListener("input", countInput);

$("sampleBtn").addEventListener("click", () => {
    $("inputText").value = sample;
    countInput();
    $("inputText").focus();
    toast("Sample text added.");
});

$("clearBtn").addEventListener("click", () => {
    $("inputText").value = "";
    countInput();
    $("inputText").focus();
});

function setTask(n, status) {
    const el = $("s" + n);
    el.textContent = status;
    el.className = "task-status";
    if (status === "DONE") el.classList.add("done");
    if (status === "ERROR") el.classList.add("error");
}

function setAllTasks(status) {
    for (let i = 1; i <= 5; i++) setTask(i, status);
}

function progress(percent, message) {
    $("progressBar").style.width = percent + "%";
    $("progressPercent").textContent = percent + "%";
    $("progressText").textContent = message;
}

function safe(value) {
    return String(value ?? "").replace(/[&<>"']/g, ch => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;",
        '"': "&quot;", "'": "&#39;"
    })[ch]);
}

function historyMarkup(records) {
    if (!records.length) return '<div class="empty">No saved runs yet. Run a workflow first.</div>';

    return records.slice().reverse().map(record => `
        <div class="history-item">
            <div class="history-title">${safe(record.title || "Text cleaning workflow")}</div>
            <div class="history-meta">
                ${safe(record.timestamp || "")}
                · ${Number(record.analysis?.word_count || 0)} words
                · ${Number(record.analysis?.character_count || 0)} characters
                · ${safe(record.status || "completed")}
            </div>
        </div>
    `).join("");
}

async function refreshHistory(showMessage = false) {
    const button = $("refreshHistoryBtn");
    if (button) {
        button.disabled = true;
        button.textContent = "Refreshing...";
    }

    if ($("historyStatus")) $("historyStatus").textContent = "Loading latest history...";

    try {
        const response = await fetch("/api/history?ts=" + Date.now(), {cache: "no-store"});
        if (!response.ok) throw new Error("Server returned " + response.status);

        const data = await response.json();
        const records = Array.isArray(data.records) ? data.records : [];

        $("historyList").innerHTML = historyMarkup(records);
        $("recentActivity").innerHTML = records.length
            ? historyMarkup(records.slice(-3))
            : '<div class="empty">No runs yet. Enter text and click Run Workflow.</div>';

        $("totalRuns").textContent = records.length;
        $("successRuns").textContent = records.filter(r => r.status === "completed").length;

        const last = records.length ? records[records.length - 1] : null;
        if (last) {
            $("wordsCleaned").textContent = last.analysis?.word_count ?? 0;
            $("duration").textContent = (last.duration_ms ?? 0) + " ms";
        } else {
            $("wordsCleaned").textContent = "0";
            $("duration").textContent = "—";
        }

        if ($("historyStatus")) {
            $("historyStatus").textContent = "Updated successfully · " + records.length + " saved run(s).";
        }

        if (showMessage) toast("History refreshed successfully.");
    } catch (error) {
        if ($("historyStatus")) $("historyStatus").textContent = "Refresh failed: " + error.message;
        if (showMessage) toast("History refresh failed. Check that Python is running.");
    } finally {
        if (button) {
            button.disabled = false;
            button.textContent = "↻ Refresh History";
        }
    }
}

async function refreshReport(showMessage = false) {
    const button = $("refreshReportBtn");
    if (button) {
        button.disabled = true;
        button.textContent = "Refreshing...";
    }

    try {
        const response = await fetch("/api/report?ts=" + Date.now(), {cache: "no-store"});
        if (!response.ok) throw new Error("Server returned " + response.status);

        const data = await response.json();
        latestReport = data.report || "";
        $("reportOutput").textContent = latestReport || "No report generated yet.";

        if (showMessage) toast("Report refreshed successfully.");
    } catch (error) {
        $("reportOutput").textContent = "Could not load report. Make sure the Python server is running.";
        if (showMessage) toast("Report refresh failed: " + error.message);
    } finally {
        if (button) {
            button.disabled = false;
            button.textContent = "↻ Refresh Report";
        }
    }
}

function downloadText(filename, content) {
    const blob = new Blob([content], {type: "text/plain;charset=utf-8"});
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function downloadLatestReport() {
    if (!latestReport) {
        toast("Run a workflow first to generate a report.");
        return;
    }
    downloadText("miniflow_report.txt", latestReport);
}

$("downloadBtn").addEventListener("click", downloadLatestReport);
$("downloadReportBtn").addEventListener("click", downloadLatestReport);

$("copyBtn").addEventListener("click", async () => {
    if (!latestCleaned) {
        toast("Run a workflow first.");
        return;
    }

    try {
        await navigator.clipboard.writeText(latestCleaned);
        toast("Cleaned text copied.");
    } catch (error) {
        const temp = document.createElement("textarea");
        temp.value = latestCleaned;
        document.body.appendChild(temp);
        temp.select();
        const copied = document.execCommand("copy");
        temp.remove();
        toast(copied ? "Cleaned text copied." : "Copy failed. Select and copy the output manually.");
    }
});

function showPage(page) {
    document.querySelectorAll(".page").forEach(el => {
        el.classList.toggle("active", el.id === page);
    });

    document.querySelectorAll(".nav").forEach(el => {
        el.classList.toggle("active", el.dataset.page === page);
    });

    const titles = {
        dashboard: ["Workflow Dashboard", "Enter text and run your automation pipeline."],
        history: ["Run History", "Review all your saved workflow executions."],
        reports: ["Generated Reports", "View and download the latest report."]
    };

    $("pageTitle").textContent = titles[page][0];
    $("pageSubtitle").textContent = titles[page][1];

    if (page === "history") refreshHistory();
    if (page === "reports") refreshReport();
}

document.querySelectorAll(".nav").forEach(button => {
    button.addEventListener("click", () => showPage(button.dataset.page));
});

$("viewHistoryBtn").addEventListener("click", () => showPage("history"));
$("refreshHistoryBtn").addEventListener("click", () => refreshHistory(true));
$("refreshReportBtn").addEventListener("click", () => refreshReport(true));

$("runBtn").addEventListener("click", async () => {
    const rawText = $("inputText").value;

    if (!rawText.trim()) {
        toast("Please type or paste some text first.");
        $("inputText").focus();
        return;
    }

    const button = $("runBtn");
    button.disabled = true;
    button.textContent = "Running workflow...";
    $("pipelineTag").textContent = "RUNNING";
    $("cleanedOutput").textContent = "Processing your text...";
    $("analysisOutput").textContent = "Please wait...";

    setAllTasks("WAITING");
    progress(10, "Sending input to Python...");

    try {
        const response = await fetch("/api/run", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({text: rawText})
        });

        const data = await response.json();
        if (!response.ok || !data.ok) throw new Error(data.error || "Workflow failed.");

        for (let i = 1; i <= 5; i++) {
            setTask(i, "DONE");
            progress(i * 20, "Completed task " + i + " of 5");
            await new Promise(resolve => setTimeout(resolve, 90));
        }

        $("pipelineTag").textContent = "COMPLETED";
        latestCleaned = data.cleaned_text;
        latestReport = data.report;

        $("cleanedOutput").textContent = latestCleaned;
        $("analysisOutput").textContent =
            "Words: " + data.analysis.word_count +
            "\nCharacters: " + data.analysis.character_count +
            "\nLines: " + data.analysis.line_count +
            "\nExtra whitespace removed: " + (data.analysis.whitespace_changes ? "Yes" : "No") +
            "\nInput saved: input.txt\nReport saved: report.txt";

        $("reportOutput").textContent = latestReport;
        $("wordsCleaned").textContent = data.analysis.word_count;
        $("duration").textContent = data.duration_ms + " ms";

        await refreshHistory();
        toast("Workflow completed. Report saved successfully.");
    } catch (error) {
        $("pipelineTag").textContent = "ERROR";
        progress(0, "Workflow failed");
        $("cleanedOutput").textContent = "Unable to process text.";
        $("analysisOutput").textContent = error.message;
        toast("Workflow failed: " + error.message);
    } finally {
        button.disabled = false;
        button.textContent = "▶ Run Workflow";
    }
});

refreshHistory();
refreshReport();
countInput();
</script>
</body>
</html>
"""


# =========================
# HISTORY MANAGEMENT
# =========================

def load_history():
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []


def save_history(records):
    HISTORY_FILE.write_text(
        json.dumps(records, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


# =========================
# TEXT PROCESSING
# =========================

def clean_text(raw_text):
    raw_text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    cleaned_lines = []

    for line in raw_text.split("\n"):
        line = re.sub(r"[ \t]+", " ", line).strip()
        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def analyze_text(cleaned_text):
    words = re.findall(r"\b[\w'-]+\b", cleaned_text, flags=re.UNICODE)

    return {
        "word_count": len(words),
        "character_count": len(cleaned_text),
        "line_count": len(cleaned_text.splitlines()) if cleaned_text else 0,
        "whitespace_changes": False
    }


def generate_report(cleaned_text, analysis, timestamp):
    report = (
        "MINIFLOW - TEXT CLEANING REPORT\n"
        "================================\n"
        f"Run time: {timestamp}\n"
        f"Words: {analysis['word_count']}\n"
        f"Characters: {analysis['character_count']}\n"
        f"Lines: {analysis['line_count']}\n"
        f"Extra whitespace removed: "
        f"{'Yes' if analysis['whitespace_changes'] else 'No'}\n\n"
        "CLEANED TEXT\n"
        "------------\n"
        f"{cleaned_text}\n"
    )

    REPORT_FILE.write_text(report, encoding="utf-8")
    return report


def run_workflow(raw_text):
    start = time.perf_counter()

    if not isinstance(raw_text, str):
        raise ValueError("Input must be text.")

    if not raw_text.strip():
        raise ValueError("Input cannot be empty.")

    INPUT_FILE.write_text(raw_text, encoding="utf-8")

    cleaned = clean_text(raw_text)
    analysis = analyze_text(cleaned)
    analysis["whitespace_changes"] = cleaned != raw_text

    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    report = generate_report(cleaned, analysis, timestamp)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)

    record = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "title": "Text cleaning workflow",
        "timestamp": timestamp,
        "status": "completed",
        "analysis": analysis,
        "duration_ms": duration_ms,
        "cleaned_text": cleaned
    }

    with LOCK:
        records = load_history()
        records.append(record)
        save_history(records)

    return {
        "ok": True,
        "cleaned_text": cleaned,
        "analysis": analysis,
        "report": report,
        "duration_ms": duration_ms
    }


# =========================
# LOCAL WEB SERVER
# =========================

class Handler(BaseHTTPRequestHandler):

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]

        if path == "/":
            body = HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        elif path == "/api/history":
            with LOCK:
                records = load_history()
            self.send_json({"records": records})

        elif path == "/api/report":
            try:
                report = REPORT_FILE.read_text(encoding="utf-8")
            except (FileNotFoundError, OSError):
                report = ""
            self.send_json({"report": report})

        else:
            self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        if self.path.split("?")[0] != "/api/run":
            self.send_json({"ok": False, "error": "Not found"}, 404)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode("utf-8")
            payload = json.loads(body)
            raw_text = payload.get("text", "")

            result = run_workflow(raw_text)
            self.send_json(result)

        except (ValueError, json.JSONDecodeError) as error:
            self.send_json({"ok": False, "error": str(error)}, 400)

        except Exception as error:
            self.send_json(
                {"ok": False, "error": f"Unexpected error: {error}"},
                500
            )

    def log_message(self, format_string, *args):
        pass


# =========================
# START MINIFLOW
# =========================

def main():
    try:
        server = ThreadingHTTPServer((HOST, PORT), Handler)
    except OSError as error:
        print(f"Could not start server on port {PORT}: {error}")
        print("Close the other MiniFlow server or change PORT to 8002.")
        return

    url = f"http://{HOST}:{PORT}"

    print("\n================================")
    print("       MINIFLOW IS READY")
    print("================================")
    print(f"Open in your browser: {url}")
    print("Keep this terminal open while using MiniFlow.")
    print("Press Ctrl+C to stop the server.")
    print("================================\n")

    threading.Timer(1, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nMiniFlow stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
