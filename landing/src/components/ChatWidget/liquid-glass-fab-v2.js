// Apple-grade Liquid Glass FAB
// SDF displacement, chromatic aberration, physical bezel, specular rim

class SpringValue {
    constructor(initial, stiffness, damping) {
        this.current = initial
        this.target = initial
        this.velocity = 0
        this.stiffness = stiffness
        this.damping = damping
    }

    set(target) {
        this.target = target
    }

    update() {
        const delta = this.target - this.current
        const springForce = delta * this.stiffness
        const dampingForce = this.velocity * this.damping

        this.velocity += springForce - dampingForce
        this.current += this.velocity

        if (Math.abs(this.velocity) < 0.001 && Math.abs(delta) < 0.001) {
            this.current = this.target
            this.velocity = 0
        }
    }
}

export class LiquidGlassFAB {
    constructor(container, onToggle) {
        this.container = container
        this.onToggle = onToggle
        this.isOpen = false
        this.isDestroyed = false

        // Create structure
        this.createElements()
        this.createSVGFilter()

        // Initialize physics
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

        // FAB button with layers
        this.fab = document.createElement('button')
        this.fab.className = 'liquid-fab'
        this.fab.setAttribute('aria-label', 'Toggle chat')

        // Bezel layer (outer rim)
        const bezel = document.createElement('div')
        bezel.className = 'liquid-fab-bezel'

        // Glass surface
        const glass = document.createElement('div')
        glass.className = 'liquid-fab-glass'

        // Specular highlight
        const specular = document.createElement('div')
        specular.className = 'liquid-fab-specular'

        // Caustic glow
        const caustic = document.createElement('div')
        caustic.className = 'liquid-fab-caustic'

        // Icon with parallax
        const icon = document.createElement('div')
        icon.className = 'liquid-fab-icon-wrapper'
        icon.innerHTML = `
            <svg class="chat-icon" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
        `

        this.fab.appendChild(bezel)
        this.fab.appendChild(glass)
        this.fab.appendChild(specular)
        this.fab.appendChild(caustic)
        this.fab.appendChild(icon)

        this.wrapper.appendChild(this.fab)
        this.container.appendChild(this.wrapper)

        // Store references
        this.bezel = bezel
        this.glass = glass
        this.specular = specular
        this.caustic = caustic
        this.iconWrapper = icon
    }

    createSVGFilter() {
        // Create SVG with advanced displacement map
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
        svg.setAttribute('width', '0')
        svg.setAttribute('height', '0')
        svg.setAttribute('style', 'position: absolute;')

        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs')

        // Main filter with chromatic aberration
        const filter = document.createElementNS('http://www.w3.org/2000/svg', 'filter')
        filter.setAttribute('id', 'liquid-glass-refraction')
        filter.setAttribute('x', '-50%')
        filter.setAttribute('y', '-50%')
        filter.setAttribute('width', '200%')
        filter.setAttribute('height', '200%')
        filter.setAttribute('color-interpolation-filters', 'sRGB')

        // SDF-based displacement map (neutral center, strong edges)
        const turbulence = `
            <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="1" result="noise" seed="1"/>
            <feColorMatrix in="noise" type="matrix"
                values="1 0 0 0 0
                        0 1 0 0 0
                        0 0 1 0 0
                        0 0 0 12 -6" result="noise2"/>

            <!-- SDF circle gradient -->
            <feGaussianBlur in="SourceAlpha" stdDeviation="8" result="blur"/>
            <feColorMatrix in="blur" type="matrix"
                values="0 0 0 0 0.5
                        0 0 0 0 0.5
                        0 0 0 0 0
                        0 0 0 1 0" result="sdf"/>

            <feComposite in="sdf" in2="noise2" operator="arithmetic" k1="0" k2="1" k3="0.15" k4="0" result="displacement-map"/>

            <!-- Red channel (less displacement) -->
            <feDisplacementMap in="SourceGraphic" in2="displacement-map"
                scale="-32" xChannelSelector="R" yChannelSelector="G" result="r"/>
            <feColorMatrix in="r" type="matrix"
                values="1 0 0 0 0
                        0 0 0 0 0
                        0 0 0 0 0
                        0 0 0 1 0" result="red-only"/>

            <!-- Green channel (medium displacement) -->
            <feDisplacementMap in="SourceGraphic" in2="displacement-map"
                scale="-36" xChannelSelector="R" yChannelSelector="G" result="g"/>
            <feColorMatrix in="g" type="matrix"
                values="0 0 0 0 0
                        0 1 0 0 0
                        0 0 0 0 0
                        0 0 0 1 0" result="green-only"/>

            <!-- Blue channel (most displacement) -->
            <feDisplacementMap in="SourceGraphic" in2="displacement-map"
                scale="-40" xChannelSelector="R" yChannelSelector="G" result="b"/>
            <feColorMatrix in="b" type="matrix"
                values="0 0 0 0 0
                        0 0 0 0 0
                        0 0 1 0 0
                        0 0 0 1 0" result="blue-only"/>

            <!-- Combine RGB channels -->
            <feBlend in="red-only" in2="green-only" mode="screen" result="rg"/>
            <feBlend in="rg" in2="blue-only" mode="screen" result="final"/>
        `

        filter.innerHTML = turbulence
        defs.appendChild(filter)
        svg.appendChild(defs)

        document.body.appendChild(svg)
        this.svgFilter = svg
    }

