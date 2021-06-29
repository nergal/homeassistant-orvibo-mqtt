# -*- coding: utf-8 -*-

from orvibo import Orvibo, OrviboException
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
        try:
            raw_device = Orvibo(config['ip'])
            attrs = (raw_device, config['type'], config['name'])

            if raw_device.type == 'socket':
                return DeviceSocket(*attrs)
            elif raw_device.type == 'irda':
                return DeviceClimate(*attrs)
            else:
                _LOGGER.error("Unknown device discovered at %s (%s)" % (config['ip'], raw_device.type))

        except OrviboException as err:
            _LOGGER.error("Unable to initialize device ip=%s" % config['ip'])

    def on_connect(self, *args, **kwargs):
        for device in self.device_pool:
            device.on_connect(*args, **kwargs)

    def on_message(self, *args, **kwargs):
        for device in self.device_pool:
            device.on_message(*args, **kwargs)

    def destruct(self, client):
        for device in self.device_pool:
            device.destruct(client)
