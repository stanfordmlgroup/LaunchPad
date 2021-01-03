from .slurm_job import SlurmJob 
from .shell_job import ShellJob
from .master_job import MasterJob
from .nni_job import NNIJob

def Job(config):
    if config.meta.get("run", None) == 'nni':
        return NNIJob(config)
    else:
        return MasterJob(config)
