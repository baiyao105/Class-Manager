:: Use GB2312 AND CRLF
:: Commit by CRLF, not LF
@echo off
chcp 936 >nul
setlocal enabledelayedexpansion
title ClassManager_����
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
echo      ClassManager ���� v2.2
echo        ��ǰ��������!COMPILER_NAME!
echo ===================================
echo [��ǰ����]
call :show_config create_venv       "�������⻷��"
call :show_config install_requirements "��װ����"
call :show_config show_process      "��ʾ������"
call :show_config build_zip         "���ɷ��а�"
echo ===================================
set "modify="
set /p "modify=����M�޸����ã���������ʼ���룺"
if /i "%modify%"=="M" call :modify_config

call :check_dependencies || exit /b 1

if not exist "ClassManager\Compile" (
    md "ClassManager\Compile" 2>nul || (
        echo �޷���������Ŀ¼
        pause
        exit /b 1
    )
)
if "%create_venv%"=="1" (
    echo ���ڳ�ʼ�����⻷��...
    rd /s /q .venv 2>nul
    python -m venv .venv || (
        echo ���⻷������ʧ��
        pause
        exit /b 1
    )
    call .venv\Scripts\activate
    set "install_requirements=1"  :: ǿ�ư�װ����
)
if "%install_requirements%"=="1" (
    echo ���ڰ�װ��������...
    if "%show_process%"=="1" (
        python -m pip install -r requirements.txt --progress-bar pretty
    ) else (
        python -m pip install -r requirements.txt -q
    )
    python -m pip install pillow >nul
    echo ���ڰ�װ!COMPILER_NAME!...
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
    echo ��������ѱ�������!OUTPUT_PATH!
)

echo.
echo ===== ��������� =====
pause
exit /b

:first_run_config
cls
echo ===== �״��������� =====
echo ��������³�ʼ�����ã�
echo.
choice /c 12 /n /m "ѡ������� (1.PyInstaller 2.Nuitka): "
set "compiler=!errorlevel!"
echo.
choice /c 01 /n /m "�������⻷�� (1=��/0=��): "
set "create_venv=!errorlevel!"
set /a create_venv-=1
choice /c 01 /n /m "��ʾ������ (1=��/0=��): "
set "show_process=!errorlevel!"
set /a show_process-=1
choice /c 01 /n /m "���ɷ��а� (1=��/0=��): "
set "build_zip=!errorlevel!"
set /a build_zip-=1

:: �Զ�����������װ

if "%create_venv%"=="1" (set "install_requirements=1") else (set "install_requirements=0")

(echo compiler=%compiler%
 echo create_venv=%create_venv%
 echo install_requirements=%install_requirements%
 echo show_process=%show_process%
 echo build_zip=%build_zip%) > compile.conf
exit /b

:modify_config
cls
echo ===== �޸����� =====
echo ��ǰ��������!COMPILER_NAME!
echo.
choice /c 12 /n /m "ѡ������� (1.PyInstaller 2.Nuitka): "
set "compiler=!errorlevel!"
echo.

rem set /p "create_venv=�������⻷�� (1=��/0=��): "
rem set /p "show_process=��ʾ������ (1=��/0=��): "
rem set /p "build_zip=���ɷ��а� (1=��/0=��): "

choice /c 01 /n /m "�������⻷�� (1=��/0=��): "
set "create_venv=!errorlevel!"
set /a create_venv-=1
choice /c 01 /n /m "��ʾ������ (1=��/0=��): "
set "show_process=!errorlevel!"
set /a show_process-=1
choice /c 01 /n /m "���ɷ��а� (1=��/0=��): "
set "build_zip=!errorlevel!"
set /a build_zip-=1

if "%create_venv%"=="1" set "install_requirements=1"

(echo compiler=%compiler%
 echo create_venv=%create_venv%
 echo install_requirements=%install_requirements%
 echo show_process=%show_process%
 echo build_zip=%build_zip%) > compile.conf
echo �����Ѹ��£�
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
    echo ����Python����δ��ȷ����
    echo ��ȷ�ϣ�
    echo 1. �Ѱ�װPython 3.8+
    echo 2. �������ϵͳPATH
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
    choice /m "Ŀ¼!OUTPUT_PATH!�Ѵ��ڣ��Ƿ񸲸ǣ�(Y����/Nȡ��)"
    if errorlevel 2 exit /b 1
    rd /s /q "!OUTPUT_PATH!" 2>nul
)
if exist "img\favicon.ico" (
    echo ������֤ͼ���ļ�...
    python -c "from PIL import Image; img = Image.open('img/favicon.ico'); img.verify()" || (
        echo ����ͼ���ļ��𻵻��ʽ����ȷ
        pause
        exit /b 1
    )
) else (
    echo ����ͼ���ļ���������imgĿ¼
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
        --add-data           "utils;utils" ^
        --add-data           "widgets;widgets" ^
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

echo ����ʹ��PyInstaller����...

rem set "cmd=!cmd! --exclude-module _bootlocale"
rem ����Ǹ�ɶ�õģ�������߼������dill�ᱬ��

for /f %%i in ('powershell -Command "Get-Date -Uformat %%s"') do set "start_time=%%i"
if "%show_process%"=="0" set "cmd=!cmd! >nul 2>&1"
cmd /c "!cmd!" || (
    echo PyInstaller����ʧ��
    pause
    exit /b 1

)
for /f %%i in ('powershell -Command "Get-Date -Uformat %%s"') do set "end_time=%%i"
for /f %%i in ('powershell -Command "[Math]::Round(!end_time! - !start_time!, 3)"') do set "time=%%i"
echo �����ʱ��!time!��
echo ������ɣ�
timeout /t 3 >nul
exit /b

:nuitka_compile
echo ����ʹ��Nuitka����(��)...
pip freeze | findstr Nuitka >nul 2>&1 || (
    echo Nuitkaδ��װ, ���ڰ�װ...
    pip install nuitka -i https://pypi.tuna.tsinghua.edu.cn/simple
    if errorlevel 1 (
        echo Nuitka��װʧ��
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
        --include-data-dir=utils=./utils ^
        --include-data-dir=widgets=./widgets ^
        --include-data-dir=src=./src ^
        --include-data-file=version=./version ^
        --include-data-file=LICENSE=./LICENSE ^
        --windows-console-mode=disable ^
        --follow-imports main.py ^
        --jobs=16

if "%show_process%"=="1" set "cmd=!cmd! --show-memory --show-progress"

cmd /c "!cmd!" || (
    echo Nuitka����ʧ��
    pause
    exit /b 1
)
for /f %%i in ('powershell -Command "Get-Date -Uformat %%s"') do set "end_time=%%i"
for /f %%i in ('powershell -Command "[Math]::Round(!end_time! - !start_time!, 3)"') do set "time=%%i"
echo �����ʱ��!time!��
echo �����ļ�...
if exist "dist\main.dist" (
    ren "dist\main.dist" "main"
    move "dist\main" "!OUTPUT_PATH!" >nul
)
echo ������ɣ�
timeout /t 3 >nul
exit /b

:package_release
timeout /t 2  >nul
echo �������ɷ��а�...
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
echo ѹ����ʱ��!time!��
if exist "ClassManager\Compile\main_*.zip" (
    echo | set /p "_dummy=���а������ɣ�"
    powershell -Command "$date=(Get-Date -Format 'yyyyMMdd'); $zipPath='ClassManager\Compile\main_'+$date+'.zip'; $zippath"
    rd /s /q dist build 2>nul
) else (
    echo ѹ��������ʧ��
)
exit /b