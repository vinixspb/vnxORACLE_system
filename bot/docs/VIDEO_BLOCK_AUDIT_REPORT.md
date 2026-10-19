# 🔍 ОТЧЁТ: Проверка текущего состояния видеоблока

**Дата:** 2026-10-19  
**Цель:** Выявить незавершённые места перед минимальным рабочим запуском

---

## ✅ ЧТО УЖЕ РАБОТАЕТ

### 1. Созданные файлы:

- ✅ `config_video_models.py` (6,647 байт) — реестр 5 моделей
- ✅ `services/video_router.py` (12,750 байт) — VideoRouter с OpenRouter API
- ✅ `keyboards/ai_video.py` — обновлён (+199 строк)
- ✅ `handlers/video.py` — обновлён (+296 строк)
- ✅ `handlers/callback_router.py` — добавлены обработчики (+35 строк)
- ✅ `handlers/chat.py` — добавлены режимы (+6 строк)
- ✅ `handlers/media.py` — обработка фото для video (+7 строк)

### 2. Обработчики callback-кнопок:

```python
# handlers/callback_router.py

elif data == "feature_video":
    # Главное меню видео с 5 моделями
    await _safe_menu_edit(query, context, menu_text, get_video_menu_keyboard())

elif data.startswith("video_model_"):
    # Выбор модели → показ информации + режимы (Text/Image)
    model_key = data.replace("video_model_", "")
    await _safe_menu_edit(query, context, model_info_text, 
                         get_video_generation_keyboard(model_key))

elif data.startswith("video_text_"):
    # Text-to-Video с выбранной моделью
    model_key = data.replace("video_text_", "")
    await ask_video_prompt(update, context, "text", model_key)

elif data.startswith("video_image_"):
    # Image-to-Video с выбранной моделью
    model_key = data.replace("video_image_", "")
    await ask_video_prompt(update, context, "image", model_key)
```

### 3. Состояния (modes):

- ✅ `video_text_wait` — ожидание текстового промпта (chat.py:331)
- ✅ `video_image_wait` — ожидание фотографии (media.py:214)
- ✅ `video_image_prompt_wait` — ожидание промпта движения (chat.py:337)

### 4. Сохранение контекста:

```python
context.user_data['video_model'] = model_key  # Выбранная модель
context.user_data['mode'] = 'video_text_wait'  # Текущее состояние
```

---

## ⚠️ ВЫЯВЛЕННЫЕ ПРОБЛЕМЫ

### 1. **КРИТИЧНО: Нет обработки результата генерации**

**Проблема:** В `handlers/video.py` функции `handle_video_text_request()` и `handle_video_image_with_prompt()` вызывают `video_router.generate_video()`, но **не обрабатывают результат**.

**Текущий код:**
```python
# handlers/video.py (строка ~100)
result_url = await video_router.generate_video(
    prompt=safe_api_prompt,
    model_key=model_key,
    tariff=user_tariff
)

# ❌ ПРОБЛЕМА: после этого ничего не происходит!
# Нет отправки видео в Telegram
# Нет обработки ошибок
# Нет post-generation меню
```

**Что должно быть:**
```python
if result_url:
    # Скачать MP4
    # Отправить в Telegram
    # Показать post-generation меню
else:
    # Показать ошибку
    # Предложить fallback на KIE
```

### 2. **КРИТИЧНО: Нет скачивания и отправки MP4**

**Проблема:** `video_router.py` возвращает только URL, но нет кода для:
- Скачивания MP4 файла
- Отправки через `bot.send_video()`
- Показа кнопок под видео

**Необходимо добавить:**
```python
async def send_video_result(update, context, video_url, prompt, model_key):
    """Скачивание и отправка готового видео"""
    
    # Скачивание MP4
    async with aiohttp.ClientSession() as session:
        async with session.get(video_url) as resp:
            video_data = await resp.read()
    
    # Отправка в Telegram
    caption = f"🎬 Video by vnxORACLE\nModel: {model_name}\nPrompt: {prompt}"
    
    await context.bot.send_video(
        chat_id=user_id,
        video=video_data,
        caption=caption,
        reply_markup=get_post_video_generation_keyboard()
    )
```

### 3. **КРИТИЧНО: Нет post-generation меню**

**Проблема:** В `keyboards/ai_video.py` нет функции `get_post_video_generation_keyboard()` (аналог `get_post_generation_keyboard()` из блока изображений).

