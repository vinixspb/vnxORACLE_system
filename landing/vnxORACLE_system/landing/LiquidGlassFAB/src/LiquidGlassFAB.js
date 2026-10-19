/**
 * Liquid Glass FAB - Professional Standalone Module
 * Apple Vision Pro style water drop button with spring physics
 *
 * @version 1.2.1
 * @license MIT
 * @author vnxORACLE
 *
 * Architecture v1.2:
 * - Shadow DOM isolation (immune to global CSS)
 * - Portal Pattern (mode: 'embedded' | 'global')
 * - Strict Timer Registry (zero memory leaks)
 * - Proportional physics scaling
 *
 * Features:
 * - Spring physics for organic motion (Hooke's law)
 * - 8-corner morphing with CSS variables
 * - Glass morphism with backdrop filters
 * - Water drop entrance animation
 * - Ripple effect on click
 * - Parallax icon movement
 * - Light caustics following cursor
 * - Full instance isolation (multiple buttons per page)
 * - Framework agnostic vanilla JS
 *
 * Usage:
 *   import { LiquidGlassFAB } from './LiquidGlassFAB.js'
 *
 *   // Embedded mode (default)
 *   const fab = new LiquidGlassFAB(containerElement, {
 *     size: 80,
 *     mode: 'embedded',
 *     icon: '<svg>...</svg>',
 *     ariaLabel: 'Toggle chat',
 *     onToggle: (isOpen) => console.log('Toggled:', isOpen)
 *   })
 *
 *   // Global mode (portal to document.body)
 *   const fabGlobal = new LiquidGlassFAB(document.body, {
 *     mode: 'global',
 *     position: { bottom: '24px', right: '24px' }
 *   })
 *
 *   fab.setState(true)
 *   fab.destroy()
 */

// Spring physics simulation for organic motion
class SpringValue {
    constructor(initial, stiffness = 0.1, damping = 0.8) {
        this.current = initial
        this.target = initial
        this.velocity = 0
        this.stiffness = stiffness
        this.damping = damping
    }

