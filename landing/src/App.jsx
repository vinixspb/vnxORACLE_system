import { motion } from 'motion/react'
import { Plus } from 'lucide-react'
import { useState } from 'react'
import './App.css'

const EASE = [0.16, 1, 0.3, 1]

const VIDEO_URL =
  'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260508_215831_c6a8989c-d716-4d8d-8745-e972a2eec711.mp4'

const translations = {
  en: {
    brand: 'vnxORACLE',
    menu: 'Menu',
    tagAdvanced: 'Digital Workforce',
    tagCognitive: 'Cognitive AI',
    adaptiveSystems: 'B2B Solutions',
    subtitle: '• The Future of Corporate Hiring 2026',
    heading: ['Hire Intelligence.', 'Rent Results.'],
    btnFeatures: 'Who We Offer?',
    btnHowItWorks: 'How Rental Works',
    tag1: 'LLM Models',
    tag2: 'Deep Integration',
    tag3: '24/7 Automation',
    // Section 2: Roles
    rolesHeading: 'Who are you hiring?',
    rolesDescription: "We don't sell chatbots. We rent ready-made specialists already trained to solve tasks in your niche.",
    role1Title: 'Technical Support Specialist (L1/L2)',
    role1Desc: "Instantly closes 80% of tickets. Knows all documentation. Never gets tired.",
    role2Title: 'Sales Manager',
    role2Desc: 'Qualifies leads, consults on catalog, drives to payment.',
    role3Title: 'Internal Assistant (HR/Office)',
    role3Desc: 'Helps your live employees find regulations and onboard newcomers.',
    // Section 3: How it works
    howHeading: 'Employee as a Service (EaaS)',
    howStep1Title: 'Interview',
    howStep1Desc: 'You tell us what tasks the digital employee should handle and which databases to access.',
    howStep2Title: 'Training',
    howStep2Desc: 'We deploy the vnxORACLE core, train the neural network on your specifics, and integrate into your processes.',
    howStep3Title: 'Going Live',
    howStep3Desc: 'The employee starts working for a fixed subscription fee. No sick leave, taxes, or vacations.',
    // Section 4: Trust
    trustHeading: 'Intelligence you can trust your business with.',
    trustPoint1Title: 'Isolated Memory',
    trustPoint1Desc: 'Your company data stays within your perimeter only.',
    trustPoint2Title: 'Controlled Logic',
    trustPoint2Desc: "The employee doesn't hallucinate and strictly follows the assigned Tone of Voice.",
    trustPoint3Title: 'Continuous Evolution',
    trustPoint3Desc: 'You get AI core updates automatically, with no hidden development fees.'
  },
  ru: {
    brand: 'vnxORACLE',
    menu: 'Меню',
    tagAdvanced: 'Цифровой Штат',
    tagCognitive: 'Когнитивный ИИ',
    adaptiveSystems: 'B2B Решения',
    subtitle: '• Будущее корпоративного найма 2026',
    heading: ['Нанимайте Интеллект.', 'Арендуйте Результат.'],
    btnFeatures: 'Кого мы предлагаем?',
    btnHowItWorks: 'Как работает аренда',
    tag1: 'LLM-Модели',
    tag2: 'Глубокая Интеграция',
    tag3: 'Автоматизация 24/7',
    // Section 2: Roles
    rolesHeading: 'Кого вы берете в команду?',
    rolesDescription: 'Мы не продаем чат-ботов. Мы сдаем в аренду готовых специалистов, которые уже обучены решать задачи вашей ниши.',
    role1Title: 'Специалист Техподдержки (L1/L2)',
    role1Desc: 'Мгновенно закрывает 80% тикетов. Знает всю документацию. Не устает.',
    role2Title: 'Менеджер по Продажам',
    role2Desc: 'Квалифицирует лидов, консультирует по каталогу, доводит до оплаты.',
    role3Title: 'Внутренний Ассистент (HR/Офис)',
    role3Desc: 'Помогает вашим живым сотрудникам находить регламенты и онбордить новичков.',
    // Section 3: How it works
    howHeading: 'Сотрудник как Услуга (EaaS)',
    howStep1Title: 'Собеседование',
    howStep1Desc: 'Вы рассказываете, какие задачи должен закрывать цифровой сотрудник и к каким базам данных иметь доступ.',
    howStep2Title: 'Стажировка',
    howStep2Desc: 'Мы разворачиваем ядро на базе vnxORACLE, обучаем нейросеть вашей специфике и интегрируем в ваши процессы.',
    howStep3Title: 'Выход на работу',
    howStep3Desc: 'Сотрудник начинает работу за фиксированную абонентскую плату. Никаких больничных, налогов и отпусков.',
    // Section 4: Trust
    trustHeading: 'Разум, которому можно доверить бизнес.',
    trustPoint1Title: 'Изолированная память',
    trustPoint1Desc: 'Данные вашей компании остаются только внутри вашего контура.',
    trustPoint2Title: 'Управляемая логика',
    trustPoint2Desc: 'Сотрудник не галлюцинирует и строго следует заданному Tone of Voice.',
    trustPoint3Title: 'Непрерывная эволюция',
    trustPoint3Desc: 'Вы получаете апдейты AI-ядра автоматически, без скрытых платежей за разработку.'
  }
}

