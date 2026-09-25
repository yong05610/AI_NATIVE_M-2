const configuredApiBaseUrl = window.APP_CONFIG?.API_BASE_URL;
const API_BASE_URL = (configuredApiBaseUrl || "http://localhost:8000").replace(/\/+$/, "");

let editingDocumentId = null;
let mutationInProgress = false;

document.addEventListener("DOMContentLoaded", () => {
  const studyForm = document.querySelector("#study-form");
  const cancelButton = document.querySelector("#study-cancel-button");
  const chatForm = document.querySelector("#chat-form");

  studyForm?.addEventListener("submit", handleStudySubmit);
  cancelButton?.addEventListener("click", () => cancelEdit(true));

  chatForm?.addEventListener("submit", (event) => {
    event.preventDefault();
    showStatus("AI 채팅 연동은 다음 단계에서 구현합니다.", "info");
  });

  refreshStudyView();
});

async function request(path, options = {}) {
  const headers = { ...options.headers };

  if (options.body !== undefined && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let detail = `요청에 실패했습니다. (HTTP ${response.status})`;

    try {
      const errorBody = await response.json();
      detail = formatErrorDetail(errorBody.detail) || detail;
    } catch {
      // JSON 오류 응답이 아니면 기본 HTTP 오류 메시지를 사용합니다.
    }

    throw new Error(detail);
  }

  return response.json();
}

function formatErrorDetail(detail) {
  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail.map((item) => item?.msg || String(item)).join(" ");
  }

  return "";
}

async function refreshStudyView(successMessage = "") {
  setPageLoading(true);
  showStatus("학습기록과 요약 통계를 불러오는 중입니다...", "loading");

  try {
    await Promise.all([loadStudyData(), loadStudySummary()]);
    showStatus(successMessage || "학습기록과 요약 통계를 불러왔습니다.", "success");
  } catch (error) {
    showStatus(`데이터를 불러오지 못했습니다. ${getErrorMessage(error)}`, "error");
  } finally {
    setPageLoading(false);
  }
}

async function loadStudyData() {
  const studyList = document.querySelector("#study-list");

  if (studyList) {
    studyList.replaceChildren(createMessage("학습기록을 불러오는 중입니다...", "loading-message"));
  }

  const records = await request("/api/data");
  renderStudyData(Array.isArray(records) ? records : []);
}

async function loadStudySummary() {
  const summaryContent = document.querySelector("#summary-content");
  summaryContent?.setAttribute("aria-busy", "true");

  try {
    const summary = await request("/api/data/summary");
    renderStudySummary(summary);
  } finally {
    summaryContent?.setAttribute("aria-busy", "false");
  }
}

async function handleStudySubmit(event) {
  event.preventDefault();

  if (mutationInProgress) {
    return;
  }

  const payload = readStudyForm();

  if (!payload) {
    return;
  }

  setMutationState(true);
  showStatus(editingDocumentId ? "학습기록을 수정하는 중입니다..." : "학습기록을 등록하는 중입니다...", "loading");

  try {
    const isEditing = Boolean(editingDocumentId);
    const path = isEditing
      ? `/api/data/${encodeURIComponent(editingDocumentId)}`
      : "/api/data";

    await request(path, {
      method: isEditing ? "PUT" : "POST",
      body: JSON.stringify(payload),
    });

    cancelEdit(false);
    await refreshStudyView(isEditing ? "학습기록을 수정했습니다." : "학습기록을 등록했습니다.");
  } catch (error) {
    showStatus(`학습기록을 저장하지 못했습니다. ${getErrorMessage(error)}`, "error");
  } finally {
    setMutationState(false);
  }
}

function readStudyForm() {
  const dateInput = document.querySelector("#study-date");
  const valueInput = document.querySelector("#study-value");
  const memoInput = document.querySelector("#study-memo");
  const date = dateInput?.value || "";
  const value = Number(valueInput?.value);
  const memo = memoInput?.value.trim() || "";

  if (!date) {
    showStatus("학습 날짜를 입력해 주세요.", "error");
    dateInput?.focus();
    return null;
  }

  if (!Number.isFinite(value) || value <= 0) {
    showStatus("학습시간은 0보다 큰 숫자로 입력해 주세요.", "error");
    valueInput?.focus();
    return null;
  }

  return { date, value, memo };
}

function renderStudyData(records) {
  const studyList = document.querySelector("#study-list");

  if (!studyList) {
    return;
  }

  if (records.length === 0) {
    studyList.replaceChildren(createMessage("저장된 학습기록이 없습니다.", "empty-message"));
    return;
  }

  const list = document.createElement("ul");
  list.className = "study-records";

  records.forEach((record) => {
    const item = document.createElement("li");
    item.className = "study-record";

    const content = document.createElement("div");
    content.className = "study-record-content";

    const title = document.createElement("strong");
    title.textContent = `${formatMinutes(record.value)}분`;

    const date = document.createElement("span");
    date.textContent = record.date;

    const memo = document.createElement("p");
    memo.textContent = record.memo || "메모 없음";

    content.append(title, date, memo);

    const actions = document.createElement("div");
    actions.className = "record-actions";

    const editButton = document.createElement("button");
    editButton.type = "button";
    editButton.className = "secondary-button record-action-button";
    editButton.textContent = "수정";
    editButton.disabled = mutationInProgress;
    editButton.addEventListener("click", () => startEdit(record));

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.className = "delete-button record-action-button";
    deleteButton.textContent = "삭제";
    deleteButton.disabled = mutationInProgress;
    deleteButton.addEventListener("click", () => deleteStudyData(record));

    actions.append(editButton, deleteButton);
    item.append(content, actions);
    list.append(item);
  });

  studyList.replaceChildren(list);
}

