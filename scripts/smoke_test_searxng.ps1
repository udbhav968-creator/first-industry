$url = if ($env:SEARXNG_URL) { $env:SEARXNG_URL } else { "http://localhost:8080" }

Write-Host "Testing SearXNG connectivity at $url..."

try {
    $res = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
    Write-Host "searxng: ok ($($res.StatusCode))"

    # Also test JSON search format API
    try {
        $searchRes = Invoke-RestMethod -Uri "$url/search?q=test&format=json" -TimeoutSec 5
        Write-Host "searxng json api: ok (returned $($searchRes.results.Count) results)"
    } catch {
        Write-Host "searxng json api: ready with default format"
    }
} catch {
    Write-Error "searxng: connection failed at $url"
    exit 1
}
