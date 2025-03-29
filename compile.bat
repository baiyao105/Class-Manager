:: Use GB2312 AND CRLF
:: Commit by CRLF, not LF
@echo off
chcp 936 >nul
setlocal enabledelayedexpansion
title ClassManager_编译
cd /d "%~dp0"

set "DEFAULT_COMPILER=1"
set "COMPILER_CMD=pyinstaller"
set "COMPILER_NAME=PyInstaller"

if not exist "compile.conf" (
    call :first_run_config
)

for /f "tokens=1,2 delims==" %%a in (compile.conf) do set "%%a=%%b"

if "%create_venv%"=="1" set "install_requirements=1"

if "%compiler%"=="1" (
    set "COMPILER_CMD=pyinstaller"
    set "COMPILER_NAME=PyInstaller"
) else if "%compiler%"=="2" (
    set "COMPILER_CMD=nuitka"
    set "COMPILER_NAME=Nuitka"
)

:main_menu
cls
echo ===================================
echo      ClassManager 编译 v2.2
echo        当前编译器：!COMPILER_NAME!
echo ===================================
echo [当前配置]
call :show_config create_venv       "创建虚拟环境"
call :show_config install_requirements "安装依赖"
call :show_config show_process      "显示进度条"
call :show_config build_zip         "生成发行包"
echo ===================================
set "modify="
set /p "modify=输入M修改配置，其他键开始编译："
if /i "%modify%"=="M" call :modify_config

call :check_dependencies || exit /b 1

if not exist "ClassManager\Compile" (
    md "ClassManager\Compile" 2>nul || (
        echo 无法创建编译目录
        pause
        exit /b 1
    )
)
if "%create_venv%"=="1" (
    echo 正在初始化虚拟环境...
    rd /s /q .venv 2>nul
    python -m venv .venv || (
        echo 虚拟环境创建失败
        pause
        exit /b 1
    )
    call .venv\Scripts\activate
    set "install_requirements=1"  :: 强制安装依赖
)
if "%install_requirements%"=="1" (
    echo 正在安装基础依赖...
    if "%show_process%"=="1" (
        python -m pip install -r requirements.txt --progress-bar pretty
    ) else (
        python -m pip install -r requirements.txt -q
    )
    python -m pip install pillow >nul
    echo 正在安装!COMPILER_NAME!...
    if "%COMPILER_CMD%"=="nuitka" (
        python -m pip install nuitka >nul
    ) else (
        python -m pip install pyinstaller >nul
    )
)

call :generate_output_path

if "%COMPILER_CMD%"=="pyinstaller" (
    call :pyinstaller_compile
) else (
    call :nuitka_compile
)

if "%build_zip%"=="1" (
    call :package_release
) else (
    echo 编译输出已保存至：!OUTPUT_PATH!
)

echo.
echo ===== 操作已完成 =====
pause
exit /b

:first_run_config
cls
echo ===== 首次运行配置 =====
echo 请完成以下初始化配置：
echo.
choice /c 12 /n /m "选择编译器 (1.PyInstaller 2.Nuitka): "
set "compiler=!errorlevel!"
echo.
choice /c 01 /n /m "创建虚拟环境 (1=是/0=否): "
set "create_venv=!errorlevel!"
set /a create_venv-=1
choice /c 01 /n /m "显示进度条 (1=是/0=否): "
set "show_process=!errorlevel!"
set /a show_process-=1
choice /c 01 /n /m "生成发行包 (1=是/0=否): "
set "build_zip=!errorlevel!"
set /a build_zip-=1

:: 自动设置依赖安装

if "%create_venv%"=="1" (set "install_requirements=1") else (set "install_requirements=0")

(echo compiler=%compiler%
 echo create_venv=%create_venv%
 echo install_requirements=%install_requirements%
 echo show_process=%show_process%
 echo build_zip=%build_zip%) > compile.conf
exit /b

:modify_config
cls
echo ===== 修改配置 =====
echo 当前编译器：!COMPILER_NAME!
echo.
choice /c 12 /n /m "选择编译器 (1.PyInstaller 2.Nuitka): "
set "compiler=!errorlevel!"
echo.

rem set /p "create_venv=创建虚拟环境 (1=是/0=否): "
rem set /p "show_process=显示进度条 (1=是/0=否): "
rem set /p "build_zip=生成发行包 (1=是/0=否): "

choice /c 01 /n /m "创建虚拟环境 (1=是/0=否): "
set "create_venv=!errorlevel!"
set /a create_venv-=1
choice /c 01 /n /m "显示进度条 (1=是/0=否): "
set "show_process=!errorlevel!"
set /a show_process-=1
choice /c 01 /n /m "生成发行包 (1=是/0=否): "
set "build_zip=!errorlevel!"
set /a build_zip-=1

if "%create_venv%"=="1" set "install_requirements=1"

(echo compiler=%compiler%
 echo create_venv=%create_venv%
 echo install_requirements=%install_requirements%
 echo show_process=%show_process%
 echo build_zip=%build_zip%) > compile.conf
echo 配置已更新！
timeout /t 2 >nul
goto :main_menu

:show_config
setlocal
set "flag=[ ]"
if "!%~1!"=="1" set "flag=[=]"
echo %flag% %~2
endlocal
exit /b

:check_dependencies
python --version >nul 2>&1 || (
    echo 错误：Python环境未正确配置
    echo 请确认：
    echo 1. 已安装Python 3.8+
    echo 2. 已添加至系统PATH
    pause
    exit /b 1
)
exit /b 0

