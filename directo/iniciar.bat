@echo off
chcp 65001 >nul
title Directo - Duelos de objetos
cd /d "%~dp0"
where node >nul 2>nul || (echo Falta Node.js. Descargalo de https://nodejs.org ^(version LTS^), instalalo y vuelve a abrir este archivo. & pause & exit /b)
if not exist node_modules (echo Instalando la primera vez... & call npm install --no-audit --no-fund)
start "" /min cmd /c "timeout /t 3 >nul && (start chrome --app=http://localhost:3060 --window-size=540,960 || start msedge --app=http://localhost:3060 --window-size=540,960) && start http://localhost:3060/control"
node servidor.js %*
pause
