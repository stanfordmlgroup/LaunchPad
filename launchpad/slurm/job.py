import os
import uuid
import re
import pkgutil
import pandas as pd
from cachetools.func import ttl_cache
from subprocess import (check_call, 
                        check_output,
                        CalledProcessError)


class Job:
    def __init__(self, config):
        self._meta = config.meta
        self._hp = config.hp
        self._sbatch = config.sbatch
        
        self._format = '%.18i %.9P %.100j %.8u %.2t %.10M %.6D %R'
        self._id = None
        self._exp_name = self._get_exp_name()
        self._hp['exp_name'] = self._exp_name
        self._exec_line = self._get_exec_line()
        self._sbatch_config = self._get_sbatch_config()
        self._sbatch_filepath = os.path.join(self._meta.sbatch_dir, f"{self._exp_name}.sh")
        self._log_filepath = os.path.join(self._meta.log_dir, f"{self._exp_name}.log")
 
    
    def compile(self):
        template = pkgutil.get_data(__name__, "scripts/sbatch_template.sh").decode()
        template = template.replace("@GPUS", f"{self._meta.gpus}")
        template = template.replace("@LOG", f"{self._meta.log_dir}")
        template = template.replace("@NAME", f"{self._exp_name}")
        template = template.replace("@CONFIG", f"{self._sbatch_config}")
        template = template.replace("@COMMAND", f"{self._exec_line}")
        with open(self._sbatch_filepath, 'w') as f:
            f.write(template)
    
    @ttl_cache(ttl=30)
    def get_state(self):
        state = None
        cmd = ['squeue', '-n', self._exp_name, '-o', self._format]
        try:
            smines = check_output(cmd)
            smines = smines.decode('utf8').split('\n')
            states = [None for _ in range(len(smines) - 2)]
            for i, smine in enumerate(smines[1:-1]):
                smine = smine.split(' ')
                s = [s for s in smine if s != '']
                state = s[4]
                self._id = s[0]
        except FileNotFoundError:
            pass # e.g. squeue not installed

        if state is not None:
            if state == "R":
                state = "Running"
            elif state == "PD":
                state = "Pending"
        else:
            if os.path.exists(self._log_filepath):
                state = "Finished"
            else:
                if os.path.exists(self._sbatch_filepath):
                    state = "Compiled"
                else:
                    state = "Unknown"

        return state
    
    @ttl_cache(ttl=5)
    def get_metrics(self):
        return pd.read_csv(self._get_metrics_path()).tail(1)
                                    
    def shell(self): 
        try:
            check_call(self._exec_line.split())
        except CalledProcessError as e:
            print(e.output)

    def sbatch(self): 
        self.compile()
        output = check_output(["sbatch", self._sbatch_filepath])
        x = re.findall("Submitted batch job \d+", str(output))
        self._id = int(x[0].split()[-1])

    def cancel(self):
        check_output(["scancel", "-n", self._exp_name])
    
    def _get_metrics_path(self):
        metrics_path = self._meta.get("metrics_path", None)
        if metrics_path is None:
            raise ValueError("[metrics_path] has not been set up!")
        metrics_path = metrics_path.format(**self._hp)
        return metrics_path

    def _get_exec_line(self):
        executor, script_path = self._meta.script.split()
        config_path = self._meta.config_path
        script_path = os.path.abspath(os.path.join(os.path.dirname(config_path),
                                      script_path))
        exec_line = " ".join([executor, script_path] \
                + [f"--{k} {v}" for k, v in self._hp.items()])
        return exec_line

    def _get_exp_name(self): 
        if "key" in self._meta:
            exp_name = "_".join([str(self._hp[k]) for k in self._meta.key])
        else:
            exp_name = uuid.uuid4().hex
        if "prefix" in self._meta:
            exp_name = self._meta.prefix + "_" + exp_name

        return exp_name

    def _get_sbatch_config(self):
        return "\n".join(
                [f"#SBATCH --{k}={v}" for k, v in self._sbatch.items()])
