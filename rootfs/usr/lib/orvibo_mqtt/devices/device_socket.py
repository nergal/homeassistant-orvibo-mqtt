import logging
from json import dumps

from .abstract_device import AbstractDevice

_LOGGER = logging.getLogger(__name__)


class DeviceSocket(AbstractDevice):
    DISCOVERY_TOPIC = "%s/config"
    COMMAND_TOPIC = "%s/set"
    STATE_TOPIC = "%s/state"
    AVAILABILITY_TOPIC = "%s/availability"

    def get_discovery_payload(self):
        payload = {
            "name": self.name,
            "command_topic": self.COMMAND_TOPIC % self.topic_name,
            "state_topic": self.STATE_TOPIC % self.topic_name,
            "availability_topic": self.AVAILABILITY_TOPIC % self.topic_name,
            "unique_id": self.mac,
            "optimistic": False,
            "state_off": self.OFF_VALUE,
            "state_on": self.ON_VALUE,
            "payload_on": self.ON_VALUE,
            "payload_off": self.OFF_VALUE,
            "payload_available": self.ONLINE_STATE,
            "payload_not_available": self.OFFLINE_STATE,
            "availability_mode": "any",
            "device": {
                "manufacturer": "Orvibo",
                "model": "S20",
                "name": self.mac,
                "identifiers": self.mac,
                "via_device": "homeassistant-orvibo-mqtt",
            },
        }
        return dumps(payload)

    def send_config(self, client):
        discovery_payload = self.get_discovery_payload()
        client.publish(
            self.DISCOVERY_TOPIC % self.topic_name, payload=discovery_payload
        )

    def send_availability(self, client, value: bool):
        payload = self.ONLINE_STATE if value else self.OFFLINE_STATE
        client.publish(self.AVAILABILITY_TOPIC % self.topic_name, payload=payload)

    def send_state(self, client, value: bool):
        msg = self.ON_VALUE if value else self.OFF_VALUE
        client.publish(DeviceSocket.STATE_TOPIC % self.topic_name, payload=msg)

    def send_command(self, client, msg):
        if msg == self.ON_VALUE:
            _LOGGER.debug("Change state => ON")
            self.device.on = True
            self.send_state(client, self.device.on)
        elif msg == self.OFF_VALUE:
            _LOGGER.debug("Change state => OFF")
            self.device.on = False
            self.send_state(client, self.device.on)
        elif msg == self.HA_INIT_TOPIC:
            self.do_initialize(client, True)

    def do_initialize(self, client, ha_init=False):
        _LOGGER.info(
            "Send initialization info for %s (%s) because of %s",
            self.name,
            self.mac,
            "HA Config event" if ha_init else "addon start",
        )
        self.send_config(client)
        self.send_availability(client, True)

    def on_connect(self, client, userdata, flags, rc):
        super().on_connect(client, userdata, flags, rc)

        client.subscribe(self.HA_INIT_TOPIC)
        client.subscribe("%s/#" % self.topic_name)

        self.do_initialize(client)

    def on_message(self, client, userdata, msg):
        if msg.topic == self.COMMAND_TOPIC % self.topic_name:
            self.send_command(client, msg.payload.decode("utf-8"))

    def on_disconnect(self, client, userdata, rc):
        self.send_availability(client, False)
