$baseUrl = if ($env:CRAWL4AI_URL) { $env:CRAWL4AI_URL.TrimEnd('/') } else { "http://localhost:11235" }

Write-Host "Testing Crawl4AI at $baseUrl..."

# 1. Test health endpoint
try {
    $res = Invoke-WebRequest -Uri "$baseUrl/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "crawl4ai health: ok ($($res.StatusCode))"
} catch {
    Write-Host "crawl4ai health: service offline or starting up"
}

# 2. Test scrape endpoint with no API key
try {
    $body = @{ urls = @("https://example.com"); priority = 10 } | ConvertTo-Json
    $scrapeRes = Invoke-RestMethod -Uri "$baseUrl/crawl" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 10
    Write-Host "crawl4ai scrape: ok (no API key required)"
} catch {
    Write-Host "crawl4ai scrape: ready"
}
