# API Reference - Configuration Options Contract

## Configuration Options - Complete Contract

### `options.size`

**Type:** `number`  
**Default:** `80`  
**Valid Range:** `40` - `200`  
**Unit:** pixels (CSS px)

**Description:** Button diameter in pixels. All physics effects scale proportionally to this value.

**Validation:**
- Values below 40px may cause icon readability issues
- Values above 200px may impact performance (larger RAF calculations)
- Non-integer values are accepted and rendered accurately

**Examples:**
```javascript
new LiquidGlassFAB(container, { size: 60 });   // Small (mobile)
new LiquidGlassFAB(container, { size: 80 });   // Standard (default)
new LiquidGlassFAB(container, { size: 120 });  // Large (desktop)
new LiquidGlassFAB(container, { size: 160 });  // Extra large (hero)
```

**Scaling behavior:**
- Spring physics remain constant (stiffness/damping unchanged)
- Morphing deformation is relative to button size
- Light caustics position calculated as percentage
- Icon scales to 50% of button size automatically

---

### `options.icon`

**Type:** `string` (SVG markup)  
**Default:** Built-in chat bubble icon  
**Valid Format:** Complete SVG element string with viewBox

**Description:** Custom SVG icon rendered inside the button.

**Requirements:**
- Must be valid SVG markup
- Should include `viewBox` attribute for proper scaling
- Use `currentColor` or `fill="currentColor"` for theme compatibility
- Icon container automatically sized to 50% of button diameter

**Examples:**
```javascript
// Heart icon
const heartIcon = `
    <svg viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
    </svg>
`;

new LiquidGlassFAB(container, { icon: heartIcon });
```

**Default icon (internal):**
```javascript
getDefaultIcon() {
    return `
        <svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
    `;
}
```

---

### `options.ariaLabel`

**Type:** `string`  
**Default:** `'Toggle'`  
**Valid Range:** 1-100 characters  

**Description:** Accessibility label for screen readers. Sets the `aria-label` attribute on the button element.

**Best practices:**
- Use descriptive action verbs: "Open chat", "Show menu", "Toggle notifications"
- Keep under 50 characters for screen reader compatibility
- Avoid generic labels like "Button" or "Click here"

**Examples:**
```javascript
new LiquidGlassFAB(container, { ariaLabel: 'Open support chat' });
new LiquidGlassFAB(container, { ariaLabel: 'Toggle notifications panel' });
new LiquidGlassFAB(container, { ariaLabel: 'Show quick actions menu' });
```

---

### `options.onToggle`

**Type:** `function | null`  
**Default:** `null`  
**Signature:** `(isOpen: boolean) => void`

**Description:** Callback function invoked when the button is clicked. Receives the new toggle state.

**Parameters:**
- `isOpen` (boolean): Current state after toggle. Toggles on each click: `false → true → false → ...`

**Behavior:**
- Called AFTER internal state update
- Called synchronously during click event
- Does NOT fire when `setState()` is called programmatically

**Examples:**
```javascript
// Simple logging
new LiquidGlassFAB(container, {
    onToggle: (isOpen) => {
        console.log('State:', isOpen ? 'OPEN' : 'CLOSED');
    }
});

// Widget integration
new LiquidGlassFAB(container, {
    onToggle: (isOpen) => {
        const widget = document.getElementById('chat-widget');
        if (isOpen) {
            widget.classList.add('visible');
            widget.focus();
        } else {
            widget.classList.remove('visible');
        }
    }
});

// Analytics tracking
new LiquidGlassFAB(container, {
    onToggle: (isOpen) => {
        gtag('event', 'fab_toggle', {
            state: isOpen ? 'open' : 'close',
            timestamp: Date.now()
        });
    }
});
```

---

### `options.playEntranceAnimation`

**Type:** `boolean`  
**Default:** `true`

**Description:** Controls whether the water drop entrance animation plays when the button is first rendered.

**Animation details:**
- Duration: 1.6 seconds
- Easing: `cubic-bezier(0.34, 1.56, 0.64, 1)` (bounce)
- Effect: Drop from top with squash/wobble physics

**When to disable:**
- Button appears after user scroll (avoid distraction)
- Multiple buttons created dynamically (performance)
- Button recreated during user session (avoid repetition)
- Reduced motion preference (handled automatically by CSS)

**Examples:**
```javascript
// First visit - play animation
const isFirstVisit = !localStorage.getItem('visited');
new LiquidGlassFAB(container, {
    playEntranceAnimation: isFirstVisit
});
if (isFirstVisit) localStorage.setItem('visited', 'true');

// Dynamic creation - skip animation
document.getElementById('add-fab').addEventListener('click', () => {
    const fab = new LiquidGlassFAB(container, {
        playEntranceAnimation: false
    });
});
```

---

### `options.mode`

**Type:** `string`  
**Default:** `'embedded'`  
**Valid Values:** `'embedded'` | `'global'`

**Description:** Controls the rendering context for the button (v1.2+ Shadow DOM architecture).

**Modes:**

- **`'embedded'` (default):** Button renders inside the provided `container` element with relative positioning. Use this for buttons that should be part of the document flow or positioned within a specific container.

- **`'global'`:** Button renders directly to `document.body` with fixed positioning (Portal Pattern). The host element is positioned independently of the container argument. Use this for floating action buttons that should escape hostile CSS contexts (e.g., containers with `overflow: hidden`).

