$port = 9222
$chromePath = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
$userDataDir = "C:\chrome-debug"

try {
    Invoke-WebRequest -Uri "http://localhost:$port/json" -TimeoutSec 3 | Out-Null
    Write-Output "Chrome debug port already running."
    exit 0
} catch {}

Stop-Process -Name chrome -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Start-Process $chromePath -ArgumentList @(
    "--remote-debugging-port=$port",
    "--user-data-dir=$userDataDir"
)

$elapsed = 0
while ($elapsed -lt 15) {
    Start-Sleep -Seconds 2
    $elapsed += 2
    try {
        Invoke-WebRequest -Uri "http://localhost:$port/json" -TimeoutSec 3 | Out-Null
        Write-Output "Chrome ready."
        exit 0
    } catch {}
}

Write-Output "Chrome startup timeout."
exit 1
