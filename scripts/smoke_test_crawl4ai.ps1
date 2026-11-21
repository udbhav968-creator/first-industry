$url = if ($env:CRAWL4AI_URL) { $env:CRAWL4AI_URL } else { "http://localhost:11235/health" }

try {
    $res = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
    Write-Host "crawl4ai: ok ($($res.StatusCode))"
} catch {
    Write-Error "crawl4ai: connection failed at $url"
    exit 1
}
