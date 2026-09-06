import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { MessageCircle, X, Send, Loader2, ArrowRight } from 'lucide-react'
import { LiquidGlassFAB } from './liquid-glass-fab.js'
import './ChatWidget.css'
import './liquid-glass-fab.css'

const EASE = [0.16, 1, 0.3, 1]
// Порт 8001: 8000 занят другими сервисами на обоих серверах.
// В production задаётся через VITE_API_URL на этапе сборки.
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001'

const translations = {
  en: {
    title: 'AI Consultant',
    subtitle: 'vnxORACLE Sales Team',
    placeholder: 'Ask about our AI employees...',
    send: 'Send',
    typing: 'Typing...',
    contactTitle: 'Leave your contact',
    contactSubtitle: 'Our consultant will reach out shortly',
    contactName: 'Your name',
    contactEmail: 'Email or Telegram',
    contactCompany: 'Company (optional)',
    contactSubmit: 'Send',
    contactSuccess: 'Thank you! We will contact you soon.',
    errorTitle: 'Connection Error',
    errorMessage: 'Unable to reach the server. Please try again later.',
    handoffText: 'I have enough to prepare a configuration for your digital employee.',
    handoffCta: 'Open the filled form',
    initialMessage: 'Hello! I can help you choose the right AI employee for your business. What tasks do you want to automate?'
  },
  ru: {
    title: 'AI Консультант',
    subtitle: 'Отдел продаж vnxORACLE',
    placeholder: 'Спросите про AI-сотрудников...',
    send: 'Отправить',
    typing: 'Печатает...',
    contactTitle: 'Оставьте контакт',
    contactSubtitle: 'Наш консультант свяжется в ближайшее время',
    contactName: 'Ваше имя',
    contactEmail: 'Email или Telegram',
    contactCompany: 'Компания (опционально)',
    contactSubmit: 'Отправить',
    contactSuccess: 'Спасибо! Мы свяжемся с вами в ближайшее время.',
    errorTitle: 'Ошибка соединения',
    errorMessage: 'Не удалось связаться с сервером. Попробуйте позже.',
    handoffText: 'Мне достаточно данных, чтобы подготовить конфигурацию цифрового сотрудника.',
    handoffCta: 'Открыть заполненную форму',
    initialMessage: 'Здравствуйте! Я помогу подобрать AI-сотрудника для вашего бизнеса. Какие задачи хотите автоматизировать?'
  }
}

