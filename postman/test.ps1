# ODIN Protocol Quick Test
# Update the variables below with your actual credentials

$apiToken = "your-api-token-here"
$baseUrl = "https://api.odin-protocol.com"

Write-Host "ODIN Protocol Quick Test" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan

if ($apiToken -eq "your-api-token-here") {
    Write-Host ""
    Write-Host "Please update your API credentials first!" -ForegroundColor Yellow
    Write-Host "Edit this file (test.ps1) and set:" -ForegroundColor White
    Write-Host "- apiToken = 'your-actual-token'" -ForegroundColor Gray
    Write-Host "- baseUrl = 'your-api-endpoint'" -ForegroundColor Gray
    Write-Host ""
    exit 1
}

Write-Host "Running ODIN Protocol tests..." -ForegroundColor Yellow
Write-Host "API Endpoint: $baseUrl" -ForegroundColor Gray
Write-Host ""

# Run the test suite
newman run ODIN_Protocol_Tests.json `
    -e ODIN_Protocol_Environment.json `
    --env-var "odin_api_token=$apiToken" `
    --env-var "odin_base_url=$baseUrl" `
    --reporters cli,html `
    --reporter-html-export results/test-report.html `
    --timeout-request 10000

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Tests completed successfully!" -ForegroundColor Green
    Write-Host "View detailed report: results/test-report.html" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "Some tests failed. Check the report for details." -ForegroundColor Red
}
