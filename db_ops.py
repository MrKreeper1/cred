import sqlite3
from sqlite3 import Error
import logging
from otherfs import *

CREATE_DATABASE_QUERY1 = """
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  surname TEXT NOT NULL,
  class TEXT NOT NULL,
  login TEXT NOT NULL,
  password TEXT NOT NULL,
  balance INTEGER NOT NULL DEFAULT(0),
  privilege INTEGER NOT NULL DEFAULT(1)
);
"""
CREATE_DATABASE_QUERY2 = """
CREATE TABLE IF NOT EXISTS credits (
  cred_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user TEXT NOT NULL,
  num INTEGER NOT NULL DEFAULT(1),
  start_date DATE NOT NULL,
  finish_date DATE,
  desc TEXT,
  status NUMBER NOT NULL DEFAULT(1)
);
"""

CREATE_DATABASE_QUERY3 = """
CREATE TABLE IF NOT EXISTS requests (
  req_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user TEXT NOT NULL,
  num INTEGER NOT NULL DEFAULT(1)
);
"""

DROP_DATABASE_QUERY1 = """
DROP TABLE users;
"""
DROP_DATABASE_QUERY2 = """
DROP TABLE credits;
"""
DROP_DATABASE_QUERY3 = """
DROP TABLE requests;
"""

logging.basicConfig(level=logging.INFO, filename="logs.log",filemode="a", encoding="utf-8")

def create_connection(path):
    conn = None
    try:
        conn = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return conn

def execute_query(conn, query):
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        conn.commit()
        print("Query executed successfully -", query.replace("\n", " "))
        logging.info("Query executed successfully -" + query.replace("\n", " "))
    except Error as e:
        print(query)
        print(f"The error '{e}' occurred")
        logging.info(f"The error '{e}' occurred in '" + query + "'")

def execute_read_query(conn, query):
    cursor = conn.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        conn.commit()
        return result
    except Error as e:
        print(query)
        print(f"The error '{e}' occurred")

def INIT(conn):
    print("***********\nDB initialization!\n***********")
    execute_query(conn, CREATE_DATABASE_QUERY1)
    execute_query(conn, CREATE_DATABASE_QUERY2)
    execute_query(conn, CREATE_DATABASE_QUERY3)

def DROP_ALL(conn):
    print("***********\nDB dropping!\n***********")
    execute_query(conn, DROP_DATABASE_QUERY1)
    execute_query(conn, DROP_DATABASE_QUERY2)
    execute_query(conn, DROP_DATABASE_QUERY3)

def RECREATE(conn):
    DROP_ALL(conn)
    INIT(conn)

def SELECT_USERS(conn):
    return execute_read_query(conn, "SELECT * FROM users")

def SELECT_CREDITS(conn):
    return execute_read_query(conn, "SELECT * FROM credits")

def SELECT_REQUESTS(conn):
    return execute_read_query(conn, "SELECT * FROM requests")

def register(conn, _name, _surname, _class, _login, _password):
    query = f"""INSERT INTO users(name, surname, class, login, password, balance) VALUES ('{_name}', '{_surname}', '{_class}', '{_login}', '{_password}', 0);
"""
    print(query)
    execute_query(conn, query)

def check_db(conn):
    print("Checking DB...")
    users = SELECT_USERS(conn)
    creds = SELECT_CREDITS(conn)
    reqs = SELECT_REQUESTS(conn)
    for u in users:
        num = 0
        u1 = user(u)
        for c in creds:
            if cred(c)["user"] == u1["login"] and cred(c)["status"]:
                num += 1
        if u1["balance"] != num:
            print("Updating balance for", u1["login"])
            execute_query(conn, f"UPDATE users SET balance = {num} WHERE login=\"{u1['login']}\"")
    loglist = []
    for el in users:
        loglist.append(user(el)["login"])
    for c in creds:
        if cred(c)["user"] not in loglist:
            print(f"Deleting credit number {cred(c)['cred_id']} to {cred(c)['user']}")
            execute_query(conn, f"DELETE FROM credits WHERE cred_id={cred(c)['cred_id']}")
    for r in reqs:
        if req(c)["user"] not in loglist:
            print(f"Deleting request number {req(c)['req_id']} to {req(c)['user']}")
            execute_query(conn, f"DELETE FROM requests WHERE cred_id={req(c)['req_id']}")
