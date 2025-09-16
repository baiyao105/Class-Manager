"""文件操作工具模块

提供各种文件操作相关的工具函数。
"""

import csv
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union

from .logger import get_logger

logger = get_logger("file_ops")


class FileOperationError(Exception):
    """文件操作错误异常"""


class FileManager:
    """文件管理器"""

    @staticmethod
    def ensure_dir(path: Union[str, Path]) -> Path:
        """确保目录存在

        Args:
            path: 目录路径

        Returns:
            Path对象
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"确保目录存在: {path}")
        return path

    @staticmethod
    def safe_remove(path: Union[str, Path]) -> bool:
        """安全删除文件或目录

        Args:
            path: 文件或目录路径

        Returns:
            是否删除成功
        """
        try:
            path = Path(path)
            if path.is_file():
                path.unlink()
                logger.info(f"删除文件: {path}")
            elif path.is_dir():
                shutil.rmtree(path)
                logger.info(f"删除目录: {path}")
            else:
                logger.warning(f"路径不存在: {path}")
                return False
            return True
        except Exception as e:
            logger.exception(f"删除失败 {path}: {e}")
            return False

    @staticmethod
    def copy_file(src: Union[str, Path], dst: Union[str, Path], overwrite: bool = False) -> bool:
        """复制文件

        Args:
            src: 源文件路径
            dst: 目标文件路径
            overwrite: 是否覆盖已存在的文件

        Returns:
            是否复制成功
        """
        try:
            src = Path(src)
            dst = Path(dst)

            if not src.exists():
                logger.error(f"源文件不存在: {src}")
                return False

            if dst.exists() and not overwrite:
                logger.warning(f"目标文件已存在且不允许覆盖: {dst}")
                return False

            # 确保目标目录存在
            FileManager.ensure_dir(dst.parent)

            shutil.copy2(src, dst)
            logger.info(f"复制文件: {src} -> {dst}")
            return True
        except Exception as e:
            logger.exception(f"复制文件失败: {e}")
            return False

    @staticmethod
    def move_file(src: Union[str, Path], dst: Union[str, Path]) -> bool:
        """移动文件

        Args:
            src: 源文件路径
            dst: 目标文件路径

        Returns:
            是否移动成功
        """
        try:
            src = Path(src)
            dst = Path(dst)

            if not src.exists():
                logger.error(f"源文件不存在: {src}")
                return False

            # 确保目标目录存在
            FileManager.ensure_dir(dst.parent)

            shutil.move(str(src), str(dst))
            logger.info(f"移动文件: {src} -> {dst}")
            return True
        except Exception as e:
            logger.exception(f"移动文件失败: {e}")
            return False

    @staticmethod
    def get_file_info(path: Union[str, Path]) -> Optional[dict[str, Any]]:
        """获取文件信息

        Args:
            path: 文件路径

        Returns:
            文件信息字典
        """
        try:
            path = Path(path)
            if not path.exists():
                return None

            stat = path.stat()
            return {
                "name": path.name,
                "path": str(path.absolute()),
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime),
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "is_file": path.is_file(),
                "is_dir": path.is_dir(),
                "extension": path.suffix.lower() if path.is_file() else None,
            }
        except Exception as e:
            logger.exception(f"获取文件信息失败 {path}: {e}")
            return None

    @staticmethod
    def list_files(directory: Union[str, Path], pattern: str = "*", recursive: bool = False) -> list[Path]:
        """列出目录中的文件

        Args:
            directory: 目录路径
            pattern: 文件模式
            recursive: 是否递归搜索

        Returns:
            文件路径列表
        """
        try:
            directory = Path(directory)
            if not directory.is_dir():
                logger.error(f"不是有效目录: {directory}")
                return []

            files = list(directory.rglob(pattern)) if recursive else list(directory.glob(pattern))

            # 只返回文件, 不包括目录
            files = [f for f in files if f.is_file()]
            logger.debug(f"找到 {len(files)} 个文件在 {directory}")
            return files
        except Exception as e:
            logger.exception(f"列出文件失败 {directory}: {e}")
            return []

    @staticmethod
    def get_file_size_human(size_bytes: int) -> str:
        """将字节大小转换为人类可读格式

        Args:
            size_bytes: 字节大小

        Returns:
            人类可读的大小字符串
        """
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"


class JsonFileHandler:
    """JSON文件处理器"""

    @staticmethod
    def read_json(file_path: Union[str, Path], encoding: str = "utf-8") -> Optional[Any]:
        """读取JSON文件

        Args:
            file_path: 文件路径
            encoding: 文件编码

        Returns:
            JSON数据
        """
        try:
            with open(file_path, encoding=encoding) as f:
                data = json.load(f)
            logger.debug(f"读取JSON文件: {file_path}")
            return data
        except Exception as e:
            logger.exception(f"读取JSON文件失败 {file_path}: {e}")
            return None

    @staticmethod
    def write_json(data: Any, file_path: Union[str, Path], encoding: str = "utf-8", indent: int = 2) -> bool:
        """写入JSON文件

        Args:
            data: 要写入的数据
            file_path: 文件路径
            encoding: 文件编码
            indent: 缩进空格数

        Returns:
            是否写入成功
        """
        try:
            file_path = Path(file_path)
            FileManager.ensure_dir(file_path.parent)

            with open(file_path, "w", encoding=encoding) as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
            logger.info(f"写入JSON文件: {file_path}")
            return True
        except Exception as e:
            logger.exception(f"写入JSON文件失败 {file_path}: {e}")
            return False


class CsvFileHandler:
    """CSV文件处理器"""

    @staticmethod
    def read_csv(file_path: Union[str, Path], encoding: str = "utf-8") -> Optional[list[dict[str, str]]]:
        """读取CSV文件

        Args:
            file_path: 文件路径
            encoding: 文件编码

        Returns:
            CSV数据列表
        """
        try:
            data = []
            with open(file_path, encoding=encoding, newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
            logger.debug(f"读取CSV文件: {file_path}, 行数: {len(data)}")
            return data
        except Exception as e:
            logger.exception(f"读取CSV文件失败 {file_path}: {e}")
            return None

    @staticmethod
    def write_csv(data: list[dict[str, Any]], file_path: Union[str, Path], encoding: str = "utf-8") -> bool:
        """写入CSV文件

        Args:
            data: 要写入的数据
            file_path: 文件路径
            encoding: 文件编码

        Returns:
            是否写入成功
        """
        try:
            if not data:
                logger.warning(f"没有数据要写入CSV文件: {file_path}")
                return False

            file_path = Path(file_path)
            FileManager.ensure_dir(file_path.parent)

            fieldnames = data[0].keys()
            with open(file_path, "w", encoding=encoding, newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            logger.info(f"写入CSV文件: {file_path}, 行数: {len(data)}")
            return True
        except Exception as e:
            logger.exception(f"写入CSV文件失败 {file_path}: {e}")
            return False


class TextFileHandler:
    """文本文件处理器"""

    @staticmethod
    def read_text(file_path: Union[str, Path], encoding: str = "utf-8") -> Optional[str]:
        """读取文本文件

        Args:
            file_path: 文件路径
            encoding: 文件编码

        Returns:
            文件内容
        """
        try:
            with open(file_path, encoding=encoding) as f:
                content = f.read()
            logger.debug(f"读取文本文件: {file_path}")
            return content
        except Exception as e:
            logger.exception(f"读取文本文件失败 {file_path}: {e}")
            return None

    @staticmethod
    def write_text(content: str, file_path: Union[str, Path], encoding: str = "utf-8") -> bool:
        """写入文本文件

        Args:
            content: 文件内容
            file_path: 文件路径
            encoding: 文件编码

        Returns:
            是否写入成功
        """
        try:
            file_path = Path(file_path)
            FileManager.ensure_dir(file_path.parent)

            with open(file_path, "w", encoding=encoding) as f:
                f.write(content)
            logger.info(f"写入文本文件: {file_path}")
            return True
        except Exception as e:
            logger.exception(f"写入文本文件失败 {file_path}: {e}")
            return False

    @staticmethod
    def read_lines(file_path: Union[str, Path], encoding: str = "utf-8") -> Optional[list[str]]:
        """按行读取文本文件

        Args:
            file_path: 文件路径
            encoding: 文件编码

        Returns:
            文件行列表
        """
        try:
            with open(file_path, encoding=encoding) as f:
                lines = f.readlines()
            # 去除行尾换行符
            lines = [line.rstrip("\n\r") for line in lines]
            logger.debug(f"读取文本文件行: {file_path}, 行数: {len(lines)}")
            return lines
        except Exception as e:
            logger.exception(f"读取文本文件行失败 {file_path}: {e}")
            return None

    @staticmethod
    def append_text(content: str, file_path: Union[str, Path], encoding: str = "utf-8") -> bool:
        """追加文本到文件

        Args:
            content: 要追加的内容
            file_path: 文件路径
            encoding: 文件编码

        Returns:
            是否追加成功
        """
        try:
            file_path = Path(file_path)
            FileManager.ensure_dir(file_path.parent)

            with open(file_path, "a", encoding=encoding) as f:
                f.write(content)
            logger.debug(f"追加文本到文件: {file_path}")
            return True
        except Exception as e:
            logger.exception(f"追加文本失败 {file_path}: {e}")
            return False


# 便捷函数
def ensure_dir(path: Union[str, Path]) -> Path:
    """确保目录存在"""
    return FileManager.ensure_dir(path)


def safe_remove(path: Union[str, Path]) -> bool:
    """安全删除文件或目录"""
    return FileManager.safe_remove(path)


def read_json(file_path: Union[str, Path]) -> Optional[Any]:
    """读取JSON文件"""
    return JsonFileHandler.read_json(file_path)


def write_json(data: Any, file_path: Union[str, Path]) -> bool:
    """写入JSON文件"""
    return JsonFileHandler.write_json(data, file_path)


def read_csv(file_path: Union[str, Path]) -> Optional[list[dict[str, str]]]:
    """读取CSV文件"""
    return CsvFileHandler.read_csv(file_path)


def write_csv(data: list[dict[str, Any]], file_path: Union[str, Path]) -> bool:
    """写入CSV文件"""
    return CsvFileHandler.write_csv(data, file_path)


def read_text(file_path: Union[str, Path]) -> Optional[str]:
    """读取文本文件"""
    return TextFileHandler.read_text(file_path)


def write_text(content: str, file_path: Union[str, Path]) -> bool:
    """写入文本文件"""
    return TextFileHandler.write_text(content, file_path)


# 导出的函数和类
__all__ = [
    "CsvFileHandler",
    "FileManager",
    "FileOperationError",
    "JsonFileHandler",
    "TextFileHandler",
    "ensure_dir",
    "read_csv",
    "read_json",
    "read_text",
    "safe_remove",
    "write_csv",
    "write_json",
    "write_text",
]
