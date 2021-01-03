import os
import uuid
import re
import pkgutil
import pandas as pd
from subprocess import (check_call, 
                        check_output,
                        CalledProcessError)
from .job import Job


class NNIJob(Job):
    def __init__(self, config): 
        super().__init__(config)
        
        self._nni_hp_path = os.path.join(self._meta.nni_dir, f"{self._exp_name}.json")
        self._nni_config_path = os.path.join(self._meta.nni_dir, f"{self._exp_name}.yaml")

    def compile(self):
        with open(self._nni_config_path, 'w') as f:
            f.write(template)
            # TODO: NNI config
        with open(self._nni_hp_path, 'w') as f:
            f.write(template)
            # TODO: NNI HP 
    
    
    def run(self): 
        self.compile()
        # TODO: NNI running CLI 
        self.gpus = self._get_gpus()
        output = check_output(["nnictl", self._sbatch_filepath])

    def cancel(self):
        check_output(["nnictl", "stop"])

    def _get_gpus(self):
        # TODO: get gpus using sbatch sleeping jobs
        pass
