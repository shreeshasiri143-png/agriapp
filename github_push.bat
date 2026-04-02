@echo off
echo Attempting to initialize and push to GitHub...

git init
if %errorlevel% neq 0 (
    echo.
    echo ERROR: "git" is still not recognized. 
    echo Please install Git for Windows (https://git-scm.com/download/win) 
    echo OR ensure C:\Program Files\Git\cmd is in your Windows Path.
    pause
    exit /b
)

git add .
git commit -m "Auto-commit: AgriApp System"
git branch -M main
git remote add origin https://github.com/shreeshasiri143-png/agriapp.git
git push -u origin main

echo.
echo Process complete!
pause
