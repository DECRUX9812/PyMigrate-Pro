$ErrorActionPreference = "Stop"

Write-Host "Step 1: Installing dependencies..."
pip install -r requirements-dev.txt
if ($LASTEXITCODE -ne 0) { Write-Error "Dependency installation failed"; exit 1 }

Write-Host "`nStep 2: Linting with Black..."
black --check .
if ($LASTEXITCODE -ne 0) { Write-Warning "Black found formatting issues." } else { Write-Host "Black passed." }

Write-Host "`nStep 3: Linting with Ruff..."
ruff check .
if ($LASTEXITCODE -ne 0) { Write-Warning "Ruff found linting issues." } else { Write-Host "Ruff passed." }

Write-Host "`nStep 4: Running Tests..."
if (Get-Command pytest -ErrorAction SilentlyContinue) {
    pytest
    if ($LASTEXITCODE -eq 5) { 
        Write-Warning "Pytest: No tests collected." 
    } elseif ($LASTEXITCODE -ne 0) {
        Write-Error "Tests failed."
        exit 1
    } else {
        Write-Host "Tests passed."
    }
} else {
    Write-Warning "Pytest not found. Skipping tests."
}

Write-Host "`nCI Run Completed."
