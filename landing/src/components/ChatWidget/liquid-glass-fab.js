/**
 * Liquid Glass FAB - Standalone Module
 * Apple Vision Pro style water drop button
 * Pure vanilla JS - works with any framework
 *
 * Usage:
 * const fab = new LiquidGlassFAB(containerElement, onToggleCallback)
 * fab.setState(isOpen)
 * fab.destroy()
 */

// Spring physics for organic motion
class SpringValue {
    constructor(initial, stiffness = 0.1, damping = 0.8) {
        this.current = initial
        this.target = initial
        this.velocity = 0
        this.stiffness = stiffness
        this.damping = damping
    }

    update() {
        this.velocity += (this.target - this.current) * this.stiffness
        this.velocity *= this.damping
        this.current += this.velocity

        // Settle threshold
        if (Math.abs(this.velocity) < 0.001 && Math.abs(this.target - this.current) < 0.001) {
            this.current = this.target
            this.velocity = 0
        }
    }

    set(newTarget) {
        this.target = newTarget
    }
}

export class LiquidGlassFAB {
    constructor(container, onToggle) {
        this.container = container
        this.onToggle = onToggle
        this.isOpen = false

        // Create FAB structure
        this.createElements()

        // Initialize spring physics
        this.initPhysics()

        // Bind events
        this.initEventListeners()

        // Start animation loop
        this.startAnimationLoop()

        // Entrance animation
        this.playEntranceAnimation()
    }

    createElements() {
        // Wrapper
        this.wrapper = document.createElement('div')
        this.wrapper.className = 'liquid-fab-wrapper'

        // FAB button
        this.fab = document.createElement('button')
        this.fab.className = 'liquid-fab'
        this.fab.setAttribute('aria-label', 'Toggle chat')
        this.fab.innerHTML = `
            <svg class="chat-icon" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
        `

        this.wrapper.appendChild(this.fab)
        this.container.appendChild(this.wrapper)
    }

    initPhysics() {
        // Light caustics
        this.lightX = new SpringValue(35, 0.08, 0.82)
        this.lightY = new SpringValue(35, 0.08, 0.82)
        this.scale = new SpringValue(1.0, 0.15, 0.75)
        this.shineX = new SpringValue(0, 0.06, 0.85)
        this.shineY = new SpringValue(0, 0.06, 0.85)

        // 8-corner morphing (faster response)
        this.morphTL = new SpringValue(50, 0.12, 0.75)
        this.morphTR = new SpringValue(50, 0.12, 0.75)
        this.morphBR = new SpringValue(50, 0.12, 0.75)
        this.morphBL = new SpringValue(50, 0.12, 0.75)
        this.morphTLV = new SpringValue(50, 0.12, 0.75)
        this.morphTRV = new SpringValue(50, 0.12, 0.75)
        this.morphBRV = new SpringValue(50, 0.12, 0.75)
        this.morphBLV = new SpringValue(50, 0.12, 0.75)

        // Translation
        this.translateX = new SpringValue(0, 0.08, 0.84)
        this.translateY = new SpringValue(0, 0.08, 0.84)

        // Parallax for icon
        this.parallaxX = new SpringValue(0, 0.12, 0.85)
        this.parallaxY = new SpringValue(0, 0.12, 0.85)

        this.isHovering = false
    }

    initEventListeners() {
        this.onEnterBound = () => this.onEnter()
        this.onLeaveBound = () => this.onLeave()
        this.onMoveBound = (e) => this.onMove(e)
        this.onClickBound = (e) => this.onClick(e)

        this.fab.addEventListener('pointerenter', this.onEnterBound)
        this.fab.addEventListener('pointerleave', this.onLeaveBound)
        this.fab.addEventListener('pointermove', this.onMoveBound)
        this.fab.addEventListener('click', this.onClickBound)
    }

    onEnter() {
        this.isHovering = true
        this.scale.set(1.1)
    }

