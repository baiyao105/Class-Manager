import socket
import time
import random
from noneprompt import Choice, ListPrompt, InputPrompt
from prompt_toolkit.styles import Style
from queue import Queue
import json
import sys
import pickle
import dill as pickle
import json
import copy
from typing import overload, Union, Tuple, Optional, List, Iterable, Any, Callable, Literal, Type, Dict
from threading import Thread
import traceback
from rich.console import Console
import ipaddress
from utils.base import Base

console = Console()

connection_mode: Literal["ipv4", "ipv6"] = "ipv6"

NoneType     = type(None)
BaseDataType = Union[int, float, str, bytes, bool, NoneType]
DataType     = Union[BaseDataType, List[BaseDataType], Dict[BaseDataType, BaseDataType], Tuple[BaseDataType]]

def get_ipv6_addresses() -> List[str]:
    return [addr[4][0] for addr in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET6, socket.SOCK_STREAM)]



socket_type = socket.AF_INET6 if connection_mode == "ipv6" else socket.AF_INET

class Message:
    "一条信息"
    @overload
    def __init__(self, 
                 content:   str,
                 edit_time: float,
                 sender:    str,
                 others:    dict):
        """创建一个新的信息对象。
        
        :param content: 内容
        :param edit_time: 编辑时间
        :param sender: 发送者
        :param others: 其他数据"""

        ...

    @overload
    def __init__(self, json_data: str) -> "Message":
        "从一个json字符串创建一个新的信息对象"
        ...

    def __init__(self,
                 content:   str,
                 edit_time: float = None,
                 sender:    str   = None,
                 others:    dict  = None):
        
        if edit_time:
            
            self.content     = content
            "内容"
            self.edit_time   = edit_time
            "这条信息的编辑时间"
            self.sender      = sender
            "发送这条信息的人"
            self.others      = others
            "其他数据"

        else:
            self.load_from(content)

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join([f'{k}={v!r}' for k, v in self.__dict__ if not k.startswith('__')])})"
    
    def to_string(self):
        "把这个Message转成一个字符串"
        return json.dumps({"content":   self.content,
                           "edit_time": self.edit_time,
                           "sender":    self.sender,
                           "others":    self.others})
    
  
    def load_from(self, obj: Union[str, bytes, dict]):
        "从一个str/bytes加载新的Message"

        if isinstance(obj, bytes):
            obj = obj.decode()
        elif isinstance(obj, dict):
            obj = json.dumps(obj)
        obj: dict      = json.loads(obj)
        self.content   = obj["content"]
        self.edit_time = obj["edit_time"]
        self.sender    = obj["sender"]
        self.others    = obj["others"]
        return self


    


class DevInfo:
    "一个设备的信息"

    def __init__(self,
                 user:      str   = "default",
                 addr:      str   = "localhost",
                 port:      int   = 11451,
                 hostname:  str   = "LAPTOP-11451419",
                 pythonver: tuple = sys.version_info,
                 others:    dict  = None):
        """创建一个新的设备信息对象。

        :param user: 用户名
        :param addr: IP地址
        :param port: 端口
        :param hostname: 主机名
        :param pythonver: Python版本
        :param others: 其他数据    
        """
        self.user      = user
        self.addr      = addr
        self.port      = port
        self.hostname  = hostname
        self.pythonver = pythonver
        self.others    = others

    def to_string(self):
        "把这些信息转换成一个字符串"
        return json.dumps(
            {"user":      self.user,
             "addr":      self.addr,
             "port":      self.port,
             "hostname":  self.hostname,
             "pythonver": self.pythonver,
             "others":    self.others})
    
    def to_dict(self):
        "把这些信息转换成一个字典"
        return {"user":      self.user,
                "addr":      self.addr,
                "port":      self.port,
                "hostname":  self.hostname,
                "pythonver": self.pythonver,
                "others":    self.others
               }

    def load_from(self, obj: Union[str, bytes, dict]):
        "从一个str/bytes加载新的DevInfo"
        if isinstance(obj, bytes):
            obj = obj.decode()
        elif isinstance(obj, dict):
            obj = json.dumps(obj)
        obj: dict = json.loads(obj)
        self.user      = obj["user"]
        self.addr      = obj["addr"]
        self.port      = obj["port"]
        self.hostname  = obj["hostname"]
        self.pythonver = obj["pythonver"]
        self.others    = obj["others"]
        return self
    
    def __eq__(self, value: "DevInfo"):
        if not isinstance(value, DevInfo):
            return False
        return self.to_string() == value.to_string()



