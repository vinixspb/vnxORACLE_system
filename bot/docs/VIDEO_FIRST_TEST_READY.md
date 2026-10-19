# ✅ ГОТОВО К ПЕРВОМУ ТЕСТУ: Финальные корректировки

**Дата:** 2026-10-19  
**Статус:** Готов к production test  
**Изменения:** 2 критические корректировки выполнены

---

## ✅ КОРРЕКТИРОВКА #1: Исправление цен (завершено)

### Проблема:
Цены в меню и конфигурации не соответствовали фактическим тарифам OpenRouter для режима без звука (`generate_audio=false`).

### Исправлено:

| Модель | Было | Стало | Обоснование |
|--------|------|-------|-------------|
| Kling Pro | $0.168/s → $1.34/8s | $0.112/s → $0.90/8s | Официальная ставка 720p без звука |
| Veo Fast | $0.10/s → $0.80/8s | $0.08/s → $0.64/8s | Официальная ставка 720p без звука |
| Seedance 2.0 | $0.1512/s → $1.21/8s | Без изменений ✅ | Уже корректно |
| Seedance Fast | $0.09072/s → $0.73/8s | Без изменений ✅ | Уже корректно |
| Seedance Mini | $0.0756/s → $0.60/8s | Без изменений ✅ | Уже корректно |

### Изменённые файлы:

**1. config_video_models.py**
```python
# Kling Pro
"price_per_second": 0.112,  # было 0.168
"best_for": "... (~$0.90 за 8 сек)"  # было ~$1.34

# Veo Fast
"price_per_second": 0.08,  # было 0.10
"best_for": "... (~$0.64 за 8 сек)"  # было ~$0.80
```

**2. keyboards/ai_video.py**
```python
[InlineKeyboardButton("💎 Kling Pro — Качество ($0.90)", ...)],  # было $1.34
[InlineKeyboardButton("🎬 Veo Fast — Альтернатива ($0.64)", ...)],  # было $0.80
```

---

## ✅ КОРРЕКТИРОВКА #2: Отключение автоматического fallback (завершено)

### Проблема:
При временной ошибке OpenRouter (таймаут сети, temporary unavailable) автоматический fallback на KIE запускал вторую платную генерацию, что могло привести к двойному списанию.

### Решение:
Временно отключён автоматический fallback на KIE для первого теста. При ошибке OpenRouter бот покажет понятное сообщение пользователю и запишет ошибку в лог.

### Изменённые файлы:

**handlers/video.py** (2 места)

**1. handle_video_text_request() (строка ~138)**
```python
# ⚠️ ВРЕМЕННО ОТКЛЮЧЕНО для первого теста:
# Fallback на KIE может вызвать двойное списание при временной ошибке OpenRouter
# После успешного теста можно включить обратно

# if not video_url:
#     logger.warning(f"OpenRouter failed, trying KIE fallback...")
#     kie_model = getattr(config, 'VIDEO_KLING_3', "kling-3-motion-control")
#     video_url = await video_router.generate_video_kie_fallback(
#         prompt=safe_api_prompt,
#         model=kie_model
#     )
```

**2. handle_video_image_with_prompt() (строка ~293)**
```python
# ⚠️ ВРЕМЕННО ОТКЛЮЧЕНО для первого теста:
# Fallback на KIE может вызвать двойное списание при временной ошибке OpenRouter
# После успешного теста можно включить обратно

# if not video_url:
#     logger.warning(f"OpenRouter failed, trying KIE fallback...")
#     kie_model = getattr(config, 'VIDEO_KLING_3', "kling-3-motion-control")
#     video_url = await video_router.generate_video_kie_fallback(
#         prompt=safe_prompt,
#         model=kie_model,
#         source_image=image_path
#     )
```

### Что произойдёт при ошибке:

**Сейчас (fallback отключён):**
```
OpenRouter ошибка
    ↓
video_url = None
    ↓
Пользователю: "❌ Сбой рендеринга. Нейросеть отклонила запрос..."
    ↓
logger.error("Video generation error: ...")
    ↓
КОНЕЦ (одна попытка)
```

**После включения fallback (после успешного теста):**
```
OpenRouter ошибка
    ↓
video_url = None
    ↓
Автоматический запуск KIE
    ↓
Вторая платная генерация
    ↓
Риск двойного списания
```

---

## 🧪 ПЕРВЫЙ ТЕСТ: Инструкция

### Параметры теста:

```yaml
Модель: bytedance/seedance-2.0-mini
Режим: Image-to-Video
Фото: Любое (лучше портрет)
Промпт: "The person smiles and waves at the camera. Natural movement, static camera."
Параметры:
  resolution: 720p
  aspect_ratio: 16:9
  duration: 8 секунд
  generate_audio: false
Ожидаемая стоимость: ~$0.60
```

### Сценарий в Telegram:

```
1. /start
2. 🧩 Меню возможностей
3. 🎬 Видео AI
4. 🪙 Seedance Mini — Тесты ($0.60)
5. 🖼 Оживить картинку (Image2Video)
6. [Отправка фотографии через Telegram]
7. Написать: "The person smiles and waves at the camera. Natural movement, static camera."
8. Ожидание 2-5 минут
9. Получение MP4
```

