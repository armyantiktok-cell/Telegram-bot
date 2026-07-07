import logging
import os
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, WebAppInfo
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters, ContextTypes
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

ADMIN_ID = int(os.environ.get("ADMIN_CHAT_ID", "0"))
REVIEWS_LINK = os.environ.get("REVIEWS_LINK", "https://t.me/ARMYANua")
_domain = os.environ.get("REPLIT_DOMAINS", "")
WEBAPP_URL = f"https://{_domain}" if _domain else ""

MONOBANK_CARD = "4441 1111 3196 2080"
PUBG_ID_FOR_UC = "51230579110"

(
    CHOOSING_PAYMENT,
    WAITING_UAH_SCREENSHOT,
    WAITING_UAH_TG,
    WAITING_UAH_PUBG_ID,
    WAITING_UC_SCREENSHOT,
    WAITING_UC_TG,
) = range(6)


def main_menu_keyboard():
    rows = []
    if WEBAPP_URL:
        rows.append([InlineKeyboardButton("🚀 Открыть Mini App", web_app=WebAppInfo(url=WEBAPP_URL))])
    rows.append([InlineKeyboardButton("🎯 Индивидуальная настройка чувствительности", callback_data="sensitivity")])
    rows.append([InlineKeyboardButton("⭐ Отзывы", callback_data="reviews")])
    rows.append([InlineKeyboardButton("📩 Связаться со мной", callback_data="contact")])
    rows.append([InlineKeyboardButton("❓ Частые вопросы", callback_data="faq")])
    return InlineKeyboardMarkup(rows)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"Привет, <b>{name}</b>! 👋\n\n"
        "Я бот ARMYAN — помогаю игрокам PUBG MOBILE улучшить игру.\n\n"
        "Выбери, что тебя интересует:",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard()
    )


async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Выбери раздел:",
        reply_markup=main_menu_keyboard()
    )


async def sensitivity_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    text = (
        "🎯 <b>Индивидуальная настройка чувствительности PUBG MOBILE</b>\n\n"
        "✅ Настройка проводится лично в <b>голосовом звонке</b>\n"
        "✅ Связь через Telegram\n"
        "✅ Подходит для iPhone, iPad, Android-смартфонов и планшетов\n"
        "✅ Индивидуальный подход к каждому игроку\n\n"
        "💳 Стоимость:\n"
        "  • <b>800 грн</b> (Monobank)\n"
        "  • <b>1320 UC</b> (пополнение на PUBG ID)\n\n"
        "⚠️ <b>Важно:</b> сначала производится оплата, после чего мы договариваемся "
        "о времени и проводим настройку в голосовом звонке.\n\n"
        "Выбери способ оплаты:"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Оплатить гривнами (800 грн)", callback_data="pay_uah")],
        [InlineKeyboardButton("💎 Оплатить UC (1320 UC)", callback_data="pay_uc")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")],
    ])
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=keyboard)
    return CHOOSING_PAYMENT


async def pay_uah(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    text = (
        "💳 <b>Оплата гривнами — Monobank</b>\n\n"
        f"Номер карты:\n<code>{MONOBANK_CARD}</code>\n\n"
        "Сумма: <b>800 грн</b>\n\n"
        "После оплаты нажми кнопку ниже 👇"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Я оплатил", callback_data="paid_uah")],
        [InlineKeyboardButton("◀️ Назад", callback_data="sensitivity")],
    ])
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=keyboard)
    return CHOOSING_PAYMENT


async def pay_uc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    text = (
        "💎 <b>Оплата через UC</b>\n\n"
        "Пополни UC на PUBG ID:\n"
        f"<code>{PUBG_ID_FOR_UC}</code>\n\n"
        "Сумма: <b>1320 UC</b>\n\n"
        "После пополнения нажми кнопку ниже 👇"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Я оплатил", callback_data="paid_uc")],
        [InlineKeyboardButton("◀️ Назад", callback_data="sensitivity")],
    ])
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=keyboard)
    return CHOOSING_PAYMENT


async def paid_uah_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["payment_type"] = "UAH"
    await query.edit_message_text(
        "📸 Отлично! Пришли скриншот оплаты (фото квитанции из Monobank):"
    )
    return WAITING_UAH_SCREENSHOT


async def paid_uc_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["payment_type"] = "UC"
    await query.edit_message_text(
        "📸 Отлично! Пришли скриншот пополнения UC:"
    )
    return WAITING_UC_SCREENSHOT


async def uah_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message.photo:
        await update.message.reply_text("📸 Нужно прислать именно фото (скриншот). Попробуй снова:")
        return WAITING_UAH_SCREENSHOT

    context.user_data["screenshot"] = update.message.photo[-1].file_id
    await update.message.reply_text(
        "✅ Скриншот получен!\n\n"
        "📝 Теперь укажи свой <b>Telegram тег</b> (например: @username):",
        parse_mode="HTML"
    )
    return WAITING_UAH_TG


async def uah_tg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["tg_tag"] = update.message.text.strip()
    await update.message.reply_text(
        "🎮 Отлично! Последний шаг — укажи свой <b>PUBG ID</b>:",
        parse_mode="HTML"
    )
    return WAITING_UAH_PUBG_ID


async def uah_pubg_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["pubg_id"] = update.message.text.strip()
    await _finalize_payment(update, context)
    return ConversationHandler.END