class DataPack:
    "数据包"
    def __init__(self, type: str = "default", devinfo: Optional[DevInfo] = None, data: DataType = None):
        self.data = data
        self.devinfo = devinfo
        self.type = type

    def __eq__(self, other):
        return self.data == other
    
    def __req__(self, other):
        return self.data != other
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    @staticmethod
    def from_string(string: str):
        "从一个字符串加载新的DataPack"
        return DataPack().load_from(string)


    def to_string(self):
        "把数据包转换成字符串"
        return json.dumps(self.to_dict())
    

    def to_dict(self):
        "把数据包转换成字典"
        return {"type": self.type,
                "devinfo": self.devinfo.to_dict() if isinstance(self.devinfo, DevInfo) else self.devinfo,
                "data": self.data
               }

    def load_from(self, obj: Union[str, bytes, dict]):
        "从一个str/bytes加载新的DataPack"
        if isinstance(obj, bytes):
            obj = obj.decode()
        elif isinstance(obj, dict):
            obj = json.dumps(obj)
        obj: dict = json.loads(obj)
        self.type = obj["type"]
        self.devinfo = DevInfo().load_from(obj["devinfo"])
        self.data = obj["data"]
        return self



class ProcessingClient:
    "处理中的客户端"
    def __init__(self, devinfo: DevInfo):
        self.addr      = devinfo.addr
        self.port      = devinfo.port
        self.devinfo   = devinfo
        self.user      = devinfo.user
        self.hostname  = devinfo.hostname
        self.pythonver = devinfo.pythonver
        self.others    = devinfo.others


class SocketMsg:
    "连接消息"

    OK = "OK"
    "最敷衍的一句"

    class Connection:
        "连接"
        ClientHello = "client_hello"
        "客户端握手"
        ServerHello = "server_hello"
        "服务器握手"
        ClientConfirm = "client_confirm"
        "客户端连接确认"
        ServerConfirm = "server_confirm"
        "服务端连接确认"
        ClientReject = "client_reject"
        "客户端拒绝"
        ServerReject = "server_reject"
        "服务端拒绝"
        ClientKeepAliveCheck = "client_keep_alive_chk"
        "客户端发起连接检查"
        ClientKeepAliveCheckReply = "server_keep_alive_rep"
        "客户端连接检查回复"
        ServerKeepAliveCheck = "server_keep_alive_chk"
        "服务端发起连接检查"
        ServerKeepAliveCheckReply = "client_keep_alive_rep"
        "服务端连接检查回复"
        ClientDisconnect = "client_disconnect"
        "客户端提出断开连接"
        ServerDisconnect = "server_disconnect"
        "服务端提出断开连接"
        ClientError = "client_error"
        "客户端出错"
        ServerError = "server_error"
        "服务端出错"

        class ServerErrorInfo:
            "服务器错误信息"
            Full = "Server is full."
            "服务器满了"
            TimeOut = "Timeout expired."
            "连接超时"

        class ServerDisconnectInfo:
            "服务器断连信息"
            ClientTimeout = "Client timeout during keep-alive check."
            "客户端在连接检查期间超时"
            ServerError = "Server error."
            "服务器错误"
    




