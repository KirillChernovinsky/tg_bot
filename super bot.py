
import telebot
from telebot import types
import sqlite3 as sq
import time
bot = telebot.TeleBot("6383840892:AAHaMIJ846ceU9zZ-IHrntA5enYkT_SXPpY")
bot1 = telebot.TeleBot("6415225888:AAFnIQ9CXfujGmVeeiZ5_M9YYoHKipx3KWg")
with sq.connect("players.db", timeout=15000) as daswf:
        curs = daswf.cursor()
# создаем таблицу users с полями id name и (всего один раз впринципе)
        curs.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, numbers TEXT)')

#message.from_user.id #
name = None
winners = 0
number = None
adminid = [1206557152, 497819876]
time_start = 0




@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    with sq.connect("players.db", timeout=15000) as daswf:
        curs = daswf.cursor()
        curs.execute("SELECT name FROM users WHERE id=?", (user_id,))
        result = curs.fetchone()



    markup = types.ReplyKeyboardMarkup(row_width=1)
    item = types.KeyboardButton("ДА")
    item2 = types.KeyboardButton("НЕТ")
    markup.add(item, item2)
    bot.send_message(message.chat.id, f'Добрый день, {message.from_user.first_name}! \nХотите принять участие в розыгрыше?', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'ДА')
def ifyes(message):
    if message.text == 'ДА':
        bot.send_message(message.chat.id, "Отлично! Зарегистрируем вас.\n"
                                          " Введите свое имя и фамилию."
                                          "(позже изменить имя до конца следующего розыгрыша будет нельзя)")
        bot.register_next_step_handler(message, check_user_existence)

@bot.message_handler(func=lambda message: message.text == 'НЕТ')
def idno(message):
    if message.text == "НЕТ":
        bot.send_message(message.chat.id, "Эх, жаль. Ну если все таки захочешь поучавствовать, то жми ДА.")


def check_user_existence(message):
    user_id = message.chat.id
    with sq.connect("players.db", timeout=15000) as daswf:
        curs = daswf.cursor()
        # Проверяем наличие пользователя по id
        curs.execute("SELECT * FROM users WHERE id=?", (user_id,))
        result = curs.fetchone()

        if not result:
            global name
            name = message.text  # strip удаляет пробелы в сообщениях
            with sq.connect("players.db", timeout=15000) as daswf:
                curs = daswf.cursor()
                # Проверяем наличие пользователя по id
                curs.execute("INSERT OR REPLACE INTO users (id,name) VALUES (?, ?)", (user_id,name))

            bot.send_message(message.chat.id, "Также введите свой номер телефона.\n Учтите что поменять номер до начала следующего розыгрыша будет нельзя!")
            bot.register_next_step_handler(message, vsedann)
        else:
            bot.send_message(message.chat.id, ("Пользователь уже зарегистрирован."))
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton("ID", callback_data="result", color=(255, 0, 16)))

            bot.send_message(message.chat.id, "Ваш id по кнопочке.", reply_markup=markup)
def vsedann(message):
    number = message.text
    id_user = message.chat.id
    with sq.connect("players.db", timeout=15000) as daswf:
        curs = daswf.cursor()
        print(id_user)
        curs.execute("""UPDATE users SET numbers = (?) WHERE id = (?)""",(number, id_user))

    with sq.connect("players.db", timeout=15000) as daswf:
        curs = daswf.cursor()
        curs.execute("""SELECT id, name, numbers FROM users WHERE id = ?""", (message.from_user.id,))
        result = curs.fetchall()  # вернет все найденные записи fetchall-берет все
    if result:
        response = f"ID: {result[0]}\n"
        admin_chat_id = 1206557152
        bot1.send_message(admin_chat_id, response)
        chat_s_zakazhikom_id = 497819876
        bot1.send_message(chat_s_zakazhikom_id, response)
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("ID", callback_data="result"))

        bot.send_message(message.chat.id, "Ваш id по кнопочке.", reply_markup=markup)


# обработка кнопки список пользователей
@bot.callback_query_handler(func=lambda call: True)
def result(call):
    if call.message:
        if call.data == "result":
            with sq.connect("players.db", timeout=15000) as daswf:
                curs = daswf.cursor()
                curs.execute("""SELECT id, name FROM users WHERE id = ?""", (call.from_user.id,))
                result = curs.fetchall()  # вернет все найденные записи fetchall-берет все
            if result:
                response = f"ID: {result[0]}\n"
            else:
                response = "База данных пустая."

            bot.send_message(call.message.chat.id, response)


























