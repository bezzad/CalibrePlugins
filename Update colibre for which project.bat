@if (@CodeSection == @Batch) @then

@echo off

rem Use %SendKeys% to send keys to the keyboard buffer
set SendKeys=CScript //nologo //E:JScript "%~F0"

title Calibre Updator

SET ca32 = "C:\Program Files (x86)\Calibre2\calibre-customize.exe"
SET ca64 = "C:\Program Files\Calibre2\calibre-customize.exe"
SET p[1]=create_sample
SET p[2]=editor
SET p[3]=indesign_to_epub_initial_settings
SET p[4]=span_garbage_collector
SET qut="
SET id=0

echo Welcome to Calibre Updator
echo.
echo.

:loop

echo Please select one calibre plugin:
echo    1. %p[1]%
echo    2. %p[2]%
echo    3. %p[3]%
echo    4. %p[4]%
echo.
SET ok=0
SET /p id="Enter id: "    

setlocal enableDelayedExpansion
SET target=!p[%id%]!

// id > 0 && id < 5 
if %id% GTR 0 if %id% LSS 5 (    
    cls
    echo Updating %target%

    echo building...
    calibre-customize -b "%target%"   
    
    start "%ca32% -b %qut%%target%%qut%"     
    %SendKeys% "exit{ENTER}"
    echo 32bit calibre updated

    start "%ca64% -b %qut%%target%%qut%"     
    %SendKeys% "exit{ENTER}"
    echo 64bit calibre updated

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
endlocal
@end

// JScript section
var WshShell = WScript.CreateObject("WScript.Shell");
WshShell.SendKeys(WScript.Arguments(0));