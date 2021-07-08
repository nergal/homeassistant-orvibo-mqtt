#!/usr/bin/env bashio
set -e

bashio::log.info "Creating Orvibo configuration..."

CONFIG="/app/config.yaml"

MQTT_HOST=$(bashio::services mqtt "host")
MQTT_PORT=$(bashio::services mqtt "port")
MQTT_USERNAME=$(bashio::services mqtt "username")
MQTT_PASSWORD=$(bashio::services mqtt "password")

{
    echo "mqtt_host: ${MQTT_HOST}"
    echo "mqtt_port: ${MQTT_PORT}"
    echo "mqtt_username: ${MQTT_USERNAME}"
    echo "mqtt_password: ${MQTT_PASSWORD}"
    echo "devices:"
} > "${CONFIG}"

for device in $(bashio::config 'devices|keys'); do
    DEVICE_IP=$(bashio::config "devices[${device}].ip")
    DEVICE_TYPE=$(bashio::config "devices[${device}].type")
    DEVICE_NAME=$(bashio::config "devices[${device}].name")

    {
        echo "  - ip: ${DEVICE_IP}"
        echo "    type: ${DEVICE_TYPE}"
        echo "    name: ${DEVICE_NAME}"
    } >> "${CONFIG}"
done

bashio::log.info "Running Orvibo daemon..."
cd /app
python3 /app/daemon.py