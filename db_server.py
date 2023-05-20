import socket
from db_ops import execute_read_query, create_connection
import config_parse as conf

conf.config_init()
PATH = conf.path
dbconn = create_connection(PATH)

sock = socket.socket()
sock.bind(('', 9090))
sock.listen(1)
conn, addr = sock.accept()

print('connected:', addr)

while True:
    data = conn.recv(1024)
    if not data:
        break
    res = execute_read_query(dbconn, data)
    conn.send(str(res))

conn.close()