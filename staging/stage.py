"""
Stage class
"""

from dataclasses import field, dataclass

from dataclass_wizard import JSONWizard, JSONSerializable

from .step import Step
from .logger import logger
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

    name: str | None = None
    description: str | None = None
    formatter: dict[str, str] = field(default_factory=dict)
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
                logger.info(f"Step failed but continue_on_failure is set to True: {e}")
