# ODIN Protocol Postman Plugin Setup Script for Windows
# PowerShell script to automate installation and configuration

Write-Host "🚀 ODIN Protocol Postman Plugin Setup" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

# Check if Node.js is installed
Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow

try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js is installed: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is not installed!" -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    Write-Host "Then run this script again." -ForegroundColor Yellow
    exit 1
}

# Check if Newman is installed
try {
    $newmanVersion = newman --version
    Write-Host "✅ Newman is already installed: $newmanVersion" -ForegroundColor Green
} catch {
    Write-Host "📦 Installing Newman (Postman CLI)..." -ForegroundColor Yellow
    npm install -g newman
    npm install -g newman-reporter-html
    npm install -g newman-reporter-htmlextra
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Newman installed successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to install Newman" -ForegroundColor Red
        exit 1
    }
}

# Create results directory
Write-Host "📁 Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "postman\results" | Out-Null

# Navigate to postman directory
Set-Location "postman"

# Validate collection files
Write-Host "🔍 Validating collection files..." -ForegroundColor Yellow

$requiredFiles = @(
    "ODIN_Protocol_Collection.json",
    "ODIN_Protocol_Environment.json",
    "ODIN_Protocol_Tests.json"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✅ Found: $file" -ForegroundColor Green
        
        # Validate JSON
        try {
            Get-Content $file | ConvertFrom-Json | Out-Null
            Write-Host "   ✅ JSON is valid" -ForegroundColor Green
        } catch {
            Write-Host "   ❌ JSON is invalid: $file" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "❌ Missing: $file" -ForegroundColor Red
        Write-Host "Please ensure all collection files are in the postman directory" -ForegroundColor Yellow
        exit 1
    }
}

# Create local environment setup
Write-Host "⚙️ Setting up local environment..." -ForegroundColor Yellow

$envSetup = @"
# ODIN Protocol Environment Setup
# Copy this to your environment variables or .env file

# Required Variables (Update these with your actual values)
ODIN_BASE_URL=https://api.odin-protocol.com
ODIN_API_TOKEN=your-api-token-here
SECURITY_TOKEN=your-security-token-here

# Optional Variables
ENVIRONMENT=development
RULE_SET_ID=default-rule-set
TRACE_ID_PREFIX=postman-test

# For CI/CD
NEWMAN_REPORT_PATH=./results
NEWMAN_TIMEOUT=30000
"@

$envSetup | Out-File -FilePath "environment-setup.txt" -Encoding UTF8

# Create quick test script
Write-Host "📝 Creating test scripts..." -ForegroundColor Yellow

$quickTestScript = @"
# Quick Test Script for ODIN Protocol
# Run this to test your setup

Write-Host "🧪 Running ODIN Protocol Quick Tests..." -ForegroundColor Cyan

# Set environment variables (update these first!)
`$env:ODIN_BASE_URL = "https://api.odin-protocol.com"
`$env:ODIN_API_TOKEN = "your-api-token-here"

# Run smoke tests
newman run ODIN_Protocol_Tests.json ``
    -e ODIN_Protocol_Environment.json ``
    --folder "🧪 Smoke Tests" ``
    --reporters cli,html ``
    --reporter-html-export results/smoke-test-report.html ``
    --timeout-request 10000

if (`$LASTEXITCODE -eq 0) {
    Write-Host "✅ Quick tests passed!" -ForegroundColor Green
    Write-Host "📊 View detailed report: results/smoke-test-report.html" -ForegroundColor Cyan
} else {
    Write-Host "❌ Quick tests failed" -ForegroundColor Red
    Write-Host "Check the HTML report for details" -ForegroundColor Yellow
}
"@

$quickTestScript | Out-File -FilePath "quick-test.ps1" -Encoding UTF8

# Create comprehensive test script
$fullTestScript = @"
# Full Test Suite for ODIN Protocol
# Runs all test categories with detailed reporting

param(
    [string]`$ApiToken = `$env:ODIN_API_TOKEN,
    [string]`$BaseUrl = `$env:ODIN_BASE_URL,
    [string]`$Environment = "development"
)

