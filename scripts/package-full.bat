@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1

echo ========================================
echo PB-BI Portable Package Builder
echo ========================================
echo.
echo This script creates a complete portable package
echo with Python and Node.js runtime included.
echo.

set PROJECT_DIR=%~dp0..
set DIST_DIR=%PROJECT_DIR%\dist\pb-bi-portable
set PYTHON_VERSION=3.11.7
set NODE_VERSION=20.11.0

echo [1/12] Cleaning old package...
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"
mkdir "%DIST_DIR%"
mkdir "%DIST_DIR%\backend"
mkdir "%DIST_DIR%\frontend"
mkdir "%DIST_DIR%\config"
mkdir "%DIST_DIR%\runtime"

echo [2/12] Copying backend code...
xcopy "%PROJECT_DIR%\src" "%DIST_DIR%\backend\src" /E /I /Y >nul
xcopy "%PROJECT_DIR%\config" "%DIST_DIR%\config" /E /I /Y >nul
copy "%PROJECT_DIR%\requirements.txt" "%DIST_DIR%\backend\" /Y >nul

echo [3/12] Building frontend...
cd /d "%PROJECT_DIR%\frontend"
call npm install >nul 2>&1
call npm run build >nul 2>&1
xcopy "%PROJECT_DIR%\frontend\dist" "%DIST_DIR%\frontend\dist" /E /I /Y >nul

echo [4/12] Downloading Python %PYTHON_VERSION% portable...
cd /d "%DIST_DIR%\runtime"
if not exist "python" (
    curl -L -o python.zip "https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-embed-amd64.zip"
    mkdir python
    tar -xf python.zip -C python
    del python.zip
    
    rem Configure Python embed version - use only local libs (no system packages)
    (
    echo python%PYTHON_VERSION:.=%.zip
    echo .
    echo libs
    echo ../../backend/libs
    ) > python\python%PYTHON_VERSION:.=%._pth
    
    rem Install pip
    cd python
    curl -o get-pip.py https://bootstrap.pypa.io/get-pip.py
    python.exe get-pip.py >nul 2>&1
    del get-pip.py
    cd ..
)

echo [5/12] Downloading Node.js %NODE_VERSION% portable...
if not exist "node" (
    curl -L -o node.zip "https://nodejs.org/dist/v%NODE_VERSION%/node-v%NODE_VERSION%-win-x64.zip"
    tar -xf node.zip
    ren "node-v%NODE_VERSION%-win-x64" node
    del node.zip
)

echo [6/12] Installing Python dependencies...
cd /d "%DIST_DIR%\backend"
"%DIST_DIR%\runtime\python\python.exe" -m pip install -r requirements.txt -t ./libs --no-warn-script-location >nul 2>&1

echo [7/12] Installing serve for frontend...
cd /d "%DIST_DIR%\runtime"
mkdir npm-global 2>nul
"%DIST_DIR%\runtime\node\npm.cmd" install -g serve --prefix npm-global >nul 2>&1

echo [8/12] Creating backend start script...
(
echo @echo off
echo chcp 65001 ^>nul 2^>^&1
echo title PB-BI Backend
echo.
echo set SCRIPT_DIR=%%~dp0
echo cd /d %%SCRIPT_DIR%%backend
echo.
echo set PYTHONPATH=%%SCRIPT_DIR%%backend\libs
echo set PATH=%%SCRIPT_DIR%%runtime\python;%%PATH%%
echo.
echo echo Starting PB-BI Backend on port 8000...
echo %%SCRIPT_DIR%%runtime\python\python.exe -m uvicorn src.main:app --host 0.0.0.0 --port 8000
) > "%DIST_DIR%\start-backend.bat"

