Write-Host "ODIN Protocol Demo Test" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan

$demoApiToken = "demo-token-12345"
$demoBaseUrl = "https://httpbin.org"

Write-Host ""
Write-Host "Testing collection structure..." -ForegroundColor Yellow
Write-Host "Demo API: $demoBaseUrl" -ForegroundColor Gray
Write-Host ""

newman run ODIN_Protocol_Tests.json -e ODIN_Protocol_Environment.json --env-var "odin_api_token=$demoApiToken" --env-var "odin_base_url=$demoBaseUrl" --reporters cli,html --reporter-html-export results/demo-test-report.html --timeout-request 5000 --ignore-redirects --bail

Write-Host ""
if ($LASTEXITCODE -eq 0) {
    Write-Host "Collection structure is valid!" -ForegroundColor Green
} else {
    Write-Host "Expected - some tests will fail with demo endpoints" -ForegroundColor Yellow
    Write-Host "The important thing is that the collection loads properly" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Demo test report: results/demo-test-report.html" -ForegroundColor Cyan
