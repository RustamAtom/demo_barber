import telebot
from telebot import types
import database
from datetime import datetime, timedelta
import re
from apscheduler.schedulers.background import BackgroundScheduler
import time

TOKEN = "8311036046:AAGEYHD9JGp-3VVH7p9ZZ1hW6IJ-PQ33rBo"
ADMIN_ID = 5068250115

bot = telebot.TeleBot(TOKEN)

user_data = {}
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id != ADMIN_ID:
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton('🖊️Оставить заявку', callback_data='start_zayvka')
        markup.add(btn)
        bot.send_message(message.chat.id, '👋Вас приветствует демо-версия бота для приёма заявок\n👇Нажми на кнопку ниже, чтобы оставить заявку', reply_markup=markup)
    else:
        start_admin(message)
def start_admin(message):
    if message.chat.id == ADMIN_ID:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('📝Список клиентов', callback_data='spisok')
        btn2 = types.InlineKeyboardButton('📅Добавить свободные окошки', callback_data='add_okoshki')
        btn3 = types.InlineKeyboardButton('📢Сделать рассылку', callback_data='rassylka')
        markup.add(btn1, btn2)
        bot.send_message(ADMIN_ID, '🏠Главное меню АДМИНА', reply_markup=markup)
    else:
        start(message)
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    def ask_phone(message):
                user_data[message.chat.id] = {"name": message.text}
                bot.send_message(message.chat.id, "📞Введите номер телефона\nНапример: <b>+79998887766</b>", parse_mode='HTML')
                bot.register_next_step_handler(message, ask_usluga)
    def ask_usluga(message):
                user_data[message.chat.id]["phone"] = message.text
                
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
                btn1 = types.KeyboardButton('🎫Услуга|💵Цена: 100')
                btn2 = types.KeyboardButton('🎫Услуга|💵Цена: 100')
                btn3 = types.KeyboardButton('🎫Услуга|💵Цена: 100')
                btn4 = types.KeyboardButton('🎫Услуга|💵Цена: 100')
                markup.add(btn1, btn2, btn3, btn4)
                msg = bot.send_message(message.chat.id, '🎫Выбери услугу\n💵Цены предоставлены в рублях', reply_markup=markup)
                bot.register_next_step_handler(msg, ask_day)
    def ask_day(message):
        user_data[message.chat.id]['usluga'] = message.text
        today = datetime.now()
        
        str_today = today.strftime('%d.%m')
        str_tomorrow = (today + timedelta(days=1)).strftime('%d.%m')
        str_after_tomorrow = (today + timedelta(days=2)).strftime('%d.%m')

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton(f'Сегодня({str_today})')
        btn2 = types.KeyboardButton(f'Завтра({str_tomorrow})')
        btn3 = types.KeyboardButton(f'Послезавтра({str_after_tomorrow})')
        markup.add(btn1, btn2, btn3)
        msg = bot.send_message(message.chat.id, '📅Выбери день', reply_markup=markup)
        bot.register_next_step_handler(msg, ask_time)
    def ask_time(message):
        user_data[message.chat.id]['day'] = message.text
        
        date_match = re.search(r'\d{2}\.\d{2}', message.text)
        if date_match:
            clean_day = date_match.group()
            free_times = database.get_free_slot(clean_day)
            if free_times:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                for t in free_times:
                    markup.add(types.KeyboardButton(t))
                msg = bot.send_message(message.chat.id, '🕰️Выбери доступное время', reply_markup=markup)
                bot.register_next_step_handler(msg, finish)
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton('🔁Попробовать снова', callback_data='start_zayvka'))
                bot.send_message(message.chat.id, '😔К сожалению на этот день свободных окон нет\nНажмите кнопку ниже и начните отправку заявки заново👇', reply_markup=markup)
    def finish(message):
        user_id = message.chat.id
        user_data[message.chat.id]['time'] = message.text
        
        name = user_data[message.chat.id]['name']
        phone = user_data[message.chat.id]['phone']
        usluga = user_data[message.chat.id]['usluga']
        day = user_data[message.chat.id]['day']
        time = user_data[message.chat.id]['time']
        
        database.save_zayvka(user_id=user_id, name=name, phone=phone, usluga=usluga, day=day, time=time)
        database.book_slot(day=day, time=time)
        
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton('❌Отменить заявку', callback_data='otmena')
        markup.add(btn)
        bot.send_message(message.chat.id, "Спасибо! Ваша заявка отправлена ✅", reply_markup=markup)
        bot.send_message(ADMIN_ID, f'🔔У вас новая заявка\n👤Имя: <b>{name}</b>\n📞Номер телефона: <b>{phone}</b>\n🎫Услуга: <b>{usluga}</b>\n📅День: <b>{day}</b>\n🕰️Время: <b>{time}</b>\n🟢Статус: <i>✅Активна</i>', parse_mode='HTML')
    def send_broadcast_messages(message):
        users = database.get_all_clients()
        count = 0
        soo = message.text
        
        for user_id in users:
            try:
                bot.send_message(user_id, soo)
                count += 1
            except Exception as e:
                print(f"Не удалось оттправить сообщение {user_id}: {e}")
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🏠Главное меню', callback_data='home'))
        bot.send_message(ADMIN_ID, f'✅Рассылка завершена!\nПолучили <b>{count}</b> человек', parse_mode='HTML', reply_markup=markup)
    if call.data == 'start_zayvka':
        msg = bot.send_message(call.message.chat.id, "👤Введите ваше имя\nНапример: <b>Олег</b>", parse_mode='HTML')
        bot.register_next_step_handler(msg, ask_phone)
    elif call.data == 'spisok':
        bot.send_message(call.message.chat.id, 'Список')
    elif call.data == 'otmena':
        client = database.get_zayvka(call.message.chat.id)
        if client:
            name, phone, usluga, day, time = client
            bot.send_message(ADMIN_ID, f'<b>❌ЗАЯВКА ОТМЕНЕНА</b>\n👤Имя: <b>{name}</b>\n📞Номер телефона: <b>{phone}</b>\n🎫Услуга: <b>{usluga}</b>\n📅День: <b>{day}</b>\n🕰️Время: <b>{time}</b>\n🟢Статус: <i>❌Не активна</i>', parse_mode='HTML')
            bot.send_message(call.message.chat.id, "❌Ваша заявка была отменена")
            database.delete_zayvka(call.message.chat.id)
    elif call.data == 'add_okoshki':
        markup = types.InlineKeyboardMarkup()
        today = datetime.now()
        d1 = today.strftime('%d.%m')
        d2 = (today + timedelta(days=1)).strftime('%d.%m')
        d3 = (today + timedelta(days=2)).strftime('%d.%m')
        
        btn1 = types.InlineKeyboardButton(f'На сегодня ({d1})', callback_data=f'setday_{d1}')
        btn2 = types.InlineKeyboardButton(f'На завтра ({d2})', callback_data=f'setday_{d2}')
        btn3 = types.InlineKeyboardButton(f'На послезавтра ({d3})', callback_data=f'setday_{d3}')

        markup.add(btn1, btn2, btn3)
        bot.send_message(ADMIN_ID, '❓На какой день добавить окошко?')
    elif call.data == 'rassylka':
        if call.message.chat.id == ADMIN_ID:
            msg = bot.send_message(call.message.chat.id, '👇Введите текст рассылки одним сообщением: ')
            bot.register_next_step_handler(msg, send_broadcast_messages)
    elif call.data == 'home':
        start(call.message)
