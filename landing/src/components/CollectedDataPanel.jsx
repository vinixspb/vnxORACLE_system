import { motion, AnimatePresence } from 'motion/react'
import { X, CheckCircle2, Circle } from 'lucide-react'

const EASE = [0.16, 1, 0.3, 1]

export default function CollectedDataPanel({ isOpen, onClose, config, prefilled, t }) {
  // Собираем поля из всех шагов конфигуратора
  const allFields = t.onboarding.steps.flatMap((step) => step.fields || [])

  // Группируем по шагам для отображения
  const groups = t.onboarding.steps.map((step) => ({
    title: step.title,
    fields: (step.fields || []).map((field) => ({
      label: field.label,
      value: config[field.id] || '',
      filled: prefilled.has(field.id) && !!config[field.id]
    }))
  }))

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            className="collected-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={onClose}
          />

          {/* Panel */}
          <motion.div
            className="collected-panel"
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ duration: 0.4, ease: EASE }}
          >
            <div className="collected-header">
              <h3 className="collected-title">Collected data</h3>
              <button className="collected-close" onClick={onClose} aria-label="Close panel">
                <X size={20} strokeWidth={2} />
              </button>
            </div>

            <div className="collected-body">
              {groups.map((group, idx) => (
                <div key={idx} className="collected-group">
                  <h4 className="collected-group-title">{group.title}</h4>
                  {group.fields.map((field, fIdx) => (
                    <div key={fIdx} className="collected-field">
                      <div className="collected-field-head">
                        {field.filled ? (
                          <CheckCircle2 size={16} strokeWidth={2} className="collected-icon-filled" />
                        ) : (
                          <Circle size={16} strokeWidth={2} className="collected-icon-empty" />
                        )}
                        <span className="collected-field-label">{field.label}</span>
                      </div>
                      {field.value && (
                        <p className="collected-field-value">{field.value}</p>
                      )}
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
