import os.path
if not os.path.exists("config"):
    data = """close_conn=1
path=main.db
save=1"""
    with open("config", "w") as f:
        f.write(data)

close_conn = True
path = ""
save = False
res = {}
def config_init():
    global res, close_conn, path, save
    with open("config", "r") as f:
        lines = f.readlines()
    res = {}
    for line in lines:
        pref, val = line.replace("\n", "").split("=")
        if pref.isdigit():
            res[pref] = int(val)
        else:
            res[pref] = val
    close_conn = res["close_conn"]
    path = res["path"]
    save = bool(res["save"])
        
if __name__ == "__main__":
    config_init()
    print(res)