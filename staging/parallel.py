"""
Parallel class
"""

import asyncio
import logging
from asyncio import Task
from dataclasses import field, dataclass

from .step import Step
from .logger import logger
from .executable import Executable


@dataclass
class Parallel(Executable):
    """
    Parallel class
    """

    steps: list[Step] = field(default_factory=list)

    async def run(self):
        tasks: list[Task] = []
        try:
            async with asyncio.TaskGroup() as tg:
                for step in self.steps:
                    task = tg.create_task(step.run())
                    tasks.append(task)
            for task in tasks:
                await task
        except* Exception as eg:
            exceptions = [
                exc
                for exc in eg.exceptions  # pylint:disable=no-member
                if not isinstance(exc, asyncio.CancelledError)  # Ignore cancellations
            ]
            if logger.level <= logging.INFO:
                for exception in exceptions:
                    logger.error(f"Exception happened: {exception}")
            raise Exception("Parallel steps failed") from exceptions[0]  # pylint:disable=broad-exception-raised
