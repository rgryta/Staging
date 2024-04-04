"""
This module is the entry point for the staging tool. It reads the pyproject.toml file and executes
the stages defined in it.
"""

import sys
import asyncio
import logging
import argparse

from tomlkit import parse

from .stage import Stage
from .config import clear, get_format, set_format
from .logger import logger, setup_logger

STAGING = {"steps": {}, "stages": {}}


def _parse_toml():
    with open("pyproject.toml", encoding="utf-8") as f:
        toml = parse(f.read())
    staging_config = toml.get("tool", {}).get("staging", {})

    STAGING["steps"] = {k: {"name": k, **v} for k, v in staging_config.get("steps", {}).items()}
    STAGING["stages"] = staging_config.get("stages", {})


def _parse_args() -> argparse.Namespace:  # pragma: no cover
    parser = argparse.ArgumentParser(description="Execute stage of the pipeline.")
    parser.add_argument("stage", nargs="+", type=str, choices=set(STAGING["stages"]), help="name stages to execute")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="increase output verbosity")
    args = parser.parse_args()
    return args


async def _main() -> None:  # pragma: no cover
    _parse_toml()
    args = _parse_args()
    match args.verbose:
        case 0:
            setup_logger()
        case 1:
            setup_logger(level=logging.INFO)
        case 2:
            setup_logger(level=logging.DEBUG)
        case _:
            setup_logger(level=logging.NOTSET)

    stages = []
    for stage in args.stage:
        stage_info = STAGING["stages"][stage]

        steps = []
        for step_info in stage_info["steps"]:
            step = step_info.get("step", None)
            parallel = step_info.get("parallel", None)
            continue_on_failure = step_info.get("continue_on_failure", False)

            if step and parallel:
                raise ValueError("Both step and parallel cannot be set")

            if step:
                steps.append({"key": "Step", **STAGING["steps"][step], "continue_on_failure": continue_on_failure})
            if parallel:
                parallel_steps = []
                for parallel_step in parallel.get("steps", []):
                    parallel_steps.append(STAGING["steps"][parallel_step])
                steps.append({"key": "Parallel", "steps": parallel_steps, "continue_on_failure": continue_on_failure})

        formatter = {}
        for k, v in stage_info.get("format", {}).items():
            formatter[k] = v

        stages.append(
            Stage.from_dict(
                {"name": stage, "description": stage_info.get("description"), "steps": steps, "formatter": formatter}
            )
        )
    for stage in stages:
        clear()
        try:
            for k, v in stage.formatter.items():
                set_format(k, v)
            await stage.run()
        except Exception as e:  # pylint:disable=broad-except
            logger.error(f"Error in stage [{stage.name}]: {e}")
            logger.info(f"[Stage {{{stage.name}}}] Finishing with error")
            sys.exit(1)
        logger.info(f"[Stage {{{stage.name}}}] Finishing with success")


def main():  # pragma: no cover
    """
    Main entry point for the staging tool
    """
    asyncio.run(_main())
