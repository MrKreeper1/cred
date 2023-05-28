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

def get_allowed_commands(priv):
    com = []
    if priv >= 1:
        com += ["reg", "login", "unlogin", "help", "start", "profile", "request", "my_credits"]
    if priv >= 2:
        com += ["alogin", "aprofile", "userlist", "execcom", "msgall"]
    elif priv >= 3:
        com += ["stop"]
    return com

def user(el):
    res = {
        "id": el[0],
        "name": el[1],
        "surname": el[2],
        "class": el[3],
        "login": el[4],
        "password": el[5],
        "balance": el[6],
        "privilegy": el[7]
        }
    return res

def cred(el):
    res = {
        "cred_id": el[0],
        "user": el[1],
        "num": el[2],
        "start_date": el[3],
        "finish_date": el[4],
        "desc": el[5],
        "status": el[6]
    }
    return res

def get_user(chat_id):
    login = ALL.LOGIN[chat_id]
    res = {}
    for el in ALL.USERS:
        el1 = user(el)
        if el1["login"] == login:
            res = el1
            break
    return res

def get_profile(login):
    res = {}
    for el in ALL.USERS:
        el1 = user(el)
        if el1["login"] == login:
            res = el1
            break
    print(res)
    return res

def savelogin():
    if conf.save:
        with open("save", "w") as f:
            pass
        with open("save", "w") as f:
            json.dump(ALL.LOGIN, f)



conn = 0
iscon = False
#энд
#Важные переменные декларэйшн
bot = Bot('5860281367:AAGmZCTEvrJRXPLOV8bXGtf4JMlwNKir_YU')
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO, filename="logs.log",filemode="a", encoding="utf-8")
class ALL:
        USERS = []
        CREDITS = []
        LOGIN = {}

#Важные переменные деклерейшн энд

def set_default_login(chat_id):
    if chat_id not in ALL.LOGIN.keys():
        ALL.LOGIN[chat_id] = "default"

def can_call(com, chat_id):
    login = ALL.LOGIN[chat_id]
    lev = 1
    for el in ALL.USERS:
        el1 = user(el)
        if el1["login"] == login:
            lev = el1["privilegy"]
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
    COMNAME = "start"
    logging.info(message)
    set_default_login(message.chat.id)

    if can_call(COMNAME, message.chat.id):
        await message.answer('Привет! Добро пожаловать в НикольКредитБанк!')
    else:
        await message.answer("Недостаточно прав!")
    savelogin()

async def _reg(message):
    COMNAME = "reg"
    logging.info(message)
    set_default_login(message.chat.id)
    print(message)
    if can_call(COMNAME, message.chat.id):
        args = message.get_args().split()
        if len(args) != 5:
            await message.answer("""Пожалуйста, введите свое имя, фамилию, класс, логин и пароль, который вы себе поставите, например:
/reg Петров Иван 7Б petrov qwerty
                             """)
        else:
            _name, _surname, _class, _login, _password = args
            ALL.USERS = SELECT_USERS(conn)
            print(ALL.USERS, _login)
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
    savelogin()

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
        else:
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
        print(ALL.LOGIN)
    else:
        await message.answer("Недостаточно прав!")
    savelogin()

async def _unlogin(message):
    COMNAME = "unlogin"
    logging.info(message)
    if ALL.LOGIN[message.chat.id] == "default":
        await message.answer("Вы еще не вошли в систему!")
    elif can_call(COMNAME, message.chat.id):
        try:
            ALL.LOGIN.pop(message.chat.id)
            print(ALL.LOGIN)
            set_default_login(message.chat.id)
            await message.answer("Вы успешно вышли из аккаунта!")
        except:
            await message.answer("Вы не входили в аккаунт!")
        
    else:
        await message.answer("Недостаточно прав!")
    savelogin()

async def _help(message):
    COMNAME = "help"
    logging.info(message)
    set_default_login(message.chat.id)

    if can_call(COMNAME, message.chat.id):
        await message.answer(HELP)
    else:
        await message.answer("Недостаточно прав!")
    savelogin()

async def _profile(message):
    COMNAME = "profile"
    logging.info(message)
    set_default_login(message.chat.id)

    if ALL.LOGIN[message.chat.id] == "default":
        await message.answer("Вы еще не вошли в систему!")
    elif can_call(COMNAME, message.chat.id):
        try:
            b = True
            res = []
            for i in ALL.USERS:
                i1 = user(i)
                if i1["login"] == ALL.LOGIN[message.chat.id]:
                    res = i1
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
    savelogin()
    print(ALL.LOGIN)

