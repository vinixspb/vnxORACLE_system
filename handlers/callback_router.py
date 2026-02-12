from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
import config
from loader import sheets_mgr, db, USER_MODELS
import keyboards
from .admin import show_profile

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    if data == "profile_tariffs":
        tariffs_text = "\n\n".join(config.TARIFF_INFO.values())
        await query.edit_message_text(f"{tariffs_text}\n\n👇 <b>Выберите тариф:</b>", reply_markup=keyboards.get_subscription_keyboard(), parse_mode='HTML')
    elif data == "profile_support":
        await query.edit_message_text(config.MSG_SUPPORT, parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_to_profile")]]))
    elif data == "back_to_profile":
        await show_profile(update, user_id)
    elif data.startswith("buy_"):
        plan = data.split("_")[1]
        await query.edit_message_text(f"💳 <b>Оплата тарифа {plan}</b>\n\n{config.PAYMENT_INFO}", parse_mode='HTML')

    elif data == "history_manage":
        await query.edit_message_reply_markup(reply_markup=keyboards.get_history_keyboard(user_id, mode="delete"))
    elif data == "history_back":
        await query.edit_message_reply_markup(reply_markup=keyboards.get_history_keyboard(user_id, mode="view"))
    elif data.startswith("del_"):
        db.delete_session(user_id, int(data.split("_")[1]))
        await query.answer("🗑 Удалено")
        markup = keyboards.get_history_keyboard(user_id, mode="delete")
        if markup: await query.edit_message_reply_markup(reply_markup=markup)
        else: await query.edit_message_text("📂 Архив пуст.", reply_markup=keyboards.get_features_keyboard())
    elif data.startswith("session_"):
        db.activate_session(user_id, int(data.split("_")[1]))
        await query.message.reply_text("📂 <b>Диалог восстановлен.</b>", parse_mode='HTML')

    elif data == "feature_text":
        context.user_data['mode'] = None
        curr = USER_MODELS.get(user_id, config.DEFAULT_MODEL)
        await query.edit_message_text("💡 <b>ВЫБОР МОДЕЛИ:</b>", reply_markup=keyboards.get_models_keyboard(curr), parse_mode='HTML')
    elif data.startswith("setmodel_"):
        new_model = data.split("setmodel_")[1]
        USER_MODELS[user_id] = new_model
        context.user_data['mode'] = None
        try: await query.message.delete()
        except: pass
        model_name = next((name for name, code in config.MODELS_LIST if code == new_model), new_model)
        await context.bot.send_message(chat_id=user_id, text=f"🧠 <b>Модель:</b> {model_name}", parse_mode='HTML')

    elif data == "feature_design":
        context.user_data['mode'] = None
        curr_img = context.user_data.get('img_model', config.DEFAULT_IMG_MODEL)
        await query.edit_message_text("🎨 <b>СТУДИЯ ДИЗАЙНА</b>", reply_markup=keyboards.get_image_models_keyboard(user_id, curr_img), parse_mode='HTML')
    elif data.startswith("setimg_"):
        new_model = data.split("setimg_")[1]
        context.user_data['img_model'] = new_model
        context.user_data['mode'] = 'img_wait'
        try: await query.message.delete()
        except: pass
        await context.bot.send_message(chat_id=user_id, text=f"🎨 <b>Модель:</b> <code>{new_model}</code>\nОпишите изображение:", parse_mode='HTML')

    elif data == "feature_audio":
        await query.edit_message_text("🎤 <b>АУДИО СЕРВИСЫ:</b>", reply_markup=keyboards.get_audio_keyboard(), parse_mode='HTML')
    elif data == "audio_tts":
        await query.edit_message_text("🗣 <b>ВЫБЕРИТЕ ГОЛОС:</b>", reply_markup=keyboards.get_voice_selection_keyboard(), parse_mode='HTML')
    elif data.startswith("setvoice_"):
        context.user_data['voice_id'] = data.split("setvoice_")[1]
        context.user_data['mode'] = 'tts_wait'
        await query.answer("🎙 Голос выбран")
        await query.message.reply_text("🗣 <b>Режим диктора.</b>\nПришлите текст:", parse_mode='HTML')
    elif data == "audio_tts_again":
        context.user_data['mode'] = 'tts_wait'
        await query.message.reply_text("🎤 Жду текст:", parse_mode='HTML')
    elif data == "audio_sfx":
        context.user_data['mode'] = 'sfx_wait'
        await query.message.reply_text("🔊 <b>Опишите звук (на англ):</b>", parse_mode='HTML')
    
    elif data == "mode_chat_reset":
        context.user_data['mode'] = None
        db.create_session(user_id, title="Новый диалог")
        await query.message.reply_text("💬 <b>Текстовый режим.</b>", parse_mode='HTML')
    elif data == "back_to_features":
        await query.edit_message_text("🧩 <b>МЕНЮ ВОЗМОЖНОСТЕЙ:</b>", reply_markup=keyboards.get_features_keyboard(), parse_mode='HTML')
    
    try: await query.answer()
    except: pass