#АДМИНСКОЕ МЕНЮ
@bot.message_handler(commands=['adminstart'])
def start_command(message):
    if message.chat.id == 1206557152 or 497819876:
        # Создание клавиатуры с кнопками
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("Начать розыгрыш")
        markup.row('Выбрать количество победителей')
        markup.row('Список зарегистрированных участников')
        markup.row('Подвести итоги')
        markup.row('Удалить базу данных')
        markup.row("Восстановить базу данных")
        markup.row('Удалить запасную базу')
        bot.send_message(message.chat.id, 'Добро пожаловать! Выберите действие:', reply_markup=markup)
    else:
        pass

# Обработчик нажатия на кнопку "Выбрать количество победителей"
@bot.message_handler(func=lambda message: message.text == 'Выбрать количество победителей')
def select_winners(message):
    if message.from_user.id == 1206557152 or 497819876:
        bot.send_message(message.chat.id, 'Введите количество победителей:')
        bot.register_next_step_handler(message, process_winners)
    else:
        pass

# Обработчик ввода количества победителей
def process_winners(message):
    if message.from_user.id == 1206557152 or 497819876:
        try:
            global winners
            winners = int(message.text)
            bot.send_message(message.chat.id, f'Количество победителей: {winners}')
            bot.send_message(message.chat.id,
                         'Чтобы посмотреть список участников, нажмите "Список зарегистрированных участников".')
            bot.send_message(message.chat.id, 'Чтобы Подвести итоги, нажмите "Подвести итоги".')
        except ValueError:
            bot.send_message(message.chat.id, 'Неверный формат. Введите число.')
            bot.register_next_step_handler(message, process_winners)
    else:
        bot.send_message(message.chat.id, "У вас нет прав.")

# Обработчик нажатия на кнопку "Список зарегистрированных участников"
@bot.message_handler(func=lambda message: message.text == 'Список зарегистрированных участников')
def show_players(message):
    if message.from_user.id == 1206557152 or 497819876:
        with sq.connect('players.db', timeout=15000) as conn:
            cursor = conn.cursor()
            # Выполнение SQL-запроса для получения списка участников
            cursor.execute("SELECT COUNT(id) FROM users")
            # Извлекаем результат запроса
            players = cursor.fetchone()[0]
            if players > 0:
                cursor.execute('SELECT * FROM users')
                players = cursor.fetchall()
                Spisok = ""

                # Отправка списка участников построчно
                for player in players:
                    Spisok += f'ID: {player[0]}, Имя: {player[1]}, Номер: {player[2]}\n'
                bot.send_message(message.chat.id, Spisok)
                print(Spisok)

                    # bot.send_message(message.chat.id, f'ID: {player[0]}, Имя: {player[1]}, Номер: {player[2]}')
            else:
                bot.send_message(message.chat.id, "Список пуст(нет участников)")

    else:
        pass



# Обработчик нажатия на кнопку "Подвести итоги"
@bot.message_handler(func=lambda message: message.text == 'Подвести итоги')
def start_raffle(message):
    if message.from_user.id == 1206557152 or 497819876:
        with sq.connect("players.db", timeout=15000) as conn:
            # Создаем курсор
            cursor = conn.cursor()

            # Выполняем запрос для получения количества id в таблице users
            cursor.execute("SELECT COUNT(id) FROM users")

            # Извлекаем результат запроса
            count = cursor.fetchone()[0]
            print(count)
            print(f"Количество id в таблице users: {count}")

            if count >= winners:
                with sq.connect("players.db", timeout=15000) as conn:
                    # Создаем курсор
                    cursor = conn.cursor()
                    # Получаем список всех записей в таблице
                    cursor.execute("SELECT id, name, numbers FROM users ORDER BY RANDOM() LIMIT ?", (winners,))
                    all_ids = cursor.fetchall()
                    print(all_ids)
                    Spisok_for_bazadannyx = ""

                    for player in all_ids:
                        print([player])
                        bot.send_message(message.chat.id, f'ID: {player[0]}, Имя: {player[1]}, Номер: {player[2]}')
                        yer = player[0]
                        # bot1 база данных отправляет список победителей, дату и кол-во участников
                        Spisok_for_bazadannyx += (f'ID: {player[0]}, Имя: {player[1]}, Номер: {player[2]}\n')
                    # Здесь бот отправляет сообщения победителям
                        try:
                            for winner in [yer]:
                                pass
                                # bot.send_message(winner, "Привет, вы победили!!! Для получения приза напишите по ссылке: https://t.me/neva5555")
                        except Exception as not_found_user:
                            bot.send_message(message.chat.id, "К пользователю 👆 нету доступа. (удаленный аккаунт)")
                    named_tuple = time.localtime()  # получить struct_time
                    time_string = time.strftime("%m/%d/%Y, %H:%M", named_tuple)

                    bot1.send_message(message.chat.id, f"Розыгрыш начат: {time_start}\nРозыгрыш окончен в {time_string}\n Победители:\n{Spisok_for_bazadannyx}")


                    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                    markup.row("Начать розыгрыш")
                    markup.row('Выбрать количество победителей')
                    markup.row('Список зарегистрированных участников')
                    markup.row('Подвести итоги')
                    markup.row('Удалить базу данных')
                    markup.row("Восстановить базу данных")
                    markup.row('Удалить запасную базу')
                    bot.send_message(message.chat.id, 'Хотите удалить текущий список участников (для начала другого нового розыгрыша)? \nЕсли хотите создать новый розыгрыш, то можете либо удалить этот список участников, либо провести розыгрыш с прошлыми участниками. \nЕсли хотите оставить список как есть, то можете ввести новое количество победителей, нажав кнопку "Выбрать количество победителей". \nТогда вы запустите новый розыгрыш со старым списком пользователей.', reply_markup=markup)
                    print("норм")
                    print(winners)

            else:
                bot.send_message(message.chat.id, "Участников меньше чем победителей.")

    else:
        pass

