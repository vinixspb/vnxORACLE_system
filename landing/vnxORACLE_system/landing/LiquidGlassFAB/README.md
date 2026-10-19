# 🌊 Liquid Glass FAB v1.0.0 Canon

<div align="center">

**Apple Vision Pro style floating action button**

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)

*Spring Physics • 8-Corner Morphing • Glass Morphism • Full Instance Isolation*

</div>

---

## 🎯 What This Is

A professional, production-ready UI module featuring liquid glass morphing effects inspired by Apple Vision Pro design language. Built with vanilla JavaScript and spring physics for organic, responsive interactions.

**Key Features:**
- ⚡️ **Spring Physics Engine** - Hooke's law implementation for natural motion
- 🎨 **8-Corner Dynamic Morphing** - Border-radius manipulation following cursor
- 💎 **Multi-Layer Glass Morphism** - Backdrop filters with caustic lighting
- 💧 **Water Drop Entrance** - Cinematic entry animation with wobble
- 🎭 **Complete Isolation** - Multiple independent instances per page
- 🚀 **Zero Dependencies** - Pure vanilla JS, framework agnostic
- 📦 **NPM Ready** - ES6 module with clean public API

## 📸 Live Demo

Open `tests/canon-test.html` to see all 5 validation tests:

```bash
cd LiquidGlassFAB
python -m http.server 8000
# Navigate to http://localhost:8000/tests/canon-test.html
```

## 🚀 Quick Start

### 1. Import Module

```javascript
import { LiquidGlassFAB } from './src/LiquidGlassFAB.js';
```

### 2. Include Styles

```html
<link rel="stylesheet" href="./src/liquid-glass-fab.css">
```

### 3. Create Instance

```javascript
const container = document.getElementById('fab-container');

const fab = new LiquidGlassFAB(container, {
    size: 80,
    ariaLabel: 'Open chat',
    onToggle: (isOpen) => {
        console.log('Button toggled:', isOpen);
    }
});
```

That's it! 🎉

## 📚 Documentation

- **[README.md](docs/README.md)** - Full feature documentation and examples
- **[API.md](docs/API.md)** - Complete API reference with integration guides

## 🧪 Canon Test Suite

The module includes a comprehensive test suite validating:

1. **Standard Button** - Baseline physics and animations
2. **Dual Independence** - Complete state isolation between instances
3. **Custom Sizing** - Dynamic scaling without pixel dependencies
4. **Memory Cleanup** - RAF cancellation and DOM removal validation
5. **Reinstantiation** - Clean recreation after destruction

**Test Coverage:**
- ✅ Event listener isolation
- ✅ Animation frame independence
- ✅ DOM garbage collection
- ✅ Spring physics state isolation
- ✅ Multiple concurrent instances

## 🏗️ Architecture

### Module Structure

```
LiquidGlassFAB/
├── src/
│   ├── LiquidGlassFAB.js      # 450 lines - Core module with SpringValue class
│   └── liquid-glass-fab.css    # 280 lines - Isolated BEM styles
├── docs/
│   ├── README.md               # Feature documentation
│   └── API.md                  # API reference + React/Vue examples
├── tests/
│   └── canon-test.html         # 5-test validation suite
└── package.json                # NPM metadata
```

### BEM Naming Convention

```css
.liquid-glass-fab              /* Main button */
.liquid-glass-fab__wrapper     /* Position container */
.liquid-glass-fab__icon        /* Icon container with parallax */
.liquid-glass-fab__ripple      /* Click ripple effect */
.liquid-glass-fab--drop-entrance  /* Modifier: entrance animation */
```

### Instance Isolation

Each button maintains:
- **Separate DOM tree** - No shared elements
- **Independent RAF loop** - Private animation cycle
- **Isolated event listeners** - Bound to instance only
- **Private physics state** - 16 spring values per instance

```javascript
// ✅ This works perfectly - no conflicts
const fab1 = new LiquidGlassFAB(container1);
const fab2 = new LiquidGlassFAB(container2);
const fab3 = new LiquidGlassFAB(container3);
```

## 🎨 Visual Canon (Frozen)

The following properties are **locked** in v1.0.0:

| Property | Value | Notes |
|----------|-------|-------|
| Base color | `rgba(100, 116, 139, 0.4)` | Gray glass |
| Backdrop blur | `12px` | Glass morphism depth |
| Spring stiffness | `0.06 - 0.15` | Organic motion feel |
| Spring damping | `0.75 - 0.88` | Smooth settling |
| Entrance duration | `1.6s` | Water drop animation |
| Ripple scale | `4x` | Click feedback expansion |
| Morph range | `50% ± 45%` | Border-radius limits |

**These values define the canonical visual experience and must not be modified without a major version bump.**

## 🔧 API Summary

### Constructor
```javascript
new LiquidGlassFAB(container, options)
```

### Options
```javascript
{
    size: 80,                           // Diameter in px
    icon: '<svg>...</svg>',             // Custom SVG
    ariaLabel: 'Toggle',                // A11y label
    onToggle: (isOpen) => {},           // Click callback
    playEntranceAnimation: true         // Water drop on init
}
```

### Methods
```javascript
fab.setState(true)      // Update state
fab.getState()          // Get current state
fab.destroy()           // Complete cleanup
```

See [API.md](docs/API.md) for full documentation.

## 🎯 Framework Integration

### React
```jsx
function ChatButton() {
    const containerRef = useRef(null);
    const fabRef = useRef(null);

    useEffect(() => {
        fabRef.current = new LiquidGlassFAB(containerRef.current, {
            onToggle: (open) => console.log(open)
        });
        return () => fabRef.current?.destroy();
    }, []);

    return <div ref={containerRef} />;
}
```

### Vue 3
```vue
<template>
    <div ref="fabContainer"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';

const fabContainer = ref(null);
let fab = null;

onMounted(() => {
    fab = new LiquidGlassFAB(fabContainer.value);
});

onBeforeUnmount(() => fab?.destroy());
</script>
```

More examples in [API.md](docs/API.md).

## 🌐 Browser Support

- Chrome/Edge 88+
- Firefox 94+
- Safari 15.4+

**Required features:**
- CSS `backdrop-filter`
- ES6 modules
- `requestAnimationFrame`

## ⚡ Performance

- **GPU Accelerated** - `transform` and `will-change` optimizations
- **60 FPS Target** - Single RAF loop per instance
- **Efficient Physics** - Early termination on spring settle
- **Memory Safe** - Complete cleanup on `destroy()`

## 📦 NPM Package

```json
{
  "name": "@vnxoracle/liquid-glass-fab",
  "version": "1.0.0",
  "type": "module",
  "main": "src/LiquidGlassFAB.js",
  "exports": {
    ".": "./src/LiquidGlassFAB.js",
    "./css": "./src/liquid-glass-fab.css"
  }
}
```

## 🛡️ Canon Status

This is the **official v1.0.0 canon release**. The module has undergone architectural rework to ensure:

- ✅ Professional-grade code structure
- ✅ Complete instance isolation
- ✅ BEM naming convention
- ✅ NPM-ready packaging
- ✅ Comprehensive test coverage
- ✅ Framework-agnostic design

**All visual behavior is frozen** - changes require version bump.

## 📝 License

MIT License © 2026 vnxORACLE

---

<div align="center">

**[Documentation](docs/README.md)** • **[API Reference](docs/API.md)** • **[Test Suite](tests/canon-test.html)**

*Built with precision for the vnxORACLE ecosystem*

</div>
