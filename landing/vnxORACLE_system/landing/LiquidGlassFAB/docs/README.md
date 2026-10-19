# Liquid Glass FAB

Apple Vision Pro style floating action button with spring physics and glass morphism.

## ✨ Features

- **Spring Physics**: Hooke's law implementation for organic motion
- **8-Corner Morphing**: Dynamic border-radius manipulation following cursor
- **Glass Morphism**: Multi-layer backdrop filters and gradients
- **Water Drop Entrance**: Cinematic entry animation with wobble physics
- **Ripple Effects**: Touch feedback with radial expansion
- **Parallax Icon**: Subtle depth effect on hover
- **Light Caustics**: Cursor-following highlight system
- **Full Isolation**: Multiple independent instances per page
- **Framework Agnostic**: Pure vanilla JavaScript ES6 module
- **Zero Dependencies**: No external libraries required

## 📦 Installation

### Direct Import (ESM)

```javascript
import { LiquidGlassFAB } from './src/LiquidGlassFAB.js';
```

### Include CSS

```html
<link rel="stylesheet" href="./src/liquid-glass-fab.css">
```

## 🚀 Quick Start

### Minimal Example

```javascript
import { LiquidGlassFAB } from './LiquidGlassFAB.js';

const container = document.getElementById('fab-container');
const fab = new LiquidGlassFAB(container);
```

### With Options

```javascript
const fab = new LiquidGlassFAB(container, {
    size: 80,
    icon: '<svg>...</svg>',
    ariaLabel: 'Open chat',
    playEntranceAnimation: true,
    onToggle: (isOpen) => {
        console.log('Button state:', isOpen);
    }
});
```

### Managing State

```javascript
// Set state programmatically
fab.setState(true);

// Get current state
const isOpen = fab.getState();

// Clean up
fab.destroy();
```

## 🎨 Customization

### Size

```javascript
// Small button (60px)
new LiquidGlassFAB(container, { size: 60 });

// Standard (80px - default)
new LiquidGlassFAB(container, { size: 80 });

// Large (120px)
new LiquidGlassFAB(container, { size: 120 });
```

### Custom Icon

```javascript
const customIcon = `
    <svg viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2L2 7l10 5 10-5-10-5z"/>
        <path d="M2 17l10 5 10-5M2 12l10 5 10-5"/>
    </svg>
`;

new LiquidGlassFAB(container, { icon: customIcon });
```

### Toggle Callback

```javascript
new LiquidGlassFAB(container, {
    onToggle: (isOpen) => {
        if (isOpen) {
            openChatWidget();
        } else {
            closeChatWidget();
        }
    }
});
```

## 🔧 API Reference

### Constructor

```typescript
new LiquidGlassFAB(container: HTMLElement, options?: Options)
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `size` | `number` | `80` | Button diameter in pixels |
| `icon` | `string` | Default chat icon | SVG markup for the icon |
| `ariaLabel` | `string` | `'Toggle'` | Accessibility label |
| `onToggle` | `function` | `null` | Callback on click: `(isOpen: boolean) => void` |
| `playEntranceAnimation` | `boolean` | `true` | Play water drop animation on init |

### Methods

#### `setState(isOpen: boolean)`
Update button state without triggering toggle callback.

```javascript
fab.setState(true);  // Set to open state
fab.setState(false); // Set to closed state
```

#### `getState(): boolean`
Get current button state.

```javascript
const isOpen = fab.getState();
```

#### `destroy()`
Complete cleanup: removes DOM, stops animation loop, clears event listeners.

```javascript
fab.destroy();
```

## 🧪 Testing

Open `tests/canon-test.html` in a browser to see the full test suite:

- **Test 1**: Standard single button
- **Test 2**: Dual independent buttons (state isolation)
- **Test 3**: Custom size (120px)
- **Test 4**: Memory cleanup validation
- **Test 5**: Reinstantiation test

```bash
# Serve locally
python -m http.server 8000
# Open http://localhost:8000/tests/canon-test.html
```

## 🎯 Browser Support

- Chrome/Edge 88+
- Firefox 94+
- Safari 15.4+

**Required features:**
- CSS `backdrop-filter`
- ES6 modules
- `requestAnimationFrame`

## 📐 Architecture

### Spring Physics
Uses Hooke's law (`F = -kx`) for organic motion:
- Stiffness: 0.08-0.15
- Damping: 0.75-0.88
- 60 FPS via `requestAnimationFrame`

### CSS Variables
Dynamic values controlled via CSS custom properties:
- `--light-x`, `--light-y`: Cursor-following light position
- `--scale`: Hover/click scale transform
- `--radius-*`: 8-corner morphing values
- `--parallax-x`, `--parallax-y`: Icon movement

### BEM Naming
Strict namespace isolation:
```
.liquid-glass-fab              # Main button
.liquid-glass-fab__wrapper     # Positioning container
.liquid-glass-fab__icon        # Icon container
.liquid-glass-fab__ripple      # Click ripple effect
```

## 🔐 Instance Isolation

Each button instance maintains:
- Isolated DOM tree
- Independent animation loop
- Separate event listeners
- Private physics state

**Multiple buttons work independently:**
```javascript
const fab1 = new LiquidGlassFAB(container1);
const fab2 = new LiquidGlassFAB(container2);
// Completely isolated - no shared state
```

## ⚡ Performance

- GPU-accelerated transforms
- `will-change` hints for browser optimization
- Single RAF loop per instance
- Efficient spring physics (early termination on settle)

## 🎨 Visual Canon

The following visual properties are **frozen** in v1.0.0:

- Gray glass base: `rgba(100, 116, 139, 0.4)`
- Backdrop blur: `12px`
- Spring timings: stiffness/damping ratios locked
- 8-corner morph algorithm: quadrant-based deformation
- Water drop entrance: 1.6s duration, cubic-bezier timing
- Ripple expansion: 4x scale over 0.8s

**Do not modify these without version bump.**

## 📝 License

MIT License - vnxORACLE 2026

## 🤝 Contributing

This is a canon module. Architectural changes require approval.

For bugs or issues, provide:
1. Browser/OS version
2. Minimal reproduction case
3. Expected vs actual behavior

---

**Version**: 1.0.0 Canon  
**Status**: Production Ready  
**Author**: vnxORACLE
