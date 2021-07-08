# -*- coding: utf-8 -*-

from orvibo import Orvibo, OrviboException
from typing import Final, List
import logging
from sdnotify import SystemdNotifier
from .devices import DeviceSocket, DeviceClimate, AbstractDevice

logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)


class DeviceZoo:
    device_pool: List[AbstractDevice] = []

    def __init__(self, config):
        self.config = config
        self.sd_notifier = SystemdNotifier()
        for device_config in config['devices'].get():
            device = self.device_factory(device_config)

            if device:
                self.device_pool.append(device)

    def device_factory(self, device_config):
        try:
            ip = device_config['ip']
            raw_device = Orvibo(ip)
            attrs = (raw_device, device_config, self.config)

            if raw_device.type == 'socket':
                return DeviceSocket(*attrs)
            elif raw_device.type == 'irda':
                return DeviceClimate(*attrs)
            else:
                _LOGGER.error("Unknown device discovered at %s (%s)" % (ip, raw_device.type))

        except OrviboException as err:
            _LOGGER.error("Unable to initialize device ip=%s" % ip)

    def loop_forever(self):
        for device in self.device_pool:
            device.loop_forever()

        self.sd_notifier.notify('READY=1')
        _LOGGER.info("Ready to go!")

        for device in self.device_pool:
            device.thread.join()

    def __del__(self):
        for device in self.device_pool:
            device.__del__()

    
