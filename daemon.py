#!env python3
# -*- coding: utf-8 -*-

import logging
import paho.mqtt.client as mqtt
import confuse
from pathlib import PurePath
import os
import sdnotify
from homeassistant_orvibo_mqtt.device_zoo import DeviceZoo

logging.basicConfig(level=logging.DEBUG)

APP_NAME = 'homeassistant-orvibo-mqtt'
CONFIG_FILE = 'config.yaml'

if __name__ == "__main__":
    sd_notifier = sdnotify.SystemdNotifier()

    cwd = os.path.dirname(os.path.abspath(__file__))
    config_path = PurePath(cwd, CONFIG_FILE)

    source = confuse.YamlSource(config_path)
    config = confuse.RootView([source])

    handler = DeviceZoo(config)

    client = mqtt.Client(APP_NAME)
    client.on_connect = handler.on_connect
    client.on_message = handler.on_message

    try:
        mqtt_host = config['mqtt_host'].get()
        mqtt_port = config['mqtt_port'].get(int)

        client.connect(mqtt_host, mqtt_port)
        sd_notifier.notify('READY=1')

        client.loop_forever()
    except KeyboardInterrupt:
        pass
    finally:
        handler.destruct(client)
