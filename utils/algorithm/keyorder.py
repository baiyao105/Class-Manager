"""
键值排序类所在文件
"""

import copy
from abc import ABC
from typing import Iterable, List, TypeVar, Union, Dict, Iterator, Tuple, Optional
from collections import OrderedDict

try:
    from utils.logger import Logger
except ImportError:

    class Logger:
        "覆写用的日志记录类"

        def log(l, c, s):
            "记录日志"
            print(c)


__all__ = ["SupportsKeyOrdering", "OrderedKeyList"]


class SupportsKeyOrdering(ABC):
    # 注：Supports是支持的意思（
    # 还有，其实把鼠标悬浮在"SupportsKeyOrdering"上就可以看到这个注释了，经过美化了的
    """
    支持key排序的抽象类。

        意思就是说这个类有一个``key``属性，这个属性是``str``类型

        这个``SupportsKeyOrdering``是为了方便使用而设计的，因为很多类都需要一个``key``属性

        （比如``ScoreModifactionTemplate``的``key``就表示模板本身的标识符）

        只要这个类实现了``key``属性，那么就可以使用``OrderedKeyList``（后面有讲）来存储这个类

        （比如``OrderedKeyList[ScoreModificationTemplate]``）

        还有，只要继承这个类，然后自己写一下key的实现，就可以直接使用``OrderedKeyList``来存储这个类了

        就像这样：
        >>> class SomeClassThatSupportsKeyOrdering(SupportsKeyOrdering):
        ...     def __init__(self, key: str):
        ...         self.key = key      # 在一个OrderedKeyList里面每一个元素都有自己的key
        ...                             # 至于这个key表示的是什么就由你来决定了
        >>>                             # 但是但是，这个key只能是str，因为int拿来做索引值了，float和tuple(元组)之类的懒得写


        以前以来我们都用``collections.OrderedDict``来寻找模板，比如这样

        >>> DEFAULT_SCORE_TEMPLATES: OrderedDict[str, ScoreModificationTemplate] = OrderedDict([
        ...   "go_to_school_early": ScoreModificationTemplate(
        ...         "go_to_school_early", 1.0,  "7:20前到校", "早起的鸟儿有虫吃"),
        ...   "go_to_school_late": ScoreModificationTemplate(
        ...         "go_to_school_late", -1.0, "7:25后到校", "早起的虫儿被鸟吃"),
        ... ])
        >>> DEFAULT_SCORE_TEMPLATES["go_to_school_early"]
        ScoreModificationTemplate("go_to_school_early", 1.0,  "7:20前到校", "早起的鸟儿有虫吃")

        这样做的好处是我们可以直接通过key来获取模板，也可以通过模板反向找到它的key值

        但是缺点是如果``OrderedDict``中的key和``ScoreModification``中的key不一致就会出错

        现在我们可以用``OrderedKeyList``来存储模板这类"SupportsKeyOrdering"的对象，就不用写dict的key

        这样就不用担心dict中的key和模板中的不一样了

        >>> DEFAULT_SCORE_TEMPLATES = OrderedKeyList([
        ...   ScoreModificationTemplate("go_to_school_early", 1.0, "7:20前到校", "早起的鸟儿有虫吃"),
        ...   ScoreModificationTemplate("go_to_school_late", -1.0, "7:25后到校", "早起的虫儿被鸟吃"),
        ... ])   # 这就不需要写Key了，而且这个东西支持所有list的方法和部分dict的方法
        >>>      #（比如append，keys和items之类）
        >>> DEFAULT_SCORE_TEMPLATES[0]
        ScoreModificationTemplate("go_to_school_early", 1.0, "7:20前到校", "早起的鸟儿有虫吃")
        >>> DEFAULT_SCORE_TEMPLATES["go_to_school_early"]
        ScoreModificationTemplate("go_to_school_early", 1.0, "7:20前到校", "早起的鸟儿有虫吃")

        你学废了吗？
    """


_Template = TypeVar("_Template", bound=SupportsKeyOrdering)
"""
这东西不用管，写类型注释用的，方便理解

（可以理解为写在类型注释里的一个变量，绑定``SupportsKeyOrdering``的类，传进去什么类型就传出来什么类型）

如果你给一个``OrderedKeyList``初始值是``ScoreModificationTemplate``的列表，他就会自动识别为``OrderedKeyList[ScoreModificationTemplate]``

那么这个``OrderedKeyList``迭代或者取值的时候VSCode就会知道取出来的东西ScoreModificationTemplate，就方便查看它的属性和方法，肥肠方便

（但是对于写类型注释的人并不方便）
"""