class Connection:
    "连接"

    def __init__(self, 
                 self_addr: str, 
                 self_port: int, 
                 target_addr: Optional[str] = None,
                 target_port: Optional[int] = None,
                 user:        Optional[str] = None,
                 devinfo:     Optional[DevInfo] = None,
                 session_timeout: float = 5):
        """初始化连接。

        :param self_addr: 本地地址
        :param self_port: 本地端口
        :param target_addr: 目标地址
        :param target_port: 目标端口
        :param user: 用户名
        :param devinfo: 设备信息
        :param session_timeout: 会话超时时间

        """
        self.self_addr = self_addr
        self.self_port = self_port
        self.target_addr = target_addr
        self.target_port = target_port
        self.timeout = session_timeout
        for addr in (self_addr, target_addr):
            if addr:
                addr = ipaddress.IPv4Address(addr) if connection_mode == "ipv4" else ipaddress.IPv6Address(addr)

        self.devinfo = DevInfo(
            user if user else "未知用户",
            self_addr,
            self_port,
            socket.gethostname(),
            sys.version_info,
            {}
        ) if not devinfo else devinfo

        # addrinfo = socket.getaddrinfo(self_addr, self_port, socket.AF_INET, socket.SOCK_STREAM)[0]

    def send_rawdata_to(self, 
                        data: Union[bytes, str], 
                        addr: str, 
                        port: int, 
                        timeout: float = -1) -> None:
        """发送原始数据到指定的地址
        
        :param addr: 目标地址
        :param port: 目标端口
        :param from_addr: 发送地址
        :param from_port: 发送端口
        :param data: 发送的数据
        :param timeout: 超时时间
        """
        while 1:
            try:
                Base.log("D", f"向{'[' if connection_mode == 'ipv6' else ''}{addr}{']' if connection_mode == 'ipv6' else ''}:{port}发送数据：{data}", "Connection.send_rawdata_to")
                if isinstance(data, str):
                    data = data.encode()
                elif not isinstance(data, bytes):
                    raise NotImplementedError("bro你丢了个啥东西过来")
                sock = socket.socket(socket_type, socket.SOCK_STREAM)
                if timeout >= 0:
                    sock.settimeout(timeout)
                sock.connect((addr, port))
                sock.sendall(data)
                Base.log("D", f"向{'[' if connection_mode == 'ipv6' else ''}{addr}{']' if connection_mode == 'ipv6' else ''}:{port}发送数据成功", "Connection.send_rawdata_to")
                sock.close()
                return
            except ConnectionResetError:
                Base.log("W", "遇到ConnectionResetError，尝试继续", "Connection.send_rawdata_to")


    def recv_rawdata_as(self, 
                        addr: str, 
                        port: int, 
                        timeout: float = -1, 
                        return_addr: bool = False) \
                        -> Union[bytes, Tuple[bytes, Any]]:
        """等待原始数据
        
        :param addr: 目标地址
        :param port: 目标端口
        :param timeout: 超时时间
        :param return_addr: 是否返回地址
        """
        while 1:
            try:
                Base.log("D", f"在{'[' if connection_mode == 'ipv6' else ''}{addr}{']' if connection_mode == 'ipv6' else ''}:{port}等待数据", "Connection.recv_rawdata_as")
                sock = socket.socket(socket_type, socket.SOCK_STREAM)
                if timeout >= 0:
                    sock.settimeout(timeout)
                sock.bind((addr, port))
                sock.listen()
                conn, addr = sock.accept()
                data = conn.recv(1024)
                conn.close()
                sock.close()
                Base.log("D", f"从{addr}接收到数据：{data}", "Connection.recv_rawdata_as")
                if return_addr:
                    return data, addr
                return data
            except ConnectionResetError:
                Base.log("W", "遇到ConnectionResetError，尝试继续", "Connection.recv_rawdata_as")

                


    @overload
    def send_datapack_to(self,
                        datapack: DataPack, 
                        addr:      str, 
                        port:      int, 
                        timeout:  float = -1,
                        errors:   Literal["ignore", "raise", "log"] = "raise") -> bool:
        """将指定的DataPack发送到addr:port, timeout为-1时表示不设置超时
        
        :param datapack: 要发送的DataPack
        :param addr: 目标地址
        :param port: 目标端口
        :param timeout: 超时时间
        :param errors: 错误处理方式
        :return: 发送是否成功
        """

    @overload
    def send_datapack_to(self,
                         type:    str, 
                         data:    DataType, 
                         devinfo: DevInfo, 
                         addr:    str, 
                         port:    int, 
                         timeout: float = -1,
                         errors:  Literal["ignore", "raise", "log"] = "raise") -> bool:
        """将指定type的data作为DataPack发送到addr:port, timeout为-1时表示不设置超时
        
        :param type: DataPack类型
        :param data: DataPack数据
        :param devinfo: 发送设备信息
        :param addr: 目标地址
        :param port: 目标端口
        :param from_addr: 发送时自身地址
        :param from_port: 发送时自身端口
        :param timeout: 超时时间
        """

    def send_datapack_to(self,
                         arg1: Union[DataPack,                          str], 
                         arg2: Union[str,                               DataType],
                         arg3: Union[int,                               Optional[DevInfo]],
                         arg4: Union[float,                             str]  = None,
                         arg5: Union[Literal["ignore", "raise", "log"], int]  = None,
                         arg6:                                          float = None,
                         arg7:                                          Literal["ignore", "raise", "log"] = None) -> bool:
        "很棒的@overload，这使我大脑爆炸"
        if isinstance(arg1, DataPack):
            datapack = arg1
            addr    = arg2
            port    = arg3
            timeout = arg4 if arg4 is not None else -1
            errors  = arg5 if arg5 is not None else "raise"
    
        else:
            datapack = DataPack(arg1, self.devinfo or arg3, arg2)
            addr    = arg4
            port    = arg5
            timeout = arg6 if arg6 is not None else -1
            errors  = arg7 if arg7 is not None else "raise"

        if errors == "raise":
            self.send_rawdata_to(datapack.to_string(), addr, port, timeout)
            return True
        else:
            try:
                self.send_rawdata_to(datapack.to_string(), addr, port, timeout)
                return True
            except:
                if errors == "log":
                    Base.log_exc("E", f"向{'[' if connection_mode == 'ipv6' else ''}{addr}{']' if connection_mode == 'ipv6' else ''}发送数据失败", "Connection.send_datapack_to", "W")
                return False


    def recv_datapack_as(self, 
                         addr: str, 
                         port: int, 
                         timeout: float = -1, 
                         return_addr: bool = False) \
                        -> Union[DataPack, Tuple[DataPack, Any]]:
        """等待DataPack

        :param addr: 目标地址
        :param port: 目标端口
        :param timeout: 超时时间
        """
        data, addr = self.recv_rawdata_as(addr, port, timeout, return_addr=True)
        if return_addr:
            return DataPack.from_string(data), addr
        return DataPack.from_string(data)
        

    def send_raw(self, data: Union[str, bytes], errors: Literal["ignore", "raise", "log"] = "raise", timeout: Optional[float] = None) -> bool:
        "发送原始数据给target_addr:target_port（快捷方式）"
        if errors == "raise":
            self.send_rawdata_to(data, self.target_addr, self.target_port, self.timeout if not timeout else timeout)
            return True
        else:
            try:
                self.send_rawdata_to(data, self.target_addr, self.target_port, self.timeout if not timeout else timeout)
                return True
            except Exception:
                if errors == "log":
                    Base.log(f"向{self.target_addr}:{self.target_port}发送数据失败", "Connection.send_raw", "W")
                return False
    
    def recv_raw(self, return_addr: bool = False, errors: Literal["ignore", "raise", "log"] = "raise", timeout: Optional[float] = None) \
                                                            -> Union[bytes, Tuple[bytes, Any]]:
        "接收原始数据（快捷方式）"
        if errors == "raise":
            return self.recv_rawdata_as(self.self_addr, self.self_port, self.timeout if not timeout else timeout, return_addr=return_addr)
        else:
            try:
                return self.recv_rawdata_as(self.self_addr, self.self_port, self.timeout if not timeout else timeout, return_addr=return_addr)
            except:
                if errors == "log":
                    Base.log(f"从{self.target_addr}:{self.target_port}接收数据失败", "Connection.recv_raw", "W")
                return None
    
    @overload
    def send_datapack(self, datapack: DataPack, errors: Literal["ignore", "raise", "log"] = "raise", timeout: Optional[float] = None) -> bool:
        "发送DataPack"

    @overload
    def send_datapack(self, type: str, data: DataType, errors: Literal["ignore", "raise", "log"] = "raise", timeout: Optional[float] = None) -> bool:
        "发送DataPack"
    
    def send_datapack(self, 
                      arg1: Union[DataPack,                          str],
                      arg2: Union[Literal["ignore", "raise", "log"], DataType] = None,
                      arg3: Union[Optional[float],                   Literal["ignore", "raise", "log"]] = None,
                      arg4:                                          Optional[float] = None) -> bool:
        "发送DataPack"
        if isinstance(arg1, DataPack):
            return self.send_datapack_to(arg1, 
                                         self.target_addr, 
                                         self.target_port, 
                                         self.timeout if not arg3 else arg3, 
                                         arg2 if not arg2 else "raise")
        elif isinstance(arg1, str):
            return self.send_datapack_to(DataPack(arg1, self.devinfo, arg2), 
                                         self.target_addr, 
                                         self.target_port, 
                                         self.timeout if not arg4 else arg4, 
                                         arg3 if not arg3 else "raise")
        