:generate_output_path
for /f "tokens=2 delims==" %%a in ('wmic os get localdatetime /value') do set "datetime=%%a"
set "date_suffix=%datetime:~2,6%"
set "OUTPUT_PATH=dist\main"
if "%build_zip%"=="0" set "OUTPUT_PATH=dist\main_%date_suffix%"

if exist "!OUTPUT_PATH!" (
    choice /m "目录!OUTPUT_PATH!已存在，是否覆盖？(Y覆盖/N取消)"
    if errorlevel 2 exit /b 1
    rd /s /q "!OUTPUT_PATH!" 2>nul
)
if exist "img\favicon.ico" (
    echo 正在验证图标文件...
    python -c "from PIL import Image; img = Image.open('img/favicon.ico'); img.verify()" || (
        echo 错误：图标文件损坏或格式不正确
        pause
        exit /b 1
    )
) else (
    echo 错误：图标文件不存在于img目录
    pause
    exit /b 1
)
exit /b

:pyinstaller_compile
set cmd=pyinstaller main.py -w ^
        --icon               "img/favicon.ico" ^
        -n                   "main" ^
        --contents-directory "." ^
        --add-data           "audio;audio" ^
        --add-data           "img;img" ^
        --add-data           "ui;ui" ^
        --add-data           "utils;utils" ^
        --add-data           "LICENSE;." ^
        --add-data           "src;src" ^
        --add-data           "version;." ^
        --add-data           "main.py;." ^
        --hidden-import      "PyQt6.QtWebEngine" ^
        --exclude-module     "PyQt5" ^
        --exclude-module     "PyQt6" ^
        --distpath           "dist" ^
        --workpath           "build" ^
        --noconfirm

echo 正在使用PyInstaller编译...

rem set "cmd=!cmd! --exclude-module _bootlocale"
rem 这个是干啥用的，在我这边加了这个dill会爆掉

for /f %%i in ('powershell -Command "Get-Date -Uformat %%s"') do set "start_time=%%i"
if "%show_process%"=="0" set "cmd=!cmd! >nul 2>&1"
cmd /c "!cmd!" || (
    echo PyInstaller编译失败
    pause
    exit /b 1

)
for /f %%i in ('powershell -Command "Get-Date -Uformat %%s"') do set "end_time=%%i"
for /f %%i in ('powershell -Command "[Math]::Round(!end_time! - !start_time!, 3)"') do set "time=%%i"
echo 编译耗时：!time!秒
echo 编译完成！
timeout /t 3 >nul
exit /b

:nuitka_compile
echo 正在使用Nuitka编译(慢)...
pip freeze | findstr Nuitka >nul 2>&1 || (
    echo Nuitka未安装, 正在安装...
    pip install nuitka -i https://pypi.tuna.tsinghua.edu.cn/simple
    if errorlevel 1 (
        echo Nuitka安装失败
        pause
        exit /b 1
    )
)
for /f %%i in ('powershell -Command "Get-Date -Uformat %%s"') do set "start_time=%%i"
set cmd=python -m nuitka ^
        --mingw64 ^
        --output-dir=dist ^
        --standalone ^
        --enable-plugin=pyside6 ^
        --include-data-dir=audio=./audio ^
        --include-data-dir=img=./img ^
        --include-data-dir=ui=./ui ^
        --include-data-dir=utils=./utils ^
        --include-data-dir=src=./src ^
        --include-data-file=version=./version ^
        --include-data-file=LICENSE=./LICENSE ^
        --windows-console-mode=disable ^
        --follow-imports main.py ^
        --jobs=16

if "%show_process%"=="1" set "cmd=!cmd! --show-memory --show-progress"

cmd /c "!cmd!" || (
    echo Nuitka编译失败
    pause
    exit /b 1
)
for /f %%i in ('powershell -Command "Get-Date -Uformat %%s"') do set "end_time=%%i"
for /f %%i in ('powershell -Command "[Math]::Round(!end_time! - !start_time!, 3)"') do set "time=%%i"
echo 编译耗时：!time!秒
echo 复制文件...
if exist "dist\main.dist" (
    ren "dist\main.dist" "main"
    move "dist\main" "!OUTPUT_PATH!" >nul
)
echo 编译完成！
timeout /t 3 >nul
exit /b

:package_release
timeout /t 2  >nul
echo 正在生成发行包...
for /f %%i in ('powershell -Command "Get-Date -Uformat %%s"') do set "start_time=%%i"
if not exist "ClassManager\Compile" md "ClassManager\Compile"
set "temp_dir=ClassManager\Compile\temp"
rd /s /q "%temp_dir%" 2>nul
md "%temp_dir%"
xcopy /E /Y "!OUTPUT_PATH!\*" "%temp_dir%\" >nul
powershell -Command "$date=(Get-Date -Format 'yyyyMMdd'); $zipPath='ClassManager\Compile\main_'+$date+'.zip'; Compress-Archive -Path '%temp_dir%' -DestinationPath $zipPath -Force"
rd /s /q "%temp_dir%"
for /f %%i in ('powershell -Command "Get-Date -Uformat %%s"') do set "end_time=%%i"
for /f %%i in ('powershell -Command "[Math]::Round(!end_time! - !start_time!, 3)"') do set "time=%%i"
echo 压缩耗时：!time!秒
if exist "ClassManager\Compile\main_*.zip" (
    echo | set /p "_dummy=发行包已生成："
    powershell -Command "$date=(Get-Date -Format 'yyyyMMdd'); $zipPath='ClassManager\Compile\main_'+$date+'.zip'; $zippath"
    rd /s /q dist build 2>nul
) else (
    echo 压缩包生成失败
)
exit /b