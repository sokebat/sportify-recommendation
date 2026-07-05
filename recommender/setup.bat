@echo off
cd /d "%~dp0"
 
echo.

if exist .venv\ (
    echo Virtual environment already exists. Skipping creation.
) else (
    echo Creating virtual environment...
    python -m venv .venv
    echo Done.
)

echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing dependencies...
pip install --prefer-binary -r requirements.txt

echo.
echo === Setup complete! Run run.bat to start the app. ===
pause