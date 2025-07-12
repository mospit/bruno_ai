# PostgreSQL Password Reset Script for Windows
# Run this script as Administrator

param(
    [string]$NewPassword = "bruno123"
)

Write-Host "Resetting PostgreSQL password..." -ForegroundColor Green

try {
    # Stop PostgreSQL service
    Write-Host "Stopping PostgreSQL service..." -ForegroundColor Yellow
    Stop-Service -Name "postgresql-x64-15" -Force
    Start-Sleep -Seconds 2
    
    # Backup original pg_hba.conf
    $pgDataDir = "C:\Program Files\PostgreSQL\15\data"
    $pgHbaConf = "$pgDataDir\pg_hba.conf"
    $backupFile = "$pgHbaConf.backup"
    
    Write-Host "Backing up pg_hba.conf..." -ForegroundColor Yellow
    Copy-Item $pgHbaConf $backupFile -Force
    
    # Modify pg_hba.conf to allow trust authentication
    Write-Host "Modifying authentication method..." -ForegroundColor Yellow
    (Get-Content $pgHbaConf) -replace "md5", "trust" | Set-Content $pgHbaConf
    
    # Start PostgreSQL service
    Write-Host "Starting PostgreSQL service..." -ForegroundColor Yellow
    Start-Service -Name "postgresql-x64-15"
    Start-Sleep -Seconds 5
    
    # Reset password
    Write-Host "Resetting postgres user password..." -ForegroundColor Yellow
    & "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "ALTER USER postgres PASSWORD '$NewPassword';"
    
    # Create Bruno database and user
    Write-Host "Creating Bruno database and user..." -ForegroundColor Yellow
    & "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "CREATE DATABASE bruno_db;"
    & "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "CREATE USER bruno_user WITH PASSWORD 'bruno_pass123';"
    & "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE bruno_db TO bruno_user;"
    & "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d bruno_db -c "GRANT ALL ON SCHEMA public TO bruno_user;"
    
    # Stop service to restore security
    Write-Host "Stopping PostgreSQL service to restore security..." -ForegroundColor Yellow
    Stop-Service -Name "postgresql-x64-15" -Force
    Start-Sleep -Seconds 2
    
    # Restore original pg_hba.conf
    Write-Host "Restoring original authentication method..." -ForegroundColor Yellow
    Copy-Item $backupFile $pgHbaConf -Force
    Remove-Item $backupFile -Force
    
    # Start service again
    Write-Host "Starting PostgreSQL service..." -ForegroundColor Yellow
    Start-Service -Name "postgresql-x64-15"
    Start-Sleep -Seconds 3
    
    Write-Host "Password reset complete!" -ForegroundColor Green
    Write-Host "New postgres password: $NewPassword" -ForegroundColor Cyan
    Write-Host "Bruno database and user created successfully!" -ForegroundColor Green
    
} catch {
    Write-Host "Error occurred: $_" -ForegroundColor Red
    Write-Host "Please run this script as Administrator" -ForegroundColor Yellow
    
    # Try to restore backup if it exists
    if (Test-Path $backupFile) {
        Copy-Item $backupFile $pgHbaConf -Force
        Remove-Item $backupFile -Force
        Start-Service -Name "postgresql-x64-15" -ErrorAction SilentlyContinue
    }
}
