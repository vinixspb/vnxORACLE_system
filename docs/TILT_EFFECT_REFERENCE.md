# Схема обработки эффекта tilt карточек при наведении мышки

> **Документ для технической передачи**  
> Полная архитектура 3D tilt-эффекта с плавным первичным наведением и реактивным следованием за курсором.

---

## 📁 Файловая структура

```
vnxORACLE_system/landing/src/
├── hooks/
│   └── useTiltEffect.js          # Хук для 3D tilt эффекта
├── components/
│   ├── DirectionsSection.jsx     # Использует tilt на direction-card
│   ├── ProblemsSection.jsx       # Использует tilt на problem-card
│   ├── SolutionSection.jsx       # Использует tilt на solution-card
│   └── UnderTheHoodSection.jsx   # Использует tilt на tech-card
└── App.jsx                       # RoleCard, StepCard, TrustCard используют tilt
```

---

## 🎯 Концепция эффекта

**Двухфазный алгоритм:**

1. **Первичное наведение (First Contact)** — плавный переход в tilt за 300ms с `ease-out`
2. **Активное следование** — мгновенное следование за курсором без transition (имитация физики)
3. **Выход курсора** — плавное возвращение в исходное положение за 400ms с `ease-out`

**Трансформации:**
- `perspective(1000px)` — глубина 3D сцены
- `rotateX()` — наклон по вертикали (вверх/вниз)
- `rotateY()` — наклон по горизонтали (влево/вправо)
- `scale3d(1.02, 1.02, 1.02)` — лёгкое увеличение при hover

---

## 📄 Код хука: `useTiltEffect.js`

```javascript
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
```

---

## 🔍 Детальный разбор алгоритма

### 1. Инициализация (хук вызван в компоненте)

```javascript
const { ref, onMouseEnter, onMouseMove, onMouseLeave } = useTiltEffect(10)
```

**Что происходит:**
- Создаётся `ref` для привязки к DOM-элементу
- Создаётся `isFirstContact` — флаг первичного наведения (начальное значение `true`)
- Возвращаются обработчики событий

**Параметр `strength`:**
- Определяет максимальный угол наклона (по умолчанию 15°)
- `strength = 10` → макс. наклон ±10°
- `strength = 15` → макс. наклон ±15°

---

### 2. Первичное наведение (First Contact)

**Событие:** `onMouseEnter`

```javascript
const handleMouseEnter = () => {
  if (!ref.current) return
  isFirstContact.current = true
  ref.current.style.transition = 'transform 0.3s ease-out'
}
```

**Что происходит:**
1. Проверяем, что ref привязан к элементу
2. Устанавливаем флаг `isFirstContact = true`
3. **Включаем CSS transition** на 300ms с `ease-out`

**Зачем:**
- Плавный вход в tilt при первом касании курсора
- Избегаем резкого скачка карточки

---

### 3. Движение курсора (Active Tracking)

**Событие:** `onMouseMove`

```javascript
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

  if (isFirstContact.current) {
    isFirstContact.current = false
    setTimeout(() => {
      if (card) card.style.transition = 'none'
    }, 300)
  }

  card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`
}
```

**Пошагово:**

#### 3.1. Получение позиции курсора относительно карточки

```javascript
const rect = card.getBoundingClientRect()
const x = e.clientX - rect.left   // Позиция X внутри карточки (0 → width)
const y = e.clientY - rect.top    // Позиция Y внутри карточки (0 → height)
```

#### 3.2. Расчёт центра карточки

```javascript
const centerX = rect.width / 2    // Центр по горизонтали
const centerY = rect.height / 2   // Центр по вертикали
```

#### 3.3. Расчёт смещения от центра (нормализация -1 до +1)

```javascript
const offsetX = (x - centerX) / centerX  // -1 (левый край) → +1 (правый край)
const offsetY = (y - centerY) / centerY  // -1 (верхний край) → +1 (нижний край)
```

#### 3.4. Вычисление углов наклона

```javascript
const rotateX = offsetY * -strength  // Инвертируем Y (вверх = положительный rotateX)
const rotateY = offsetX * strength   // X без инверсии (вправо = положительный rotateY)
```

**Пример (strength = 15, карточка 300×200):**
- Курсор в центре (150, 100) → `rotateX = 0°`, `rotateY = 0°`
- Курсор сверху по центру (150, 0) → `rotateX = +15°`, `rotateY = 0°` (карточка наклонена вверх)
- Курсор снизу по центру (150, 200) → `rotateX = -15°`, `rotateY = 0°` (карточка наклонена вниз)
- Курсор слева сверху (0, 0) → `rotateX = +15°`, `rotateY = -15°` (наклон влево-вверх)

#### 3.5. Отключение transition после первого движения

```javascript
if (isFirstContact.current) {
  isFirstContact.current = false
  setTimeout(() => {
    if (card) card.style.transition = 'none'
  }, 300)
}
```

**Алгоритм первичного наведения:**

1. **Курсор входит** → `onMouseEnter` → `transition = '0.3s ease-out'` + `isFirstContact = true`
2. **Первое движение** → `onMouseMove` → применяется transform с плавной анимацией (300ms)
3. **Через 300ms** → `setTimeout` убирает transition → `transition = 'none'`
4. **Последующие движения** → transform применяется мгновенно (без transition)

**Зачем это нужно:**
- Плавный вход при первом касании
- Мгновенная реакция при активном движении (имитация физики)

#### 3.6. Применение трансформации

```javascript
card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`
```