class Server(Connection):
    "服务器"
    def __init__(self, addr: str, port: int,  max_conn: int = 10):
        """构建一个服务器
        
        :param addr: 将服务器绑定的地址
        :param port: 将服务器绑定的端口"""
        super().__init__(addr, port, None, None, "Server", DevInfo("Server", addr, port, socket.gethostname(), sys.version_info, {}), 5)
        self.max_conn = max_conn
        self.requests: List[DataPack] = []
        self.processing_clients: List[ProcessingClient] = []


    def start(self):
        "启动服务器，不阻塞"
        Thread(target=self.wait_for_requests, name="GetRequests").start()
        Thread(target=self.wait_for_client_connection, name="ClientConnectionHandler").start()
        Thread(target=self.keep_alive_check, name="KeepAliveCheck(Main)").start()
        Thread(target=self.wait_for_client_keepalive_check, name="ClientKeepAliveCheckHandler(Main)").start()

    def run(self):
        "启动服务器，阻塞"
        self.start()
        while True:
            time.sleep(0.1)


    def get_client(self, obj: Union[DataPack, DevInfo]) -> ProcessingClient:
        "获取一个客户端"
        if isinstance(obj, DevInfo):
            addr = obj.addr
            port = obj.port
        elif isinstance(obj, DataPack):
            if not obj.devinfo:
                raise ValueError("DataPack中没有包含devinfo？是不是来自服务端的请求...")
            addr = obj.devinfo.addr
            port = obj.devinfo.port

        for client in self.processing_clients:
            if client.addr == addr and client.port == port:
                return client
        raise ValueError("没有找到这个客户端...")
    
    @overload
    def send_to_client(self, 
                       client: ProcessingClient, 
                       datapack: DataPack, 
                       timeout: Optional[float] = None, 
                       errors: Literal["ignore", "raise", "log"] = "raise") -> bool:
        "将指定的DataPack发送到client"

    @overload
    def send_to_client(self, 
                       client: ProcessingClient, 
                       type: str, 
                       data: DataType, 
                       timeout: Optional[float] = None, 
                       errors: Literal["ignore", "raise", "log"] = "raise") -> bool:
        "将指定的DataPack发送到client"
    
    def send_to_client(self, 
                    client: ProcessingClient, 
                    arg1: Union[DataPack,                          str],
                    arg2: Union[Optional[float],                   DataType], 
                    arg3: Union[Literal["ignore", "raise", "log"], Optional[float]]    = None,
                    arg4: Union[                                   Literal["ignore", "raise", "log"]] = None) -> bool:
        
        if isinstance(arg1, DataPack):
            return self.send_datapack_to(arg1, 
                                  client.addr, 
                                  client.port, 
                                  arg2 if arg2 else self.timeout, 
                                  arg3 if arg3 else "raise")
        elif isinstance(arg1, str):
            return self.send_datapack_to(arg1, 
                                  arg2, 
                                  self.devinfo, 
                                  client.addr, 
                                  client.port, 
                                  arg3 if arg3 else self.timeout, 
                                  arg4 if arg4 else "raise")

    def wait_for_client_connection(self):
        "等待客户端连接"
        while True:
            req = self.get_request(SocketMsg.Connection.ClientHello)
            Base.log("I", f"收到一个客户端连接请求，来自{'[' if connection_mode == 'ipv6' else ''}{req.devinfo.addr}{']' if connection_mode == 'ipv6' else ''}:{req.devinfo.port}", "Connection.Server.wait_for_client_connection")
            def handle_client():
                nonlocal req
                client = ProcessingClient(req.devinfo)
                Base.log("I", "开始处理客户端连接请求", "Connection.Server.handle_client")
                Base.log("I", "向客户端发送ServerHello", "Connection.Server.handle_client")
                self.send_to_client(client, SocketMsg.Connection.ServerHello, "Hello there!")
                Base.log("I", "等待客户端回复", "Connection.Server.handle_client")
                try:
                    req = self.get_request(SocketMsg.Connection.ClientConfirm, 10)
                    Base.log("I", f"收到客户端的ClientConfirm: {req.data}", "Connection.Server.handle_client")
                    if len(self.processing_clients) < self.max_conn:
                        self.send_to_client(client, SocketMsg.Connection.ServerConfirm, "Hello there!")
                        self.processing_clients.append(client)
                        Base.log("I", "客户端连接成功", "Connection.Server.handle_client")
                        Base.log("I", f"将{client.addr}:{client.port}添加到处理客户端列表, 当前连接数：{len(self.processing_clients)}", 
                                "Connection.Server.handle_client")
                    else:
                        Base.log("I", "客户端连接失败，服务器已满", "Connection.Server.handle_client")
                        self.send_to_client(client, SocketMsg.Connection.ServerError, SocketMsg.Connection.ServerErrorInfo.Full)

                except TimeoutError:
                    Base.log("W", "客户端连接超时，关闭连接", "Connection.Server.handle_client")
                    self.send_to_client(client, SocketMsg.Connection.ServerError, SocketMsg.Connection.ServerErrorInfo.TimeOut)

            Thread(target=handle_client).start()
            Base.log("I", "等待下一个客户端连接请求", "Connection.Server.wait_for_client_connection")

    def wait_for_requests(self):
        "等待请求"
        while True:
            self.requests.append(self.recv_datapack_as(self.self_addr, self.self_port))

    
    def get_request(self, type: Union[str, Iterable[str]], timeout: float = -1, from_client: ProcessingClient = None) -> DataPack:
        """获取一个请求，并且把这个请求从请求列表中移除

        :param type: 请求的类型
        :param timeout: 超时时间"""
        st = time.time()
        while time.time() - st < timeout or timeout < 0:
            for request in self.requests:
                if isinstance(type, str):
                    if request.type == type:
                        if not from_client or from_client.devinfo == request.devinfo:
                            self.requests.remove(request)
                            return request
                else:
                    for t in type:
                        if request.type == t:
                            self.requests.remove(request)
                            return request
            time.sleep(0.01)
        raise TimeoutError(f"在{repr(timeout)}秒内没有获取到{repr(type)}类型的请求")

    def check_client(self, client: ProcessingClient) -> bool:
        is_alive = False
        max_retry = 3
        for i in range(max_retry):
            Base.log("I", f"检查{'[' if connection_mode == 'ipv6' else ''}{client.addr}{']' if connection_mode == 'ipv6' else ''}:{client.port}的连接", "Connection.Server.keep_alive_check")
            try:
                self.send_to_client(client, SocketMsg.Connection.ServerKeepAliveCheck, "")
                Base.log("I", f"向{'[' if connection_mode == 'ipv6' else ''}{client.addr}{']' if connection_mode == 'ipv6' else ''}:{client.port}发送ServerKeepAliveCheck", "Connection.Server.keep_alive_check")
                req = self.get_request(SocketMsg.Connection.ServerKeepAliveCheckReply, 1, client)
                Base.log("I", f"收到{'[' if connection_mode == 'ipv6' else ''}{client.addr}{']' if connection_mode == 'ipv6' else ''}:{client.port}的ServerKeepAliveCheckReply，连接继续（内容：{repr(req.data)}）",
                        "Connection.Server.keep_alive_check")
                is_alive = True
                return True
            except TimeoutError:
                Base.log("W", f"在1秒内没有收到{'[' if connection_mode == 'ipv6' else ''}{client.addr}{']' if connection_mode == 'ipv6' else ''}:{client.port}的ServerKeepAliveCheckReply... ({i+1} / {max_retry})", "Connection.Server.keep_alive_check")
        if not is_alive:
            Base.log("W", f"{'[' if connection_mode == 'ipv6' else ''}{client.addr}{']' if connection_mode == 'ipv6' else ''}:{client.port}的连接已断开，发送ServerDisconnect", "Connection.Server.keep_alive_check")
            try:
                self.send_to_client(client, SocketMsg.Connection.ServerDisconnect, "", timeout=1)
            except:
                Base.log("W", f"{'[' if connection_mode == 'ipv6' else ''}{client.addr}:{client.port}{']' if connection_mode == 'ipv6' else ''}连ServerDisconnect也没接，多半似掉了", "Connection.Server.keep_alive_check")
            Base.log("W", f"{'[' if connection_mode == 'ipv6' else ''}{client.addr}{']' if connection_mode == 'ipv6' else ''}:{client.port}的连接已断开", "Connection.Server.keep_alive_check")
            self.processing_clients.remove(client)
            Base.log("I", f"当前连接数：{len(self.processing_clients)}", "Connection.Server.keep_alive_check")
            return False
        return True
    
    def keep_alive_check(self):
        "为客户端保持连接"
        while True:
            Base.log("I", F"准备检查连接，当前连接数：{len(self.processing_clients)}")
            for client in self.processing_clients:
                Thread(name=f"KeepAliveCheck({'[' if connection_mode == 'ipv6' else ''}{client.addr}{']' if connection_mode == 'ipv6' else ''}:{client.port}))", target=self.check_client, args=(client,)).start()
            time.sleep(10)

    def wait_for_client_keepalive_check(self):
        "等待客户端主动检查连接"
        while True:
            try:
                req = self.get_request(SocketMsg.Connection.ClientKeepAliveCheck)
                client = self.get_client(req)
                Base.log("I", F"收到{'[' if connection_mode == 'ipv6' else ''}{client.addr}{']' if connection_mode == 'ipv6' else ''}:{client.port}的ClientKeepAliveCheck，发送ClientKeepAliiveCheckReply", "Server.wait_for_client_keepalive_check")
                def send(client: ProcessingClient):
                    retry = 3
                    for i in range(retry):
                        try:
                            self.send_to_client(client, SocketMsg.Connection.ClientKeepAliveCheckReply, SocketMsg.OK, 1)
                            Base.log("I", 
                                     f"向{'[' if connection_mode == 'ipv6' else ''}{client.addr}{']' if connection_mode == 'ipv6' else ''}:{client.port}"
                                     "发送ClientKeepAliveCheckReply成功", "Server.wait_for_client_keepalive_check")
                            return
                        except:
                            Base.log_exc_short(f"向{'[' if connection_mode == 'ipv6' else ''}{client.addr}{']' if connection_mode == 'ipv6' else ''}:{client.port}"
                                     F"发送ClientKeepAliveCheckReply失败（{i+1} / {retry}）", "Server.wait_for_client_keepalive_check")
                    Base.log("W", f"{'[' if connection_mode == 'ipv6' else ''}{client.addr}{']' if connection_mode == 'ipv6' else ''}:{client.port}"
                                  f"在ClientKeepAliveCheck中自己断开连接了，不管它")
                Thread(target=lambda client=client, f=send: f(client), name=F"ClientKeepAliveCheckHandler({'[' if connection_mode == 'ipv6' else ''}{client.addr}{']' if connection_mode == 'ipv6' else ''}:{client.port})").start()
            except:
                Base.log_exc("等待ClientKeepAliveCheck时出现错误", "Server.wait_for_client_keepalive_check")