export default function ChatWidget({ lang = 'ru', theme = 'dark', onHandoff, openSignal = 0 }) {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [sessionId, setSessionId] = useState(null)
  const [isTyping, setIsTyping] = useState(false)
  const [needsContact, setNeedsContact] = useState(false)
  const [showContactForm, setShowContactForm] = useState(false)
  const [contactSubmitted, setContactSubmitted] = useState(false)
  const [error, setError] = useState(null)

  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const fabContainerRef = useRef(null)
  const fabInstanceRef = useRef(null)

  const t = translations[lang]

  // Initialize liquid glass FAB
  useEffect(() => {
    if (fabContainerRef.current && !fabInstanceRef.current) {
      fabInstanceRef.current = new LiquidGlassFAB(
        fabContainerRef.current,
        () => setIsOpen(prev => !prev)
      )
    }

    return () => {
      if (fabInstanceRef.current) {
        fabInstanceRef.current.destroy()
        fabInstanceRef.current = null
      }
    }
  }, [])

  // Sync open state to FAB
  useEffect(() => {
    fabInstanceRef.current?.setState(isOpen)
  }, [isOpen])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  // Focus input when opened
  useEffect(() => {
    if (isOpen && !showContactForm) {
      inputRef.current?.focus()
    }
  }, [isOpen, showContactForm])

  // Внешний триггер открытия (кнопка «Тестовый диалог» в конфигураторе).
  useEffect(() => {
    if (openSignal > 0) setIsOpen(true)
  }, [openSignal])

  // Load messages from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('vnx-chat-messages')
    const savedSessionId = localStorage.getItem('vnx-chat-session')
    if (saved) {
      setMessages(JSON.parse(saved))
    } else {
      // Initial AI message
      setMessages([{
        role: 'assistant',
        content: t.initialMessage,
        timestamp: Date.now()
      }])
    }
    if (savedSessionId) {
      setSessionId(savedSessionId)
    }
  }, [])

  // Save messages to localStorage
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem('vnx-chat-messages', JSON.stringify(messages))
    }
  }, [messages])

  const sendMessage = async (content) => {
    if (!content.trim()) return

    const userMessage = {
      role: 'user',
      content: content.trim(),
      timestamp: Date.now()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsTyping(true)
    setError(null)

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: content.trim(),
          session_id: sessionId,
          user_data: null
        })
      })

      if (!response.ok) {
        throw new Error('API request failed')
      }

      const data = await response.json()

      const assistantMessage = {
        role: 'assistant',
        content: data.response,
        timestamp: Date.now()
      }

      setMessages(prev => [...prev, assistantMessage])
      setSessionId(data.session_id)
      localStorage.setItem('vnx-chat-session', data.session_id)

      if (data.needs_contact && !contactSubmitted) {
        setNeedsContact(true)
        setShowContactForm(true)
      }    } catch (err) {
      console.error('Chat error:', err)
      setError(err.message)
    } finally {
      setIsTyping(false)
    }
  }

  const submitContact = async (e) => {
    e.preventDefault()
    const formData = new FormData(e.target)
    const name = formData.get('name')
    const contact = formData.get('contact')
    const company = formData.get('company')

    try {
      const response = await fetch(`${API_URL}/api/lead/capture`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          contact,
          company,
          problem: '',
          messages: messages.filter(m => m.role === 'user').map(m => m.content),
          session_id: sessionId
        })
      })

      if (response.ok) {
        setContactSubmitted(true)
        setShowContactForm(false)
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: t.contactSuccess,
          timestamp: Date.now()
        }])
      }
    } catch (err) {
      console.error('Lead capture error:', err)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(inputValue)
    }
  }

  return (
    <div className="chat-widget">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="chat-window"
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.3, ease: EASE }}
          >
            {/* Header */}
            <div className="chat-header">
              <div className="chat-header-content">
                <div className="chat-avatar">
                  <MessageCircle size={20} strokeWidth={2} />
                </div>
                <div className="chat-title-wrapper">
                  <h3 className="chat-title">{t.title}</h3>
                  <p className="chat-subtitle">{t.subtitle}</p>
                </div>
              </div>
              <button
                className="chat-close"
                onClick={() => setIsOpen(false)}
                type="button"
                aria-label="Close chat"
              >
                <X size={18} strokeWidth={2} />
              </button>
            </div>

            {/* Messages */}
            <div className="chat-messages">
              {messages.map((msg, idx) => (
                <motion.div
                  key={idx}
                  className={`message message-${msg.role}`}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, ease: EASE }}
                >
                  <div className="message-content">{msg.content}</div>
                </motion.div>
              ))}

              {isTyping && (
                <motion.div
                  className="message message-assistant"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <div className="message-content typing-indicator">
                    <Loader2 size={14} className="spinner" />
                    <span>{t.typing}</span>
                  </div>
                </motion.div>
              )}

              {error && (
                <motion.div
                  className="message message-error"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <div className="message-content">
                    <strong>{t.errorTitle}</strong>
                    <br />
                    {t.errorMessage}
                  </div>
                </motion.div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Handoff to the full configurator */}
            {needsContact && !contactSubmitted && onHandoff && (
              <motion.div
                className="chat-handoff"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, ease: EASE }}
              >
                <p className="chat-handoff-text">{t.handoffText}</p>
                <button
                  className="chat-handoff-btn"
                  type="button"
                  onClick={() => {
                    onHandoff(messages.filter((m) => m.role === 'user').map((m) => m.content))
                    setIsOpen(false)
                  }}
                >
                  {t.handoffCta}
                  <ArrowRight size={15} strokeWidth={2} />
                </button>
              </motion.div>
            )}

            {/* Contact Form */}
            {showContactForm && !contactSubmitted && (
              <motion.div
                className="contact-form-wrapper"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, ease: EASE }}
              >
                <div className="contact-form-header">
                  <h4>{t.contactTitle}</h4>
                  <p>{t.contactSubtitle}</p>
                </div>
                <form className="contact-form" onSubmit={submitContact}>
                  <input
                    type="text"
                    name="name"
                    placeholder={t.contactName}
                    required
                    className="contact-input"
                  />
                  <input
                    type="text"
                    name="contact"
                    placeholder={t.contactEmail}
                    required
                    className="contact-input"
                  />
                  <input
                    type="text"
                    name="company"
                    placeholder={t.contactCompany}
                    className="contact-input"
                  />
                  <button type="submit" className="contact-submit">
                    {t.contactSubmit}
                  </button>
                </form>
              </motion.div>
            )}

            {/* Input */}
            {!showContactForm && (
              <div className="chat-input-wrapper">
                <input
                  ref={inputRef}
                  type="text"
                  className="chat-input"
                  placeholder={t.placeholder}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                />
                <button
                  className="chat-send"
                  onClick={() => sendMessage(inputValue)}
                  type="button"
                  disabled={!inputValue.trim() || isTyping}
                  aria-label={t.send}
                >
                  <Send size={18} strokeWidth={2} />
                </button>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Liquid glass FAB container */}
      <div ref={fabContainerRef} className="chat-fab-container" />
    </div>
  )
}
