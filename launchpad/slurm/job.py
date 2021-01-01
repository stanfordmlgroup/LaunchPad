import os
import uuid
import re
from subprocess import check_call, check_output

from .smanager import Smanager
from util import colorful_state

class Job:
    def __init__(self, config):
        self._meta = config.meta
        self._hp = config.hp
        self._sbatch = config.sbatch
    

        self._id = None
        self._exec_line = f"{self._meta.script} " + \
                " ".join([f"--{k} {v}" for k, v in self._hp.items()])
        self._sbatch_config = "\n".join(
                [f"#SBATCH --{k}={v}" for k, v in self._sbatch.items()])
        self._get_exp_name()
        self._sbatch_filepath = os.path.join(self._meta.sandbox, f"{self._exp_name}.sh")
        self._log_filepath = os.path.join(self._meta.logpath, f"{self._exp_name}.log")
 
    
    def compile(self):
        #template = pkgutil.get_data(__name__, "scripts/sbatch_template.sh").decode()
        with open("scripts/sbatch_template.sh", "r") as f:
            template = f.read()
        template = template.replace("@GPUS", f"{self._meta.gpus}")
        template = template.replace("@LOG", f"{self._meta.logpath}")
        template = template.replace("@NAME", f"{self._exp_name}")
        template = template.replace("@CONFIG", f"{self._sbatch_config}")
        template = template.replace("@COMMAND", f"{self._exec_line}")
        with open(self._sbatch_filepath, 'w') as f:
            f.write(template)

    def get_state(self):
        state = None
        if self._id is None:
            if os.path.exists(self._log_filepath):
                state = "Finished"
            else:
                if os.path.exists(self._sbatch_filepath):
                    state = "Compiled"
                else:
                    state = "Unknown"
        else:
            cmd = ['squeue', '-j', self._id, '-o', self._format]
            smines = subprocess.check_output(cmd)
            smines = smines.decode('utf8').split('\n')
            states = [None for _ in range(len(smines) - 2)]
            for i, smine in enumerate(smines[1:-1]):
                smine = smine.split(' ')
                s = [s for s in smine if s is not '']
                states[i] = s[4]
            state = states[0]
            if state == "R":
                state = "Running"
            elif state == "PD":
                state = "Pending"

        return colorful_state(state)
    
    def get_metrics(self):
        pass

    def sbatch(self): 
        self.compile()
        output = check_output(f"sbatch {self._sbatch_filepath}", shell=True)
        x = re.findall("Submitted batch job \d+", str(output))
        self._id = int(x[0].split()[-1])

    def cancel(self):
        pass
    
    def _get_exp_name(self): 
        if "key" in self._meta:
            exp_name = "_".join([str(c[k]) for k in self._meta.key] \
                            + [f"{i}"])
        else:
            exp_name = uuid.uuid4().hex
        if "prefix" in self._meta:
            exp_name = self._meta.prefix + "_" + exp_name

        self._exp_name = exp_name

