@echo off
chcp 65001 >nul
echo Updating PB-BI Portable frontend...
echo.

cd /d %~dp0..

echo Removing old frontend...
rmdir /s /q dist\pb-bi-portable\frontend\dist

echo Copying new frontend...
xcopy frontend\dist dist\pb-bi-portable\frontend\dist /E /I /Y

echo.
echo ========================================
echo Update complete!
echo Now copy dist\pb-bi-portable\frontend\dist to target machine
echo ========================================
pause
