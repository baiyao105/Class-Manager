
@echo off
chcp 65001
cls
setlocal enabledelayedexpansion
if not exist py md py
set /a total=0
for %%i in (*.ui) do set /a total+=1
set /a processing=0
for /f %%i in ('powershell -Command "Get-Date -Uformat %%s"') do set "start=%%i"
for %%i in (*.ui) do (
	set /a processing+=1
	for /f "tokens=1 delims=." %%j in ("%%i") do set "fileName=%%j"
	echo. | set /p dummy="translating - %%i"
	pyside6-uic %%i > py/!fileName!.py
	echo. - finished ^(!processing!/!total!^)
)
del py\*.ui 2> nul
for /f %%i in ('powershell -Command "Get-Date -Uformat %%s"') do set "end=%%i"
for /f %%i in ('powershell -Command "[Math]::Round(!end! - !start!, 3)"') do set "time=%%i"
echo.
echo.
echo. Task completed. Elapsed !time! seconds.
echo.
echo.
timeout /t 5 /nobreak > nul
