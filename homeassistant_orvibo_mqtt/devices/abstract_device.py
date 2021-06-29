from abc import ABC, abstractmethod
import binascii
import paho.mqtt.client as mqtt
import logging
import threading

_LOGGER = logging.getLogger(__name__)


class AbstractDevice(ABC):
    ON_VALUE = 'ON'
    OFF_VALUE = 'OFF'
    ONLINE_STATE = 'ONLINE'
    OFFLINE_STATE = 'OFFLINE'

    HA_INIT_TOPIC = "homeassistant/status"

    def __init__(self, device, device_config, config):
        self.device = device
        self.name = device_config['name']
        self.type = device_config['type']
        self.mac = binascii.hexlify(self.device.mac).decode("utf-8")
        self.topic_name = self.get_topic_name()

        self.client = self.get_mqtt_client(config)

        _LOGGER.info(
            "New device has been initialized with topic = %s" % self.topic_name)

    def get_mqtt_client(self, config):
        mqtt_host = config['mqtt_host'].get()
        mqtt_port = config['mqtt_port'].get(int)

        client = mqtt.Client(self.mac)
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        client.connect(mqtt_host, mqtt_port)

        return client

    def loop_forever(self):
        try:
            self.thread = threading.Thread(target=self.client.loop_forever)
            self.thread.daemon=True
            self.thread.start()
        except (KeyboardInterrupt, SystemExit):
            print("OFF")
            _LOGGER.warning("EXIT")

    def get_topic_name(self):
        return "homeassistant/%s/%s" % (self.type, self.mac)

    @abstractmethod
    def on_connect(self, client, userdata, flags, rc):
        pass

    @abstractmethod
    def on_message(self, client, userdata, msg):
        pass
