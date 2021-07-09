import binascii
import logging
import threading
from abc import ABC, abstractmethod

import paho.mqtt.client as mqtt

_LOGGER = logging.getLogger(__name__)


class AbstractDevice(ABC):
    ON_VALUE = "ON"
    OFF_VALUE = "OFF"
    ONLINE_STATE = "ONLINE"
    OFFLINE_STATE = "OFFLINE"

    HA_INIT_TOPIC = "homeassistant/status"

    def __init__(self, device, device_config, config):
        self.device = device
        self.name = device_config["name"]
        self.type = device_config["type"]
        self.mac = binascii.hexlify(self.device.mac).decode("utf-8")
        self.topic_name = self.get_topic_name()
        self.dry_run = config.get("dry_run", False)

        self.client = self.get_mqtt_client(config)

        _LOGGER.info(
            "New device has been initialized with topic = %s" % self.topic_name
        )

    def get_mqtt_client(self, config):
        mqtt_host = config.get("mqtt_host")
        mqtt_port = int(config.get("mqtt_port", 0))

        client = mqtt.Client(self.mac)
        client.enable_logger()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.on_disconnect = self.on_disconnect

        mqtt_username = config.get("mqtt_username")
        mqtt_password = config.get("mqtt_password")
        if mqtt_username and mqtt_password:
            _LOGGER.info("Using username(%s) and password", mqtt_username)
            client.username_pw_set(username=mqtt_username, password=mqtt_password)

        _LOGGER.info("Connecting to MQTT broker %s:%s", mqtt_host, mqtt_port)
        client.connect(mqtt_host, mqtt_port)

        return client

    def loop_forever(self):
        try:
            _LOGGER.info("Running loop in a new thread for %s", self.name)
            self.thread = threading.Thread(target=self.client.loop_forever)
            self.thread.daemon = True
            self.thread.start()
        except (KeyboardInterrupt, SystemExit):
            print("OFF")
            _LOGGER.warning("EXIT")

    def get_topic_name(self):
        return "homeassistant/%s/%s" % (self.type, self.mac)

    def on_log(self, client, userdata, level, buf):
        _LOGGER.info("[%s] %s", level, buf)

    @abstractmethod
    def on_connect(self, client, userdata, flags, rc):
        if rc != mqtt.CONNACK_ACCEPTED:
            message = "Unknown error occured during client connection"
            if rc == mqtt.CONNACK_REFUSED_PROTOCOL_VERSION:
                message = "Refused protocol version"
            elif rc == mqtt.CONNACK_REFUSED_IDENTIFIER_REJECTED:
                message = "Identifier rejected"
            elif rc == mqtt.CONNACK_REFUSED_SERVER_UNAVAILABLE:
                message = "Server unavailable"
            elif rc == mqtt.CONNACK_REFUSED_BAD_USERNAME_PASSWORD:
                message = "Bad username or password"
            elif rc == mqtt.CONNACK_REFUSED_NOT_AUTHORIZED:
                message = "User is not authorized"

            _LOGGER.error("MQTT[code=%d] - %s", rc, message)

    @abstractmethod
    def on_message(self, client, userdata, msg):
        pass

    @abstractmethod
    def on_disconnect(self, client, userdata, rc):
        pass