class Client(Connection):
    "客户端"

    def __init__(self, addr: str, port: int, server_addr: str, server_port: int, username: str):
        self.addr = addr
        self.port = port
        self.server_addr = server_addr
        self.server_port = server_port
        self.devinfo     = DevInfo(username, addr, port, socket.gethostname(), sys.version_info, {})
        self.connected   = False
        self.requests:List[DataPack] = []
        self.startups: List[Callable] = []

    def start(self):
        self.startups = [
            self.wait_for_requests,
            self.connect,
            self.wait_for_keepalive_check,
            self.server_keepalive_check
        ]
        for startup in self.startups:
            Thread(target=startup).start()

    def send_request(self, type: str, data: str):
        "发送一个请求"
        self.send_datapack_to(DataPack(type, self.devinfo, data), self.server_addr, self.server_port)

    def wait_for_requests(self):
        "等待请求"
        while True:
            self.requests.append(self.recv_datapack_as(self.addr, self.port))

    def get_request(self, type: Union[str, Iterable[str]], timeout: float = -1) -> DataPack:
        """获取一个请求，并且把这个请求从请求列表中移除

        :param type: 请求的类型
        :param timeout: 超时时间"""
        st = time.time()
        while time.time() - st < timeout or timeout < 0:
            for request in self.requests:
                if isinstance(type, str):
                    if request.type == type:
                        self.requests.remove(request)
                        return request
                else:
                    for t in type:
                        if request.type == t:
                            self.requests.remove(request)
                            return request
            time.sleep(0.01)
        raise TimeoutError(f"在{repr(timeout)}秒内没有获取到{repr(type)}类型的请求")

    def connect(self, server_addr: str = None, server_port: int = None) -> bool:
        "连接服务器"
        self.server_addr = server_addr if server_addr is not None else self.server_addr
        self.server_port = server_port if server_port is not None else self.server_port
        try:
            Base.log("I", f"正在连接服务器{self.server_addr}:{self.server_port}，发送ClientHello", "Connection.Client.connect")
            self.send_request(SocketMsg.Connection.ClientHello, "Hello?")
            self.get_request(SocketMsg.Connection.ServerHello, 1)
            Base.log("I", f"访问服务器{self.server_addr}:{self.server_port}成功，接收到ServerHello，尝试确认连接，发送ClientConfirm", "Connection.Client.connect")
            self.send_request(SocketMsg.Connection.ClientConfirm, "OK")
            req = self.get_request((SocketMsg.Connection.ServerConfirm, SocketMsg.Connection.ServerError), 1)
            if req.type == SocketMsg.Connection.ServerConfirm:
                Base.log("I", f"接收到ServerConfirm，连接服务器{self.server_addr}:{self.server_port}成功，服务器确认连接", "Connection.Client.connect")
                self.connected = True
                return True
            elif req.type == SocketMsg.Connection.ServerError:
                Base.log("W", f"接收到ServerError，连接服务器{self.server_addr}:{self.server_port}失败，服务器拒绝连接，详细如下", "Connection.Client.connect")
                Base.log("W", f"[{req.type}] {req.data}", "Connection.Client.connect")
                self.connected = False
                return False

        except TimeoutError:
            Base.log(f"连接服务器{self.server_addr}:{self.server_port}失败，对方没有响应", "Connection.Client.connect")
            self.connected = False
            return False
        
        except:
            Base.log_exc(f"连接服务器{self.server_addr}:{self.server_port}失败，发生未知错误", "Connection.Client.connect")


    def wait_for_keepalive_check(self):
        "等待服务器连接检测"
        while True:
            req = self.get_request((SocketMsg.Connection.ServerKeepAliveCheck, SocketMsg.Connection.ServerDisconnect))
            if req.type == SocketMsg.Connection.ServerKeepAliveCheck:
                Base.log("I", f"接收到ServerKeepAliveCheck（内容：{repr(req.data)}），发送ServerKeepAliveCheckReply", 
                        "Connection.Client.wait_for_keepalive_check")
                self.send_request(SocketMsg.Connection.ServerKeepAliveCheckReply, "OK")
            elif req.type == SocketMsg.Connection.ServerDisconnect:
                Base.log("I", f"接收到ServerDisconnect（内容：{repr(req.data)}），服务器要求断开连接，发送ClientDisconnect（多半是超时了）", 
                        "Connection.Client.wait_for_keepalive_check")
                self.send_request(SocketMsg.Connection.ClientDisconnect, "OK")
                return


    def check_server_connection(self):
        retry = 3
        for i in range(retry):
            Base.log("I", "向服务器发送ClientKeepAliveCheck", "Client.check_server_connection")
            try:
                self.send_request(SocketMsg.Connection.ClientKeepAliveCheck, "")
            except:
                Base.log_exc_short("发送ClientKeepAliveCheck失败: ", "Client.check_server_connection")
                Base.log("W", F"进行重试 ({i+1} / {retry})")
                continue
            try:
                resp = self.get_request(SocketMsg.Connection.ClientKeepAliveCheckReply, 1)
                Base.log("I" , F"收到了服务器的ClientKeepAliveCheckReply (内容：{resp.data})，连接继续", "Client.check_server_connection")
                return True
            except:
                Base.log("W", "在1秒内没有收到服务器的ClientKeepAliveCheckReply...", "Client.check_server_connection")
        Base.log("W", "检查连接失败", "Client.check_server_connection")
        return False
    
    def server_keepalive_check(self):
        while True:
            time.sleep(10)
            if self.connected:
                Base.log("I", "检查服务器连接")
                stat = self.check_server_connection()
                if not stat:
                    Base.log("W", "服务器未响应，尝试断开连接")
                    try:
                        self.send_request(SocketMsg.Connection.ClientDisconnect, "")
                    except:
                        Base.log_exc_short("发送断开连接请求失败：")
                    Base.log("I", "询问是否尝试重连")
                    self.connected = False
                    reply = input("服务器已断开连接，是否尝试重连？(y/n)")
                    if reply == "y":
                        while not self.connect():
                            reply = input("重连失败，是否重试？(y/n)")
                            if reply == "n":
                                sys.exit(0)
                        






                
            









