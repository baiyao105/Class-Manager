import subprocess
import sys
import time
from collections.abc import Callable
from io import TextIOWrapper
from typing_extensions import TextIO
from typing import Optional, Union, Any, Callable, List
from queue import Queue
from threading import Thread
from typing import Any, NamedTuple, TextIO

stdout_queue: Queue[str] = Queue()
stderr_queue: Queue[str] = Queue()
output_list: List[str] = []

__all__ = ["CommandOutput", "SystemLogger", "output_list", "stderr_queue", "stdout_queue", "system", "system_lined"]


class SystemLogger(TextIOWrapper):
    """
    用于重定向标准输出的日志记录类

    该类通过继承TextIOWrapper实现对标准输出流的捕获和重定向

    （警告：在反复对一个TextIO[Wrapper]使用过这个类后，该TextIO[Wrapper]将无法正常使用）
    """

    def __init__(
        self,
        stream: Any,
        logger_name: str = "sys.stdout",
        function: Optional[Callable[[str], Any]] = None,
    ):
        super().__init__(stream)
        self.line = ""
        self.function = function
        self.logger_name = logger_name
        self.enabled = True

    def set_enable(self, enable: bool):
        """
        设置是否启用日志记录

        :param enable: 是否启用日志记录
        """
        self.enabled = enable


    def write(self, s: str):
        """
        写入数据到日志

        :param s: 要写入的字符串
        :return: 写入的字符数

        tip：捕获并忽略可能出现的IndexError异常
        """
        self.line += s
        if "\n" in self.line:
            try:
                log_content = self.line.rsplit("\n", 1)[0]
                if self.function:
                    self.function(log_content)
                if self.logger_name == "sys.stdout":
                    stdout_queue.put(log_content)
                elif self.logger_name == "sys.stderr":
                    stderr_queue.put(log_content)
                output_list.append(log_content)
                self.line = self.line.rsplit("\n", 1)[1]
            except IndexError:
                pass

        return len(s)

    def writelines(self, lines):
        try:
            self.line += "\n".join(lines)
            if "\n" in self.line:
                log_content = self.line.rsplit("\n", 1)[0]
                if self.function:
                    self.function(log_content)
                elif self.logger_name == "sys.stdout":
                    stdout_queue.put(log_content)
                    output_list.append(log_content)
                elif self.logger_name == "sys.stderr":
                    stderr_queue.put(log_content)
                    output_list.append(log_content)
                self.line = self.line.rsplit("\n", 1)[1]
            return len(lines)
        except IndexError:
            pass

    def flush(self):
        super().flush()


class CommandOutput(NamedTuple):
    """
    系统命令执行结果的数据结构

    包含命令执行的标准输出、标准错误、返回码等信息
    """

    stdout: str
    stderr: str
    final_output: str
    returncode: int
    pid: int
    time_cost: float
    orig_popen: subprocess.Popen


