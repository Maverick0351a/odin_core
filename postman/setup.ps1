Write-Host "ODIN Protocol Postman Plugin Setup" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

# Check Node.js
Write-Host "Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "Node.js not found. Install from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Check Newman
Write-Host "Checking Newman..." -ForegroundColor Yellow
try {
    newman --version | Out-Null
    Write-Host "Newman is installed" -ForegroundColor Green
} catch {
    Write-Host "Installing Newman..." -ForegroundColor Yellow
    npm install -g newman
    npm install -g newman-reporter-html
}

# Create results directory
if (!(Test-Path "results")) { 
    New-Item -ItemType Directory -Name "results" | Out-Null
    Write-Host "Created results directory" -ForegroundColor Green
}

# Check collection files
$files = @("ODIN_Protocol_Collection.json", "ODIN_Protocol_Environment.json", "ODIN_Protocol_Tests.json")
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "Found: $file" -ForegroundColor Green
    } else {
        Write-Host "Missing: $file" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Edit ODIN_Protocol_Environment.json" -ForegroundColor White
Write-Host "2. Set your odin_api_token value" -ForegroundColor White
Write-Host "3. Run: newman run ODIN_Protocol_Tests.json -e ODIN_Protocol_Environment.json" -ForegroundColor White