    onLeave() {
        this.isHovering = false
        this.lightX.set(35)
        this.lightY.set(35)
        this.scale.set(1.0)
        this.shineX.set(0)
        this.shineY.set(0)

        // Reset morphing to circle
        [this.morphTL, this.morphTR, this.morphBR, this.morphBL,
         this.morphTLV, this.morphTRV, this.morphBRV, this.morphBLV].forEach(m => m.set(50))

        this.translateX.set(0)
        this.translateY.set(0)
        this.parallaxX.set(0)
        this.parallaxY.set(0)
    }

    onMove(e) {
        if (!this.isHovering) return

        const rect = this.fab.getBoundingClientRect()
        const centerX = rect.width / 2
        const centerY = rect.height / 2
        const x = e.clientX - rect.left
        const y = e.clientY - rect.top

        const normX = (x / rect.width) * 100
        const normY = (y / rect.height) * 100

        // Update light caustics
        this.lightX.set(normX)
        this.lightY.set(normY)

        // Shine offset
        const dx = (normX - 50) * 0.15
        const dy = (normY - 50) * 0.15
        this.shineX.set(dx)
        this.shineY.set(dy)

        // Parallax for icon (max 6px travel)
        const parallaxStrength = 6
        this.parallaxX.set(((x - centerX) / centerX) * parallaxStrength)
        this.parallaxY.set(((y - centerY) / centerY) * parallaxStrength)

        // Aggressive morphing
        const distance = Math.hypot(x - centerX, y - centerY) / centerX
        const deformAmount = Math.min(distance * 35, 45)

        // Translation toward cursor
        this.translateX.set((x - centerX) * 0.05)
        this.translateY.set((y - centerY) * 0.05)

        // Quadrant-based morphing
        if (normX < 50 && normY < 50) {
            // Top-left quadrant
            this.morphTL.set(50 + deformAmount * 1.2)
            this.morphTLV.set(50 + deformAmount * 1.2)
            this.morphBR.set(50 - deformAmount * 0.7)
            this.morphBRV.set(50 - deformAmount * 0.7)
            this.morphTR.set(50 + deformAmount * 0.5)
            this.morphBL.set(50 + deformAmount * 0.5)
        } else if (normX >= 50 && normY < 50) {
            // Top-right quadrant
            this.morphTR.set(50 + deformAmount * 1.2)
            this.morphTRV.set(50 + deformAmount * 1.2)
            this.morphBL.set(50 - deformAmount * 0.7)
            this.morphBLV.set(50 - deformAmount * 0.7)
            this.morphTL.set(50 + deformAmount * 0.5)
            this.morphBR.set(50 + deformAmount * 0.5)
        } else if (normX >= 50 && normY >= 50) {
            // Bottom-right quadrant
            this.morphBR.set(50 + deformAmount * 1.2)
            this.morphBRV.set(50 + deformAmount * 1.2)
            this.morphTL.set(50 - deformAmount * 0.7)
            this.morphTLV.set(50 - deformAmount * 0.7)
            this.morphTR.set(50 + deformAmount * 0.5)
            this.morphBL.set(50 + deformAmount * 0.5)
        } else {
            // Bottom-left quadrant
            this.morphBL.set(50 + deformAmount * 1.2)
            this.morphBLV.set(50 + deformAmount * 1.2)
            this.morphTR.set(50 - deformAmount * 0.7)
            this.morphTRV.set(50 - deformAmount * 0.7)
            this.morphTL.set(50 + deformAmount * 0.5)
            this.morphBR.set(50 + deformAmount * 0.5)
        }
    }