    initPhysics() {
        // Smooth spring physics for organic motion with more bounce
        this.scale = new SpringValue(1.0, 0.16, 0.65)

        // Droplet morphing - squash and stretch for liquid feel
        this.squashX = new SpringValue(1.0, 0.14, 0.68)
        this.squashY = new SpringValue(1.0, 0.14, 0.68)

        // Specular highlight position (softer spring for gentle oscillation)
        this.specularX = new SpringValue(50, 0.12, 0.7)
        this.specularY = new SpringValue(30, 0.12, 0.7)

        // Caustic glow position (even softer for liquid feel)
        this.causticX = new SpringValue(50, 0.1, 0.75)
        this.causticY = new SpringValue(70, 0.1, 0.75)

        // Icon parallax (gentle bounce)
        this.parallaxX = new SpringValue(0, 0.11, 0.72)
        this.parallaxY = new SpringValue(0, 0.11, 0.72)

        // Lens center bias (very soft, droplet-like)
        this.lensX = new SpringValue(50, 0.08, 0.8)
        this.lensY = new SpringValue(50, 0.08, 0.8)

        this.isHovering = false
        this.pointerX = 0
        this.pointerY = 0
        this.pendingUpdate = false
    }

    initEventListeners() {
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
        this.scale.set(1.08)
    }

    onLeave() {
        this.isHovering = false
        this.pendingUpdate = false

        // Smooth return to center with gentle oscillation
        // Using requestAnimationFrame to ensure smooth reset even if pointer leaves abruptly
        requestAnimationFrame(() => {
            this.specularX.set(50)
            this.specularY.set(30)
            this.causticX.set(50)
            this.causticY.set(70)
            this.parallaxX.set(0)
            this.parallaxY.set(0)
            this.lensX.set(50)
            this.lensY.set(50)
            this.scale.set(1.0)
            this.squashX.set(1.0)
            this.squashY.set(1.0)
        })
    }

    onMove(e) {
        // Only mouse, not touch
        if (e.pointerType !== 'mouse') return
        if (!this.isHovering) return

        this.pointerX = e.clientX
        this.pointerY = e.clientY

        // Request update on next frame
        if (!this.pendingUpdate) {
            this.pendingUpdate = true
        }
    }

