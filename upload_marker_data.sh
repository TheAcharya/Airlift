#!/bin/sh

TOOL_PATH="/Users/xxx/Documents/CLI-Tools/Airlift/airlift"
AIRTABLE_TOKEN="patXVc95JdObwXbq3.a29732e3707027e8f70280982392d8d132d86354e0301986ecbb659376f7f5cc"
AIRTABLE_BASE="appZWICeticRVXJZp"
AIRTABLE_TABLE="tbl3802eSi3WsFCyk"
DROPBOX_TOKEN="/Users/xxx/Documents/CLI-Tools/Airlift/dropbox-token.json"
UPLOAD_PAYLOAD="/Users/xxx/Desktop/Marker_Data/App/CLI/Output/Marker Data Demo_V2 2023-12-01 07-25-12/Marker Data Demo_V2.json"
UPLOAD_LOG="/Users/xxx/Documents/CLI-Tools/Airlift/log.txt"

$TOOL_PATH --token $AIRTABLE_TOKEN --base $AIRTABLE_BASE --table $AIRTABLE_TABLE --dropbox-token $DROPBOX_TOKEN --attachment-columns-map "Image Filename" "Attachments" --md --log $UPLOAD_LOG --verbose "$UPLOAD_PAYLOAD"