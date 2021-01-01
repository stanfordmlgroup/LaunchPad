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


def check_state(exp_name, meta):
    username = os.environ['USER']
    smanager = Smanager(user=username)
    state = smanager.get_state(exp_name)
    if state == "N":
        log_filepath = os.path.join(meta.logpath, f"{exp_name}.log")
        if os.path.exists(log_filepath):
            state = "Finished"
        else:
            sbatch_filepath = os.path.join(meta.sandbox, f"{exp_name}.sh")
            if os.path.exists(sbatch_filepath):
                state = "Compiled"
            else:
                state = "Unknown"
    elif state == "R":
        state = "Running"
    elif state == "PD":
        state = "Pending"
    return state


def compile_template(exec_line, sbatch_config, exp_name, meta):
    #template = pkgutil.get_data(__name__, "scripts/sbatch_template.sh").decode()
    with open("scripts/sbatch_template.sh", "r") as f:
        template = f.read()
    template = template.replace("@GPUS", f"{meta.gpus}")
    template = template.replace("@LOG", f"{meta.logpath}")
    template = template.replace("@NAME", f"{exp_name}")
    template = template.replace("@CONFIG", f"{sbatch_config}")
    template = template.replace("@COMMAND", f"{exec_line}")
    sbatch_filepath = os.path.join(meta.sandbox, f"{exp_name}.sh")
    with open(sbatch_filepath, 'w') as f:
        f.write(template)
    return sbatch_filepath


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
                        f"Override existing experiment [{exp_name}].")
                else:
                    logger.warning(f"Skip existing experiment [{exp_name}].")
                    continue
            if state == "Running":
                logger.warning(
                    f"Skip experiment [{exp_name}], which is already running.")
                continue
            elif state == "Compiled":
                logger.info(f"Recompiled experiment [{exp_name}].")
            
            # Execution 
            if run == "shell":
                job.shell()
            elif run == "sbatch":
                job.sbatch()

            print("-" * col)
            print(f"Experiment No.{idx+1} -- [{job._exp_name}]:\n{job._exec_line}")
            print(f"Current State: {state}") 
            if run == "sbatch":
                print(f"Slurm job ID: {job._id}")


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
