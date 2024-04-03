"""
Stage class
"""

import logging
from dataclasses import field, dataclass

from dataclass_wizard import JSONWizard, JSONSerializable

from .step import Step
from .parallel import Parallel


@dataclass
class Stage(JSONSerializable):
    """
    Stage class
    """

    class Meta(JSONWizard.Meta):
        """
        Metaclass for JSONWizard
        """

        tag_key = "key"
        auto_assign_tags = True

    description: str | None = None
    steps: list[Step | Parallel] = field(default_factory=list)

    async def run(self):
        """
        Run the stage
        """
        for step in self.steps:
            try:
                await step.run()
            except Exception as e:  # pylint:disable=broad-except
                if not step.continue_on_failure:
                    raise e
                logging.info(f"Step failed but continue_on_failure is set to True: {e}")
