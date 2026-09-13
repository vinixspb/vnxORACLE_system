# Liquid Glass FAB — Полная реализация капли для веб-чата

**Дата:** 2026-09-13  
**Проект:** vnxORACLE Web Chat Widget  
**Стиль:** Apple Vision Pro — liquid glass morphing button

---

## 📦 Файловая структура

```
src/components/ChatWidget/
├── liquid-glass-fab.js       # JavaScript модуль с физикой
├── liquid-glass-fab.css      # Стили и анимации
└── index.jsx                  # Использование в React компоненте
```

---

## 🎨 Концепция дизайна

**Референс:** Apple Vision Pro UI — капля воды с реалистичной физикой деформации

### Ключевые эффекты:

1. **Spring Physics** — пружинная анимация всех параметров (16 spring-объектов)
2. **8-Corner Morphing** — деформация по 8 углам (horizontal + vertical border-radius)
3. **Light Caustics** — динамическое освещение, следующее за курсором
4. **Parallax Icon** — иконка смещается при наведении
5. **Water Drop Entrance** — анимация появления капли сверху
6. **Ripple Effect** — волны при клике
7. **Glass Morphism** — backdrop-filter с blur + saturation
8. **Specular Highlights** — блики на поверхности

---

## 📄 JavaScript: `liquid-glass-fab.js`

### SpringValue — физика органичного движения

```javascript
class SpringValue {
    constructor(initial, stiffness = 0.1, damping = 0.8) {
        this.current = initial
        this.target = initial
        this.velocity = 0
        this.stiffness = stiffness  // Жёсткость пружины
        this.damping = damping      // Затухание
    }

    update() {
        // Hooke's law: F = -kx
        this.velocity += (this.target - this.current) * this.stiffness
        this.velocity *= this.damping
        this.current += this.velocity

        // Остановка при малых значениях
        if (Math.abs(this.velocity) < 0.001 && 
            Math.abs(this.target - this.current) < 0.001) {
            this.current = this.target
            this.velocity = 0
        }
    }

    set(newTarget) {
        this.target = newTarget
    }
}
```

**Параметры пружин:**
- `lightX, lightY` — следят за курсором (stiffness: 0.08, damping: 0.82)
- `scale` — увеличение при hover (stiffness: 0.15, damping: 0.75)
- `morphTL, morphTR, morphBR, morphBL` — деформация углов (stiffness: 0.14, damping: 0.78)
- `parallaxX, parallaxY` — смещение иконки (stiffness: 0.10, damping: 0.88)

---

### LiquidGlassFAB — основной класс

```javascript
export class LiquidGlassFAB {
    constructor(container, onToggle) {
        this.container = container
        this.onToggle = onToggle
        this.isOpen = false

        this.createElements()
        this.initPhysics()
        this.initEventListeners()
        this.startAnimationLoop()
        this.playEntranceAnimation()
    }

    // ... полный код в файле
}
```

**Основные методы:**

1. **`createElements()`** — создаёт DOM-структуру:
   ```html
   <div class="liquid-fab-wrapper">
       <button class="liquid-fab">
           <svg class="chat-icon">...</svg>
       </button>
   </div>
   ```

2. **`initPhysics()`** — инициализирует 17 SpringValue объектов:
   - Light: `lightX, lightY`
   - Scale: `scale`
   - Shine: `shineX, shineY`
   - Morph: `morphTL, morphTR, morphBR, morphBL, morphTLV, morphTRV, morphBRV, morphBLV`
   - Translate: `translateX, translateY`
   - Parallax: `parallaxX, parallaxY`

3. **`onMove(e)`** — обработка движения мыши:
   ```javascript
   onMove(e) {
       const rect = this.fab.getBoundingClientRect()
       const x = e.clientX - rect.left
       const y = e.clientY - rect.top
       
       const normX = (x / rect.width) * 100
       const normY = (y / rect.height) * 100
       
       // Обновляем свет
       this.lightX.set(normX)
       this.lightY.set(normY)
       
       // Деформация в зависимости от квадранта
       const centerX = rect.width / 2
       const centerY = rect.height / 2
       const distance = Math.hypot(x - centerX, y - centerY) / centerX
       const deformAmount = Math.min(distance * 35, 45)
       
       if (normX < 50 && normY < 50) {
           // Top-left: деформируем TL угол наружу, BR внутрь
           this.morphTL.set(50 + deformAmount * 0.4)
           this.morphBR.set(50 - deformAmount * 0.3)
       }
       // ... остальные квадранты
   }
   ```

