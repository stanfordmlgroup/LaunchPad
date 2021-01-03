import os
import uuid
import re
import pkgutil
import pandas as pd
from cachetools.func import ttl_cache
from subprocess import (check_call, 
                        check_output,
                        CalledProcessError)

from .base import BaseJob

class ShellJob(BaseJob):
    def __init__(self, config):
        super().__init__(config)
        self._state = "Compiled"

    def get_state(self):
        return self._state

    def run(self): 
        try:
            check_call(self._exec_line.split())
            self.state = "Finished"
        except CalledProcessError as e:
            self.state = "Failed"
            print(e.output)
