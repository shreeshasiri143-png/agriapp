@echo off
echo ========================================
echo  Fertilizer Recommendation System
echo  Local Deployment Script
echo ========================================
echo.
echo This will start both backend and frontend services.
echo.
echo Backend API: http://127.0.0.1:8000
echo Frontend UI: http://localhost:5173
echo API Docs: http://127.0.0.1:8000/docs
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause > nul
echo.

echo Starting Backend Server...
start "Backend Server" cmd /k "echo Starting Fertilizer Recommendation Backend... && echo Backend available at: http://127.0.0.1:8000 && echo API Documentation at: http://127.0.0.1:8000/docs && echo. && uvicorn backend.main:app --reload --port 8000"

echo Waiting for backend to initialize...
timeout /t 5 > nul

echo Starting Frontend Server...
start "Frontend Server" cmd /k "echo Starting Fertilizer Recommendation Frontend... && echo Installing dependencies... && cd frontend && npm install && echo. && echo Starting development server... && echo Frontend available at: http://localhost:5173 && echo. && npm run dev"

echo.
echo ========================================
echo  Both services are starting!
echo ========================================
echo Backend: http://127.0.0.1:8000
echo Frontend: http://localhost:5173
echo API Docs: http://127.0.0.1:8000/docs
echo.
echo Two new command windows will open.
echo Wait for both to fully load, then visit:
echo http://localhost:5173 to use the application
echo.
echo Close those windows to stop the services.
echo.
pause