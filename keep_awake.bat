@echo off
REM Prevent system sleep during training
echo Preventing system sleep...
powercfg /change standby-timeout-ac 0
powercfg /change monitor-timeout-ac 30
powercfg /change hibernate-timeout-ac 0
echo Done! System will not sleep while plugged in.
echo Monitor will turn off after 30 minutes (to save power).
pause
