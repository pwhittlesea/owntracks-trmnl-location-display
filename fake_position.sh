#!/bin/bash

USERNAME=$1
PASSWORD=$2
HOST=$3
LAT=$4
LON=$5
TIME=$(date +%s)

URL="https://${USERNAME}:${PASSWORD}@${HOST}/owntrack/locations"

curl ${URL} \
    -H 'Content-Type: application/json' \
    -d "{\"tid\": \"fake\", \"batt\": 69, \"lon\": $LON, \"acc\": 7, \"bs\": 1, \"p\": 101.332, \"vac\": 30, \"lat\": $LAT, \"t\": \"u\", \"conn\": \"w\", \"tst\": $TIME, \"m\": 0, \"alt\": 57, \"_type\": \"location\"}" \
    -X POST
echo
curl ${URL} | jq .
echo
