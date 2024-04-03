"""
Executable class
"""

from dataclasses import dataclass

from dataclass_wizard import JSONSerializable


@dataclass
class Executable(JSONSerializable):
    """
    Executable class
    """

    continue_on_failure: bool = False

    async def run(self):
        """
        Run the executable
        """
        raise NotImplementedError("Method `run` must be implemented in subclasses")
