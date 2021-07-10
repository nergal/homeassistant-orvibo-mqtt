import logging
from json import dumps

from .abstract_device import AbstractDevice
from .commands import IRCommands
from .commands.climate_commands import ClimateCommands

_LOGGER = logging.getLogger(__name__)


class DeviceClimate(AbstractDevice):
    AVAILABILITY_TOPIC = "%s/availability"
    DISCOVERY_TOPIC = "%s/config"
    STATS_TOPIC = "%s/properties"
    TEMPERATURE_TOPIC = "%s/properties/targetTemperature"
    FAN_TOPIC = "%s/properties/fanMode"
    MODE_TOPIC = "%s/properties/mode"
    SWING_TOPIC = "%s/properties/swing"

    def __init__(self, device, device_config, config):
        super().__init__(device, device_config, config)
        if "commands_set" in device_config:
            commands_transpiller = ClimateCommands()
            self.ir_commands = IRCommands(
                device_config["commands_set"], commands_transpiller
            )
        else:
            raise ConnectionRefusedError(
                "Configuration was not provided for irda device"
            )

    def get_discovery_payload(self):
        payload = {
            "name": self.name,
            "unique_id": self.mac,
            "payload_on": self.ON_VALUE,
            "payload_off": self.OFF_VALUE,
            "payload_available": self.ONLINE_STATE,
            "payload_not_available": self.OFFLINE_STATE,
            "availability_topic": self.AVAILABILITY_TOPIC % self.topic_name,
            "action_topic": self.STATS_TOPIC % self.topic_name,
            "action_template": "{{value_json.action}}",
            "temperature_command_topic": self.TEMPERATURE_TOPIC % self.topic_name,
            "mode_command_topic": self.MODE_TOPIC % self.topic_name,
            "mode_state_topic": self.STATS_TOPIC % self.topic_name,
            "mode_state_template": "{{value_json.mode}}",
            "modes": [
                ClimateCommands.MODE_AUTO,
                ClimateCommands.MODE_OFF,
                ClimateCommands.MODE_COOL,
                ClimateCommands.MODE_HEAT,
                ClimateCommands.MODE_DRY,
                ClimateCommands.MODE_FAN,
            ],
            "current_temperature_topic": self.STATS_TOPIC % self.topic_name,
            "current_temperature_template": "{{value_json.temperature}}",
            "fan_mode_command_topic": self.FAN_TOPIC % self.topic_name,
            "fan_mode_state_topic": self.STATS_TOPIC % self.topic_name,
            "fan_mode_state_template": "{{value_json.fanMode}}",
            "fan_modes": [
                ClimateCommands.FAN_AUTO,
                ClimateCommands.FAN_LOW,
                ClimateCommands.FAN_MEDIUM,
                ClimateCommands.FAN_HIGH,
            ],
            "swing_mode_command_topic": self.SWING_TOPIC % self.topic_name,
            "swing_mode_state_template": "{{value_json.swing}}",
            "swing_mode_state_topic": self.STATS_TOPIC % self.topic_name,
            "swing_modes": [ClimateCommands.SWING_ON, ClimateCommands.SWING_OFF],
            "min_temp": ClimateCommands.MIN_TEMPERATURE,
            "max_temp": ClimateCommands.MAX_TEMPERATURE,
            "temp_step": 1,
            "availability_mode": "any",
            "temperature_unit": "C",
            "device": {
                "manufacturer": "Orvibo",
                "model": "AllOne",
                "name": self.mac,
                "identifiers": self.mac,
                "via_device": "homeassistant-orvibo-mqtt",
            },
        }
        return dumps(payload)

    def on_connect(self, client, userdata, flags, rc):
        super().on_connect(client, userdata, flags, rc)

        if client.is_connected():
            client.subscribe(self.HA_INIT_TOPIC)
            client.subscribe("%s/#" % self.topic_name)
            self.do_initialize(client)
        else:
            _LOGGER.warning("There is no connection can be used to send init strings")

    def on_message(self, client, userdata, msg):
        if msg.topic == self.MODE_TOPIC % self.topic_name:
            self.update_state(client, {"mode": msg.payload.decode("utf-8")})
        elif msg.topic == self.TEMPERATURE_TOPIC % self.topic_name:
            t_value = int(float(msg.payload.decode("utf-8")))
            self.update_state(client, {"temperature": t_value})
        elif msg.topic == self.FAN_TOPIC % self.topic_name:
            self.update_state(client, {"fanMode": msg.payload.decode("utf-8")})
        elif msg.topic == self.SWING_TOPIC % self.topic_name:
            self.update_state(client, {"swing": msg.payload.decode("utf-8")})
        elif msg.topic == self.HA_INIT_TOPIC:
            self.do_initialize(client, True)

        _LOGGER.debug("Message received-> %s %s", msg.topic, str(msg.payload))

    def send_ir_signal(self, ir_command):
        signal = self.ir_commands.resolve(ir_command)
        if signal:
            _LOGGER.info("Executing command %s", ir_command)
            _LOGGER.debug("Payload for the command %s = %s", ir_command, signal.hex())
            if not self.dry_run:
                self.device.emit_ir(signal)
            else:
                _LOGGER.error(
                    "!!! \U0001F6A8 !!! You are in dry run mode, any of commands won't be emitted by IR device"
                )

    def do_initialize(self, client, ha_init=False):
        _LOGGER.info(
            "Send initialization info for %s (%s) because of %s",
            self.name,
            self.mac,
            "HA Config event" if ha_init else "addon start",
        )
        self.send_config(client)
        self.send_availability(client, True)
        self.send_stats(client)

    def update_state(self, client, updates: dict):
        command = self.ir_commands.get(updates)
        self.send_ir_signal(command)
        self.send_stats(client)

    def send_config(self, client):
        discovery_payload = self.get_discovery_payload()
        client.publish(
            self.DISCOVERY_TOPIC % self.topic_name, payload=discovery_payload
        )

    def send_stats(self, client):
        state = self.ir_commands.get_state()
        client.publish(self.STATS_TOPIC % self.topic_name, payload=dumps(state))

    def send_availability(self, client, value: bool):
        payload = self.ONLINE_STATE if value else self.OFFLINE_STATE
        client.publish(self.AVAILABILITY_TOPIC % self.topic_name, payload=payload)

    def on_disconnect(self, client, userdata, rc):
        self.send_availability(client, False)
