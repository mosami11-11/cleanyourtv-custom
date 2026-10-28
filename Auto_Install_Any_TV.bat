@echo off
title CleanYourTV - One-Click Auto Installer
cd /d "%~dp0"
echo ========================================================
echo    CleanYourTV Custom Edition - Auto Installer
echo ========================================================
set /p TV_IP="Enter the new TV IP Address (e.g. 192.168.1.143): "
set TV_HOST=%TV_IP%
echo.
echo [1/5] Pushing & Installing Custom Launcher APK...
tools\venv\Scripts\python.exe -I tools\b64push.py apk\launcher-custom.apk /data/local/tmp/tvhome.apk
tools\venv\Scripts\python.exe -I tools\tv.py "pm install -r /data/local/tmp/tvhome.apk && rm /data/local/tmp/tvhome.apk"
tools\venv\Scripts\python.exe -I tools\tv.py "cmd package set-home-activity --user 0 com.gathin.tvhome/.MainActivity"
echo [2/5] Granting Spotify/Media Widget & Location Permissions...
tools\venv\Scripts\python.exe -I tools\tv.py "cmd notification allow_listener com.gathin.tvhome/com.gathin.tvhome.MediaNoteService"
tools\venv\Scripts\python.exe -I tools\tv.py "pm grant com.gathin.tvhome android.permission.ACCESS_FINE_LOCATION"
echo [3/5] Applying Custom Aurora Theme & Tile Menu...
powershell -ExecutionPolicy Bypass -File tools\theme.ps1 -TvHost %TV_IP% themes\aurora
echo [4/5] Applying Clock Screensaver & 0.5x Fast Animations...
tools\venv\Scripts\python.exe -I tools\tv.py "settings put secure screensaver_components com.gathin.tvhome/.ClockDreamService"
tools\venv\Scripts\python.exe -I tools\tv.py "settings put global window_animation_scale 0.5"
tools\venv\Scripts\python.exe -I tools\tv.py "settings put global transition_animation_scale 0.5"
tools\venv\Scripts\python.exe -I tools\tv.py "settings put global animator_duration_scale 0.5"
echo [5/5] Debloating Ads, Wallpaper & Stock Launcher...
tools\venv\Scripts\python.exe -I tools\tv.py "pm enable --user 0 com.mitv.livetv"
tools\venv\Scripts\python.exe -I tools\tv.py "pm enable --user 0 com.mitv.livetv.ci_mediatek"
tools\venv\Scripts\python.exe -I tools\tv.py "pm enable --user 0 com.xiaomi.mitv.smartshare"
tools\venv\Scripts\python.exe -I tools\tv.py "pm enable --user 0 com.xiaomi.wfdsinkhelperservice"
powershell -ExecutionPolicy Bypass -File tools\disable.ps1 -TvHost %TV_IP% examples\xiaomi-mitv-mosr4\debloat.txt
tools\venv\Scripts\python.exe -I tools\tv.py "pm disable-user --user 0 com.mitv.dream"
tools\venv\Scripts\python.exe -I tools\tv.py "pm enable --user 0 com.google.android.katniss"
tools\venv\Scripts\python.exe -I tools\tv.py "am start -a android.intent.action.MAIN -c android.intent.category.HOME"
echo.
echo ========================================================
echo    DONE! The TV is 100%% Customized & Ready!
echo ========================================================
pause
