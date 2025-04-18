@echo off

:: Install the required packages.
pip3 install azure-search-documents==11.6.0b9 --upgrade --user %*
pip3 install colorama --upgrade --user %*
pip3 install openai --upgrade --user %*
pip3 install pandas --upgrade --user %*
pip3 install python-dotenv --upgrade --user %*
pip3 install tiktoken --upgrade --user %*

:: Create the AI generated output folder.
mkdir ..\ai_generated 2>nul

:: Create the environment variables file.
type NUL >> ..\.env