    updatePointerEffects() {
        if (!this.isHovering || !this.pendingUpdate) return

        const rect = this.fab.getBoundingClientRect()
        const centerX = rect.width / 2
        const centerY = rect.height / 2

        const x = this.pointerX - rect.left
        const y = this.pointerY - rect.top

        // Distance from center
        let dx = x - centerX
        let dy = y - centerY
        const distance = Math.sqrt(dx * dx + dy * dy)
        const maxRadius = Math.min(rect.width, rect.height) / 2

        // Clamp to circular boundary (not square) for natural droplet movement
        if (distance > maxRadius) {
            const angle = Math.atan2(dy, dx)
            dx = Math.cos(angle) * maxRadius
            dy = Math.sin(angle) * maxRadius
        }

        // Constrained position relative to center
        const constrainedX = centerX + dx
        const constrainedY = centerY + dy

        // Normalized 0-100 with circular constraint
        const normX = (constrainedX / rect.width) * 100
        const normY = (constrainedY / rect.height) * 100

        // Droplet squash & stretch based on movement direction
        // When moving right/left, stretch horizontally and compress vertically
        // When moving up/down, compress horizontally and stretch vertically
        const normalizedDx = dx / maxRadius // -1 to 1
        const normalizedDy = dy / maxRadius // -1 to 1

        // Squash amount increases with distance from center
        const squashAmount = Math.min(distance / maxRadius, 1) * 0.15

        // Direction-based morphing for liquid droplet effect
        this.squashX.set(1.0 + Math.abs(normalizedDx) * squashAmount)
        this.squashY.set(1.0 + Math.abs(normalizedDy) * squashAmount)

        // Icon parallax (subtle, droplet interior moves)
        this.parallaxX.set(dx * 0.12)
        this.parallaxY.set(dy * 0.12)

        // Specular highlight (follows pointer smoothly within circle)
        this.specularX.set(normX)
        this.specularY.set(normY)

        // Caustic glow (opposite direction for depth)
        this.causticX.set(100 - normX)
        this.causticY.set(100 - normY)

        // Lens center bias (very subtle droplet distortion)
        this.lensX.set(50 + dx * 0.04)
        this.lensY.set(50 + dy * 0.04)

        this.pendingUpdate = false
    }

    onClick(e) {
        // Only handle actual clicks, not pointer events
        if (e.pointerType === 'mouse' || e.type === 'click') {
            // Press animation
            this.scale.set(0.94)

            // Spring back with overshoot
            setTimeout(() => {
                this.scale.set(1.025)
                setTimeout(() => {
                    this.scale.set(this.isHovering ? 1.08 : 1.0)
                }, 150)
            }, 100)

            // Ripple effect
            this.createRipple(e)

            // Call toggle
            if (this.onToggle) {
                this.onToggle()
            }

            console.log('FAB clicked!')
        }
    }

    createRipple(e) {
        const ripple = document.createElement('div')
        ripple.className = 'liquid-fab-ripple'

        const rect = this.fab.getBoundingClientRect()
        const size = Math.max(rect.width, rect.height) * 2
        const x = e.clientX - rect.left - size / 2
        const y = e.clientY - rect.top - size / 2

        ripple.style.width = `${size}px`
        ripple.style.height = `${size}px`
        ripple.style.left = `${x}px`
        ripple.style.top = `${y}px`

        this.fab.appendChild(ripple)

        setTimeout(() => ripple.remove(), 600)
    }

    startAnimationLoop() {
        this.isDestroyed = false

        const animate = () => {
            if (this.isDestroyed) return

            // Update pointer effects
            this.updatePointerEffects()

            // Update all springs
            this.scale.update()
            this.squashX.update()
            this.squashY.update()
            this.specularX.update()
            this.specularY.update()
            this.causticX.update()
            this.causticY.update()
            this.parallaxX.update()
            this.parallaxY.update()
            this.lensX.update()
            this.lensY.update()

            // Apply to CSS with droplet morphing
            const scaleTransform = `scale(${this.scale.current * this.squashX.current}, ${this.scale.current * this.squashY.current})`
            this.fab.style.transform = scaleTransform

            this.specular.style.setProperty('--x', `${this.specularX.current}%`)
            this.specular.style.setProperty('--y', `${this.specularY.current}%`)

            this.caustic.style.setProperty('--x', `${this.causticX.current}%`)
            this.caustic.style.setProperty('--y', `${this.causticY.current}%`)

            this.iconWrapper.style.transform =
                `translate(${this.parallaxX.current}px, ${this.parallaxY.current}px)`

            this.glass.style.setProperty('--lens-x', `${this.lensX.current}%`)
            this.glass.style.setProperty('--lens-y', `${this.lensY.current}%`)

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
    }

    destroy() {
        this.isDestroyed = true

        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame)
        }

        if (this.fab && this.onEnterBound) {
            this.fab.removeEventListener('pointerenter', this.onEnterBound)
            this.fab.removeEventListener('pointerleave', this.onLeaveBound)
            this.fab.removeEventListener('pointermove', this.onMoveBound)
            this.fab.removeEventListener('click', this.onClickBound)
        }

        if (this.svgFilter && this.svgFilter.parentNode) {
            this.svgFilter.remove()
        }

        if (this.wrapper && this.wrapper.parentNode) {
            this.wrapper.remove()
        }
    }
}
