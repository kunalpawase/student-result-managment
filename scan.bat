@echo off
echo ============================================================
echo   Student Result System — Image Scan ^& Verification
echo ============================================================

REM Build the image first
echo [1/4] Building Docker image...
docker build -t student-result-flask:latest .

REM Check if Trivy is installed
where trivy >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [INFO] Trivy not found locally. Running via Docker...
    SET TRIVY_CMD=docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy
) ELSE (
    SET TRIVY_CMD=trivy
)

REM Scan image for vulnerabilities
echo.
echo [2/4] Scanning image for vulnerabilities...
%TRIVY_CMD% image --severity HIGH,CRITICAL student-result-flask:latest

REM Scan filesystem for secrets
echo.
echo [3/4] Scanning source code for secrets...
%TRIVY_CMD% fs --scanners secret .

REM Scan for misconfigurations
echo.
echo [4/4] Scanning Dockerfile and Compose for misconfigurations...
%TRIVY_CMD% config .

echo.
echo ============================================================
echo   Scan Complete
echo ============================================================
