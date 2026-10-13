/* ============================================================
   AI Medical Triage — Frontend JavaScript
   All API interactions, tab switching, form logic, chat, toast
   ============================================================ */

const BACKEND_URL = "http://localhost:8000";

// ─── DOM Elements ───────────────────────────────────────────
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

// ─── Toast Notifications ────────────────────────────────────
function showToast(message, type = "info", duration = 4000) {
    const container = $("#toast-container");
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.add("out");
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ─── Tab Navigation ─────────────────────────────────────────
function initTabs() {
    const tabBtns = $$(".tab-btn");
    const panels = $$(".tab-panel");

    tabBtns.forEach((btn) => {
        btn.addEventListener("click", () => {
            const target = btn.dataset.tab;

            // Deactivate all
            tabBtns.forEach((b) => {
                b.classList.remove("active");
                b.setAttribute("aria-selected", "false");
            });
            panels.forEach((p) => p.classList.remove("active"));

            // Activate target
            btn.classList.add("active");
            btn.setAttribute("aria-selected", "true");
            const panel = $(`#panel-${target}`);
            if (panel) panel.classList.add("active");
        });
    });
}

// ─── Backend Health Check ───────────────────────────────────
async function checkBackendHealth() {
    const dot = $("#status-dot");
    const text = $("#status-text");
    try {
        const res = await fetch(`${BACKEND_URL}/api/health`, { signal: AbortSignal.timeout(4000) });
        const data = await res.json();
        if (data.ollama_connected) {
            dot.className = "status-dot online";
            text.textContent = `Gemma 3:1B Connected`;
        } else {
            dot.className = "status-dot offline";
            text.textContent = "Backend Online — Ollama Model Offline";
        }
    } catch {
        dot.className = "status-dot offline";
        text.textContent = "Backend Offline — Start main.py";
    }
}

// ─── Loading Overlay Helpers ────────────────────────────────
function showLoading(id) {
    const el = $(`#${id}`);
    if (el) el.classList.add("active");
}

function hideLoading(id) {
    const el = $(`#${id}`);
    if (el) el.classList.remove("active");
}

// ============================================================
// SEVERITY SLIDER
// ============================================================
function initSeveritySlider() {
    const slider = $("#triage-severity");
    const display = $("#severity-display");
    const label = $("#severity-text-label");

    function update(val) {
        val = parseInt(val);
        display.textContent = val;

        // Color class
        display.className = "severity-value";
        if (val <= 3) {
            display.classList.add("low");
            label.textContent = "Mild";
        } else if (val <= 5) {
            display.classList.add("medium");
            label.textContent = "Moderate";
        } else if (val <= 7) {
            display.classList.add("high");
            label.textContent = "High";
        } else {
            display.classList.add("critical");
            label.textContent = "Critical";
        }
    }

    slider.addEventListener("input", (e) => update(e.target.value));
    update(slider.value);
}

// ============================================================
// TAB 1: SYMPTOM TRIAGE
// ============================================================
function initTriageForm() {
    const form = $("#triage-form");
    const submitBtn = $("#triage-submit-btn");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const symptoms = $("#triage-symptoms").value.trim();
        if (!symptoms) {
            showToast("Please describe your symptoms.", "error");
            return;
        }

        const payload = {
            age: parseInt($("#triage-age").value),
            gender: $("#triage-gender").value,
            symptoms: symptoms,
            duration: $("#triage-duration").value.trim() || "Not specified",
            severity_score: parseInt($("#triage-severity").value),
            existing_conditions: $("#triage-conditions").value.trim() || "None",
            language: $("#triage-language").value,
        };

        submitBtn.disabled = true;
        showLoading("triage-loading");

        try {
            const res = await fetch(`${BACKEND_URL}/api/triage/assess`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({ detail: res.statusText }));
                throw new Error(err.detail || "Triage request failed");
            }

            const data = await res.json();
            renderTriageResults(data);
            showToast("Triage assessment complete!", "success");
        } catch (err) {
            showToast(`Triage error: ${err.message}`, "error");
        } finally {
            submitBtn.disabled = false;
            hideLoading("triage-loading");
        }
    });
}

