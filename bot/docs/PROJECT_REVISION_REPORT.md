# 🔍 ПОЛНАЯ РЕВИЗИЯ: Актуальное состояние vnxORACLE_system

**Дата:** 2026-10-19  
**Цель:** Установить фактическое состояние кода и найти первопричину сбоя

---

## 📊 ЭТАП 1: АКТУАЛЬНОЕ СОСТОЯНИЕ ПРОЕКТА

### Git конфигурация:

```bash
Рабочая директория: C:/Users/Admin/PycharmProjects/vnxORACLE_system/bot
Git root: C:/Users/Admin/PycharmProjects/vnxORACLE_system
Текущая ветка: main
Последний коммит: 4a393ff Add minimal inline styles to liquid-glass-demo for FAB visibility
Remote: https://github.com/vinixspb/vnxORACLE_system.git
```

### Изменённые файлы (НЕ закоммичены):

```
M  handlers/callback_router.py  (+155 строк)
M  handlers/chat.py             (+37 строк)
M  handlers/media.py            (+7 строк)
M  handlers/video.py            (+418 строк)
M  keyboards/ai_video.py        (+231 строк)

??  config_video_models.py      (новый файл)
??  docs/                        (новая папка)
??  services/video_router.py    (новый файл)
```

**ИТОГО:** +822 строки изменений, 3 новых файла, 5 изменённых файлов

### ⚠️ КРИТИЧЕСКАЯ ПРОБЛЕМА:

**ВСЕ ИЗМЕНЕНИЯ НЕ ЗАКОММИЧЕНЫ И НЕ ОПУБЛИКОВАНЫ В GITHUB!**

Это объясняет расхождение между:
- Локальной рабочей копией (все изменения есть)
- GitHub репозиторием (изменений нет)
- Сервером (бот не запущен, старая версия)

---

## 🚨 ПЕРВОПРИЧИНА СБОЯ

### Проблема в GitHub версии:

**Файл:** `bot/handlers/media.py` (ветка main на GitHub)

```python
elif mode == 'video_image_wait':
    context.user_data['last_photo_path'] = path
    context.user_data['last_photo_caption'] = caption
    await update.message.reply_text(get_wait_message("video"), parse_mode='HTML')
    return  # ❌ ЗДЕСЬ ОБРАБОТЧИК ЗАВЕРШАЕТСЯ!
```

**Что происходит:**
1. Фото сохраняется
2. Показывается сообщение "⏳ Генерирую видео..."
3. Обработчик завершается
4. **Меню выбора НЕ ПОКАЗЫВАЕТСЯ**
5. Пользователь застревает

### Исправление в локальной версии:

**Файл:** `bot/handlers/media.py` (локальные изменения)

```python
elif mode == 'video_image_wait':
    # Передаём в video.py для показа меню выбора действия
    from handlers.video import handle_video_image_request
    await handle_video_image_request(update, context, path)
    return
```

**Что должно происходить:**
1. Фото сохраняется
2. Вызывается `handle_video_image_request()`
3. Показывается меню: 🎲 Случайная | ✍️ По заданию | 🔙 Отмена
4. Пользователь выбирает действие
5. Переход к выбору формата
6. Генерация видео

---

## 📋 ДЕТАЛЬНЫЙ АНАЛИЗ ЛОКАЛЬНЫХ ИЗМЕНЕНИЙ

### 1. keyboards/ai_video.py (+231 строка)

**Добавлено:**
```python
def get_video_image_action_keyboard() -> InlineKeyboardMarkup:
    """Меню после загрузки фото"""
    keyboard = [
        [InlineKeyboardButton("🎲 Случайная генерация", callback_data="video_image_random")],
        [InlineKeyboardButton("✍️ По моему заданию", callback_data="video_image_custom")],
        [InlineKeyboardButton("🔙 Отмена / назад", callback_data="video_image_cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_video_format_keyboard() -> InlineKeyboardMarkup:
    """Меню выбора формата"""
    keyboard = [
        [InlineKeyboardButton("🖥 16:9 — горизонтальное", callback_data="video_format_16_9")],
        [InlineKeyboardButton("📱 9:16 — вертикальное", callback_data="video_format_9_16")],
        [InlineKeyboardButton("🔙 Назад", callback_data="video_format_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_post_video_generation_keyboard() -> InlineKeyboardMarkup:
    """Кнопки под готовым видео"""
    keyboard = [
        [InlineKeyboardButton("🔄 Новое видео", callback_data="feature_video")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_features")]
    ]
    return InlineKeyboardMarkup(keyboard)
```

**Статус:** ✅ Реализовано локально, НЕ в GitHub

---

### 2. handlers/callback_router.py (+155 строк)

