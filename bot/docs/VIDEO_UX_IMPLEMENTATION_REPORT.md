# ✅ РЕАЛИЗАЦИЯ: UX Image-to-Video по образцу блока изображений

**Дата:** 2026-10-19  
**Статус:** Реализовано, готово к тестированию  
**Версия:** v2.0 (полный UX с выбором формата)

---

## 📊 РЕАЛИЗОВАННАЯ АРХИТЕКТУРА

### Полный граф Image-to-Video:

```
1. Пользователь отправляет фотографию
   ↓ handlers/media.py:214
   ↓ handle_video_image_request(image_path)

2. Показ меню выбора действия
   ↓ context.user_data['mode'] = 'video_image_action_choice'
   ↓ Кнопки: 🎲 Случайная | ✍️ По заданию | 🔙 Отмена

3A. СЦЕНАРИЙ A: Случайная генерация
   ↓ callback: video_image_random
   ↓ Выбор random промпта из 5 вариантов
   ↓ context.user_data['video_image_prompt'] = prompt
   ↓ Переход к шагу 4

3B. СЦЕНАРИЙ B: По заданию пользователя
   ↓ callback: video_image_custom
   ↓ context.user_data['mode'] = 'video_image_custom_prompt_wait'
   ↓ Пользователь пишет текст
   ↓ handlers/chat.py:342
   ↓ context.user_data['video_image_prompt'] = text
   ↓ Переход к шагу 4

4. Выбор формата видео (ОБЯЗАТЕЛЬНЫЙ ШАГ)
   ↓ context.user_data['mode'] = 'video_image_format_wait'
   ↓ Кнопки: 🖥 16:9 | 📱 9:16 | 🔙 Назад
   ↓ Таймер 20 секунд → автовыбор 9:16

5. Генерация видео
   ↓ callback: video_format_16_9 или video_format_9_16
   ↓ context.user_data['video_aspect_ratio'] = "16:9" или "9:16"
   ↓ handle_video_image_with_prompt_and_format(prompt, image_path, aspect_ratio)
   ↓ video_router.generate_video(..., aspect_ratio=aspect_ratio)

6. Отправка результата
   ↓ bot.send_video(video=url, reply_markup=post_generation_keyboard)
   ↓ Кнопки: 🔄 Новое видео | 🔙 Главное меню
```

---

## 🔧 ИЗМЕНЁННЫЕ ФАЙЛЫ

### 1. keyboards/ai_video.py (+26 строк)

**Добавлено:**
```python
def get_video_image_action_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора действия после загрузки фотографии
    """
    keyboard = [
        [InlineKeyboardButton("🎲 Случайная генерация", callback_data="video_image_random")],
        [InlineKeyboardButton("✍️ По моему заданию", callback_data="video_image_custom")],
        [InlineKeyboardButton("🔙 Отмена / назад", callback_data="video_image_cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_video_format_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора формата видео (аналог get_ratio_keyboard из блока изображений)
    """
    keyboard = [
        [InlineKeyboardButton("🖥 16:9 — горизонтальное", callback_data="video_format_16_9")],
        [InlineKeyboardButton("📱 9:16 — вертикальное", callback_data="video_format_9_16")],
        [InlineKeyboardButton("🔙 Назад", callback_data="video_format_back")]
    ]
    return InlineKeyboardMarkup(keyboard)
```

---

### 2. handlers/video.py (+120 строк)

**Изменено:**
```python
async def handle_video_image_request(update, context, image_path):
    """
    Показ меню выбора действия (НОВЫЙ UX)
    """
    # Сохраняем путь к фото
    context.user_data['video_image_path'] = image_path
    context.user_data['mode'] = 'video_image_action_choice'

    # Показываем меню выбора действия
    await update.message.reply_text(
        "🖼 <b>Фотография получена!</b>\n\n"
        "Теперь выберите, как оживить изображение:\n\n"
        "🎲 <b>Случайная генерация</b> — бот сам выберет подходящий вариант движения.\n"
        "✍️ <b>По моему заданию</b> — вы сами опишете, что должно происходить в видео.\n"
        "🔙 <b>Отмена / назад</b> — выйти из текущего сценария.",
        reply_markup=get_video_image_action_keyboard(),
        parse_mode='HTML'
    )
```

