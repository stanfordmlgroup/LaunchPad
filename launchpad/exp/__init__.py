from .slurm_job import SlurmJob 
from .shell_job import ShellJob
from .nni_job import NNIJob

def create_job(config):
    if config.meta.mode != 'nni':
        return SlurmJob(config)
    else:
        return NNIJob(config)

