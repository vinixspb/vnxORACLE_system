import { motion } from 'motion/react'
import { XCircle, Unplug, RefreshCcw } from 'lucide-react'

const EASE = [0.16, 1, 0.3, 1]

const icons = {
  0: XCircle,
  1: Unplug,
  2: RefreshCcw
}

export default function ProblemsSection({ t }) {
  return (
    <section className="section problems-section" id="problems">
      <div className="container">
        <div className="problems-head">
          <motion.h2
            className="section-heading"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.6, ease: EASE }}
          >
            {t.problems.heading}
          </motion.h2>
          <motion.p
            className="problems-subheading"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.6, delay: 0.1, ease: EASE }}
          >
            {t.problems.subheading}
          </motion.p>
        </div>

        <div className="problems-grid">
          {t.problems.items.map((item, idx) => {
            const Icon = icons[idx]
            return (
              <motion.div
                key={idx}
                className="problem-card"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-80px' }}
                transition={{ duration: 0.5, delay: idx * 0.1, ease: EASE }}
              >
                <div className="problem-icon">
                  <Icon size={28} strokeWidth={1.8} />
                </div>
                <h3 className="problem-title">{item.title}</h3>
                <p className="problem-desc">{item.desc}</p>
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
