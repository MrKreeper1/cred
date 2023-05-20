from db_ops import *

__ALL__ = ["con"]

#СКьюЛь часть
PATH = "main.db"
    
def con(conn):
    global last
    run = True
    while run:
        run = False
        com = input(">>> ")
        line = False
        if com == "INIT":
            INIT(conn)
            continue
        elif com == "DROP_ALL":
            DROP_ALL(conn)
            continue
        elif com == "RECREATE":
            RECREATE(conn)
            continue
        elif com == "!last":
            com = last
        elif com == "!exit":
            conn = 0
            exit(0)
        if len(com) > 1 and com[0] == "!":
            line = True
            last = com
            com = com[1:]
        else:
            last = com
        res = execute_read_query(conn, com)
        if res != None:
            if line:
                try:
                    for el in res:
                        print(el)
                except:
                    pass
            else:
                print(res)

if __name__ == "__main__":
    conn = create_connection(PATH)
    last = ""
    while True:
        con(conn)