@bot.callback_query_handler(func=lambda call: call.data.startswith('setday_'))
def admin_setday(call):
    day = call.data.split('_')[1]
    user_data[call.message.chat.id] = {'admin_day': day}
    
    msg = bot.send_message(ADMIN_ID, f'🕰️Введите свободные окошки для {day}\nНапример: <b>14:00</b>', parse_mode='HTML')
    bot.register_next_step_handler(msg, admin_save_time)
    
    def admin_save_time(message):
        day = user_data[message.chat.id]['admin_day']
        time = message.text
        database.add_slot(day=day, time=time)
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('➕Добавить ещё окошко', callback_data='add_okoshki'))
        
        bot.send_message(ADMIN_ID, f'✅Окошко {day} в {time} добавлено', reply_markup=markup)

def check_reminders():
    reminder_time = (datetime.now() + timedelta(hours=2)).strftime('%H%M')
    today_date = datetime.now().strftime('%d%m')
    
    clients_to_remind = database.get_clients_for_reminder(today_date, reminder_time)
    
    for client in clients_to_remind:
        user_id, name, time_slot = client
        try:
            bot.send_message(user_id, f'🔔{name} напоминаем! Вы записаны на сегодня в {time_slot}. Ждём Вас!')
            print(f'Отправлено напоминание для {name}')
        except Exception as e:
            print(f'Error: {e}')
scheduler = BackgroundScheduler()
scheduler.add_job(check_reminders, 'interval', minutes=1)
scheduler.start()

bot.polling()