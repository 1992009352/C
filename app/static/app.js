const state = {
  dashboard: null,
  modules: {},
  records: [],
};

const moduleFields = {
  expense: [
    ["amount", "金额", "number"],
    ["category", "分类", "text"],
    ["merchant", "商户", "text"],
  ],
  exercise: [
    ["duration", "分钟", "number"],
    ["distance", "距离 km", "number"],
    ["intensity", "强度", "text"],
  ],
  reading: [
    ["book", "书名", "text"],
    ["progress", "进度", "number"],
    ["unit", "单位", "text"],
  ],
  health: [
    ["metric", "指标", "text"],
    ["value", "数值", "number"],
    ["unit", "单位", "text"],
  ],
  diet: [
    ["calories", "热量", "number"],
    ["protein", "蛋白质", "number"],
    ["carbs", "碳水", "number"],
  ],
  experience: [
    ["place", "地点", "text"],
    ["mood", "感受", "text"],
  ],
  todo: [
    ["priority", "优先级", "text"],
    ["due_date", "截止日期", "date"],
  ],
  note: [["content", "内容", "text"]],
  password: [
    ["account", "账号", "text"],
    ["url", "网址", "url"],
    ["secret", "密码", "password"],
  ],
  contact: [
    ["name", "姓名", "text"],
    ["phone", "电话", "text"],
    ["relation", "关系", "text"],
  ],
  bill: [
    ["amount", "金额", "number"],
    ["due_date", "到期日", "date"],
    ["cycle", "周期", "text"],
  ],
};

const $ = (selector) => document.querySelector(selector);

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "请求失败");
  }
  return data;
}

async function bootstrap() {
  bindEvents();
  await refreshAll();
}

function bindEvents() {
  $("#record-module").addEventListener("change", renderDetailFields);
  $("#record-form").addEventListener("submit", submitRecord);
  $("#quick-form").addEventListener("submit", submitQuickEntry);
  $("#reminder-form").addEventListener("submit", submitReminder);
  $("#module-filter").addEventListener("change", refreshRecords);
  $("#export-data").addEventListener("click", exportData);
}

async function refreshAll() {
  const [dashboard, records, forecast] = await Promise.all([
    api("/api/dashboard"),
    api("/api/records?limit=80"),
    api("/api/forecast"),
  ]);
  state.dashboard = dashboard;
  state.modules = dashboard.modules;
  state.records = records.records;
  state.forecast = forecast;
  renderModules();
  renderDashboard();
  renderDetailFields();
  renderRecords();
}

function renderModules() {
  const moduleSelect = $("#record-module");
  const filter = $("#module-filter");
  const selectedModule = moduleSelect.value;
  const selectedFilter = filter.value;
  const options = Object.entries(state.modules)
    .map(([key, item]) => `<option value="${key}">${item.label}</option>`)
    .join("");
  moduleSelect.innerHTML = options;
  filter.innerHTML = `<option value="">全部模块</option>${options}`;
  if (selectedModule && state.modules[selectedModule]) {
    moduleSelect.value = selectedModule;
  }
  if (selectedFilter && state.modules[selectedFilter]) {
    filter.value = selectedFilter;
  }
  $("#module-grid").innerHTML = Object.entries(state.modules)
    .map(
      ([key, item]) => `
        <button class="module-card" data-module="${key}" style="--accent:${item.accent}">
          <span>${item.label}</span>
          <strong>${summaryFor(key)?.total || 0}</strong>
        </button>
      `,
    )
    .join("");
  document.querySelectorAll(".module-card").forEach((card) => {
    card.addEventListener("click", () => {
      $("#module-filter").value = card.dataset.module;
      refreshRecords();
    });
  });
}

function summaryFor(module) {
  return state.dashboard?.summary.find((item) => item.module === module);
}

function renderDashboard() {
  $("#life-score").textContent = state.dashboard.life_score;
  $("#insights").innerHTML = state.dashboard.insights
    .map((insight) => `<li>${escapeHtml(insight)}</li>`)
    .join("");
  $("#summary").innerHTML = state.dashboard.summary
    .map(
      (item) => `
        <div class="summary-item">
          <span>${item.label}</span>
          <strong>${item.score}</strong>
          <small>${item.total} 条</small>
        </div>
      `,
    )
    .join("");
  $("#due-reminders").innerHTML = state.dashboard.reminders_due.length
    ? state.dashboard.reminders_due
        .map((item) => `<li>${escapeHtml(item.title)} <small>${item.due_at}</small></li>`)
        .join("")
    : "<li>暂无到期提醒</li>";
  renderForecast();
}

