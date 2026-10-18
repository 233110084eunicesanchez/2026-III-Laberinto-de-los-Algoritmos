@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Primero sigue GUIA_WINDOWS.html para instalar el proyecto.
  pause
  exit /b 1
)
if not exist ".env" (
  echo Falta .env. Ejecuta preparar.py y configura PostgreSQL.
  pause
  exit /b 1
)
echo Abre http://127.0.0.1:8000/ en tu navegador.
echo Para detener: Ctrl+C.
".venv\Scripts\python.exe" manage.py runserver
pause
