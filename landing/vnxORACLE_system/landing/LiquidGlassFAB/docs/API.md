# API Reference

Complete API documentation for Liquid Glass FAB v1.0.0

## Table of Contents

- [Constructor](#constructor)
- [Configuration Options](#configuration-options)
- [Public Methods](#public-methods)
- [Spring Physics Parameters](#spring-physics-parameters)
- [CSS Custom Properties](#css-custom-properties)
- [Event Handling](#event-handling)
- [Examples](#examples)

---

## Constructor

### `new LiquidGlassFAB(container, options)`

Creates a new Liquid Glass FAB instance.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `container` | `HTMLElement` | Yes | DOM element to mount the button in (embedded mode) or validation anchor (global mode) |
| `options` | `Object` | No | Configuration options (see below) |

**Returns:** `LiquidGlassFAB` instance

**Throws:** `Error` if container is not a valid HTMLElement

**Important — Container behavior in Global mode:**

In `mode: 'global'`, the `container` argument is **required for API backward compatibility with v1.1**, but it is **validated and not used for mounting**. The component renders directly to `document.body` with fixed positioning (Portal Pattern). This preserves strict API compatibility while enabling the Portal escape hatch.

**Rationale:** Requiring `container` in both modes maintains a consistent API signature. Making it optional in global mode would be a breaking change for v1.x.

**Example:**
```javascript
// Embedded mode (default) - container is used for mounting
const container = document.getElementById('fab-mount');
const fab = new LiquidGlassFAB(container, {
    size: 80,
    mode: 'embedded',
    ariaLabel: 'Toggle chat'
});

// Global mode - container is validated but ignored for mounting
// Component renders to document.body instead
const fabGlobal = new LiquidGlassFAB(document.body, {
    mode: 'global',
    position: { bottom: '24px', right: '24px' }
});
```

---

## Configuration Options

### `options.size`

- **Type:** `number`
- **Default:** `80`
- **Description:** Button diameter in pixels. Physics scale proportionally.

```javascript
new LiquidGlassFAB(container, { size: 120 }); // Large button
```

### `options.icon`

- **Type:** `string` (SVG markup)
- **Default:** Chat bubble icon
- **Description:** SVG code for the button icon. Use `currentColor` for proper theming.

```javascript
const heartIcon = `
    <svg viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
    </svg>
`;

new LiquidGlassFAB(container, { icon: heartIcon });
```

### `options.ariaLabel`

- **Type:** `string`
- **Default:** `'Toggle'`
- **Description:** Accessibility label for screen readers. Sets `aria-label` attribute.

```javascript
new LiquidGlassFAB(container, { 
    ariaLabel: 'Open support chat' 
});
```

### `options.onToggle`

- **Type:** `function | null`
- **Default:** `null`
- **Signature:** `(isOpen: boolean) => void`
- **Description:** Callback fired when button is clicked. Receives current open state.

```javascript
new LiquidGlassFAB(container, {
    onToggle: (isOpen) => {
        console.log('Button is now:', isOpen ? 'OPEN' : 'CLOSED');
        if (isOpen) {
            showChatWidget();
        } else {
            hideChatWidget();
        }
    }
});
```

### `options.playEntranceAnimation`

- **Type:** `boolean`
- **Default:** `true`
- **Description:** Whether to play the water drop entrance animation on initialization.

```javascript
// Skip entrance animation
new LiquidGlassFAB(container, { 
    playEntranceAnimation: false 
});
```

---

## Public Methods

### `setState(isOpen)`

Set button state programmatically without triggering the `onToggle` callback.

**Parameters:**
- `isOpen` (boolean): New state to set

**Returns:** `void`

**Example:**
```javascript
const fab = new LiquidGlassFAB(container);

// Open programmatically
fab.setState(true);

// Close programmatically
fab.setState(false);
```

**Use cases:**
- Syncing button state with external widget
- Setting initial state after construction
- Resetting state without triggering side effects

---

### `getState()`

Get current button state.

**Parameters:** None

**Returns:** `boolean` - Current open/closed state

**Example:**
```javascript
const fab = new LiquidGlassFAB(container);
fab.setState(true);

console.log(fab.getState()); // true
```

---

### `destroy()`

Complete cleanup and removal of the button instance.

**Parameters:** None

**Returns:** `void`

**What it does:**
1. Cancels animation frame loop
2. Removes all event listeners
3. Removes DOM elements
4. Clears internal references for garbage collection

**Example:**
```javascript
const fab = new LiquidGlassFAB(container);

// Later, when done
fab.destroy();
```

**Important:** After calling `destroy()`, the instance cannot be reused. Create a new instance if needed.

```javascript
// ❌ Wrong - instance is destroyed
fab.destroy();
fab.setState(true); // This will fail

// ✅ Correct - create new instance
fab.destroy();
fab = new LiquidGlassFAB(container);
```

---

## Spring Physics Parameters

Internal spring physics values (for reference - not configurable via API in v1.0.0).

### Light Caustics
```javascript
lightX: SpringValue(35, stiffness: 0.08, damping: 0.82)
lightY: SpringValue(35, stiffness: 0.08, damping: 0.82)
```

### Scale Transform
```javascript
scale: SpringValue(1.0, stiffness: 0.15, damping: 0.75)
```

### Shine Offset
```javascript
shineX: SpringValue(0, stiffness: 0.06, damping: 0.85)
shineY: SpringValue(0, stiffness: 0.06, damping: 0.85)
```

### 8-Corner Morphing
```javascript
morphTL/TR/BR/BL: SpringValue(50, stiffness: 0.14, damping: 0.78)
morphTLV/TRV/BRV/BLV: SpringValue(50, stiffness: 0.14, damping: 0.78)
```

### Icon Parallax
```javascript
parallaxX: SpringValue(0, stiffness: 0.10, damping: 0.88)
parallaxY: SpringValue(0, stiffness: 0.10, damping: 0.88)
```

---

## CSS Custom Properties

These CSS variables are dynamically updated by JavaScript. You can override them for customization.

### Shape & Transform

```css
--radius-tl       /* Top-left horizontal radius (%) */
--radius-tr       /* Top-right horizontal radius (%) */
--radius-br       /* Bottom-right horizontal radius (%) */
--radius-bl       /* Bottom-left horizontal radius (%) */
--radius-tl-v     /* Top-left vertical radius (%) */
--radius-tr-v     /* Top-right vertical radius (%) */
--radius-br-v     /* Bottom-right vertical radius (%) */
--radius-bl-v     /* Bottom-left vertical radius (%) */
--scale           /* Scale transform value */
--translateX      /* X offset (px) */
--translateY      /* Y offset (px) */
```

### Lighting & Effects

```css
--light-x         /* Light caustic X position (%) */
--light-y         /* Light caustic Y position (%) */
--shine-x         /* Specular highlight X offset (px) */
--shine-y         /* Specular highlight Y offset (px) */
--parallax-x      /* Icon parallax X (px) */
--parallax-y      /* Icon parallax Y (px) */
```

### Custom Styling Example

Override base styles while preserving physics:

```css
.liquid-glass-fab {
    /* Custom glass color */
    background: rgba(59, 130, 246, 0.4) !important;
}

.liquid-glass-fab__icon {
    /* Custom icon color */
    color: #fbbf24 !important;
}
```

---

## Event Handling

### Pointer Events

The button uses modern pointer events for broad device support:

- `pointerenter`: Triggers hover state, scales button to 1.1
- `pointerleave`: Resets hover state, returns to scale 1.0
- `pointermove`: Updates cursor tracking for morphing and caustics
- `click`: Triggers toggle, creates ripple, calls `onToggle` callback

### Event Isolation

Each instance has isolated event listeners bound to its own DOM elements. Multiple instances on the same page do not interfere with each other.

```javascript
// Two independent buttons - separate hover states
const fab1 = new LiquidGlassFAB(container1);
const fab2 = new LiquidGlassFAB(container2);
// Hovering fab1 does NOT affect fab2
```

---

## Examples

### React Integration

```jsx
import { useEffect, useRef, useState } from 'react';
import { LiquidGlassFAB } from './LiquidGlassFAB.js';

function ChatButton() {
    const containerRef = useRef(null);
    const fabRef = useRef(null);
    const [isOpen, setIsOpen] = useState(false);

    useEffect(() => {
        fabRef.current = new LiquidGlassFAB(containerRef.current, {
            size: 80,
            ariaLabel: 'Toggle chat',
            onToggle: (open) => setIsOpen(open)
        });

        return () => fabRef.current?.destroy();
    }, []);

    // Sync external state changes
    useEffect(() => {
        if (fabRef.current) {
            fabRef.current.setState(isOpen);
        }
    }, [isOpen]);

    return <div ref={containerRef} />;
}
```

### Vue 3 Integration

```vue
<template>
    <div ref="fabContainer"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { LiquidGlassFAB } from './LiquidGlassFAB.js';

const fabContainer = ref(null);
let fab = null;

onMounted(() => {
    fab = new LiquidGlassFAB(fabContainer.value, {
        size: 80,
        onToggle: (isOpen) => {
            console.log('Chat is', isOpen ? 'open' : 'closed');
        }
    });
});

onBeforeUnmount(() => {
    fab?.destroy();
});
</script>
```

### Vanilla JS Dynamic Creation

```javascript
function createFABGrid(count) {
    const grid = document.getElementById('fab-grid');
    const instances = [];

    for (let i = 0; i < count; i++) {
        const container = document.createElement('div');
        container.style.display = 'inline-block';
        container.style.margin = '10px';
        grid.appendChild(container);

        const fab = new LiquidGlassFAB(container, {
            size: 60,
            ariaLabel: `Button ${i + 1}`,
            onToggle: (isOpen) => {
                console.log(`Button ${i + 1}:`, isOpen);
            }
        });

        instances.push(fab);
    }

    return instances;
}

// Create 10 independent buttons
const buttons = createFABGrid(10);

// Clean up all at once
function cleanup() {
    buttons.forEach(fab => fab.destroy());
}
```

### Conditional Entrance Animation

```javascript
const isFirstVisit = !localStorage.getItem('visited');

const fab = new LiquidGlassFAB(container, {
    playEntranceAnimation: isFirstVisit
});

if (isFirstVisit) {
    localStorage.setItem('visited', 'true');
}
```

### State Synchronization

```javascript
let chatWidget = { open: false };

const fab = new LiquidGlassFAB(container, {
    onToggle: (isOpen) => {
        chatWidget.open = isOpen;
        if (isOpen) {
            document.getElementById('chat-widget').classList.add('visible');
        } else {
            document.getElementById('chat-widget').classList.remove('visible');
        }
    }
});

// External trigger (e.g., keyboard shortcut)
document.addEventListener('keydown', (e) => {
    if (e.key === 'c' && e.ctrlKey) {
        chatWidget.open = !chatWidget.open;
        fab.setState(chatWidget.open);
    }
});
```

---

## Version History

### v1.0.0 (2026-09-14)
- Initial canon release
- Full instance isolation
- BEM naming convention
- Professional module architecture
- Complete test suite

---

**Module**: Liquid Glass FAB  
**Version**: 1.0.0 Canon  
**Author**: vnxORACLE  
**License**: MIT
