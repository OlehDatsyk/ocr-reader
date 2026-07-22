/* =============================================================================
   OCR Reader — frontend application logic
   No build step, no framework: plain ES2020 running directly in the browser.
   ============================================================================= */

const OCRReader = (() => {
  "use strict";

  const THEME_KEY = "ocr-reader-theme";

  /* ---------------------------------------------------------------------- */
  /* Shared: theme + toast                                                   */
  /* ---------------------------------------------------------------------- */

  function getTheme() {
    return document.documentElement.getAttribute("data-theme") || "light";
  }

  function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(THEME_KEY, theme);
    syncThemeControls();
  }

  function toggleTheme() {
    setTheme(getTheme() === "dark" ? "light" : "dark");
  }

  function syncThemeControls() {
    const isDark = getTheme() === "dark";

    const dark = document.getElementById("theme-icon-dark");
    const light = document.getElementById("theme-icon-light");
    const label = document.getElementById("theme-toggle-label");
    if (dark && light) {
      dark.style.display = isDark ? "none" : "block";
      light.style.display = isDark ? "block" : "none";
    }
    if (label) {
      label.textContent = isDark ? "Light mode" : "Dark mode";
    }

    const settingsToggle = document.getElementById("settings-theme-toggle");
    if (settingsToggle) {
      settingsToggle.checked = isDark;
    }
  }

  function initThemeToggle() {
    syncThemeControls();
    const btn = document.getElementById("theme-toggle");
    if (btn) {
      btn.addEventListener("click", toggleTheme);
    }
  }

  let toastTimer = null;
  function showToast(message) {
    const toast = document.getElementById("toast");
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("visible"), 2600);
  }

  function formatBytes(bytes) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  }

  async function parseErrorResponse(response) {
    try {
      const data = await response.json();
      return data.detail || data.error || `Request failed (${response.status})`;
    } catch {
      return `Request failed (${response.status})`;
    }
  }

  function downloadBlob(filename, content, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  function baseName(filename) {
    return (filename || "ocr-result").replace(/\.[^.]+$/, "");
  }

  function toMarkdown(filename, language, model, text) {
    return [
      `# OCR Result — ${filename}`,
      "",
      `- **Detected language:** ${language}`,
      `- **Model:** ${model}`,
      "",
      "---",
      "",
      text.trim(),
      "",
    ].join("\n");
  }

  /* ---------------------------------------------------------------------- */
  /* Upload page                                                             */
  /* ---------------------------------------------------------------------- */

  function initUploadPage() {
    const dropzone = document.getElementById("dropzone");
    const dropzoneEmpty = document.getElementById("dropzone-empty");
    const dropzonePreview = document.getElementById("dropzone-preview");
    const previewImage = document.getElementById("preview-image");
    const scanBeam = document.getElementById("scan-beam");
    const fileInput = document.getElementById("file-input");
    const cameraInput = document.getElementById("camera-input");
    const browseBtn = document.getElementById("browse-btn");
    const cameraBtn = document.getElementById("camera-btn");
    const extractBtn = document.getElementById("extract-btn");
    const form = document.getElementById("ocr-form");
    const languageSelect = document.getElementById("language-select");
    const structuredToggle = document.getElementById("structured-toggle");
    const streamToggle = document.getElementById("stream-toggle");

    const resultMeta = document.getElementById("result-meta");
    const resultText = document.getElementById("result-text");
    const copyBtn = document.getElementById("copy-btn");
    const downloadTxtBtn = document.getElementById("download-txt-btn");
    const downloadMdBtn = document.getElementById("download-md-btn");

    let selectedFile = null;
    let lastResult = null; // { filename, text, detected_language, model }

    function setSelectedFile(file) {
      if (!file) return;
      selectedFile = file;
      const url = URL.createObjectURL(file);
      previewImage.src = url;
      dropzoneEmpty.style.display = "none";
      dropzonePreview.classList.add("visible");
      extractBtn.disabled = false;
    }

    dropzone.addEventListener("click", () => {
      if (!selectedFile) fileInput.click();
    });
    dropzone.addEventListener("keydown", (e) => {
      if ((e.key === "Enter" || e.key === " ") && !selectedFile) {
        e.preventDefault();
        fileInput.click();
      }
    });
    browseBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      fileInput.click();
    });
    cameraBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      cameraInput.click();
    });
    fileInput.addEventListener("change", () => {
      if (fileInput.files[0]) setSelectedFile(fileInput.files[0]);
    });
    cameraInput.addEventListener("change", () => {
      if (cameraInput.files[0]) setSelectedFile(cameraInput.files[0]);
    });

    ["dragenter", "dragover"].forEach((evt) =>
      dropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        dropzone.classList.add("drag-active");
      })
    );
    ["dragleave", "drop"].forEach((evt) =>
      dropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        dropzone.classList.remove("drag-active");
      })
    );
    dropzone.addEventListener("drop", (e) => {
      const file = e.dataTransfer.files && e.dataTransfer.files[0];
      if (file) setSelectedFile(file);
    });

    function setBusy(isBusy) {
      extractBtn.disabled = isBusy || !selectedFile;
      extractBtn.textContent = isBusy ? "Extracting…" : "";
      if (!isBusy) {
        extractBtn.innerHTML =
          '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21 21-4.34-4.34"/><circle cx="11" cy="11" r="8"/></svg> Extract text';
      } else {
        extractBtn.textContent = "Extracting…";
      }
      scanBeam.classList.toggle("scanning", isBusy);
    }

    function renderMeta({ detected_language, model, char_count, word_count, structured }) {
      resultMeta.style.display = "flex";
      resultMeta.innerHTML = "";
      const chips = [
        `Language: ${detected_language}`,
        `Model: ${model}`,
        `${char_count} chars`,
        `${word_count} words`,
        structured ? "Structured" : "Plain text",
      ];
      for (const label of chips) {
        const chip = document.createElement("span");
        chip.className = "chip";
        chip.textContent = label;
        resultMeta.appendChild(chip);
      }
    }

    function enableResultActions(enabled) {
      copyBtn.disabled = !enabled;
      downloadTxtBtn.disabled = !enabled;
      downloadMdBtn.disabled = !enabled;
    }

    async function submitExtraction(e) {
      e.preventDefault();
      if (!selectedFile) return;

      resultText.textContent = "";
      enableResultActions(false);
      resultMeta.style.display = "none";
      setBusy(true);

      const language = languageSelect.value;
      const structured = structuredToggle.checked;
      const streaming = streamToggle.checked && !structured;

      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("language", language);
      formData.append("structured", String(structured));

      try {
        if (streaming) {
          await runStreamingExtraction(formData, language);
        } else {
          await runSyncExtraction(formData, structured);
        }
      } catch (err) {
        showToast(err.message || "Extraction failed");
        resultText.textContent = "";
        resultText.setAttribute(
          "data-placeholder",
          `Extraction failed: ${err.message || "unknown error"}`
        );
      } finally {
        setBusy(false);
      }
    }

    async function runSyncExtraction(formData, structured) {
      const response = await fetch("/api/ocr/extract", { method: "POST", body: formData });
      if (!response.ok) throw new Error(await parseErrorResponse(response));
      const result = await response.json();
      resultText.textContent = result.text;
      renderMeta(result);
      enableResultActions(true);
      lastResult = result;
      showToast("Text extracted");
    }

    async function runStreamingExtraction(formData, language) {
      const response = await fetch("/api/ocr/stream", { method: "POST", body: formData });
      if (!response.ok) throw new Error(await parseErrorResponse(response));
      if (!response.body) throw new Error("Streaming is not supported in this browser.");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let finalResult = null;

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const events = buffer.split("\n\n");
        buffer = events.pop() || "";

        for (const rawEvent of events) {
          const line = rawEvent.trim();
          if (!line.startsWith("data:")) continue;
          const payload = JSON.parse(line.slice(5).trim());

          if (payload.type === "delta") {
            resultText.textContent += payload.text;
            resultText.scrollTop = resultText.scrollHeight;
          } else if (payload.type === "done") {
            finalResult = payload.result;
          } else if (payload.type === "error") {
            throw new Error(payload.message || "Streaming failed");
          }
        }
      }

      if (finalResult) {
        renderMeta(finalResult);
        enableResultActions(true);
        lastResult = finalResult;
        showToast("Text extracted");
      } else {
        throw new Error("The stream ended before a result was produced.");
      }
    }

    form.addEventListener("submit", submitExtraction);

    copyBtn.addEventListener("click", async () => {
      if (!resultText.textContent) return;
      await navigator.clipboard.writeText(resultText.textContent);
      showToast("Copied to clipboard");
    });

    downloadTxtBtn.addEventListener("click", () => {
      if (!lastResult) return;
      downloadBlob(`${baseName(lastResult.filename)}.txt`, lastResult.text, "text/plain");
    });

    downloadMdBtn.addEventListener("click", () => {
      if (!lastResult) return;
      const md = toMarkdown(
        lastResult.filename,
        lastResult.detected_language,
        lastResult.model,
        lastResult.text
      );
      downloadBlob(`${baseName(lastResult.filename)}.md`, md, "text/markdown");
    });
  }

  /* ---------------------------------------------------------------------- */
  /* History page                                                            */
  /* ---------------------------------------------------------------------- */

  function initHistoryPage() {
    const listEl = document.getElementById("history-list");
    const emptyEl = document.getElementById("history-empty");
    const countEl = document.getElementById("history-count");
    const clearBtn = document.getElementById("clear-history-btn");

    const modal = document.getElementById("history-modal");
    const modalFilename = document.getElementById("modal-filename");
    const modalMeta = document.getElementById("modal-meta");
    const modalText = document.getElementById("modal-text");
    const modalClose = document.getElementById("modal-close");
    const modalCopyBtn = document.getElementById("modal-copy-btn");
    const modalDownloadTxt = document.getElementById("modal-download-txt");
    const modalDownloadMd = document.getElementById("modal-download-md");
    const modalDeleteBtn = document.getElementById("modal-delete-btn");

    let activeId = null;

    function openModal(item) {
      activeId = item.id;
      modalFilename.textContent = item.filename;
      modalText.textContent = item.text;
      modalMeta.innerHTML = "";
      [
        `Language: ${item.language}`,
        `Model: ${item.model}`,
        `${item.char_count} chars`,
        `${item.word_count} words`,
      ].forEach((label) => {
        const chip = document.createElement("span");
        chip.className = "chip";
        chip.textContent = label;
        modalMeta.appendChild(chip);
      });
      modalDownloadTxt.href = `/api/history/${item.id}/download?fmt=txt`;
      modalDownloadMd.href = `/api/history/${item.id}/download?fmt=md`;
      modal.classList.add("open");
    }

    function closeModal() {
      modal.classList.remove("open");
      activeId = null;
    }

    modalClose.addEventListener("click", closeModal);
    modal.addEventListener("click", (e) => {
      if (e.target === modal) closeModal();
    });

    modalCopyBtn.addEventListener("click", async () => {
      await navigator.clipboard.writeText(modalText.textContent);
      showToast("Copied to clipboard");
    });

    modalDeleteBtn.addEventListener("click", async () => {
      if (activeId == null) return;
      await fetch(`/api/history/${activeId}`, { method: "DELETE" });
      closeModal();
      showToast("Extraction deleted");
      loadHistory();
    });

    clearBtn.addEventListener("click", async () => {
      if (!confirm("Delete all history? This cannot be undone.")) return;
      await fetch("/api/history", { method: "DELETE" });
      showToast("History cleared");
      loadHistory();
    });

    function renderRow(item) {
      const row = document.createElement("div");
      row.className = "history-row";
      row.innerHTML = `
        <div class="history-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        </div>
        <div class="history-body">
          <p class="history-filename"></p>
          <p class="history-preview"></p>
        </div>
        <div class="history-meta">
          <span class="history-meta-item"></span>
          <span class="history-meta-item"></span>
        </div>
        <div class="history-row-actions">
          <button type="button" class="icon-btn" aria-label="Delete">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
          </button>
        </div>
      `;
      row.querySelector(".history-filename").textContent = item.filename;
      row.querySelector(".history-preview").textContent = item.preview;
      const metaSpans = row.querySelectorAll(".history-meta-item");
      metaSpans[0].textContent = item.language;
      metaSpans[1].textContent = new Date(item.created_at.replace(" ", "T") + "Z").toLocaleString();

      row.addEventListener("click", async (e) => {
        if (e.target.closest(".icon-btn")) return;
        const response = await fetch(`/api/history/${item.id}`);
        if (!response.ok) {
          showToast("Could not load this item");
          return;
        }
        openModal(await response.json());
      });

      row.querySelector(".icon-btn").addEventListener("click", async (e) => {
        e.stopPropagation();
        await fetch(`/api/history/${item.id}`, { method: "DELETE" });
        showToast("Extraction deleted");
        loadHistory();
      });

      return row;
    }

    async function loadHistory() {
      countEl.textContent = "Loading…";
      const response = await fetch("/api/history?limit=100");
      if (!response.ok) {
        countEl.textContent = "Failed to load history";
        return;
      }
      const data = await response.json();
      listEl.innerHTML = "";

      if (data.items.length === 0) {
        emptyEl.style.display = "flex";
        countEl.textContent = "No extractions yet";
        return;
      }

      emptyEl.style.display = "none";
      countEl.textContent = `${data.total} extraction${data.total === 1 ? "" : "s"}`;
      for (const item of data.items) {
        listEl.appendChild(renderRow(item));
      }
    }

    loadHistory();
  }

  /* ---------------------------------------------------------------------- */
  /* Settings page                                                           */
  /* ---------------------------------------------------------------------- */

  function initSettingsPage() {
    const toggle = document.getElementById("settings-theme-toggle");
    if (!toggle) return;
    toggle.checked = getTheme() === "dark";
    toggle.addEventListener("change", () => setTheme(toggle.checked ? "dark" : "light"));
  }

  /* ---------------------------------------------------------------------- */
  /* Bootstrap                                                                */
  /* ---------------------------------------------------------------------- */

  document.addEventListener("DOMContentLoaded", initThemeToggle);

  return { initUploadPage, initHistoryPage, initSettingsPage };
})();
