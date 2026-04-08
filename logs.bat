@echo off
echo ============================================================
echo   Student Result System — Logging ^& Monitoring
echo ============================================================
echo.
echo Select an option:
echo   1. Live logs — Flask app
echo   2. Live logs — MySQL
echo   3. Live logs — Nginx
echo   4. Live logs — All services
echo   5. Container stats (CPU/Memory)
echo   6. Container health status
echo   7. View app log file (from volume)
echo   8. Exit
echo.
set /p choice="Enter choice [1-8]: "

IF "%choice%"=="1" (
    echo Streaming Flask logs (Ctrl+C to stop)...
    docker logs -f flask_app
)
IF "%choice%"=="2" (
    echo Streaming MySQL logs (Ctrl+C to stop)...
    docker logs -f mysql_db
)
IF "%choice%"=="3" (
    echo Streaming Nginx logs (Ctrl+C to stop)...
    docker logs -f nginx_proxy
)
IF "%choice%"=="4" (
    echo Streaming all logs (Ctrl+C to stop)...
    docker-compose logs -f
)
IF "%choice%"=="5" (
    echo Live container resource stats (Ctrl+C to stop)...
    docker stats flask_app mysql_db nginx_proxy
)
IF "%choice%"=="6" (
    echo Container health status:
    docker inspect --format="{{.Name}} — Status: {{.State.Health.Status}}" flask_app mysql_db nginx_proxy
)
IF "%choice%"=="7" (
    echo Reading app.log from volume...
    docker exec flask_app cat /app/logs/app.log
)
IF "%choice%"=="8" exit
