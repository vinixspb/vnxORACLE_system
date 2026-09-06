import { motion } from 'motion/react'
import { Zap, Shield, Settings } from 'lucide-react'

const EASE = [0.16, 1, 0.3, 1]

const icons = {
  0: Zap,
  1: Shield,
  2: Settings
}

export default function UnderTheHoodSection({ t }) {
  return (
    <section className="section under-hood-section" id="under-hood">
      <div className="container">
        <div className="under-hood-head">
          <motion.h2
            className="section-heading"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.6, ease: EASE }}
          >
            {t.underTheHood.heading}
          </motion.h2>
          <motion.p
            className="under-hood-subheading"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.6, delay: 0.1, ease: EASE }}
          >
            {t.underTheHood.subheading}
          </motion.p>
        </div>

        <div className="under-hood-grid">
          {t.underTheHood.items.map((item, idx) => {
            const Icon = icons[idx]
            return (
              <motion.div
                key={idx}
                className="hood-card"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-80px' }}
                transition={{ duration: 0.5, delay: idx * 0.1, ease: EASE }}
              >
                <div className="hood-icon">
                  <Icon size={30} strokeWidth={1.8} />
                </div>
                <h3 className="hood-title">{item.title}</h3>
                <p className="hood-desc">{item.desc}</p>
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
