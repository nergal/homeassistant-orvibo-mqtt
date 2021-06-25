# -*- coding: utf-8 -*-

from orvibo import Orvibo
from typing import Final, List
import logging
from .devices import DeviceSocket, DeviceClimate, AbstractDevice

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


class DeviceZoo:
    device_pool: List[AbstractDevice] = []

    def __init__(self, config):
        for device_config in config['devices'].get():
            device = self.device_factory(device_config)

            if device:
                self.device_pool.append(device)

    def device_factory(self, config):
        raw_device = Orvibo(config['ip'], config['mac'], config['type'])
        if raw_device.type == 'socket':
            return DeviceSocket(raw_device, 'switch', config['name'])
        elif raw_device.type == 'irda':
            return DeviceClimate(raw_device, 'climate', config['name'])
        else:
            _LOGGER.error("Unknown device discovered at %s" % ip)

    def on_connect(self, *args, **kwargs):
        for device in self.device_pool:
            device.on_connect(*args, **kwargs)

    def on_message(self, *args, **kwargs):
        for device in self.device_pool:
            device.on_message(*args, **kwargs)

    def destruct(self, client):
        for device in self.device_pool:
            device.destruct(client)
