"""
和分数模板相关的模型。
"""

from __future__ import annotations

import time

from utils.basetypes import Base
from utils.functions.qtutils import wait_till_close, wait_until
from utils.classobjects import ScoreModificationTemplate

from widgets import ListView, NewTemplateWidget, EditTemplateWidget

from widgets.custom.ListView import ListViewItemDataType

from .class_ui_model import MixinSuperType


class TemplateManageModel(MixinSuperType):
    """
    和分数模板相关的模型。
    """
    
    def __init__(
        self, 
        current_user: str, 
        class_name: str, 
        class_key: str, 
        save_path: str | None = None
    ):
        Base.log("D", "初始化TemplateManageModel", "TemplateManageModel.__init__")

        self.template_listbox: ListView | None = None
        "模板列表框"
        self.manage_template_cursel_index: int | None = None
        "管理模板时选中的索引"
        self.new_template_window: NewTemplateWidget | None = None
        "新建模板窗口"
        self.edit_template_window: EditTemplateWidget | None = None
        "编辑模板窗口"

    def new_template(self):
        """
        打开新建模板的窗口。
        """
        self.new_template_window = NewTemplateWidget(self, self)
        self.new_template_window.show()

    def manage_templates(self):
        """
        打开管理模板的窗口。
        """
        self.template_listbox = ListView("管理模板", self)
        self.manage_template_cursel_index = 0

        def _generate_new_template_data():
            data: list[ListViewItemDataType] = []
            Base.log("I", "正在生成模板列表", "TemplateManageModel.manage_template")

            for index, template in enumerate(self.modify_templates.values()):
                
                def _edit_template(template: ScoreModificationTemplate = template, index: int = index):
                    self.edit_template(template, index)
                    wait_until(lambda: self.new_template_window is not None)
                    assert self.new_template_window is not None, "过类型检查"
                    wait_till_close(self.new_template_window)
                    assert self.template_listbox is not None, "也是过类型检查"
                    self.template_listbox.setData(_generate_new_template_data())

                data.append((template.title, lambda: _edit_template()))

            return data

        def _swap_template(index1: int, index2: int):
            Base.log("I", f"正在交换模板 {index1} 和 {index2}", "TemplateManageModel.manage_template")
            self.modify_templates.swaps(index1, index2)

        def _move_up(index: int):
            assert self.template_listbox is not None, "过类型检查"
            if index == -1 or index == 0:
                return
            Base.log("I", f"正在上移模板 {index}", "TemplateManageModel.manage_template")
            if index > 0:
                _swap_template(index, index - 1)
                self.template_listbox.setData(_generate_new_template_data())
                self.manage_template_cursel_index = max(index - 1, 0)

        def _move_down(index: int):
            assert self.template_listbox is not None, "过类型检查"
            if index == -1 or index == len(self.modify_templates) - 1:
                return
            Base.log("I", f"正在下移模板 {index}", "TemplateManageModel.manage_template")
            if index < len(self.modify_templates) - 1:
                _swap_template(index, index + 1)
                self.template_listbox.setData(_generate_new_template_data())
                self.manage_template_cursel_index = min(
                    index + 1, len(self.modify_templates) - 1
                )

        def move_up():
            assert self.template_listbox is not None, "过类型检查"
            _move_up(self.template_listbox.listWidget.currentRow())
            self.template_listbox.setData(_generate_new_template_data())
            self.template_listbox.listWidget.setCurrentRow(
                self.manage_template_cursel_index or 0
            )
            

        def move_down():
            assert self.template_listbox is not None, "过类型检查"
            _move_down(self.template_listbox.listWidget.currentRow())
            self.template_listbox.setData(_generate_new_template_data())
            self.template_listbox.listWidget.setCurrentRow(
                self.manage_template_cursel_index or 0
            )


        def new_template():
            assert self.template_listbox is not None, "过类型检查"
            assert self.new_template_window is not None, "也是过类型检查"
            self.new_template()
            wait_till_close(self.new_template_window)
            if self.template_listbox.listWidget.count() < len(self.modify_templates):
                self.template_listbox.setData(_generate_new_template_data())


        def delete_template():
            assert self.template_listbox is not None, "过类型检查"
            assert self.new_template_window is not None, "也是过类型检查"

            def _confirm_delete():
                assert self.template_listbox is not None, "过类型检查"
                assert self.new_template_window is not None, "也是过类型检查"
                self.del_template(
                    list(self.modify_templates.keys())[
                        self.template_listbox.listWidget.currentRow()
                    ],
                    "模板列表快捷删除",
                )
                time.sleep(0.2)
                self.template_listbox.setData(_generate_new_template_data())


            if self.template_listbox.listWidget.currentRow() != -1:
                self.question_if_exec(
                    "警告",
                    f"确定删除模板 "
                    f"{repr(list(self.modify_templates.values())[self.template_listbox.listWidget.currentRow()].title)} 吗？"
                    "\n删除后，它将会被移除出模板列表且无法恢复，\n但不会影响已经添加到列表中的项目。",
                    _confirm_delete,
               )
                        
        def reset_missing():
            assert self.template_listbox is not None, "过类型检查"
            assert self.new_template_window is not None, "也是过类型检查"
            def _confirm_restore():
                assert self.template_listbox is not None, "还是过类型检查"
                self.reset_missing_defaults()
                self.template_listbox.setData(_generate_new_template_data())

            self.question_if_exec(
                "提示",
                "是否将默认模板补充到模板列表中？\n"
                "这个操作会同时将默认成就，小组和班级补全，但是不会覆盖现有的数据。\n"
                "（补充完了记得翻到底下看看！）",
                _confirm_restore,
            )

        def reset_all_defaults():
            assert self.template_listbox is not None, "过类型检查"
            def _confirm_reset():
                assert self.template_listbox is not None, "过类型检查"
                self.reset_all_defaults()
                self.template_listbox.setData(_generate_new_template_data())
            self.question_if_exec(
                "警告",
                "是否复原所有默认模板？\n"
                "这个操作会覆盖现有的默认模板，当前已有的修改将会丢失。",
                _confirm_reset,
            )

        def reset_all_data():
            assert self.template_listbox is not None, "过类型检查"
            def _confirm_reset():
                assert self.template_listbox is not None, "过类型检查"
                self.reset_all_data()
                self.template_listbox.setData(_generate_new_template_data())
            self.question_if_exec(
                "警告",
                "是否复原所有模板？\n"
                "这个操作会重置现有的所有模板，新建的将会删除，修改将会丢失。",
                _confirm_reset,
            )

        self.template_listbox.setData(_generate_new_template_data())
        self.template_listbox.setCommands(
            [
                ("项目上移", move_up),
                ("项目下移", move_down),
                ("新建模板", new_template),
                ("删除模板", delete_template),
                ("补充默认", reset_missing),
                ("复原默认", reset_all_defaults),
                ("复原所有", reset_all_data)
            ]
        )

        self.template_listbox.show()

    def edit_template(self, template: ScoreModificationTemplate, index: int):
        """
        打开编辑模板的窗口。

        :param template: 模板对象
        """
        self.edit_template_window = EditTemplateWidget(
            self, template, self.template_listbox, index, self
        )
        self.edit_template_window.show()