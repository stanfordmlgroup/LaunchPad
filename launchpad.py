import yaml
from sklearn.model_selection import ParameterGrid, ParameterSampler
from subprocess import check_call
import uuid
import fire
import os
import pkgutil

from config import Config


def run(config="config.yaml",
        run="compile"):

    _config = Config(config)
    meta, hp = _config.meta, _config.hp

    for i in range(meta.repeat):
        if meta.mode == "grid":
            config_list = list(ParameterGrid(hp))
        elif meta.mode == "random":
            config_list = list(ParameterSampler(hp, meta.sample))

        for idx, c in enumerate(config_list):
            if "key" in meta:
                key_config = meta.key
                c['exp_name'] = exp_name = "_".join(
                    [str(c[k]) for k in key_config]) + f"_round_{i}"
            else:
                c['exp_name'] = exp_name = uuid.uuid4().hex
            exec_line = f"{meta.script} " + \
                " ".join([f"--{k} {v}" for k, v in c.items()])

            if run == "compile":
                print(exec_line)
            elif run == "shell":
                print(exec_line)
                check_call(exec_line, shell=True)
            elif run == "sbatch":
                template = pkgutil.get_data(__name__, "scripts/sbatch_template.sh").decode()

                template = template.replace("@GPUS", f"{meta.gpus}")
                template = template.replace("@EXCLUDE", f"{meta.exclude}")
                template = template.replace("@LOG", f"{meta.logpath}")
                template = template.replace("@NAME", f"{exp_name}")
                template = template.replace("@COMMAND", f"{exec_line}")

                sbatch_filepath = os.path.join(meta.sandbox, f"{exp_name}.sh")
                with open(sbatch_filepath, 'w') as f:
                    f.write(template)

                check_call(f"sbatch {sbatch_filepath}", shell=True)
                print(exec_line)
                # os.remove(sbatch_filepath)


def main():
    fire.Fire(run)
