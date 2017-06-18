@echo off
title Calibre Updator

SET p1=create_sample
SET p2=editor
SET p3=indesign_to_epub_initial_settings
SET p4=span garbage collector
SET qut="
SET id=0

echo Welcome to Calibre Updator
echo.
echo.
:loop
echo Please select one calibre plugin:
echo    1. %p1%
echo    2. %p2%
echo    3. %p3%
echo    4. %p4%
echo.
SET /p id="Enter id: "    

SET ok=0

if %id% == 1 (
    echo Updating %p1%
    calibre-customize -b %qut%%p1%%qut%
    set ok=1
)

if %id% == 2 (
    echo Updating %p2%
    calibre-customize -b %qut%%p2%%qut%
    set ok=1
)

if %id% == 3 (
    echo Updating %p3%
    calibre-customize -b %qut%%p3%%qut%
    set ok=1
)

if %id% == 4 (
    echo Updating %p4%
    calibre-customize -b %qut%%p4%%qut%
    set ok=1
)

if %ok% == 0 (
    echo.
    echo your entry id must between 1 and 4
)
if %ok% == 1 (
    echo.    
    echo The plugin updated successfully.
)

pause
cls
goto loop