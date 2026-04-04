import telebot
from telebot import types

TOKEN = "8311036046:AAGEYHD9JGp-3VVH7p9ZZ1hW6IJ-PQ33rBo"
ADMIN_ID = 5068250115

bot = telebot.TeleBot(TOKEN)

user_data = {}
@bot.message_handler(commands=['start'])
def start(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        btn = types.KeyboardButton('🖊️Оставить заявку')
        markup.add(btn)
        bot.send_message(message.chat.id, '👇Нажми на кнопку ниже, чтобы оставить заявку', reply_markup=markup)
def start_admin(message):
    if message.chat.id == ADMIN_ID:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('📝Список клиентов', callback_data='spisok')
        markup.add(btn1)
        bot.send_message(message.chat.id, '🏠Главное меню АДМИНА', reply_markup=markup)
    else:
        start(message)
@bot.message_handler(func=lambda message: message.text == '🖊️Оставить заявку')
def ask_name(message):
            bot.send_message(message.chat.id, "👤Введите ваше имя\nНапример: <b>Олег</b>", parse_mode='HTML')
            bot.register_next_step_handler(message, ask_phone)
def ask_phone(message):
            user_data[message.chat.id] = {"name": message.text}
            bot.send_message(message.chat.id, "📞Введите номер телефона\nНапример: <b>+79998887766</b>", parse_mode='HTML')
            bot.register_next_step_handler(message, ask_usluga)
def ask_usluga(message):
            user_data[message.chat.id]["phone"] = message.text
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton('🎫Услуга')
            btn2 = types.KeyboardButton('🎫Услуга')
            btn3 = types.KeyboardButton('🎫Услуга')
            btn4 = types.KeyboardButton('🎫Услуга')
            markup.add(btn1, btn2, btn3, btn4)
            msg = bot.send_message(message.chat.id, '🎫Выбери услугу', reply_markup=markup)
            bot.register_next_step_handler(msg, finish)
def finish(message):
            user_data[message.chat.id]['usluga'] = message.text

            name = user_data[message.chat.id]["name"]
            phone = user_data[message.chat.id]["phone"]
            usluga = user_data[message.chat.id]['usluga']

            markup = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton('❌Отменить заявку', callback_data='otmena')
            markup.add(btn)
            bot.send_message(message.chat.id, "Спасибо! Ваша заявка отправлена ✅", reply_markup=markup)
            bot.send_message(ADMIN_ID, f'🔔У вас новая заявка\nИмя: {name}\nНомер телефона: {phone}\nУслуга: {usluga}\nСтатус: ✅Активна')
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == 'spisok':
        bot.send_message(call.message.chat.id, 'Список')

bot.polling()