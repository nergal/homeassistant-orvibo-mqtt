import logging
from typing import Optional

from .abstract_commands import AbstractCommands

_LOGGER = logging.getLogger(__name__)


class ClimateCommands(AbstractCommands):
    MANDATORTY_FIELDS = ["temperature", "mode", "fanMode", "swing", "action"]

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

    COMMAND_OFF = "off"
    COMMAND_ON = "on"

    MIN_TEMPERATURE = 18
    MAX_TEMPERATURE = 30

    DEFAULT_TEMPERATURE = 23

    state = {
        "temperature": DEFAULT_TEMPERATURE,
        "mode": MODE_OFF,
        "fanMode": FAN_AUTO,
        "action": ACTION_OFF,
        "swing": SWING_OFF,
    }

    def get_state(self) -> dict:
        return self.state

    def validate_change(self, state: dict) -> bool:
        return all(x in self.MANDATORTY_FIELDS for x in state)

    def mode_to_action(self, mode):
        if mode == self.MODE_AUTO:
            return self.ACTION_COOLING
        elif mode == self.MODE_COOL:
            return self.MODE_COOL
        elif mode == self.MODE_DRY:
            return self.ACTION_DRYING
        elif mode == self.MODE_FAN:
            return self.ACTION_FAN
        elif mode == self.MODE_HEAT:
            return self.ACTION_HEATING
        elif mode == self.MODE_OFF:
            return self.ACTION_OFF

        return self.ACTION_IDLE

    def get_command_from_state(self, updates: dict) -> Optional[str]:
        for (name, value) in updates.items():
            _LOGGER.info("Change %s => %s", name, value)

        state = self.get_state()
        if not self.validate_change(updates):
            raise ValueError("Provided change of the state is invalid")

        if "swing" in updates:
            self.state.update({"swing": updates["swing"]})
            return f"swing_{updates['swing']}"
        else:
            mode = state["mode"] if state["mode"] != self.MODE_OFF else self.MODE_COOL

            if "fanMode" in updates:
                self.state.update({"fanMode": updates["fanMode"], "mode": mode})

            if mode == self.MODE_FAN:
                return f"{state['mode']}_{state['fanMode']}"

            if "temperature" in updates:
                if (
                    updates["temperature"] >= self.MIN_TEMPERATURE
                    and updates["temperature"] <= self.MAX_TEMPERATURE
                ):
                    self.state.update(
                        {
                            "mode": mode,
                            "temperature": updates["temperature"],
                            "action": self.ACTION_COOLING
                            if mode != self.state["mode"]
                            else self.state["action"],
                        }
                    )
                else:
                    _LOGGER.warning(
                        "Wanted temp value %s is not in range of allowed [%d..%d]",
                        updates["temperature"],
                        self.MIN_TEMPERATURE,
                        self.MAX_TEMPERATURE,
                    )
                    return None

            if "mode" in updates:
                send_on = False
                if updates["mode"] == self.MODE_OFF:
                    self.state.update(
                        {
                            "mode": self.MODE_OFF,
                            "action": self.ACTION_OFF,
                        }
                    )
                    return self.COMMAND_OFF
                elif state["mode"] == self.MODE_OFF:
                    send_on = True

                temp = (
                    state["temperature"]
                    if state["temperature"] is not None
                    else self.MIN_TEMPERATURE
                )
                action = self.mode_to_action(updates["mode"])

                self.state.update(
                    {
                        "action": action,
                        "mode": updates["mode"],
                        "temperature": temp if temp != state["temperature"] else state["temperature"],
                    }
                )

                if send_on:
                    return self.COMMAND_ON

            return f"{state['mode']}_t{state['temperature']}_{state['fanMode']}"

        return None
