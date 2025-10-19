@echo off
echo ========================================
echo Building News Dashboard Executable
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo Step 1: Installing/Updating dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Step 2: Building executable with PyInstaller...
echo.

pyinstaller --name="News Dashboard" ^
    --onefile ^
    --windowed ^
    --noconsole ^
    --icon=news.png ^
    --add-data="web;web" ^
    --hidden-import=eel ^
    --hidden-import=bottle ^
    --hidden-import=bottle_websocket ^
    --hidden-import=gevent ^
    --hidden-import=geventwebsocket ^
    --hidden-import=bs4 ^
    --hidden-import=lxml ^
    --hidden-import=deep_translator ^
    --hidden-import=deep_translator.google ^
    --hidden-import=tkinter ^
    --hidden-import=fastighetsvarlden_scraper ^
    --hidden-import=cision_scraper ^
    --hidden-import=lokalguiden_scraper ^
    --hidden-import=di_scraper ^
    --hidden-import=fastighetsnytt_scraper ^
    --hidden-import=nordicpropertynews_scraper ^
    --hidden-import=config ^
    --collect-all=eel ^
    --noconfirm ^
    app.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    echo.
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD COMPLETED SUCCESSFULLY!
echo ========================================
echo.
echo Your executable is located at:
echo    dist\News Dashboard.exe
echo.
echo You can now:
echo  1. Test it: cd dist ^&^& "News Dashboard.exe"
echo  2. Share it with others (fully portable!)
echo  3. Data saves to: Documents\News Dashboard Data\
echo.
echo ========================================
pause

