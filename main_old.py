
import sys
from control import ClassWindowModel
from utils import QApplication, login, DEFAULT_CLASS_KEY, Base


if __name__ == "__main__":
    app = QApplication(sys.argv)
    model = ClassWindowModel(app, login(), "测试班级", DEFAULT_CLASS_KEY)
    model.mainloop()
    Base.log("I", "程序结束", "MainThread")
