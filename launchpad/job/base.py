import os
import uuid
import re
import pkgutil
import pandas as pd
from cachetools.func import ttl_cache
from subprocess import (check_call, 
                        check_output,
                        CalledProcessError)


class BaseJob:
    def __init__(self, config):
        self._meta = config.meta
        self._hp = config.hp
        self._sbatch = config.sbatch
        self._nni = config.nni
        
        self._get_exp_name()
        self._get_exec_line()
        self._log_filepath = os.path.join(self._meta.log_dir, f"{self._exp_name}.log")
 
    
    def compile(self):
        pass
            
    def get_state(self):
        raise NotImplementedError("Method [get_state(self)] has not been implemented!")
    
    def get_metrics(self):
        raise NotImplementedError("Method [get_metrics(self)] has not been implemented!")
    
    def run(self):
        raise NotImplementedError("Method [run(self)] has not been implemented!")

    def cancel(self):
        raise NotImplementedError("Method [cancel(self)] has not been implemented!")

    def shell(self): 
        try:
            check_call(self._exec_line.split())
        except CalledProcessError as e:
            print(e.output)

    def _get_metrics_path(self):
        metrics_path = self._meta.get("metrics_path", None)
        if metrics_path is None:
            raise ValueError("[metrics_path] has not been set up!")
        metrics_path = metrics_path.format(**self._hp)
        return metrics_path
        
    def _parse_script(self):
        script_items = tuple(self._meta.script.split())
        if len(script_items) == 2:
            executor, script_path = script_items 
            args = []
        else:
            executor, script_path, args = script_items 
            args = [args]
        config_path = self._meta.config_path
        script_path = os.path.abspath(os.path.join(os.path.dirname(config_path),
                                  script_path))
        return executor, script_path, args

    def _get_exec_line(self):
        executor, script_path, args = self._parse_script()
        self._code_dir = os.path.dirname(script_path)
        self._exec_line = " ".join([executor, script_path] + args \
                + [f"--{k} {v}" for k, v in self._hp.items()])

    def _get_exp_name(self): 
        if "key" in self._meta:
            exp_name = "_".join([str(self._hp[k]) for k in self._meta.key])
        else:
            exp_name = uuid.uuid4().hex
        if "prefix" in self._meta:
            exp_name = self._meta.prefix + "_" + exp_name
        self._exp_name = self._hp['exp_name'] = exp_name

    def _get_sbatch_config(self):
        return "\n".join(
                [f"#SBATCH --{k}={v}" for k, v in self._sbatch.items()])
