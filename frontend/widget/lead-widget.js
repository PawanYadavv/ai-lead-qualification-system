(function () {
  var config = window.AILeadWidgetConfig || {};
  var defaultApiBase = "https://ai-lead-qualification-system-production.up.railway.app/api/v1";
  if (window.location && window.location.origin && window.location.origin.indexOf("http") === 0) {
    defaultApiBase = window.location.origin.replace(/\/+$/, "") + "/api/v1";
  }
  var apiBase = config.apiBaseUrl || defaultApiBase;
  var tenantToken = config.tenantToken;

  if (!tenantToken) {
    console.error("AILeadWidget: tenantToken is required in window.AILeadWidgetConfig");
    return;
  }

  var sessionId = null;
  var isOpen = false;

  var style = document.createElement("style");
  style.innerHTML = "\n    .ai-lead-widget-btn {\n      position: fixed;\n      right: 20px;\n      bottom: 20px;\n      width: 60px;\n      height: 60px;\n      border-radius: 50%;\n      border: none;\n      background: linear-gradient(135deg, #0f766e, #155e75);\n      color: #fff;\n      font-size: 24px;\n      cursor: pointer;\n      box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2);\n      z-index: 9999;\n    }\n\n    .ai-lead-widget-panel {\n      position: fixed;\n      right: 20px;\n      bottom: 90px;\n      width: 340px;\n      max-width: calc(100vw - 24px);\n      height: 480px;\n      background: #ffffff;\n      border-radius: 16px;\n      border: 1px solid #d1d5db;\n      box-shadow: 0 18px 45px rgba(15, 23, 42, 0.2);\n      display: none;\n      flex-direction: column;\n      overflow: hidden;\n      z-index: 9999;\n      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;\n    }\n\n    .ai-lead-widget-header {\n      background: #0f172a;\n      color: #f8fafc;\n      padding: 12px 14px;\n      font-weight: 600;\n      font-size: 14px;\n    }\n\n    .ai-lead-widget-messages {\n      flex: 1;\n      overflow-y: auto;\n      padding: 12px;\n      background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);\n    }\n\n    .ai-lead-msg {\n      margin-bottom: 10px;\n      padding: 10px 12px;\n      border-radius: 12px;\n      font-size: 14px;\n      line-height: 1.45;\n      max-width: 85%;\n      white-space: pre-wrap;\n      word-wrap: break-word;\n    }\n\n    .ai-lead-msg-user {\n      margin-left: auto;\n      background: #0f766e;\n      color: #f0fdfa;\n    }\n\n    .ai-lead-msg-assistant {\n      background: #ffffff;\n      color: #0f172a;\n      border: 1px solid #e2e8f0;\n    }\n\n    .ai-lead-widget-input {\n      display: flex;\n      padding: 10px;\n      gap: 8px;\n      border-top: 1px solid #e2e8f0;\n      background: #ffffff;\n    }\n\n    .ai-lead-widget-input textarea {\n      flex: 1;\n      min-height: 40px;\n      max-height: 90px;\n      resize: vertical;\n      border: 1px solid #cbd5e1;\n      border-radius: 10px;\n      padding: 8px 10px;\n      font-size: 14px;\n      font-family: inherit;\n    }\n\n    .ai-lead-widget-send {\n      border: none;\n      border-radius: 10px;\n      padding: 0 14px;\n      background: #0f172a;\n      color: #ffffff;\n      font-weight: 600;\n      cursor: pointer;\n    }\n\n    @media (max-width: 520px) {\n      .ai-lead-widget-panel {\n        right: 12px;\n        left: 12px;\n        width: auto;\n        bottom: 82px;\n        height: 62vh;\n      }\n\n      .ai-lead-widget-btn {\n        right: 12px;\n        bottom: 12px;\n      }\n    }\n  ";
  document.head.appendChild(style);

  var button = document.createElement("button");
  button.className = "ai-lead-widget-btn";
  button.innerText = "?";
  document.body.appendChild(button);

  var panel = document.createElement("div");
  panel.className = "ai-lead-widget-panel";
  panel.innerHTML = "\n    <div class='ai-lead-widget-header'>Sales Assistant</div>\n    <div class='ai-lead-widget-messages' id='ai-lead-messages'></div>\n    <div class='ai-lead-widget-input'>\n      <textarea id='ai-lead-input' placeholder='Type your message...'></textarea>\n      <button class='ai-lead-widget-send' id='ai-lead-send'>Send</button>\n    </div>\n  ";
  document.body.appendChild(panel);

  var messagesEl = panel.querySelector("#ai-lead-messages");
  var inputEl = panel.querySelector("#ai-lead-input");
  var sendEl = panel.querySelector("#ai-lead-send");

  function addMessage(role, text) {
    var div = document.createElement("div");
    div.className = "ai-lead-msg " + (role === "user" ? "ai-lead-msg-user" : "ai-lead-msg-assistant");
    div.textContent = text;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  async function ensureSession() {
    if (sessionId) {
      return true;
    }

    try {
      var response = await fetch(apiBase + "/chatbot/session/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tenant_token: tenantToken,
        }),
      });

      if (!response.ok) {
        addMessage("assistant", "We are having trouble connecting right now. Please try again soon.");
        return false;
      }

      var data = await response.json();
      sessionId = data.session_id;
      addMessage("assistant", data.greeting_message);
      return true;
    } catch (err) {
      addMessage(
        "assistant",
        "Connection blocked. If you opened demo.html directly, run it via http://localhost:8080 and try again."
      );
      return false;
    }
  }

  async function sendMessage() {
    var text = inputEl.value.trim();
    if (!text) {
      return;
    }

    if (!sessionId) {
      var ready = await ensureSession();
      if (!ready) {
        return;
      }
    }

    inputEl.value = "";
    addMessage("user", text);

    try {
      var response = await fetch(apiBase + "/chatbot/session/" + sessionId + "/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tenant_token: tenantToken,
          message: text,
        }),
      });

      if (!response.ok) {
        addMessage("assistant", "Sorry, I could not process that. Please try again.");
        return;
      }

      var data = await response.json();
      addMessage("assistant", data.reply || "Thanks for your message.");
    } catch (err) {
      addMessage("assistant", "Network issue detected. Please try again.");
    }
  }

  button.addEventListener("click", async function () {
    isOpen = !isOpen;
    panel.style.display = isOpen ? "flex" : "none";

    if (isOpen && !sessionId) {
      await ensureSession();
    }
  });

  sendEl.addEventListener("click", sendMessage);
  inputEl.addEventListener("keydown", function (event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  });
})();

