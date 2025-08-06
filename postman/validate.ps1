Write-Host "ODIN Protocol Collection Test" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Testing collection syntax and structure..." -ForegroundColor Yellow

# First, let's validate the JSON structure
try {
    Get-Content "ODIN_Protocol_Collection.json" | ConvertFrom-Json | Out-Null
    Write-Host "✅ Collection JSON is valid" -ForegroundColor Green
} catch {
    Write-Host "❌ Collection JSON is invalid" -ForegroundColor Red
    exit 1
}

try {
    Get-Content "ODIN_Protocol_Environment.json" | ConvertFrom-Json | Out-Null
    Write-Host "✅ Environment JSON is valid" -ForegroundColor Green
} catch {
    Write-Host "❌ Environment JSON is invalid" -ForegroundColor Red
    exit 1
}

try {
    Get-Content "ODIN_Protocol_Tests.json" | ConvertFrom-Json | Out-Null
    Write-Host "✅ Tests JSON is valid" -ForegroundColor Green
} catch {
    Write-Host "❌ Tests JSON is invalid" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Testing with Newman (this will show errors due to demo endpoints)..." -ForegroundColor Yellow

# Run a basic test to validate collection structure
newman run ODIN_Protocol_Tests.json -e ODIN_Protocol_Environment.json --env-var "odin_api_token=demo-token" --env-var "odin_base_url=https://httpbin.org" --timeout-request 3000 --bail

Write-Host ""
Write-Host "✅ Collection structure validation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "The collection is properly formatted and ready to use." -ForegroundColor White
Write-Host "To test with real ODIN Protocol API:" -ForegroundColor White
Write-Host "1. Get your API token from ODIN Protocol" -ForegroundColor Gray
Write-Host "2. Edit test.ps1 with your credentials" -ForegroundColor Gray
Write-Host "3. Run: .\test.ps1" -ForegroundColor Gray
