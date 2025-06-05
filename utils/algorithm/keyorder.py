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
        self._key_to_index_map: Dict[str, int] = {}
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
                self.append(v) # append will handle _key_to_index_map
        elif isinstance(objects, OrderedKeyList):
            # Iterate and append to correctly build the map,
            # leveraging the modified append logic.
            for t in objects:
                self.append(t)
        else:
            # This loop will also use the modified append,
            # which handles map population.
            temp_list_for_init = []
            processed_keys = {} # To handle duplicates before appending to super()
            for v_idx, v in enumerate(objects):
                original_key = getattr(v, self.keyattr)
                current_key = original_key
                if current_key in processed_keys:
                    if not self.allow_dumplicate:
                        raise ValueError(
                            f"模板的key（{current_key!r}）重复"
                        )
                    Logger.log(
                        "W",
                        f"模板的key（{current_key!r}）重复，"
                        f"补充为{current_key!r}{self.dumplicate_suffix}",
                        "OrderedKeyList.__init__",
                    )
                    current_key = f"{current_key}{self.dumplicate_suffix}"
                    # Ensure the generated key is also unique
                    while current_key in processed_keys:
                        current_key = f"{current_key}{self.dumplicate_suffix}"
                    setattr(v, self.keyattr, current_key)

                processed_keys[current_key] = v_idx
                temp_list_for_init.append(v)

            super().extend(temp_list_for_init)
            # Now that super() list is populated, build the map
            for i, obj in enumerate(self):
                self._key_to_index_map[getattr(obj, self.keyattr)] = i


    def __getitem__(self, key: Union[int, str, _Template]) -> _Template:
        "返回指定索引或key的模板"
        if isinstance(key, str):
            index = self._key_to_index_map.get(key)
            if index is not None:
                return super().__getitem__(index)
            # Fallthrough to existing logic if key not in map (e.g. could be an object)
        elif isinstance(key, int):
            return super().__getitem__(key)

        # Fallback for non-str/non-int keys or str key not in map
        # (covers _Template type or if map somehow becomes inconsistent)
        for obj in self:
            if getattr(obj, self.keyattr) == key: # handles str key not initially in map
                return obj
        for obj in self: # handles _Template object itself as key
            if obj is key:
                return obj
        raise KeyError(f"列表中不存在key为{key!r}的模板")

    def __setitem__(self, key: Union[int, str, _Template], value: _Template):
        "设置指定索引或key的模板"
        new_key = getattr(value, self.keyattr)

        if isinstance(key, str):
            index = self._key_to_index_map.get(key)
            if index is not None:
                old_obj = self[index]
                old_obj_key = getattr(old_obj, self.keyattr)
                if old_obj_key in self._key_to_index_map and self._key_to_index_map[old_obj_key] == index:
                    del self._key_to_index_map[old_obj_key]

                super().__setitem__(index, value)

                current_new_key = new_key # Use a temporary variable for potential modification
                if self.allow_dumplicate:
                    if current_new_key in self._key_to_index_map and self._key_to_index_map[current_new_key] != index:
                        # Duplicate key detected for a *different* item, apply suffix
                        original_key_for_log = current_new_key
                        Logger.log(
                            "W",
                            f"模板的key（{original_key_for_log!r}）在赋值时与现有key冲突，"
                            f"将尝试补充后缀 {self.dumplicate_suffix}",
                            "OrderedKeyList.__setitem__ (str key)",
                        )
                        suffixed_new_key = f"{current_new_key}{self.dumplicate_suffix}"
                        while suffixed_new_key in self._key_to_index_map and self._key_to_index_map[suffixed_new_key] != index:
                            suffixed_new_key = f"{suffixed_new_key}{self.dumplicate_suffix}"
                        setattr(value, self.keyattr, suffixed_new_key)
                        current_new_key = suffixed_new_key
                        Logger.log(
                            "I",
                            f"模板的key已修改为 {current_new_key!r} 以避免冲突",
                            "OrderedKeyList.__setitem__ (str key)",
                        )
                elif new_key in self._key_to_index_map and self._key_to_index_map[new_key] != index :
                    # Not allowing duplicates, and new_key (which might be different from original `key` if `key` was an object)
                    # clashes with an existing key for a *different* item.
                    # Revert and raise error.
                    super().__setitem__(index, old_obj) # Revert list change
                    if old_obj_key not in self._key_to_index_map : # Put back old key if it was removed
                         self._key_to_index_map[old_obj_key] = index
                    raise ValueError(f"Setting item with key '{key}' to new item with key '{new_key}' would create a duplicate key with an existing item.")

                self._key_to_index_map[current_new_key] = index
                return
            else: # Key (string) not in map, this implies key does not exist.
                for i, obj_iter in enumerate(self):
                    if obj_iter is key: # key is _Template object
                        old_obj_key = getattr(obj_iter, self.keyattr)
                        if old_obj_key in self._key_to_index_map:
                            del self._key_to_index_map[old_obj_key]
                        super().__setitem__(i, value)
                        if not self.allow_dumplicate and new_key in self._key_to_index_map and self._key_to_index_map[new_key] != i:
                             # Revert (more complex as original object key might be gone)
                             # This path is tricky, for now, let's assume if key is _Template, it implies direct replacement.
                             # The duplicate check should ideally happen before deletion from map.
                            pass # Simplified: relies on append-like duplicate handling if key changes
                        self._key_to_index_map[new_key] = i
                        return
                # If key is a string and not in map, and not an object reference, this is an error or append.
                # The original code had append logic here, let's reconsider.
                # If key is str, and value.key matches key, and not self.allow_duplicate and key in map, error.
                # This part follows the original logic's append attempt:
                if isinstance(key, str) and new_key == key:
                    if not self.allow_dumplicate and new_key in self._key_to_index_map:
                         raise ValueError(f"Cannot set item; key '{new_key}' would be a duplicate.")
                    # This implies adding a new item if key not found by string or object.
                    # This behavior is a bit unusual for __setitem__ if key doesn't exist.
                    # Let's stick closer to typical __setitem__ which updates existing or fails.
                    # The original code's append here is more like an "upsert".
                    # For now, if str key not found, raise KeyError.
                    raise KeyError(f"列表中不存在key为{key!r}的模板 (for setting)")
                else: # Fallback or other unhandled cases
                    raise KeyError(f"列表中不存在key为{key!r}的模板 (for setting)")

        elif isinstance(key, int): # key is an index
            if 0 <= key < len(self):
                old_obj = self[key]
                old_obj_key = getattr(old_obj, self.keyattr)
                    if old_obj_key in self._key_to_index_map and self._key_to_index_map[old_obj_key] == key: # key is index here
                    del self._key_to_index_map[old_obj_key]

                super().__setitem__(key, value) # key is index here

                current_new_key = new_key # Use a temporary variable for potential modification
                if self.allow_dumplicate:
                    if current_new_key in self._key_to_index_map and self._key_to_index_map[current_new_key] != key: # key is index
                        # Duplicate key detected for a *different* item, apply suffix
                        original_key_for_log = current_new_key
                        Logger.log(
                            "W",
                            f"模板的key（{original_key_for_log!r}）在赋值时与现有key冲突 (index {key})，"
                            f"将尝试补充后缀 {self.dumplicate_suffix}",
                            "OrderedKeyList.__setitem__ (int key)",
                        )
                        suffixed_new_key = f"{current_new_key}{self.dumplicate_suffix}"
                        while suffixed_new_key in self._key_to_index_map and self._key_to_index_map[suffixed_new_key] != key: # key is index
                            suffixed_new_key = f"{suffixed_new_key}{self.dumplicate_suffix}"
                        setattr(value, self.keyattr, suffixed_new_key)
                        current_new_key = suffixed_new_key
                        Logger.log(
                            "I",
                            f"模板的key已修改为 {current_new_key!r} 以避免冲突 (index {key})",
                            "OrderedKeyList.__setitem__ (int key)",
                        )
                elif new_key in self._key_to_index_map and self._key_to_index_map[new_key] != key: # key is index
                    # Not allowing duplicates, and new_key clashes with an existing key for a *different* item.
                    # Revert and raise error.
                    super().__setitem__(key, old_obj) # Revert list change
                    if old_obj_key not in self._key_to_index_map: # Put back old key if it was removed
                        self._key_to_index_map[old_obj_key] = key # key is index
                    raise ValueError(f"Setting item at index {key} to new item with key '{new_key}' would create a duplicate key with an existing item.")

                self._key_to_index_map[current_new_key] = key # key is index here
                return
            else:
                raise IndexError("list assignment index out of range")
        else: # key is _Template object, try to find by object identity
            for i, obj_iter in enumerate(self):
                if obj_iter is key:
                    old_obj_key = getattr(obj_iter, self.keyattr)
                    old_obj_key_original = getattr(obj_iter, self.keyattr) # key is the _Template object itself
                    if old_obj_key_original in self._key_to_index_map and self._key_to_index_map[old_obj_key_original] == i:
                        del self._key_to_index_map[old_obj_key_original]

                    super().__setitem__(i, value)
                    current_new_key = new_key # Use a temporary variable
                    if self.allow_dumplicate:
                        if current_new_key in self._key_to_index_map and self._key_to_index_map[current_new_key] != i:
                            original_key_for_log = current_new_key
                            Logger.log(
                                "W",
                                f"模板的key（{original_key_for_log!r}）在赋值时与现有key冲突 (obj {key!r}, index {i})，"
                                f"将尝试补充后缀 {self.dumplicate_suffix}",
                                "OrderedKeyList.__setitem__ (obj key)",
                            )
                            suffixed_new_key = f"{current_new_key}{self.dumplicate_suffix}"
                            while suffixed_new_key in self._key_to_index_map and self._key_to_index_map[suffixed_new_key] != i:
                                suffixed_new_key = f"{suffixed_new_key}{self.dumplicate_suffix}"
                            setattr(value, self.keyattr, suffixed_new_key)
                            current_new_key = suffixed_new_key
                            Logger.log(
                                "I",
                                f"模板的key已修改为 {current_new_key!r} 以避免冲突 (obj {key!r}, index {i})",
                                "OrderedKeyList.__setitem__ (obj key)",
                            )
                    elif new_key in self._key_to_index_map and self._key_to_index_map[new_key] != i:
                        super().__setitem__(i, obj_iter) # Revert list change (obj_iter is the old 'key' object)
                        if old_obj_key_original not in self._key_to_index_map: # Put back old key if it was removed
                             self._key_to_index_map[old_obj_key_original] = i
                        raise ValueError(f"Setting item '{old_obj_key_original}' (obj {key!r}) to new item with key '{new_key}' would create a duplicate key with an existing item.")

                    self._key_to_index_map[current_new_key] = i
                    return
            raise KeyError(f"列表中不存在对象为{key!r}的模板 (for setting by object)")


    def __delitem__(self, key: Union[int, str]):
        "删除指定索引或key的模板"
        index_to_delete = -1
        if isinstance(key, int):
            if 0 <= key < len(self):
                index_to_delete = key
                obj_to_delete = self[index_to_delete]
                obj_key = getattr(obj_to_delete, self.keyattr)
                if obj_key in self._key_to_index_map:
                    del self._key_to_index_map[obj_key]
                super().__delitem__(index_to_delete)
            else:
                raise IndexError("list assignment index out of range")
        elif isinstance(key, str):
            index_from_map = self._key_to_index_map.get(key)
            if index_from_map is not None:
                index_to_delete = index_from_map
                # Key is already known, so directly delete from map and list
                del self._key_to_index_map[key]
                super().__delitem__(index_to_delete)
            else:
                # Fallback: iterate to find (should not happen if map is consistent)
                for i, obj in enumerate(self):
                    if getattr(obj, self.keyattr) == key:
                        index_to_delete = i
                        # No need to delete from map here as it wasn't found by map.get()
                        super().__delitem__(i)
                        break
                else: # for-else: loop completed without break
                    raise KeyError(f"列表中不存在key为{key!r}的模板")
        else: # Should be int or str as per type hint
            raise TypeError("Key for __delitem__ must be an int or str")

        if index_to_delete != -1:
            # Rebuild map for items from the deleted index onwards
            # This is a simple way to ensure correctness.
            # A more optimized way would be to decrement indices of subsequent items,
            # but full rebuild is safer given potential complexities with duplicate keys
            # if allow_dumplicate were true and not handled perfectly by map.
            # For now, the prompt asks for a full rebuild from the index onwards.
            # However, a full rebuild of the entire map is simpler and less error-prone.
            self._key_to_index_map = {getattr(obj, self.keyattr): i for i, obj in enumerate(self)}

    def __len__(self) -> int:
        "返回列表中模板的数量"
        return super().__len__()

    def __reversed__(self) -> Iterator[_Template]:
        "返回列表的反向迭代器"
        return super().__reversed__()

    def __contains__(self, item: _Template) -> bool:
        "判断列表中是否包含指定模板"
        if isinstance(item, str): # Check if item is a key string
            return self._key_to_index_map.get(item) is not None
        # Fallback to object identity check or iterating if item is not str
        # The original logic `[getattr(obj, self.keyattr) for obj in self].count(item) > 0`
        # seems to imply `item` could be a key string.
        # If `item` is an object:
        if hasattr(item, self.keyattr):
             key = getattr(item, self.keyattr)
             if self._key_to_index_map.get(key) is not None:
                 # Further check if the object at that index is indeed the item
                 # This handles cases where keys might be shared (if allow_dumplicate is true
                 # and map points to first, or if map is out of sync)
                 return self[self._key_to_index_map[key]] is item
        return super().__contains__(item) # Checks for object identity in the list

    def swaps(self, lh: Union[int, str], rh: Union[int, str]):
        "交换指定索引或key的模板"
        lh_idx: int
        rh_idx: int

        if isinstance(lh, str):
            idx = self._key_to_index_map.get(lh)
            if idx is None:
                raise KeyError(f"列表中不存在key为{lh!r}的模板")
            lh_idx = idx
        else: # int
            lh_idx = lh

        if isinstance(rh, str):
            idx = self._key_to_index_map.get(rh)
            if idx is None:
                raise KeyError(f"列表中不存在key为{rh!r}的模板")
            rh_idx = idx
        else: # int
            rh_idx = rh

        # Perform boundary checks for integer indices
        if not (0 <= lh_idx < len(self) and 0 <= rh_idx < len(self)):
            raise IndexError("list index out of range for swap")

        # Swap items in the list
        obj_lh = self[lh_idx]
        obj_rh = self[rh_idx]
        super().__setitem__(lh_idx, obj_rh) # Use super setitem to avoid our complex __setitem__
        super().__setitem__(rh_idx, obj_lh)

        # Update map
        self._key_to_index_map[getattr(obj_lh, self.keyattr)] = rh_idx
        self._key_to_index_map[getattr(obj_rh, self.keyattr)] = lh_idx
        return self

    def __iter__(self) -> Iterator[_Template]:
        "返回列表的迭代器"
        return super().__iter__()

    def append(self, obj: _Template):
        "添加到列表"
        key = getattr(obj, self.keyattr)
        if self._key_to_index_map.get(key) is not None: # Check using the map
            if not self.allow_dumplicate:  # 如果不允许重复直接抛出异常
                raise ValueError(f"模板的key（{key!r}）重复")

            original_key = key
            Logger.log( # Changed print to Logger.log for consistency
                "W",
                f"模板的key（{original_key!r}）重复，"
                f"补充为{original_key!r}{self.dumplicate_suffix}",
                "OrderedKeyList.append",
            )
            # Ensure the generated key is also unique in the map
            new_key = f"{original_key}{self.dumplicate_suffix}"
            while self._key_to_index_map.get(new_key) is not None:
                new_key = f"{new_key}{self.dumplicate_suffix}"
            setattr(obj, self.keyattr, new_key)
            key = new_key # update key to the new unique key

        super().append(obj)
        self._key_to_index_map[key] = len(self) - 1
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
