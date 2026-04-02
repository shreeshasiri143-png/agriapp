@echo off
echo Starting Fertilizer Recommendation Frontend...
echo Installing dependencies if needed...
cd frontend
call npm install
echo.
echo Starting development server...
echo Frontend will be available at: http://localhost:5173
echo.
npm run dev
pause