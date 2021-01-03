import yaml
from subprocess import check_call, check_output
import uuid
import fire
import os
import pandas as pd
import logging
import shutil

from .job import create_job 
from .util import colorful_state, Config, Args

logger = logging.getLogger("LaunchPad")
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)


def run(config="config.yaml",
        run="compile"):
    if os.path.isdir(config):
        config = os.path.join(config, "config.yaml")
    col, _ = shutil.get_terminal_size()
    _config = Config(config)
    if _config.meta.mode == "nni":
        job = create_job(_config)
        job.compile()
        job.cancel()
        return 
    for idx, c in enumerate(_config):
        job = create_job(c)
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

            # Execution 
            if run == "shell":
                job.shell()
            elif run == "sbatch":
                job.sbatch()

        print("-" * col)
        print(f"Experiment No.{idx+1} -- [{job._exp_name}]:\n{job._exec_line}")
        print(f"Current State: {colorful_state(state)}") 
        if state == "Running":
            print(f"Slurm job ID: {job._id}")
            print("Latest metrics: ")
            print(f"{job.get_metrics()}")

def main():
    fire.Fire(run)

if __name__ == "__main__":
    fire.Fire(run)
