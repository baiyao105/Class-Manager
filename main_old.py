import sys
from control.classwindow import *
from utils import *
from utils.classobjects.dataloaders import set_loader_type

mode = "legacy"

set_loader_type(mode)

if __name__ == "__main__":
    os.environ["QT_OPENGL"] = "angle"
    format = QSurfaceFormat()
    format.setVersion(3, 3)  # 使用 OpenGL 3.3
    format.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
    format.setRenderableType(QSurfaceFormat.RenderableType.OpenGL)
    format.setDepthBufferSize(24)
    QSurfaceFormat.setDefaultFormat(format)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseDesktopOpenGL, True)
    app = QApplication(sys.argv)
    widget = ClassWindowModel(app, f"{mode}_legacy", "测试班级", DEFAULT_CLASS_KEY)
    widget.show()
    app.exec()

    
