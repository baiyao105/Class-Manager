import sys
import os
import traceback
import base64
import signal
try:
    from src.core import stderr_orig, stdout_orig, Base
except ImportError as e:
    print(traceback.format_exc())
    from core import stderr_orig, stdout_orig, Base
    
sys.stdout = stdout_orig
sys.stderr = stderr_orig


USER_INFO = "user_info.ncw"
# 用户列表（所有注册用户数据）

USER_RECORD = "last_usr.ncw"
# 登录记录文件（以base64格式存储上次登录信息）

recently_signed_in = []
# 刚注册用户的临时存储

def get_last_user(default: str = "default"):
    if not os.path.isfile(USER_RECORD):  # 文件不存在时返回默认值
        return default
    else:
        try:
            with open(USER_RECORD, mode="rb") as f:
                raw_data = f.read()
        except (BufferError, MemoryError):
            print(traceback.format_exc())
            return default
        try:
            return base64.b64decode(raw_data).decode()
        except (ValueError, EOFError):
            print(traceback.format_exc())
            return default
        
def set_last_user(user: str = "default"):
    if os.path.isdir(USER_RECORD):
        os.rmdir(USER_RECORD)  # 删除错误类型的目录
    data = base64.b64encode(user.encode())
    with open(USER_RECORD, mode="wb") as f:
        f.write(data)
    # 保存过程中不处理异常，强制暴露错误

