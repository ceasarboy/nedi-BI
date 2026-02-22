@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0

rem 默认配置
set DEFAULT_PYTHON_PATH=%SCRIPT_DIR%runtime\python
set DEFAULT_NODE_PATH=%SCRIPT_DIR%runtime\node
set DEFAULT_PYTHON_LIBS_PATH=%SCRIPT_DIR%backend\libs
set DEFAULT_FRONTEND_PATH=%SCRIPT_DIR%frontend\dist
set DEFAULT_CONFIG_PATH=%SCRIPT_DIR%config
set DEFAULT_FRONTEND_PORT=3000
set DEFAULT_BACKEND_PORT=8000
set DEFAULT_BACKEND_HOST=0.0.0.0

rem 读取配置文件
if exist "%SCRIPT_DIR%config.ini" (
  echo Reading config from: %SCRIPT_DIR%config.ini
  for /f "usebackq tokens=1,2 delims==" %%a in ("%SCRIPT_DIR%config.ini") do (
    set line=%%a
    if not "!line:~0,1!"=="#" if not "!line:~0,1!"="[" (
      set key=%%a
      set value=%%b
      set !key!=!value!
    )
  )
)

rem 使用配置或默认值
if not defined python_path set python_path=%DEFAULT_PYTHON_PATH%
if not defined node_path set node_path=%DEFAULT_NODE_PATH%
if not defined python_libs_path set python_libs_path=%DEFAULT_PYTHON_LIBS_PATH%
if not defined frontend_path set frontend_path=%DEFAULT_FRONTEND_PATH%
if not defined config_path set config_path=%DEFAULT_CONFIG_PATH%
if not defined frontend_port set frontend_port=%DEFAULT_FRONTEND_PORT%
if not defined backend_port set backend_port=%DEFAULT_BACKEND_PORT%
if not defined backend_host set backend_host=%DEFAULT_BACKEND_HOST%
if not defined api_base_url (
  set api_base_url=http://%COMPUTERNAME%:%backend_port%
)

rem 输出配置
echo Configuration:
echo   Python: %python_path%
echo   Node: %node_path%
echo   Python libs: %python_libs_path%
echo   Frontend: %frontend_path%
echo   Config: %config_path%
echo   Frontend port: %frontend_port%
echo   Backend port: %backend_port%
echo   Backend host: %backend_host%
echo.

rem 传递给调用者
endlocal ^
  & set "python_path=%python_path%" ^
  & set "node_path=%node_path%" ^
  & set "python_libs_path=%python_libs_path%" ^
  & set "frontend_path=%frontend_path%" ^
  & set "config_path=%config_path%" ^
  & set "frontend_port=%frontend_port%" ^
  & set "backend_port=%backend_port%" ^
  & set "backend_host=%backend_host%" ^
  & set "api_base_url=%api_base_url%"