**Необходимо создать:**
```python
def get_post_video_generation_keyboard() -> InlineKeyboardMarkup:
    """Кнопки под готовым видео"""
    keyboard = [
        [InlineKeyboardButton("🔄 Новое видео", callback_data="feature_video")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_features")]
    ]
    return InlineKeyboardMarkup(keyboard)
```

### 4. **ВЫСОКИЙ ПРИОРИТЕТ: Нет обработки ошибок генерации**

**Проблема:** Если `video_router.generate_video()` возвращает `None` (ошибка), бот молча проглатывает ошибку.

**Необходимо добавить:**
```python
if not result_url:
    error_text = (
        "⚠️ <b>Ошибка генерации видео</b>\n\n"
        "OpenRouter временно недоступен. Попробуйте:\n"
        "• Повторить запрос через пару минут\n"
        "• Выбрать другую модель\n"
        "• Использовать Kling AI (KIE) как альтернативу"
    )
    await update.message.reply_text(error_text, parse_mode='HTML')
    return
```

### 5. **ВЫСОКИЙ ПРИОРИТЕТ: Нет сохранения пути к загруженному фото**

**Проблема:** В `handlers/video.py:handle_video_image_request()` фото загружается, но путь не сохраняется в `context.user_data`.

**Текущий код:**
```python
async def handle_video_image_request(update, context, image_path):
    # ❌ ПРОБЛЕМА: image_path не сохраняется!
    context.user_data['mode'] = 'video_image_prompt_wait'
```

**Исправление:**
```python
async def handle_video_image_request(update, context, image_path):
    context.user_data['video_source_image'] = image_path  # ✅ Сохранить
    context.user_data['mode'] = 'video_image_prompt_wait'
```

### 6. **СРЕДНИЙ ПРИОРИТЕТ: Неполная интеграция с существующим DynamicWaitMessage**

**Проблема:** В `video_router.py` используется `logger.info()` для отображения прогресса, но нет интеграции с `DynamicWaitMessage`.

**Текущий код:**
```python
# video_router.py
logger.info(f"⏳ Generation {status}... {progress}%")
```

**Должно быть:**
```python
# handlers/video.py
loader = DynamicWaitMessage(msg, "video")
loader.start()

try:
    result_url = await video_router.generate_video(...)
finally:
    loader.stop()
```

### 7. **СРЕДНИЙ ПРИОРИТЕТ: Упоминание 17 моделей вместо 5**

**Проблема:** В `handlers/video.py:1-4` написано "Полная поддержка всех 17 моделей", но фактически используется только 5.

**Исправление:**
```python
"""
🎬 ОБРАБОТЧИКИ ВИДЕО AI
Поддержка 5 моделей OpenRouter для производства фильма
"""
```

### 8. **НИЗКИЙ ПРИОРИТЕТ: Нет проверки capabilities модели**

**Проблема:** Не проверяется, поддерживает ли выбранная модель `image2video` перед запросом фото.

**Рекомендуется добавить:**
```python
model_info = get_model_info(model_key)
if "image2video" not in model_info.get("capabilities", []):
    await query.answer("⚠️ Эта модель не поддерживает Image-to-Video", show_alert=True)
    return
```

---

## 📋 МИНИМАЛЬНЫЙ СПИСОК ИСПРАВЛЕНИЙ ДЛЯ ПЕРВОГО ЗАПУСКА

### Обязательные изменения (без них не запустится):

1. ✅ **Добавить `get_post_video_generation_keyboard()`** в `keyboards/ai_video.py`
2. ✅ **Добавить скачивание и отправку MP4** в `handlers/video.py`
3. ✅ **Обработать результат `generate_video()`** — успех/ошибка
4. ✅ **Сохранить `video_source_image`** в `context.user_data`
5. ✅ **Получить сохранённое фото** в `handle_video_image_with_prompt()`
6. ✅ **Интегрировать `DynamicWaitMessage`** для анимации ожидания

### Желательные изменения (для стабильности):

7. ⚙️ Показ ошибки при сбое генерации
8. ⚙️ Проверка capabilities модели
9. ⚙️ Исправление комментария "17 моделей" → "5 моделей"

---

## 🧪 ПЛАН ПЕРВОГО ТЕСТА

### Сценарий: Image-to-Video через Seedance 2.0 Mini

**Путь пользователя:**
```
1. Нажать "🎬 Видео AI"
2. Выбрать "🪙 Seedance 2.0 Mini"
3. Нажать "🖼 Оживить картинку"
4. Отправить фотографию
5. Написать промпт: "The person smiles and waves"
6. Дождаться генерации (~2-5 минут)
7. Получить MP4 в Telegram
```

