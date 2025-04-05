from typing import Literal


app_style: Literal['windowsvista', 'Windows', 'Fusion', 'windows11'] = 'windowsvista'
"软件的样式"


app_stylesheet: str = """
    color: black; 
    font-family: 'Microsoft YaHei UI'; 
    font-size: 9pt;
    font-weight: bold

"""
"软件的样式表"

nl = "\n"
"换行符，3.8.10中的f-string有奇效"

log_style: Literal["new", "old"] = "new"
"日志的样式，new为新版，old为老版"
