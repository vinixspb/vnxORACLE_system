import os
import logging
import random
import aiohttp
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

import config
from loader import sheets_mgr, ai_engine, db, USER_MODELS
import keyboards

logger = logging.getLogger(__name__)

# --- ВСПОМОГАТЕЛЬНЫЕ ---
async def send_paywall(update: Update):
    await update.message.reply_text(config.MSG_NO_SUB, reply_markup=keyboards.get_subscription_keyboard(), parse_mode='HTML')

async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str):
    user_id = update.effective_user.id
    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.UPLOAD_PHOTO)
    enhanced_prompt = f"{prompt}, highly detailed, 8k, cinematic lighting"
    seed = random.randint(1, 999999)
    image_url = f"https://image.pollinations.ai/prompt/{enhanced_prompt}?seed={seed}&width=1024&height=1024&nologo=true"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    await update.message.reply_photo(
                        photo=data, 
                        caption=f"🎨 <b>Art by vnxORACLE</b>\nPrompt: <i>{prompt}</i>",
                        parse_mode='HTML'
                    )
                else:
                    await update.message.reply_text("⚠️ Сбой визуализации.")
    except Exception as e:
        logger.error(f"Img Error: {e}")
        await update.message.reply_text("⚠️ Ошибка связи с ИИ.")

async def process_ai_request(update: Update, context: ContextTypes.DEFAULT_TYPE, input_text: str):
    user_id = update.effective_user.id
    user_tariff = sheets_mgr.get_user_tariff(user_id)
    if not user_tariff: return await send_paywall(update)

    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
    session_id = db.get_active_session(user_id)
    
    # Авто-заголовок (первые 30 символов первого сообщения)
    history = db.get_history(session_id, limit=1)
    if not history:
        db.update_session_title(session_id, input_text[:30])
    
    db.add_message(session_id, "user", input_text)
    history_depth = config.LIMITS.get(user_tariff, 10)
    full_context = db.get_history(session_id, limit=history_depth)
    model = USER_MODELS.get(user_id, config.DEFAULT_MODEL)

    try:
        ai_response, tokens_spent = await ai_engine.get_response(full_context, model)
        db.add_message(session_id, "assistant", ai_response, model=model)
        db.update_tokens(user_id, tokens_spent)
        model_name = model.split('/')[-1]
        final_text = (f"{ai_response}\n\n<blockquote>⚙️ {model_name} | 🎫 {tokens_spent} | ∑ {db.get_total_tokens(user_id)}</blockquote>")
        await update.message.reply_text(final_text, parse_mode='HTML')
    except Exception as e:
        logger.error(f"AI Error: {e}")
        await update.message.reply_text("⚠️ Ошибка связи.")

