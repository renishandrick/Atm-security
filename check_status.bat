@echo off
REM Quick training status checker

setlocal enabledelayedexpansion

echo.
echo ========== ATM SECURITY TRAINING STATUS ==========
echo.

REM Check if best.pt exists
if exist "runs\detect\atm_final\exp1\weights\best.pt" (
    echo [SUCCESS] Training COMPLETED!
    echo Best model saved: runs\detect\atm_final\exp1\weights\best.pt
    echo.
    echo Next steps:
    echo   1. copy runs\detect\atm_final\exp1\weights\best.pt models\
    echo   2. python inference.py --webcam
    goto end
)

REM Check if results.csv exists
if exist "runs\detect\atm_final\exp1\results.csv" (
    echo [IN PROGRESS] Training is running...
    echo.
    for /f "tokens=*" %%a in ('powershell -NoProfile -Command "^$csv = @(Import-Csv 'runs\detect\atm_final\exp1\results.csv'); ^$last = ^$csv[-1]; Write-Host \"Epoch: ^$([int][float]^$last.Epoch + 1)/100\""') do (
        echo %%a
    )
    echo.
    echo Check again in 30 minutes...
) else (
    if exist "runs\detect\atm_final" (
        echo [STARTING] Training folder exists but results not ready yet
        echo Please wait a few minutes for data to be written...
    ) else (
        echo [NOT STARTED] Training hasn't started yet
        echo Run: python train_minimal.py
    )
)

:end
echo.
echo ====================================================
echo.
pause
