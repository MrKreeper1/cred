#import telebot
#from telebot import types
from aiogram import *
import asyncio
from db_ops import *
import config_parse as conf
import json
import logging
import atexit
from sql_con import *
import time
from otherfs import *
import os
import os.path
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
#
PATH = ""

HELP = """Добро пожаловать в НикольБанк.
Здесь будут вести учет всех кредитов на пятерки по математике.
Команды:
 /reg {имя} {фамилия} {класс} {логин} {пароль} - регистрация в нашем банке
 /login {логин} {пароль} - войти в свой аккаунт
 /unlogin - выйти из аккаунта
 /profile - показать свой профиль
 /request {количество_пятерок} - запрос на получение кредита
 /my_credits - получить список всех своих кредитов
 /help - помощь
"""
HELP2 = """/alogin {логин} - войти в систему с указанным логином 
/aprofile {логин} - просмотреть профиль пользователя с указанным логином
/acredits {логин} - просмотреть все кредиты пользователя с указанным логином
/userlist - получить список всех пользователей
/credlist - получить список всех кредитов
/acredlist - получить список всех активных кредитов
/msgall {сообщение} - отправить сообщение всем залогиненным на данный момент пользователям
/execcom {запрос} - выполнить запрос к БД
"""
HELP3 = """/stop - остановить сервер
/reqlist - просмотреть и одобрить/отклонить первую заявку на кредит
/repaycred {номера_кредитов_через_запятую} - погасить кредиты с указанными уникальными номерами
/execpyc {команда_или_!команда} - выполнить команду от имени Python, Указать ! перед командой для выполнения команды, без - для получения данных
/getlogs {количество} - получить указанное количество строк из конца файла логов
"""

def get_user(chat_id):
    login = ALL.LOGIN[chat_id]
    return get_profile(login)

def get_profile(login):
    res = {}
    for el in ALL.USERS:
        el1 = user(el)
        if el1["login"] == login:
            res = el1
            break
    return res

def savelogin():
    if conf.save:
        with open("save", "w") as f:
            pass
        with open("save", "w") as f:
            json.dump(ALL.LOGIN, f)

#энд
#Важные переменные декларэйшн
conn = 0
bot = Bot('5860281367:AAGmZCTEvrJRXPLOV8bXGtf4JMlwNKir_YU')
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO, filename="logs.log",filemode="a", encoding="utf-8")
class ALL:
        USERS = []
        CREDITS = []
        LOGIN = {}
        REQUESTS = []

#Важные переменные деклерейшн энд

def db_copy(path):
    copies = os.listdir("dbcopy")
    mxnum = 1
    for el in copies:
        if int(el[1:el.find(".")]) >= mxnum:
            mxnum = int(el[1:el.find(".")]) + 1
    with open(path, "rb") as f, open(f"dbcopy/c{mxnum}.db", "wb") as g:
        g.write(f.read())
    print("DB saved to", f"dbcopy/c{mxnum}.db")

def db_load(path, num, rem):
    with open(path, "rb") as f:
        data = f.read()
    try:
        with open(path, "wb") as f, open(f"dbcopy/c{num}.db", "rb") as g:
            f.write(g.read())
    except:
        with open(path, "wb") as f:
            f.write(data)
    if rem:
        os.remove(f"dbcopy/c{num}.db")

def gen_help(lvl):
    global HELP, HELP2, HELP3
    res = ""
    if lvl >= 1:
        res += HELP
    if lvl >= 2:
        res += HELP2
    if lvl >= 3:
        res += HELP3
    return res

def set_default_login(chat_id):
    if chat_id not in ALL.LOGIN.keys():
        ALL.LOGIN[chat_id] = "default"

def can_call(com, chat_id):
    login = ALL.LOGIN[chat_id]
    lev = 1
    for el in ALL.USERS:
        el1 = user(el)
        if el1["login"] == login:
            lev = el1["privilege"]
            break
    return com in get_allowed_commands(lev)

def atex():
    global conn
    conf.config_init()
    print(conf.res)
    savelogin()
    if conf.close_conn == "1":
        conn = None
    logging.shutdown()

async def _start(message):
    COMNAME = "help"
    logging.info(message)
    set_default_login(message.chat.id)

    if can_call(COMNAME, message.chat.id):
        await message.answer(gen_help(get_user(message.chat.id)["privilege"]))
    else:
        await message.answer("Недостаточно прав!")

