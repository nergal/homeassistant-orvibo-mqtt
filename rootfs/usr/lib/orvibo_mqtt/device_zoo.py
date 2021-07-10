import logging
from typing import List

from orvibo import Orvibo, OrviboException

from .devices.abstract_device import AbstractDevice
from .devices.device_climate import DeviceClimate
from .devices.device_socket import DeviceSocket

_LOGGER = logging.getLogger(__name__)


class DeviceZoo:
    device_pool: List[AbstractDevice] = []

    def __init__(self, config):
        self.config = config
        for device_config in config.get("devices", []):
            device = self.device_factory(device_config)

            if device:
                self.device_pool.append(device)

    def device_factory(self, device_config):
        try:
            ip = device_config["ip"]
            raw_device = Orvibo(ip)
            attrs = (raw_device, device_config, self.config)

            if raw_device.type == "socket":
                return DeviceSocket(*attrs)
            elif raw_device.type == "irda":
                return DeviceClimate(*attrs)
            else:
                _LOGGER.error(
                    "Unknown device discovered at %s (%s)" % (ip, raw_device.type)
                )

        except OrviboException:
            _LOGGER.error("Unable to initialize device ip=%s" % ip)

    def loop_forever(self):
        for device in self.device_pool:
            device.loop_forever()

        _LOGGER.warning("Starting the loops")

        for device in self.device_pool:
            device.thread.join()
