#!/bin/bash

LINK_STATIC_IP="35.208.217.95" # Insert Static IP for link-api here as well

detect_cloud_provider() {
  if curl -s --connect-timeout 2 http://metadata.google.internal/computeMetadata/v1/instance/ -H "Metadata-Flavor: Google" >/dev/null 2>&1; then
    echo "Google Cloud"
  elif curl -s --connect-timeout 2 http://169.254.169.254/latest/meta-data/ >/dev/null 2>&1; then
    echo "AWS"
  elif curl -s --connect-timeout 2 http://169.254.169.254/metadata/v1/instance?api-version=2021-02-01 -H "Metadata: true" >/dev/null 2>&1; then
    echo "Azure"
  else
    echo "Unknown"
  fi
}

get_public_ip() {
  curl -s ifconfig.me
}

CLOUD_PROVIDER=$(detect_cloud_provider)
PUBLIC_IP=$(get_public_ip)

# Send the detected info to the Flask application
curl -X POST http://"$LINK_STATIC_IP":5001/sendinfo -H "Content-Type: application/json" -d "{\"cloud_provider\": \"$CLOUD_PROVIDER\", \"public_ip\": \"$PUBLIC_IP\"}"


curl http://"$LINK_STATIC_IP":5001/currentinfo