async def _reg(message):
    COMNAME = "reg"
    logging.info(message)
    set_default_login(message.chat.id)
    if can_call(COMNAME, message.chat.id):
        args = message.get_args().split()
        if len(args) != 5:
            await message.answer("""Пожалуйста, введите свое имя, фамилию, класс, логин и пароль, который вы себе поставите, например:
/reg Петров Иван 7Б petrov qwerty
                             """)
        else:
            _name, _surname, _class, _login, _password = args
            ALL.USERS = SELECT_USERS(conn)
            for el in ALL.USERS:
                el1 = user(el)
                if el1["login"] == _login:
                    await message.answer("Этот логин уже занят!")
                    return 0
            register(conn, _name, _surname, _class, _login, _password)
            await message.answer("Регистрация проведена успешно!")
            ALL.USERS = SELECT_USERS(conn)
    else:
        await message.answer("Недостаточно прав!")

async def _login(message):
    COMNAME = "login"
    logging.info(message)
    set_default_login(message.chat.id)
    
    if can_call(COMNAME, message.chat.id):
        try:
            _login, _password = message.get_args().split()
        except ValueError:
            await message.answer("""Пожалуйста, введите после команды через пробел логин и пароль, например:
/login admin 228pass
""")
            return 0
        for el in ALL.USERS:
            el1 = user(el)
            if el1["login"] == _login:
                break
        else:
            await message.answer("Такого пользователя не существует!")
            return 0
        el1 = user(el)
        if _login == "default":
            await message.answer("Вход не удался!")
        elif _login in ALL.LOGIN.values():
            await message.answer("Человек с этим аккаунтом уже вошел в систему!")
        elif _password == el1["password"]:
            await message.answer("Вход успешен!")
            ALL.LOGIN[message.chat.id] = _login
        else:
            await message.answer("Пароль неверный!")
    else:
        await message.answer("Недостаточно прав!")

async def _unlogin(message):
    COMNAME = "unlogin"
    logging.info(message)
    if ALL.LOGIN[message.chat.id] == "default":
        await message.answer("Вы еще не вошли в систему!")
    elif can_call(COMNAME, message.chat.id):
        try:
            ALL.LOGIN.pop(message.chat.id)
            set_default_login(message.chat.id)
            await message.answer("Вы успешно вышли из аккаунта!")
        except:
            await message.answer("Вы не входили в аккаунт!")
        
    else:
        await message.answer("Недостаточно прав!")

async def _help(message):
    COMNAME = "help"
    logging.info(message)
    set_default_login(message.chat.id)

    if can_call(COMNAME, message.chat.id):
        await message.answer(gen_help(get_user(message.chat.id)["privilege"]))
    else:
        await message.answer("Недостаточно прав!")

async def _profile(message):
    COMNAME = "profile"
    logging.info(message)
    set_default_login(message.chat.id)

    if ALL.LOGIN[message.chat.id] == "default":
        await message.answer("Вы еще не вошли в систему!")
    elif can_call(COMNAME, message.chat.id):
        try:
            b = True
            for i in ALL.USERS:
                i1 = user(i)
                if i1["login"] == ALL.LOGIN[message.chat.id]:
                    break
            else:
                b = False
                await message.answer("Вы не вошли в аккаунт!")
            if b:
                msg = f"""Профиль
    Логин: {i1["login"]}
    Имя: {i1["name"]}
    Фамилия: {i1["surname"]}
    Класс: {i1["class"]}
    Долги: {i1["balance"]}
    """
                await message.answer(msg)

        except:
            await message.answer("Вы не зарегистрировны или не вошли в аккаунт!")
    else:
        await message.answer("Недостаточно прав!")

async def _userlist(message):
    COMNAME = "userlist"
    logging.info(message)
    set_default_login(message.chat.id)

    if ALL.LOGIN[message.chat.id] == "default":
        await message.answer("Вы еще не вошли в систему!")
    elif can_call(COMNAME, message.chat.id):
        res = "Список пользователей в системе:\n"
        for usern in ALL.USERS:
            if get_user(message.chat.id)["privilege"] > user(usern)["privilege"] or get_user(message.chat.id)["login"] == user(usern)["login"] or get_user(message.chat.id)["privilege"] == 3:
                res += str(usern) + "\n"
            else:
                usern = list(usern)
                usern[4] = "#"
                usern[5] = "#"
                res += str(tuple(usern)) + "\n"
        await message.answer(res)