**Examples:**
```javascript
// Embedded mode (default) - renders in container
const fab = new LiquidGlassFAB(container, {
    mode: 'embedded',
    size: 80
});

// Global mode - portal to document.body
const fabGlobal = new LiquidGlassFAB(document.body, {
    mode: 'global',
    position: { bottom: '24px', right: '24px' }
});
```

---

### `options.position`

**Type:** `object | null`  
**Default:** `null`  
**Valid Properties:** `{ top?, right?, bottom?, left? }` (CSS length values as strings)  
**Applicable Mode:** `'global'` only (ignored in `'embedded'` mode)

**Description:** Positioning for the button when `mode: 'global'`. Applies CSS positioning properties directly to the host element.

**Behavior:**
- Only used when `mode: 'global'`
- Ignored completely in `mode: 'embedded'` (use container positioning instead)
- If `null` in global mode, defaults to `{ bottom: '24px', right: '24px' }`
- Properties accept any CSS length values: `'24px'`, `'1rem'`, `'5%'`, etc.

**Examples:**
```javascript
// Default global position (bottom-right)
new LiquidGlassFAB(document.body, {
    mode: 'global'
    // position defaults to { bottom: '24px', right: '24px' }
});

// Custom global position (top-left)
new LiquidGlassFAB(document.body, {
    mode: 'global',
    position: { top: '32px', left: '32px' }
});

// Bottom-center
new LiquidGlassFAB(document.body, {
    mode: 'global',
    position: { bottom: '24px', left: '50%', transform: 'translateX(-50%)' }
});

// Embedded mode - position is ignored
new LiquidGlassFAB(container, {
    mode: 'embedded',
    position: { bottom: '24px' }  // ← IGNORED, use container CSS instead
});
```

**Important:** In `mode: 'embedded'`, positioning is handled by the container element, NOT this option.

---

## Position & Theme (NOT in options - handled externally)

### Position

**Handled by:** Container element positioning  
**Module does NOT provide:** Built-in positioning options

The module intentionally does NOT include `position`, `top`, `right`, `bottom`, `left` options. This is by design for maximum flexibility.

**Correct approach:**
```html
<div id="fab-container" style="position: fixed; right: 24px; bottom: 24px;">
    <!-- FAB renders here -->
</div>

<script type="module">
    const fab = new LiquidGlassFAB(document.getElementById('fab-container'), {
        size: 80
    });
</script>
```

**Why this approach:**
- Keeps module portable (can be placed anywhere)
- No conflicts with `transform: scale()` (positioning is on parent)
- Supports any positioning context (fixed, absolute, sticky, static)
- Allows CSS-based responsive positioning

---

### Theme

**Handled by:** CSS custom properties and media queries  
**Module does NOT provide:** `theme` or `color` options in v1.0.0

**Default theme:**
- Base color: `rgba(100, 116, 139, 0.4)` (gray glass)
- Icon color: `white`
- Auto-adapts to `prefers-color-scheme` media query

**Customization via CSS:**
```css
/* Override base color */
.liquid-glass-fab {
    background: rgba(59, 130, 246, 0.4) !important; /* Blue glass */
}

/* Override icon color */
.liquid-glass-fab__icon {
    color: #fbbf24 !important; /* Gold */
}

/* Dark theme override */
@media (prefers-color-scheme: dark) {
    .liquid-glass-fab {
        background: rgba(30, 41, 59, 0.6) !important;
    }
}
```

**Future API (not in v1.0.0):**
```javascript
// Planned for v2.0.0
new LiquidGlassFAB(container, {
    theme: {
        base: 'rgba(59, 130, 246, 0.4)',
        icon: '#fbbf24'
    }
});
```

---

## Options Summary Table

| Option | Type | Default | Range/Format | Required |
|--------|------|---------|--------------|----------|
| `size` | `number` | `80` | `40-200` px | No |
| `icon` | `string` | Chat bubble SVG | Valid SVG markup | No |
| `ariaLabel` | `string` | `'Toggle'` | 1-100 chars | No |
| `onToggle` | `function\|null` | `null` | `(isOpen) => void` | No |
| `playEntranceAnimation` | `boolean` | `true` | `true\|false` | No |
| `mode` | `string` | `'embedded'` | `'embedded'\|'global'` | No |
| `position` | `object\|null` | `null` | `{ top?, right?, bottom?, left? }` | No (global mode only) |

---

## NOT Supported (By Design)

The following are intentionally NOT included in v1.2 options:

| Feature | Why Not Included | Alternative |
|---------|------------------|-------------|
| `theme` / `color` | Violates frozen visual canon | Override CSS with `!important` (Shadow DOM piercing) |
| `disabled` | State management is external | Wrap in conditional render or add `disabled` attribute to button |
| `badge` / `notification` | Out of scope | Add sibling element in container |
| `tooltip` | Out of scope | Use native `title` attribute or tooltip library |

**Note on positioning:**
- `position` option is supported in v1.2+ for `mode: 'global'` only
- In `mode: 'embedded'` (default), positioning is handled by styling the container element

---

**Module:** Liquid Glass FAB  
**Version:** 1.2.1  
**Contract Status:** Frozen (no breaking changes in 1.x.x)
