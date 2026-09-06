import { useState } from 'react'
import { ChevronUp, ChevronDown, Sparkles, Eye } from 'lucide-react'
import CollectedDataPanel from './CollectedDataPanel'

// Поля, которые чат умеет заполнять сам.
export const CONFIG_FIELDS = [
  'website',
  'channel',
  'businessName',
  'address',
  'phone',
  'about',
  'agentName',
  'agentRoleField',
  'tone',
  'tasks',
  'contactName',
  'contactEmail',
  'contactTelegram'
]

export const emptyConfig = () =>
  CONFIG_FIELDS.reduce((acc, key) => ({ ...acc, [key]: '' }), {})

const CHANNELS = ['Telegram', 'WhatsApp', 'VK', 'Website widget']

function Field({ field, value, onChange, prefilled, badge }) {
  const common = {
    id: field.id,
    value,
    onChange: (event) => onChange(field.id, event.target.value),
    className: prefilled ? 'form-input is-prefilled' : 'form-input'
  }

  return (
    <div className="form-row">
      <label className="form-label" htmlFor={field.id}>
        {field.label}
        {prefilled && (
          <span className="form-badge">
            <Sparkles size={11} strokeWidth={2} />
            {badge}
          </span>
        )}
      </label>

      {field.type === 'textarea' ? (
        <textarea {...common} rows={5} placeholder={field.placeholder} />
      ) : field.type === 'select' ? (
        <select {...common}>
          <option value="">—</option>
          {field.options.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      ) : (
        <input {...common} type={field.type} placeholder={field.placeholder} />
      )}
    </div>
  )
}

export default function OnboardingSection({ t, config, setConfig, prefilled, onTestDialog }) {
  const o = t.onboarding
  const [openSteps, setOpenSteps] = useState(() => o.steps.map((step) => step.id))
  const [sourceOpen, setSourceOpen] = useState(true)
  const [savedAt, setSavedAt] = useState(false)
  const [activated, setActivated] = useState(false)
  const [collectedOpen, setCollectedOpen] = useState(false)

  const update = (key, value) => {
    setConfig((prev) => ({ ...prev, [key]: value }))
    setSavedAt(false)
    setActivated(false)
  }

  const toggleStep = (id) =>
    setOpenSteps((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    )

  const agentName = config.agentName?.trim() || o.unnamed

  return (
    <section className="section onboarding-section" id="configure">
      <div className="onboarding-inner">
        <div className="agent-card">
          <div className="agent-identity">
            <span className="agent-avatar" aria-hidden="true">
              {agentName.slice(0, 1).toUpperCase()}
            </span>
            <div className="agent-meta">
              <span className="agent-name">{agentName}</span>
              <span className="agent-role">{o.agentRole}</span>
            </div>
          </div>

          <div className="agent-actions">
            <button className="btn-icon" type="button" onClick={() => setCollectedOpen(true)} title="View collected data">
              <Eye size={20} />
            </button>
            <button className="btn-soft" type="button" onClick={() => setSavedAt(true)}>
              {o.save}
            </button>
            <button className="btn-outline" type="button" onClick={onTestDialog}>
              {o.testCall}
            </button>
            <button className="btn-solid" type="button" onClick={() => setActivated(true)}>
              {o.activate}
            </button>
          </div>
        </div>

        {savedAt && <p className="form-note">{o.saved}</p>}
        {activated && <p className="form-note">{o.activateHint}</p>}

        <div className="panel">
          <button
            className="panel-head"
            type="button"
            onClick={() => setSourceOpen((prev) => !prev)}
            aria-expanded={sourceOpen}
          >
            <span className="panel-title">{o.trainingSource.title}</span>
            {sourceOpen ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          </button>

          {sourceOpen && (
            <div className="panel-body">
              <div className="form-row">
                <label className="form-label" htmlFor="website">
                  {o.trainingSource.websiteLabel}
                  {prefilled.has('website') && (
                    <span className="form-badge">
                      <Sparkles size={11} strokeWidth={2} />
                      {o.prefilledBadge}
                    </span>
                  )}
                </label>
                <p className="form-hint">{o.trainingSource.websiteHint}</p>
                <input
                  id="website"
                  type="text"
                  className={prefilled.has('website') ? 'form-input is-prefilled' : 'form-input'}
                  placeholder={o.trainingSource.websitePlaceholder}
                  value={config.website}
                  onChange={(event) => update('website', event.target.value)}
                />
              </div>

              <div className="form-row">
                <label className="form-label" htmlFor="channel">
                  {o.trainingSource.channelLabel}
                  {prefilled.has('channel') && (
                    <span className="form-badge">
                      <Sparkles size={11} strokeWidth={2} />
                      {o.prefilledBadge}
                    </span>
                  )}
                </label>
                <p className="form-hint">{o.trainingSource.channelHint}</p>
                <select
                  id="channel"
                  className={prefilled.has('channel') ? 'form-input is-prefilled' : 'form-input'}
                  value={config.channel}
                  onChange={(event) => update('channel', event.target.value)}
                >
                  <option value="">—</option>
                  {CHANNELS.map((channel) => (
                    <option key={channel} value={channel}>
                      {channel}
                    </option>
                  ))}
                </select>
              </div>

              <div className="panel-footer">
                <button className="btn-solid" type="button" onClick={onTestDialog}>
                  {o.trainingSource.reinit}
                </button>
                <button
                  className="btn-link"
                  type="button"
                  onClick={() => update('website', '')}
                >
                  {o.trainingSource.noWebsite}
                </button>
                <button
                  className="btn-link btn-link-muted"
                  type="button"
                  onClick={() => setSourceOpen(false)}
                >
                  {o.trainingSource.skip}
                </button>
              </div>
            </div>
          )}
        </div>

        <h2 className="onboarding-heading">{o.heading}</h2>
        <p className="onboarding-subheading">{o.subheading}</p>

        {o.steps.map((step, index) => {
          const isOpen = openSteps.includes(step.id)

          return (
            <div className="panel" key={step.id}>
              <button
                className="panel-head"
                type="button"
                onClick={() => toggleStep(step.id)}
                aria-expanded={isOpen}
              >
                <span className="panel-title">
                  <span className="step-badge">{index + 1}</span>
                  {step.title}
                </span>
                {isOpen ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
              </button>

              {isOpen && (
                <div className="panel-body">
                  {step.fields.map((field) => (
                    <Field
                      key={field.id}
                      field={field}
                      value={config[field.id] ?? ''}
                      onChange={update}
                      prefilled={prefilled.has(field.id)}
                      badge={o.prefilledBadge}
                    />
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>

      <CollectedDataPanel
        isOpen={collectedOpen}
        onClose={() => setCollectedOpen(false)}
        config={config}
        prefilled={prefilled}
        t={t}
      />
    </section>
  )
}