async def _request(message):
    COMNAME = "request"
    logging.info(message)
    set_default_login(message.chat.id)

    if ALL.LOGIN[message.chat.id] == "default":
        await message.answer("Вы еще не вошли в систему!")
    elif can_call(COMNAME, message.chat.id):
        #пока без одобрения
        num = message.get_args()
        if num and num.isdigit() and int(num) > 0:
            execute_query(conn, f"INSERT INTO requests(user, num) VALUES(\"{ALL.LOGIN[message.chat.id]}\", {num})")
            ALL.REQUESTS = SELECT_REQUESTS(conn)
            await message.answer("Кредит запрошен...")
        else:
            await message.answer("Пожалуйста, введите через пробел количество пятерок")
    else:
        await message.answer("Недостаточно прав!")

async def _my_credits(message):
    COMNAME = "my_credits"
    logging.info(message)
    set_default_login(message.chat.id)

    if ALL.LOGIN[message.chat.id] == "default":
        await message.answer("Вы еще не вошли в систему!")
    elif can_call(COMNAME, message.chat.id):
        res = ""
        for credit in ALL.CREDITS:
            credit1 = cred(credit)
            if credit1["user"] == ALL.LOGIN[message.chat.id] and credit1["status"] == 1:
                if credit1["start_date"] != None:
                    res += f"{credit1['cred_id']}. Взят на {credit1['num']} пятерок {credit1['start_date']}.\n"
                else:
                    res += f"{credit1['cred_id']}. Взят на {credit1['num']} пятерок.\n"
        if res == "":
            res = "Кредитов нет!"
        await message.answer(res)
            
    else:
        await message.answer("Недостаточно прав!")

async def _alogin(message):
    COMNAME = "alogin"
    logging.info(message)
    set_default_login(message.chat.id)
    if ALL.LOGIN[message.chat.id] == "default":
        await message.answer("Вы еще не вошли в систему!")
    elif can_call(COMNAME, message.chat.id):
        user_ = message.get_args()
        if len(user_) > 0 and get_user(message.chat.id)["privilege"] >= get_profile(user_)["privilege"]:
            ALL.LOGIN[message.chat.id] = user_
            await message.answer("Вход успешен!")
        elif get_user(message.chat.id)["privilege"] < get_profile(user_)["privilege"]:
            await message.answer("Уровень привилегий этого пользователя выше, чем у вас!")
        else:
            await message.answer("Введите логин через пробел!")

async def _aprofile(message):
    COMNAME = "aprofile"
    logging.info(message)
    set_default_login(message.chat.id)
    if ALL.LOGIN[message.chat.id] == "default":
        await message.answer("Вы еще не вошли в систему!")
    elif can_call(COMNAME, message.chat.id):
        user_ = message.get_args()
        if len(user_) > 0:
            i1 = get_profile(user_)
            if i1 == {}:
                await message.answer("Такого пользователя не существует!")
                return 0
            msg = f"""Профиль
    Логин: {i1["login"]}
    Имя: {i1["name"]}
    Фамилия: {i1["surname"]}
    Класс: {i1["class"]}
    Долги: {i1["balance"]}
    """
            await message.answer(msg)
        else:
            await message.answer("Введите логин через пробел!")

async def _execcom(message):
    global conn
    COMNAME = "execcom"
    logging.info(message)
    set_default_login(message.chat.id)
    if ALL.LOGIN[message.chat.id] == "default":
        await message.answer("Вы еще не вошли в систему!")
    elif can_call(COMNAME, message.chat.id):
        query = message.get_args()
        if query == "":
            await message.answer("Пожалуйста, введите запрос через пробел после команды!")
            return 0
        if query == "INIT":
            INIT(conn)
            await message.answer("DB initialization...")
            return 0
        elif query == "DROP_ALL" and get_user(message.chat.id)["privilege"] >= 3:
            db_copy(PATH)
            DROP_ALL(conn)
            await message.answer("DB dropping...")
            return 0
        elif query == "RECREATE":
            db_copy(PATH)
            RECREATE(conn)
            await message.answer("DB recreation...")
            return 0
        res = str(execute_read_query(conn, query))
        ALL.USERS = SELECT_USERS(conn)
        ALL.CREDITS = SELECT_CREDITS(conn)
        ALL.REQUESTS = SELECT_REQUESTS(conn)
        await message.answer(res)

async def _execpyc(message):
    global conn
    COMNAME = "execcom"
    logging.info(message)
    set_default_login(message.chat.id)
    if ALL.LOGIN[message.chat.id] == "default":
        await message.answer("Вы еще не вошли в систему!")
    elif can_call(COMNAME, message.chat.id):
        query = message.get_args()
        if query == "":
            await message.answer("Пожалуйста, введите запрос через пробел после команды!")
            return 0
        await bot.delete_message(message.chat.id, message.message_id)
        if query[0] == "!" and query != "!":
            exec(query[1:])
        else:
            await message.answer(str(eval(query)))