**Добавлено:**
```python
async def handle_video_image_with_prompt_and_format(update, context, prompt, image_path, aspect_ratio):
    """
    Генерация image-to-video с промптом и форматом (НОВЫЙ UX)
    
    Параметры:
    - prompt: текстовый промпт движения (случайный или пользовательский)
    - image_path: путь к загруженной фотографии
    - aspect_ratio: "16:9" или "9:16"
    """
    # Проверка цензуры
    safe_prompt = clean_prompt(prompt) if prompt != "/skip" else "natural motion"

    # Генерация через OpenRouter с выбранным форматом
    video_url = await video_router.generate_video(
        prompt=safe_prompt,
        model_key=model_key,
        tariff=tariff,
        source_image=image_path,
        duration=8,
        aspect_ratio=aspect_ratio  # ✅ Передаём выбранный формат
    )

    # Отправка с post-generation меню
    await context.bot.send_video(
        chat_id=user_id,
        video=video_url,
        caption=caption_text,
        parse_mode='HTML',
        reply_markup=get_post_video_generation_keyboard()
    )
```

---

### 3. handlers/callback_router.py (+80 строк)

**Добавлено:**
```python
# 🎬 Выбор действия после загрузки фото
elif data == "video_image_random":
    # Случайная генерация - выбираем случайный промпт
    random_prompts = [
        "The person smiles and waves at the camera. Natural movement, static camera.",
        "The person looks around curiously. Subtle head movement.",
        "The person reacts with surprise. Natural facial expression.",
        "The person makes a small gesture with their hand. Gentle motion.",
        "The person performs a simple comedic action. Deadpan expression."
    ]
    prompt = random.choice(random_prompts)
    context.user_data['video_image_prompt'] = prompt
    context.user_data['mode'] = 'video_image_format_wait'

    # Показываем выбранный промпт и формат
    msg = await query.message.reply_text(
        f"🎲 <b>Случайное действие выбрано:</b>\n<i>{prompt}</i>\n\n"
        f"📐 <b>В каком формате сгенерировать видео?</b>",
        reply_markup=get_video_format_keyboard(),
        parse_mode='HTML'
    )

    # Запускаем таймер автовыбора 20 секунд
    asyncio.create_task(schedule_auto_video_format(update, context, prompt, msg.message_id))

elif data == "video_image_custom":
    # Генерация по заданию пользователя
    context.user_data['mode'] = 'video_image_custom_prompt_wait'
    await query.message.reply_text(
        "✍️ <b>Опишите, что должно происходить в видео.</b>\n\n"
        "<i>Например: человек выглядывает из-за столба, смотрит налево и направо...</i>\n\n"
        "Для отмены напишите <b>\"Отмена\"</b>.",
        parse_mode='HTML'
    )

elif data == "video_image_cancel":
    # Отмена сценария - возврат к выбору Text/Image
    context.user_data['mode'] = None
    context.user_data.pop('video_image_path', None)
    context.user_data.pop('video_image_prompt', None)

# 🎬 Выбор формата видео
elif data == "video_format_16_9":
    context.user_data['video_aspect_ratio'] = "16:9"
    context.user_data['mode'] = None  # Предотвращаем дубли от таймера
    await start_video_generation_with_format(update, context, "16:9")

elif data == "video_format_9_16":
    context.user_data['video_aspect_ratio'] = "9:16"
    context.user_data['mode'] = None
    await start_video_generation_with_format(update, context, "9:16")

elif data == "video_format_back":
    # Возврат к выбору действия
    context.user_data['mode'] = 'video_image_action_choice'
    await _safe_menu_edit(query, context,
        "🖼 <b>Фотография сохранена!</b>\n\nВыберите, как оживить изображение:",
        get_video_image_action_keyboard()
    )

# Вспомогательные функции
async def schedule_auto_video_format(update, context, prompt, message_id):
    """
    Таймер автовыбора формата видео (20 секунд)
    """
    await asyncio.sleep(20)

    if context.user_data.get('mode') == 'video_image_format_wait':
        if context.user_data.get('video_image_prompt') == prompt:
            context.user_data['mode'] = None

            # Уведомление об автовыборе
            await context.bot.edit_message_text(
                chat_id=update.effective_user.id,
                message_id=message_id,
                text=f"⏱ Время истекло. Автовыбор: Вертикальный формат (9:16)",
                parse_mode='HTML'
            )

            # Запуск генерации с 9:16
            context.user_data['video_aspect_ratio'] = "9:16"
            await start_video_generation_with_format(update, context, "9:16")

async def start_video_generation_with_format(update, context, aspect_ratio):
    """
    Запуск генерации видео с выбранным форматом
    """
    prompt = context.user_data.get('video_image_prompt')
    image_path = context.user_data.get('video_image_path')

    from handlers.video import handle_video_image_with_prompt_and_format
    await handle_video_image_with_prompt_and_format(update, context, prompt, image_path, aspect_ratio)
```

---

### 4. handlers/chat.py (+35 строк)

