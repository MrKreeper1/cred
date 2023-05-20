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