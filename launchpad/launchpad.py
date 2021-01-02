import yaml
from sklearn.model_selection import ParameterGrid, ParameterSampler
from subprocess import check_call, check_output
import uuid
import fire
import os
import pandas as pd
import pkgutil
import logging
import shutil

from slurm import Smanager, Job
from util import colorful_state, Config

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
    meta, hp, sbatch = _config.meta, _config.hp, _config.sbatch
    jobs = []
    for i in range(meta.repeat):
        if meta.mode == "grid":
            config_list = list(ParameterGrid(hp))
        elif meta.mode == "random":
            config_list = list(ParameterSampler(hp, meta.sample))

        for idx, c in enumerate(config_list):
            _config.hp = c
            job = Job(_config)
            job.compile()
            state = job.get_state()
            jobs.append(job)
                        
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

    #jobs = pd.DataFrame(jobs)
    #print("-" * col)
    #state_count = [
    #    f"{count} {colorful_state(state)}" for state,
    #    count in jobs.groupby("state")['name'].nunique().to_dict().items()]
    #print(f"{len(jobs)} jobs: {', '.join(state_count)}")


def main():
    fire.Fire(run)

if __name__ == "__main__":
    fire.Fire(run)
