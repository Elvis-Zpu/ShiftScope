Set-Location F:\mission_J\ShiftScope

Write-Host "Stopping Docker services..."
docker compose -f infra/docker-compose.yml down

Write-Host "Done. You can close backend and worker windows manually if they are still open."