class OrderedKeyList(list, Iterable[_Template]):
    """有序的key列表，可以用方括号来根据SupportsKeyOrdering对象的key，索引值或者对象本身来获取对象

    举个例子

    建立一个新的OrderedKeyList
    >>> template = ScoreModificationTemplate("go_to_school_late_more", -2.0, "7:30后到校", "哥们为什么不睡死在家里？")
    >>> # 这里有一个存在变量里面的模板，我们叫它template
    >>> DEFAULT_SCORE_TEMPLATES = OrderedKeyList([
    ...   ScoreModificationTemplate("go_to_school_early", 1.0, "7:20前到校", "早起的鸟儿有虫吃"),
    ...   ScoreModificationTemplate("go_to_school_late", -1.0, "7:25后到校", "早起的虫儿被鸟吃"),
    ...   template
    ... ])

    获取里面的元素
    >>> DEFAULT_SCORE_TEMPLATES[0]
    ScoreModificationTemplate("go_to_school_early", 1.0, "7:20前到校", "早起的鸟儿有虫吃")
    >>> DEFAULT_SCORE_TEMPLATES["go_to_school_early"]
    ScoreModificationTemplate("go_to_school_early", 1.0, "7:20前到校", "早起的鸟儿有虫吃")
    >>> DEFAULT_SCORE_TEMPLATES[template]
    ScoreModificationTemplate("go_to_school_late_more", -2.0, "7:30后到校", "哥们为什么不睡死在家里？")
    >>> DEFAULT_SCORE_TEMPLATES.keys()
    ["go_to_school_early", "go_to_school_late", "go_to_school_late"]
    >>> len(DEFAULT_SCORE_TEMPLATES)
    3

    添加元素
    >>> DEFAULT_SCORE_TEMPLATES.append(ScoreModificationTemplate("Chinese_class_good", 2.0,"语文课堂表扬","王の表扬"))
    >>> DEFAULT_SCORE_TEMPLATES.append(template) # 这里如果设置了不允许重复的话还往里面放同一个模板就会报错
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
        DEFAULT_SCORE_TEMPLATES.append(template)
      File "<stdin>", line 166, in append
        raise ValueError(F"模板的key（{getattr(v, self.keyattr)!r}）重复")
    ValueError: 模板的key（'go_to_school_late_more'）重复


    交换里面的元素顺序
    >>> DEFAULT_SCORE_TEMPLATES.swaps(0, 1)     # 交换索引0和1的元素，当然也可以填模板的key
    OrderedKeyList([
        ScoreModificationTemplate("go_to_school_late", -1.0, "7:25后到校", "早起的虫儿被鸟吃"),
        ScoreModificationTemplate("go_to_school_early", 1.0, "7:20前到校", "早起的鸟儿有虫吃"),
        ScoreModificationTemplate("go_to_school_late_more", -2.0, "7:30后到校", "哥们为什么不睡死在家里？")
    ])

    删掉/修改里面的元素
    >>> del DEFAULT_SCORE_TEMPLATES["go_to_school_early"]    # 删除key为"go_to_school_early"的元素
    >>> DEFAULT_SCORE_TEMPLATES.pop(0)                       # 删除索引为0的元素
    >>> len(DEFAULT_SCORE_TEMPLATES)                         # 查看长度（现在只剩一个7:30以后到校的了）
    1

    """

    allow_dumplicate = False
    "是否允许key重复"

    dumplicate_suffix = "_copy"
    "key重复时自动添加的后缀（如果允许放行重复的key进到列表里）"

    keyattr = "key"
    'SupportsKeyOrdering的这个"Key"的属性名'

    def __init__(
        self,
        objects: Union[
            Iterable[_Template],
            Dict[str, _Template],
            "OrderedDict[str, _Template]",
            "OrderedKeyList[_Template]",
        ],
    ):
        """初始化OrderedKeyList

        :param templates: 模板列表
        """

        super().__init__()
        if isinstance(objects, (dict, OrderedDict)):
            for k, v in objects.items():
                if getattr(v, self.keyattr) != k:
                    Logger.log(
                        "W",
                        f"模板在dict中的key（{k!r}）与模板本身的（{getattr(v, self.keyattr)!r}）不一致，"
                        "已自动修正为dict中的key",
                        "OrderedKeyList.__init__",
                    )
                    setattr(v, self.keyattr, k)
                self.append(v)
        elif isinstance(objects, OrderedKeyList):
            self.extend([t for t in objects])
        else:
            keys = []
            for v in objects:
                if getattr(v, self.keyattr) in keys:
                    if not self.allow_dumplicate:
                        raise ValueError(
                            f"模板的key（{getattr(v, self.keyattr)!r}）重复"
                        )
                    Logger.log(
                        "W",
                        f"模板的key（{getattr(v, self.keyattr)!r}）重复，"
                        f"补充为{getattr(v, self.keyattr)!r}{self.dumplicate_suffix}",
                        "OrderedKeyList.__init__",
                    )
                    setattr(
                        v,
                        self.keyattr,
                        getattr(v, self.keyattr) + self.dumplicate_suffix,
                    )
                keys.append(getattr(v, self.keyattr))
                self.append(v)

    def __getitem__(self, key: Union[int, str, _Template]) -> _Template:
        "返回指定索引或key的模板"
        if isinstance(key, int):
            return super().__getitem__(key)
        else:
            for obj in self:
                if getattr(obj, self.keyattr) == key:
                    return obj
            for obj in self:
                if obj is key:
                    return obj
            raise KeyError(f"列表中不存在key为{key!r}的模板")

    def __setitem__(self, key: Union[int, str, _Template], value: _Template):
        "设置指定索引或key的模板"
        if isinstance(key, int):
            super().__setitem__(key, value)
        else:
            for i, obj in enumerate(self):
                if getattr(obj, self.keyattr) == key:
                    super().__setitem__(i, value)
                    return
                elif obj is key:
                    super().__setitem__(i, value)
            if (
                getattr(value, self.keyattr) == key
                and isinstance(value, SupportsKeyOrdering)
                and isinstance(key, str)
            ):
                self.append(
                    value
                )  # 如果key是字符串，并且value是模板，则直接添加到列表中
            else:
                raise KeyError(f"列表中不存在key为{key!r}的模板")

    def __delitem__(self, key: Union[int, str]):
        "删除指定索引或key的模板"
        if isinstance(key, int):
            super().__delitem__(key)
        else:
            for i, obj in enumerate(self):
                if getattr(obj, self.keyattr) == key:
                    super().__delitem__(i)
                    return
            raise KeyError(f"列表中不存在key为{key!r}的模板")

    def __len__(self) -> int:
        "返回列表中模板的数量"
        return super().__len__()

    def __reversed__(self) -> Iterator[_Template]:
        "返回列表的反向迭代器"
        return super().__reversed__()

    def __contains__(self, item: _Template) -> bool:
        "判断列表中是否包含指定模板"
        return (
            super().__contains__(item)
            or [getattr(obj, self.keyattr) for obj in self].count(item) > 0
        )

    def swaps(self, lh: Union[int, str], rh: Union[int, str]):
        "交换指定索引或key的模板"
        if isinstance(lh, str):
            for i, obj in enumerate(self):
                if getattr(obj, self.keyattr) == lh:
                    lh = i
                    break
            else:
                raise KeyError(f"列表中不存在key为{lh!r}的模板")
        if isinstance(rh, str):
            for i, obj in enumerate(self):
                if getattr(obj, self.keyattr) == rh:
                    lh = i
                    break
            else:
                raise KeyError(f"列表中不存在key为{rh!r}的模板")
        self[lh], self[rh] = self[rh], self[lh]
        return self

    def __iter__(self) -> Iterator[_Template]:
        "返回列表的迭代器"
        return super().__iter__()

    def append(self, obj: _Template):
        "添加到列表"
        if getattr(obj, self.keyattr) in self.keys():
            if not self.allow_dumplicate:  # 如果不允许重复直接抛出异常
                raise ValueError(f"模板的key（{getattr(obj, self.keyattr)!r}）重复")
            print(
                "W",
                f"模板的key（{getattr(obj, self.keyattr)!r}）重复，"
                f"补充为{getattr(obj, self.keyattr)!r}{self.dumplicate_suffix}",
                "OrderedKeyList.append",
            )
            setattr(
                obj, self.keyattr, getattr(obj, self.keyattr) + self.dumplicate_suffix
            )
        super().append(obj)
        return self

    def extend(self, templates: Iterable[_Template]):
        "扩展列表"
        for template in templates:
            self.append(template)
        return self

    def keys(self) -> List[str]:
        "返回列表中所有元素的key"
        return [getattr(obj, self.keyattr) for obj in self]

    def values(self) -> List[_Template]:
        "返回列表中所有模板"
        return [obj for obj in self]

    def items(self) -> List[Tuple[str, _Template]]:
        "返回列表中所有模板的key和模板"
        return [(getattr(obj, self.keyattr), obj) for obj in self]

    def __copy__(self) -> "OrderedKeyList[_Template]":
        "返回列表的浅拷贝"
        return OrderedKeyList(self)

    def __deepcopy__(self, memo: Optional[dict]) -> "OrderedKeyList[_Template]":
        "返回列表的深拷贝"
        return OrderedKeyList([copy.deepcopy(obj, memo) for obj in self])

    def copy(self) -> "OrderedKeyList[_Template]":
        "返回列表的拷贝"
        return self.__copy__()

    def to_dict(self) -> Dict[str, _Template]:
        "返回列表的字典表示"
        return dict(self.items())

    def __repr__(self) -> str:
        "返回列表的表达式"
        return f"OrderedKeyList({super().__repr__()})"