function LogoMark() {
  return (
    <svg
      className="logo-mark"
      width="26"
      height="26"
      viewBox="0 0 26 26"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <g transform="rotate(-35 13 13)">
        <rect x="3" y="6.5" width="20" height="5.5" rx="2.75" fill="#000000" />
        <rect x="3" y="14" width="20" height="5.5" rx="2.75" fill="#000000" />
      </g>
    </svg>
  )
}

function DotGridIcon() {
  return (
    <svg
      width="12"
      height="12"
      viewBox="0 0 12 12"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <circle cx="3.5" cy="3.5" r="1.6" fill="#ffffff" />
      <circle cx="8.5" cy="3.5" r="1.6" fill="#ffffff" />
      <circle cx="3.5" cy="8.5" r="1.6" fill="#ffffff" />
      <circle cx="8.5" cy="8.5" r="1.6" fill="#ffffff" />
    </svg>
  )
}

function Navbar({ lang, setLang }) {
  const t = translations[lang]

  return (
    <motion.nav
      className="navbar"
      initial={{ y: -16, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.8, ease: EASE }}
    >
      <div className="nav-left">
        <a className="logo" href="#top">
          <LogoMark />
          <span className="brand">{t.brand}</span>
        </a>

        <button className="menu-button" type="button">
          <span className="menu-icon">
            <Plus size={12} strokeWidth={3} />
          </span>
          <span className="menu-label">{t.menu}</span>
        </button>

        <div className="tags-pill">
          <span className="tags-pill-item">{t.tagAdvanced}</span>
          <span className="tags-pill-item">{t.tagCognitive}</span>
        </div>
      </div>

      <div className="nav-right">
        <button
          className="lang-switch"
          onClick={() => setLang(lang === 'en' ? 'ru' : 'en')}
          type="button"
        >
          {lang === 'en' ? 'RU' : 'EN'}
        </button>

        <div className="right-pill">
          <button className="right-pill-button" type="button" aria-label={t.adaptiveSystems}>
            <DotGridIcon />
          </button>
          <span className="right-pill-label">{t.adaptiveSystems}</span>
        </div>
      </div>
    </motion.nav>
  )
}

function BackgroundVideo() {
  return (
    <div className="video-layer">
      <motion.div
        className="video-wrapper"
        initial={{ opacity: 0, scale: 1.05 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1.8, ease: EASE }}
      >
        <video className="hero-video" src={VIDEO_URL} autoPlay muted playsInline loop />
      </motion.div>
    </div>
  )
}

