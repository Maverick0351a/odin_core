# ODIN Protocol Demo Test
# This will test the collection structure without hitting real APIs

Write-Host "🧪 ODIN Protocol Postman Plugin Demo Test" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Test with mock/demo endpoints first
$demoApiToken = "demo-token-12345"
$demoBaseUrl = "https://httpbin.org"  # Public testing API

Write-Host ""
Write-Host "Testing collection structure..." -ForegroundColor Yellow
Write-Host "Demo API: $demoBaseUrl" -ForegroundColor Gray
Write-Host ""

# Run a basic structure test
newman run ODIN_Protocol_Tests.json `
    -e ODIN_Protocol_Environment.json `
    --env-var "odin_api_token=$demoApiToken" `
    --env-var "odin_base_url=$demoBaseUrl" `
    --reporters cli,html `
    --reporter-html-export results/demo-test-report.html `
    --timeout-request 5000 `
    --ignore-redirects `
    --bail

Write-Host ""
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Collection structure is valid!" -ForegroundColor Green
} else {
    Write-Host "ℹ️ Expected - some tests will fail with demo endpoints" -ForegroundColor Yellow
    Write-Host "   The important thing is that the collection loads properly" -ForegroundColor Gray
}

Write-Host ""
Write-Host "📊 Demo test report generated: results/demo-test-report.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔧 Next steps for real testing:" -ForegroundColor White
Write-Host "1. Get your ODIN Protocol API token" -ForegroundColor Gray
Write-Host "2. Edit test.ps1 with real credentials" -ForegroundColor Gray
Write-Host "3. Run: .\test.ps1" -ForegroundColor Gray
