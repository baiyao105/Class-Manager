import socket

import requests

import random



ipv6 = requests.get("https://v6.ident.me").text

port = random.randint(10000, 30000)

addrinfo = socket.getaddrinfo(ipv6, port, 0, 0)[0]

print("服务器地址信息：", addrinfo[-1])

tcp_server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

tcp_server.bind(addrinfo[-1])

tcp_server.listen(5)


while True:

    conn, addr = tcp_server.accept()
    print("客户端开始连接，地址: ", addr)

    while True:

        cmd = conn.recv(1024)
        print("客户端发来数据：", cmd)

        if not cmd:
            break

    print("客户端断开连接，等待下一个客户端连接")

    conn.close()

