
from socket_main import SocketDemo

address_ipv6 = input("请输入IPv6地址：")
port = input("请输入端口：")
client_114514 = SocketDemo(address_ipv6, port)
client_114514.run_as_client("114.txt")