async def _stop(message):
    global conn
    COMNAME = "stop"
    logging.info(message)
    set_default_login(message.chat.id)
    if ALL.LOGIN[message.chat.id] == "default":
        await message.answer("Вы еще не вошли в систему!")
    elif can_call(COMNAME, message.chat.id):
        await message.answer("Выключение...")
        await bot.delete_message(message.chat.id, message.message_id)
        time.sleep(5)
        raise KeyboardInterrupt

async def _msgall(message):
    COMNAME = "msgall"
    logging.info(message)
    set_default_login(message.chat.id)
    if ALL.LOGIN[message.chat.id] == "default":
        await message.answer("Вы еще не вошли в систему!")
    elif can_call(COMNAME, message.chat.id):
        text = message.get_args()
        if text:
            await bot.delete_message(message.chat.id, message.message_id)
            for user in ALL.LOGIN:
                await bot.send_message(user, "*Сообщение!*\n" + text, parse_mode="Markdown")
        else:
            await message.answer("Пожалуйста, введите текст сообщения через пробел!")

async def _acredits(message):
    COMNAME = "acredits"
    logging.info(message)
    set_default_login(message.chat.id)

    if ALL.LOGIN[message.chat.id] == "default":
        await message.answer("Вы еще не вошли в систему!")
    elif can_call(COMNAME, message.chat.id):
        user_ = message.get_args()
        if len(user_) > 0:
            res = ""
            for credit in ALL.CREDITS:
                credit1 = cred(credit)
                if credit1["user"] == user_ and credit1["status"] == 1:
                    if credit1["start_date"] != None:
                        res += f"{credit1['cred_id']}. Взят на {credit1['num']} пятерок {credit1['start_date']}.\n"
                    else:
                        res += f"{credit1['cred_id']}. Взят на {credit1['num']} пятерок.\n"
            if res == "":
                res = "Кредитов нет!"
            await message.answer(res)
        else:
            await message.answer("Пожалуйста, введите пользователя после команды через пробел!")

async def _credlist(message):
    COMNAME = "credlist"
    logging.info(message)
    set_default_login(message.chat.id)

    if ALL.LOGIN[message.chat.id] == "default":
        await message.answer("Вы еще не вошли в систему!")
    elif can_call(COMNAME, message.chat.id):
        res = "Список кредитов в системе:\n"
        for credit in ALL.CREDITS:
            res += str(credit) + "\n"
        await message.answer(res)

async def _reqlist(message):
    COMNAME = "reqlist"
    logging.info(message)
    set_default_login(message.chat.id)

    if ALL.LOGIN[message.chat.id] == "default":
        await message.answer("Вы еще не вошли в систему!")
    elif can_call(COMNAME, message.chat.id):
        if len(ALL.REQUESTS) == 0:
            await message.answer("Запросов нет!")
            return 0
        c = req(ALL.REQUESTS[0])
        inline_kb_full = InlineKeyboardMarkup(row_width=2).add(InlineKeyboardButton('Одобрить', callback_data='reqac'))
        inline_kb_full.add(InlineKeyboardButton('Отклонить', callback_data='reqdec'))
        await message.reply(f"Кредит запрошен {c['user']} на {c['num']} пятерок. Еще {len(ALL.REQUESTS) - 1} запросов", reply_markup=inline_kb_full)

async def button_callback(callback_query: types.CallbackQuery):
    if callback_query.data == "reqac":
        c = req(ALL.REQUESTS[0])
        execute_query(conn, f"INSERT INTO credits (user, num) VALUES (\"{c['user']}\", {c['num']})")
        execute_query(conn, f"UPDATE users SET balance = balance + 1 WHERE login = \"{c['user']}\"")
        execute_query(conn, f"DELETE FROM requests WHERE req_id={c['req_id']}")
        ALL.CREDITS = SELECT_CREDITS(conn)
        ALL.USERS = SELECT_USERS(conn)

        for el in ALL.LOGIN:
            if ALL.LOGIN[el] == c["user"]:
                await bot.send_message(el, f"Ваш кредит на {c['num']} пятерок одобрен!")
                break

        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, 'Кредит одобрен!')
        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    elif callback_query.data == "reqdec":
        c = req(ALL.REQUESTS[0])
        execute_query(conn, f"DELETE FROM requests WHERE req_id={c['req_id']}")

        for el in ALL.LOGIN:
            if ALL.LOGIN[el] == c["user"]:
                await bot.send_message(el, f"Ваш кредит на {c['num']} пятерок отклонен!")
                break

        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, 'Кредит отклонен!')
        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    ALL.REQUESTS = SELECT_REQUESTS(conn)