if (-not `$ApiToken) {
    Write-Host "❌ API Token required. Set ODIN_API_TOKEN environment variable or pass -ApiToken" -ForegroundColor Red
    exit 1
}

if (-not `$BaseUrl) {
    Write-Host "❌ Base URL required. Set ODIN_BASE_URL environment variable or pass -BaseUrl" -ForegroundColor Red
    exit 1
}

Write-Host "🚀 Running Full ODIN Protocol Test Suite..." -ForegroundColor Cyan
Write-Host "API Endpoint: `$BaseUrl" -ForegroundColor Yellow
Write-Host "Environment: `$Environment" -ForegroundColor Yellow

# Create timestamped results directory
`$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
`$resultsDir = "results/full-test-`$timestamp"
New-Item -ItemType Directory -Force -Path `$resultsDir | Out-Null

# Run comprehensive tests
newman run ODIN_Protocol_Collection.json ``
    -e ODIN_Protocol_Environment.json ``
    --env-var "odin_api_token=`$ApiToken" ``
    --env-var "odin_base_url=`$BaseUrl" ``
    --env-var "environment=`$Environment" ``
    --reporters cli,html,json ``
    --reporter-html-export "`$resultsDir/comprehensive-report.html" ``
    --reporter-json-export "`$resultsDir/results.json" ``
    --timeout-request 30000 ``
    --delay-request 100

# Run automated test suite
newman run ODIN_Protocol_Tests.json ``
    -e ODIN_Protocol_Environment.json ``
    --env-var "odin_api_token=`$ApiToken" ``
    --env-var "odin_base_url=`$BaseUrl" ``
    --reporters cli,html ``
    --reporter-html-export "`$resultsDir/automated-tests.html" ``
    --timeout-request 30000

if (`$LASTEXITCODE -eq 0) {
    Write-Host "✅ All tests completed successfully!" -ForegroundColor Green
    Write-Host "📊 Reports available in: `$resultsDir" -ForegroundColor Cyan
    Write-Host "   - comprehensive-report.html (Full API tests)" -ForegroundColor White
    Write-Host "   - automated-tests.html (Automated test suite)" -ForegroundColor White
    Write-Host "   - results.json (Machine-readable results)" -ForegroundColor White
} else {
    Write-Host "❌ Some tests failed" -ForegroundColor Red
    Write-Host "📊 Check reports in: `$resultsDir" -ForegroundColor Yellow
}
"@

$fullTestScript | Out-File -FilePath "run-full-tests.ps1" -Encoding UTF8

# Create performance benchmark script
$perfTestScript = @"
# Performance Benchmark Script for ODIN Protocol
# Validates sub-50ms response time requirements

param(
    [string]`$ApiToken = `$env:ODIN_API_TOKEN,
    [string]`$BaseUrl = `$env:ODIN_BASE_URL,
    [int]`$Duration = 300,  # Test duration in seconds
    [int]`$Concurrency = 10  # Concurrent requests
)

Write-Host "⚡ ODIN Protocol Performance Benchmark" -ForegroundColor Cyan
Write-Host "Duration: `$Duration seconds" -ForegroundColor Yellow
Write-Host "Concurrency: `$Concurrency requests" -ForegroundColor Yellow

`$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
`$resultsDir = "results/perf-test-`$timestamp"
New-Item -ItemType Directory -Force -Path `$resultsDir | Out-Null

# Run performance tests
newman run ODIN_Protocol_Tests.json ``
    -e ODIN_Protocol_Environment.json ``
    --folder "⚡ Performance Tests" ``
    --env-var "odin_api_token=`$ApiToken" ``
    --env-var "odin_base_url=`$BaseUrl" ``
    --iteration-count `$Concurrency ``
    --reporters cli,html ``
    --reporter-html-export "`$resultsDir/performance-report.html" ``
    --timeout-request 5000 ``
    --delay-request 50

