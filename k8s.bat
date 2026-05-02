@echo off
echo ============================================================
echo   Student Result System — Kubernetes Management
echo ============================================================
echo.
echo   1. Deploy all (apply all manifests)
echo   2. Check pod status
echo   3. Check services
echo   4. View Flask logs
echo   5. Scale Flask manually
echo   6. Check HPA (autoscaler)
echo   7. Delete all resources
echo.
set /p choice="Enter choice [1-7]: "

IF "%choice%"=="1" (
    echo Deploying to Kubernetes...
    kubectl apply -f k8s/namespace.yml
    kubectl apply -f k8s/secret.yml
    kubectl apply -f k8s/mysql-pvc.yml
    kubectl apply -f k8s/mysql-deployment.yml
    kubectl apply -f k8s/flask-deployment.yml
    kubectl apply -f k8s/nginx-deployment.yml
    kubectl apply -f k8s/flask-hpa.yml
    echo.
    echo All resources applied. Run option 2 to check pods.
)
IF "%choice%"=="2" (
    echo.
    echo === Pods ===
    kubectl get pods -n student-result
    echo.
    echo === Deployments ===
    kubectl get deployments -n student-result
)
IF "%choice%"=="3" (
    echo.
    echo === Services ===
    kubectl get services -n student-result
)
IF "%choice%"=="4" (
    echo Streaming Flask pod logs...
    kubectl logs -f -l app=flask -n student-result
)
IF "%choice%"=="5" (
    set /p replicas="Enter number of Flask replicas: "
    kubectl scale deployment flask --replicas=%replicas% -n student-result
)
IF "%choice%"=="6" (
    kubectl get hpa -n student-result
)
IF "%choice%"=="7" (
    echo Deleting all resources...
    kubectl delete namespace student-result
)