echo [9/12] Creating frontend start script...
(
echo @echo off
echo chcp 65001 ^>nul 2^>^&1
echo title PB-BI Frontend
echo.
echo set SCRIPT_DIR=%%~dp0
echo cd /d %%SCRIPT_DIR%%frontend\dist
echo.
echo rem Use portable Node.js
echo set PATH=%%SCRIPT_DIR%%runtime\node;%%SCRIPT_DIR%%runtime\npm-global;%%PATH%%
echo set npm_config_cache=%%SCRIPT_DIR%%runtime\npm-cache
echo.
echo echo Starting PB-BI Frontend on port 3000...
echo %%SCRIPT_DIR%%runtime\node\node.exe "%%SCRIPT_DIR%%runtime\npm-global\node_modules\serve\build\main.js" -s . -l 3000
) > "%DIST_DIR%\start-frontend.bat"

echo [10/12] Creating main start script...
(
echo @echo off
echo chcp 65001 ^>nul 2^>^&1
echo title PB-BI
echo.
echo set SCRIPT_DIR=%%~dp0
echo.
echo echo ========================================
echo echo PB-BI is starting...
echo echo ========================================
echo echo.
echo.
echo echo Starting backend...
echo start "PB-BI Backend" /min "%%SCRIPT_DIR%%start-backend.bat"
echo.
echo timeout /t 5 /nobreak ^>nul
echo.
echo echo Starting frontend...
echo start "PB-BI Frontend" /min "%%SCRIPT_DIR%%start-frontend.bat"
echo.
echo echo ========================================
echo echo PB-BI is running!
echo echo.
echo echo Frontend: http://localhost:3000
echo echo Backend:  http://localhost:8000
echo echo API Docs: http://localhost:8000/docs
echo echo.
echo echo LAN Access: http://YOUR_IP:3000
echo echo ========================================
echo echo.
echo echo Press any key to open browser...
echo pause ^>nul
echo start http://localhost:3000
) > "%DIST_DIR%\start.bat"

echo [11/12] Creating stop script...
(
echo @echo off
echo echo Stopping PB-BI services...
echo taskkill /FI "WINDOWTITLE eq PB-BI Backend*" /F >nul 2^>^&1
echo taskkill /FI "WINDOWTITLE eq PB-BI Frontend*" /F >nul 2^>^&1
echo echo Services stopped.
echo pause
) > "%DIST_DIR%\stop.bat"

echo [12/12] Creating README...
(
echo # PB-BI Portable
echo.
echo ## Usage
echo.
echo 1. Double-click `start.bat` to start the service
echo 2. Wait for services to start
echo 3. Browser will open automatically, or visit http://localhost:3000
echo 4. Double-click `stop.bat` to stop the service
echo.
echo ## Access URLs
echo.
echo - Frontend: http://localhost:3000
echo - Backend API: http://localhost:8000
echo - API Docs: http://localhost:8000/docs
echo - LAN Access: http://YOUR_IP:3000
echo.
echo ## Ports
echo.
echo - Frontend: 3000
echo - Backend: 8000
echo.
echo ## Directory Structure
echo.
echo ```
echo pb-bi-portable/
echo ├── backend/      # Backend code and dependencies
echo ├── frontend/     # Frontend build output
echo ├── config/       # Configuration and database
echo ├── runtime/      # Python and Node.js runtime
echo │   ├── python/   # Python portable
echo │   ├── node/     # Node.js portable
echo │   └── npm-global/ # Global npm packages (serve)
echo ├── start.bat     # Start script
echo ├── stop.bat      # Stop script
echo └── README.md     # This file
echo ```
echo.
echo ## Firewall
echo.
echo If LAN access doesn't work, run this command as Administrator:
echo.
echo ```
echo netsh advfirewall firewall add rule name="PB-BI" dir=in action=allow protocol=tcp localport=3000,8000
echo ```
echo.
echo ## Requirements
echo.
echo - No Python or Node.js installation required
echo - Just copy the folder and run start.bat
) > "%DIST_DIR%\README.md"

echo.
echo ========================================
echo Package created successfully!
echo.
echo Output: %DIST_DIR%
echo.
echo Usage:
echo   1. Copy the entire 'pb-bi-portable' folder to target machine
echo   2. Double-click start.bat to run
echo   3. No Python or Node.js installation required
echo ========================================
echo.
pause
