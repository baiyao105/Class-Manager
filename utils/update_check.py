from typing import Literal, Union, Dict
import requests
import json
import os
import signal
import zipfile
import shutil
from utils.basetypes import stderr_orig, stdout_orig
import sys


sys.stdout = stdout_orig
sys.stderr = stderr_orig


TOKEN = "9bde0e6b1c0fca0ff36408665fb75306"

AUTHOR = "JustNothing_1021"

REPO_NAME = "ClassManager"

MASTER = "master"

DOWNLOAD_URL = "https://gitee.com/api/v5/repos/{}/{}/zipball?access_token={}&ref={}".format(AUTHOR, REPO_NAME, TOKEN, MASTER)

CLIENT_UPDATE_LOG = {
    10414: """
1.4.14（2025/3/15）更新日志：
更新内容：
 - 主界面翻新

优化内容：
 - 优化了代码逻辑
 - 优化了日志的显示和存储
 - 优化了动态背景不存在时的判断
 - 优化了登录窗口对上次登录用户名的记忆
 - 优化了每次启动时pygame和qfluentwidget的提示（限发行版）

修复内容：
 - 修复了一堆乱七八糟的东西，我也不记得了
...等11个bug
 """,
    10411: """

1.4.11（2025/2/11）更新日志：
更新内容：
 - 例行维护

优化内容：
 - 优化了弹窗的图标（基本跟没优化一样）
 - 微量优化了程序稳定性

修复内容：
 - 修复了更新释放文件失败的问题
 - 修复了考勤记录界面打不开的问题
 - 修复了编译脚本出现诡异错误的问题
 - 修复了没填写作业规则显示异常的问题
 - 修复了考勤记录页面切换状态问题重叠的问题
...等6个bug

但是话说回来，我是不是几百年没写更新日志了

""",
    10212: """
1.2.12（2024/12/20）更新日志：
更新内容：
 - 例行维护

优化内容：
 - 小组菜单内给每一位成员的分数绘制条形图

修复内容：
 - ListView反复打开模板管理窗口程序崩溃的问题
 - 程序处理大量（？）数据时窗口卡住的问题
 - 程序启动时有一段时间窗口不更新的问题
... 等12个bug

（说实话这么多bug我都是一天修完的）

""",
    10204: """
1.2.4（2024/12/2）更新日志：
更新内容：
 - 例行维护

优化内容：
 - 暂无

修复内容：
 - 把之前1.2.1丢掉的一大段代码补回来了
""",

    10203: """
1.2.3（2024/12/2）更新日志：
更新内容：
 - 例行维护

优化内容：
 - 暂无

修复内容：
 - 修复成就\"摧枯拉朽\"报诡异错误的问题
 - 修复了更新时base.py未替换的问题
 - 修复日志着色问题
""",
    10202: """
1.2.2（2024/12/1）更新日志：

更新内容：
 - 更新了12个成就

优化内容：
 - 优化了日志重定向，现在日志会有着色
 - 优化了代码逻辑

修复内容
 - 一堆小bug
""",
    10201: """
1.2.1（2024/11/27）更新日志：

更新内容：
 - 暂无

优化内容：
 - 优化了ListView侧边的按钮命令执行方式的逻辑
 - 优化了程序爆炸的错误显示
 
修复内容：
 - 修复了学生分数折线图打不开的问题
 - 修复了侧边栏按钮抽风的问题

 - 修复了其他的技术性问题
""",
    10200: """
1.2.0（2024/12/26） 更新日志：

更新内容：
 - 模板管理翻新（增加排序，快捷编辑和删除）

优化内容：
 - ListView的动画和事件处理
 - 代码逻辑
 
修复内容：
 - 暂无
""",

    10119: """
1.1.19（2024/11/25） 更新日志：

更新内容：
 - 例行维护

优化内容：
 - 优化了核心结构

修复内容：
 - 暂无
""",

    10118: """
1.1.18（2024/11/25） 更新日志：

更新内容：
 - 例行维护

优化内容：
 - 暂无

修复内容：
 - 修复了学生分数折线图打不开的问题
""",

    10117: """
1.1.17（2024/11/24） 更新日志：

更新内容：
 - 按照班主任所说简化了我们的程序（代码结构上？）
 - 没有主要的大更新（你们记得告诉我要改什么）
 
优化内容：
 - 优化了按钮闪烁的动画（不过好像变得更卡了？？？）
 - 优化了学生分数折线图的绘制（用新模块）
 - 也是很日常的优化代码逻辑
 - 优化了学生名次列表的着色
 - 优化了paintEvent的处理
 - 优化了我的脑子
 
修复内容：
 - 修复了加载还原点窗口卡死的问题（因为现在还是会卡）
 - 修复了侧边栏通知过多时窗口动画卡住的问题
 - 修复了保存数据时时间过长窗口卡住的问题
 - 修复了自动更新连接超时窗口卡住的问题
 - 修复了反复开关折线图程序爆炸的问题
 - 修复了我自己还活着的bug

修了一堆bug，你就说是不是大更新吧
 """,

    10116: """
1.1.16 （2024/11/23） 更新日志：

更新内容：
 - 自动更新的错误显示
 - 夹带了部分私货

优化内容：
 - 优化了动画的算法
 - 优化了更新策略

修复内容：
 - 修复了作业结算动画卡住的问题
 - 修复了自动更新容易爆炸的bug
 - 修复了其他的小bug

周末会大更新！
对了，你猜猜私货指的是什么""",

    10115: """
1.1.15 （2024/11/22） 更新日志：

更新内容：
 - 没有大更新
 - 没有大更新

优化内容：
 - 在历史记录中会按照点评的分数对项目进行着色
 - 升级的方式（修改了升级用的脚本）
 - 优化了代码逻辑（这不废话么
 
修复内容：
 - 没有修复什么bug
 - 新增了114514个bug""",

    10114: """
1.1.14 （2024/11/21） 更新日志：

更新内容：
 - 增加了自动更新功能，以后再也不需要我把硬盘带到学校了
 - 增加了检测更新功能，位于顶边栏-更多
 - 增加了更新日志，位于顶边栏-更多

优化内容：
  - 优化了paintEvent的处理，动态背景应该会好点
  - 再次再次优化了所有动画的算法
  - 优化了代码逻辑

修复内容：
 - 修复了主界面学生按钮不能闪烁的问题
 - 修复了我还活着的bug


""",
    

    10113: """
1.1.13（2024/11/18） 更新日志：

更新内容：
 - 作业结算功能自定义模板，位于作业结算-自定义模板

优化内容：
 - 优化了动态背景的逻辑（drawPixmap->label.update）
 - 优化了学生分数折线图的绘制
 - 优化了了折线图窗口的打开方式（但是一直不停打开再关掉也会炸）
 - 优化了ListView的加载动画（颜色从浅蓝色改为了浅绿色）
 - 小幅度优化了各项动画的执行
 - 优化了代码的逻辑

修复内容：
 - 修复了历史记录中点评创建时间都是启动时间的问题
 - 修复了加载列表闪光动画时莫名卡住的问题
 - 修复了我的精神状态太好的bug

所以说这个PySide6写起来是真的头大
写动画的时候属于是手（Thread）脚（QPropertyAnimation）并用了
还有，存档定期爆炸的bug我不打算修
孩子，老老实实建你的还原点吧""",

    10112: """
1.1.12（2024/11/17） 更新日志：

更新内容：
 - 一键发送作业点评的功能，位于顶边栏-操作
 - 学生历史分数绘制图像，位于学生信息-历史记录
 - 动态背景支持，用cv2做的，播放background.mp4
 - 修改子窗口启动位置，用于照顾残障人士（？）
 - "关于"窗口，位于顶边栏-更多

优化内容：
 - 把按钮闪烁的逻辑又改了一遍（用Property和QPropertyAnimation）
 - 所有的ListWidget在加载时会显示动画，用Thread做的
 - 学生排名列表的前三名会标亮（并列会同时标亮）
 - 把班级概览信息转到了右下角的TabWidget
 - 在源代码里面补齐了部分注释

修复内容：
 - 修复了发点评太快窗口卡死的问题
 - 不记得修复了什么其他的了，反正就是一堆乱七八糟的bug
 - 另外增加了114514个bug
 - 还增加了一些反人类的东西，自己探索吧

""",
}