**Добавлено:**
```python
# 🎬 РЕЖИМ ОЖИДАНИЯ ПОЛЬЗОВАТЕЛЬСКОГО ПРОМПТА (после "✍️ По моему заданию")
if mode == 'video_image_custom_prompt_wait':
    # Проверка команды отмены
    if text.lower() in ['отмена', 'cancel', 'стоп', 'выход']:
        context.user_data['mode'] = 'video_image_action_choice'
        from keyboards.ai_video import get_video_image_action_keyboard
        await update.message.reply_text(
            "✅ Отменено. Выберите действие снова:",
            reply_markup=get_video_image_action_keyboard(),
            parse_mode='HTML'
        )
        return

    # Сохраняем промпт и переходим к выбору формата
    context.user_data['video_image_prompt'] = text
    context.user_data['mode'] = 'video_image_format_wait'

    from keyboards.ai_video import get_video_format_keyboard
    msg = await update.message.reply_text(
        f"✅ <b>Промпт сохранён!</b>\n<i>{text[:100]}...</i>\n\n"
        f"📐 <b>В каком формате сгенерировать видео?</b>",
        reply_markup=get_video_format_keyboard(),
        parse_mode='HTML'
    )

    # Запускаем таймер автовыбора 20 секунд
    from handlers.callback_router import schedule_auto_video_format
    import asyncio
    asyncio.create_task(schedule_auto_video_format(update, context, text, msg.message_id))
    return
```

---

## 📋 СОСТОЯНИЯ (context.user_data['mode'])

| Режим | Триггер | Действие | След. состояние |
|-------|---------|----------|-----------------|
| `video_image_wait` | Нажатие "🖼 Оживить картинку" | Ожидание фото | `video_image_action_choice` |
| `video_image_action_choice` | Фото получено | Показ меню действий | `video_image_format_wait` (🎲) или `video_image_custom_prompt_wait` (✍️) |
| `video_image_custom_prompt_wait` | Нажатие "✍️ По моему заданию" | Ожидание текста | `video_image_format_wait` |
| `video_image_format_wait` | Промпт сохранён | Выбор формата + таймер 20с | `None` (генерация) |
| `None` | Выбор формата или таймаут | Генерация видео | - |

---

## 🎯 РЕАЛИЗОВАННЫЕ СЦЕНАРИИ

### СЦЕНАРИЙ A: Случайная генерация

```
Пользователь:
1. Отправляет фото
2. Нажимает "🎲 Случайная генерация"
3. Видит: "🎲 Случайное действие выбрано: The person smiles and waves..."
4. Нажимает "🖥 16:9"
5. Дожидается генерации
6. Получает MP4 с кнопками

Промпты (случайные):
- "The person smiles and waves at the camera. Natural movement, static camera."
- "The person looks around curiously. Subtle head movement."
- "The person reacts with surprise. Natural facial expression."
- "The person makes a small gesture with their hand. Gentle motion."
- "The person performs a simple comedic action. Deadpan expression."
```

### СЦЕНАРИЙ B: Генерация по заданию

```
Пользователь:
1. Отправляет фото
2. Нажимает "✍️ По моему заданию"
3. Пишет: "человек выглядывает из-за столба, смотрит налево и направо"
4. Видит: "✅ Промпт сохранён! ... 📐 В каком формате?"
5. Нажимает "📱 9:16"
6. Дожидается генерации
7. Получает MP4 с кнопками
```

---

## ✅ РЕАЛИЗОВАННЫЕ UX-ПАТТЕРНЫ

### 1. Циклическая архитектура ✅
- Всегда есть кнопка "🔙 Назад" или "🔙 Отмена"
- Команда "отмена" в текстовом режиме
- Возврат к предыдущему шагу без потери данных

### 2. Таймер автовыбора ✅
- 20 секунд на выбор формата
- Автовыбор 9:16 (как в блоке изображений)
- Отмена таймера при ручном выборе
- Уведомление об автовыборе

### 3. Сохранение контекста ✅
```python
context.user_data['video_image_path'] = image_path  # Путь к фото
context.user_data['video_image_prompt'] = prompt    # Промпт (случайный или свой)
context.user_data['video_aspect_ratio'] = "16:9"    # Выбранный формат
context.user_data['mode'] = 'video_image_...'       # Текущее состояние
```

### 4. Передача формата в API ✅
```python
video_url = await video_router.generate_video(
    prompt=safe_prompt,
    model_key=model_key,
    tariff=tariff,
    source_image=image_path,
    duration=8,
    aspect_ratio=aspect_ratio  # ✅ РЕАЛЬНО передаётся в OpenRouter
)
```

### 5. Предотвращение дублей ✅
```python
# Перед генерацией
context.user_data['mode'] = None  # Блокирует таймер

# В таймере
if context.user_data.get('mode') == 'video_image_format_wait':
    if context.user_data.get('video_image_prompt') == prompt:
        # Только если состояние и промпт актуальны
        await start_video_generation_with_format(...)
```

