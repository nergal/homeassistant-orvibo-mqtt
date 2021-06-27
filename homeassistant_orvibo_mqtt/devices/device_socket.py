from json import dumps
from .abstract_device import AbstractDevice
import logging

_LOGGER = logging.getLogger(__name__)


class DeviceSocket(AbstractDevice):
    DISCOVERY_TOPIC = "%s/config"
    COMMAND_TOPIC = "%s/set"
    STATE_TOPIC = "%s/state"
    AVAILABILITY_TOPIC = "%s/availability"

    def get_discovery_payload(self):
        payload = {
            "name": self.name,
            "command_topic": DeviceSocket.COMMAND_TOPIC % self.topic_name,
            "state_topic": DeviceSocket.STATE_TOPIC % self.topic_name,
            "availability_topic": DeviceSocket.AVAILABILITY_TOPIC % self.topic_name,
            "unique_id": self.mac,
            "optimistic": False,
            "state_off": DeviceSocket.OFF_VALUE,
            "state_on": DeviceSocket.ON_VALUE,
            "payload_on": DeviceSocket.ON_VALUE,
            "payload_off": DeviceSocket.OFF_VALUE,
            "payload_available": DeviceSocket.ONLINE_STATE,
            "payload_not_available": DeviceSocket.OFFLINE_STATE,
            "availability_mode": "any",
            "device": {
                "manufacturer": "Orvibo",
                "model": "S20",
                "name": self.mac,
                "identifiers": self.mac,
                "via_device": "homeassistant-orvibo-mqtt"
            }
        }
        return dumps(payload)

    def destruct(self, client):
        self.send_availability(client, False)

    def send_config(self, client):
        discovery_payload = self.get_discovery_payload()
        client.publish(DeviceSocket.DISCOVERY_TOPIC %
                       self.topic_name, payload=discovery_payload)

    def send_availability(self, client, value: bool):
        payload = DeviceSocket.ONLINE_STATE if value else DeviceSocket.OFFLINE_STATE
        client.publish(DeviceSocket.AVAILABILITY_TOPIC %
                       self.topic_name, payload=payload)

    def send_state(self, client, value: bool):
        msg = DeviceSocket.ON_VALUE if value else DeviceSocket.OFF_VALUE
        client.publish(DeviceSocket.STATE_TOPIC % self.topic_name, payload=msg)

    def send_command(self, client, msg):
        if msg == DeviceSocket.ON_VALUE:
            _LOGGER.info("Change state => ON")
            self.device.on = True
            self.send_state(client, self.device.on)
        elif msg == DeviceSocket.OFF_VALUE:
            _LOGGER.info("Change state => OFF")
            self.device.on = False
            self.send_state(client, self.device.on)
        elif msg == DeviceSocket.HA_INIT_TOPIC:
            self.do_initialize(client)

    def do_initialize(self, client):
        _LOGGER.info("Send initialization info for %s (%s)" % (self.name, self.mac))
        self.send_config(client)
        self.send_availability(client, True)

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(DeviceSocket.HA_INIT_TOPIC)
        client.subscribe("%s/#" % self.topic_name)

        self.do_initialize(client)

    def on_message(self, client, userdata, msg):
        if msg.topic == DeviceSocket.COMMAND_TOPIC % self.topic_name:
            self.send_command(client, msg.payload.decode("utf-8"))
