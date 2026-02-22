@echo off
cd /d %~dp0

echo Configuring Git user...
git config user.email "ceasarboy@users.noreply.github.com"
git config user.name "ceasarboy"

echo Adding files...
git add .

echo Committing...
git commit -m "Add portable package support and config system"

echo Pushing to GitHub...
git push -u origin main

echo.
echo ========================================
echo Done! Check your GitHub repository.
echo ========================================
pause