async def _repaycred(message):
    COMNAME = "repaycred"
    logging.info(message)
    set_default_login(message.chat.id)

    if ALL.LOGIN[message.chat.id] == "default":
        await message.answer("Вы еще не вошли в систему!")
    elif can_call(COMNAME, message.chat.id):
        args = message.get_args().replace(" ", "").split(",")
        try:
            args = list(map(int, args))
            for c in ALL.CREDITS:
                c1 = cred(c)
                if c1["cred_id"] in args and c1["status"]:
                    execute_query(conn, f"UPDATE credits SET status=0 WHERE cred_id={c1['cred_id']}")
                    execute_query(conn, f"UPDATE users SET balance = balance - 1 WHERE login=\"{c1['user']}\"")
                    await message.answer(f"Кредит {c1['cred_id']} погашен!")
            ALL.USERS = SELECT_USERS(conn)
            ALL.CREDITS = SELECT_CREDITS(conn)
        except:
            await message.answer("Пожалуйста, введите уникальный номер кредита через пробел после команды")

async def _acredlist(message):
    COMNAME = "acredlist"
    logging.info(message)
    set_default_login(message.chat.id)

    if ALL.LOGIN[message.chat.id] == "default":
        await message.answer("Вы еще не вошли в систему!")
    elif can_call(COMNAME, message.chat.id):
        res = "Список кредитов в системе:\n"
        for credit in ALL.CREDITS:
            if cred(credit)["status"]:
                res += str(credit) + "\n"
        await message.answer(res)

async def _getlogs(message):
    COMNAME = "getlogs"
    logging.info(message)
    set_default_login(message.chat.id)

    if ALL.LOGIN[message.chat.id] == "default":
        await message.answer("Вы еще не вошли в систему!")
    elif can_call(COMNAME, message.chat.id):
        num = message.get_args()
        if num.isdigit():
            res = "Логи:\n"
            with open("logs.log", "r", encoding="utf-8") as f:
                lines = f.readlines()
            for i in range(max(0, len(lines) - int(num)), len(lines)):
                res += lines[i]
                await message.answer(res)
                res = ""

COMLIST = {
    "start": _start,
    "reg": _reg,
    "login": _login,
    "unlogin": _unlogin,
    "help": _help,
    "profile": _profile,
    "userlist": _userlist,
    "request": _request,
    "my_credits": _my_credits,
    "alogin": _alogin,
    "aprofile": _aprofile,
    "execcom": _execcom,
    "stop": _stop,
    "msgall": _msgall,
    "acredits": _acredits,
    "credlist": _credlist,
    "reqlist": _reqlist,
    "repaycred": _repaycred,
    "acredlist": _acredlist,
    "execpyc": _execpyc,
    "getlogs": _getlogs
}

async def main():
    global PATH, conn, COMLIST
    
    print("Config:")
    conf.config_init()
    print(conf.res)
    PATH = conf.path

    print("Save-load console:")
    while True:
        r = input(">>> ").split()
        if r == []:
            continue
        if r[0] == "exit":
            break
        if not os.path.isdir("dbcopy"):
            os.mkdir("dbcopy")
        if r[0] == "save":
            db_copy(PATH)
            continue
        if len(r) < 3:
            continue
        if r[0] == "load":
            db_load(PATH, r[1], r[2])
    
    if conf.save:
        if not os.path.exists("save"):
            with open("save", "w") as f:
                f.write("{}")
        with open("save", "r") as f:
            ALL.LOGIN = json.load(f)
        login1 = {}
        for mid in ALL.LOGIN:
            login1[int(mid)] = ALL.LOGIN[mid]
        ALL.LOGIN = login1.copy()

    print("Login list:")
    print(ALL.LOGIN)
    conn = create_connection(PATH)
    INIT(conn)
    check_db(conn)
    ALL.USERS = SELECT_USERS(conn)
    ALL.CREDITS = SELECT_CREDITS(conn)
    ALL.REQUESTS = SELECT_REQUESTS(conn)
    print("User list:")
    print(ALL.USERS)
    print("Credits list:")
    print(ALL.CREDITS)

    for comname in COMLIST:
        dp.register_message_handler(COMLIST[comname], commands=[comname])
    dp.register_callback_query_handler(button_callback, lambda c: c.data in ["reqac", "reqdec"])
    await dp.start_polling(bot)

if __name__ == "__main__":
    atexit.register(atex)
    asyncio.run(main())

