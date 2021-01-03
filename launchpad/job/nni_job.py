import os
import yaml
import time
import copy
import sys
import uuid
import json
import re
import pkgutil
import pandas as pd
from subprocess import (check_call, 
                        check_output,
                        CalledProcessError)

from .base import BaseJob
from .slurm_job import SlurmJob
from .util import parse_time


class NNISlurmJob(SlurmJob):
    def __init__(self, config):
        _config = copy.deepcopy(config)
        # FIXME: only K gpu is visible per node if request K each time
        _config.meta.gpus = 4 
        _config.meta.pop("key", None)
        super().__init__(_config)
        self._exec_line = f"sleep {parse_time(config.nni.maxExecDuration)}"
    
    def _get_exp_name(self): 
        self._exp_name = self._meta.prefix + "_slurm_job_" + uuid.uuid4().hex


class NNIJob(BaseJob):
    def __init__(self, config): 
        super().__init__(config)
        self._config = config
        self._nni_hp_path = os.path.join(self._meta.nni_dir, f"{self._exp_name}.json")
        self._nni_config_path = os.path.join(self._meta.nni_dir, f"{self._exp_name}.yaml")
        self._slurm_jobs = []
        self._nodes = None

    def compile(self):
        self._compile_slurm_job()
        self._get_gpus()
        self._compile_hp()
        self._compile_nni_config()
        #with open(self._nni_config_path, 'w') as f:
        #    f.write(template)
        # TODO: NNI config
    
    
    def run(self): 
        self.compile()
        output = check_output(["nnictl", "create", "--config", self._nni_config_path])

    def cancel(self):
        #check_output(["nnictl", "stop"])
        self._release_gpus()

    def _get_gpus(self):
        for job in self._slurm_jobs:
            job.run()
            print(job._log_filepath)
        nodes = []
        while len(nodes) != len(self._slurm_jobs):
            print("Sleep 3 seconds before retrieving slurm jobs status...")
            time.sleep(3)
            nodes = []
            for job in self._slurm_jobs:
                info = job.get_info()
                if info is not None \
                   and info['state'] == 'R': 
                    nodes.append(info['nodelist'])
            print(f"[{len(nodes)} / {len(self._slurm_jobs)}] is ready.")
        self._nodes = set(nodes)
        print(f"GPU resources is ready: {list(self._nodes)}")

    def _release_gpus(self):
        for job in self._slurm_jobs:
            job.cancel()

    def _prompt_key(self):
        pass 

    def _compile_slurm_job(self):
        # FIXME: only K gpu is visible per node if request K each time
        for _ in range((self._meta.gpus+3) // 4):
            slurm_job = NNISlurmJob(self._config)
            self._slurm_jobs.append(slurm_job)

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