4. **`onClick(e)`** — эффект нажатия:
   - Ripple эффект (волна света)
   - Squash animation (сжатие → восстановление)
   - Вызов callback `onToggle()`

5. **`startAnimationLoop()`** — 60 FPS анимация:
   ```javascript
   const animate = () => {
       // Обновляем все пружины
       [this.lightX, this.lightY, this.scale, /* ... */]
           .forEach(spring => spring.update())
       
       // Применяем к CSS переменным
       this.fab.style.setProperty('--light-x', `${this.lightX.current}%`)
       this.fab.style.setProperty('--scale', this.scale.current)
       // ... остальные
       
       requestAnimationFrame(animate)
   }
   ```

---

## 🎨 CSS: `liquid-glass-fab.css`

### Основная кнопка

```css
.liquid-fab {
    width: 80px;
    height: 80px;
    
    /* 8-угольная деформация */
    border-radius:
        var(--radius-tl, 50%)
        var(--radius-tr, 50%)
        var(--radius-br, 50%)
        var(--radius-bl, 50%)
        /
        var(--radius-tl-v, 50%)
        var(--radius-tr-v, 50%)
        var(--radius-br-v, 50%)
        var(--radius-bl-v, 50%);
    
    /* Многослойный фон */
    background:
        /* Динамические блики */
        radial-gradient(
            circle at var(--light-x, 35%) var(--light-y, 35%),
            rgba(255,255,255,0.18),
            rgba(255,255,255,0.08) 35%,
            transparent 60%
        ),
        /* Fresnel rim — свечение краёв */
        radial-gradient(
            circle at 50% 50%,
            transparent 40%,
            rgba(255,255,255,0.12) 70%,
            rgba(255,255,255,0.25) 88%,
            transparent
        ),
        /* Базовый цвет */
        radial-gradient(
            circle at 50% 60%,
            rgba(180,230,255,0.05),
            rgba(180,230,255,0.08)
        );
    
    /* Glass эффект */
    backdrop-filter: blur(28px) saturate(160%) brightness(1.05);
    -webkit-backdrop-filter: blur(28px) saturate(160%) brightness(1.05);
    
    /* Тени для глубины */
    box-shadow:
        inset 0 1px 2px rgba(255,255,255,0.6),
        inset 0 -4px 20px rgba(0,0,0,0.08),
        0 4px 8px rgba(0,0,0,0.1),
        0 12px 32px rgba(0,0,0,0.15),
        0 24px 64px rgba(0,0,0,0.1);
    
    /* Spring-driven трансформация */
    transform:
        scale(var(--scale, 1))
        translateX(var(--translateX, 0))
        translateY(var(--translateY, 0));
}
```

### Specular highlight (блик)

```css
.liquid-fab::before {
    content: '';
    position: absolute;
    top: 6px;
    left: 10px;
    width: 36px;
    height: 32px;
    background:
        radial-gradient(
            ellipse at 35% 35%,
            rgba(255,255,255,0.95),
            rgba(255,255,255,0.5) 40%,
            transparent 70%
        );
    border-radius: 50%;
    transform: translate(var(--shine-x, 0), var(--shine-y, 0));
    filter: blur(2px);
    mix-blend-mode: overlay;
}
```

### Glass edge (светящаяся рамка)

```css
.liquid-fab::after {
    content: '';
    position: absolute;
    inset: -1.5px;
    border-radius: inherit;
    padding: 2px;
    background: linear-gradient(
        135deg,
        rgba(255,255,255,0.6),
        rgba(255,255,255,0.2) 40%,
        transparent 70%
    );
    -webkit-mask:
        linear-gradient(#fff 0 0) content-box,
        linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
}
```

### Water drop entrance animation

```css
@keyframes dropEntrance {
    0% {
        transform: translateY(-250px) scale(0.2) rotate(-8deg);
        opacity: 0;
        border-radius: 50% 50% 50% 50% / 65% 65% 35% 35%;
    }
    30% {
        transform: translateY(-30px) scale(0.25) rotate(-2deg);
        opacity: 1;
        border-radius: 50% 50% 50% 50% / 63% 63% 37% 37%;
    }
    45% {
        transform: translateY(0) scale(1.35) rotate(1deg);
        border-radius: 42% 58% 46% 54% / 54% 46% 54% 46%;
    }
    55% {
        transform: translateY(0) scale(0.8) rotate(-1deg);
        border-radius: 54% 46% 56% 44% / 44% 56% 44% 56%;
    }
    65% {
        transform: translateY(0) scale(1.15) rotate(0.5deg);
        border-radius: 48% 52% 49% 51%;
    }
    100% {
        transform: translateY(0) scale(1) rotate(0deg);
        border-radius: 50%;
    }
}

.liquid-fab.drop-entrance {
    animation: dropEntrance 1.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}
```

