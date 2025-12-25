$ErrorActionPreference = "Stop"

Write-Host "Installing PyInstaller..."
pip install pyinstaller
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to install PyInstaller"; exit 1 }

Write-Host "Building PyMigrate Pro Executable..."
# --collect-all customtkinter is needed to include theme files and assets
pyinstaller --noconfirm --onefile --windowed --clean `
    --name "PyMigratePro" `
    --paths src `
    --collect-all customtkinter `
    launcher.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nBuild Successful!"
    Write-Host "Executable is located at: dist\PyMigratePro.exe"
}
else {
    Write-Error "Build Failed."
}