**Что должно произойти под капотом:**
```python
# 1. callback: video_model_seedance-2.0-mini
context.user_data['video_model'] = 'seedance-2.0-mini'

# 2. callback: video_image_seedance-2.0-mini
context.user_data['mode'] = 'video_image_wait'

# 3. Отправка фото
image_path = downloads/p_12345_abc123.jpg
context.user_data['video_source_image'] = image_path
context.user_data['mode'] = 'video_image_prompt_wait'

# 4. Текстовый промпт "The person smiles and waves"
await handle_video_image_with_prompt(update, context, prompt)

# 5. Генерация через OpenRouter
result_url = await video_router.generate_video(
    prompt="The person smiles and waves",
    model_key='seedance-2.0-mini',
    source_image=image_path,
    tariff='PRO'
)

# 6. Скачивание и отправка
await bot.send_video(chat_id=user_id, video=result_url, ...)
```

---

## 🚨 БЛОКЕРЫ ПЕРВОГО ЗАПУСКА

### Критические проблемы, без которых ничего не запустится:

1. ❌ **Нет отправки видео в Telegram** — результат генерации теряется
2. ❌ **Нет сохранения пути к фото** — Image-to-Video не может получить исходник
3. ❌ **Нет обработки результата** — успех/ошибка проглатываются молча
4. ❌ **Нет post-generation меню** — пользователь застревает после генерации

### Риски (могут проявиться после первого запуска):

- ⚠️ Неправильная передача фото в `frame_images` (нужна base64 или URL)
- ⚠️ Неверные параметры для конкретной модели (resolution, duration)
- ⚠️ Нет обработки статусов `cancelled`, `expired`
- ⚠️ Нет recovery после перезапуска бота (job_id теряется)

---

## ✅ РЕКОМЕНДУЕМЫЕ ДЕЙСТВИЯ

### Этап 1: Исправить критические блокеры (30 минут)

1. Добавить `get_post_video_generation_keyboard()` — **5 минут**
2. Добавить скачивание MP4 и `bot.send_video()` — **10 минут**
3. Сохранить/получить `video_source_image` — **5 минут**
4. Обработать результат `generate_video()` — **10 минут**

### Этап 2: Первый тест с реальным API ключом (10 минут)

1. Установить `OPENROUTER_API_KEY` в `.env`
2. Запустить бота
3. Пройти полный путь Image-to-Video
4. Проверить, что MP4 приходит в Telegram

### Этап 3: Доработка UX (20 минут)

1. Добавить `DynamicWaitMessage` — **5 минут**
2. Показ ошибки при сбое — **5 минут**
3. Проверка capabilities — **5 минут**
4. Кнопка "Отмена" в режимах wait — **5 минут**

---

## 📊 ИТОГОВАЯ ОЦЕНКА

| Компонент | Статус | Проблемы |
|-----------|--------|----------|
| Главное меню видео | ✅ Работает | Нет |
| Выбор из 5 моделей | ✅ Работает | Нет |
| Сохранение выбранной модели | ✅ Работает | Нет |
| Запрос промпта для text2video | ✅ Работает | Нет |
| Запрос фото для image2video | ✅ Работает | Нет |
| Запрос промпта движения | ✅ Работает | Нет |
| **Генерация через OpenRouter** | ⚠️ Не протестировано | Нужен API ключ |
| **Скачивание MP4** | ❌ Не реализовано | **БЛОКЕР** |
| **Отправка в Telegram** | ❌ Не реализовано | **БЛОКЕР** |
| **Post-generation меню** | ❌ Не реализовано | **БЛОКЕР** |
| Обработка ошибок | ❌ Не реализовано | Высокий приоритет |
| DynamicWaitMessage | ❌ Не реализовано | Средний приоритет |
| Recovery после перезапуска | ❌ Не реализовано | Низкий приоритет |

---

## 🎯 ВЫВОД

**Готовность к первому запуску:** ⚠️ **60%**

**Критические блокеры:** 4 шт.  
**Время на исправление:** ~30 минут  
**После исправления:** готов к тесту с реальным API

**Рекомендация:** Сначала исправить 4 критических блокера, затем сразу тестировать с реальным OpenRouter API ключом.

---

*Отчёт подготовлен Claude Code (Opus 5)*  
*Дата: 2026-10-19*
