# Ensure the Podman VM is running
Write-Host "Checking Podman Machine..." -ForegroundColor Cyan
podman machine start

$commands = @(
    "rm -af", 
    "rmi -af", 
    "volume prune -f", 
    "network prune -f"
)

foreach ($cmd in $commands) {
    Write-Host "Running: podman $cmd" -ForegroundColor Yellow
    Invoke-Expression "podman $cmd"
}

Write-Host "Cleanup Complete! Press any key to exit..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")