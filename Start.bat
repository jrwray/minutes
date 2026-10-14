@echo off
title Minutes
cd /d "%~dp0"
where uv >nul 2>nul && (set "UV=uv") || (set "UV=python -m uv")
%UV% run --quiet python -m minutes %*
if errorlevel 1 pause
