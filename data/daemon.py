#!env python3
# -*- coding: utf-8 -*-

import logging
import confuse
from pathlib import PurePath
import os
from homeassistant_orvibo_mqtt.device_zoo import DeviceZoo

logging.basicConfig(level=logging.DEBUG)

APP_NAME = 'homeassistant-orvibo-mqtt'
CONFIG_FILE = 'config.yaml'

if __name__ == "__main__":
    cwd = os.path.dirname(os.path.abspath(__file__))
    config_path = PurePath(cwd, CONFIG_FILE)

    source = confuse.YamlSource(config_path)
    config = confuse.RootView([source])

    handler = DeviceZoo(config)

    try:
        handler.loop_forever()
    except KeyboardInterrupt:
        pass