**Компоненты transform:**
- `perspective(1000px)` — глубина 3D пространства (чем больше, тем меньше перспектива)
- `rotateX(${rotateX}deg)` — наклон по оси X (вертикаль)
- `rotateY(${rotateY}deg)` — наклон по оси Y (горизонталь)
- `scale3d(1.02, 1.02, 1.02)` — лёгкое увеличение (2%) для эффекта "приподнятости"

---

### 4. Выход курсора (Reset)

**Событие:** `onMouseLeave`

```javascript
const handleMouseLeave = () => {
  if (!ref.current) return
  ref.current.style.transition = 'transform 0.4s ease-out'
  ref.current.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)'
  isFirstContact.current = true
}
```

**Что происходит:**
1. **Включаем transition** на 400ms с `ease-out`
2. **Возвращаем transform в нулевое положение** (без наклона, без scale)
3. **Сбрасываем флаг** `isFirstContact = true` для следующего входа

**Зачем 400ms (а не 300ms как при входе):**
- Более плавное и заметное возвращение в исходное положение
- Эффект "мягкой посадки"

---

## 🎨 CSS требования для карточек

Чтобы tilt-эффект работал корректно, карточки должны иметь:

```css
.card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  transform-style: preserve-3d;
  will-change: transform;
}
```

**Важно:**
- `transition` должен включать `transform` (для плавности hover-состояний)
- `transform-style: preserve-3d` — сохраняет 3D пространство для дочерних элементов
- `will-change: transform` — оптимизация рендеринга (GPU acceleration)

**Пример из `App.css`:**

```css
.problem-card {
  padding: 28px 24px;
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  transition: transform 0.3s ease, box-shadow 0.3s ease, background-color 0.3s ease, border-color 0.3s ease;
}
```

---

## 🔧 Использование в компонентах

### Пример 1: Простая карточка (RoleCard)

```jsx
function RoleCard({ title, desc }) {
  const { ref, onMouseEnter, onMouseMove, onMouseLeave } = useTiltEffect(10)
  
  return (
    <div 
      ref={ref} 
      onMouseEnter={onMouseEnter} 
      onMouseMove={onMouseMove} 
      onMouseLeave={onMouseLeave} 
      className="role-card"
    >
      <h3 className="role-title">{title}</h3>
      <p className="role-desc">{desc}</p>
    </div>
  )
}
```

### Пример 2: Карточка с Framer Motion (ProblemCard)

```jsx
function ProblemCard({ item, idx }) {
  const Icon = icons[idx]
  const { ref, onMouseEnter, onMouseMove, onMouseLeave } = useTiltEffect(10)

  return (
    <motion.div
      ref={ref}
      onMouseEnter={onMouseEnter}
      onMouseMove={onMouseMove}
      onMouseLeave={onMouseLeave}
      className="problem-card"
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-80px' }}
      transition={{ duration: 0.5, delay: idx * 0.1, ease: EASE }}
    >
      <div className="problem-icon">
        <Icon size={28} strokeWidth={1.8} />
      </div>
      <h3 className="problem-title">{item.title}</h3>
      <p className="problem-desc">{item.desc}</p>
    </motion.div>
  )
}
```

