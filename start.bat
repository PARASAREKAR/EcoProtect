@echo off
setlocal enabledelayedexpansion
title EcoProtect Environmental Platform — Launcher

echo.
echo  ==============================================================
echo   🌿  EcoProtect Environmental Protection Platform
echo   Technologies: C++17 / Python Flask / SQLite / HTML5 / CSS3
echo  ==============================================================
echo.

:: Step 1: Find Python
echo [1/4] Locating Python installation...
python --version >nul 2>nul
if %errorlevel% equ 0 (
    for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PYTHON_VER=%%v
    echo       Found: !PYTHON_VER!
) else (
    echo [ERROR] Python not found in PATH.
    echo         Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Step 2: Check Flask installation
echo.
echo [2/4] Checking Flask dependency...
python -c "import flask; print('Flask', flask.__version__)" >nul 2>nul
if %errorlevel% neq 0 (
    echo       Flask not found — installing automatically...
    python -m pip install flask --quiet
    if !errorlevel! equ 0 (
        echo       Flask installed successfully!
    ) else (
        echo [ERROR] Could not install Flask. Check your internet connection.
        pause
        exit /b 1
    )
) else (
    for /f "tokens=*" %%v in ('python -c "import flask; print(flask.__version__)" 2^>nul') do set FLASK_VER=%%v
    echo       Found: Flask !FLASK_VER!
)

:: Step 3: Try compiling C++ engine
echo.
echo [3/4] Compiling C++17 Scientific Eco-Engine...
if exist eco_engine.exe (
    echo       eco_engine.exe already compiled. Skipping build.
) else (
    where g++ >nul 2>nul
    if !errorlevel! equ 0 (
        echo       Compiling with g++ -O3 -std=c++17 ...
        g++ -O3 -std=c++17 eco_engine.cpp -o eco_engine.exe
        if !errorlevel! equ 0 (
            echo       C++ Engine compiled successfully!
        ) else (
            echo       [WARN] Compilation failed — Python embedded engine will be used instead.
        )
    ) else (
        echo       [INFO] No C++ compiler found. Using Python embedded scientific engine.
        echo             Run build_cpp.bat after installing g++ (MinGW / MSYS2) for the compiled engine.
    )
)

:: Step 4: Initialize DB and launch server
echo.
echo [4/4] Initializing database and launching server...
python database.py
echo.
echo  ==============================================================
echo   🌐  Website:    http://127.0.0.1:5000
echo   🔧  Admin:      http://127.0.0.1:5000/admin
echo   🔑  Login:      admin / admin123
echo  ==============================================================
echo.
echo  Press Ctrl+C in this window to stop the server.
echo.

python app.py
pause