Write-Host "📊 Performance test completed. Report: `$resultsDir/performance-report.html" -ForegroundColor Cyan
"@

$perfTestScript | Out-File -FilePath "run-performance-tests.ps1" -Encoding UTF8

# Create VS Code workspace settings
$vscodeSettings = @"
{
    "folders": [
        {
            "name": "ODIN Protocol Postman Plugin",
            "path": "."
        }
    ],
    "extensions": {
        "recommendations": [
            "Postman.postman-for-vscode",
            "ms-vscode.powershell"
        ]
    },
    "settings": {
        "files.associations": {
            "*.json": "json"
        },
        "powershell.integratedConsole.showOnStartup": false
    }
}
"@

$vscodeSettings | Out-File -FilePath "odin-postman.code-workspace" -Encoding UTF8

# Create batch file for easy Windows execution
$batchFile = @"
@echo off
echo 🚀 ODIN Protocol Postman Plugin - Quick Start
echo.

REM Check if PowerShell execution policy allows script execution
powershell -Command "if ((Get-ExecutionPolicy) -eq 'Restricted') { echo 'Setting PowerShell execution policy...'; Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force }"

REM Run the quick test
powershell -File quick-test.ps1

pause
"@

$batchFile | Out-File -FilePath "quick-start.bat" -Encoding ASCII

Write-Host "✅ Setup completed successfully!" -ForegroundColor Green
Write-Host "" -ForegroundColor White

Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. 🔑 Update your API credentials:" -ForegroundColor White
Write-Host "   - Edit ODIN_Protocol_Environment.json" -ForegroundColor Gray
Write-Host "   - Set 'odin_api_token' and 'odin_base_url' values" -ForegroundColor Gray
Write-Host "" -ForegroundColor White

Write-Host "2. 🧪 Run quick tests:" -ForegroundColor White
Write-Host "   - Double-click: quick-start.bat" -ForegroundColor Gray
Write-Host "   - Or run: .\quick-test.ps1" -ForegroundColor Gray
Write-Host "" -ForegroundColor White

Write-Host "3. 🚀 Run full test suite:" -ForegroundColor White
Write-Host "   - .\run-full-tests.ps1 -ApiToken 'your-token' -BaseUrl 'your-url'" -ForegroundColor Gray
Write-Host "" -ForegroundColor White

Write-Host "4. ⚡ Run performance tests:" -ForegroundColor White
Write-Host "   - .\run-performance-tests.ps1" -ForegroundColor Gray
Write-Host "" -ForegroundColor White

Write-Host "📁 Files Created:" -ForegroundColor Cyan
Write-Host "   ✅ quick-test.ps1 (Basic connectivity tests)" -ForegroundColor Green
Write-Host "   ✅ run-full-tests.ps1 (Comprehensive test suite)" -ForegroundColor Green
Write-Host "   ✅ run-performance-tests.ps1 (Performance validation)" -ForegroundColor Green
Write-Host "   ✅ quick-start.bat (Easy Windows launcher)" -ForegroundColor Green
Write-Host "   ✅ environment-setup.txt (Configuration guide)" -ForegroundColor Green
Write-Host "   ✅ odin-postman.code-workspace (VS Code workspace)" -ForegroundColor Green
Write-Host "" -ForegroundColor White

Write-Host "📚 Documentation:" -ForegroundColor Cyan
Write-Host "   📖 README.md - Complete usage guide" -ForegroundColor Gray
Write-Host "   ⚙️ environment-setup.txt - Configuration instructions" -ForegroundColor Gray
Write-Host "" -ForegroundColor White

Write-Host "🎉 Ready to test the ODIN Protocol HEL Rule System!" -ForegroundColor Green

# Return to original directory
Set-Location ".."
