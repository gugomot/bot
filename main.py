import telebot
from telebot import types

# Токен бота
bot = telebot.TeleBot('7598395534:AAEft4p_E78QFMd7VptKplSabG4VPlgES_g')

# ID чата для отзывов (замените на правильный ID вашей группы)
REVIEW_CHAT_ID = -4740348042  # Пример ID чата для отзывов

# Данные о дизайнерах
designers = {
    "Gugonot": {
        "chat_id": 1005232367,  # Ваш chat_id для дизайнера
        "portfolio_url": "https://imgur.com/a/O3boemf",
        "prices": {
            "Превью": 175,
            "Аватарка": 110,
            "Оформление": 250
        }
    }
}

user_state = {}

# Обработка команды /start
@bot.message_handler(commands=['start'])
def main(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🛒 Заказать дизайн", "⭐ Оставить отзыв", "👀 Посмотреть отзывы")
    bot.send_message(
        message.chat.id,
        '👋 Привет! Я — бот для заказа дизайна превью, аватарок и оформления для YouTube и не только!',
        reply_markup=markup
    )

# Обработка выбора типа дизайна
@bot.message_handler(func=lambda m: m.text == "🛒 Заказать дизайн")
def select_design_type(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🖼 Превью", "👤 Аватарка", "🎨 Оформление", "🔙 Назад")
    bot.send_message(message.chat.id, "🎯 Выберите тип дизайна:", reply_markup=markup)

# Обработка выбора дизайна
@bot.message_handler(func=lambda m: m.text in ["🖼 Превью", "👤 Аватарка", "🎨 Оформление"])
def choose_designer(message):
    design_type_map = {
        "🖼 Превью": "Превью",
        "👤 Аватарка": "Аватарка",
        "🎨 Оформление": "Оформление"
    }
    user_state[message.chat.id] = {"design_type": design_type_map[message.text]}  # Добавлено создание записи для пользователя
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in designers.keys():
        markup.add(name)
    markup.add("🔙 Назад")
    bot.send_message(message.chat.id, "👤 Выберите дизайнера:", reply_markup=markup)

# Обработка выбора дизайнера
@bot.message_handler(func=lambda m: m.text in designers.keys())
def show_designer_options(message):
    chat_id = message.chat.id

    # Убедимся, что у пользователя есть запись в user_state
    if chat_id not in user_state:
        bot.send_message(chat_id, "⚠️ Пожалуйста, начните с выбора типа дизайна.")
        return

    designer_name = message.text
    user_state[chat_id]["designer"] = designer_name
    design_type = user_state[chat_id]["design_type"]
    designer = designers[designer_name]
    price = designer['prices'][design_type]

    inline = types.InlineKeyboardMarkup()
    inline.add(
        types.InlineKeyboardButton(text="📁 Портфолио", callback_data=f"portfolio_{designer_name}"),
        types.InlineKeyboardButton(text=f"✅ Заказать: {design_type} ({price} грн)", callback_data=f"order_{designer_name}")
    )
    bot.send_message(chat_id, f"🎨 Дизайнер: {designer_name}", reply_markup=inline)

# Обработка кнопки Портфолио
@bot.callback_query_handler(func=lambda call: call.data.startswith("portfolio_"))
def send_portfolio(call):
    designer_name = call.data.split("_")[1]
    designer = designers[designer_name]
    bot.send_photo(call.message.chat.id, designer['portfolio_url'], caption=f"🖼 Портфолио дизайнера {designer_name}")

# Обработка кнопки Заказать
@bot.callback_query_handler(func=lambda call: call.data.startswith("order_"))
def handle_order(call):
    chat_id = call.message.chat.id
    designer_name = call.data.split("_")[1]
    design_type = user_state.get(chat_id, {}).get("design_type", "Неизвестно")
    username = call.from_user.username or "Без username"
    tg_link = f"https://t.me/{username}" if username != "Без username" else "(не указано)"

    designer = designers[designer_name]
    price = designer['prices'][design_type]

    bot.send_message(
        designer["chat_id"],
        f"🔔 Новый заказ!\nТип: {design_type}\nЦена: {price} грн\nПользователь: @{username}\nПрофиль: {tg_link}"
    )

    bot.send_message(chat_id, "🎉 Ваш заказ отправлен дизайнеру! Он свяжется с вами в ближайшее время.")

# Обработка кнопки для оставления отзыва
@bot.message_handler(func=lambda m: m.text == "⭐ Оставить отзыв")
def ask_for_review(message):
    msg = bot.send_message(message.chat.id, "📝 Напишите свой отзыв и мы его обязательно передадим!")
    bot.register_next_step_handler(msg, handle_review)

# Обработка отзыва
def handle_review(message):
    username = message.from_user.username or "Без username"
    review_text = message.text

    # Отправка отзыва в группу с отзывами с использованием REVIEW_CHAT_ID
    bot.send_message(REVIEW_CHAT_ID, f"📢 Новый отзыв от @{username}:\n\n{review_text}")
    bot.send_message(message.chat.id, "🙏 Спасибо за ваш отзыв!")

# Обработка кнопки для просмотра отзывов
@bot.message_handler(func=lambda m: m.text == "👀 Посмотреть отзывы")
def view_reviews(message):
    # Отправляем пользователя в группу с отзывами
    bot.send_message(
        message.chat.id,
        "👀 Перейдите в группу для просмотра всех отзывов: [Ссылка на группу с отзывами](https://t.me/+WDuu68VfwBg2NmMy)",
        parse_mode="Markdown"
    )

# Обработка кнопки Назад
@bot.message_handler(func=lambda m: m.text == "🔙 Назад")
def go_back(message):
    main(message)

# Запуск бота
bot.polling(none_stop=True)