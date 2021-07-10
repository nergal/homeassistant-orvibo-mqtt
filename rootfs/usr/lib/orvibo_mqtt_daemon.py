#!env python3
# -*- coding: utf-8 -*-

import getopt
import json
import logging
import sys

from orvibo_mqtt.device_zoo import DeviceZoo

APP_NAME = "homeassistant-orvibo-mqtt"


class Config:
    def __init__(self, filename: str):
        with open(filename, "r") as config_file:
            self.data = json.load(config_file)

    def get(self, key: str, default_value=None):
        return self.data[key] if self.has(key) else default_value

    def has(self, key: str) -> bool:
        return key in self.data


def print_help():
    print("Usage: ./main.py --config=<JSON file>")


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "c", ["config="])
    except getopt.GetoptError:
        print_help()
        sys.exit(2)

    config_path = None
    for opt, arg in opts:
        if opt in ("-c", "--config"):
            config_path = arg

    if config_path:
        config = Config(config_path)

        log_level_str = config.get("log_level", "INFO").upper()
        log_level = logging._nameToLevel[log_level_str]
        if log_level:
            logging.basicConfig(level=log_level)
            logging.info("Set log level to %s", log_level_str)

        handler = DeviceZoo(config)

        try:
            handler.loop_forever()
        except KeyboardInterrupt:
            pass
    else:
        print_help()
        sys.exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
