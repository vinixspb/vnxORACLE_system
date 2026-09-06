import { motion } from 'motion/react'
import { Plus, Moon, Sun } from 'lucide-react'
import { useCallback, useState } from 'react'
import { translations } from './i18n'
import DirectionsSection from './components/DirectionsSection'
import ProblemsSection from './components/ProblemsSection'
import SolutionSection from './components/SolutionSection'
import UnderTheHoodSection from './components/UnderTheHoodSection'
import OnboardingSection, { emptyConfig } from './components/OnboardingSection'
import { deriveConfigFromMessages } from './configFromChat'
import './App.css'
import ChatWidget from './components/ChatWidget'

const EASE = [0.16, 1, 0.3, 1]

const VIDEO_URL =
  'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260508_215831_c6a8989c-d716-4d8d-8745-e972a2eec711.mp4'

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
        <rect x="3" y="6.5" width="20" height="5.5" rx="2.75" fill="currentColor" />
        <rect x="3" y="14" width="20" height="5.5" rx="2.75" fill="currentColor" />
      </g>
    </svg>
  )
}

function Navbar({ lang, setLang, theme, toggleTheme, onCreateBot }) {
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
          className="theme-toggle"
          onClick={toggleTheme}
          type="button"
          aria-label="Toggle theme"
        >
          {theme === 'light' ? <Moon size={14} strokeWidth={2} /> : <Sun size={14} strokeWidth={2} />}
        </button>

        <button
          className="lang-switch"
          onClick={() => setLang(lang === 'en' ? 'ru' : 'en')}
          type="button"
        >
          {lang === 'en' ? 'RU' : 'EN'}
        </button>

        <button className="btn btn-ghost-nav" type="button">
          {t.navDemo}
        </button>

        <button className="btn btn-primary-nav" type="button" onClick={onCreateBot}>
          {t.navCreateBot}
        </button>
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

function FooterContent({ lang, scrollToSection, onCreateBot }) {
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
            <button
              className="btn btn-primary"
              type="button"
              onClick={onCreateBot}
            >
              {t.btnCreateBot}
            </button>
            <button
              className="btn btn-ghost"
              type="button"
              onClick={() => scrollToSection('roles')}
            >
              {t.btnFeatures}
            </button>
            <button
              className="btn btn-ghost"
              type="button"
              onClick={() => scrollToSection('how')}
            >
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
    <section className="section roles-section" id="roles">
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
    <section className="section how-section" id="how">
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
    <section className="section trust-section" id="trust">
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
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem('vnx-theme')
    return saved || 'light'
  })
  const [config, setConfig] = useState(emptyConfig)
  const [prefilled, setPrefilled] = useState(() => new Set())
  const [chatOpen, setChatOpen] = useState(0)
  const [onboardingOpen, setOnboardingOpen] = useState(false)

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
    localStorage.setItem('vnx-theme', newTheme)
  }

  const scrollToSection = (id) => {
    document.getElementById(id)?.scrollIntoView({
      behavior: 'smooth',
      block: 'start'
    })
  }

  const openOnboarding = () => {
    setOnboardingOpen(true)
  }

  const closeOnboarding = () => {
    setOnboardingOpen(false)
  }

  const t = translations[lang]
  const roleOptions =
    t.onboarding.steps
      .find((step) => step.id === 'employee')
      ?.fields.find((field) => field.id === 'agentRoleField')?.options ?? []

  // Диалог с ИИ-консультантом → предзаполненный конфигуратор.
  const handleHandoff = useCallback(
    (userMessages) => {
      const patch = deriveConfigFromMessages(userMessages, roleOptions)
      const filled = Object.entries(patch).filter(([, value]) => value)

      setConfig((prev) => ({ ...prev, ...Object.fromEntries(filled) }))
      setPrefilled(new Set(filled.map(([key]) => key)))
      setOnboardingOpen(true)
    },
    [roleOptions]
  )

  const handleDirectionSelect = useCallback((item) => {
    setConfig((prev) => ({
      ...prev,
      channel: item.id === 'messengers' ? 'Telegram' : item.id === 'web' ? 'Website widget' : prev.channel
    }))
    setOnboardingOpen(true)
  }, [])

  return (
    <div data-theme={theme}>
      <div className="hero" id="top">
        <BackgroundVideo />
        <Navbar lang={lang} setLang={setLang} theme={theme} toggleTheme={toggleTheme} onCreateBot={openOnboarding} />
        <FooterContent lang={lang} scrollToSection={scrollToSection} onCreateBot={openOnboarding} />
      </div>

      <DirectionsSection t={t} onSelect={handleDirectionSelect} />
      <ProblemsSection t={t} />
      <SolutionSection t={t} />
      <RolesSection lang={lang} />
      <HowItWorksSection lang={lang} />
      <UnderTheHoodSection t={t} />
      <TrustSection lang={lang} />

      {onboardingOpen && (
        <div className="modal-overlay" onClick={closeOnboarding}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={closeOnboarding}>×</button>
            <OnboardingSection
              t={t}
              config={config}
              setConfig={setConfig}
              prefilled={prefilled}
              onTestDialog={() => setChatOpen((n) => n + 1)}
            />
          </div>
        </div>
      )}

      <ChatWidget lang={lang} theme={theme} onHandoff={handleHandoff} openSignal={chatOpen} />
    </div>
  )
}