async def _userlist(message):
    COMNAME = "userlist"
    logging.info(message)
    set_default_login(message.chat.id)

    if ALL.LOGIN[message.chat.id] == "default":
        await message.answer("Вы еще не вошли в систему!")
    elif can_call(COMNAME, message.chat.id):
        res = "Список пользователей в системе:\n"
        for user in ALL.USERS:
            res += str(user) + "\n"
        await message.answer(res)
    else:
        await message.answer("Недостаточно прав!")
    savelogin()

async def _request(message):
    COMNAME = "request"
    logging.info(message)
    set_default_login(message.chat.id)

    if ALL.LOGIN[message.chat.id] == "default":
        await message.answer("Вы еще не вошли в систему!")
    elif can_call(COMNAME, message.chat.id):
        #пока без одобрения
        num = message.get_args()
        if num:
            execute_query(conn, f"INSERT INTO credits(user, num) VALUES(\"{ALL.LOGIN[message.chat.id]}\", {num})")
            execute_query(conn, f"UPDATE users SET balance = balance + 1 WHERE login=\"{ALL.LOGIN[message.chat.id]}\"")
            ALL.CREDITS = SELECT_CREDITS(conn)
            await message.answer("Кредит одобрен!")
        else:
            await message.answer("Пожалуйста, введите через пробел количество пятерок")
    else:
        await message.answer("Недостаточно прав!")
    savelogin()

async def _my_credits(message):
    COMNAME = "my_credits"
    logging.info(message)
    set_default_login(message.chat.id)

    if ALL.LOGIN[message.chat.id] == "default":
        await message.answer("Вы еще не вошли в систему!")
    elif can_call(COMNAME, message.chat.id):
        res, count = "", 0
        print(ALL.CREDITS)
        for credit in ALL.CREDITS:
            credit1 = cred(credit)
            if credit1["user"] == ALL.LOGIN[message.chat.id] and credit1["status"] == 1:
                count += 1
                if credit1["start_date"] != None:
                    res += f"{count}. Взят на {credit1['num']} пятерок {credit1['start_date']}.\n"
                else:
                    res += f"{count}. Взят на {credit1['num']} пятерок.\n"
        if res == "":
            res = "Кредитов нет!"
        await message.answer(res)
            
    else:
        await message.answer("Недостаточно прав!")
    savelogin()

async def _alogin(message):
    COMNAME = "alogin"
    logging.info(message)
    set_default_login(message.chat.id)
    if ALL.LOGIN[message.chat.id] == "default":
        await message.answer("Вы еще не вошли в систему!")
    elif can_call(COMNAME, message.chat.id):
        user_ = message.get_args()
        if len(user_) > 0:
            ALL.LOGIN[message.chat.id] = user_
            print(ALL.LOGIN)
            await message.answer("Вход успешен!")
        else:
            await message.answer("Введите логин через пробел!")
    else:
        await message.answer("Недостаточно прав!")
    savelogin()

async def _aprofile(message):
    COMNAME = "aprofile"
    logging.info(message)
    set_default_login(message.chat.id)
    if ALL.LOGIN[message.chat.id] == "default":
        await message.answer("Вы еще не вошли в систему!")
    elif can_call(COMNAME, message.chat.id):
        user_ = message.get_args()
        print(user_)
        if len(user_) > 0:
            i1 = get_profile(user_)
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
    else:
        await message.answer("Недостаточно прав!")
    savelogin()

async def _execcom(message):
    global conn
    COMNAME = "execcom"
    logging.info(message)
    set_default_login(message.chat.id)
    if ALL.LOGIN[message.chat.id] == "default":
        await message.answer("Вы еще не вошли в систему!")
    elif can_call(COMNAME, message.chat.id):
        query = message.get_args()
        res = str(execute_read_query(conn, query))
        ALL.USERS = SELECT_USERS(conn)
        ALL.CREDITS = SELECT_CREDITS(conn)
        await message.answer(res)
    else:
        await message.answer("Недостаточно прав!")
    savelogin()

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
    else:
        await message.answer("Недостаточно прав!")

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
        await message.answer("Недостаточно прав!")

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
    "msgall": _msgall
}

async def main():
    global PATH, conn, COMLIST
    
    conf.config_init()
    print(conf.res)
    PATH = conf.path
    if conf.save:
        with open("save", "r") as f:
            ALL.LOGIN = json.load(f)
        login1 = {}
        for mid in ALL.LOGIN:
            login1[int(mid)] = ALL.LOGIN[mid]
        ALL.LOGIN = login1.copy()


    print(ALL.LOGIN)
    conn = create_connection(PATH)
    INIT(conn)
    ALL.USERS = SELECT_USERS(conn)
    ALL.CREDITS = SELECT_CREDITS(conn)
    print(ALL.USERS)
    print(ALL.CREDITS)

    for comname in COMLIST:
        dp.register_message_handler(COMLIST[comname], commands=[comname])
    await dp.start_polling(bot)

if __name__ == "__main__":
    atexit.register(atex)
    asyncio.run(main())