def system(
    args: str | list,
    show_output: bool = True,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
    encoding: str = "gbk",
    cwd: str | None = None,
    sync_update_bit: int = 1,
) -> CommandOutput:
    """
    执行系统命令并返回结果

    :param args: 命令
    :param show_output: 是否显示输出，默认为True
    :param stdin: 标准输入，默认为None
    :param stdout: 标准输出，默认为None
    :param stderr: 标准错误，默认为None
    :param encoding: 编码，默认为gbk
    :param cwd: 工作目录，默认为None
    :param sync_update_bit: 同步更新位数，默认为1（每次从输出里面读取的字节数）
    :return: 命令执行结果
    """
    st = time.time()
    stdin  = stdin  or sys.stdin
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr

    _popen = subprocess.Popen(
        args,
        stdin=sys.stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
        encoding=encoding,
        bufsize=sync_update_bit,
        shell=True,
        errors="replace",
    )
    _stdout_sb = ""
    _stderr_sb = ""
    _outprt_pointer = 0
    _errprt_pointer = 0
    _final_output = ""

    def _write():
        nonlocal _stderr_sb, _stdout_sb
        nonlocal _outprt_pointer, _errprt_pointer
        while not (len(_stdout_sb) <= _outprt_pointer and len(_stderr_sb) <= _errprt_pointer) or _popen.poll() is None:
            if len(_stdout_sb) > _outprt_pointer:
                _written = len(_stdout_sb)
                if show_output and stdout:
                    stdout.write(_stdout_sb[_outprt_pointer:_written])
                _outprt_pointer = _written
            if len(_stderr_sb) > _errprt_pointer:
                _written = len(_stderr_sb)
                if show_output and stderr:
                    stderr.write(_stderr_sb[_errprt_pointer:_written])
                _errprt_pointer = _written
            time.sleep(0.001)

    t = Thread(target=_write)
    t.start()

    def _read_stdout():
        nonlocal _stdout_sb, _popen, _final_output
        if not _popen.stdout:
            return
        while True:
            try:
                c = _popen.stdout.read(sync_update_bit)
            except BaseException as unused:  # pylint: disable=broad-exception-caught
                c = "?"
            if c == "" and _popen.poll() is not None:
                return
            _stdout_sb += c
            _final_output += c

    def _read_stderr():
        nonlocal _stderr_sb, _popen, _final_output
        if not _popen.stderr:
            return
        while True:
            try:
                c = _popen.stderr.read(sync_update_bit)
            except BaseException as unused:  # pylint: disable=broad-exception-caught
                c = "?"
            if c == "" and _popen.poll() is not None:
                return
            _stderr_sb += c
            _final_output += c

    out_reader = Thread(target=_read_stdout)
    err_reader = Thread(target=_read_stderr)
    out_reader.start()
    err_reader.start()
    while (_popen.poll() is None) or (out_reader.is_alive() and err_reader.is_alive()):
        time.sleep(0.001)
        "就这等着吧"
    pid = _popen.pid
    returncode = _popen.returncode
    sys.stdout.flush()
    sys.stderr.flush()
    while t.is_alive():
        time.sleep(0.001)
    return CommandOutput(_stdout_sb, _stderr_sb, _final_output, returncode, pid, time.time() - st, _popen)


def system_lined(
    args: str | list,
    show_output: bool = True,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
    encoding: str = "gbk",
    cwd: str | None = None,
) -> CommandOutput:
    """
    执行命令，但是输出按行

    :param args: 命令
    :param show_output: 是否显示输出，默认为True
    :param stdin: 标准输入，默认为None
    :param stdout: 标准输出，默认为None
    :param stderr: 标准错误，默认为None
    :param encoding: 编码，默认为gbk
    :param cwd: 工作目录，默认为None
    """
    st = time.time()
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr

    _popen = subprocess.Popen(
        args,
        stdin=sys.stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
        encoding=encoding,
        bufsize=1,
        shell=True,
        errors="replace",
    )
    _stdout_sb = ""
    _stderr_sb = ""
    _final_output = ""

    def _read_stdout():
        nonlocal _stdout_sb, _popen, _final_output
        if not _popen.stdout:
            return
        while True:
            c = _popen.stdout.readline()
            if c == "" and _popen.poll() is not None:
                return
            if show_output:
                sys.stdout.write(c)
            _stdout_sb += c
            _final_output += c

    def _read_stderr():
        nonlocal _stderr_sb, _popen, _final_output
        if not _popen.stderr:
            return
        while True:
            c = _popen.stderr.readline()
            if c == "" and _popen.poll() is not None:
                return
            if show_output:
                sys.stderr.write(c)
            _stderr_sb += c
            _final_output += c

    out_reader = Thread(target=_read_stdout)
    err_reader = Thread(target=_read_stderr)
    out_reader.start()
    err_reader.start()
    while (_popen.poll() is None) or (out_reader.is_alive() and err_reader.is_alive()):
        time.sleep(0.001)
        "就这等着吧"
    pid = _popen.pid
    returncode = _popen.returncode
    sys.stdout.flush()
    sys.stderr.flush()
    return CommandOutput(_stdout_sb, _stderr_sb, _final_output, returncode, pid, time.time() - st, _popen)


if __name__ == "__main__":
    print(system_lined("ping baidu.com"))