### 6. Очистка временных данных ✅
```python
# После генерации
context.user_data.pop('video_image_path', None)
context.user_data.pop('video_image_prompt', None)
context.user_data.pop('video_aspect_ratio', None)
```

---

## 🧪 ГОТОВНОСТЬ К ТЕСТИРОВАНИЮ

### Тест A: Случайная генерация

**Шаги:**
1. Запустить бота
2. 🧩 Меню возможностей → 🎬 Видео AI
3. Выбрать "🪙 Seedance Mini"
4. Нажать "🖼 Оживить картинку"
5. Отправить ЛЮБУЮ фотографию
6. Нажать "🎲 Случайная генерация"
7. Нажать "🖥 16:9"
8. Дождаться MP4

**Ожидаемый результат:**
- ✅ Видео приходит в Telegram
- ✅ Формат 16:9 (горизонтальное)
- ✅ Под видео кнопки: 🔄 Новое видео | 🔙 Главное меню

---

### Тест B: Генерация по заданию

**Шаги:**
1. Запустить бота
2. 🧩 Меню возможностей → 🎬 Видео AI
3. Выбрать "🪙 Seedance Mini"
4. Нажать "🖼 Оживить картинку"
5. Отправить ЛЮБУЮ фотографию
6. Нажать "✍️ По моему заданию"
7. Написать: "The person smiles and waves at the camera. Natural movement, static camera."
8. Нажать "📱 9:16"
9. Дождаться MP4

**Ожидаемый результат:**
- ✅ Видео приходит в Telegram
- ✅ Формат 9:16 (вертикальное)
- ✅ Движение соответствует промпту
- ✅ Под видео кнопки работают

---

### Тест C: Таймер автовыбора

**Шаги:**
1. Отправить фото
2. Нажать "🎲 Случайная генерация"
3. **НЕ НАЖИМАТЬ НИ ОДНУ КНОПКУ**
4. Подождать 20 секунд

**Ожидаемый результат:**
- ✅ Через 20 секунд: "⏱ Время истекло. Автовыбор: Вертикальный формат (9:16)"
- ✅ Автоматически запускается генерация с 9:16
- ✅ Видео приходит в формате 9:16

---

### Тест D: Кнопка "Назад"

**Шаги:**
1. Отправить фото
2. Нажать "✍️ По моему заданию"
3. Написать любой текст
4. Нажать "🔙 Назад" на экране выбора формата

**Ожидаемый результат:**
- ✅ Возврат к меню: 🎲 Случайная | ✍️ По заданию
- ✅ Фото и промпт сохранены
- ✅ Можно выбрать другое действие

---

### Тест E: Команда "Отмена"

**Шаги:**
1. Отправить фото
2. Нажать "✍️ По моему заданию"
3. Написать: "Отмена"

**Ожидаемый результат:**
- ✅ Сообщение: "✅ Отменено. Выберите действие снова:"
- ✅ Показ меню: 🎲 Случайная | ✍️ По заданию
- ✅ Фото сохранено

---

## 📊 СТАТИСТИКА ИЗМЕНЕНИЙ

| Файл | Строк добавлено | Функций добавлено |
|------|----------------|-------------------|
| `keyboards/ai_video.py` | +26 | 2 |
| `handlers/video.py` | +120 | 1 |
| `handlers/callback_router.py` | +80 | 2 |
| `handlers/chat.py` | +35 | 0 |
| **ИТОГО** | **+261** | **5** |

**Блок изображений:** ✅ Не тронут (0 изменений)

---

## ✅ ИТОГОВЫЙ ВЕРДИКТ

**Статус:** ✅ **Готов к полному тестированию**

**Реализовано:**
- ✅ Меню выбора действия (🎲 Случайная / ✍️ Своё)
- ✅ 5 случайных промптов для случайной генерации
- ✅ Ожидание пользовательского текста
- ✅ Обязательный выбор формата (16:9 / 9:16)
- ✅ Таймер автовыбора 20 секунд → 9:16
- ✅ Передача формата в OpenRouter API
- ✅ Кнопка "Назад" на каждом экране
- ✅ Команда "Отмена" в текстовом режиме
- ✅ Предотвращение дублей от таймера
- ✅ Post-generation меню
- ✅ Очистка временных данных

**Следующий шаг:** Запустить бота и протестировать оба сценария (A и B) + таймер + кнопку "Назад".

---

*Отчёт подготовлен Claude Code (Opus 5)*  
*Дата: 2026-10-19*  
*Время реализации: 30 минут*  
*Статус: Готов к production test v2.0*
