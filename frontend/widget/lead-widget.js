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

  // Customization options
  var primaryColor = config.primaryColor || "#0f766e";
  var headerText = config.headerText || "Sales Assistant";
  var position = config.position || "right";
  var welcomeMsg = config.welcomeMessage || "";
  var isLeft = position === "left";
  var posCSS = isLeft ? "left: 20px;" : "right: 20px;";
  var posMobile = isLeft ? "left: 12px;" : "right: 12px;";

  var sessionId = null;
  var isOpen = false;

  var style = document.createElement("style");
  style.innerHTML =
    ".ai-lead-widget-btn {" +
    "  position: fixed;" + posCSS +
    "  bottom: 20px; width: 60px; height: 60px; border-radius: 50%; border: none;" +
    "  background: " + primaryColor + ";" +
    "  color: #fff; font-size: 28px; cursor: pointer;" +
    "  box-shadow: 0 8px 24px rgba(0,0,0,0.18); z-index: 9999;" +
    "  display: flex; align-items: center; justify-content: center;" +
    "  transition: transform 0.2s, box-shadow 0.2s;" +
    "}" +
    ".ai-lead-widget-btn:hover { transform: scale(1.08); box-shadow: 0 12px 30px rgba(0,0,0,0.25); }" +
    ".ai-lead-widget-panel {" +
    "  position: fixed;" + posCSS +
    "  bottom: 90px; width: 370px; max-width: calc(100vw - 24px); height: 500px;" +
    "  background: #fff; border-radius: 16px; border: 1px solid #e2e8f0;" +
    "  box-shadow: 0 20px 50px rgba(15,23,42,0.18);" +
    "  display: none; flex-direction: column; overflow: hidden; z-index: 9999;" +
    "  font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;" +
    "}" +
    ".ai-lead-widget-header {" +
    "  background: " + primaryColor + ";" +
    "  color: #fff; padding: 14px 18px; font-weight: 600; font-size: 15px;" +
    "  display: flex; align-items: center; justify-content: space-between;" +
    "}" +
    ".ai-lead-widget-header-close {" +
    "  background: none; border: none; color: #fff; font-size: 20px; cursor: pointer; opacity: 0.8; padding: 0 4px;" +
    "}" +
    ".ai-lead-widget-header-close:hover { opacity: 1; }" +
    ".ai-lead-widget-messages {" +
    "  flex: 1; overflow-y: auto; padding: 14px;" +
    "  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);" +
    "}" +
    ".ai-lead-msg {" +
    "  margin-bottom: 10px; padding: 10px 14px; border-radius: 14px;" +
    "  font-size: 14px; line-height: 1.5; max-width: 85%;" +
    "  white-space: pre-wrap; word-wrap: break-word; animation: aiMsgIn 0.2s ease-out;" +
    "}" +
    "@keyframes aiMsgIn { from { opacity:0; transform:translateY(6px); } to { opacity:1; transform:translateY(0); } }" +
    ".ai-lead-msg-user {" +
    "  margin-left: auto; background: " + primaryColor + "; color: #fff;" +
    "}" +
    ".ai-lead-msg-assistant {" +
    "  background: #fff; color: #0f172a; border: 1px solid #e2e8f0;" +
    "}" +
    ".ai-lead-widget-input {" +
    "  display: flex; padding: 10px; gap: 8px; border-top: 1px solid #e2e8f0; background: #fff;" +
    "}" +
    ".ai-lead-widget-input textarea {" +
    "  flex: 1; min-height: 42px; max-height: 90px; resize: none;" +
    "  border: 1px solid #cbd5e1; border-radius: 10px; padding: 10px 12px;" +
    "  font-size: 14px; font-family: inherit; outline: none;" +
    "}" +
    ".ai-lead-widget-input textarea:focus { border-color: " + primaryColor + "; }" +
    ".ai-lead-widget-send {" +
    "  border: none; border-radius: 10px; padding: 0 16px;" +
    "  background: " + primaryColor + "; color: #fff; font-weight: 600;" +
    "  cursor: pointer; font-size: 14px; transition: opacity 0.15s;" +
    "}" +
    ".ai-lead-widget-send:hover { opacity: 0.9; }" +
    ".ai-lead-widget-send:disabled { opacity: 0.5; cursor: not-allowed; }" +
    ".ai-lead-typing { display: flex; gap: 4px; padding: 10px 14px; }" +
    ".ai-lead-typing span { width: 7px; height: 7px; background: #94a3b8; border-radius: 50%; animation: aiDot 1.4s infinite; }" +
    ".ai-lead-typing span:nth-child(2) { animation-delay: 0.2s; }" +
    ".ai-lead-typing span:nth-child(3) { animation-delay: 0.4s; }" +
    "@keyframes aiDot { 0%,60%,100% { transform: translateY(0); } 30% { transform: translateY(-6px); } }" +
    "@media (max-width: 520px) {" +
    "  .ai-lead-widget-panel { " + posMobile + " width: auto; bottom: 82px; height: 65vh; " + (isLeft ? "" : "right: 12px;") + " }" +
    "  .ai-lead-widget-btn { " + posMobile + " bottom: 12px; }" +
    "}";
  document.head.appendChild(style);

  var button = document.createElement("button");
  button.className = "ai-lead-widget-btn";
  button.innerHTML = "&#x1F4AC;";
  document.body.appendChild(button);

  var panel = document.createElement("div");
  panel.className = "ai-lead-widget-panel";
  panel.innerHTML =
    "<div class='ai-lead-widget-header'><span>" + headerText + "</span><button class='ai-lead-widget-header-close' id='ai-lead-close'>&times;</button></div>" +
    "<div class='ai-lead-widget-messages' id='ai-lead-messages'></div>" +
    "<div class='ai-lead-widget-input'>" +
    "  <textarea id='ai-lead-input' placeholder='Type your message...' rows='1'></textarea>" +
    "  <button class='ai-lead-widget-send' id='ai-lead-send'>Send</button>" +
    "</div>";
  document.body.appendChild(panel);

  var messagesEl = panel.querySelector("#ai-lead-messages");
  var inputEl = panel.querySelector("#ai-lead-input");
  var sendEl = panel.querySelector("#ai-lead-send");
  var closeEl = panel.querySelector("#ai-lead-close");

  function addMessage(role, text) {
    var div = document.createElement("div");
    div.className = "ai-lead-msg " + (role === "user" ? "ai-lead-msg-user" : "ai-lead-msg-assistant");
    div.textContent = text;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function showTyping() {
    var el = document.createElement("div");
    el.className = "ai-lead-typing";
    el.id = "ai-lead-typing";
    el.innerHTML = "<span></span><span></span><span></span>";
    messagesEl.appendChild(el);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function hideTyping() {
    var el = document.getElementById("ai-lead-typing");
    if (el) el.remove();
  }

  async function ensureSession() {
    if (sessionId) {
      return true;
    }

    try {
      showTyping();
      var response = await fetch(apiBase + "/chatbot/session/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tenant_token: tenantToken,
        }),
      });
      hideTyping();

      if (!response.ok) {
        addMessage("assistant", "We are having trouble connecting right now. Please try again soon.");
        return false;
      }

      var data = await response.json();
      sessionId = data.session_id;
      addMessage("assistant", welcomeMsg || data.greeting_message);
      return true;
    } catch (err) {
      hideTyping();
      addMessage("assistant", "Unable to connect. Please check your internet and try again.");
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
    sendEl.disabled = true;
    addMessage("user", text);
    showTyping();

    try {
      var response = await fetch(apiBase + "/chatbot/session/" + sessionId + "/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tenant_token: tenantToken,
          message: text,
        }),
      });
      hideTyping();

      if (!response.ok) {
        addMessage("assistant", "Sorry, I could not process that. Please try again.");
        return;
      }

      var data = await response.json();
      addMessage("assistant", data.reply || "Thanks for your message.");
    } catch (err) {
      hideTyping();
      addMessage("assistant", "Network issue detected. Please try again.");
    } finally {
      sendEl.disabled = false;
      inputEl.focus();
    }
  }

  function togglePanel() {
    isOpen = !isOpen;
    panel.style.display = isOpen ? "flex" : "none";
    button.innerHTML = isOpen ? "&#x2715;" : "&#x1F4AC;";
    if (isOpen && !sessionId) ensureSession();
    if (isOpen) inputEl.focus();
  }

  button.addEventListener("click", togglePanel);
  closeEl.addEventListener("click", togglePanel);
  sendEl.addEventListener("click", sendMessage);
  inputEl.addEventListener("keydown", function (event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  });
})();