function renderStudySummary(summary) {
  setText("#summary-count", `${formatNumber(summary.count)}개`);
  setText("#summary-total", `${formatMinutes(summary.total_minutes)}분`);
  setText("#summary-average", `${formatMinutes(summary.average_minutes)}분`);
  setText("#summary-max", `${formatMinutes(summary.max_minutes)}분`);
  setText("#summary-min", `${formatMinutes(summary.min_minutes)}분`);
  setText("#summary-recent-total", `${formatMinutes(summary.recent_7_days_total)}분`);
  setText("#summary-trend", formatTrend(summary.recent_trend));
}

function startEdit(record) {
  if (mutationInProgress) {
    return;
  }

  editingDocumentId = record.id;
  setInputValue("#study-date", record.date);
  setInputValue("#study-value", record.value);
  setInputValue("#study-memo", record.memo || "");

  const submitButton = document.querySelector("#study-submit-button");
  const cancelButton = document.querySelector("#study-cancel-button");

  if (submitButton) {
    submitButton.textContent = "수정 저장";
  }

  if (cancelButton) {
    cancelButton.hidden = false;
  }

  showStatus(`${record.date} 학습기록을 수정하고 있습니다.`, "info");
  document.querySelector("#study-form-section")?.scrollIntoView({ behavior: "smooth" });
}

function cancelEdit(showMessage) {
  editingDocumentId = null;
  document.querySelector("#study-form")?.reset();

  const submitButton = document.querySelector("#study-submit-button");
  const cancelButton = document.querySelector("#study-cancel-button");

  if (submitButton) {
    submitButton.textContent = "등록";
  }

  if (cancelButton) {
    cancelButton.hidden = true;
  }

  if (showMessage) {
    showStatus("수정을 취소했습니다.", "info");
  }
}

async function deleteStudyData(record) {
  if (mutationInProgress || !window.confirm(`${record.date} 학습기록을 삭제할까요?`)) {
    return;
  }

  setMutationState(true);
  showStatus("학습기록을 삭제하는 중입니다...", "loading");

  try {
    await request(`/api/data/${encodeURIComponent(record.id)}`, { method: "DELETE" });

    if (editingDocumentId === record.id) {
      cancelEdit(false);
    }

    await refreshStudyView("학습기록을 삭제했습니다.");
  } catch (error) {
    showStatus(`학습기록을 삭제하지 못했습니다. ${getErrorMessage(error)}`, "error");
  } finally {
    setMutationState(false);
  }
}

function setPageLoading(isLoading) {
  const summaryContent = document.querySelector("#summary-content");
  summaryContent?.setAttribute("aria-busy", String(isLoading));
}

function setMutationState(isBusy) {
  mutationInProgress = isBusy;

  document.querySelectorAll("#study-form button, .record-action-button").forEach((button) => {
    button.disabled = isBusy;
  });
}

function showStatus(message, type) {
  const statusSection = document.querySelector("#status-section");
  const statusMessage = document.querySelector("#status-message");

  if (!statusMessage || !statusSection) {
    return;
  }

  statusMessage.textContent = message;
  statusSection.classList.remove("is-loading", "is-success", "is-error");

  if (type === "loading") {
    statusSection.classList.add("is-loading");
  } else if (type === "success") {
    statusSection.classList.add("is-success");
  } else if (type === "error") {
    statusSection.classList.add("is-error");
  }
}

function createMessage(message, className) {
  const paragraph = document.createElement("p");
  paragraph.className = className;
  paragraph.textContent = message;
  return paragraph;
}

function setText(selector, value) {
  const element = document.querySelector(selector);

  if (element) {
    element.textContent = value;
  }
}

function setInputValue(selector, value) {
  const input = document.querySelector(selector);

  if (input) {
    input.value = String(value);
  }
}

function formatNumber(value) {
  const number = Number(value);
  return Number.isFinite(number)
    ? new Intl.NumberFormat("ko-KR", { maximumFractionDigits: 1 }).format(number)
    : "0";
}

function formatMinutes(value) {
  return formatNumber(value);
}

function formatTrend(trend) {
  const trendLabels = {
    increasing: "증가 추세",
    decreasing: "감소 추세",
    stable: "안정적",
    not_enough_data: "데이터 부족",
  };

  return trendLabels[trend] || "데이터 부족";
}

function getErrorMessage(error) {
  return error instanceof Error ? error.message : "알 수 없는 오류가 발생했습니다.";
}
