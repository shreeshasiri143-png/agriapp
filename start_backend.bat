@echo off
echo Starting Fertilizer Recommendation Backend...
echo Backend will be available at: http://127.0.0.1:8000
echo API Documentation at: http://127.0.0.1:8000/docs
echo.
uvicorn backend.main:app --reload --port 8000
pause