# --- ХЕНДЛЕРЫ ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    tariff = sheets_mgr.get_user_tariff(user.id)
    if not tariff:
        await update.message.reply_text(config.MSG_WELCOME, parse_mode='HTML')
        await update.message.reply_text(config.MSG_NO_SUB, reply_markup=keyboards.get_subscription_keyboard(), parse_mode='HTML')
        return
    db.create_session(user.id, title="Новый чат")
    await update.message.reply_text(f"👁 <b>Доступ разрешен.</b>\nВаш уровень: <b>{tariff}</b>", reply_markup=keyboards.get_main_keyboard(), parse_mode='HTML')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    user_tariff = sheets_mgr.get_user_tariff(user_id)

    # Защита системных команд
    sys_buttons = [config.BTN_NEW_DIALOG, config.BTN_HISTORY, config.BTN_PROFILE, config.BTN_TARIFFS, config.BTN_CHANGE_MODEL, config.BTN_HELP]

    if text.startswith("/img "):
        if not user_tariff: return await send_paywall(update)
        await generate_image(update, context, text[5:])
        return

    if text in sys_buttons:
        if not user_tariff: return await send_paywall(update)
        
        if text == config.BTN_HISTORY:
            markup = keyboards.get_history_keyboard(user_id, mode="view")
            if not markup: await update.message.reply_text("📂 Архив пуст.")
            else: await update.message.reply_text("💾 <b>ИСТОРИЯ ЧАТОВ:</b>\nВыберите сессию для загрузки данных.", reply_markup=markup, parse_mode='HTML')
            return

        if text == config.BTN_NEW_DIALOG:
            db.create_session(user_id, title="Новый диалог")
            await update.message.reply_text("♻️ <b>Новый диалог создан.</b>", parse_mode='HTML')
            return

        if text == config.BTN_PROFILE:
            curr = USER_MODELS.get(user_id, config.DEFAULT_MODEL).split('/')[-1]
            await update.message.reply_text(f"👤 <b>ПРОФИЛЬ</b>\nСтатус: {user_tariff}\nМодель: <code>{curr}</code>", parse_mode='HTML')
            return

        if text == config.BTN_TARIFFS:
            await update.message.reply_text("💳 <b>ТАРИФНЫЕ ПЛАНЫ:</b>", reply_markup=keyboards.get_subscription_keyboard(), parse_mode='HTML')
            return

        if text == config.BTN_CHANGE_MODEL:
            await update.message.reply_text("🧩 <b>МЕНЮ ВОЗМОЖНОСТЕЙ:</b>", reply_markup=keyboards.get_features_keyboard(), parse_mode='HTML')
            return

        if text == config.BTN_HELP:
            await update.message.reply_text(config.MSG_SUPPORT, parse_mode='HTML')
            return
        return

    await process_ai_request(update, context, text)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    
    # Режимы истории
    if data == "history_manage":
        markup = keyboards.get_history_keyboard(user_id, mode="delete")
        await query.edit_message_text("🗑 <b>РЕЖИМ УДАЛЕНИЯ:</b>\nВыберите чат для стирания.", reply_markup=markup, parse_mode='HTML')
    elif data == "history_back":
        markup = keyboards.get_history_keyboard(user_id, mode="view")
        await query.edit_message_text("💾 <b>ИСТОРИЯ ЧАТОВ:</b>", reply_markup=markup, parse_mode='HTML')
    
    # Навигация хаба
    elif data == "back_to_features":
        await query.edit_message_text("🧩 <b>МЕНЮ ВОЗМОЖНОСТЕЙ</b>", reply_markup=keyboards.get_features_keyboard(), parse_mode='HTML')
    elif data == "feature_text":
        curr = USER_MODELS.get(user_id, config.DEFAULT_MODEL)
        await query.edit_message_text("💡 <b>НЕЙРОСЕТЬ:</b>", reply_markup=keyboards.get_models_keyboard(curr), parse_mode='HTML')
    
    # Действия
    elif data.startswith("setmodel_"):
        USER_MODELS[user_id] = data.split("_")[1]
        await query.answer("🧠 Изменено")
        await query.edit_message_text(f"✅ <b>Модель:</b> {USER_MODELS[user_id]}", parse_mode='HTML')
    elif data.startswith("del_"):
        if db.delete_session(user_id, int(data.split("_")[1])):
            await query.answer("🗑 Удалено")
            markup = keyboards.get_history_keyboard(user_id, mode="delete")
            if markup: await query.edit_message_reply_markup(reply_markup=markup)
            else: await query.edit_message_text("📂 Архив пуст.")
    elif data.startswith("session_"):
        if db.activate_session(user_id, int(data.split("_")[1])):
            await query.answer()
            await query.message.reply_text(f"📂 <b>Чат загружен.</b>", parse_mode='HTML')
    elif data.startswith("buy_"):
        plan = data.split("_")[1]
        await query.edit_message_text(f"{config.TARIFF_INFO[plan]}\n\n💳 <b>Оплата:</b> {config.PAYMENT_INFO}", parse_mode='HTML')

    await query.answer()

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if config.ARCHIVE_CHANNEL_ID:
        try:
            await context.bot.forward_message(chat_id=config.ARCHIVE_CHANNEL_ID, from_chat_id=update.effective_user.id, message_id=update.message.message_id)
            await update.message.reply_text("✅ <b>Объект сохранен.</b>", parse_mode='HTML')
        except: pass
