def user(el):
    res = {
        "id": el[0],
        "name": el[1],
        "surname": el[2],
        "class": el[3],
        "login": el[4],
        "password": el[5],
        "balance": el[6],
        "privilege": el[7]
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
def req(el):
    res = {
        "req_id": el[0],
        "user": el[1],
        "num": el[2]
    }
    return res
def get_allowed_commands(priv):
    com = []
    if priv >= 1:
        com += ["reg", "login", "unlogin", "help", "start", "profile", "request", "my_credits"]
    if priv >= 2:
        com += ["alogin", "aprofile", "userlist", "execcom", "msgall", "acredits", "credlist", "acredlist"]
    if priv >= 3:
        com += ["stop", "reqlist", "repaycred", "execpyc"]
    return com