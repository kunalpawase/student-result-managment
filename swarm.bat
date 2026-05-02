@echo off
echo ============================================================
echo   Student Result System — Docker Swarm Management
echo ============================================================
echo.
echo   1. Initialize Swarm
echo   2. Deploy Stack
echo   3. List Services
echo   4. Scale Flask (5 replicas)
echo   5. View Service Logs
echo   6. Remove Stack
echo   7. Leave Swarm
echo.
set /p choice="Enter choice [1-7]: "

IF "%choice%"=="1" (
    echo Initializing Docker Swarm...
    docker swarm init
)
IF "%choice%"=="2" (
    echo Deploying stack...
    docker stack deploy -c swarm/docker-stack.yml student-result
    echo.
    echo Stack deployed. Run option 3 to check services.
)
IF "%choice%"=="3" (
    echo.
    echo === Stack Services ===
    docker stack services student-result
    echo.
    echo === Running Tasks ===
    docker stack ps student-result
)
IF "%choice%"=="4" (
    echo Scaling Flask to 5 replicas...
    docker service scale student-result_flask=5
)
IF "%choice%"=="5" (
    echo Streaming Flask service logs...
    docker service logs -f student-result_flask
)
IF "%choice%"=="6" (
    echo Removing stack...
    docker stack rm student-result
)
IF "%choice%"=="7" (
    echo Leaving swarm...
    docker swarm leave --force
)