async def uc_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message.photo:
        await update.message.reply_text("📸 Нужно прислать именно фото (скриншот). Попробуй снова:")
        return WAITING_UC_SCREENSHOT

    context.user_data["screenshot"] = update.message.photo[-1].file_id
    await update.message.reply_text(
        "✅ Скриншот получен!\n\n"
        "📝 Укажи свой <b>Telegram тег</b> (например: @username):",
        parse_mode="HTML"
    )
    return WAITING_UC_TG


async def uc_tg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["tg_tag"] = update.message.text.strip()
    await _finalize_payment(update, context)
    return ConversationHandler.END


async def _finalize_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = context.user_data
    payment_type = data.get("payment_type", "—")
    tg_tag = data.get("tg_tag", "—")
    pubg_id = data.get("pubg_id", "—")
    screenshot = data.get("screenshot")

    await update.message.reply_text(
        "✅ <b>Оплата получена.</b>\n\n"
        "В ближайшее время с вами свяжутся в Telegram для согласования времени настройки.\n\n"
        "Подготовьте устройство, на котором играете. 🎙️",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard()
    )

    if ADMIN_ID:
        caption_lines = [
            f"🆕 <b>Новая заявка!</b>",
            f"👤 Клиент: {user.full_name} (@{user.username or '—'}, ID: {user.id})",
            f"💰 Способ оплаты: <b>{'800 грн (Monobank)' if payment_type == 'UAH' else '1320 UC'}</b>",
            f"✈️ Telegram: <code>{tg_tag}</code>",
        ]
        if pubg_id and pubg_id != "—" and payment_type == "UAH":
            caption_lines.append(f"🆔 PUBG ID: <code>{pubg_id}</code>")

        caption = "\n".join(caption_lines)

        try:
            if screenshot:
                await context.bot.send_photo(
                    chat_id=ADMIN_ID,
                    photo=screenshot,
                    caption=caption,
                    parse_mode="HTML"
                )
            else:
                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=caption,
                    parse_mode="HTML"
                )
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление администратору: {e}")

    context.user_data.clear()


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "Действие отменено. Возвращаю в меню:",
        reply_markup=ReplyKeyboardRemove()
    )
    await update.message.reply_text(
        "Выбери раздел:",
        reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END


async def reviews_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Открыть отзывы", url=REVIEWS_LINK)],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")],
    ])
    await query.edit_message_text(
        "⭐ <b>Отзывы клиентов</b>\n\n"
        "Посмотри, что говорят другие игроки о настройке:",
        parse_mode="HTML",
        reply_markup=keyboard
    )


async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✉️ Написать @ARMYANua", url="https://t.me/ARMYANua")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")],
    ])
    await query.edit_message_text(
        "📩 <b>Связаться со мной</b>\n\n"
        "По всем вопросам пиши напрямую:\n"
        "Telegram: @ARMYANua",
        parse_mode="HTML",
        reply_markup=keyboard
    )


async def faq_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "❓ <b>Частые вопросы (FAQ)</b>\n\n"
        "❓ <b>Сколько длится настройка?</b>\n"
        "Обычно от 20 до 60 минут.\n\n"
        "❓ <b>Подходит ли настройка под мой девайс?</b>\n"
        "Да, настройка делается индивидуально под любое устройство.\n\n"
        "❓ <b>Нужно ли иметь гироскоп?</b>\n"
        "Нет, настройка возможна как с гироскопом, так и без него.\n\n"
        "❓ <b>Когда начинается работа?</b>\n"
        "Сразу после подтверждения оплаты и согласования времени."
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")],
    ])
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=keyboard)


async def unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Воспользуйся меню ниже 👇",
        reply_markup=main_menu_keyboard()
    )


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN не задан.")

    if not ADMIN_ID:
        logger.warning("ADMIN_CHAT_ID не задан — уведомления администратору отправляться не будут.")

    application = Application.builder().token(token).build()

    payment_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(sensitivity_handler, pattern="^sensitivity$"),
        ],
        states={
            CHOOSING_PAYMENT: [
                CallbackQueryHandler(pay_uah, pattern="^pay_uah$"),
                CallbackQueryHandler(pay_uc, pattern="^pay_uc$"),
                CallbackQueryHandler(paid_uah_start, pattern="^paid_uah$"),
                CallbackQueryHandler(paid_uc_start, pattern="^paid_uc$"),
                CallbackQueryHandler(sensitivity_handler, pattern="^sensitivity$"),
                CallbackQueryHandler(back_to_menu, pattern="^back_to_menu$"),
            ],
            WAITING_UAH_SCREENSHOT: [
                MessageHandler(filters.PHOTO, uah_screenshot),
                MessageHandler(filters.TEXT & ~filters.COMMAND, uah_screenshot),
            ],
            WAITING_UAH_TG: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, uah_tg),
            ],
            WAITING_UAH_PUBG_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, uah_pubg_id),
            ],
            WAITING_UC_SCREENSHOT: [
                MessageHandler(filters.PHOTO, uc_screenshot),
                MessageHandler(filters.TEXT & ~filters.COMMAND, uc_screenshot),
            ],
            WAITING_UC_TG: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, uc_tg),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("start", start),
        ],
        per_message=False,
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(payment_conv)
    application.add_handler(CallbackQueryHandler(back_to_menu, pattern="^back_to_menu$"))
    application.add_handler(CallbackQueryHandler(reviews_handler, pattern="^reviews$"))
    application.add_handler(CallbackQueryHandler(contact_handler, pattern="^contact$"))
    application.add_handler(CallbackQueryHandler(faq_handler, pattern="^faq$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_text))

    logger.info("Бот ARMYAN запускается...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