    update() {
        // Hooke's law: F = -kx
        this.velocity += (this.target - this.current) * this.stiffness
        this.velocity *= this.damping
        this.current += this.velocity

        // Settle threshold to stop micro-oscillations
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
    constructor(container, options = {}) {
        // Validation
        if (!container || !(container instanceof HTMLElement)) {
            throw new Error('LiquidGlassFAB: First argument must be a valid HTMLElement')
        }

        // Configuration
        this.container = container
        this.options = {
            size: options.size || 80,
            mode: options.mode || 'embedded',
            position: options.position || null,
            icon: options.icon || this.getDefaultIcon(),
            ariaLabel: options.ariaLabel || 'Toggle',
            onToggle: options.onToggle || null,
            playEntranceAnimation: options.playEntranceAnimation !== false
        }

        // State
        this.isOpen = false
        this.isDestroyed = false
        this.isHovering = false
        this.animationFrame = null

        // Strict Timer Registry (Set for O(1) operations)
        this.timers = new Set()

        // Shadow DOM references
        this.host = null
        this.shadowRoot = null
        this.fab = null

        // Initialize
        this.createShadowDOM()
        this.initPhysics()
        this.initEventListeners()
        this.startAnimationLoop()

        if (this.options.playEntranceAnimation) {
            this.playEntranceAnimation()
        }
    }

    getDefaultIcon() {
        return `
            <svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
        `
    }

    /**
     * Strict Timer Registry - wraps setTimeout with automatic tracking
     * SECURITY: Delete timerId BEFORE callback to prevent registry leak on exception
     */
    setTimer(callback, delay) {
        const timerId = setTimeout(() => {
            // Remove from registry FIRST (before callback can throw)
            this.timers.delete(timerId)

            // Only execute if not destroyed
            if (!this.isDestroyed) {
                callback()
            }
        }, delay)

        this.timers.add(timerId)
        return timerId
    }

    /**
     * Create Shadow DOM with isolated styles
     */
    createShadowDOM() {
        // Create host element
        this.host = document.createElement('liquid-glass-fab')

        // Apply mode-specific positioning
        if (this.options.mode === 'global') {
            // Portal Pattern: render directly in document.body
            this.host.style.position = 'fixed'
            this.host.style.zIndex = '9999'

            // Apply position from options
            if (this.options.position) {
                Object.entries(this.options.position).forEach(([key, value]) => {
                    this.host.style[key] = value
                })
            } else {
                // Default global position
                this.host.style.bottom = '24px'
                this.host.style.right = '24px'
            }

            document.body.appendChild(this.host)
        } else {
            // Embedded mode: render in provided container
            this.host.style.position = 'relative'
            this.host.style.display = 'inline-block'
            this.container.appendChild(this.host)
        }

        // Create Shadow Root (closed for complete isolation)
        this.shadowRoot = this.host.attachShadow({ mode: 'closed' })

        // Inject styles into Shadow DOM
        const styleSheet = document.createElement('style')
        styleSheet.textContent = this.getShadowStyles()
        this.shadowRoot.appendChild(styleSheet)

        // Create button structure
        this.fab = document.createElement('button')
        this.fab.className = 'liquid-glass-fab'
        this.fab.setAttribute('aria-label', this.options.ariaLabel)
        this.fab.setAttribute('type', 'button')

        // Set size
        this.fab.style.width = `${this.options.size}px`
        this.fab.style.height = `${this.options.size}px`

        // Icon container
        const iconContainer = document.createElement('div')
        iconContainer.className = 'liquid-glass-fab__icon'
        iconContainer.innerHTML = this.options.icon

        this.fab.appendChild(iconContainer)
        this.shadowRoot.appendChild(this.fab)
    }

    /**
     * Get CSS for Shadow DOM (isolated from global styles)
     */
    getShadowStyles() {
        return `
            /* Shadow DOM isolated styles */
            :host {
                display: inline-block;
                contain: layout style paint;
            }

            .liquid-glass-fab {
                /* Layout */
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
                border: none;
                padding: 0;
                cursor: pointer;
                overflow: visible;

                /* Shape - dynamic via CSS variables */
                border-radius:
                    var(--radius-tl, 50%) var(--radius-tr, 50%)
                    var(--radius-br, 50%) var(--radius-bl, 50%) /
                    var(--radius-tl-v, 50%) var(--radius-tr-v, 50%)
                    var(--radius-br-v, 50%) var(--radius-bl-v, 50%);

                /* Transform */
                transform:
                    translate(var(--translateX, 0), var(--translateY, 0))
                    scale(var(--scale, 1));

                /* Transitions */
                transition:
                    border-radius 0.05s ease-out,
                    box-shadow 0.3s ease;

                /* Performance */
                will-change: transform, border-radius;

                /* Accessibility */
                -webkit-tap-highlight-color: transparent;
                user-select: none;
                -webkit-user-select: none;

                /* Glass morphism base - CANON */
                background: rgba(100, 116, 139, 0.4);
                backdrop-filter: blur(28px) saturate(160%) brightness(1.05);
                -webkit-backdrop-filter: blur(28px) saturate(160%) brightness(1.05);

                /* Layered glass effect */
                box-shadow:
                    0 0 0 1px rgba(255, 255, 255, 0.1),
                    0 8px 32px rgba(0, 0, 0, 0.2),
                    inset 0 1px 2px rgba(255, 255, 255, 0.15),
                    inset 0 -1px 2px rgba(0, 0, 0, 0.1);
            }

            /* Cursor-following light layer */
            .liquid-glass-fab::before {
                content: '';
                position: absolute;
                inset: 0;
                border-radius: inherit;
                background: radial-gradient(
                    circle at var(--light-x, 35%) var(--light-y, 35%),
                    rgba(255, 255, 255, 0.25) 0%,
                    rgba(255, 255, 255, 0.08) 30%,
                    rgba(255, 255, 255, 0) 60%
                );
                opacity: 0;
                transition: opacity 0.3s ease;
                pointer-events: none;
            }

            .liquid-glass-fab:hover::before {
                opacity: 1;
            }

            /* Specular highlight layer */
            .liquid-glass-fab::after {
                content: '';
                position: absolute;
                top: calc(10% + var(--shine-y, 0));
                left: calc(20% + var(--shine-x, 0));
                width: 40%;
                height: 30%;
                border-radius: 50%;
                background: radial-gradient(
                    ellipse at center,
                    rgba(255, 255, 255, 0.4) 0%,
                    rgba(255, 255, 255, 0.2) 40%,
                    transparent 70%
                );
                filter: blur(8px);
                opacity: 0;
                transition: opacity 0.4s ease;
                pointer-events: none;
                mix-blend-mode: overlay;
            }

            .liquid-glass-fab:hover::after {
                opacity: 1;
            }

            /* Icon container */
            .liquid-glass-fab__icon {
                position: relative;
                width: 50%;
                height: 50%;
                color: white;
                transform: translate(
                    var(--parallax-x, 0),
                    var(--parallax-y, 0)
                );
                transition: transform 0.1s ease-out;
                pointer-events: none;
                z-index: 2;
            }

            .liquid-glass-fab__icon svg {
                width: 100%;
                height: 100%;
                display: block;
                filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
            }

            /* Ripple effect */
            .liquid-glass-fab__ripple {
                position: absolute;
                width: 20px;
                height: 20px;
                border-radius: 50%;
                background: radial-gradient(
                    circle,
                    rgba(255, 255, 255, 0.6) 0%,
                    rgba(255, 255, 255, 0.3) 50%,
                    transparent 100%
                );
                transform: translate(-50%, -50%) scale(0);
                animation: liquid-glass-fab-ripple 0.8s ease-out forwards;
                pointer-events: none;
                z-index: 1;
            }

            @keyframes liquid-glass-fab-ripple {
                0% {
                    transform: translate(-50%, -50%) scale(0);
                    opacity: 1;
                }
                100% {
                    transform: translate(-50%, -50%) scale(4);
                    opacity: 0;
                }
            }

            /* Water drop entrance animation */
            .liquid-glass-fab--drop-entrance {
                animation: liquid-glass-fab-drop-entrance 1.6s cubic-bezier(0.34, 1.56, 0.64, 1);
            }

            @keyframes liquid-glass-fab-drop-entrance {
                0% {
                    transform: translateY(-200px) scale(0.3);
                    opacity: 0;
                    border-radius: 50%;
                }
                40% {
                    transform: translateY(0) scale(1.1);
                    opacity: 1;
                    border-radius: 50% 50% 50% 50% / 50% 50% 50% 50%;
                }
                50% {
                    border-radius: 48% 52% 50% 50% / 42% 42% 58% 58%;
                }
                65% {
                    border-radius: 52% 48% 50% 50% / 55% 55% 45% 45%;
                    transform: translateY(0) scale(0.95);
                }
                75% {
                    border-radius: 49% 51% 51% 49% / 51% 49% 51% 49%;
                    transform: translateY(0) scale(1.02);
                }
                85% {
                    border-radius: 50.5% 49.5% 49.5% 50.5% / 49.5% 50.5% 49.5% 50.5%;
                    transform: translateY(0) scale(0.99);
                }
                100% {
                    transform: translateY(0) scale(1);
                    border-radius: 50%;
                }
            }

            /* Focus state */
            .liquid-glass-fab:focus-visible {
                outline: 2px solid rgba(255, 255, 255, 0.6);
                outline-offset: 4px;
            }

            /* Active state */
            .liquid-glass-fab:active {
                box-shadow:
                    0 0 0 1px rgba(255, 255, 255, 0.1),
                    0 4px 16px rgba(0, 0, 0, 0.3),
                    inset 0 2px 4px rgba(0, 0, 0, 0.2);
            }

            /* Dark theme support */
            @media (prefers-color-scheme: dark) {
                .liquid-glass-fab {
                    background: rgba(100, 116, 139, 0.5);
                    box-shadow:
                        0 0 0 1px rgba(255, 255, 255, 0.15),
                        0 8px 32px rgba(0, 0, 0, 0.4),
                        inset 0 1px 2px rgba(255, 255, 255, 0.2),
                        inset 0 -1px 2px rgba(0, 0, 0, 0.2);
                }
            }

            /* Light theme support */
            @media (prefers-color-scheme: light) {
                .liquid-glass-fab {
                    background: rgba(120, 136, 159, 0.35);
                    box-shadow:
                        0 0 0 1px rgba(255, 255, 255, 0.2),
                        0 8px 32px rgba(0, 0, 0, 0.15),
                        inset 0 1px 2px rgba(255, 255, 255, 0.25),
                        inset 0 -1px 2px rgba(0, 0, 0, 0.08);
                }
            }

            /* Reduced motion support */
            @media (prefers-reduced-motion: reduce) {
                .liquid-glass-fab,
                .liquid-glass-fab::before,
                .liquid-glass-fab::after,
                .liquid-glass-fab__icon {
                    transition: none !important;
                    animation: none !important;
                }

                .liquid-glass-fab--drop-entrance {
                    animation: none !important;
                    opacity: 1 !important;
                    transform: none !important;
                }
            }
        `
    }

    initPhysics() {
        // Light caustics (cursor-following effect)
        this.lightX = new SpringValue(35, 0.08, 0.82)
        this.lightY = new SpringValue(35, 0.08, 0.82)

        // Scale for hover/click effects
        this.scale = new SpringValue(1.0, 0.15, 0.75)

        // Shine offset (surface reflection)
        this.shineX = new SpringValue(0, 0.06, 0.85)
        this.shineY = new SpringValue(0, 0.06, 0.85)

        // 8-corner morphing (border-radius manipulation)
        this.morphTL = new SpringValue(50, 0.14, 0.78)
        this.morphTR = new SpringValue(50, 0.14, 0.78)
        this.morphBR = new SpringValue(50, 0.14, 0.78)
        this.morphBL = new SpringValue(50, 0.14, 0.78)
        this.morphTLV = new SpringValue(50, 0.14, 0.78)
        this.morphTRV = new SpringValue(50, 0.14, 0.78)
        this.morphBRV = new SpringValue(50, 0.14, 0.78)
        this.morphBLV = new SpringValue(50, 0.14, 0.78)

        // Position offset
        this.translateX = new SpringValue(0, 0.08, 0.84)
        this.translateY = new SpringValue(0, 0.08, 0.84)

        // Icon parallax
        this.parallaxX = new SpringValue(0, 0.10, 0.88)
        this.parallaxY = new SpringValue(0, 0.10, 0.88)
    }

    initEventListeners() {
        // Store bound functions for proper cleanup
        this.onEnterBound = this.onEnter.bind(this)
        this.onLeaveBound = this.onLeave.bind(this)
        this.onMoveBound = this.onMove.bind(this)
        this.onClickBound = this.onClick.bind(this)

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

        // Reset light to center
        this.lightX.set(35)
        this.lightY.set(35)

        // Reset scale
        this.scale.set(1.0)

        // Reset shine
        this.shineX.set(0)
        this.shineY.set(0)

        // Reset morphing to perfect circle
        this.morphTL.set(50)
        this.morphTR.set(50)
        this.morphBR.set(50)
        this.morphBL.set(50)
        this.morphTLV.set(50)
        this.morphTRV.set(50)
        this.morphBRV.set(50)
        this.morphBLV.set(50)

        // Reset position
        this.translateX.set(0)
        this.translateY.set(0)

        // Reset icon parallax
        this.parallaxX.set(0)
        this.parallaxY.set(0)
    }

    onMove(e) {
        if (!this.isHovering) return

        const rect = this.fab.getBoundingClientRect()
        const x = e.clientX - rect.left
        const y = e.clientY - rect.top

        // Normalized coordinates (0-100 range)
        const normX = (x / rect.width) * 100
        const normY = (y / rect.height) * 100

        // Update light position (caustics follow cursor)
        this.lightX.set(normX)
        this.lightY.set(normY)

        // PROPORTIONAL PHYSICS: Shine effect scales with button size
        const shineOffsetX = ((normX - 50) / 100) * this.options.size * 0.15
        const shineOffsetY = ((normY - 50) / 100) * this.options.size * 0.15
        this.shineX.set(shineOffsetX)
        this.shineY.set(shineOffsetY)

        // PROPORTIONAL PHYSICS: Icon parallax scales with button size
        const parallaxX = ((normX - 50) / 100) * this.options.size * 0.12
        const parallaxY = ((normY - 50) / 100) * this.options.size * 0.12
        this.parallaxX.set(parallaxX)
        this.parallaxY.set(parallaxY)

        // 8-corner morphing based on cursor quadrant
        // PROPORTIONAL PHYSICS: Deformation scales with button size
        const centerX = rect.width / 2
        const centerY = rect.height / 2
        const distance = Math.hypot(x - centerX, y - centerY) / centerX
        const deformCoefficient = this.options.size * 0.4375  // 35/80 for 80px baseline
        const deformMax = this.options.size * 0.5625  // 45/80 for 80px baseline
        const deformAmount = Math.min(distance * deformCoefficient, deformMax)

        // Determine quadrant and apply asymmetric morphing
        if (normX < 50 && normY < 50) {
            // Top-left quadrant
            this.morphTL.set(50 + deformAmount * 0.4)
            this.morphTLV.set(50 + deformAmount * 0.3)
            this.morphBR.set(50 - deformAmount * 0.3)
            this.morphBRV.set(50 - deformAmount * 0.2)
            this.morphTR.set(50 + deformAmount * 0.2)
            this.morphBL.set(50 + deformAmount * 0.2)
            this.morphTRV.set(50)
            this.morphBLV.set(50)
        } else if (normX >= 50 && normY < 50) {
            // Top-right quadrant
            this.morphTR.set(50 + deformAmount * 0.4)
            this.morphTRV.set(50 + deformAmount * 0.3)
            this.morphBL.set(50 - deformAmount * 0.3)
            this.morphBLV.set(50 - deformAmount * 0.2)
            this.morphTL.set(50 + deformAmount * 0.2)
            this.morphBR.set(50 + deformAmount * 0.2)
            this.morphTLV.set(50)
            this.morphBRV.set(50)
        } else if (normX >= 50 && normY >= 50) {
            // Bottom-right quadrant
            this.morphBR.set(50 + deformAmount * 0.4)
            this.morphBRV.set(50 + deformAmount * 0.3)
            this.morphTL.set(50 - deformAmount * 0.3)
            this.morphTLV.set(50 - deformAmount * 0.2)
            this.morphBL.set(50 + deformAmount * 0.2)
            this.morphTR.set(50 + deformAmount * 0.2)
            this.morphBLV.set(50)
            this.morphTRV.set(50)
        } else {
            // Bottom-left quadrant
            this.morphBL.set(50 + deformAmount * 0.4)
            this.morphBLV.set(50 + deformAmount * 0.3)
            this.morphTR.set(50 - deformAmount * 0.3)
            this.morphTRV.set(50 - deformAmount * 0.2)
            this.morphTL.set(50 + deformAmount * 0.2)
            this.morphBR.set(50 + deformAmount * 0.2)
            this.morphTLV.set(50)
            this.morphBRV.set(50)
        }
    }

    onClick(e) {
        // Squash effect (press down) - using Strict Timer Registry
        this.scale.set(0.96)
        this.setTimer(() => {
            this.scale.set(this.isHovering ? 1.1 : 1.0)
        }, 150)

        // Ripple effect
        this.createRipple(e)

        // Toggle state
        this.isOpen = !this.isOpen

        // Callback
        if (this.options.onToggle) {
            this.options.onToggle(this.isOpen)
        }
    }

    createRipple(e) {
        const ripple = document.createElement('div')
        ripple.className = 'liquid-glass-fab__ripple'

        const rect = this.fab.getBoundingClientRect()
        const x = e.clientX - rect.left
        const y = e.clientY - rect.top

        ripple.style.left = `${x}px`
        ripple.style.top = `${y}px`

        this.fab.appendChild(ripple)

        // Auto-remove after animation - using Strict Timer Registry
        this.setTimer(() => {
            if (ripple.parentNode) {
                ripple.remove()
            }
        }, 800)
    }

    startAnimationLoop() {
        const animate = () => {
            if (this.isDestroyed) return

            // Update all spring physics
            this.lightX.update()
            this.lightY.update()
            this.scale.update()
            this.shineX.update()
            this.shineY.update()
            this.morphTL.update()
            this.morphTR.update()
            this.morphBR.update()
            this.morphBL.update()
            this.morphTLV.update()
            this.morphTRV.update()
            this.morphBRV.update()
            this.morphBLV.update()
            this.translateX.update()
            this.translateY.update()
            this.parallaxX.update()
            this.parallaxY.update()

            // Apply physics values to CSS custom properties
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

            // Schedule next frame
            this.animationFrame = requestAnimationFrame(animate)
        }

        animate()
    }

    playEntranceAnimation() {
        this.fab.classList.add('liquid-glass-fab--drop-entrance')

        // Using Strict Timer Registry
        this.setTimer(() => {
            this.fab.classList.remove('liquid-glass-fab--drop-entrance')
        }, 1600)
    }

    /**
     * Update button state
     * @param {boolean} isOpen - New state
     */
    setState(isOpen) {
        this.isOpen = isOpen
    }

    /**
     * Get current state
     * @returns {boolean}
     */
    getState() {
        return this.isOpen
    }

    /**
     * Get timer count (for debugging)
     * @returns {number}
     */
    getActiveTimerCount() {
        return this.timers.size
    }

    /**
     * Clean up and remove the button
     * Stops animation loop, clears all timers, removes event listeners, and removes DOM
     */
    destroy() {
        // Mark as destroyed to stop animation loop
        this.isDestroyed = true

        // Cancel animation frame
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame)
            this.animationFrame = null
        }

        // STRICT TIMER CLEANUP: Clear all pending timers
        this.timers.forEach(timerId => clearTimeout(timerId))
        this.timers.clear()

        // Log for verification
        console.log('[LiquidGlassFAB] destroy() executed - Active timers after cleanup:', this.timers.size)

        // Remove event listeners
        if (this.fab) {
            this.fab.removeEventListener('pointerenter', this.onEnterBound)
            this.fab.removeEventListener('pointerleave', this.onLeaveBound)
            this.fab.removeEventListener('pointermove', this.onMoveBound)
            this.fab.removeEventListener('click', this.onClickBound)
        }

        // Remove host element (Shadow DOM is removed automatically)
        if (this.host && this.host.parentNode) {
            this.host.remove()
        }

        // Clear references for garbage collection
        this.fab = null
        this.shadowRoot = null
        this.host = null
        this.container = null
        this.options = null
    }
}
