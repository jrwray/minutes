@echo off
title Minutes
rem UTF-8 console so names, arrows and non-English text display correctly
chcp 65001 >nul
cd /d "%~dp0"
where uv >nul 2>nul && (set "UV=uv") || (set "UV=python -m uv")
%UV% run --quiet python -m minutes %*
if errorlevel 1 pause
