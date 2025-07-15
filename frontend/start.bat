@echo off
echo Starting Gridseek Frontend...
echo.

REM 检查是否安装了依赖
echo Checking dependencies...
pip list | findstr streamlit >nul
if %errorlevel% neq 0 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
)

echo Starting application...
echo Open your browser and go to the URL shown below:
echo.

REM 启动应用
streamlit run app.py

pause
