import { useRef } from 'react'

/**
 * 3D tilt effect: card follows mouse pointer with perspective transform
 * First contact is smooth, then follows mouse speed
 */
export function useTiltEffect(strength = 15) {
  const ref = useRef(null)
  const isFirstContact = useRef(true)

  const handleMouseEnter = () => {
    if (!ref.current) return
    // При первом контакте включаем плавный transition
    isFirstContact.current = true
    ref.current.style.transition = 'transform 0.3s ease-out'
  }

  const handleMouseMove = (e) => {
    if (!ref.current) return

    const card = ref.current
    const rect = card.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    const centerX = rect.width / 2
    const centerY = rect.height / 2

    const rotateX = ((y - centerY) / centerY) * -strength
    const rotateY = ((x - centerX) / centerX) * strength

    // После первого движения убираем transition для быстрого следования за мышкой
    if (isFirstContact.current) {
      isFirstContact.current = false
      setTimeout(() => {
        if (card) card.style.transition = 'none'
      }, 300)
    }

    card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`
  }

  const handleMouseLeave = () => {
    if (!ref.current) return
    // При уходе мыши плавно возвращаем в исходное положение
    ref.current.style.transition = 'transform 0.4s ease-out'
    ref.current.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)'
    // Сбрасываем флаг для следующего контакта
    isFirstContact.current = true
  }

  return {
    ref,
    onMouseEnter: handleMouseEnter,
    onMouseMove: handleMouseMove,
    onMouseLeave: handleMouseLeave
  }
}
