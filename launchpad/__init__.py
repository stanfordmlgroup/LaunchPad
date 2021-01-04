import yaml
from subprocess import check_call, check_output
import uuid
import fire
import time
import os
import pandas as pd
import logging
import shutil

from .job import Job
from .util import Config, Args


def run(config="config.yaml",
         run=False):
    if os.path.isdir(config):
        config = os.path.join(config, "config.yaml")
    
    _config = Config(config)

    if isinstance(run, str):
        _config.meta['run'] = run

    job = Job(_config)
    
    if run:
        job.run()
    else:
        job.compile()

def main():
    fire.Fire(run)

if __name__ == "__main__":
    fire.Fire(run)