    onClick(e) {
        // Ripple effect
        const ripple = document.createElement('div')
        ripple.className = 'liquid-fab-ripple'

        const rect = this.fab.getBoundingClientRect()
        const size = Math.max(rect.width, rect.height)
        const x = e.clientX - rect.left - size / 2
        const y = e.clientY - rect.top - size / 2

        ripple.style.width = ripple.style.height = size + 'px'
        ripple.style.left = x + 'px'
        ripple.style.top = y + 'px'

        this.fab.appendChild(ripple)
        setTimeout(() => ripple.remove(), 800)

        // Squash animation
        this.scale.set(0.96)
        ;[this.morphTL, this.morphTR].forEach(m => m.set(45))
        ;[this.morphBR, this.morphBL].forEach(m => m.set(55))
        ;[this.morphTLV, this.morphTRV].forEach(m => m.set(55))
        ;[this.morphBRV, this.morphBLV].forEach(m => m.set(45))

        setTimeout(() => {
            this.scale.set(this.isHovering ? 1.1 : 1.0)
            ;[this.morphTL, this.morphTR, this.morphBR, this.morphBL,
             this.morphTLV, this.morphTRV, this.morphBRV, this.morphBLV].forEach(m => m.set(50))
        }, 150)

        // Trigger callback
        if (this.onToggle) {
            this.onToggle()
        }
    }

    startAnimationLoop() {
        const animate = () => {
            // Update all springs
            ;[this.lightX, this.lightY, this.scale, this.shineX, this.shineY,
             this.morphTL, this.morphTR, this.morphBR, this.morphBL,
             this.morphTLV, this.morphTRV, this.morphBRV, this.morphBLV,
             this.translateX, this.translateY, this.parallaxX, this.parallaxY]
            .forEach(spring => spring.update())

            // Apply to CSS variables
            this.fab.style.setProperty('--light-x', `${this.lightX.current}%`)
            this.fab.style.setProperty('--light-y', `${this.lightY.current}%`)
            this.fab.style.setProperty('--scale', this.scale.current)
            this.fab.style.setProperty('--shine-x', `${this.shineX.current}px`)
            this.fab.style.setProperty('--shine-y', `${this.shineY.current}px`)

            this.fab.style.setProperty('--radius-tl', `${this.morphTL.current}%`)
            this.fab.style.setProperty('--radius-tr', `${this.morphTR.current}%`)
            this.fab.style.setProperty('--radius-br', `${this.morphBR.current}%`)
            this.fab.style.setProperty('--radius-bl', `${this.morphBL.current}%`)
            this.fab.style.setProperty('--radius-tl-v', `${this.morphTLV.current}%`)
            this.fab.style.setProperty('--radius-tr-v', `${this.morphTRV.current}%`)
            this.fab.style.setProperty('--radius-br-v', `${this.morphBRV.current}%`)
            this.fab.style.setProperty('--radius-bl-v', `${this.morphBLV.current}%`)

            this.fab.style.setProperty('--translateX', `${this.translateX.current}px`)
            this.fab.style.setProperty('--translateY', `${this.translateY.current}px`)

            this.fab.style.setProperty('--parallax-x', `${this.parallaxX.current}px`)
            this.fab.style.setProperty('--parallax-y', `${this.parallaxY.current}px`)

            this.animationFrame = requestAnimationFrame(animate)
        }

        this.animationFrame = requestAnimationFrame(animate)
    }

    playEntranceAnimation() {
        this.fab.classList.add('drop-entrance')
        setTimeout(() => {
            this.fab.classList.remove('drop-entrance')
        }, 1600)
    }

    setState(isOpen) {
        this.isOpen = isOpen
        // Visual state sync can be added here if needed
        // e.g., change icon, add 'open' class, etc.
    }

    destroy() {
        // Cancel animation loop
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame)
        }

        // Remove event listeners
        this.fab.removeEventListener('pointerenter', this.onEnterBound)
        this.fab.removeEventListener('pointerleave', this.onLeaveBound)
        this.fab.removeEventListener('pointermove', this.onMoveBound)
        this.fab.removeEventListener('click', this.onClickBound)

        // Remove DOM
        this.wrapper.remove()
    }
}
