#!/usr/bin/env bash

# Install py venv
ENV_DIR=".venv"

# if .venv doesnt exist, install
if [[ ! -e "$ENV_DIR" ]]; then
    echo Setting up virtual environment... 
    echo `python3 -m venv .venv`
    echo Installing packages... 
    echo `pip install -r requirements.txt`
    echo Done. 
    echo _____________________________________________
    echo  
fi

echo "Enter OpenRouter API Key:"

read API_KEY

while [[ -z "$API_KEY" ]]; do 
    echo "Nope. Enter API key:"
    read API_KEY 
done

export OPEN_ROUTER_API_KEY="$API_KEY"

echo "Stored as environment variable: OPEN_ROUTER_API_KEY 🗣️🔑"