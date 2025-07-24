import socket

# 创建IPv6套接字
client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

# 服务器的IPV6地址和端口（请根据实际服务器IP地址进行替换）
server_address = (input("请输入服务器IP地址:"), int(input("请输入服务器端口号:")))

# 连接服务器
client_socket.connect(server_address)

try:
    message = "Hello, IPV6 Server!"
    print(f"发送消息: {message}")
    client_socket.sendall(message.encode())

    # 接收服务器响应
    data = client_socket.recv(1024)
    print(f"收到来自服务器的响应: {data.decode()}")
finally:
    client_socket.close()
