# Dev_Stack Host Setup Script (Windows PowerShell)
# Installs Python dependencies required for running Dev_Stack utility scripts

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Dev_Stack Host Setup (Windows)" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python 3
Write-Host "Checking Python 3 installation..." -ForegroundColor Yellow

$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $version = python --version 2>&1
    if ($version -match "Python 3") {
        $pythonCmd = "python"
    }
}

if (-not $pythonCmd -and (Get-Command python3 -ErrorAction SilentlyContinue)) {
    $pythonCmd = "python3"
}

if ($pythonCmd) {
    $version = & $pythonCmd --version
    Write-Host "✓ Found: $version" -ForegroundColor Green
} else {
    Write-Host "✗ Python 3 not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.8+ first:" -ForegroundColor Yellow
    Write-Host "  Option 1: Download from https://www.python.org/downloads/"
    Write-Host "  Option 2: winget install Python.Python.3.12"
    Write-Host "  Option 3: choco install python"
    Write-Host ""
    Write-Host "Make sure to check 'Add Python to PATH' during installation!"
    exit 1
}
Write-Host ""

# Check pip
Write-Host "Checking pip installation..." -ForegroundColor Yellow

$pipCmd = $null
if (Get-Command pip -ErrorAction SilentlyContinue) {
    $pipCmd = "pip"
} elseif (Get-Command pip3 -ErrorAction SilentlyContinue) {
    $pipCmd = "pip3"
}

if ($pipCmd) {
    Write-Host "✓ pip is already installed" -ForegroundColor Green
} else {
    Write-Host "! pip not found, attempting to install..." -ForegroundColor Yellow
    
    & $pythonCmd -m ensurepip --upgrade
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ pip installed successfully" -ForegroundColor Green
        $pipCmd = "pip"
    } else {
        Write-Host "✗ Failed to install pip" -ForegroundColor Red
        Write-Host "Please install pip manually: $pythonCmd -m ensurepip --upgrade"
        exit 1
    }
}
Write-Host ""

# Install Python packages
Write-Host "Installing Python dependencies from requirements.txt..." -ForegroundColor Yellow
Write-Host ""

$installCmd = "$pipCmd install -r requirements.txt"
Invoke-Expression $installCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    Write-Host ""
    Write-Host "You may need to create a virtual environment instead:" -ForegroundColor Yellow
    Write-Host "  $pythonCmd -m venv .venv"
    Write-Host "  .venv\Scripts\Activate.ps1"
    Write-Host "  pip install -r requirements.txt"
    exit 1
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "✓ Setup Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now run Dev_Stack utility scripts:"
Write-Host "  $pythonCmd scripts\embed_codebase.py"
Write-Host "  $pythonCmd scripts\task_manager.py"
Write-Host "  $pythonCmd scripts\watcher.py"
Write-Host ""