function renderForecast() {
  const predictions = Object.entries(state.forecast?.predictions || {});
  $("#forecast").innerHTML = predictions.length
    ? predictions
        .map(([module, item]) => {
          const meta = state.modules[module] || { label: module };
          return `
            <div class="forecast-item">
              <span>${meta.label}</span>
              <strong>${item.next_week_score}</strong>
              <small>${item.trend} / 置信度 ${item.confidence}</small>
            </div>
          `;
        })
        .join("")
    : "<p class='muted'>暂无足够数据生成预测。</p>";
}

function renderDetailFields() {
  const module = $("#record-module").value || "expense";
  $("#detail-fields").innerHTML = (moduleFields[module] || [])
    .map(
      ([name, label, type]) => `
        <label>
          ${label}
          <input name="${name}" type="${type}" ${type === "number" ? "step='0.01'" : ""}>
        </label>
      `,
    )
    .join("");
}

async function submitRecord(event) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const module = form.get("module");
  const payload = {
    module,
    title: form.get("title"),
    occurred_on: form.get("occurred_on"),
    status: form.get("status"),
    tags: form.get("tags"),
    details: {},
  };
  for (const [name, value] of form.entries()) {
    if (!["module", "title", "occurred_on", "status", "tags"].includes(name) && value !== "") {
      payload.details[name] = numberIfPossible(value);
    }
  }
  await api("/api/records", { method: "POST", body: JSON.stringify(payload) });
  event.currentTarget.reset();
  renderDetailFields();
  await refreshAll();
}

async function submitQuickEntry(event) {
  event.preventDefault();
  const text = $("#quick-text").value.trim();
  if (!text) return;
  await api("/api/quick-entry", { method: "POST", body: JSON.stringify({ text }) });
  $("#quick-text").value = "";
  await refreshAll();
}

async function submitReminder(event) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  await api("/api/reminders", {
    method: "POST",
    body: JSON.stringify({
      title: form.get("title"),
      due_at: form.get("due_at"),
      channel: form.get("channel"),
      message: form.get("message"),
    }),
  });
  event.currentTarget.reset();
  await refreshAll();
}

async function completeReminder(id) {
  await api(`/api/reminders/${id}`, { method: "PUT", body: JSON.stringify({ is_done: true }) });
  await refreshAll();
}

async function refreshRecords() {
  const module = $("#module-filter").value;
  const query = module ? `?module=${encodeURIComponent(module)}&limit=80` : "?limit=80";
  const data = await api(`/api/records${query}`);
  state.records = data.records;
  renderRecords();
}

function renderRecords() {
  $("#records").innerHTML = state.records.length
    ? state.records
        .map((record) => {
          const module = state.modules[record.module] || { label: record.module, accent: "#64748b" };
          return `
            <article class="record-card" style="--accent:${module.accent}">
              <div>
                <span class="pill">${module.label}</span>
                <strong>${escapeHtml(record.title)}</strong>
                <small>${record.occurred_on} / ${record.status} / ${record.score}</small>
              </div>
              <pre>${escapeHtml(JSON.stringify(record.details, null, 2))}</pre>
            </article>
          `;
        })
        .join("")
    : "<p class='muted'>暂无记录。</p>";
}

function renderReminders() {
  const reminders = state.dashboard.reminders_due;
  $("#due-reminders").innerHTML = reminders.length
    ? reminders
        .map(
          (item) => `
            <article class="reminder-card">
              <div>
                <strong>${escapeHtml(item.title)}</strong>
                <small>${escapeHtml(item.due_at)} / ${escapeHtml(item.channel)}</small>
                <p>${escapeHtml(item.message || "无备注")}</p>
              </div>
              <button class="secondary" type="button" data-reminder="${item.id}">完成</button>
            </article>
          `,
        )
        .join("")
    : "<p class='muted'>暂无到期提醒。</p>";
  document.querySelectorAll("[data-reminder]").forEach((button) => {
    button.addEventListener("click", () => completeReminder(button.dataset.reminder));
  });
}

async function exportData() {
  const data = await api("/api/export");
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `life-os-export-${new Date().toISOString().slice(0, 10)}.json`;
  link.click();
  URL.revokeObjectURL(url);
}

function numberIfPossible(value) {
  if (value === "") return value;
  const numeric = Number(value);
  return Number.isFinite(numeric) && String(value).match(/^\d+(\.\d+)?$/) ? numeric : value;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

bootstrap().catch((error) => {
  console.error(error);
  alert(error.message);
});