### Что проверяется:

**Цепочка №1: Загрузка фото**
```
Telegram photo → bot.get_file() → download_to_drive() 
→ downloads/p_{user_id}_{uuid}.jpg
```

**Цепочка №2: Передача в OpenRouter**
```
image_path → _encode_image_to_base64() 
→ data:image/jpeg;base64,/9j/4AAQSkZJRg...
→ frame_images: [{"type": "image_url", "image_url": {"url": "data:..."}, "frame_type": "first_frame"}]
→ POST /api/v1/videos
```

**Цепочка №3: Polling статуса**
```
result.id → polling_url
→ GET polling_url (каждые 30s → 15s)
→ status: pending → in_progress → completed
→ unsigned_urls[0]
```

**Цепочка №4: Отправка результата**
```
video_url → bot.send_video(video=video_url)
→ Telegram скачивает MP4 → отправка пользователю
→ Кнопки: 🔄 Новое видео | 🔙 Главное меню
```

---

## 📊 CHECKLIST ПРИЁМКИ

### Must Have (обязательно):

- [ ] Фотография скачивается из Telegram
- [ ] Фото кодируется в base64
- [ ] OpenRouter принимает задание (возвращает job_id)
- [ ] Polling получает статус `completed`
- [ ] Возвращается URL видео (`unsigned_urls[0]`)
- [ ] MP4 отправляется обратно в Telegram
- [ ] Под видео показываются кнопки
- [ ] Кнопки работают корректно

### Nice to Have (желательно):

- [ ] Фактическая стоимость из `usage.cost` совпадает с ожидаемой (~$0.60)
- [ ] Длительность видео = 8 секунд
- [ ] Разрешение = 720p, 16:9
- [ ] DynamicWaitMessage корректно отображается
- [ ] Ошибки (если есть) логируются с полным стектрейсом

---

## 🚨 ЧТО ДЕЛАТЬ ПРИ ОШИБКЕ

### Если тест провалился:

**НЕ ДЕЛАТЬ:**
- ❌ Переписывать весь модуль наугад
- ❌ Добавлять новые функции
- ❌ Менять архитектуру

**ДЕЛАТЬ:**
1. ✅ Показать точную ошибку из логов (без API ключей)
2. ✅ Указать, на каком этапе сбой (загрузка фото, polling, отправка MP4)
3. ✅ Проверить response OpenRouter API
4. ✅ Исправить ТОЛЬКО выявленную проблему
5. ✅ Повторить тест

### Типичные ошибки и решения:

| Ошибка | Причина | Решение |
|--------|---------|---------|
| HTTP 401 | Неверный API ключ | Проверить `OPENROUTER_API_KEY` в .env |
| HTTP 400 | Неверный payload | Проверить структуру `frame_images` |
| HTTP 413 | Слишком большое фото | Проверить размер base64 (лимит ~10 МБ) |
| Timeout polling | Генерация > 10 минут | Увеличить `max_attempts` в video_router.py |
| Telegram error 413 | MP4 > 50 МБ | Скачать локально, затем отправить через `open()` |
| status: failed | Неверный промпт | Проверить `error` в response |

---

## 📋 ПОСЛЕ УСПЕШНОГО ТЕСТА

### Что делать дальше:

1. ✅ Проверить остальные 4 модели (Fast, Standard, Kling Pro, Veo Fast)
2. ✅ Проверить Text-to-Video
3. ⚙️ Включить fallback на KIE обратно (убрать комментарии)
4. ⚙️ Добавить сохранение `usage.cost` из OpenRouter
5. ⚙️ Добавить recovery незавершённых заданий (job_id в БД)
6. ⚙️ Добавить таймер автовыбора модели (20 секунд)
7. ⚙️ Добавить выбор длительности (4, 6, 8 секунд)

### Что НЕ ДЕЛАТЬ сразу:

- ❌ Upscale видео
- ❌ Редактирование видео
- ❌ Автоматический retry при ошибке
- ❌ Сложная аналитика расходов
- ❌ Дополнительные параметры (resolution, fps, audio)

---

## 🎯 СТАТУС ПРОЕКТА

**Готовность:** ✅ 100% (для первого теста)

**Изменённые файлы:**
- `config_video_models.py` — исправлены цены
- `keyboards/ai_video.py` — исправлены цены в меню
- `handlers/video.py` — отключён fallback на KIE

**Нетронутые модули:**
- ✅ Блок изображений (0 изменений)
- ✅ Блок текста (0 изменений)
- ✅ Блок аудио (0 изменений)
- ✅ OpenClaw (0 изменений)

**Следующий шаг:** Запустить бота и выполнить первый реальный тест Image-to-Video.

---

*Отчёт подготовлен Claude Code (Opus 5)*  
*Дата: 2026-10-19*  
*Время исправлений: 5 минут*  
*Статус: Готов к первому production test*