CORE_UPDATE_LOG:Dict[int, str] = {
    10105:"""

1.1.5（2024/11/26） 更新日志：

新内容：
 - 模板存储优化（dict->collections.OrderedDict）

bug修复：
 - 暂无

""",
    10104: """

1.1.4（2024/11/17） 更新日志：

新内容：
 - 在撤回时可以简单预览将要撤回的内容（以后会详细做）
 - 成就系统内部支持对上周信息的查询
 - 增加绘图类，支持绘制各种函数图像
 - 然后我自己都不记得更新了什么
 
bug修复：
 - 修复了多用户的接口（NCW狂喜）
 - 修复了撤回点评时历史最低分不能恢复的bug
 - 修复部分新版本加载老版本存档爆掉的问题
 - 修复了我精神状态过于正常的bug

"""
} 


# 获取本地版本信息
try:
    VERSION_INFO = json.loads(open("version", "r").read())
    CORE_VERSION = VERSION_INFO["core_version"]
    CORE_VERSION_CODE = VERSION_INFO["core_version_code"]
    CLIENT_VERSION = VERSION_INFO["client_version"]
    CLIENT_VERSION_CODE = VERSION_INFO["client_version_code"]
except Exception as e:
    print("警告：获取本地版本信息失败")
    VERSION_INFO = {
        "core_version": "unknown",
        "core_version_code": 0,
        "client_version": "unknown",
        "client_version_code": 0
    }
    CORE_VERSION = VERSION_INFO["core_version"]
    CORE_VERSION_CODE = VERSION_INFO["core_version_code"]
    CLIENT_VERSION = VERSION_INFO["client_version"]
    CLIENT_VERSION_CODE = VERSION_INFO["client_version_code"]


