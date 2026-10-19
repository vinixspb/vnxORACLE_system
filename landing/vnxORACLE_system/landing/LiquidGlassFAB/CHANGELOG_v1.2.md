# 🔧 CHANGELOG v1.2.0 - Bug Fixes & Canon Restoration

## Критические исправления

### ✅ ЗАДАЧА 1: Устранение утечки таймеров
**Проблема:** `destroy()` не очищал активные `setTimeout`, оставляя висящие замыкания в памяти.

**Решение:**
```javascript
// Добавлено в constructor
this.timers = []

// Все setTimeout теперь отслеживаются
const squashTimer = setTimeout(() => { ... }, 150)
this.timers.push(squashTimer)

const rippleTimer = setTimeout(() => { ... }, 800)
this.timers.push(rippleTimer)

const entranceTimer = setTimeout(() => { ... }, 1600)
this.timers.push(entranceTimer)

// В destroy() добавлена очистка
this.timers.forEach(timerId => clearTimeout(timerId))
this.timers = []
```

**Результат:** Все 3 таймера (squash 150ms, ripple 800ms, entrance 1600ms) корректно очищаются при вызове `destroy()`.

---

### ✅ ЗАДАЧА 2: Пропорциональное масштабирование физики
**Проблема:** `shineOffsetX/Y` и `parallaxX/Y` использовали фиксированные множители `* 0.15` и `* 0.12`, игнорируя размер кнопки.

**Было:**
```javascript
const shineOffsetX = (normX - 50) * 0.15  // Всегда одинаковое смещение в пикселях
const parallaxX = (normX - 50) * 0.12
```

**Стало:**
```javascript
// Смещение пропорционально размеру кнопки
const shineOffsetX = ((normX - 50) / 100) * this.options.size * 0.15
const shineOffsetY = ((normY - 50) / 100) * this.options.size * 0.15

const parallaxX = ((normX - 50) / 100) * this.options.size * 0.12
const parallaxY = ((normY - 50) / 100) * this.options.size * 0.12
```

**Результат:** 
- Кнопка 80px: shine смещается на ±6px, parallax на ±4.8px
- Кнопка 160px: shine смещается на ±12px, parallax на ±9.6px
- Физика масштабируется строго пропорционально

---

### ✅ ЗАДАЧА 3: Восстановление визуального канона
**Проблема:** Упрощение backdrop-filter и overflow: hidden ломали оригинальный визуал.

**Изменения в CSS:**

1. **overflow: visible** (было: hidden)
```css
.liquid-glass-fab {
    overflow: visible;  /* Ripple и тени не обрезаются */
}
```

2. **Полный backdrop-filter** (был упрощён)
```css
/* Было */
backdrop-filter: blur(12px);

/* Восстановлено */
backdrop-filter: blur(28px) saturate(160%) brightness(1.05);
-webkit-backdrop-filter: blur(28px) saturate(160%) brightness(1.05);
```

**Результат:** 100% совпадение с исходным каноном 325 строк.

---

### ✅ ЗАДАЧА 4: Модернизация Test 10
**Проблема:** Тест проверял `console.error`, а не реальную очистку таймеров.

**Новая реализация:**
- Mock нативных `setTimeout` и `clearTimeout`
- Трекинг всех созданных таймеров в `Map`
- Проверка количества активных таймеров после `destroy()`
- Детальный лог каждого таймера (ID, delay, stack trace)

**Новый файл:** `tests/test10-timer-leak-detection.html`

**Возможности:**
- ▶ Run Test - одиночный тест
- 💥 Spam Test (10x) - стресс-тест
- Live статистика: Created / Cleared / Leaked
- Детальный лог утечек с stack trace

**Критерий провала:** Leaked > 0 после `destroy()`

---

## Проверка исправлений

### Test 7: Instance State Snapshot
✅ Пропорциональная физика не нарушает изоляцию экземпляров

### Test 8: CSS Hostility  
✅ `overflow: visible` не конфликтует с BEM-изоляцией

### Test 9: Stacking & Layout
✅ Восстановленный backdrop-filter работает в сложных DOM-структурах

### Test 10: Timer Leak Detection
✅ Все 3 таймера корректно очищаются в destroy()

---

## Файлы изменены

1. `src/LiquidGlassFAB.js` - версия обновлена на 1.2.0
2. `src/liquid-glass-fab.css` - восстановлен канон
3. `tests/test10-timer-leak-detection.html` - новый тест (создан)

---

## Статус

**v1.2.0 готов к повторному аудиту.**

Все 4 критических дефекта устранены:
- ✅ Таймеры очищаются
- ✅ Физика пропорциональна
- ✅ Визуал восстановлен
- ✅ Test 10 проверяет реальную очистку