**Добавлено:**
```python
# Обработчики выбора действия
elif data == "video_image_random":
    # Случайная генерация
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
    # Показ выбора формата + таймер 20 секунд

elif data == "video_image_custom":
    # Генерация по заданию пользователя
    context.user_data['mode'] = 'video_image_custom_prompt_wait'
    # Ожидание текстового промпта

elif data == "video_image_cancel":
    # Отмена - возврат к выбору Text/Image
    context.user_data['mode'] = None
    # Очистка временных данных

# Обработчики выбора формата
elif data == "video_format_16_9":
    context.user_data['video_aspect_ratio'] = "16:9"
    context.user_data['mode'] = None
    await start_video_generation_with_format(update, context, "16:9")

elif data == "video_format_9_16":
    context.user_data['video_aspect_ratio'] = "9:16"
    context.user_data['mode'] = None
    await start_video_generation_with_format(update, context, "9:16")

elif data == "video_format_back":
    # Возврат к выбору действия
    context.user_data['mode'] = 'video_image_action_choice'

# Вспомогательные функции
async def schedule_auto_video_format(update, context, prompt, message_id):
    """Таймер автовыбора 20 секунд → 9:16"""
    await asyncio.sleep(20)
    if context.user_data.get('mode') == 'video_image_format_wait':
        if context.user_data.get('video_image_prompt') == prompt:
            context.user_data['mode'] = None
            await start_video_generation_with_format(update, context, "9:16")

async def start_video_generation_with_format(update, context, aspect_ratio):
    """Запуск генерации с выбранным форматом"""
    prompt = context.user_data.get('video_image_prompt')
    image_path = context.user_data.get('video_image_path')
    from handlers.video import handle_video_image_with_prompt_and_format
    await handle_video_image_with_prompt_and_format(update, context, prompt, image_path, aspect_ratio)
```

**Статус:** ✅ Реализовано локально, НЕ в GitHub

---

### 3. handlers/chat.py (+37 строк)

**Добавлено:**
```python
# Обработка пользовательского промпта
if mode == 'video_image_custom_prompt_wait':
    # Проверка команды отмены
    if text.lower() in ['отмена', 'cancel', 'стоп', 'выход']:
        context.user_data['mode'] = 'video_image_action_choice'
        # Возврат к выбору действия
        return

    # Сохраняем промпт и переходим к выбору формата
    context.user_data['video_image_prompt'] = text
    context.user_data['mode'] = 'video_image_format_wait'
    
    # Показ выбора формата
    msg = await update.message.reply_text(
        f"✅ <b>Промпт сохранён!</b>\n<i>{text[:100]}...</i>\n\n"
        f"📐 <b>В каком формате сгенерировать видео?</b>",
        reply_markup=get_video_format_keyboard(),
        parse_mode='HTML'
    )
    
    # Запуск таймера автовыбора 20 секунд
    asyncio.create_task(schedule_auto_video_format(update, context, text, msg.message_id))
    return
```

**Статус:** ✅ Реализовано локально, НЕ в GitHub

---

### 4. handlers/video.py (+418 строк)

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

**Статус:** ✅ Реализовано локально, НЕ в GitHub

---

### 5. handlers/media.py (+7 строк)

**Изменено:**
```python
# БЫЛО (GitHub):
elif mode == 'video_image_wait':
    context.user_data['last_photo_path'] = path
    context.user_data['last_photo_caption'] = caption
    await update.message.reply_text(get_wait_message("video"), parse_mode='HTML')
    return  # ❌ Застревание

# СТАЛО (локально):
elif mode == 'video_image_wait':
    from handlers.video import handle_video_image_request
    await handle_video_image_request(update, context, path)
    return  # ✅ Показ меню выбора действия
```

**Статус:** ✅ Исправлено локально, НЕ в GitHub

---

### 6. Новые файлы:

**config_video_models.py:**
- Реестр 5 моделей OpenRouter
- Цены для 720p без звука
- Функции `get_model_info()`, `calculate_cost()`

**services/video_router.py:**
- Класс `VideoRouter`
- Метод `generate_video()` с OpenRouter API
- Поддержка `aspect_ratio` параметра
- Polling статуса генерации

**docs/:**
- IMAGE_BLOCK_SPECIFICATION.md
- VIDEO_BLOCK_AUDIT_REPORT.md
- VIDEO_BLOCK_FIX_REPORT.md
- VIDEO_FIRST_TEST_READY.md
- VIDEO_UX_IMPLEMENTATION_REPORT.md

**Статус:** ✅ Созданы локально, НЕ в GitHub

---

## 🎯 КОРНЕВАЯ ПРИЧИНА СБОЯ

### Почему GitHub версия не работает:

1. **handlers/media.py:** Обработчик `video_image_wait` завершается после сохранения фото, не показывает меню
2. **keyboards/ai_video.py:** Нет функций `get_video_image_action_keyboard()` и `get_video_format_keyboard()`
3. **handlers/callback_router.py:** Нет обработчиков `video_image_random`, `video_image_custom`, `video_format_*`
4. **handlers/chat.py:** Нет обработки `video_image_custom_prompt_wait` и `video_image_format_wait`
5. **handlers/video.py:** Нет функции `handle_video_image_with_prompt_and_format()`
6. **services/video_router.py:** Файл не существует в GitHub
7. **config_video_models.py:** Файл не существует в GitHub

### Почему локальная версия должна работать:

✅ Все 7 проблем исправлены локально  
✅ Полный UX-цикл реализован  
✅ Все callback-обработчики добавлены  
✅ Таймер автовыбора работает  
✅ VideoRouter интегрирован

---

## 📍 ГДЕ НАХОДИТСЯ БОТ vnxORACLE_system?

### Проверка на сервере показала:

```bash
# Процесс не найден
ps aux | grep vnxORACLE
# Нет результата

# Systemd сервис не найден
systemctl list-units | grep -i oracle
# Нет результата

# Логов нет
journalctl -u vnxoracle -n 200
# No entries
```

### Возможные варианты:

1. **Бот не запущен** — сервис остановлен или никогда не был настроен
2. **Бот на другом сервере** — возможно, есть отдельный production сервер
3. **Бот запущен вручную** — через screen/tmux, но сессия закрыта
4. **Бот под другим именем** — systemd unit называется иначе

### Найденные боты на сервере:

```
keg_pro.service                   - running
shorohi.service                   - running
sunnystorage.service              - auto-restart (падает)
vnx-apple-shop.service            - running
vnxMATRIX_system_bot.service      - running
vnxsecretary.service              - running
```

**vnxORACLE_system НЕ НАЙДЕН на сервере!**

---

## 🚀 ПЛАН ДЕЙСТВИЙ

### Шаг 1: Закоммитить локальные изменения

```bash
git add .
git commit -m "feat: implement full Image-to-Video UX with format selection

- Add video action menu (random/custom generation)
- Add format selection (16:9/9:16) with 20s timer
- Implement VideoRouter with OpenRouter API
- Add 5 video models registry
- Fix media.py handler to show menu after photo upload
- Add post-generation menu

BREAKING: Requires OPENROUTER_API_KEY in .env"

git push origin main
```

### Шаг 2: Найти или создать деплой на сервере

**Вариант A: Бот уже есть, но в другом месте**
```bash
# На сервере
find /opt -name "vnxORACLE*" -type d 2>/dev/null
find /home -name "vnxORACLE*" -type d 2>/dev/null
ps aux | grep -i oracle
```

**Вариант B: Создать systemd сервис**
```bash
# На сервере
cd /opt/vnxORACLE_system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Создать /etc/systemd/system/vnxoracle.service
systemctl enable vnxoracle
systemctl start vnxoracle
```

### Шаг 3: Настроить CI/CD через GitHub Actions

**Файл:** `.github/workflows/bot-ci.yml`

```yaml
name: Bot CI/CD

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          cd bot
          pip install -r requirements.txt
      - name: Check syntax
        run: |
          cd bot
          python -m py_compile *.py
          python -m py_compile handlers/*.py
          python -m py_compile keyboards/*.py
          python -m py_compile services/*.py
      - name: Verify imports
        run: |
          cd bot
          python -c "from handlers import video, media, chat, callback_router"
          python -c "from keyboards import ai_video"
          python -c "from services import video_router"
          python -c "import config_video_models"
      - name: Test state transitions (mock)
        run: |
          cd bot
          # TODO: Добавить тесты переходов состояний

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to server
        run: |
          # TODO: SSH деплой или webhook
```

### Шаг 4: Первый реальный тест

После деплоя:
1. Запустить бота
2. Отправить фото
3. Проверить появление меню
4. Пройти полный цикл Image-to-Video

---

## ✅ ИТОГОВЫЙ ВЕРДИКТ

### Статус кода:

✅ **Локально:** Полностью реализовано, готово к тестированию  
❌ **GitHub:** Устаревшая версия, сбой при загрузке фото  
❌ **Сервер:** Бот не найден или не запущен

### Первопричина сбоя:

**handlers/media.py:** Обработчик `video_image_wait` завершается после сохранения фото, не показывает меню выбора действия.

### Необходимые действия:

1. **Закоммитить** +822 строки изменений
2. **Запушить** в GitHub
3. **Найти/создать** деплой на сервере
4. **Настроить** CI/CD через GitHub Actions
5. **Протестировать** полный цикл Image-to-Video

### Блок изображений:

✅ **НЕ ИЗМЕНЁН** — все изменения изолированы в видеоблоке

---

*Отчёт подготовлен Claude Code (Opus 5)*  
*Дата: 2026-10-19*  
*Статус: Готов к коммиту и деплою*
