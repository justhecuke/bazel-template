@echo off
set "CACHED_GH=%USERPROFILE%\.cache\bazel_template\gh\v2.103.0\gh.exe"
if exist "%CACHED_GH%" (
    "%CACHED_GH%" %*
    exit /b %ERRORLEVEL%
)
python "%~dp0gh.py" %*
