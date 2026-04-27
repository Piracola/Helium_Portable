@echo off
chcp 65001 >nul

set "APP_DIR=%~dp0Helium"
set "HELIUM_EXE=%APP_DIR%\chrome.exe"

if not exist "%HELIUM_EXE%" (
    echo 未找到 Helium\chrome.exe
    pause
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "$s=New-Object -ComObject WScript.Shell; $l=$s.CreateShortcut('%~dp0Helium.lnk'); $l.TargetPath='%HELIUM_EXE%'; $l.Arguments='--disable-background-networking'; $l.WorkingDirectory='%APP_DIR%'; $l.IconLocation='%HELIUM_EXE%,0'; $l.Save()"

if exist "%~dp0Helium.lnk" (
    echo 快捷方式创建成功
    echo 指向：%HELIUM_EXE%
    exit /b 0
) else (
    echo 快捷方式创建失败
    pause
    exit /b 1
)
