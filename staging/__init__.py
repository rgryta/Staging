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

STAGING = {"steps": {}, "stages": {}}


logging.getLogger().setLevel(logging.INFO)


def _parse_toml():
    with open("pyproject.toml", encoding="utf-8") as f:
        toml = parse(f.read())
    staging_config = toml.get("tool", {}).get("staging", {})

    STAGING["steps"] = {k: {"name": k, **v} for k, v in staging_config.get("steps", {}).items()}
    STAGING["stages"] = staging_config.get("stages", {})


def _parse_args() -> argparse.Namespace:  # pragma: no cover
    parser = argparse.ArgumentParser(description="Execute stage of the pipeline.")
    parser.add_argument("stage", nargs="+", type=str, choices=set(STAGING["stages"]), help="name stages to execute")
    args = parser.parse_args()
    return args


async def _main() -> None:  # pragma: no cover
    _parse_toml()
    args = _parse_args()

    for stage in args.stage:
        clear()
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

        for k, v in stage_info.get("format", {}).items():
            set_format(k, v)

        stage_to_run = Stage.from_dict({"name": stage, "description": stage_info.get("description"), "steps": steps})
        try:
            await stage_to_run.run()
        except Exception as e:  # pylint:disable=broad-except
            logging.error(f"Error in stage [{stage}]: {e}")
            logging.info(f"[Staging {stage}] Finishing with error")
            sys.exit(1)
        logging.info(f"[Staging {stage}] Finishing with success")


def main():  # pragma: no cover
    """
    Main entry point for the staging tool
    """
    asyncio.run(_main())
