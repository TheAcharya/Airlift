#!/bin/bash

# Get the directory of the script
script_directory="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Prompt user for app_key
read -p "Enter your Dropbox App key: " app_key_value

# Create JSON content
json_content="{\"app_key\": \"$app_key_value\"}"

# Save JSON content to file in the script's directory
echo $json_content > "$script_directory/dropbox-token.json"

echo "JSON file '$script_directory/dropbox-token.json' has been created with the following content:"
cat "$script_directory/dropbox-token.json"
