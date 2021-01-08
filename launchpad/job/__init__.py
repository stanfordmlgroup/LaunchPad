from .slurm_job import SlurmJob 
from .shell_job import ShellJob
from .master_job import MasterJob
from .nni_job import NNISlurmJob, NNILocalJob

def Job(config):
    if config.nni is None:
        return MasterJob(config)
    else:
        if config.meta.get("run", "shell") == "shell":
            return NNILocalJob(config)
        else:
            return NNISlurmJob(config)
