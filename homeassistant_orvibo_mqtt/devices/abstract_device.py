from abc import ABC, abstractmethod
import binascii
import logging

_LOGGER = logging.getLogger(__name__)


class AbstractDevice(ABC):
    ON_VALUE = 'ON'
    OFF_VALUE = 'OFF'
    ONLINE_STATE = 'ONLINE'
    OFFLINE_STATE = 'OFFLINE'

    def __init__(self, device, type, name):
        self.name = name
        self.device = device
        self.type = type
        self.mac = binascii.hexlify(self.device.mac).decode("utf-8")
        self.topic_name = self.getTopicName()

        _LOGGER.info(
            "New device has been initialized with topic = %s" % self.topic_name)

    def getTopicName(self):
        return "homeassistant/%s/%s" % (self.type, self.mac)

    @abstractmethod
    def on_connect(self, client, userdata, flags, rc):
        pass

    @abstractmethod
    def on_message(self, client, userdata, msg):
        pass

    def destruct(self, client):
        pass
