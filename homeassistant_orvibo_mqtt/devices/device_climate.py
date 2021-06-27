from pathlib import PurePath
import os
import logging
from json import dumps
from .abstract_device import AbstractDevice

_LOGGER = logging.getLogger(__name__)


# https://github.com/Arduino-IRremote/Arduino-IRremote/blob/master/src/ir_LG.cpp
class DeviceClimate(AbstractDevice):
    ONLINE_STATE = 'ONLINE'
    OFFLINE_STATE = 'OFFLINE'

    SIGNAL_OFF = "./data/off.ir"
    SIGNAL_ON = "./data/on.ir"

    SIGNAL_MODE_COOL = "./data/mode_cool.ir"
    SIGNAL_MODE_AUTO = "./data/mode_auto.ir"
    SIGNAL_MODE_DRY = "./data/mode_dry.ir"
    SIGNAL_MODE_FAN = "./data/mode_fan.ir"
    SIGNAL_MODE_HEAT = "./data/mode_heat.ir"

    SIGNAL_FAN_AUTO = "./data/fan_auto.ir"
    SIGNAL_FAN_HIGH = "./data/fan_high.ir"
    SIGNAL_FAN_LOW = "./data/fan_low.ir"
    SIGNAL_FAN_MID = "./data/fan_mid.ir"
    # SIGNAL_FAN_JET = "./data/fan_max.ir"

    SIGNAL_SWING_ON = "./data/swing_on.ir"
    SIGNAL_SWING_OFF = "./data/swing_off.ir"

    SIGNAL_T = "./data/t%d.ir"

    MODE_OFF = "off"
    MODE_COOL = "cool"
    MODE_HEAT = "heat"
    MODE_DRY = "dry"
    MODE_FAN = "fan_only"
    MODE_AUTO = "auto"

    FAN_AUTO = "auto"
    FAN_LOW = "low"
    FAN_MEDIUM = "medium"
    FAN_HIGH = "high"

    SWING_ON = "on"
    SWING_OFF = "off"

    ACTION_OFF = "off"
    ACTION_HEATING = "heating"
    ACTION_COOLING = "cooling"
    ACTION_DRYING = "drying"
    ACTION_IDLE = "idle"
    ACTION_FAN = "fan"

    AVAILABILITY_TOPIC = "%s/availability"
    DISCOVERY_TOPIC = "%s/config"
    STATS_TOPIC = "%s/properties"
    TEMPERATURE_TOPIC = "%s/properties/targetTemperature"
    FAN_TOPIC = "%s/properties/fanMode"
    MODE_TOPIC = "%s/properties/mode"
    SWING_TOPIC = "%s/properties/swing"

    DEFAULT_TEMPERATURE = None

    MIN_TEMPERATURE = 18
    MAX_TEMPERATURE = 30

    state_temperature = DEFAULT_TEMPERATURE
    state_mode = MODE_OFF
    state_fan_mode = FAN_AUTO
    state_swing = SWING_OFF
    state_action = ACTION_OFF

    def get_discovery_payload(self):
        payload = {
            "name": self.name,
            "unique_id": self.mac,
            "payload_on": DeviceClimate.ON_VALUE,
            "payload_off": DeviceClimate.OFF_VALUE,
            "payload_available": DeviceClimate.ONLINE_STATE,
            "payload_not_available": DeviceClimate.OFFLINE_STATE,
            "availability_topic": DeviceClimate.AVAILABILITY_TOPIC % self.topic_name,
            "action_topic": DeviceClimate.STATS_TOPIC % self.topic_name,
            "action_template": '{{value_json.action}}',
            "temperature_command_topic": DeviceClimate.TEMPERATURE_TOPIC % self.topic_name,
            "mode_command_topic": DeviceClimate.MODE_TOPIC % self.topic_name,
            "mode_state_topic": DeviceClimate.STATS_TOPIC % self.topic_name,
            "mode_state_template": '{{value_json.mode}}',
            "modes": [DeviceClimate.MODE_AUTO, DeviceClimate.MODE_OFF, DeviceClimate.MODE_COOL, DeviceClimate.MODE_HEAT, DeviceClimate.MODE_DRY, DeviceClimate.MODE_FAN],
            "current_temperature_topic": DeviceClimate.STATS_TOPIC % self.topic_name,
            "current_temperature_template": "{{value_json.temperature}}",
            "fan_mode_command_topic": DeviceClimate.FAN_TOPIC % self.topic_name,
            "fan_mode_state_topic": DeviceClimate.STATS_TOPIC % self.topic_name,
            "fan_mode_state_template": '{{value_json.fanMode}}',
            "fan_modes": [DeviceClimate.FAN_AUTO, DeviceClimate.FAN_LOW, DeviceClimate.FAN_MEDIUM, DeviceClimate.FAN_HIGH],
            "swing_mode_command_topic": DeviceClimate.SWING_TOPIC % self.topic_name,
            "swing_mode_state_template": '{{value_json.swing}}',
            "swing_mode_state_topic": DeviceClimate.STATS_TOPIC % self.topic_name,
            "swing_modes": [DeviceClimate.SWING_ON, DeviceClimate.SWING_OFF],
            "min_temp": self.MIN_TEMPERATURE,
            "max_temp": self.MAX_TEMPERATURE,
            "temp_step": 1,
            "availability_mode": "any",
            "temperature_unit": "C",
            "device": {
                "manufacturer": "Orvibo",
                "model": "AllOne",
                "name": self.mac,
                "identifiers": self.mac,
                "via_device": "homeassistant-orvibo-mqtt"
            }
        }
        return dumps(payload)

    def get_current_status(self):
        payload = {
            "temperature": self.state_temperature,
            "mode": self.state_mode,
            "fanMode": self.state_fan_mode,
            "action": self.state_action,
            "swing": self.state_swing,
        }

        return dumps(payload)

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(DeviceClimate.HA_INIT_TOPIC)
        client.subscribe("%s/#" % self.topic_name)

        self.do_initialize(client)

    def on_message(self, client, userdata, msg):
        if msg.topic == DeviceClimate.MODE_TOPIC % self.topic_name:
            self.do_mode_change(client, msg.payload.decode("utf-8"))
        elif msg.topic == DeviceClimate.TEMPERATURE_TOPIC % self.topic_name:
            self.do_temperature_change(client, msg.payload.decode("utf-8"))
        elif msg.topic == DeviceClimate.FAN_TOPIC % self.topic_name:
            self.do_fan_change(client, msg.payload.decode("utf-8"))
        elif msg.topic == DeviceClimate.SWING_TOPIC % self.topic_name:
            self.do_swing_change(client, msg.payload.decode("utf-8"))
        elif msg.topic == DeviceClimate.HA_INIT_TOPIC:
            self.do_initialize(client)

        _LOGGER.debug("Message received-> " +
                      msg.topic + " " + str(msg.payload))

    def __send_ir_signal(self, file_path):
        real_path = str(PurePath(os.getcwd(), file_path))
        self.device.emit_ir(real_path)

    def do_initialize(self, client):
        _LOGGER.info("Send initialization info for %s (%s)" % (self.name, self.mac))
        self.send_config(client)
        self.send_availability(client, True)
        self.send_stats(client)

    def do_mode_change(self, client, mode):
        _LOGGER.info("Change mode => " + mode)
        if mode == self.MODE_OFF:
            if self.state_action == self.ACTION_OFF:
                self.state_action = self.ACTION_COOLING
                self.__send_ir_signal(self.SIGNAL_ON)
            else:
                self.state_action = self.ACTION_OFF
                self.__send_ir_signal(self.SIGNAL_OFF)
        elif mode == self.MODE_COOL:
            self.state_action = self.ACTION_COOLING
            self.__send_ir_signal(self.SIGNAL_MODE_COOL)
        elif mode == self.MODE_AUTO:
            self.state_action = self.ACTION_IDLE
            self.__send_ir_signal(self.SIGNAL_MODE_AUTO)
        elif mode == self.MODE_DRY:
            self.state_action = self.ACTION_DRYING
            self.__send_ir_signal(self.SIGNAL_MODE_DRY)
        elif mode == self.MODE_FAN:
            self.state_action = self.ACTION_FAN
            self.__send_ir_signal(self.SIGNAL_MODE_FAN)
        elif mode == self.MODE_HEAT:
            self.state_action = self.ACTION_HEATING
            self.__send_ir_signal(self.SIGNAL_MODE_HEAT)
        else:
            _LOGGER.warning("Unknown mode => " + mode)

            self.state_action = self.ACTION_COOLING
            self.__send_ir_signal(self.SIGNAL_ON)

        self.state_mode = mode
        self.send_stats(client)

    def do_temperature_change(self, client, temperature):
        _LOGGER.info("Change temperature => " + temperature)

        t_value = int(float(temperature))

        self.__send_ir_signal(self.SIGNAL_T % t_value)

        self.state_temperature = t_value
        self.send_stats(client)

    def do_fan_change(self, client, mode):
        _LOGGER.info("Change fan => " + mode)

        if mode == self.FAN_AUTO:
            self.__send_ir_signal(self.SIGNAL_FAN_AUTO)
        elif mode == self.FAN_HIGH:
            self.__send_ir_signal(self.SIGNAL_FAN_HIGH)
        elif mode == self.FAN_LOW:
            self.__send_ir_signal(self.SIGNAL_FAN_LOW)
        elif mode == self.FAN_MEDIUM:
            self.__send_ir_signal(self.SIGNAL_FAN_MID)
        else:
            _LOGGER.warning("Unknown fan mode => " + mode)

        self.state_fan_mode = mode
        self.send_stats(client)

    def do_swing_change(self, client, mode):
        _LOGGER.info("Change swing => " + mode)

        if mode == self.SWING_OFF:
            self.__send_ir_signal(self.SIGNAL_SWING_OFF)
        elif mode == self.SWING_ON:
            self.__send_ir_signal(self.SIGNAL_SWING_ON)
        else:
            _LOGGER.warning("Unknown swing mode => " + mode)

        self.state_swing = mode
        self.send_stats(client)

    def send_config(self, client):
        discovery_payload = self.get_discovery_payload()
        client.publish(DeviceClimate.DISCOVERY_TOPIC %
                       self.topic_name, payload=discovery_payload)

    def send_stats(self, client):
        payload = self.get_current_status()
        client.publish(DeviceClimate.STATS_TOPIC %
                       self.topic_name, payload=payload)

    def send_availability(self, client, value: bool):
        payload = DeviceClimate.ONLINE_STATE if value else DeviceClimate.OFFLINE_STATE
        client.publish(DeviceClimate.AVAILABILITY_TOPIC %
                       self.topic_name, payload=payload)

    def destruct(self, client):
        self.send_availability(client, False)
