@echo off
cd /d "%~dp0"
echo ==========================================
echo   INICIANDO SISTEMA DE GESTION ESCOLAR
echo ==========================================
echo.
echo 1. Ingresando al directorio del proyecto...
cd gestion_escolar
echo 2. Activando entorno virtual e iniciando servidor...
call .\venv\Scripts\activate.bat
echo 3. Servidor corriendo en http://127.0.0.1:8000/
echo.
echo (No cierres esta ventana mientras uses el sistema)
echo ==========================================
python manage.py runserver
pause
