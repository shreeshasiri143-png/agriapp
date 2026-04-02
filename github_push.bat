@echo off
echo ========================================
echo  Pushing AgriApp to GitHub
echo  Repository: https://github.com/shreeshasiri143-png/agriapp
echo ========================================
echo.

echo Checking git status...
git status

echo.
echo Adding all changes...
git add .

echo.
echo Committing changes...
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" set commit_msg=Update AgriApp - Fertilizer Recommendation System

git commit -m "%commit_msg%"

echo.
echo Pushing to GitHub...
echo Note: You may need to authenticate in your browser
git push origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo  SUCCESS! Code pushed to GitHub
    echo  Repository: https://github.com/shreeshasiri143-png/agriapp
    echo ========================================
) else (
    echo.
    echo ========================================
    echo  Push failed. Please check authentication
    echo  and try again.
    echo ========================================
)

echo.
pause
