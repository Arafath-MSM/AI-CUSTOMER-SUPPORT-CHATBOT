(function () {
  const currentScript = document.currentScript;
  const config = {
    apiBaseUrl:
      currentScript?.dataset.apiBaseUrl ||
      window.AICustomerSupportChatbot?.apiBaseUrl ||
      window.location.origin,
    companyId:
      currentScript?.dataset.companyId ||
      window.AICustomerSupportChatbot?.companyId ||
      "default",
    title:
      currentScript?.dataset.title ||
      window.AICustomerSupportChatbot?.title ||
      "Support",
    welcomeMessage:
      currentScript?.dataset.welcomeMessage ||
      window.AICustomerSupportChatbot?.welcomeMessage ||
      "Hi, how can I help you today?",
  };

  const existing = document.getElementById("ai-support-widget-root");
  if (existing) {
    return;
  }

  const root = document.createElement("div");
  root.id = "ai-support-widget-root";
  root.innerHTML = `
    <button class="ai-support-launcher" type="button" aria-label="Open support chat">
      <span class="ai-support-launcher-icon">?</span>
    </button>
    <section class="ai-support-panel" aria-label="Customer support chat" hidden>
      <header class="ai-support-header">
        <div>
          <strong>${escapeHtml(config.title)}</strong>
          <span>Online</span>
        </div>
        <button class="ai-support-close" type="button" aria-label="Close support chat">×</button>
      </header>
      <div class="ai-support-messages" role="log" aria-live="polite"></div>
      <form class="ai-support-form">
        <textarea class="ai-support-input" rows="1" placeholder="Ask a question..." aria-label="Message"></textarea>
        <button class="ai-support-send" type="submit" aria-label="Send message">Send</button>
      </form>
    </section>
  `;

  const style = document.createElement("style");
  style.textContent = `
    #ai-support-widget-root {
      --ai-support-bg: #ffffff;
      --ai-support-text: #172033;
      --ai-support-muted: #657085;
      --ai-support-border: #d8dee9;
      --ai-support-primary: #1463ff;
      --ai-support-primary-dark: #0c4fd1;
      --ai-support-bubble: #eef3ff;
      --ai-support-shadow: 0 18px 50px rgba(19, 32, 55, 0.18);
      color: var(--ai-support-text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      position: fixed;
      right: 20px;
      bottom: 20px;
      z-index: 2147483647;
    }

    #ai-support-widget-root * {
      box-sizing: border-box;
    }

    .ai-support-launcher {
      align-items: center;
      background: var(--ai-support-primary);
      border: 0;
      border-radius: 50%;
      box-shadow: var(--ai-support-shadow);
      color: #fff;
      cursor: pointer;
      display: flex;
      height: 56px;
      justify-content: center;
      width: 56px;
    }

    .ai-support-launcher:hover,
    .ai-support-send:hover {
      background: var(--ai-support-primary-dark);
    }

    .ai-support-launcher-icon {
      border: 2px solid currentColor;
      border-radius: 50%;
      display: inline-flex;
      font-size: 22px;
      font-weight: 800;
      height: 28px;
      justify-content: center;
      line-height: 24px;
      width: 28px;
    }

    .ai-support-panel {
      background: var(--ai-support-bg);
      border: 1px solid var(--ai-support-border);
      border-radius: 8px;
      bottom: 72px;
      box-shadow: var(--ai-support-shadow);
      display: flex;
      flex-direction: column;
      height: min(620px, calc(100vh - 108px));
      overflow: hidden;
      position: absolute;
      right: 0;
      width: min(380px, calc(100vw - 40px));
    }

    .ai-support-panel[hidden] {
      display: none;
    }

    .ai-support-header {
      align-items: center;
      background: #101828;
      color: #fff;
      display: flex;
      justify-content: space-between;
      min-height: 64px;
      padding: 14px 16px;
    }

    .ai-support-header strong,
    .ai-support-header span {
      display: block;
    }

    .ai-support-header strong {
      font-size: 15px;
    }

    .ai-support-header span {
      color: #b7c4d7;
      font-size: 12px;
      margin-top: 2px;
    }

    .ai-support-close {
      background: transparent;
      border: 0;
      color: #fff;
      cursor: pointer;
      font-size: 24px;
      height: 36px;
      line-height: 1;
      width: 36px;
    }

    .ai-support-messages {
      display: flex;
      flex: 1;
      flex-direction: column;
      gap: 10px;
      overflow-y: auto;
      padding: 14px;
    }

    .ai-support-message {
      border-radius: 8px;
      font-size: 14px;
      line-height: 1.45;
      max-width: 86%;
      padding: 10px 12px;
      white-space: pre-wrap;
      word-break: break-word;
    }

    .ai-support-message.bot {
      align-self: flex-start;
      background: var(--ai-support-bubble);
      color: var(--ai-support-text);
    }

    .ai-support-message.user {
      align-self: flex-end;
      background: var(--ai-support-primary);
      color: #fff;
    }

    .ai-support-sources {
      color: var(--ai-support-muted);
      font-size: 11px;
      margin-top: 8px;
    }

    .ai-support-form {
      border-top: 1px solid var(--ai-support-border);
      display: grid;
      gap: 8px;
      grid-template-columns: 1fr auto;
      padding: 10px;
    }

    .ai-support-input {
      border: 1px solid var(--ai-support-border);
      border-radius: 8px;
      color: var(--ai-support-text);
      font: inherit;
      max-height: 110px;
      min-height: 42px;
      outline: none;
      padding: 10px;
      resize: none;
      width: 100%;
    }

    .ai-support-input:focus {
      border-color: var(--ai-support-primary);
    }

    .ai-support-send {
      background: var(--ai-support-primary);
      border: 0;
      border-radius: 8px;
      color: #fff;
      cursor: pointer;
      font: inherit;
      font-weight: 700;
      min-height: 42px;
      padding: 0 14px;
    }

    .ai-support-send:disabled,
    .ai-support-input:disabled {
      cursor: wait;
      opacity: 0.65;
    }

    @media (max-width: 480px) {
      #ai-support-widget-root {
        bottom: 14px;
        right: 14px;
      }

      .ai-support-panel {
        bottom: 68px;
        height: calc(100vh - 96px);
        width: calc(100vw - 28px);
      }
    }
  `;

  document.head.appendChild(style);
  document.body.appendChild(root);

  const launcher = root.querySelector(".ai-support-launcher");
  const panel = root.querySelector(".ai-support-panel");
  const closeButton = root.querySelector(".ai-support-close");
  const messages = root.querySelector(".ai-support-messages");
  const form = root.querySelector(".ai-support-form");
  const input = root.querySelector(".ai-support-input");
  const sendButton = root.querySelector(".ai-support-send");

  addMessage("bot", config.welcomeMessage);

  launcher.addEventListener("click", () => {
    panel.hidden = !panel.hidden;
    if (!panel.hidden) {
      input.focus();
    }
  });

  closeButton.addEventListener("click", () => {
    panel.hidden = true;
  });

  input.addEventListener("input", () => {
    input.style.height = "auto";
    input.style.height = `${input.scrollHeight}px`;
  });

  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      form.requestSubmit();
    }
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const text = input.value.trim();
    if (!text) {
      return;
    }

    addMessage("user", text);
    input.value = "";
    input.style.height = "auto";
    setLoading(true);
    const loadingMessage = addMessage("bot", "Thinking...");

    try {
      const response = await fetch(`${config.apiBaseUrl.replace(/\/$/, "")}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          company_id: config.companyId,
          message: text,
        }),
      });

      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail || "The chat request failed.");
      }

      loadingMessage.remove();
      addMessage("bot", payload.answer, payload.sources || []);
    } catch (error) {
      loadingMessage.remove();
      addMessage("bot", "I could not reach support right now. Please try again.");
    } finally {
      setLoading(false);
      input.focus();
    }
  });

  function addMessage(role, text, sources) {
    const bubble = document.createElement("div");
    bubble.className = `ai-support-message ${role}`;
    bubble.textContent = text;

    if (sources && sources.length > 0) {
      const sourceSummary = document.createElement("div");
      sourceSummary.className = "ai-support-sources";
      sourceSummary.textContent = `Sources: ${sources
        .map((source) => `${source.title} #${source.chunk_index}`)
        .join(", ")}`;
      bubble.appendChild(sourceSummary);
    }

    messages.appendChild(bubble);
    messages.scrollTop = messages.scrollHeight;
    return bubble;
  }

  function setLoading(isLoading) {
    input.disabled = isLoading;
    sendButton.disabled = isLoading;
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
})();