function renderTriageResults(data) {
    const container = $("#triage-results");
    const urgency = (data.urgency_level || "ROUTINE").toUpperCase();

    const badgeMap = {
        EMERGENCY: { cls: "emergency", icon: "🚨", label: "EMERGENCY — IMMEDIATE CARE REQUIRED" },
        URGENT:    { cls: "urgent",    icon: "⚠️", label: "URGENT — SEE DOCTOR WITHIN 24-48 HOURS" },
        ROUTINE:   { cls: "routine",   icon: "ℹ️",  label: "ROUTINE — SCHEDULE APPOINTMENT" },
        SELF_CARE: { cls: "selfcare",  icon: "✅", label: "SELF CARE — MONITOR AT HOME" },
    };

    const badge = badgeMap[urgency] || badgeMap.ROUTINE;

    let redFlagsHtml = "";
    if (data.red_flags_detected && data.red_flags_detected.length > 0) {
        redFlagsHtml = `
            <div class="result-section">
                <div class="result-section-title">🚩 Red Flags Detected</div>
                <div class="red-flag-box">
                    <strong>Warning:</strong> ${data.red_flags_detected.join(", ")}
                </div>
            </div>`;
    }

    let questionsHtml = "";
    if (data.questions_for_doctor && data.questions_for_doctor.length > 0) {
        questionsHtml = `
            <div class="result-section">
                <div class="result-section-title">🩺 Questions to Ask Your Doctor</div>
                <ul class="questions-list">
                    ${data.questions_for_doctor.map((q) => `<li>${escapeHtml(q)}</li>`).join("")}
                </ul>
            </div>`;
    }

    container.innerHTML = `
        <div class="glass-card results-container">
            <h2 class="card-title">Triage Assessment Results</h2>

            <div class="urgency-badge ${badge.cls}">
                ${badge.icon} ${badge.label}
            </div>

            <div class="result-section">
                <div class="result-section-title">📋 Recommended Action</div>
                <div class="result-action">${escapeHtml(data.recommended_action || "")}</div>
            </div>

            ${redFlagsHtml}

            <div class="result-section">
                <div class="result-section-title">📝 Clinical Explanation</div>
                <div class="result-text">${escapeHtml(data.summary || "")}</div>
            </div>

            ${questionsHtml}

            <div class="disclaimer-box">
                <strong>⚠️ Disclaimer:</strong> ${escapeHtml(data.disclaimer || "")}
            </div>
        </div>`;

    container.style.display = "block";
    container.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ============================================================
// TAB 2: MEDICAL REPORT EXPLAINER
// ============================================================
let selectedFile = null;

function initReportUpload() {
    const zone = $("#upload-zone");
    const fileInput = $("#pdf-file-input");
    const browseTrigger = $("#upload-browse-trigger");
    const submitBtn = $("#report-submit-btn");

    // Click to browse
    browseTrigger.addEventListener("click", (e) => {
        e.stopPropagation();
        fileInput.click();
    });
    zone.addEventListener("click", () => fileInput.click());

    // File selected
    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            handleFileSelected(fileInput.files[0]);
        }
    });

    // Drag & drop
    zone.addEventListener("dragover", (e) => {
        e.preventDefault();
        zone.classList.add("dragover");
    });

    zone.addEventListener("dragleave", () => {
        zone.classList.remove("dragover");
    });

    zone.addEventListener("drop", (e) => {
        e.preventDefault();
        zone.classList.remove("dragover");
        if (e.dataTransfer.files.length > 0) {
            const file = e.dataTransfer.files[0];
            if (file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf")) {
                handleFileSelected(file);
            } else {
                showToast("Only PDF files are supported.", "error");
            }
        }
    });

    // Submit
    submitBtn.addEventListener("click", () => processReport());
}

function handleFileSelected(file) {
    selectedFile = file;
    const display = $("#file-selected-display");
    const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
    display.innerHTML = `
        <div class="file-selected-info">
            📎 <strong>${escapeHtml(file.name)}</strong> (${sizeMB} MB)
        </div>`;
    $("#report-submit-btn").disabled = false;
    showToast(`File selected: ${file.name}`, "info");
}

async function processReport() {
    if (!selectedFile) {
        showToast("Please select a PDF file first.", "error");
        return;
    }

    const submitBtn = $("#report-submit-btn");
    submitBtn.disabled = true;
    showLoading("report-loading");

    try {
        // Step 1: Upload & extract text
        const formData = new FormData();
        formData.append("file", selectedFile);

        const uploadRes = await fetch(`${BACKEND_URL}/api/reports/upload`, {
            method: "POST",
            body: formData,
        });

        if (!uploadRes.ok) {
            const err = await uploadRes.json().catch(() => ({ detail: uploadRes.statusText }));
            throw new Error(err.detail || "Upload failed");
        }

        const uploadData = await uploadRes.json();
        const extractedText = uploadData.extracted_text;

        if (!extractedText || !extractedText.trim()) {
            throw new Error("Could not extract readable text from this PDF.");
        }

        showToast(`Extracted text from ${uploadData.total_pages} page(s). Analyzing...`, "success");

        // Step 2: Analyze the extracted text
        const analyzePayload = {
            report_text: extractedText,
            language: $("#report-language").value,
        };

        const analyzeRes = await fetch(`${BACKEND_URL}/api/reports/analyze`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(analyzePayload),
        });

        if (!analyzeRes.ok) {
            const err = await analyzeRes.json().catch(() => ({ detail: analyzeRes.statusText }));
            throw new Error(err.detail || "Analysis failed");
        }

        const reportData = await analyzeRes.json();
        renderReportResults(reportData);
        showToast("Report analysis complete!", "success");
    } catch (err) {
        showToast(`Report error: ${err.message}`, "error");
    } finally {
        submitBtn.disabled = false;
        hideLoading("report-loading");
    }
}

