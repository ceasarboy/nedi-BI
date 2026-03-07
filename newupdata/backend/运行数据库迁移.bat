@echo off
echo ========================================
echo 便携版数据库迁移工具
echo ========================================
echo.

cd /d "%~dp0"

echo 正在运行数据库迁移...
..\runtime\python\python.exe migrate_db.py

echo.
echo ========================================
echo 迁移完成！
echo ========================================
echo.
pause
