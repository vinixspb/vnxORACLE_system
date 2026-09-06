// ---------------------------------------------------------------
// Восстановление конфигурации цифрового сотрудника из транскрипта
// беседы с ИИ-консультантом. Работает эвристиками по тексту
// пользовательских реплик — сервер не обязан возвращать структуру.
// ---------------------------------------------------------------

const ROLE_MATCHERS = [
  ['поддержк', 'техпод', 'support', 'тикет', 'ticket', 'l1', 'l2'],
  ['продаж', 'sales', 'лид', 'lead', 'менеджер', 'manager'],
  ['hr', 'ассистент', 'assistant', 'офис', 'office', 'внутрен', 'internal']
]

const CHANNEL_MATCHERS = [
  ['telegram', 'телеграм', 'тг'],
  ['whatsapp', 'вотсап', 'ватсап', 'вацап'],
  ['vk', 'вконтакте'],
  ['сайт', 'site', 'website', 'виджет', 'widget', 'веб', 'web']
]
export const CHANNEL_VALUES = ['Telegram', 'WhatsApp', 'VK', 'Website widget']

const EMAIL_RE = /[\w.+-]+@[\w-]+\.[\w.]+/
const TELEGRAM_RE = /@[a-z0-9_]{4,}/i
const URL_RE = /((https?:\/\/)?[a-z0-9-]{2,}\.[a-z]{2,}(\/\S*)?)/i

function matchOption(text, matchers, values) {
  const lower = text.toLowerCase()
  for (let i = 0; i < matchers.length; i += 1) {
    if (matchers[i].some((token) => lower.includes(token))) return values[i]
  }
  return ''
}

// Свободный ответ на конкретный вопрос → патч полей формы.
export function parseAnswer(field, answer, roleOptions = []) {
  const text = answer.trim()
  if (!text) return {}

  switch (field) {
    case 'agentRoleField': {
      const matched = matchOption(text, ROLE_MATCHERS, roleOptions)
      return matched ? { agentRoleField: matched } : { tasks: text }
    }
    case 'channel': {
      const matched = matchOption(text, CHANNEL_MATCHERS, CHANNEL_VALUES)
      return matched ? { channel: matched } : {}
    }
    case 'about':
    case 'businessName': {
      const patch = { [field]: text }
      const url = text.match(URL_RE)
      if (url && !EMAIL_RE.test(url[0])) patch.website = url[0]
      return patch
    }
    case 'contactName': {
      const patch = {}
      const email = text.match(EMAIL_RE)
      const telegram = text.match(TELEGRAM_RE)
      if (email) patch.contactEmail = email[0]
      if (telegram) patch.contactTelegram = telegram[0]

      const name = text
        .replace(EMAIL_RE, '')
        .replace(TELEGRAM_RE, '')
        .replace(/[,;•·|]+/g, ' ')
        .trim()
      if (name) patch.contactName = name
      return patch
    }
    default:
      return { [field]: text }
  }
}

// Полный транскрипт → черновик конфигурации.
// Первая реплика обычно описывает бизнес, дальше по тексту ищем
// роль, канал и контакты в любом порядке.
export function deriveConfigFromMessages(userMessages, roleOptions = []) {
  const texts = userMessages.map((item) => String(item).trim()).filter(Boolean)
  if (!texts.length) return {}

  const joined = texts.join('\n')
  const patch = {}

  const role = matchOption(joined, ROLE_MATCHERS, roleOptions)
  if (role) patch.agentRoleField = role

  const channel = matchOption(joined, CHANNEL_MATCHERS, CHANNEL_VALUES)
  if (channel) patch.channel = channel

  const email = joined.match(EMAIL_RE)
  if (email) patch.contactEmail = email[0]

  const telegram = joined.match(TELEGRAM_RE)
  if (telegram) patch.contactTelegram = telegram[0]

  const url = joined.match(URL_RE)
  if (url && (!email || !email[0].includes(url[0]))) patch.website = url[0]

  // Самая длинная реплика — наиболее содержательное описание задач.
  const longest = texts.reduce((a, b) => (b.length > a.length ? b : a), '')
  if (longest.length > 40) patch.about = longest

  return patch
}
