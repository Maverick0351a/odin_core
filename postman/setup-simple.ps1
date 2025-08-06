# ODIN Protocol Postman Plugin Setup Script for Windows
# Simple PowerShell script to set up the testing environment

Write-Host "🚀 ODIN Protocol Postman Plugin Setup" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

# Check Node.js
Write-Host "🔍 Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>$null
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Check/Install Newman
Write-Host "📦 Checking Newman..." -ForegroundColor Yellow
try {
    $newmanVersion = newman --version 2>$null
    Write-Host "✅ Newman found: $newmanVersion" -ForegroundColor Green
} catch {
    Write-Host "Installing Newman..." -ForegroundColor Yellow
    npm install -g newman
    npm install -g newman-reporter-html
}

# Create directories
Write-Host "📁 Creating directories..." -ForegroundColor Yellow
if (!(Test-Path "results")) { New-Item -ItemType Directory -Name "results" }

# Validate files
Write-Host "🔍 Checking collection files..." -ForegroundColor Yellow
$files = @("ODIN_Protocol_Collection.json", "ODIN_Protocol_Environment.json", "ODIN_Protocol_Tests.json", "README.md")

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "✅ Found: $file" -ForegroundColor Green
    } else {
        Write-Host "❌ Missing: $file" -ForegroundColor Red
    }
}

# Create quick start script
Write-Host "📝 Creating test scripts..." -ForegroundColor Yellow

$quickScript = @'
# Quick Test for ODIN Protocol
Write-Host "🧪 Running ODIN Protocol Tests..." -ForegroundColor Cyan

# Update these variables with your actual credentials
$apiToken = "your-api-token-here"
$baseUrl = "https://api.odin-protocol.com"

if ($apiToken -eq "your-api-token-here") {
    Write-Host "⚠️ Please update the API token in this script first!" -ForegroundColor Yellow
    Write-Host "Edit the variables at the top of quick-test.ps1" -ForegroundColor Yellow
    exit 1
}

newman run ODIN_Protocol_Tests.json -e ODIN_Protocol_Environment.json --env-var "odin_api_token=$apiToken" --env-var "odin_base_url=$baseUrl" --reporters cli,html --reporter-html-export results/test-report.html

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Tests completed! Check results/test-report.html" -ForegroundColor Green
} else {
    Write-Host "❌ Some tests failed. Check the report for details." -ForegroundColor Red
}
'@

$quickScript | Out-File -FilePath "quick-test.ps1" -Encoding UTF8

# Create environment guide
$envGuide = @'
# ODIN Protocol Environment Configuration

## Required Environment Variables:

1. odin_api_token - Your ODIN Protocol API authentication token
2. odin_base_url - API base URL (e.g., https://api.odin-protocol.com)
3. security_token - Security validation token (for compliance tests)

## Setup Instructions:

### Option 1: Edit Environment File
Open ODIN_Protocol_Environment.json and update the "value" fields:
- odin_api_token: "your-actual-token-here"
- odin_base_url: "https://api.odin-protocol.com"

### Option 2: Use Command Line
newman run ODIN_Protocol_Collection.json -e ODIN_Protocol_Environment.json --env-var "odin_api_token=YOUR_TOKEN" --env-var "odin_base_url=YOUR_URL"

### Option 3: Environment Variables
Set Windows environment variables:
$env:ODIN_API_TOKEN = "your-token"
$env:ODIN_BASE_URL = "https://api.odin-protocol.com"

## Test Commands:

### Basic Health Check:
newman run ODIN_Protocol_Tests.json -e ODIN_Protocol_Environment.json --folder "🧪 Smoke Tests"

### Performance Tests:
newman run ODIN_Protocol_Tests.json -e ODIN_Protocol_Environment.json --folder "⚡ Performance Tests"

### Full Test Suite:
newman run ODIN_Protocol_Collection.json -e ODIN_Protocol_Environment.json --reporters html --reporter-html-export results/full-report.html

### Security Tests:
newman run ODIN_Protocol_Tests.json -e ODIN_Protocol_Environment.json --folder "🔒 Security Tests"
'@

$envGuide | Out-File -FilePath "SETUP_GUIDE.txt" -Encoding UTF8

# Create batch launcher
$batchLauncher = @'
@echo off
echo 🚀 ODIN Protocol Quick Start
echo.
echo Make sure to update your API credentials first!
echo Edit quick-test.ps1 and set your API token and base URL
echo.
pause
echo Running tests...
powershell -ExecutionPolicy Bypass -File quick-test.ps1
pause
'@

$batchLauncher | Out-File -FilePath "QUICK_START.bat" -Encoding ASCII

Write-Host ""
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 🔑 Configure your API credentials:" -ForegroundColor White
Write-Host "   Option A: Edit ODIN_Protocol_Environment.json" -ForegroundColor Gray
Write-Host "   Option B: Edit quick-test.ps1 and update the variables" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 🧪 Run your first test:" -ForegroundColor White
Write-Host "   Double-click: QUICK_START.bat" -ForegroundColor Gray
Write-Host "   Or run: .\quick-test.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "3. 📚 Read the documentation:" -ForegroundColor White
Write-Host "   - README.md (Complete guide)" -ForegroundColor Gray
Write-Host "   - SETUP_GUIDE.txt (Configuration help)" -ForegroundColor Gray
Write-Host ""
Write-Host "📁 Files created:" -ForegroundColor Cyan
Write-Host "   ✅ quick-test.ps1" -ForegroundColor Green
Write-Host "   ✅ QUICK_START.bat" -ForegroundColor Green
Write-Host "   ✅ SETUP_GUIDE.txt" -ForegroundColor Green
Write-Host ""
Write-Host "🎉 Ready to test ODIN Protocol!" -ForegroundColor Green
