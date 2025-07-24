import socket
import requests

# 创建IPv6套接字
server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

# 设置服务器地址和端口（选择公网可用的端口）
server_address = ('::', 12345)  # '::'表示绑定到所有可用的IPv6地址
server_socket.bind(server_address)
print((requests.get("https://v6.ident.me").text, 12345))


# 监听连接
server_socket.listen(1)

print("服务器正在等待连接...")

# 接受客户端连接
connection, client_address = server_socket.accept()
print(f"连接来自: {client_address}")

try:
    while True:
        data = connection.recv(1024)  # 接收数据
        if data:
            print(f"收到数据: {data.decode()}")
            # 响应客户端
            connection.sendall("消息已收到".encode())
        else:
            print("客户端已关闭连接")
            break
finally:
    connection.close()
    server_socket.close()
