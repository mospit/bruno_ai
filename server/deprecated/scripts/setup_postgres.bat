@echo off
echo Setting up PostgreSQL for Bruno AI...
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This script must be run as Administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo Stopping PostgreSQL service...
net stop postgresql-x64-15

echo Backing up pg_hba.conf...
copy "C:\Program Files\PostgreSQL\15\data\pg_hba.conf" "C:\Program Files\PostgreSQL\15\data\pg_hba.conf.backup"

echo Modifying authentication method...
powershell -Command "(Get-Content 'C:\Program Files\PostgreSQL\15\data\pg_hba.conf') -replace 'md5', 'trust' | Set-Content 'C:\Program Files\PostgreSQL\15\data\pg_hba.conf'"

echo Starting PostgreSQL service...
net start postgresql-x64-15

echo Waiting for PostgreSQL to start...
timeout /t 5 /nobreak >nul

echo Resetting postgres password...
psql -U postgres -c "ALTER USER postgres PASSWORD 'bruno123';"

echo Creating Bruno database and user...
psql -U postgres -c "CREATE DATABASE bruno_db;"
psql -U postgres -c "CREATE USER bruno_user WITH PASSWORD 'bruno_pass123';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE bruno_db TO bruno_user;"
psql -U postgres -d bruno_db -c "GRANT ALL ON SCHEMA public TO bruno_user;"

echo Restoring security settings...
net stop postgresql-x64-15
copy "C:\Program Files\PostgreSQL\15\data\pg_hba.conf.backup" "C:\Program Files\PostgreSQL\15\data\pg_hba.conf"
del "C:\Program Files\PostgreSQL\15\data\pg_hba.conf.backup"
net start postgresql-x64-15

echo.
echo ✅ PostgreSQL setup complete!
echo.
echo Database credentials:
echo   - postgres password: bruno123
echo   - bruno_user password: bruno_pass123
echo   - Database: bruno_db
echo.
pause
