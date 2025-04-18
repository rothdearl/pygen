@echo off

:: Store variables locally.
setlocal

set command=py

:: Check if the "py" command exists.
where %command% >nul 2>&1

:: If it does not exist, set it to "python".
if %errorlevel% neq 0 (
    set command=python
)

:: Set the JIRA ticket field.
set field=description

:: Run with options.
%command% ..\pygen.py --field %field% --log-level debug --split --no-test-cases --helper-methods 15 %*
