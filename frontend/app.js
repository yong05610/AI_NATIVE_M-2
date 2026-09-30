const configuredApiBaseUrl = window.APP_CONFIG?.API_BASE_URL;
const API_BASE_URL = (configuredApiBaseUrl || "http://127.0.0.1:8001").replace(/\/+$/, "");

let editingDocumentId = null;
let mutationInProgress = false;
let activeConversationId = null;
let chatRequestInProgress = false;
let conversationMutationInProgress = false;

document.addEventListener("DOMContentLoaded", () => {
  const studyForm = document.querySelector("#study-form");
  const cancelButton = document.querySelector("#study-cancel-button");
  const chatForm = document.querySelector("#chat-form");
  const dateInput = document.querySelector("#study-date");
  const valueInput = document.querySelector("#study-value");
  const memoInput = document.querySelector("#study-memo");
  const chatInput = document.querySelector("#chat-message");

  studyForm?.addEventListener("submit", handleStudySubmit);
  cancelButton?.addEventListener("click", () => cancelEdit(true));
  chatForm?.addEventListener("submit", handleChatSubmit);

  dateInput?.addEventListener("input", updateStudySubmitAvailability);
  valueInput?.addEventListener("input", updateStudySubmitAvailability);
  memoInput?.addEventListener("input", updateMemoCount);
  chatInput?.addEventListener("input", () => {
    updateChatMessageCount();
    updateChatSubmitAvailability();
  });

  updateStudySubmitAvailability();
  updateMemoCount();
  updateChatMessageCount();
  updateChatSubmitAvailability();

  refreshStudyView();
  loadConversations();
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

  const [dataResult, summaryResult] = await Promise.allSettled([
    loadStudyData(),
    loadStudySummary(),
  ]);

  if (dataResult.status === "rejected") {
    const message = getErrorMessage(dataResult.reason);
    renderStudyListError(message);
    showAreaFeedback("#study-list-feedback", `학습시간 데이터 오류: ${message}`, "error");
  }

  if (summaryResult.status === "rejected") {
    const message = getErrorMessage(summaryResult.reason);
    renderStudySummary(createEmptySummary());
    showAreaFeedback("#summary-feedback", `요약 통계 오류: ${message}`, "error");
  }

  if (dataResult.status === "fulfilled" && summaryResult.status === "fulfilled") {
    showStatus(successMessage || "학습기록과 요약 통계를 불러왔습니다.", "success");
  } else {
    showStatus("일부 학습 데이터를 불러오지 못했습니다. 영역별 오류 안내를 확인한 뒤 다시 시도해 주세요.", "error");
  }

  setPageLoading(false);
}

async function loadStudyData() {
  const studyList = document.querySelector("#study-list");

  if (studyList) {
    studyList.setAttribute("aria-busy", "true");
    studyList.replaceChildren(createMessage("학습기록을 불러오는 중입니다...", "loading-message"));
  }

  showAreaFeedback("#study-list-feedback", "학습기록을 불러오는 중입니다.", "loading");

  try {
    const records = await request("/api/data");
    renderStudyData(Array.isArray(records) ? records : []);
    clearAreaFeedback("#study-list-feedback");
  } finally {
    studyList?.setAttribute("aria-busy", "false");
  }
}

async function loadStudySummary() {
  const summaryContent = document.querySelector("#summary-content");
  summaryContent?.setAttribute("aria-busy", "true");
  showAreaFeedback("#summary-feedback", "학습 통계를 계산해 불러오는 중입니다.", "loading");

  try {
    const summary = await request("/api/data/summary");
    renderStudySummary(summary);
    const count = Number(summary.count);

    if (Number.isFinite(count) && count === 0) {
      showAreaFeedback("#summary-feedback", "아직 요약할 학습기록이 없습니다. 첫 학습시간을 등록해 보세요.", "info");
    } else {
      clearAreaFeedback("#summary-feedback");
    }
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

  const isEditing = Boolean(editingDocumentId);
  setMutationState(true, isEditing ? "수정 저장 중..." : "등록 중...");
  showAreaFeedback(
    "#study-form-feedback",
    isEditing ? "학습기록을 수정하는 중입니다." : "학습기록을 등록하는 중입니다.",
    "loading",
  );
  showStatus(isEditing ? "학습기록을 수정하는 중입니다..." : "학습기록을 등록하는 중입니다...", "loading");

  try {
    const path = isEditing
      ? `/api/data/${encodeURIComponent(editingDocumentId)}`
      : "/api/data";

    await request(path, {
      method: isEditing ? "PUT" : "POST",
      body: JSON.stringify(payload),
    });

    cancelEdit(false);
    await refreshStudyView(isEditing ? "학습기록을 수정했습니다." : "학습기록을 등록했습니다.");
    showAreaFeedback(
      "#study-form-feedback",
      isEditing ? "학습기록을 수정했습니다." : "학습기록을 등록했습니다.",
      "success",
    );
  } catch (error) {
    const message = getErrorMessage(error);
    showAreaFeedback("#study-form-feedback", `학습시간 데이터 오류: ${message}`, "error");
    showStatus(`학습기록을 저장하지 못했습니다. ${message}`, "error");
  } finally {
    setMutationState(false);
  }
}

function readStudyForm() {
  const dateInput = document.querySelector("#study-date");
  const valueInput = document.querySelector("#study-value");
  const memoInput = document.querySelector("#study-memo");
  const date = dateInput?.value || "";
  const rawValue = valueInput?.value.trim() || "";
  const value = Number(rawValue);
  const memo = memoInput?.value.trim() || "";

  if (!date) {
    showAreaFeedback("#study-form-feedback", "학습 날짜를 입력해 주세요.", "error");
    showStatus("학습 날짜를 입력해 주세요.", "error");
    dateInput?.focus();
    return null;
  }

  if (!rawValue) {
    showAreaFeedback("#study-form-feedback", "학습시간을 분 단위로 입력해 주세요.", "error");
    showStatus("학습시간을 입력해 주세요.", "error");
    valueInput?.focus();
    return null;
  }

  if (!Number.isFinite(value)) {
    showAreaFeedback("#study-form-feedback", "학습시간은 숫자로 입력해 주세요.", "error");
    showStatus("학습시간은 숫자로 입력해 주세요.", "error");
    valueInput?.focus();
    return null;
  }

  if (value <= 0) {
    showAreaFeedback("#study-form-feedback", "학습시간은 0보다 큰 숫자로 입력해 주세요.", "error");
    showStatus("학습시간은 0보다 큰 숫자로 입력해 주세요.", "error");
    valueInput?.focus();
    return null;
  }

  if (memo.length > 200) {
    showAreaFeedback("#study-form-feedback", "메모는 200자 이하로 입력해 주세요.", "error");
    showStatus("메모가 너무 깁니다. 200자 이하로 입력해 주세요.", "error");
    memoInput?.focus();
    return null;
  }

  clearAreaFeedback("#study-form-feedback");

  return { date, value, memo };
}

function renderStudyData(records) {
  const studyList = document.querySelector("#study-list");

  if (!studyList) {
    return;
  }

  if (records.length === 0) {
    studyList.replaceChildren(
      createMessage("아직 저장된 학습기록이 없습니다. 위 입력 폼에서 첫 기록을 추가해 보세요.", "empty-message"),
    );
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
    date.textContent = formatStudyDate(record.date);

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
    deleteButton.addEventListener("click", () => deleteStudyData(record, deleteButton));

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
  updateMemoCount();
  updateStudySubmitAvailability();

  const submitButton = document.querySelector("#study-submit-button");
  const cancelButton = document.querySelector("#study-cancel-button");

  if (submitButton) {
    submitButton.textContent = "수정 저장";
  }

  if (cancelButton) {
    cancelButton.hidden = false;
  }

  clearAreaFeedback("#study-form-feedback");
  showStatus(`${formatStudyDate(record.date)} 학습기록을 수정하고 있습니다.`, "info");
  document.querySelector("#study-form-section")?.scrollIntoView({ behavior: "smooth" });
}

function cancelEdit(showMessage) {
  editingDocumentId = null;
  document.querySelector("#study-form")?.reset();
  updateMemoCount();

  const submitButton = document.querySelector("#study-submit-button");
  const cancelButton = document.querySelector("#study-cancel-button");

  if (submitButton) {
    submitButton.textContent = "등록";
  }

  if (cancelButton) {
    cancelButton.hidden = true;
  }

  if (showMessage) {
    showAreaFeedback("#study-form-feedback", "학습기록 수정을 취소했습니다.", "info");
    showStatus("수정을 취소했습니다.", "info");
  }

  updateStudySubmitAvailability();
}

async function deleteStudyData(record, deleteButton) {
  if (mutationInProgress || !window.confirm(`${record.date} 학습기록을 삭제할까요?`)) {
    return;
  }

  setMutationState(true, "처리 중...");

  if (deleteButton) {
    deleteButton.textContent = "삭제 중...";
  }

  showAreaFeedback("#study-list-feedback", "학습기록을 삭제하는 중입니다.", "loading");
  showStatus("학습기록을 삭제하는 중입니다...", "loading");

  try {
    await request(`/api/data/${encodeURIComponent(record.id)}`, { method: "DELETE" });

    if (editingDocumentId === record.id) {
      cancelEdit(false);
    }

    await refreshStudyView("학습기록을 삭제했습니다.");
    showAreaFeedback("#study-list-feedback", "학습기록을 삭제했습니다.", "success");
  } catch (error) {
    const message = getErrorMessage(error);
    showAreaFeedback("#study-list-feedback", `학습시간 데이터 오류: ${message}`, "error");
    showStatus(`학습기록을 삭제하지 못했습니다. ${message}`, "error");
  } finally {
    if (deleteButton?.isConnected) {
      deleteButton.textContent = "삭제";
    }
    setMutationState(false);
  }
}

async function handleChatSubmit(event) {
  event.preventDefault();

  if (chatRequestInProgress) {
    return;
  }

  const messageInput = document.querySelector("#chat-message");
  const message = messageInput?.value.trim() || "";

  if (!message) {
    showAreaFeedback("#chat-feedback", "AI에게 보낼 질문을 입력해 주세요.", "error");
    showStatus("AI에게 보낼 질문을 입력해 주세요.", "error");
    messageInput?.focus();
    return;
  }

  if (message.length > 500) {
    showAreaFeedback("#chat-feedback", "질문은 500자 이하로 입력해 주세요.", "error");
    showStatus("질문이 너무 깁니다. 500자 이하로 입력해 주세요.", "error");
    messageInput?.focus();
    return;
  }

  setChatLoading(true);
  renderChatLoading();
  showAreaFeedback("#chat-feedback", "AI가 학습 데이터를 분석해 답변하고 있습니다.", "loading");
  showStatus("AI가 학습 데이터를 분석해 답변하고 있습니다...", "loading");

  try {
    const conversation = await request("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message }),
    });

    activeConversationId = conversation.id;
    renderConversationDetail(conversation);

    if (messageInput) {
      messageInput.value = "";
    }

    updateChatMessageCount();

    await loadConversations();
    showAreaFeedback("#chat-feedback", "AI 답변을 받았습니다.", "success");
    showStatus("AI 답변을 받았습니다.", "success");
  } catch (error) {
    const errorMessage = getErrorMessage(error);
    renderChatError(`AI 답변을 받지 못했습니다. ${errorMessage}`);
    showAreaFeedback("#chat-feedback", `AI 채팅 오류: ${errorMessage}`, "error");
    showStatus(`AI 답변 요청에 실패했습니다. ${errorMessage}`, "error");
  } finally {
    setChatLoading(false);
  }
}

async function loadConversations() {
  const conversationList = document.querySelector("#conversation-list");

  if (!conversationList) {
    return false;
  }

  conversationList.setAttribute("aria-busy", "true");
  conversationList.replaceChildren(createMessage("대화 기록을 불러오는 중입니다...", "loading-message"));
  showAreaFeedback("#conversation-feedback", "이전 대화 목록을 불러오는 중입니다.", "loading");

  try {
    const conversations = await request("/api/conversations");
    renderConversationList(Array.isArray(conversations) ? conversations : []);

    if (Array.isArray(conversations) && conversations.length === 0) {
      showAreaFeedback("#conversation-feedback", "아직 저장된 대화가 없습니다. AI에게 첫 질문을 보내보세요.", "info");
    } else {
      clearAreaFeedback("#conversation-feedback");
    }

    return true;
  } catch (error) {
    const errorMessage = getErrorMessage(error);
    conversationList.replaceChildren(
      createMessage(`대화 기록을 불러오지 못했습니다. ${errorMessage}`, "conversation-error"),
    );
    showAreaFeedback("#conversation-feedback", `대화 기록 오류: ${errorMessage}`, "error");
    showStatus(`대화 기록 조회에 실패했습니다. ${errorMessage}`, "error");
    return false;
  } finally {
    conversationList.setAttribute("aria-busy", "false");
  }
}

function renderConversationList(conversations) {
  const conversationList = document.querySelector("#conversation-list");

  if (!conversationList) {
    return;
  }

  if (conversations.length === 0) {
    conversationList.replaceChildren(
      createMessage("아직 저장된 대화가 없습니다. AI에게 첫 질문을 보내보세요.", "empty-message"),
    );
    return;
  }

  const list = document.createElement("ul");
  list.className = "conversation-records";

  conversations.forEach((conversation) => {
    const item = document.createElement("li");
    item.className = "conversation-record";
    item.dataset.conversationId = conversation.id;
    item.classList.toggle("is-selected", conversation.id === activeConversationId);

    const selectButton = document.createElement("button");
    selectButton.type = "button";
    selectButton.className = "conversation-select-button conversation-action-button";
    selectButton.disabled = conversationMutationInProgress;
    selectButton.setAttribute("aria-pressed", String(conversation.id === activeConversationId));
    selectButton.setAttribute("aria-label", `대화 불러오기: ${conversation.message}`);
    selectButton.addEventListener("click", () => loadConversationDetail(conversation.id));

    const question = document.createElement("strong");
    question.textContent = conversation.message;

    const answer = document.createElement("span");
    answer.textContent = summarizeAnswer(conversation.answer);

    const createdAt = document.createElement("time");
    if (conversation.created_at) {
      createdAt.dateTime = conversation.created_at;
    }
    createdAt.textContent = formatConversationDate(conversation.created_at);

    selectButton.append(question, answer, createdAt);

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.className = "conversation-delete-button conversation-action-button";
    deleteButton.textContent = "삭제";
    deleteButton.disabled = conversationMutationInProgress;
    deleteButton.setAttribute("aria-label", `대화 삭제: ${conversation.message}`);
    deleteButton.addEventListener("click", () => deleteConversation(conversation));

    item.append(selectButton, deleteButton);
    list.append(item);
  });

  conversationList.replaceChildren(list);
}

async function loadConversationDetail(documentId) {
  if (conversationMutationInProgress) {
    return;
  }

  setConversationMutationState(true);
  showAreaFeedback("#conversation-feedback", "선택한 대화를 불러오는 중입니다.", "loading");
  showStatus("선택한 대화를 불러오는 중입니다...", "loading");

  try {
    const conversation = await request(`/api/conversations/${encodeURIComponent(documentId)}`);
    activeConversationId = conversation.id;
    renderConversationDetail(conversation);
    markSelectedConversation();
    showAreaFeedback("#conversation-feedback", "선택한 대화를 채팅 영역에 복원했습니다.", "success");
    showStatus("선택한 대화를 불러왔습니다.", "success");
  } catch (error) {
    const message = getErrorMessage(error);
    showAreaFeedback("#conversation-feedback", `대화 기록 오류: ${message}`, "error");
    showStatus(`대화를 불러오지 못했습니다. ${message}`, "error");
  } finally {
    setConversationMutationState(false);
  }
}

async function deleteConversation(conversation) {
  if (
    conversationMutationInProgress
    || !window.confirm("이 대화 기록을 삭제할까요?")
  ) {
    return;
  }

  setConversationMutationState(true, "삭제 중...");
  showAreaFeedback("#conversation-feedback", "대화 기록을 삭제하는 중입니다.", "loading");
  showStatus("대화 기록을 삭제하는 중입니다...", "loading");

  try {
    await request(`/api/conversations/${encodeURIComponent(conversation.id)}`, {
      method: "DELETE",
    });

    if (activeConversationId === conversation.id) {
      activeConversationId = null;
      resetChatResult();
    }

    const listLoaded = await loadConversations();

    if (listLoaded) {
      showAreaFeedback("#conversation-feedback", "대화 기록을 삭제했습니다.", "success");
      showStatus("대화 기록을 삭제했습니다.", "success");
    }
  } catch (error) {
    const message = getErrorMessage(error);
    showAreaFeedback("#conversation-feedback", `대화 기록 오류: ${message}`, "error");
    showStatus(`대화 기록을 삭제하지 못했습니다. ${message}`, "error");
  } finally {
    setConversationMutationState(false);
  }
}

function renderConversationDetail(conversation) {
  const chatResult = document.querySelector("#chat-result");

  if (!chatResult) {
    return;
  }

  const heading = document.createElement("h3");
  heading.textContent = "AI 답변";

  const questionBlock = createChatMessageBlock("질문", conversation.message);
  const answerBlock = createChatMessageBlock("AI 답변", conversation.answer);
  const createdAt = document.createElement("time");
  createdAt.className = "chat-created-at";
  if (conversation.created_at) {
    createdAt.dateTime = conversation.created_at;
  }
  createdAt.textContent = `생성 시간: ${formatConversationDate(conversation.created_at)}`;

  chatResult.replaceChildren(heading, questionBlock, answerBlock, createdAt);
}

function createChatMessageBlock(label, message) {
  const block = document.createElement("div");
  block.className = "chat-message-block";

  const labelElement = document.createElement("strong");
  labelElement.textContent = label;

  const messageElement = document.createElement("p");
  messageElement.textContent = message;

  block.append(labelElement, messageElement);
  return block;
}

function renderChatLoading() {
  const chatResult = document.querySelector("#chat-result");

  if (chatResult) {
    chatResult.replaceChildren(createMessage("AI가 답변을 생성하는 중입니다...", "loading-message"));
    chatResult.setAttribute("aria-busy", "true");
  }
}

function renderChatError(message) {
  const chatResult = document.querySelector("#chat-result");

  if (chatResult) {
    chatResult.replaceChildren(createMessage(message, "conversation-error"));
  }
}

function resetChatResult() {
  const chatResult = document.querySelector("#chat-result");

  if (!chatResult) {
    return;
  }

  const heading = document.createElement("h3");
  heading.textContent = "AI 답변";
  chatResult.replaceChildren(
    heading,
    createMessage("학습 흐름이나 다음 학습 계획에 대해 AI에게 질문해 보세요.", "empty-message"),
  );
}

function setChatLoading(isLoading) {
  chatRequestInProgress = isLoading;

  const messageInput = document.querySelector("#chat-message");
  const submitButton = document.querySelector("#chat-submit-button");
  const chatResult = document.querySelector("#chat-result");

  if (messageInput) {
    messageInput.disabled = isLoading;
  }

  if (submitButton) {
    submitButton.textContent = isLoading ? "AI가 답변 중입니다..." : "AI에게 질문하기";
  }

  chatResult?.setAttribute("aria-busy", String(isLoading));
  updateChatSubmitAvailability();
}

function setConversationMutationState(isBusy, pendingLabel = "") {
  conversationMutationInProgress = isBusy;

  document.querySelectorAll(".conversation-action-button").forEach((button) => {
    button.disabled = isBusy;

    if (button.classList.contains("conversation-delete-button")) {
      if (isBusy && pendingLabel) {
        button.dataset.idleText = button.textContent;
        button.textContent = pendingLabel;
      } else if (!isBusy && button.dataset.idleText) {
        button.textContent = button.dataset.idleText;
        delete button.dataset.idleText;
      }
    }
  });
}

function markSelectedConversation() {
  document.querySelectorAll(".conversation-record").forEach((item) => {
    const isSelected = item.dataset.conversationId === activeConversationId;
    item.classList.toggle("is-selected", isSelected);
    item.querySelector(".conversation-select-button")?.setAttribute("aria-pressed", String(isSelected));
  });
}

function updateStudySubmitAvailability() {
  const submitButton = document.querySelector("#study-submit-button");
  const dateValue = document.querySelector("#study-date")?.value.trim() || "";
  const rawStudyValue = document.querySelector("#study-value")?.value.trim() || "";
  const studyValue = Number(rawStudyValue);
  const hasValidRequiredValues = Boolean(dateValue)
    && rawStudyValue !== ""
    && Number.isFinite(studyValue)
    && studyValue > 0;

  if (submitButton) {
    submitButton.disabled = mutationInProgress || !hasValidRequiredValues;
  }
}

function updateChatSubmitAvailability() {
  const submitButton = document.querySelector("#chat-submit-button");
  const message = document.querySelector("#chat-message")?.value.trim() || "";

  if (submitButton) {
    submitButton.disabled = chatRequestInProgress || message.length === 0 || message.length > 500;
  }
}

function updateMemoCount() {
  const memoInput = document.querySelector("#study-memo");
  const counter = document.querySelector("#study-memo-count");

  if (counter) {
    counter.textContent = `${memoInput?.value.length || 0} / 200`;
  }
}

function updateChatMessageCount() {
  const messageInput = document.querySelector("#chat-message");
  const counter = document.querySelector("#chat-message-count");

  if (counter) {
    counter.textContent = `${messageInput?.value.length || 0} / 500`;
  }
}

function showAreaFeedback(selector, message, type = "") {
  const feedback = document.querySelector(selector);

  if (!feedback) {
    return;
  }

  feedback.hidden = false;
  feedback.textContent = message;
  feedback.classList.remove("is-loading", "is-success", "is-error");
  feedback.setAttribute("aria-live", type === "error" ? "assertive" : "polite");

  if (type) {
    feedback.classList.add(`is-${type}`);
  }
}

function clearAreaFeedback(selector) {
  const feedback = document.querySelector(selector);

  if (!feedback) {
    return;
  }

  feedback.hidden = true;
  feedback.textContent = "";
  feedback.classList.remove("is-loading", "is-success", "is-error");
}

function renderStudyListError(message) {
  const studyList = document.querySelector("#study-list");

  if (studyList) {
    studyList.replaceChildren(createMessage(`학습기록을 표시할 수 없습니다. ${message}`, "conversation-error"));
  }
}

function createEmptySummary() {
  return {
    count: 0,
    total_minutes: 0,
    average_minutes: 0,
    max_minutes: 0,
    min_minutes: 0,
    recent_7_days_total: 0,
    recent_trend: "not_enough_data",
  };
}

function summarizeAnswer(answer) {
  const normalizedAnswer = String(answer || "").replace(/\s+/g, " ").trim();
  return normalizedAnswer.length > 90
    ? `${normalizedAnswer.slice(0, 90)}…`
    : normalizedAnswer || "답변 없음";
}

function formatConversationDate(value) {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value || "생성 시간 없음";
  }

  return new Intl.DateTimeFormat("ko-KR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function formatStudyDate(value) {
  if (!value) {
    return "날짜 없음";
  }

  const date = new Date(`${value}T00:00:00`);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("ko-KR", {
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(date);
}

function setPageLoading(isLoading) {
  const summaryContent = document.querySelector("#summary-content");
  summaryContent?.setAttribute("aria-busy", String(isLoading));
}

function setMutationState(isBusy, pendingLabel = "") {
  mutationInProgress = isBusy;

  const submitButton = document.querySelector("#study-submit-button");
  const cancelButton = document.querySelector("#study-cancel-button");

  document.querySelectorAll(".record-action-button").forEach((button) => {
    button.disabled = isBusy;
  });

  if (submitButton) {
    submitButton.textContent = isBusy
      ? pendingLabel || "처리 중..."
      : editingDocumentId
        ? "수정 저장"
        : "등록";
  }

  if (cancelButton) {
    cancelButton.disabled = isBusy;
  }

  updateStudySubmitAvailability();
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
