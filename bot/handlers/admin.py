from telegram import Update
from telegram.ext import ContextTypes
import config
from loader import sheets_mgr, db, USER_MODELS
import keyboards

async def send_paywall(update: Update):
    await update.message.reply_text(config.MSG_NO_SUB, reply_markup=keyboards.get_subscription_keyboard(), parse_mode='HTML')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    user = update.effective_user
    user_id = user.id
    
    tariff = sheets_mgr.get_user_tariff(user_id)
    if not tariff:
        await update.message.reply_text(config.MSG_NO_SUB, reply_markup=keyboards.get_subscription_keyboard(), parse_mode='HTML')
        return
    
    db.create_session(user_id, title="Новый чат")
    first_name = user.first_name or "Пользователь"
    
    await update.message.reply_text("🖥 <b>Терминал запущен.</b>", reply_markup=keyboards.get_main_keyboard(), parse_mode='HTML')
    
    welcome_text = (
        f"👋 <b>Здравствуйте, {first_name}!</b>\n\n"
        "Я — <b>vnxORACLE</b>, ваш персональный нейро-ассистент.\n"
        "👇 <b>С чего начнем?</b>"
    )
    await update.message.reply_text(welcome_text, reply_markup=keyboards.get_features_keyboard(), parse_mode='HTML')

async def show_profile(update: Update, user_id: int):
    user_tariff = sheets_mgr.get_user_tariff(user_id)
    if not user_tariff: return
    
    status = f"✅ {user_tariff}"
    total_tokens = db.get_total_tokens(user_id)
    current_model = USER_MODELS.get(user_id, config.DEFAULT_MODEL)
    
    text = (
        f"👤 <b>МОЙ ПРОФИЛЬ</b>\n"
        f"ID: <code>{user_id}</code>\n"
        f"Статус: <b>{status}</b>\n"
        f"Расход токенов: <b>{total_tokens}</b>\n"
        f"Активная модель: <code>{current_model}</code>"
    )
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=keyboards.get_profile_keyboard(), parse_mode='HTML')
    else:
        await update.message.reply_text(text, reply_markup=keyboards.get_profile_keyboard(), parse_mode='HTML')
