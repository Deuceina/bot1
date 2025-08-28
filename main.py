import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Загружаем переменные окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Тексты для разделов — ЗАПОЛНИТЕ САМИ
TEXT_MIXING = "📌 Здесь будет информация о сведении.\n\nНапример:\n- Что входит в сведение\n- Сроки\n- Примеры работ\n- Цена\n\nДобавьте сюда свой текст."

TEXT_MASTERING = "📌 Здесь будет информация о мастеринге.\n\nНапример:\n- Что такое мастеринг\n- Форматы\n- Как подготовить трек\n- Сроки и стоимость\n\nДобавьте сюда свой текст."

TEXT_BOTH = "📌 Полный аудио-пакет: сведение + мастеринг.\n\n- Комплексная обработка\n- Скидка при заказе пакета\n- Приоритетная очередь\n\nДобавьте сюда свой текст."

TEXT_INFO = "📌 Обо мне:\n\nЯ — аудиоинженер с 5+ лет опыта.\nРаботаю в Pro Tools, Logic, Ableton.\nСпециализируюсь на электронике, хип-хопе, поп.\n\n📩 Свяжитесь со мной для вопросов.\n\n⭐ Отзывы: @reviews_channel"

# Клавиатура "Назад"
def get_back_button():
    return [[InlineKeyboardButton("◀️ Назад", callback_data="back")]]

# Обработчик /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("1. Сведение", callback_data="mixing")],
        [InlineKeyboardButton("2. Мастеринг", callback_data="mastering")],
        [InlineKeyboardButton("3. Сведение и мастеринг", callback_data="both")],
        [InlineKeyboardButton("4. Информация", callback_data="info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет Выбери, что тебя интересует:", reply_markup=reply_markup)

# Обработчик кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "back":
        # Возврат в главное меню
        keyboard = [
            [InlineKeyboardButton("1. Сведение", callback_data="mixing")],
            [InlineKeyboardButton("2. Мастеринг", callback_data="mastering")],
            [InlineKeyboardButton("3. Сведение и мастеринг", callback_data="both")],
            [InlineKeyboardButton("4. Информация", callback_data="info")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Выбери раздел:", reply_markup=reply_markup)
        return

    # Кнопки с "Назад" и "Оставить заявку"
    action_keyboard = [
        [InlineKeyboardButton("📩 Оставить заявку", callback_data=f"apply_{data}")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(action_keyboard)

    # Отправка текста в зависимости от выбора
    if data == "mixing":
        await query.edit_message_text(text=TEXT_MIXING, reply_markup=reply_markup, parse_mode='HTML')
    elif data == "mastering":
        await query.edit_message_text(text=TEXT_MASTERING, reply_markup=reply_markup, parse_mode='HTML')
    elif data == "both":
        await query.edit_message_text(text=TEXT_BOTH, reply_markup=reply_markup, parse_mode='HTML')
    elif data == "info":
        await query.edit_message_text(text=TEXT_INFO, reply_markup=reply_markup, parse_mode='HTML')

# Обработчик заявки
async def apply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data.replace("apply_", "")  # например, "mixing"
    user = query.from_user
    username = f"@{user.username}" if user.username else f"ID: {user.id}"

    # Определяем название услуги
    service_names = {
        "mixing": "сведение",
        "mastering": "мастеринг",
        "both": "сведение и мастеринг",
        "info": "информацию"
    }
    service = service_names.get(data, "неизвестную услугу")

    # Отправляем заявку администратору
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📩 Вам пришла новая заявка на <b>{service}</b> от {username}",
            parse_mode='HTML'
        )
        await query.edit_message_text(
            text="✅ Заявка отправлена Я свяжусь с вами в ближайшее время.",
            reply_markup=InlineKeyboardMarkup(get_back_button())
        )
    except Exception as e:
        await query.edit_message_text(
            text="❌ Не удалось отправить заявку. Попробуйте позже или свяжитесь напрямую.",
            reply_markup=InlineKeyboardMarkup(get_back_button())
        )
        print(f"Ошибка отправки заявки: {e}")

# Основная функция
def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(apply_handler, pattern=r"^apply_"))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Бот запущен. Ожидание команд...")
    application.run_polling()

if __name__ == "__main__":
    main()
