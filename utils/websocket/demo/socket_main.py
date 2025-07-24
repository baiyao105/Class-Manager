import socket

class SocketDemo:
    def __init__(self, ip:str = "::1", port:int = 11451):
        self.ip = ip
        self.port = int(port)

    def run_as_server(self):
        server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

        server_socket.bind((self.ip, self.port))
        server_socket.listen(1)

        print("等待客户端连接...")

        connect, address = server_socket.accept()
        self.connect = connect
        self.address = address

        print(f"连接来自{self.address}")

        with open("received_file", "wb") as f:
            print("接收文件中...")
            while True:
                recv_data = self.connect.recv(32)
                self.recv_data = recv_data
                if not recv_data:
                    break
                f.write(self.recv_data)
        print("文件接收完毕！")
        self.connect.close()
        server_socket.close()

    def run_as_client(self, file_path:str = "C:\\Windows\\System32\\cmd.exe"):
        self.file_path = file_path

        client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

        client_socket.connect((self.ip, self.port))

        with open(file_path, "rb") as f:
            print("发送文件中...")
            send_data = f.read(32)
            while send_data:
                client_socket.send(send_data)
                send_data = f.read(32)
        print("文件发送完毕！")
        
        client_socket.close()


        