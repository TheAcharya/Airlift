#!/bin/sh

TOOL_PATH="poetry run airlift"
AIRTABLE_TOKEN="patGhcvvRkgwlYzGO.ce7ce38079dbfcf21c0d4290e94dcea69b253aeb37750224a0010949f0fbdc58"
AIRTABLE_BASE="appaBjSPop4XTLth0"
AIRTABLE_TABLE="tbltopx43vvzGFwNo"
DROPBOX_TOKEN="dropbox_token.json"
UPLOAD_PAYLOAD="Demo/big_cats.csv"
UPLOAD_LOG="log.txt"

$TOOL_PATH --token $AIRTABLE_TOKEN --base $AIRTABLE_BASE --table $AIRTABLE_TABLE --dropbox-token $DROPBOX_TOKEN --attachment-columns "Image Filename" --md --log $UPLOAD_LOG --disable-bypass-column-creation --verbose "$UPLOAD_PAYLOAD"