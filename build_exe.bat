@echo off
setlocal

REM Make sure the venv exists and activate it
if not exist ".venv\Scripts\activate" (
  echo Virtualenv not found. Run run_kinito.bat first to create it.
  pause
  exit /b 1
)

call .venv\Scripts\activate

REM Install PyInstaller if missing
pip install pyinstaller

REM Build single-file executable.
REM NOTE: --add-data format uses semicolon on Windows: "source;dest"
pyinstaller --noconfirm --onefile --windowed --add-data "GameAssets;GameAssets" Kinito.py

echo.
echo Build finished. Check the dist\ directory for Kinito.exe
pause
