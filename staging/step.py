"""
Step class
"""

import sys
import asyncio
from dataclasses import field, dataclass

from .config import get_format, set_format
from .executable import Executable


@dataclass
class Step(Executable):  # pylint:disable=too-many-instance-attributes
    """
    Step class
    """

    name: str | None = None

    execute: str | None = None

    prepare: str | None = None
    cleanup: str | None = None

    output: str | None = None
    format: dict[str, str] = field(default_factory=dict)

    success_codes: list[int] = field(default_factory=list)
    error_codes: list[int] = field(default_factory=list)

    def __post_init__(self):

        if self.success_codes and self.error_codes:
            raise ValueError(f"[Step {{{self.name}}}] Both success_codes and error_codes cannot be set")

        if not self.error_codes and not self.success_codes:
            self.success_codes = [0]

        if self.execute is None:
            raise ValueError(f"[Step {{{self.name}}}] Content of `execute` is required")

    def _format(self):
        """
        Format the commands
        """
        formatter = {k: get_format(v) for k, v in self.format.items()}
        if self.prepare is not None:
            self.prepare = self.prepare.format(**formatter)
        if self.cleanup is not None:
            self.cleanup = self.cleanup.format(**formatter)

        self.execute = self.execute.format(**formatter)

    async def _run(self, cmd):
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await proc.communicate()
        return proc.returncode, stdout, stderr

    async def run(self):
        self._format()
        try:
            if self.prepare:
                ret, stdout, stderr = await self._run(self.prepare)
                if ret != 0:
                    sys.stderr.write(stdout.decode())
                    sys.stderr.write(stderr.decode())
                    raise Exception(  # pylint:disable=broad-exception-raised
                        f"[Step {{{self.name}}}] Execution failed with code {ret}."
                    )

            ret, stdout, stderr = await self._run(self.execute)
            if ret in self.error_codes or (not self.error_codes and ret not in self.success_codes):
                sys.stderr.write(stdout.decode())
                sys.stderr.write(stderr.decode())
                raise Exception(  # pylint:disable=broad-exception-raised
                    f"[Step {{{self.name}}}] Execution failed with code {ret}."
                )

            if self.output:
                set_format(self.output, stdout.decode())
        except Exception as e:
            raise e
        finally:
            if self.cleanup:
                await self._run(self.cleanup)
