/**
 * vnxORACLE Chat Widget — Vanilla JS
 * Встраиваемый виджет для любого сайта
 *
 * Использование:
 * <script src="https://api.vnxoracle.uk/chat-widget.js"></script>
 * <script>VnxOracleWidget.init({ apiUrl: 'https://api.vnxoracle.uk' });</script>
 */

(function() {
  'use strict';

  const VnxOracleWidget = {
    config: {
      apiUrl: 'http://localhost:8001',
      position: 'bottom-right', // bottom-right | bottom-left
      theme: 'auto', // auto | light | dark
      language: 'ru'
    },

    state: {
      isOpen: false,
      sessionId: null,
      messages: [],
      isTyping: false
    },

    // Инициализация виджета
    init(options = {}) {
      this.config = { ...this.config, ...options };

      // Загружаем session_id из localStorage
      const saved = localStorage.getItem('vnx_chat_session');
      if (saved) {
        try {
          const data = JSON.parse(saved);
          this.state.sessionId = data.session_id;
          this.state.messages = data.messages || [];
        } catch (e) {
          console.warn('Failed to restore chat session:', e);
        }
      }

      // Определяем тему (auto = следуем за системной)
      if (this.config.theme === 'auto') {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        this.config.theme = prefersDark ? 'dark' : 'light';
      }

      this.injectCSS();
      this.createUI();
      this.attachEventListeners();
    },

    // Внедряем CSS в страницу
    injectCSS() {
      if (document.getElementById('vnx-widget-styles')) return;

      const css = `
        /* === vnxORACLE Chat Widget Styles === */

        :root {
          --vnx-primary: #2563eb;
          --vnx-primary-hover: #1d4ed8;
          --vnx-text: #1f2937;
          --vnx-text-secondary: #6b7280;
          --vnx-bg: #ffffff;
          --vnx-bg-secondary: #f9fafb;
          --vnx-border: #e5e7eb;
          --vnx-shadow: rgba(0, 0, 0, 0.1);
        }

        [data-theme="dark"] {
          --vnx-text: #f9fafb;
          --vnx-text-secondary: #d1d5db;
          --vnx-bg: #1f2937;
          --vnx-bg-secondary: #111827;
          --vnx-border: #374151;
          --vnx-shadow: rgba(0, 0, 0, 0.3);
        }

        #vnx-chat-widget {
          position: fixed;
          z-index: 99999;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        #vnx-chat-widget.position-bottom-right {
          bottom: 20px;
          right: 20px;
        }

        #vnx-chat-widget.position-bottom-left {
          bottom: 20px;
          left: 20px;
        }

        /* Floating button */
        #vnx-chat-button {
          width: 60px;
          height: 60px;
          border-radius: 50%;
          background: var(--vnx-primary);
          color: white;
          border: none;
          cursor: pointer;
          box-shadow: 0 4px 12px var(--vnx-shadow);
          display: flex;
          align-items: center;
          justify-content: center;
          transition: transform 0.2s, background 0.2s;
        }

        #vnx-chat-button:hover {
          background: var(--vnx-primary-hover);
          transform: scale(1.05);
        }

        #vnx-chat-button svg {
          width: 28px;
          height: 28px;
        }

        /* Chat window */
        #vnx-chat-window {
          position: absolute;
          bottom: 80px;
          width: 380px;
          height: 600px;
          max-height: calc(100vh - 120px);
          background: var(--vnx-bg);
          border-radius: 16px;
          box-shadow: 0 8px 32px var(--vnx-shadow);
          display: none;
          flex-direction: column;
          overflow: hidden;
        }

        #vnx-chat-window.open {
          display: flex;
        }

        /* Header */
        #vnx-chat-header {
          background: var(--vnx-primary);
          color: white;
          padding: 16px;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        #vnx-chat-header h3 {
          margin: 0;
          font-size: 16px;
          font-weight: 600;
        }

        #vnx-chat-close {
          background: transparent;
          border: none;
          color: white;
          cursor: pointer;
          padding: 4px;
          display: flex;
          align-items: center;
        }

        /* Messages */
        #vnx-chat-messages {
          flex: 1;
          overflow-y: auto;
          padding: 16px;
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .vnx-message {
          max-width: 80%;
          padding: 10px 14px;
          border-radius: 12px;
          line-height: 1.5;
          word-wrap: break-word;
        }

        .vnx-message.user {
          align-self: flex-end;
          background: var(--vnx-primary);
          color: white;
        }

        .vnx-message.assistant {
          align-self: flex-start;
          background: var(--vnx-bg-secondary);
          color: var(--vnx-text);
          border: 1px solid var(--vnx-border);
        }

        .vnx-message strong, .vnx-message b {
          font-weight: 600;
        }

        .vnx-message em, .vnx-message i {
          font-style: italic;
        }

        .vnx-message a {
          color: var(--vnx-primary);
          text-decoration: underline;
        }

        .vnx-message code {
          background: rgba(0,0,0,0.05);
          padding: 2px 4px;
          border-radius: 3px;
          font-family: monospace;
          font-size: 0.9em;
        }

        /* Typing indicator */
        .vnx-typing {
          display: flex;
          gap: 4px;
          padding: 10px 14px;
        }

        .vnx-typing span {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: var(--vnx-text-secondary);
          animation: vnx-bounce 1.4s infinite ease-in-out both;
        }

        .vnx-typing span:nth-child(1) { animation-delay: -0.32s; }
        .vnx-typing span:nth-child(2) { animation-delay: -0.16s; }

        @keyframes vnx-bounce {
          0%, 80%, 100% { transform: scale(0); }
          40% { transform: scale(1); }
        }

        /* Input */
        #vnx-chat-input-container {
          padding: 16px;
          border-top: 1px solid var(--vnx-border);
          display: flex;
          gap: 8px;
        }

        #vnx-chat-input {
          flex: 1;
          padding: 10px 14px;
          border: 1px solid var(--vnx-border);
          border-radius: 20px;
          font-size: 14px;
          outline: none;
          background: var(--vnx-bg);
          color: var(--vnx-text);
        }

        #vnx-chat-input:focus {
          border-color: var(--vnx-primary);
        }

        #vnx-chat-send {
          background: var(--vnx-primary);
          color: white;
          border: none;
          width: 40px;
          height: 40px;
          border-radius: 50%;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: background 0.2s;
        }

        #vnx-chat-send:hover:not(:disabled) {
          background: var(--vnx-primary-hover);
        }

        #vnx-chat-send:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        /* Mobile responsive */
        @media (max-width: 480px) {
          #vnx-chat-window {
            width: calc(100vw - 32px);
            height: calc(100vh - 100px);
            bottom: 70px;
          }
        }
      `;

      const style = document.createElement('style');
      style.id = 'vnx-widget-styles';
      style.textContent = css;
      document.head.appendChild(style);
    },
