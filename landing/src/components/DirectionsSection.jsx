import { motion } from 'motion/react'
import { MessagesSquare, BrainCircuit, Globe, ArrowRight, Check } from 'lucide-react'

const EASE = [0.16, 1, 0.3, 1]

const ICONS = {
  messages: MessagesSquare,
  brain: BrainCircuit,
  globe: Globe
}

export default function DirectionsSection({ t, onSelect }) {
  const d = t.directions

  return (
    <section className="section directions-section" id="directions">
      <div className="section-inner">
        <div className="directions-head">
          <h2 className="section-heading directions-heading">{d.heading}</h2>
          <p className="directions-subheading">{d.subheading}</p>
        </div>

        <div className="directions-grid">
          {d.items.map((item, index) => {
            const Icon = ICONS[item.icon] ?? MessagesSquare

            return (
              <motion.article
                key={item.id}
                className="direction-card"
                initial={{ y: 24, opacity: 0 }}
                whileInView={{ y: 0, opacity: 1 }}
                viewport={{ once: true, amount: 0.3 }}
                transition={{ duration: 0.7, delay: index * 0.12, ease: EASE }}
              >
                <span className="direction-icon">
                  <Icon size={30} strokeWidth={1.5} />
                </span>

                <h3 className="direction-title">{item.title}</h3>
                <p className="direction-desc">{item.desc}</p>

                <ul className="direction-bullets">
                  {item.bullets.map((bullet) => (
                    <li key={bullet} className="direction-bullet">
                      <Check size={14} strokeWidth={2.5} />
                      <span>{bullet}</span>
                    </li>
                  ))}
                </ul>

                <button
                  className="direction-link"
                  type="button"
                  onClick={() => onSelect(item)}
                >
                  {d.learnMore}
                  <ArrowRight size={15} strokeWidth={2} />
                </button>
              </motion.article>
            )
          })}
        </div>
      </div>
    </section>
  )
}
