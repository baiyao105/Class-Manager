import random
import requests
import socket
from socket_main import SocketDemo

address_ipv6 = requests.get("https://v6.ident.me/").text
random_port = random.randint(11451, 65500)
for addr in [address_ipv6] + [addr[4][0] for addr in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET6, socket.SOCK_STREAM)] \
    + ["::0", "::1"]:
    try:
        server_114514 = SocketDemo(addr, random_port)
        print(f"服务器在[{addr}]:{random_port}上开启！")
        server_114514.run_as_server()
    except:
        print(f"服务器在[{addr}]:{random_port}上开启失败！")

