/**
 * result.js – WanderAI Result Page
 * - Renders markdown itinerary
 * - Powers the chat interface
 * - Copy-to-clipboard
 */
(function () {
  "use strict";

  /* ── Render Itinerary Markdown ──────────────────────────────── */
  const rawEl    = document.getElementById("rawItinerary");
  const renderEl = document.getElementById("itineraryRendered");

  if (rawEl && renderEl && typeof marked !== "undefined") {
    try {
      const raw = JSON.parse(rawEl.textContent);
      renderEl.innerHTML = marked.parse(raw);
    } catch (err) {
      renderEl.textContent = rawEl.textContent;
    }
  }

  /* ── Copy to Clipboard ──────────────────────────────────────── */
  const copyBtn = document.getElementById("copyBtn");
  if (copyBtn) {
    copyBtn.addEventListener("click", function () {
      const text = renderEl ? renderEl.innerText : "";
      navigator.clipboard.writeText(text).then(function () {
        copyBtn.innerHTML = '<i class="bi bi-check2 me-1"></i>Copied!';
        setTimeout(function () {
          copyBtn.innerHTML = '<i class="bi bi-clipboard me-1"></i>Copy';
        }, 2000);
      });
    });
  }

  /* ── Chat Interface ─────────────────────────────────────────── */
  const chatMessages  = document.getElementById("chatMessages");
  const chatInput     = document.getElementById("chatInput");
  const chatSend      = document.getElementById("chatSend");
  const suggestions   = document.querySelectorAll(".wai-suggestion-btn");

  function scrollToBottom() {
    if (chatMessages) {
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  }

  function appendMessage(role, content) {
    if (!chatMessages) return;
    const isUser = role === "user";
    const msg = document.createElement("div");
    msg.className = "wai-chat-msg" + (isUser ? " wai-chat-msg--user" : "");

    const avatar = document.createElement("div");
    avatar.className = "wai-chat-avatar";
    avatar.innerHTML = isUser
      ? '<i class="bi bi-person-fill"></i>'
      : '<i class="bi bi-robot"></i>';

    const bubble = document.createElement("div");
    bubble.className = "wai-chat-bubble";

    if (!isUser && typeof marked !== "undefined") {
      bubble.innerHTML = marked.parse(content);
    } else {
      bubble.textContent = content;
    }

    if (isUser) {
      msg.appendChild(bubble);
      msg.appendChild(avatar);
    } else {
      msg.appendChild(avatar);
      msg.appendChild(bubble);
    }

    chatMessages.appendChild(msg);
    scrollToBottom();
    return msg;
  }

  function showTyping() {
    if (!chatMessages) return null;
    const msg = document.createElement("div");
    msg.className = "wai-chat-msg";
    msg.id = "typingIndicator";
    msg.innerHTML = `
      <div class="wai-chat-avatar"><i class="bi bi-robot"></i></div>
      <div class="wai-chat-bubble wai-typing">
        <span></span><span></span><span></span>
      </div>`;
    chatMessages.appendChild(msg);
    scrollToBottom();
    return msg;
  }

  async function sendMessage(message) {
    if (!message.trim()) return;
    if (chatInput) chatInput.value = "";
    if (chatSend) chatSend.disabled = true;

    appendMessage("user", message);
    const typingEl = showTyping();

    try {
      const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message }),
      });
      const data = await res.json();

      if (typingEl) typingEl.remove();

      if (data.success) {
        appendMessage("assistant", data.response);
      } else {
        appendMessage("assistant", "Sorry, I encountered an error: " + (data.error || "Unknown error."));
      }
    } catch (err) {
      if (typingEl) typingEl.remove();
      appendMessage("assistant", "Network error. Please check your connection and try again.");
    } finally {
      if (chatSend) chatSend.disabled = false;
      if (chatInput) chatInput.focus();
    }
  }

  if (chatSend) {
    chatSend.addEventListener("click", function () {
      sendMessage(chatInput ? chatInput.value : "");
    });
  }

  if (chatInput) {
    chatInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage(chatInput.value);
      }
    });
  }

  suggestions.forEach(function (btn) {
    btn.addEventListener("click", function () {
      sendMessage(btn.textContent.trim());
    });
  });

  scrollToBottom();
})();
