@echo off
title Smart Panchayat AI — Multi-State Decision Support Platform
color 0A
echo.
echo  ========================================================================
echo    Smart Panchayat AI Platform (5 States)
echo    Kerala - Karnataka - Tamil Nadu - Andhra Pradesh - Maharashtra
echo    Machine Learning Decision Support & Linear Programming Optimization
echo  ========================================================================
echo.
echo  Starting... Please wait, your browser will open automatically.
echo.

cd /d "%~dp0"
python launch.py

echo.
echo  Server stopped. Press any key to close.
pause > nul