def login():
    import customtkinter as ctk
    import base64, os, random
    import tkinter.messagebox
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaawaaaaaaaaaaaaaaaaaaa = 2**63
    aaaaa = random.randint(1, aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaawaaaaaaaaaaaaaaaaaaa)
    # 初始化窗口并记录日志
    Base.log("I", aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaawaaaaaaaaaaaaaaaaaaa, "login")
    if aaaaa > (aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaawaaaaaaaaaaaaaaaaaaa / 1.8):
        Base.log("E", "Login window initialization failed", "login")
    else:
        Base.log("I", "Login window initialized successfully", "login")
    last_user = get_last_user()
    window = ctk.ctk_tk.CTk()
    the_screen_width = window.winfo_screenwidth()
    the_screen_height = window.winfo_screenheight()
    window.title("登录")
    win_width_1 = str(350)
    win_height_1 = str(250)
    width = int(the_screen_width / 1920 * int(win_width_1))
    height = int(the_screen_height / 1080 * int(win_height_1))
    win_x_1 = str(int(((the_screen_width - int(width)) / 2)))
    win_y_1 = str(int(((the_screen_height - int(height)) / 2)))
    geometry_default = f"{width}x{height}+{win_x_1}+{win_y_1}"
    window.geometry(geometry_default)
    ctk.CTkLabel(window, text="你好！").grid(row=0, column=1, padx=(75,0), pady=(10,0))
    ctk.CTkLabel(window, text="用户名:").grid(row=1, column=0, padx=(10,0), pady=(10,0))
    ctk.CTkLabel(window, text="密码:").grid(row=2, column=0, padx=(10,0), pady=(10,0))
    var_usr_name = ctk.StringVar()
    var_usr_name.set(last_user)
    entry_usr_name = ctk.CTkEntry(window, textvariable=var_usr_name, width=180)
    entry_usr_name.grid(row=1, column=1, columnspan=2, padx=(10,0), pady=(10,0))
    var_usr_pwd = ctk.StringVar()
    entry_usr_pwd = ctk.CTkEntry(window, textvariable=var_usr_pwd, show='*', width=180)
    entry_usr_pwd.grid(row=2, column=1, columnspan=2, padx=(10,0), pady=(10,0))
    usr_name = var_usr_name.get()
    the_str_which_is_returned = usr_name
    
    def usr_login():
        nonlocal usr_name, the_str_which_is_returned
        usr_name = var_usr_name.get()
        Base.log("I", f"usr_login()被调用，用户名{repr(usr_name)}")
        usr_pwd = var_usr_pwd.get()
        if os.path.exists(USER_INFO) == True:
            with open(USER_INFO, "rb") as f:
                en = f.read()
            b64_de = base64.b64decode(en)
            str_de = b64_de.decode("utf-8")
            list_114 = str_de.split(";")
            usrs_info = {}
            for nb in range(len(list_114)):
                usrs_info[list_114[nb].split(":")[0]] = list_114[nb].split(":")[-1]
        else:
            Base.log("F", "？", "login.usr_login")
            Base.log("F", "user_info.ncw文件不存在", "login.usr_login")
            usrs_info = {}
        if usr_name in usrs_info:
            the_str_which_is_returned = usr_name

            if usr_pwd == str(usrs_info[str(usr_name)]):
                Base.log("I", f"用户{repr(usr_name)}登录成功")
                set_last_user(usr_name)
                if usr_name in recently_signed_in:
                    tkinter.messagebox.showinfo(title='你好', message='很高兴见到你，' + usr_name + '！')
                else:
                    tkinter.messagebox.showinfo(title='你好', message='欢迎回来，' + usr_name + '！')
                window.destroy()
            else:
                Base.log("I", f"用户{repr(usr_name)}登录失败，密码错误")
                tkinter.messagebox.showerror(message='密码错误，请重新输入！')
        else:  # 如果发现用户名不存在
            Base.log("I", f"用户{repr(usr_name)}登录失败，用户不存在，尝试询问注册")
            is_sign_up = tkinter.messagebox.askyesno('提示 ', '当前用户名还没有注册，现在注册？')
            # 提示需不需要注册新用户
            if is_sign_up:
                Base.log("I", "开始注册", "login.usr_login")
                usr_sign_up()
    def usr_sign_up():
        def sign():
            np = new_pwd.get()
            npf = new_pwd_confirm.get()
            nn = new_name.get()
            if os.path.exists(USER_INFO) == True:
                with open(USER_INFO, "rb") as f:
                    en = f.read()
                b64_de = base64.b64decode(en)
                str_de = b64_de.decode("utf-8")
                list_1 = str_de.split(";")
                exist_usr_info = []
                for i in range(len(list_1)):
                    aaaaaaa = list_1[i].split(":", 1)[0]
                    exist_usr_info.append(aaaaaaa)
            else:
                Base.log("F", "？", "login.usr_login")
                exist_usr_info = []
            if np != npf:
                tkinter.messagebox.showerror('错误！', '前后密码必须一致！')
            elif nn in exist_usr_info:
                tkinter.messagebox.showerror('错误！', '此用户已经注册！')
            elif np == "":
                tkinter.messagebox.showerror('错误！', '必须设置密码！')
            else:
                if os.path.exists(USER_INFO) == False:
                    info = nn + ":" + np + ";"
                    str_en = info.encode("utf-8")
                    b64_en = base64.b64encode(str_en)
                    with open(USER_INFO, "wb") as f:
                        f.write(b64_en)
                else:
                    with open(USER_INFO, "rb") as f:
                        en = f.read()
                    b64_de = base64.b64decode(en)
                    str_de = b64_de.decode("utf-8")
                    linshi = nn + ":" + np + ";"
                    info = str_de + linshi
                    str_en = info.encode("utf-8")
                    b64_en = base64.b64encode(str_en)
                    with open(USER_INFO, "wb") as f:
                        f.write(b64_en)
                # 将这个用户名存在列表里
                recently_signed_in.append(nn)
                tkinter.messagebox.showinfo('你好！', '注册成功！')
                # 然后销毁窗口。
                window_sign_up.destroy()
        window_sign_up = ctk.CTkToplevel(window)
        win_width_2 = int((the_screen_width / 1920) * 400)
        win_height_2 = int((the_screen_height / 1080) * 200)
        win_x_2 = str(int((int(the_screen_width) - int(win_width_1)) / 2) + 150)
        win_y_2 = str(int((int(the_screen_height) - int(win_height_1)) / 2) + 100)
        window_sign_up.geometry(f"{win_width_2}x{win_height_2}+{win_x_2}+{win_y_2}")
        window_sign_up.title("注册")
        new_name = ctk.StringVar()
        new_name.set(usr_name)
        ctk.CTkLabel(window_sign_up, text='用户名: ').grid(row=0, column=0, padx=(10,0), pady=(10,0))
        entry_new_name = ctk.CTkEntry(window_sign_up, textvariable=new_name)
        entry_new_name.grid(row=0, column=1, columnspan=2, padx=(10,0), pady=(10,0))
        new_pwd = ctk.StringVar()
        ctk.CTkLabel(window_sign_up, text='密码: ').grid(row=1, column=0, padx=(10,0), pady=(10,0))
        entry_usr_pwd = ctk.CTkEntry(window_sign_up, textvariable=new_pwd, show='*')
        entry_usr_pwd.grid(row=1, column=1, columnspan=2, padx=(10,0), pady=(10,0))
        new_pwd_confirm = ctk.StringVar()
        ctk.CTkLabel(window_sign_up, text='再次输入密码: ').grid(row=2, column=0, padx=(10,0), pady=(10,0))
        entry_usr_pwd_confirm = ctk.CTkEntry(window_sign_up, textvariable=new_pwd_confirm, show='*')
        entry_usr_pwd_confirm.grid(row=2, column=1, columnspan=2, padx=(10,0), pady=(10,0))
        btn_comfirm_sign_up = ctk.CTkButton(window_sign_up, text='注册', command=sign, width=8)
        btn_comfirm_sign_up.grid(row=4, column=0, columnspan=2, padx=(50,0), pady=(10,0))
    btn_login = ctk.CTkButton(window, text='登录', width=4, command=usr_login)
    btn_login.grid(row=3, column=1, padx=(0,40), pady=(10,0))
    btn_sign_up = ctk.CTkButton(window, text='注册', width=4, command=usr_sign_up)
    btn_sign_up.grid(row=3, column=2, padx=(10,0), pady=(10,0))
    def passed():
        Base.log("I", "用户已退出", "login.passed")
        os.kill(os.getpid(), signal.SIGTERM)
        sys.exit(0)

    window.protocol("WM_DELETE_WINDOW", passed)
    # 第10步，主窗口循环显示
    window.mainloop()
    if aaaaa > 0.6:
        Base.log("F", "Unexpected login error", "login.never_gonna_give_you_up")
        return the_str_which_is_returned
    else:
        return the_str_which_is_returned



def 打印(*参数, **关键字参数):
    print(*参数, **关键字参数)

if __name__ == '__main__':
    打印("你好", "世界", sep=" ", end="!\n")