import telebot
from telebot import types

TOKEN = "8311036046:AAGEYHD9JGp-3VVH7p9ZZ1hW6IJ-PQ33rBo"
ADMIN_ID = 5068250115  # сюда свой Telegram ID

bot = telebot.TeleBot(TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("Оставить заявку")
    markup.add(btn)
    bot.send_message(message.chat.id, "Нажмите кнопку ниже, чтобы оставить заявку", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Оставить заявку")
def ask_name(message):
    bot.send_message(message.chat.id, "Введите ваше имя:")
    bot.register_next_step_handler(message, ask_phone)

def ask_phone(message):
    user_data[message.chat.id] = {"name": message.text}
    bot.send_message(message.chat.id, "Введите номер телефона:")
    bot.register_next_step_handler(message, finish)

def finish(message):
    user_data[message.chat.id]["phone"] = message.text

    name = user_data[message.chat.id]["name"]
    phone = user_data[message.chat.id]["phone"]

    bot.send_message(message.chat.id, "Спасибо! Ваша заявка отправлена ✅")

    bot.send_message(ADMIN_ID, f"Новая заявка:\nИмя: {name}\nТелефон: {phone}")

bot.polling()