import logging
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from pprint import pprint
from typing import Dict, Optional

from .abstract_commands import AbstractCommands

_LOGGER = logging.getLogger(__name__)


class IRCommands:
    ir_commands: Dict[str, bytes] = {}

    def __init__(self, filename: str, transpiler: AbstractCommands):
        self.transpiler = transpiler
        mapping_file = Path(os.getcwd(), f"usr/share/{filename}.xml")

        if mapping_file.exists():
            mapping_root = ET.parse(mapping_file).getroot()
            for elem in mapping_root.findall("remote/code"):
                name = elem.attrib["name"]
                ccf = elem.find("ccf")

                if ccf is not None and ccf.text is not None:
                    hex_snapshot = " ".join(
                        map(lambda x: x[2:4] + x[0:2], ccf.text.split(" "))
                    )
                    self.ir_commands[name] = bytes.fromhex(hex_snapshot)
                else:
                    _LOGGER.error("Unable to load ccf's from %s", mapping_file)
        else:
            raise FileExistsError(
                f"Configuration file not found, looking at {mapping_file}"
            )

    def get_state(self) -> Dict[str, str]:
        return self.transpiler.get_state()

    def resolve(self, name: str) -> Optional[bytes]:
        pprint(name)
        if name in self.ir_commands:
            return self.ir_commands[name]
        else:
            _LOGGER.error("Unknown signal: %s", name)
            return None

    def get(self, updates: dict) -> str:
        return self.transpiler.get_command_from_state(updates)
