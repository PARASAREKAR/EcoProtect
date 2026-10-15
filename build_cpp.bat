@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo   Compiling Environmental Protection C++ Scientific Engine
echo ========================================================

where g++ >nul 2>nul
if %errorlevel% equ 0 (
    echo [FOUND] GCC g++ compiler detected.
    echo Compiling eco_engine.cpp with g++ -O3 -std=c++17 ...
    g++ -O3 -std=c++17 eco_engine.cpp -o eco_engine.exe
    if %errorlevel% equ 0 (
        echo [SUCCESS] eco_engine.exe compiled successfully with g++!
        goto :test_engine
    ) else (
        echo [ERROR] Compilation with g++ failed.
    )
)

where clang++ >nul 2>nul
if %errorlevel% equ 0 (
    echo [FOUND] Clang++ compiler detected.
    echo Compiling eco_engine.cpp with clang++ -O3 -std=c++17 ...
    clang++ -O3 -std=c++17 eco_engine.cpp -o eco_engine.exe
    if %errorlevel% equ 0 (
        echo [SUCCESS] eco_engine.exe compiled successfully with clang++!
        goto :test_engine
    )
)

where cl >nul 2>nul
if %errorlevel% equ 0 (
    echo [FOUND] MSVC cl.exe compiler detected.
    echo Compiling eco_engine.cpp with cl /O2 /std:c++17 ...
    cl /O2 /std:c++17 /EHsc eco_engine.cpp /Fe:eco_engine.exe
    if %errorlevel% equ 0 (
        echo [SUCCESS] eco_engine.exe compiled successfully with MSVC!
        goto :test_engine
    )
)

echo [INFO] No C++ compiler (g++, clang++, or cl) found in standard PATH.
echo [INFO] The Python backend automatically includes an identical high-precision
echo        embedded Python computation engine as a graceful fallback.
echo [INFO] When a C++ compiler is installed, re-run this script to generate eco_engine.exe.
goto :done

:test_engine
echo.
echo Running diagnostic self-test of compiled C++ engine:
.\eco_engine.exe

:done
echo ========================================================
