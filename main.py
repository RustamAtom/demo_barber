import telebot
from telebot import types
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import database

TOKEN = "8311036046:AAGEYHD9JGp-3VVH7p9ZZ1hW6IJ-PQ33rBo"
ADMIN_ID = 5068250115  # поставь свой id

bot = telebot.TeleBot(TOKEN)
user_data = {}
slots = {}


# ---------------- START ----------------
@bot.message_handler(commands=["start"])
def start(message):
    if message.chat.id == ADMIN_ID:
        admin_menu()
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🖊 Записаться", callback_data="start_z"))
        bot.send_message(
            message.chat.id,
            "👋 Нажмите кнопку для записи\n[<i>Тут будет ваш индивидуальный приветственный текст с прикреплённым фото, где будет логотип вашего барбершопа</i>]",
            parse_mode="HTML",
            reply_markup=markup,
        )


# ---------------- АДМИН ----------------
def admin_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📅 Добавить слот", callback_data="add_slot"),
        types.InlineKeyboardButton("📝 Заявки", callback_data="list"),
    )
    bot.send_message(ADMIN_ID, "⚙️ Админ-панель", reply_markup=markup)


# ---------------- CALLBACK ----------------
@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    # старт записи
    if call.data == "start_z":
        msg = bot.send_message(
            call.message.chat.id,
            "👤Введите ваше имя\nНапример: <i>Олег</i>",
            parse_mode="HTML",
        )
        bot.register_next_step_handler(msg, get_name)

    # список заявок
    elif call.data == "list":
        clients = database.get_all_zayvki()
        if not clients:
            bot.send_message(ADMIN_ID, "😔Заявок нет")
            return

        for c in clients:
            user_id, name, phone, usluga, day, time, status = c
            text = f"👤Имя: {name}\n📞Номер телефона: {phone}\n🎫Услуга: {usluga}\n📅День: {day}\n🕐Время:{time}\nℹ️Статус: {status}"

            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton(
                    "❌Отменить", callback_data=f"cancel_{user_id}"
                )
            )

            bot.send_message(ADMIN_ID, text, reply_markup=markup)

    # отмена
    elif call.data.startswith("cancel_"):
        user_id = int(call.data.split("_")[1])
        z = database.get_zayvka(user_id)
        if z:
            name, phone, usluga, day, time, status = z
            database.cancel_zayvka(user_id)
            database.free_slot(day, time)

            bot.send_message(ADMIN_ID, f"❌Отменено: {name} {day} {time}")
            try:
                bot.send_message(user_id, "❌Ваша запись отменена")
            except:
                pass

    # добавить слот
    elif call.data == "add_slot":
        msg = bot.send_message(
            ADMIN_ID,
            "📅Введите дату\nНапример: <i>25.04</i>\nФормат: <i>ДЕНЬ.МЕСЯЦ</i>",
            parse_mode="HTML",
        )
        bot.register_next_step_handler(msg, add_slot_bulk1)


# ---------------- ЗАЯВКА ----------------
def get_name(message):
    user_data[message.chat.id] = {"name": message.text}
    msg = bot.send_message(
        message.chat.id,
        "📞Введите номер телефона\nНапример: <i>+79998887766</i>",
        parse_mode="HTML",
    )
    bot.register_next_step_handler(msg, get_phone)


def get_phone(message):
    user_data[message.chat.id]["phone"] = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Стрижка", "Борода")

    msg = bot.send_message(message.chat.id, "🎫Выберите услугу:", reply_markup=markup)
    bot.register_next_step_handler(msg, get_service)


def get_service(message):
    user_data[message.chat.id]["usluga"] = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(7):
        day = (datetime.now() + timedelta(days=i)).strftime("%d.%m")
        markup.add(day)

    msg = bot.send_message(message.chat.id, "📅Выберите день:", reply_markup=markup)
    bot.register_next_step_handler(msg, get_day)


def get_day(message):
    user_data[message.chat.id]["day"] = message.text

    times = database.get_free_slot(message.text)
    if not times:
        bot.send_message(message.chat.id, "❌Нет свободных окон")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for t in times:
        markup.add(t)

    msg = bot.send_message(message.chat.id, "🕐Выберите время:", reply_markup=markup)
    bot.register_next_step_handler(msg, finish)


def finish(message):
    data = user_data[message.chat.id]
    data["time"] = message.text

    database.save_zayvka(
        message.chat.id,
        data["name"],
        data["phone"],
        data["usluga"],
        data["day"],
        data["time"],
    )

    database.book_slot(data["day"], data["time"])

    bot.send_message(message.chat.id, "✅ Вы записаны!")

    bot.send_message(
        ADMIN_ID,
        f"🔔Новая запись:\n👤Имя: {data['name']}\n📅День: {data['day']}\n🕐Время: {data['time']}",
    )


# ---------------- ДОБАВЛЕНИЕ СЛОТОВ ----------------
def add_slot_bulk1(message):
    chat_id = message.chat.id

    if chat_id not in slots:
        slots[chat_id] = {}

    slots[chat_id]["day"] = message.text.strip()

    msg = bot.send_message(
        message.chat.id,
        "🕰️Теперь введите свободные окошки через запятую\nНапример: <i>12:00, 13:15, 20:59</i>\nФормат: <i>ЧАСЫ:МИНУТЫ</i>",
        parse_mode="HTML",
    )
    bot.register_next_step_handler(msg, add_slot_bulk2)


def add_slot_bulk2(message):
    text = message.text.strip()
    day = slots[message.chat.id]["day"]

    try:
        times_list = text.split(",")

        added = 0

        for t in times_list:
            if len(t) == 5 and ":" in t:
                database.add_slot(day, t)
                added += 1

        bot.send_message(ADMIN_ID, f"✅ Добавлено {times_list} окошек на {day}")

    except Exception as e:
        bot.send_message(
            ADMIN_ID,
            "❌ Ошибка формата\nПример:\n<i>25.04 | 14:00, 16:00, 18:00</i>",
            parse_mode="HTML",
        )


# ---------------- НАПОМИНАНИЯ ----------------
def reminders():
    clients = database.get_clients_for_reminder(datetime.now())
    for user_id, name, time in clients:
        try:
            bot.send_message(user_id, f"⏰ Напоминание! Вы записаны на {time}")
        except:
            pass


# ---------------- ОЧИСТКА ----------------
def clear_old():
    database.clear_old_records()


# ---------------- SCHEDULER ----------------
scheduler = BackgroundScheduler()
scheduler.add_job(reminders, "interval", minutes=1)
scheduler.add_job(clear_old, "interval", minutes=10)
scheduler.start()

# ---------------- ЗАПУСК ----------------
if __name__ == "__main__":
    print("Бот запущен")
    bot.polling(non_stop=True)
