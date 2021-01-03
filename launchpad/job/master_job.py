import os
import uuid
import logging
import re
import pkgutil
import shutil
import pandas as pd
from cachetools.func import ttl_cache
from subprocess import (check_call, 
                        check_output,
                        CalledProcessError)

from .base import BaseJob
from .slurm_job import SlurmJob
from .shell_job import ShellJob
from .color import colorful_state

logger = logging.getLogger("LaunchPad/MasterJob")
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)


class MasterJob(BaseJob):
    def __init__(self, config):
        self._jobs = [] 
        self._col, _ = shutil.get_terminal_size()
        for idx, c in enumerate(config):
            if config.meta.get("run", None) == "slurm":
                self._jobs.append(SlurmJob(c))
            else:
                self._jobs.append(ShellJob(c))

    def compile(self):
        for idx, job in enumerate(self._jobs):
            job.compile()
            state = job.get_state()
                    
            # Check state
            if state == "Finish":
                if 'override' in meta and meta['override']:
                    logger.warning(
                        f"Override existing experiment [{job._exp_name}].")
                else:
                    logger.warning(f"Skip existing experiment [{job._exp_name}].")
            elif state == "Running":
                logger.warning(
                    f"Skip experiment [{job._exp_name}], which is already running.")
            else: 
                if state == "Compiled":
                    logger.info(f"Recompiled experiment [{job._exp_name}].")
            self.print_state(idx, job)

    def run(self):
        for idx, job in enumerate(self._jobs):
            job.run()
            self.print_state(idx, job)

    def print_state(self, idx, job):
        state = job.get_state()
        print("-" * self._col)
        print(f"Experiment No.{idx+1} -- [{job._exp_name}]:\n{job._exec_line}")
        print(f"Current State: {colorful_state(state)}") 
        if state == "Running":
            print(f"Slurm job ID: {job._id}")
            print("Latest metrics: ")
            print(f"{job.get_metrics()}")
