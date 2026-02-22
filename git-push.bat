@echo off
cd /d %~dp0

echo Configuring Git user...
git config user.email "ceasarboy@users.noreply.github.com"
git config user.name "ceasarboy"

echo Adding resolved files...
git add .

echo Committing merge...
git commit -m "Merge and add project files"

echo Pushing to GitHub...
git push -u origin main

echo.
echo ========================================
echo Done! Check your GitHub repository.
echo ========================================
pause
