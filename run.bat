@echo off
cd /d "%~dp0"

if not exist .venv\ (
    echo Virtual environment not found. Running setup first...
    call setup.bat
)

echo.
echo starting......
call .venv\Scripts\activate.bat