@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1

echo ========================================
echo PB-BI Portable Quick Update
echo ========================================
echo.
echo This script updates the portable package
echo with the latest code and dependencies.
echo.

set PROJECT_DIR=%~dp0..
set DIST_DIR=%PROJECT_DIR%\dist\pb-bi-portable

if not exist "%DIST_DIR%" (
    echo Error: Portable package not found at %DIST_DIR%
    echo Please run package-full.bat first to create the full package.
    pause
    exit /b 1
)

echo [1/5] Updating backend code...
echo   Removing old backend code...
if exist "%DIST_DIR%\backend\src" rmdir /s /q "%DIST_DIR%\backend\src"
echo   Copying new backend code...
xcopy "%PROJECT_DIR%\src" "%DIST_DIR%\backend\src" /E /I /Y >nul
copy "%PROJECT_DIR%\requirements.txt" "%DIST_DIR%\backend\" /Y >nul

echo [2/5] Updating frontend build...
echo   Removing old frontend build...
if exist "%DIST_DIR%\frontend\dist" rmdir /s /q "%DIST_DIR%\frontend\dist"
echo   Copying new frontend build...
xcopy "%PROJECT_DIR%\frontend\dist" "%DIST_DIR%\frontend\dist" /E /I /Y >nul

echo [3/5] Updating config...
echo   Copying config example...
copy "%PROJECT_DIR%\config.example.ini" "%DIST_DIR%\config\" /Y >nul 2>&1

echo [4/5] Updating Python dependencies...
echo   This may take a few minutes...
cd /d "%DIST_DIR%\backend"
"%DIST_DIR%\runtime\python\python.exe" -m pip install -r requirements.txt -t ./libs --no-warn-script-location --upgrade

echo [5/5] Updating scripts...
echo   Copying startup scripts...
copy "%PROJECT_DIR%\scripts\start.bat" "%DIST_DIR%\" /Y >nul 2>&1
copy "%PROJECT_DIR%\scripts\start-dev.bat" "%DIST_DIR%\" /Y >nul 2>&1

echo.
echo ========================================
echo Portable package updated successfully!
echo.
echo Output: %DIST_DIR%
echo.
echo Note: This only updates code and dependencies.
echo Runtime (Python/Node.js) was not changed.
echo ========================================
echo.
pause
