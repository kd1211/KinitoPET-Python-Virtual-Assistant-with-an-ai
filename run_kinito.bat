@echo off
setlocal

REM 1) create a venv if it doesn't exist
if not exist ".venv\Scripts\python.exe" (
  python -m venv .venv
)

REM 2) activate venv
call .venv\Scripts\activate

REM 3) upgrade pip and install required packages
python -m pip install --upgrade pip
pip install requests Pillow pygame pyttsx3 pyautogui

REM 4) optional default Ollama env vars (edit or remove if you don't want them)
set OLLAMA_HOST=http://localhost:11434
set OLLAMA_MODEL=llama2

REM 5) run the app
python Kinito.py

pause
