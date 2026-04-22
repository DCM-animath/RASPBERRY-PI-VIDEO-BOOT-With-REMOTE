@echo off
setlocal ENABLEDELAYEDEXPANSION
cd /d "%~dp0"

echo ==========================================
echo   Push package to GitHub
echo ==========================================
echo.

git --version >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Git belum terinstall atau belum masuk PATH.
  pause
  exit /b 1
)

if not exist ".git" (
  git init
)

for /f "delims=" %%i in ('git config --global user.name 2^>nul') do set GIT_NAME=%%i
for /f "delims=" %%i in ('git config --global user.email 2^>nul') do set GIT_EMAIL=%%i

if "%GIT_NAME%"=="" (
  set /p GIT_NAME=Masukkan git user.name: 
  git config --global user.name "%GIT_NAME%"
)

if "%GIT_EMAIL%"=="" (
  set /p GIT_EMAIL=Masukkan git user.email: 
  git config --global user.email "%GIT_EMAIL%"
)

for /f "delims=" %%i in ('git remote get-url origin 2^>nul') do set ORIGIN_URL=%%i
if "%ORIGIN_URL%"=="" (
  set ORIGIN_URL=https://github.com/DCM-animath/raspi-dual-mpv.git
  git remote add origin "!ORIGIN_URL!" 2>nul
)

git add .
git commit -m "Switch to single MPV combined video system"

git checkout -B main
git push -u origin main --force

pause
