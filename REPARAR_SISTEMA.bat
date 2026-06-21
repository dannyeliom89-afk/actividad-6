@echo off
cd /d "%~dp0"
echo ==============================================
echo   REPARANDO RUTAS DEL ENTORNO VIRTUAL
echo ==============================================
cd gestion_escolar
.\venv\Scripts\python.exe -c "import os; venv_path = os.path.abspath('venv'); cfg_path = os.path.join(venv_path, 'pyvenv.cfg'); act_path = os.path.join(venv_path, 'Scripts', 'activate.bat'); c = open(cfg_path).read(); lines=c.splitlines(); old_v=None; for l in lines: \n  if l.startswith('command'): old_v=l.split('venv ')[1]\nif old_v: open(cfg_path, 'w').write(c.replace(old_v, venv_path))\na = open(act_path).read(); lines_a=a.splitlines(); old_a=None; for l in lines_a:\n  if l.startswith('set \"VIRTUAL_ENV='): old_a=l.split('=')[1].replace('\"', '')\nif old_a: open(act_path, 'w').write(a.replace(old_a, venv_path))\nprint('Rutas actualizadas a:', venv_path)"
echo.
echo Proceso finalizado.
pause
