#!/usr/bin/env bashio

## Config
bashio::log.info "Building daemon configuration..."

if ! bashio::services.available "mqtt"; then
    bashio::exit.nok "No internal MQTT service found and no MQTT server defined. Please install Mosquitto broker or specify your own."
else
    bashio::log.info "MQTT available, fetching server detail ..."

    HASSIO_UI_CONFIG_PATH=/data/options.json
    DAEMON_CONFIG_PATH=/data/configuration.json

    MQTT_HOST=$(bashio::services "mqtt" "host")
    MQTT_PORT=$(bashio::services "mqtt" "port")
    MQTT_USERNAME=$(bashio::services "mqtt" "username")
    MQTT_PASSWORD=$(bashio::services "mqtt" "password")

    if bashio::var.has_value "${MQTT_HOST}" && bashio::var.has_value "${MQTT_PORT}"; then
        bashio::log.info "MQTT server settings not configured, trying to auto-discovering ..."
        bashio::log.info "Configuring '$MQTT_HOST:$MQTT_PORT' mqtt server"
    fi

    if bashio::var.has_value "${MQTT_USERNAME}" && bashio::var.has_value "${MQTT_PASSWORD}"; then
        bashio::log.info "MQTT credentials not configured, trying to auto-discovering ..."
        bashio::log.info "Configuring '$MQTT_USERNAME' mqtt user"
    fi

    bashio::log.info "Adjusting Orvibo MQTT core JSON config with add-on quirks ..."
    cat "$HASSIO_UI_CONFIG_PATH" \
        | MQTT_USERNAME="$MQTT_USERNAME"  jq '.mqtt_username=env.MQTT_USERNAME' \
        | MQTT_PASSWORD="$MQTT_PASSWORD" jq '.mqtt_password=env.MQTT_PASSWORD' \
        | MQTT_HOST="$MQTT_HOST" jq '.mqtt_host=env.MQTT_HOST' \
        | MQTT_PORT="$MQTT_PORT" jq '.mqtt_port=env.MQTT_PORT' \
        > $DAEMON_CONFIG_PATH

    ## Execution
    bashio::log.info "Running Orvibo daemon..."
    python3 /usr/lib/orvibo_mqtt_daemon.py --config=$DAEMON_CONFIG_PATH
fi
