import os
import yaml
import sys
import shutil
import time
import socket
import copy
import uuid
import json
import getpass
import traceback
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
        self._duration = parse_time(config.nni.maxExecDuration)
        self._nni_hp_path = os.path.join(self._meta.nni_dir, f"{self._exp_name}.json")
        self._nni_config_path = os.path.join(self._meta.nni_dir, f"{self._exp_name}.yaml")
        self._slurm_jobs = []
        self._nodes = None

    def compile(self):
        self._prompt_key()
        self._compile_slurm_job()
        self._get_gpus()
        self._compile_hp()
        self._compile_nni_config()
    
    
    def run(self): 
        self.compile()
        try:
            output = check_output(["nnictl", "create", 
                        "--config", self._nni_config_path, 
                        "--port", str(self._meta.port)])
            print("Output from NNI:")
            print(output.decode("utf-8"))
            os.remove(self._nni_config_path)
            print(f"Removed nni config file [{self._nni_config_path}].")

        except CalledProcessError as e:
            print(f"Error from NNI (return code={e.returncode}):")
            print(e.output.decode("utf-8"))
            raise e

        try:
            time.sleep(self._duration)
        except KeyboardInterrupt:
            print('Stopped by user')
            try:
                self.cancel()
                sys.exit(0)
            except SystemExit:
                os._exit(0)


    def cancel(self):
        check_output(["nnictl", "stop"])
        if os.path.isfile(self._nni_config_path):
            os.remove(self._nni_config_path)
        self._release_gpus()
    
    def __del__(self):
        self.cancel()

    def _get_gpus(self):
        print(f"Launching {len(self._slurm_jobs)} slurm jobs: ")
        for job in self._slurm_jobs:
            job.run()

        nodes = []
        while len(nodes) != len(self._slurm_jobs):
            print("Sleep 3 seconds before retrieving slurm jobs status ...")
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
        if len(self._nodes) == 0:
            return

        print(f"Release GPU resources {list(self._nodes)} ...")

        for job in self._slurm_jobs:
            job.cancel()
        self._nodes = []

    def _prompt_key(self):
        self._passwd = getpass.getpass()

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
        # FIXME: allow more than 1 gpus per trial
        self._nni['trial'] = {"gpuNum": 1,
                              "command": self._exec_line,
                              "codeDir": self._code_dir}
        self._nni['trainingServicePlatform'] = "remote"

        username = os.environ['USER']
        machine_list = []
        conda_env = os.environ['CONDA_DEFAULT_ENV']
        pre_command = f"conda deactivate && conda activate {conda_env}"
        for node in self._nodes:
            machine_list.append({"ip": node + ".stanford.edu",
                                 "username": username,
                                 "passwd": self._passwd, 
                                 "useActiveGpu": True,
                                 "maxTrialNumPerGpu": 1,
                                 "preCommand": pre_command})
        self._nni['machineList'] = machine_list
        self._nni['nniManagerIp'] = socket.gethostname()

        with open(self._nni_config_path, 'w') as f:
            yaml.dump(dict(self._nni), f)

        print(f"Dump nni config file to [{self._nni_config_path}].")

    def _get_exp_name(self): 
        self._exp_name = self._meta.prefix
    
    def _get_exec_line(self):
        executor, script_path = self._meta.script.split()
        config_path = self._meta.config_path
        script_path = os.path.abspath(os.path.join(os.path.dirname(config_path),
                                      script_path))
        self._code_dir = os.path.dirname(script_path)
        self._exec_line = " ".join([executor, script_path])

