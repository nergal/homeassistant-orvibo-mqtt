from abc import ABC, abstractmethod


class AbstractCommands(ABC):
    @abstractmethod
    def get_state(self):
        pass

    @abstractmethod
    def get_command_from_state(self, updates: dict):
        pass
