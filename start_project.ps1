Set-Location F:\mission_J\ShiftScope

Write-Host "Starting Docker services..."
docker compose -f infra/docker-compose.yml up -d

Write-Host "Opening backend server..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd F:\mission_J\ShiftScope\backend; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload"

Write-Host "Opening Celery worker..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd F:\mission_J\ShiftScope\backend; .\.venv\Scripts\Activate.ps1; celery -A app.workers.celery_app.celery_app worker --loglevel=info -P solo"