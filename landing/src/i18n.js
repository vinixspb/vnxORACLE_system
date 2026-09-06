// ---------------------------------------------------------------
// Переводы интерфейса. Плоские ключи — легаси хиро-секции,
// вложенные объекты — новые блоки (directions, onboarding, chat).
// ---------------------------------------------------------------

export const LANGS = ['ru', 'en']

export const translations = {
  en: {
    brand: 'vnxORACLE',
    menu: 'Menu',
    tagAdvanced: 'Digital Workforce',
    tagCognitive: 'Cognitive AI',
    adaptiveSystems: 'B2B Solutions',
    subtitle: 'The Future of Corporate Hiring 2026',
    heading: ['Hire Intelligence.', 'Rent Results.'],
    btnFeatures: 'Who We Offer?',
    btnHowItWorks: 'How Rental Works',
    tag1: 'LLM Models',
    tag2: 'Deep Integration',
    tag3: '24/7 Automation',

    rolesHeading: 'Who are you hiring?',
    rolesDescription:
      "We don't sell chatbots. We rent ready-made specialists already trained to solve tasks in your niche.",
    role1Title: 'Technical Support Specialist (L1/L2)',
    role1Desc: 'Instantly closes 80% of tickets. Knows all documentation. Never gets tired.',
    role2Title: 'Sales Manager',
    role2Desc: 'Qualifies leads, consults on catalog, drives to payment.',
    role3Title: 'Internal Assistant (HR/Office)',
    role3Desc: 'Helps your live employees find regulations and onboard newcomers.',

    howHeading: 'Employee as a Service (EaaS)',
    howStep1Title: 'Interview',
    howStep1Desc:
      'You tell us what tasks the digital employee should handle and which databases to access.',
    howStep2Title: 'Training',
    howStep2Desc:
      'We deploy the vnxORACLE core, train the neural network on your specifics, and integrate into your processes.',
    howStep3Title: 'Going Live',
    howStep3Desc:
      'The employee starts working for a fixed subscription fee. No sick leave, taxes, or vacations.',

    trustHeading: 'Intelligence you can trust your business with.',
    trustPoint1Title: 'Isolated Memory',
    trustPoint1Desc: 'Your company data stays within your perimeter only.',
    trustPoint2Title: 'Controlled Logic',
    trustPoint2Desc: "The employee doesn't hallucinate and strictly follows the assigned Tone of Voice.",
    trustPoint3Title: 'Continuous Evolution',
    trustPoint3Desc: 'You get AI core updates automatically, with no hidden development fees.',

    directions: {
      heading: 'What we do',
      subheading: 'We build digital employees that take over routine business operations',
      learnMore: 'Learn more',
      items: [
        {
          id: 'messengers',
          icon: 'messages',
          title: 'Messenger employees',
          desc: 'Telegram, WhatsApp and VK agents that answer, qualify and hand off to your team.',
          bullets: ['Telegram / WhatsApp / VK', 'Media, voice and files', 'Live-operator escalation']
        },
        {
          id: 'ai-core',
          icon: 'brain',
          title: 'AI assistants on your data',
          desc: 'A trained core that knows your documentation, price list and internal rules.',
          bullets: ['Knowledge base on your docs', 'Isolated company memory', 'Controlled tone of voice']
        },
        {
          id: 'web',
          icon: 'globe',
          title: 'Website and CRM integration',
          desc: 'A chat widget plus deep integration with the systems your business already runs on.',
          bullets: ['Website chat widget', 'CRM and helpdesk sync', 'Analytics and dialogue reports']
        }
      ]
    },

    onboarding: {
      heading: 'Configuration Checklist',
      subheading: 'Set up your digital employee. The assistant fills this in for you as you talk.',
      agentRole: 'AI Employee',
      unnamed: 'New agent',
      save: 'Save draft',
      testCall: 'Test dialogue',
      activate: 'Request activation',
      saved: 'Draft saved locally',
      activateHint: 'We will contact you to confirm the launch.',
      prefilledBadge: 'Filled from the dialogue',
      trainingSource: {
        title: 'Training source',
        websiteLabel: 'Your business website',
        websiteHint: 'The AI employee will use your website data to answer customer questions.',
        websitePlaceholder: 'https://your-company.com',
        noWebsite: "I don't have a website",
        channelLabel: 'Primary channel',
        channelHint: 'Where the digital employee should work.',
        reinit: 'Re-initialize agent',
        skip: 'Skip'
      },
      steps: [
        {
          id: 'business',
          title: 'My business',
          fields: [
            { id: 'businessName', label: 'Business name', type: 'text', placeholder: 'Acme Ltd' },
            { id: 'address', label: 'Address', type: 'text', placeholder: 'City, country' },
            { id: 'phone', label: 'Public phone number', type: 'tel', placeholder: '+357 00 000000' },
            {
              id: 'about',
              label: 'About your business',
              type: 'textarea',
              placeholder: 'What you do, for whom, and what makes you different.'
            }
          ]
        },
        {
          id: 'employee',
          title: 'Digital employee',
          fields: [
            { id: 'agentName', label: 'Employee name', type: 'text', placeholder: 'Aylin' },
            {
              id: 'agentRoleField',
              label: 'Role',
              type: 'select',
              options: ['Technical support (L1/L2)', 'Sales manager', 'Internal assistant (HR/Office)']
            },
            {
              id: 'tone',
              label: 'Tone of voice',
              type: 'select',
              options: ['Professional', 'Friendly', 'Concise', 'Formal']
            },
            {
              id: 'tasks',
              label: 'Tasks to take over',
              type: 'textarea',
              placeholder: 'Which questions and requests should be closed without a human?'
            }
          ]
        },
        {
          id: 'contact',
          title: 'Contact for launch',
          fields: [
            { id: 'contactName', label: 'Your name', type: 'text', placeholder: 'Name' },
            { id: 'contactEmail', label: 'Email', type: 'email', placeholder: 'you@company.com' },
            { id: 'contactTelegram', label: 'Telegram', type: 'text', placeholder: '@username' }
          ]
        }
      ]
    },

    chat: {
      title: 'Connection assistant',
      subtitle: 'Answer a few questions — I will prepare the configuration',
      open: 'Talk to the assistant',
      close: 'Close',
      placeholder: 'Type your answer…',
      send: 'Send',
      restart: 'Start over',
      toForm: 'Open the filled form',
      done: 'I collected enough. Open the form — the fields are already filled in.',
      greeting: "Hi! I'm the vnxORACLE assistant. I'll ask a few questions and prepare a ready configuration for your digital employee.",
      questions: [
        { field: 'businessName', text: 'What is your company called?' },
        { field: 'about', text: 'What does your business do? A couple of sentences is enough.' },
        { field: 'agentRoleField', text: 'Which employee do you need: technical support, sales, or an internal assistant?' },
        { field: 'channel', text: 'Which channel comes first: Telegram, WhatsApp, or the website?' },
        { field: 'tasks', text: 'Which requests should the employee close without a human?' },
        { field: 'contactName', text: 'How should I address you, and how do we reach you (email or Telegram)?' }
      ]
    }
  },
  ru: {
    brand: 'vnxORACLE',
    menu: 'Меню',
    tagAdvanced: 'Цифровой Штат',
    tagCognitive: 'Когнитивный ИИ',
    adaptiveSystems: 'B2B Решения',
    subtitle: 'Будущее корпоративного найма 2026',
    heading: ['Нанимайте Интеллект.', 'Арендуйте Результат.'],
    btnFeatures: 'Кого мы предлагаем?',
    btnHowItWorks: 'Как работает аренда',
    tag1: 'LLM-Модели',
    tag2: 'Глубокая Интеграция',
    tag3: 'Автоматизация 24/7',

    rolesHeading: 'Кого вы берете в команду?',
    rolesDescription:
      'Мы не продаем чат-ботов. Мы сдаем в аренду готовых специалистов, которые уже обучены решать задачи вашей ниши.',
    role1Title: 'Специалист Техподдержки (L1/L2)',
    role1Desc: 'Мгновенно закрывает 80% тикетов. Знает всю документацию. Не устает.',
    role2Title: 'Менеджер по Продажам',
    role2Desc: 'Квалифицирует лидов, консультирует по каталогу, доводит до оплаты.',
    role3Title: 'Внутренний Ассистент (HR/Офис)',
    role3Desc: 'Помогает вашим живым сотрудникам находить регламенты и онбордить новичков.',

    howHeading: 'Сотрудник как Услуга (EaaS)',
    howStep1Title: 'Собеседование',
    howStep1Desc:
      'Вы рассказываете, какие задачи должен закрывать цифровой сотрудник и к каким базам данных иметь доступ.',
    howStep2Title: 'Стажировка',
    howStep2Desc:
      'Мы разворачиваем ядро на базе vnxORACLE, обучаем нейросеть вашей специфике и интегрируем в ваши процессы.',
    howStep3Title: 'Выход на работу',
    howStep3Desc:
      'Сотрудник начинает работу за фиксированную абонентскую плату. Никаких больничных, налогов и отпусков.',

    trustHeading: 'Разум, которому можно доверить бизнес.',
    trustPoint1Title: 'Изолированная память',
    trustPoint1Desc: 'Данные вашей компании остаются только внутри вашего контура.',
    trustPoint2Title: 'Управляемая логика',
    trustPoint2Desc: 'Сотрудник не галлюцинирует и строго следует заданному Tone of Voice.',
    trustPoint3Title: 'Непрерывная эволюция',
    trustPoint3Desc:
      'Вы получаете апдейты AI-ядра автоматически, без скрытых платежей за разработку.',

    directions: {
      heading: 'Чем мы занимаемся',
      subheading: 'Мы собираем цифровых сотрудников, которые забирают рутину бизнеса на себя',
      learnMore: 'Подробнее',
      items: [
        {
          id: 'messengers',
          icon: 'messages',
          title: 'Сотрудники в мессенджерах',
          desc: 'Агенты в Telegram, WhatsApp и VK: отвечают, квалифицируют и передают диалог команде.',
          bullets: ['Telegram / WhatsApp / VK', 'Медиа, голос и файлы', 'Эскалация на живого оператора']
        },
        {
          id: 'ai-core',
          icon: 'brain',
          title: 'ИИ-ассистенты на ваших данных',
          desc: 'Обученное ядро, которое знает вашу документацию, прайс и внутренние регламенты.',
          bullets: ['База знаний по вашим документам', 'Изолированная память компании', 'Управляемый tone of voice']
        },
        {
          id: 'web',
          icon: 'globe',
          title: 'Интеграция с сайтом и CRM',
          desc: 'Чат-виджет плюс глубокая интеграция с системами, в которых уже работает бизнес.',
          bullets: ['Чат-виджет на сайт', 'Связка с CRM и хелпдеском', 'Аналитика и отчёты по диалогам']
        }
      ]
    },

    onboarding: {
      heading: 'Чек-лист конфигурации',
      subheading: 'Настройте цифрового сотрудника. Ассистент заполняет форму за вас в ходе беседы.',
      agentRole: 'ИИ-сотрудник',
      unnamed: 'Новый агент',
      save: 'Сохранить черновик',
      testCall: 'Тестовый диалог',
      activate: 'Запросить активацию',
      saved: 'Черновик сохранён локально',
      activateHint: 'Мы свяжемся с вами, чтобы подтвердить запуск.',
      prefilledBadge: 'Заполнено из диалога',
      trainingSource: {
        title: 'Источник обучения',
        websiteLabel: 'Сайт вашего бизнеса',
        websiteHint: 'ИИ-сотрудник будет использовать данные сайта, чтобы отвечать на вопросы клиентов.',
        websitePlaceholder: 'https://ваша-компания.com',
        noWebsite: 'У меня нет сайта',
        channelLabel: 'Основной канал',
        channelHint: 'Где должен работать цифровой сотрудник.',
        reinit: 'Переинициализировать агента',
        skip: 'Пропустить'
      },
      steps: [
        {
          id: 'business',
          title: 'Мой бизнес',
          fields: [
            { id: 'businessName', label: 'Название компании', type: 'text', placeholder: 'ООО «Ромашка»' },
            { id: 'address', label: 'Адрес', type: 'text', placeholder: 'Город, страна' },
            { id: 'phone', label: 'Публичный телефон', type: 'tel', placeholder: '+357 00 000000' },
            {
              id: 'about',
              label: 'О вашем бизнесе',
              type: 'textarea',
              placeholder: 'Чем занимаетесь, для кого работаете и чем отличаетесь.'
            }
          ]
        },
        {
          id: 'employee',
          title: 'Цифровой сотрудник',
          fields: [
            { id: 'agentName', label: 'Имя сотрудника', type: 'text', placeholder: 'Айлин' },
            {
              id: 'agentRoleField',
              label: 'Роль',
              type: 'select',
              options: ['Техподдержка (L1/L2)', 'Менеджер по продажам', 'Внутренний ассистент (HR/Офис)']
            },
            {
              id: 'tone',
              label: 'Tone of voice',
              type: 'select',
              options: ['Профессиональный', 'Дружелюбный', 'Лаконичный', 'Формальный']
            },
            {
              id: 'tasks',
              label: 'Какие задачи забрать',
              type: 'textarea',
              placeholder: 'Какие вопросы и заявки должны закрываться без человека?'
            }
          ]
        },
        {
          id: 'contact',
          title: 'Контакт для запуска',
          fields: [
            { id: 'contactName', label: 'Ваше имя', type: 'text', placeholder: 'Имя' },
            { id: 'contactEmail', label: 'Email', type: 'email', placeholder: 'you@company.com' },
            { id: 'contactTelegram', label: 'Telegram', type: 'text', placeholder: '@username' }
          ]
        }
      ]
    },

    chat: {
      title: 'Ассистент подключения',
      subtitle: 'Ответьте на несколько вопросов — я подготовлю конфигурацию',
      open: 'Поговорить с ассистентом',
      close: 'Закрыть',
      placeholder: 'Напишите ответ…',
      send: 'Отправить',
      restart: 'Начать заново',
      toForm: 'Открыть заполненную форму',
      done: 'Я собрал достаточно. Откройте форму — поля уже заполнены.',
      greeting: 'Привет! Я ассистент vnxORACLE. Задам несколько вопросов и подготовлю готовую конфигурацию цифрового сотрудника.',
      questions: [
        { field: 'businessName', text: 'Как называется ваша компания?' },
        { field: 'about', text: 'Чем занимается ваш бизнес? Достаточно пары предложений.' },
        { field: 'agentRoleField', text: 'Какой сотрудник нужен: техподдержка, продажи или внутренний ассистент?' },
        { field: 'channel', text: 'Какой канал в приоритете: Telegram, WhatsApp или сайт?' },
        { field: 'tasks', text: 'Какие обращения сотрудник должен закрывать без человека?' },
        { field: 'contactName', text: 'Как к вам обращаться и как с вами связаться (email или Telegram)?' }
      ]
    }
  }
}