#ЭТО УДАЛЕНИЕ БАЗЫ ДАННЫХ ПОСЛЕ РОЗЫГРЫША
@bot.message_handler(func=lambda message: message.text == 'Удалить базу данных')
def tcno(message):
    if message.from_user.id == 1206557152 or 497819876:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row('Точно точно удалить?')
        bot.send_message(message.chat.id, 'Они исчезнут навсегда. Если не хотите, то введите /adminstart.', reply_markup=markup)
    else:
        pass
@bot.message_handler(func=lambda message: message.text == 'Точно точно удалить?')
def delbaza(message):
    if message.from_user.id == 1206557152 or 497819876:

        with sq.connect("players.db", timeout=15000) as dasww:
            curs = dasww.cursor()
            # создаем таблицу users с полями id name и (всего один раз впринципе)
            curs.execute('CREATE TABLE IF NOT EXISTS delete_users (id INTEGER PRIMARY KEY, name TEXT, numbers TEXT)')
            curs.execute('SELECT * FROM users')
            vse_dannj = curs.fetchall()
            curs.executemany("""INSERT OR IGNORE INTO delete_users (id, name, numbers) VALUES (?, ?, ?)""", vse_dannj)

        # Подключаемся к базе данных
        with sq.connect("players.db", timeout=15000) as daswf:
            curs = daswf.cursor()
            table_name = 'users'

            curs.execute(f'DROP TABLE IF EXISTS {table_name}')
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row("Начать розыгрыш")
            markup.row('Выбрать количество победителей')
            markup.row('Список зарегистрированных участников')
            markup.row('Подвести итоги')
            markup.row('Удалить базу данных')
            markup.row("Восстановить базу данных")
            markup.row('Удалить запасную базу')
            bot.send_message(message.chat.id, "Список участников теперь пуст.", reply_markup=markup)
            with sq.connect("players.db", timeout=15000) as daswf:
                curs = daswf.cursor()
                # создаем таблицу users с полями id name и (всего один раз впринципе)
                curs.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, numbers TEXT)')

    else:
        pass
@bot.message_handler(func=lambda message: message.text == 'Восстановить базу данных')
def helpbaza(message):
    if message.from_user.id == 1206557152 or 497819876:
        with sq.connect("players.db", timeout=15000) as dasww:
            curs = dasww.cursor()
            # создаем таблицу users с полями id name и (всего один раз впринципе)
            curs.execute('CREATE TABLE IF NOT EXISTS delete_users (id INTEGER PRIMARY KEY, name TEXT, numbers TEXT)')
            curs.execute('SELECT * FROM delete_users')
            vse_dannj = curs.fetchall()
            curs.executemany("""INSERT OR IGNORE INTO users (id, name, numbers) VALUES (?, ?, ?)""", vse_dannj)
            bot.send_message(message.chat.id, "База данных восстановлена.")
    else:
        pass
@bot.message_handler(func=lambda message: message.text == 'Удалить запасную базу')
def del_helpbaza(message):
    if message.from_user.id == 1206557152 or 497819876:
        with sq.connect("players.db", timeout=15000) as daswf:
            curs = daswf.cursor()
            table_name = 'delete_users'
            curs.execute(f'DROP TABLE IF EXISTS {table_name}')
            bot.send_message(message.chat.id, "Запасная база удалена.")
    else:
        pass

@bot.message_handler(func=lambda message: message.text == 'Начать розыгрыш')
def start_time(message):
    if message.from_user.id == 1206557152 or 497819876:
        named_tuple = time.localtime()  # получить struct_time
        global time_start
        time_start = time.strftime("%m/%d/%Y, %H:%M", named_tuple)
        bot.send_message(message.chat.id, "Вы начали розыгрыш! (эта информация нужна только базе данных).")
    else:
        pass

bot.infinity_polling()