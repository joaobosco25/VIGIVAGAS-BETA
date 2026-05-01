@echo off
set BACKUP_DIR=backups
if not exist %BACKUP_DIR% mkdir %BACKUP_DIR%
for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set DT=%%d-%%b-%%c
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set HR=%%a%%b
pg_dump "%DATABASE_URL%" -F p -f "%BACKUP_DIR%\vigivagas_backup_%DT%_%HR%.sql"
echo Backup finalizado em %BACKUP_DIR%.
pause
