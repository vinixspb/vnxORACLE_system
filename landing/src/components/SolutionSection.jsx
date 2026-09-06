import { motion } from 'motion/react'
import { Link, Database, Sparkles } from 'lucide-react'

const EASE = [0.16, 1, 0.3, 1]

const icons = {
  0: Link,
  1: Database,
  2: Sparkles
}

export default function SolutionSection({ t }) {
  return (
    <section className="section solution-section" id="solution">
      <div className="container">
        <div className="solution-head">
          <motion.h2
            className="section-heading"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.6, ease: EASE }}
          >
            {t.solution.heading}
          </motion.h2>
          <motion.p
            className="solution-subheading"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.6, delay: 0.1, ease: EASE }}
          >
            {t.solution.subheading}
          </motion.p>
        </div>

        <div className="solution-grid">
          {t.solution.items.map((item, idx) => {
            const Icon = icons[idx]
            return (
              <motion.div
                key={idx}
                className="solution-card"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-80px' }}
                transition={{ duration: 0.5, delay: idx * 0.1, ease: EASE }}
              >
                <div className="solution-icon">
                  <Icon size={32} strokeWidth={1.8} />
                </div>
                <h3 className="solution-title">{item.title}</h3>
                <p className="solution-desc">{item.desc}</p>
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
