import os
import yaml
import sys
import uuid
import json
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
        self._gpus = []

    def compile(self):
        self._compile_hp()
        self._compile_nni_config()
        #with open(self._nni_config_path, 'w') as f:
        #    f.write(template)
        # TODO: NNI config
    
    
    def run(self): 
        self._get_gpus()
        self.compile()
        output = check_output(["nnictl", "create", "--config", self._nni_config_path])

    def cancel(self):
        check_output(["nnictl", "stop"])
        self._release_gpus()

    def _get_gpus(self):
        for _ in range(self._meta.gpus):
            pass 
            # TODO: get gpus using sbatch sleeping jobs
        pass
    
    def _prompt_key(self):
        pass 

    def _compile_hp(self):
        hp_json_dict = {}
        for k, v in self._hp.items():
            hp_json_dict[k] = {"_type": "choice", "_value": v}
        with open(self._nni_hp_path, 'w') as f:
            json.dump(hp_json_dict, f)
        print(f"Dump HP json file to [{self._nni_hp_path}].")

    def _compile_nni_config(self): 
        self._nni['searchSpacePath'] = self._nni_hp_path
        self._nni['logDir'] = self._meta.nni_dir
        self._nni['trial'] = {"gpuNum": self._meta.gpus,
                              "command": self._exec_line,
                              "codeDir": self._code_dir}
        self._nni['trainingServicePlatform'] = "remote"

        with open(self._nni_config_path, 'w') as f:
            yaml.dump(dict(self._nni), f)

        print(f"Dump nni config file to [{self._nni_config_path}].")

    def _get_exp_name(self): 
        self._exp_name = self._meta.prefix

