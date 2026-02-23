"""
Pydantic SQLite Loader - 使用标准化表结构存储数据。

与 pydantic_loader 的区别：
- pydantic_loader: 使用 JSON 列存储数据
- pydantic_sqlite: 使用标准化表结构，每个类型对应专门的表

优势：
- 支持 SQL 查询字段
- 支持索引加速
- 支持外键约束
- 更好的数据完整性
"""

from .loader import PydanticSQLiteLoader
from .schema import TableSchema

__all__ = ["PydanticSQLiteLoader", "TableSchema"]
