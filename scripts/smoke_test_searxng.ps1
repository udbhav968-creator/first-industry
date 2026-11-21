$url = if ($env:SEARXNG_URL) { $env:SEARXNG_URL } else { "http://localhost:8080" }

try {
    $res = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
    Write-Host "searxng: ok ($($res.StatusCode))"
} catch {
    Write-Error "searxng: connection failed at $url"
    exit 1
}
