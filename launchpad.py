import yaml
from sklearn.model_selection import ParameterGrid, ParameterSampler
from subprocess import check_call, check_output
import uuid
import fire
import os
import pkgutil
import logging
import shutil

from config import Config
from smanager import Smanager 

logger = logging.getLogger("LaunchPad")
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


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
    template = pkgutil.get_data(__name__, "scripts/sbatch_template.sh").decode()
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
    #TODO Add the logic if config is a folder concat config.yaml
    col, _ = shutil.get_terminal_size() 
    _config = Config(config)
    meta, hp, sbatch = _config.meta, _config.hp, _config.sbatch

    for i in range(meta.repeat):
        if meta.mode == "grid":
            config_list = list(ParameterGrid(hp))
        elif meta.mode == "random":
            config_list = list(ParameterSampler(hp, meta.sample))

        for idx, c in enumerate(config_list):
            if "key" in meta:
                key_config = meta.key
                exp_name = "_".join(
                        [str(c[k]) for k in key_config] + [f"{i}"])
            else:
                exp_name = uuid.uuid4().hex

            if "prefix" in meta:
                exp_name = meta.prefix + "_" + exp_name
            
            c['exp_name'] = exp_name
            
            exec_line = f"{meta.script} " + \
                " ".join([f"--{k} {v}" for k, v in c.items()])
            sbatch_config = "\n".join([f"#SBATCH --{k}={v}" for k, v in sbatch.items()])
           
            col, _ = shutil.get_terminal_size()
            state = check_state(exp_name, meta)
            print("-"*col)
            print(f"Experiment No.{idx+1} -- [{exp_name}]:\n{exec_line}\n")
            print(f"Current State: {state}")
            # TODO: Add a status
            if state == "Finish":
                if 'override' in meta and meta['override']:
                    logger.warning(f"Override existing experiment [{exp_name}].") 
                else:
                    logger.warning(f"Skip existing experiment [{exp_name}].") 
                    continue
            if state == "Running":
                logger.warning(f"Skip experiment [{exp_name}], which is already running.") 
                continue
            if state == "Compiled":
                logger.info(f"Recompiled experiment [{exp_name}].") 
 
            if run == "compile":
                sbatch_filepath = compile_template(exec_line, sbatch_config, exp_name, meta)
            elif run == "shell":
                check_call(exec_line, shell=True)
            elif run == "sbatch":
                sbatch_filepath = compile_template(exec_line, sbatch_config, exp_name, meta)
                check_call(f"sbatch {sbatch_filepath}", shell=True)
                #os.remove(sbatch_filepath)
    print("-"*col)
    # TODO: Add a job summary (colorful)


def main():
    fire.Fire(run)