function renderReportResults(data) {
    const container = $("#report-results");

    // Abnormal values
    let abnormalHtml = "";
    if (data.abnormal_values && data.abnormal_values.length > 0) {
        abnormalHtml = `
            <div class="result-section">
                <div class="result-section-title">⚠️ Highlighted Abnormal / Out-of-Range Values</div>
                ${data.abnormal_values.map((v) => `<div class="abnormal-item">• ${escapeHtml(v)}</div>`).join("")}
            </div>`;
    }

    // Simplified terms
    let termsHtml = "";
    if (data.simplified_terms && Object.keys(data.simplified_terms).length > 0) {
        const cards = Object.entries(data.simplified_terms)
            .map(([term, meaning]) => `
                <div class="term-card">
                    <span class="term-name">${escapeHtml(term)}</span>
                    <span class="term-meaning">${escapeHtml(meaning)}</span>
                </div>`)
            .join("");
        termsHtml = `
            <div class="result-section">
                <div class="result-section-title">💡 Medical Jargon Explained</div>
                <div class="terms-grid">${cards}</div>
            </div>`;
    }

    // Next steps
    let stepsHtml = "";
    if (data.next_steps && data.next_steps.length > 0) {
        stepsHtml = `
            <div class="result-section">
                <div class="result-section-title">📋 Suggested Next Steps</div>
                <ul class="steps-list">
                    ${data.next_steps.map((s) => `<li>${escapeHtml(s)}</li>`).join("")}
                </ul>
            </div>`;
    }

    container.innerHTML = `
        <div class="glass-card results-container">
            <h2 class="card-title">Report Analysis Results</h2>

            <div class="result-section">
                <div class="result-section-title">📝 Executive Summary</div>
                <div class="report-summary-box">${escapeHtml(data.summary || "")}</div>
            </div>

            ${abnormalHtml}
            ${termsHtml}

            <div class="result-section">
                <div class="result-section-title">🔑 Key Findings</div>
                <ul class="steps-list">
                    ${(data.key_findings || []).map((f) => `<li>${escapeHtml(f)}</li>`).join("")}
                </ul>
            </div>

            ${stepsHtml}

            <div class="disclaimer-box">
                <strong>⚠️ Disclaimer:</strong> ${escapeHtml(data.disclaimer || "")}
            </div>
        </div>`;

    container.style.display = "block";
    container.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ============================================================
// TAB 3: HEALTH CHAT
// ============================================================
let chatHistory = [
    {
        role: "assistant",
        content: "Hello! I'm your AI Health Assistant powered by Gemma 3:1B. How can I help you understand health concepts or medical terms today? 🩺",
    },
];

function initChat() {
    const input = $("#chat-input");
    const sendBtn = $("#chat-send-btn");

    sendBtn.addEventListener("click", () => sendChatMessage());

    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendChatMessage();
        }
    });
}

async function sendChatMessage() {
    const input = $("#chat-input");
    const sendBtn = $("#chat-send-btn");
    const messagesEl = $("#chat-messages");
    const userText = input.value.trim();

    if (!userText) return;

    // Add user message
    chatHistory.push({ role: "user", content: userText });
    appendChatBubble("user", userText);
    input.value = "";
    sendBtn.disabled = true;

    // Show typing indicator
    const typingEl = createTypingIndicator();
    messagesEl.appendChild(typingEl);
    scrollChatToBottom();

    try {
        const res = await fetch(`${BACKEND_URL}/api/chat/query`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ messages: chatHistory }),
        });

        // Remove typing indicator
        typingEl.remove();

        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: res.statusText }));
            throw new Error(err.detail || "Chat request failed");
        }

        const data = await res.json();
        const reply = data.response || "I'm sorry, I couldn't generate a response.";

        chatHistory.push({ role: "assistant", content: reply });
        appendChatBubble("assistant", reply);
    } catch (err) {
        typingEl.remove();
        appendChatBubble("assistant", `⚠️ Error: ${err.message}. Please ensure the backend is running.`);
        showToast(`Chat error: ${err.message}`, "error");
    } finally {
        sendBtn.disabled = false;
        input.focus();
    }
}

function appendChatBubble(role, content) {
    const messagesEl = $("#chat-messages");
    const bubble = document.createElement("div");
    bubble.className = `chat-bubble ${role}`;
    bubble.textContent = content;
    messagesEl.appendChild(bubble);
    scrollChatToBottom();
}

function createTypingIndicator() {
    const el = document.createElement("div");
    el.className = "typing-indicator";
    el.innerHTML = `<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>`;
    return el;
}

function scrollChatToBottom() {
    const messagesEl = $("#chat-messages");
    requestAnimationFrame(() => {
        messagesEl.scrollTop = messagesEl.scrollHeight;
    });
}

// ============================================================
// UTILITIES
// ============================================================
function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// ============================================================
// INITIALIZATION
// ============================================================
document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initSeveritySlider();
    initTriageForm();
    initReportUpload();
    initChat();
    checkBackendHealth();

    // Periodic health check every 30 seconds
    setInterval(checkBackendHealth, 30000);
});
