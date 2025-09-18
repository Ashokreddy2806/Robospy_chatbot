Set-Location "C:\project-robopsy"

& "C:\project-robopsy\venv\Scripts\Activate.ps1"

Set-Location "C:\project-robopsy\RobopsyApp"

Start-Process -NoNewWindow -FilePath "python" -ArgumentList "manage.py runserver 0.0.0.0:8000"

Start-Sleep -Seconds 5

Start-Process "C:\Program Files\Mozilla Firefox\firefox.exe" -ArgumentList "--kiosk http://localhost:8000"