url = "https://gitee.com/JustNothing_1021/class_manager/raw/master/version"

def update_check(current_core_version:int, current_gui_version:int) -> Union[Literal[True], Exception, dict]:

    """获取更新信息。
    
    Args:
        current_core_version (int): 当前核心版本号
        current_gui_version (int): 当前GUI版本号

    Returns:
        bool: 是否有更新
        str: 更新信息
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = json.loads(response.text)
        core_version = data["core_version_code"]
        gui_version = data["client_version_code"]
        if core_version > current_core_version or gui_version > current_gui_version:
            return data
        elif core_version == current_core_version and gui_version == current_gui_version:
            return True
        else:
            return False
            
    except Exception as e:
        return e
    


def get_update_zip(path:str="update.zip") -> Union[Literal[True], Exception, dict]:
    """下载更新包"""
    try:
        response = requests.get(DOWNLOAD_URL)
        response.raise_for_status()
        with open(path, "wb") as f:
            f.write(response.content)
        return True
    except Exception as e:
        return e

def unzip_to_dir(path:str="update.zip", dir:str="update"):
    """解压更新包到指定目录"""
    try:
        shutil.rmtree(dir)
    except FileNotFoundError:
        pass
    try:
        with zipfile.ZipFile(path, "r") as zip_ref:
            zip_ref.extractall(dir)
        return True
    except Exception as e:
        return e

def update(dir:str="update"):
    """执行更新操作"""
    try:
        shutil.copytree(os.path.join(dir, f"{REPO_NAME}-{MASTER}"), os.getcwd(), dirs_exist_ok=True)
    except Exception as e:
        print("更新失败，请手动更新")
        print(f"错误：[{e.__class__.__name__}] {e}")
        raise
    finally:
        try:
            os.remove("update.zip")
            print("删除源文件，准备趋势")
            shutil.rmtree(dir)
        except Exception as e:
            print("警告：更新包删除失败")
            print(f"[{e.__class__.__name__}] {e}")
    print("更新完成，趋势")
    os.kill(os.getpid(), signal.SIGTERM)