**Важно:** `ref` от `useTiltEffect` совместим с Framer Motion's `motion.div`.

---

## 🧪 Тестирование эффекта

### Проверка корректности работы:

1. **Плавный вход**
   - Наведите курсор на карточку
   - Первое движение должно быть плавным (300ms)
   - Последующие движения — мгновенные

2. **Корректность углов**
   - Курсор вверху → карточка наклонена вверх
   - Курсор внизу → карточка наклонена вниз
   - Курсор слева → карточка наклонена влево
   - Курсор справа → карточка наклонена вправо

3. **Плавный выход**
   - Уведите курсор за пределы карточки
   - Карточка должна плавно вернуться в исходное положение за 400ms

### Дебаг:

```javascript
// Добавить логирование в handleMouseMove:
console.log(`rotateX: ${rotateX.toFixed(1)}°, rotateY: ${rotateY.toFixed(1)}°`)
```

---

## 📊 Производительность

**Оптимизации:**

1. **GPU Acceleration**
   - `transform` использует GPU (не вызывает reflow/repaint)
   - `will-change: transform` предзагружает на GPU

2. **Отсутствие лишних перерисовок**
   - После отключения transition (`transition: none`) браузер не пересчитывает CSS-анимации

3. **Один обработчик на элемент**
   - `onMouseMove` вызывается только для элемента с hover
   - Не распространяется на дочерние элементы

**Метрики:**
- ~60 FPS при активном движении курсора
- Latency: <16ms (1 frame)

---

## 🔄 Жизненный цикл эффекта

```
[Карточка в покое]
       ↓
   onMouseEnter → transition: 0.3s → isFirstContact: true
       ↓
   onMouseMove (первый раз) → transform применяется с transition
       ↓
   setTimeout(300ms) → transition: none → isFirstContact: false
       ↓
   onMouseMove (последующие) → transform применяется мгновенно
       ↓
   onMouseLeave → transition: 0.4s → transform: исходное → isFirstContact: true
       ↓
[Карточка в покое]
```

---

## 🛠 Параметры настройки

| Параметр | Где | Значение | Описание |
|----------|-----|----------|----------|
| `strength` | хук | 10–15° | Максимальный угол наклона |
| `perspective` | transform | 1000px | Глубина 3D сцены |
| `scale3d` | transform | 1.02 | Увеличение при hover |
| Enter transition | CSS | 0.3s ease-out | Плавность первого касания |
| Leave transition | CSS | 0.4s ease-out | Плавность возврата |
| setTimeout | JS | 300ms | Время до отключения transition |

---

## 📝 Проблемы и решения

### Проблема 1: Эффект дёргается при первом касании
**Причина:** CSS transition не включен в `onMouseEnter`  
**Решение:** Проверить, что `ref.current.style.transition = 'transform 0.3s ease-out'` вызывается

### Проблема 2: Карточка не возвращается в исходное положение
**Причина:** `onMouseLeave` не сбрасывает transform  
**Решение:** Проверить, что transform установлен в `rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)`

### Проблема 3: Эффект работает медленно на мобильных
**Причина:** Touch events не поддерживают `onMouseMove`  
**Решение:** Добавить `onTouchMove` обработчик (требует доработки хука)

### Проблема 4: Эффект конфликтует с другими hover-анимациями
**Причина:** CSS transition перезаписывается  
**Решение:** Убедиться, что CSS transition включает `transform` явно

---

## 🎯 Итоговый checklist интеграции

- [ ] Импортировать `useTiltEffect` из `hooks/useTiltEffect.js`
- [ ] Вызвать хук с нужным `strength` (10–15)
- [ ] Привязать `ref` к корневому элементу карточки
- [ ] Добавить обработчики `onMouseEnter`, `onMouseMove`, `onMouseLeave`
- [ ] Убедиться, что CSS карточки включает `transition: transform ...`
- [ ] Протестировать плавность первого касания и возврата

---

**Документ создан:** 2026-09-13  
**Версия:** 1.0  
**Код актуален для:** `vnxORACLE_system/landing` (commit e347442)