### Ripple effect при клике

```css
@keyframes liquidRipple {
    to {
        transform: scale(3);
        opacity: 0;
    }
}

.liquid-fab-ripple {
    position: absolute;
    border-radius: 50%;
    background: radial-gradient(
        circle,
        rgba(255,255,255,0.5),
        rgba(255,255,255,0.2) 50%,
        transparent 70%
    );
    transform: scale(0);
    animation: liquidRipple 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    mix-blend-mode: overlay;
}
```

---

## 🔧 Использование в React

```jsx
import { useEffect, useRef } from 'react'
import { LiquidGlassFAB } from './liquid-glass-fab.js'
import './liquid-glass-fab.css'

function ChatWidget() {
    const fabRef = useRef(null)
    const fabInstanceRef = useRef(null)
    const [isOpen, setIsOpen] = useState(false)

    useEffect(() => {
        if (fabRef.current && !fabInstanceRef.current) {
            fabInstanceRef.current = new LiquidGlassFAB(
                fabRef.current,
                () => setIsOpen(prev => !prev)
            )
        }

        return () => {
            if (fabInstanceRef.current) {
                fabInstanceRef.current.destroy()
                fabInstanceRef.current = null
            }
        }
    }, [])

    // Синхронизация состояния
    useEffect(() => {
        if (fabInstanceRef.current) {
            fabInstanceRef.current.setState(isOpen)
        }
    }, [isOpen])

    return (
        <div>
            <div ref={fabRef} />
            {isOpen && <ChatWindow />}
        </div>
    )
}
```

---

## 🎯 Ключевые параметры настройки

### Spring Physics

| Параметр | Stiffness | Damping | Эффект |
|---|---|---|---|
| Light tracking | 0.08 | 0.82 | Плавное следование за курсором |
| Scale | 0.15 | 0.75 | Упругое увеличение при hover |
| Morphing | 0.14 | 0.78 | Органичная деформация |
| Shine | 0.06 | 0.85 | Медленное смещение бликов |
| Parallax | 0.10 | 0.88 | Глубина иконки |

### Deformation Amounts

- **Primary corner:** `deformAmount * 0.4` (максимум ~18%)
- **Opposite corner:** `deformAmount * -0.3` (сжатие ~13%)
- **Adjacent corners:** `deformAmount * 0.2` (слабая деформация ~9%)

### Visual Layers

1. **Dynamic caustics** — радиальный градиент от курсора
2. **Fresnel rim** — свечение краёв (40% → 88% radius)
3. **Core color** — базовый оттенок
4. **Backdrop filter** — blur(28px) + saturate(160%)
5. **Specular highlight** — белый блик сверху слева
6. **Glass edge** — gradient border через mask-composite

---

## 📱 Адаптивность

```css
@media (max-width: 480px) {
    .liquid-fab {
        width: 56px;
        height: 56px;
    }
    
    .chat-icon {
        width: 28px;
        height: 28px;
    }
}
```

---

## 🌈 Светлая тема

```css
[data-theme="light"] .liquid-fab {
    background:
        radial-gradient(
            circle at var(--light-x, 35%) var(--light-y, 35%),
            rgba(56, 189, 248, 0.3),
            rgba(56, 189, 248, 0.1) 35%,
            transparent 60%
        ),
        /* ... */;
    
    box-shadow:
        inset 0 1px 2px rgba(255,255,255,0.8),
        /* ... более мягкие тени */;
}
```

---

## 🔍 Отладка и производительность

### Performance

- **requestAnimationFrame** — 60 FPS
- **will-change: transform, border-radius** — GPU acceleration
- **Spring settling threshold** — останавливает анимацию при velocity < 0.001

### Debug Mode (опционально)

```javascript
// В onMove добавить визуализацию
console.log({
    cursor: { x: normX, y: normY },
    deform: deformAmount,
    corners: {
        TL: this.morphTL.current,
        BR: this.morphBR.current
    }
})
```

---

## 📚 Связанные файлы

- [liquid-glass-fab.js](../../../landing/src/components/ChatWidget/liquid-glass-fab.js) — полный код
- [liquid-glass-fab.css](../../../landing/src/components/ChatWidget/liquid-glass-fab.css) — стили
- [ChatWidget/index.jsx](../../../landing/src/components/ChatWidget/index.jsx) — интеграция

---

**Дата создания:** 2026-09-13  
**Автор:** vnxORACLE Frontend Team  
**Лицензия:** Proprietary
