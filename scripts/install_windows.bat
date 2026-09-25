@echo off
REM =============================================================================
REM  install_windows.bat — Despliega el Chatbot_With_ML como tarea programada.
REM
REM  Decide con el dueño (Fase 8):
REM   - Tarea programada al iniciar sesión (schtasks /SC ONLOGON).
REM   - .env validado + copiado desde .env.example (nunca se versionan credenciales).
REM   - Instalación idempotente (re-crea la tarea con /F si ya existe).
REM
REM  Uso:  descomprime el repo y ejecuta este archivo con doble clic (o como admin).
REM =============================================================================
@setlocal EnableExtensions
cd /d "%~dp0.."

set "ROOT=%CD%\"
set "PYEXE=%ROOT%venv\Scripts\python.exe"
set "TASK_NAME=ChatbotML"

echo.
echo  Instalador del Chatbot con ML (Windows)
echo  Directorio : %ROOT%
echo  Tarea      : %TASK_NAME% (inicia sesion)
echo.

REM -- 1) Entorno virtual -----------------------------------------------------
if not exist "%PYEXE%" (
    echo [1/4] Creando entorno virtual...
    where py >nul 2>nul
    if %errorlevel%==0 (
        py -3 -m venv "%ROOT%venv"
    ) else (
        python -m venv "%ROOT%venv"
    )
    if errorlevel 1 goto :error
) else (
    echo [1/4] Entorno virtual ya existe.
)

REM -- 2) Dependencias --------------------------------------------------------
echo [2/4] Instalando dependencias (requirements.txt)...
"%PYEXE%" -m pip install --upgrade pip -q
"%PYEXE%" -m pip install -r "%ROOT%requirements.txt" -q
if errorlevel 1 goto :error

REM -- 3) .env: validar o copiar la plantilla --------------------------------
echo [3/4] Configurando .env...
if not exist "%ROOT%.env" (
    if exist "%ROOT%.env.example" (
        copy /Y "%ROOT%.env.example" "%ROOT%.env" >nul
    )
    echo.
    echo    Se creo .env a partir de .env.example.
    echo    EDITALO con las credenciales de Green-API y SMTP y vuelve a ejecutar este script.
    pause
    exit /b 1
)
"%PYEXE%" -c "from app import config; config.validate_credentials()"
if errorlevel 1 (
    echo   [ERROR] Validacion del .env fallo. Revisa ID_INSTANCE y API_TOKEN_INSTANCE.
    pause
    exit /b 1
)
attrib +h "%ROOT%.env" >nul 2>nul
echo   .env validado (oculto).

REM -- 4) Tarea programada ----------------------------------------------------
echo [4/4] Creando tarea programada...
schtasks /Create /F /SC ONLOGON /TN "%TASK_NAME%" /TR "\"%PYEXE%w\" \"%ROOT%run.py\"" >nul
if errorlevel 1 goto :error

schtasks /Query /TN "%TASK_NAME%" >nul
if errorlevel 1 goto :error

echo.
echo  Instalacion completada.
echo.
echo   Iniciar manualmente: schtasks /Run /TN "%TASK_NAME%"
echo   Estado de la tarea:  schtasks /Query /TN "%TASK_NAME%"
echo   Logs:                %ROOT%chatbot_operations.log
echo   Datos:               %ROOT%app\data\ (facturas, contador, clientes)
echo.
echo   Operacion 24/7: ver docs\DESPLEGUE.md.
echo.
pause
exit /b 0

:error
echo.
echo [ERROR] Fallo en la instalacion. Revisa el mensaje anterior.
pause
exit /b 1