
import sys
from control import ClassWindowModel
from utils import QApplication, DEFAULT_CLASS_KEY, Base
from utils.classobjects.dataloaders import set_loader_type

set_loader_type("pydantic")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    model = ClassWindowModel(app, "pydantic_test", "测试班级", DEFAULT_CLASS_KEY)
    model.mainloop()
    Base.log("I", "程序结束", "MainThread")
