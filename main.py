import sqlite3 as sq
from config import token
from config import adminschat
import telebot 
from telebot import types
import datetime
bot = telebot.TeleBot(token)
#######################################################################################################################################################################################
###SQLite###
#1)function to create a table
def createtable():
    with sq.connect("tickets.db") as con:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS tickets(
        ticketnumber INTEGER,
        tgid INTEGER,
        nik TEXT,
        ticket TEXT,
        ticketdate TEXT,
        response TEXT,
        responsedate TEXT,
        adminid INTEGER
        )
""")
#2)функция внесения тикета инфы в БД #function to enter ticket info into the database
def add_ticket_to_table(ticketnumber, tgid, nik, ticket, ticketdate):
    with sq.connect("tickets.db") as con:
        cur = con.cursor()
        cur.execute(f"INSERT INTO tickets VALUES ({ticketnumber}, {tgid}, '{nik}', '{ticket}', '{ticketdate}', '', '', 0)")
#3)функция добавления респонса в бд #function to add a response to the database
def add_response_to_table(ticketnumber, response, responsdate, adminid):
    with sq.connect("tickets.db") as con:
        cur = con.cursor() #int = 0 text = ''
        cur.execute(f"UPDATE tickets SET response = ?, responsedate = ?, adminid = ? WHERE ticketnumber = ?", (response, responsdate, adminid, ticketnumber))
        con.commit() 
#4)функция поиска респонса в бд #function to search for a response in the database
def searchresponse(nmb):
    with sq.connect("tickets.db") as con:
        cur = con.cursor()
        cur.execute("SELECT response FROM tickets WHERE ticketnumber=?", (nmb,))
        rsp = cur.fetchone()
        if rsp == ('',):
            text = "Ответ на заявку еще не готов.\nОжидайте ответа в ближайшее время\nВыберите действие:"
            return text
        else:
            text = f"Ответ на заявку готов:\n{str(rsp)[2:-3]}\nВыберите действие:"
            return text
#5)Сравнение тгайди юзера с автором заявки в бд #Comparison of the user's telegram ID with the author of the ticket in the database
def check_user_authorization(ticket_number, user_id):
    with sq.connect("tickets.db") as con:
        cur = con.cursor()
        cur.execute("SELECT tgid FROM tickets WHERE ticketnumber=?", (ticket_number,))
        result = cur.fetchone()
        if result is not None and result[0] == user_id:
            return True
        else:
            return False       
#6)функция вызова номера заявки #function to call up the ticket number 
def get_next_ticket_number():
    with sq.connect("tickets.db") as con:
        cur = con.cursor()
        cur.execute("SELECT MAX(ticketnumber) FROM tickets")
        max_number = cur.fetchone()[0]
        if max_number is None:
            # Если в таблице нет записей, начинаем с номера 1
            return 1
        else:
            return max_number + 1
#######################################################################################################################################################################################
#######TELEBOT#######
#основная клавиатура #main keyboard
def main_keyboard():
    mainkeyboar = types.InlineKeyboardMarkup(row_width=1)
    createticket = types.InlineKeyboardButton(text="Создать заявку.", callback_data="create_ticket")
    aboutticket = types.InlineKeyboardButton(text="Проверить состояние заяки.", callback_data="about_ticket")
    about = types.InlineKeyboardButton(text="about", callback_data="about")
    mainkeyboar.add(createticket, aboutticket, about)
    return mainkeyboar
#команда /start # /start command
@bot.message_handler(commands=['start'])
def start(message):
    keyboard = main_keyboard()
    bot.send_message(message.chat.id, 'Привет!', reply_markup=keyboard)
    bot_info = bot.get_me()    
#Обработчик ответов на сообщения бота и внесение их в дб с помощью функции add_response_to_table #Handler for responses to bot messages and adding them to the database using the add_response_to_table function
@bot.message_handler(func=lambda message: message.chat.id == int(adminschat) and message.reply_to_message is not None and message.reply_to_message.from_user.id == 7197457890)
def handle_response_to_bot_message(message):
    keyboard = main_keyboard()
    current_datetime = datetime.datetime.now()
    responsdate = current_datetime.strftime("%d-%m-%Y %H:%M:%S")
    adminid = message.from_user.id
    response = message.text
    origmsg = message.reply_to_message.text
    origmsglistm = origmsg.split('\n')
    ticketnumber = origmsglistm[0]
    responseid = origmsglistm[1]
    add_response_to_table(ticketnumber, response, responsdate, adminid)
    bot.send_message(responseid, f"Получен ответ на заявку #{ticketnumber}:")
    bot.send_message(responseid, response)
    bot.send_message(responseid, f"Выберите действие:", reply_markup=keyboard)
#Функция создания заяки create_ticket #create_ticket function for creating a request
@bot.callback_query_handler(func=lambda callback: callback.data == "create_ticket")
def new_ticket(callback):
    msg = bot.send_message(callback.message.chat.id, 'Сообщи о своей проблеме максимально подробно. Не забудь представиться и указать номер кабинета.')
    bot.register_next_step_handler(msg, register_ticket) 
def register_ticket(message):
    keyboard = main_keyboard()
    ticketnumber = get_next_ticket_number()
    tgid = message.from_user.id 
    nik = message.from_user.username
    ticket = message.text
    current_datetime = datetime.datetime.now()
    ticketdate = current_datetime.strftime("%d-%m-%Y %H:%M:%S")
    tckt = f"Поступила новая заявка\n{ticketnumber}, {tgid}, {nik}, {ticket}, {ticketdate}"
    print(tckt)
    add_ticket_to_table(ticketnumber, tgid, nik, ticket, ticketdate)
    bot.send_message(adminschat, f"{ticketnumber}\n{tgid}\n{ticket}\n{nik}, {ticketdate}")
    bot.send_message(message.chat.id, f"Ваша заявка успешно создана под номером {ticketnumber}.\nВыберите действие:", reply_markup=keyboard)
#функция поиска заявки по номеру about_ticket #ticket search function by number about_ticket
@bot.callback_query_handler(func=lambda callback: callback.data == "about_ticket")
def aboutticket(callback):
    msg = bot.send_message(callback.message.chat.id, 'Напиши номер заявки в чат.\nПомни, что номер заявки может состоять только из цифр.')
    bot.register_next_step_handler(msg, searchticket)
def searchticket(message):
    keyboard = main_keyboard()
    ticket_number = message.text
    user_id = message.from_user.id
    if ticket_number.isdigit():
        auth_check = check_user_authorization(ticket_number, user_id)
        if auth_check:
            bot.send_message(message.chat.id, f"{searchresponse(ticket_number)}", reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, "Авторство не подтверждено. Доступ запрещен.\nВыберите действие:", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "Номер заявки может состоять только из чисел.\nВыберите действие:", reply_markup=keyboard)
################################about
#доп клавиатура #additional keyboard
def aboutkeyboard():
    mainkeyboar = types.InlineKeyboardMarkup(row_width=1)
    zkz = types.InlineKeyboardButton(text="Заказать разработку бота.", url="https://t.me/Kierkegaart")
    gth = types.InlineKeyboardButton(text="Github.", url="https://github.com/K33333NSH1")
    vzv = types.InlineKeyboardButton(text="Возврат в основное меню", callback_data="vozvrat")
    mainkeyboar.add(zkz, gth, vzv)
    return mainkeyboar
#Функция инф. об авторе about
@bot.callback_query_handler(func=lambda callback: callback.data == "about")
def aboutauth(callback):
    keyboard = aboutkeyboard()
    bot.send_message(callback.message.chat.id, """Prod. by:
@Kierkegaart
https://github.com/K33333NSH1
""", reply_markup=keyboard)
#функция возврата к начальному меню #function to return to the main menu
@bot.callback_query_handler(func=lambda callback: callback.data == "vozvrat")
def backtomainmenu(callback):
    keyboard = main_keyboard()
    bot.send_message(callback.message.chat.id, "Выберите действие:", reply_markup=keyboard)
#######################################################################################################################################################################################
def main():
    createtable()
    print("Table was created")
    bot.polling() #функция запуска бота #bot launch function
if __name__ == '__main__':
    main() #точка входа #entry point
