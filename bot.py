import fcntl
import json
import logging
import os
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
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
ADMIN_IDS = {ADMIN_ID} if ADMIN_ID > 0 else set()
REVIEWS_LINK = os.environ.get("REVIEWS_LINK", "https://t.me/ARMYANua")

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
ORDERS_FILE = DATA_DIR / "orders.json"
ORDERS_LOCK_FILE = DATA_DIR / "orders.lock"


@contextmanager
def _orders_lock():
    with open(ORDERS_LOCK_FILE, "w") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lf, fcntl.LOCK_UN)


def _load_orders():
    if ORDERS_FILE.exists():
        try:
            return json.loads(ORDERS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def _save_orders(orders):
    tmp = ORDERS_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(orders, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(ORDERS_FILE)


def save_order(order):
    with _orders_lock():
        orders = _load_orders()
        orders.append(order)
        _save_orders(orders)


def set_order_status(order_id, status):
    """Возвращает 'updated', 'already' или 'missing'."""
    with _orders_lock():
        orders = _load_orders()
        for o in orders:
            if o.get("id") == order_id:
                if o.get("status") in ("done", "cancelled"):
                    return "already"
                o["status"] = status
                _save_orders(orders)
                return "updated"
        return "missing"


_domain = os.environ.get("REPLIT_DOMAINS", "")
WEBAPP_URL = os.environ.get("WEBAPP_URL", f"https://{_domain}" if _domain else "")

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
    rows.append([InlineKeyboardButton("📩 Поддержка", callback_data="contact")])
    rows.append([InlineKeyboardButton("❓ Частые вопросы", callback_data="faq")])
    return InlineKeyboardMarkup(rows)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"Привет, <b>{name}</b>! 👋\n\n"
        "Добро пожаловать в <b>ARMYAN SERVICES</b>\n\n"
        "Здесь вы можете быстро и удобно заказать любые мои услуги по PUBG MOBILE, "
        "ознакомиться с отзывами и получить всю необходимую информацию в одном месте.\n\n"
        "⚡ Для вашего удобства доступно мини-приложение, которое поможет оформить заказ всего за пару кликов.\n\n"
        "✅ Индивидуальная настройка чувствительности\n"
        "✅ Буст ранга\n"
        "✅ Поддержка клиентов\n"
        "✅ Быстрое оформление заказов\n\n"
        "🕒 Работаем 24/7 – заявки принимаются круглосуточно.\n\n"
        "Выберите интересующий вас раздел ниже:",
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

    order_id = uuid.uuid4().hex[:12].upper()
    price_label = "800 грн (Monobank)" if payment_type == "UAH" else "1320 UC"
    amount = "800 грн" if payment_type == "UAH" else "1320 UC"

    save_order({
        "id": order_id,
        "timestamp": int(time.time()),
        "user_name": user.full_name,
        "user_id": str(user.id),
        "tg_tag": tg_tag,
        "pubg_id": pubg_id if pubg_id != "—" else "",
        "payment_type": payment_type,
        "price_label": price_label,
        "status": "new",
    })

    if ADMIN_ID:
        caption_lines = [
            "💰 <b>ОПЛАТА (Bot)!</b>",
            f"🆔 <code>{order_id}</code>",
            f"👤 @{user.username or '—'} (ID: <code>{user.id}</code>)",
            f"🎁 Настройка чувствительности — {price_label}",
        ]
        if pubg_id and pubg_id != "—" and payment_type == "UAH":
            caption_lines.append(f"🎮 PUBG ID: <code>{pubg_id}</code>")
        caption_lines.append(f"✈️ Тег: <code>{tg_tag}</code>")
        caption_lines.append(f"💵 Сумма: <b>{amount}</b>")

        caption = "\n".join(caption_lines)
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Готово", callback_data=f"adm:done:{user.id}:{order_id}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"adm:rej:{user.id}:{order_id}"),
        ]])

        try:
            if screenshot:
                await context.bot.send_photo(
                    chat_id=ADMIN_ID,
                    photo=screenshot,
                    caption=caption,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            else:
                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=caption,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление администратору: {e}")

    context.user_data.clear()


async def admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("⛔ Нет доступа", show_alert=True)
        return

    try:
        _, action, client_id, order_id = query.data.split(":")
    except ValueError:
        await query.answer("Ошибка данных")
        return

    done = action == "done"
    result = set_order_status(order_id, "done" if done else "cancelled")
    if result == "already":
        await query.answer("⚠️ Заказ уже обработан", show_alert=True)
        return
    if result == "missing":
        logger.warning(f"Заказ {order_id} не найден в orders.json")

    stamp = "\n\n✅ <b>ВЫПОЛНЕНО</b>" if done else "\n\n❌ <b>ОТКЛОНЕНО</b>"

    try:
        if query.message.photo:
            await query.edit_message_caption(
                caption=(query.message.caption_html or "") + stamp,
                parse_mode="HTML"
            )
        else:
            await query.edit_message_text(
                text=(query.message.text_html or "") + stamp,
                parse_mode="HTML"
            )
    except Exception as e:
        logger.error(f"Не удалось обновить сообщение заказа: {e}")

    client_text = (
        f"✅ Твой заказ <code>{order_id}</code> выполнен! Спасибо за покупку! 🎯"
        if done else
        f"❌ Твой заказ <code>{order_id}</code> отклонён. Если это ошибка — напиши @ARMYAN_help"
    )
    try:
        await context.bot.send_message(chat_id=int(client_id), text=client_text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Не удалось уведомить клиента {client_id}: {e}")

    await query.answer("Статус обновлён ✅")


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
        [InlineKeyboardButton("✉️ Написать @ARMYAN_help", url="https://t.me/ARMYAN_help")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")],
    ])
    await query.edit_message_text(
        "📩 <b>Связаться со мной</b>\n\n"
        "По всем вопросам пиши напрямую:\n"
        "Telegram: @ARMYAN_help",
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

    application.add_handler(CallbackQueryHandler(admin_decision, pattern="^adm:"), group=-1)
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