function FooterContent({ lang }) {
  const t = translations[lang]

  return (
    <motion.div
      className="footer"
      initial={{ y: 20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 1, delay: 0.5, ease: EASE }}
    >
      <div className="footer-inner">
        <div className="footer-left">
          <motion.div
            className="subtitle"
            initial={{ y: 16, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.6, ease: EASE }}
          >
            <span className="subtitle-dot" />
            <span className="subtitle-text">{t.subtitle}</span>
          </motion.div>

          <motion.h1
            className="heading"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.8, ease: EASE }}
          >
            {t.heading[0]}
            <br />
            {t.heading[1]}
          </motion.h1>

          <motion.div
            className="actions"
            initial={{ y: 16, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.8, delay: 1, ease: EASE }}
          >
            <button className="btn btn-primary" type="button">
              {t.btnFeatures}
            </button>
            <button className="btn btn-ghost" type="button">
              {t.btnHowItWorks}
            </button>
          </motion.div>
        </div>

        <div className="footer-right">
          <span className="tag">{t.tag1}</span>
          <span className="tag">{t.tag2}</span>
          <span className="tag">{t.tag3}</span>
        </div>
      </div>
    </motion.div>
  )
}

function RolesSection({ lang }) {
  const t = translations[lang]

  return (
    <section className="section roles-section">
      <div className="section-inner">
        <h2 className="section-heading">{t.rolesHeading}</h2>
        <p className="section-description">{t.rolesDescription}</p>

        <div className="roles-grid">
          <div className="role-card">
            <h3 className="role-title">{t.role1Title}</h3>
            <p className="role-desc">{t.role1Desc}</p>
          </div>
          <div className="role-card">
            <h3 className="role-title">{t.role2Title}</h3>
            <p className="role-desc">{t.role2Desc}</p>
          </div>
          <div className="role-card">
            <h3 className="role-title">{t.role3Title}</h3>
            <p className="role-desc">{t.role3Desc}</p>
          </div>
        </div>
      </div>
    </section>
  )
}

function HowItWorksSection({ lang }) {
  const t = translations[lang]

  return (
    <section className="section how-section">
      <div className="section-inner">
        <h2 className="section-heading">{t.howHeading}</h2>

        <div className="steps-grid">
          <div className="step-card">
            <div className="step-number">01</div>
            <h3 className="step-title">{t.howStep1Title}</h3>
            <p className="step-desc">{t.howStep1Desc}</p>
          </div>
          <div className="step-card">
            <div className="step-number">02</div>
            <h3 className="step-title">{t.howStep2Title}</h3>
            <p className="step-desc">{t.howStep2Desc}</p>
          </div>
          <div className="step-card">
            <div className="step-number">03</div>
            <h3 className="step-title">{t.howStep3Title}</h3>
            <p className="step-desc">{t.howStep3Desc}</p>
          </div>
        </div>
      </div>
    </section>
  )
}

function TrustSection({ lang }) {
  const t = translations[lang]

  return (
    <section className="section trust-section">
      <div className="section-inner">
        <h2 className="section-heading">{t.trustHeading}</h2>

        <div className="trust-grid">
          <div className="trust-card">
            <h3 className="trust-title">{t.trustPoint1Title}</h3>
            <p className="trust-desc">{t.trustPoint1Desc}</p>
          </div>
          <div className="trust-card">
            <h3 className="trust-title">{t.trustPoint2Title}</h3>
            <p className="trust-desc">{t.trustPoint2Desc}</p>
          </div>
          <div className="trust-card">
            <h3 className="trust-title">{t.trustPoint3Title}</h3>
            <p className="trust-desc">{t.trustPoint3Desc}</p>
          </div>
        </div>
      </div>
    </section>
  )
}

export default function App() {
  const [lang, setLang] = useState('ru')

  return (
    <>
      <div className="hero" id="top">
        <BackgroundVideo />
        <Navbar lang={lang} setLang={setLang} />
        <FooterContent lang={lang} />
      </div>

      <RolesSection lang={lang} />
      <HowItWorksSection lang={lang} />
      <TrustSection lang={lang} />
    </>
  )
}
