#!/usr/bin/env bashio

bashio::log.info "Running Orvibo daemon..."
python3 /app/daemon.py -f /data/config.json