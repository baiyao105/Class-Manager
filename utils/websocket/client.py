import socket


ipv6 = input("输入ipv6地址:")

port = input("输入端口:")

addr = socket.getaddrinfo(ipv6, port, 0, 0)[0][-1]

tcp_server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

tcp_server.connect(addr)
try:
    while True:
        tcp_server.send(input("输入信息, 按回车发送, Ctrl+C退出:").encode("utf-8"))
except KeyboardInterrupt:
    tcp_server.close()

