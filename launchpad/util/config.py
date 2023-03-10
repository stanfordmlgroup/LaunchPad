import yaml
import os
import copy
from pathlib import Path
from sklearn.model_selection import ParameterGrid, ParameterSampler


class Args(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__.update(args[0])

    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        #self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            AttributeError("No such attribute: " + name)


class Config:
    def __init__(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Configuration file [{path}] not found!")
        with open(path, "r") as f:
            _config = yaml.load(f, Loader=yaml.SafeLoader)
        self.meta = Args(_config['meta'])
        self.meta['config_path'] = path

        if "sandbox" not in self.meta:
            self.meta.sandbox = "~/.launchpad"
        self.meta.sandbox = os.path.abspath(os.path.expanduser(self.meta.sandbox))
        self.meta.sandbox = os.path.join(self.meta.sandbox, self.meta.prefix)

        self.meta.log_dir = os.path.join(self.meta.sandbox, "log")
        self.meta.sbatch_dir = os.path.join(self.meta.sandbox, "sbatch")
        self.meta.nni_dir = os.path.join(self.meta.sandbox, "nni")
        os.makedirs(self.meta.log_dir, exist_ok=True) 
        os.makedirs(self.meta.sbatch_dir, exist_ok=True) 
        os.makedirs(self.meta.nni_dir, exist_ok=True) 

        self.hp = Args(_config['hp'])
        if 'sbatch' in _config:
            self.sbatch = Args(_config['sbatch'])
        else:
            self.sbatch = None
        if 'nni' in _config:
            self.nni = Args(_config['nni'])
        else:
            self.nni = None
            
        self.src_path = None 
        self.dst_dir = None
        if 'data' in _config:
            data = Args(_config['data'])
            if 'src_path' in data:
                if Path(data['src_path']).exists():
                    self.src_path = data['src_path']
                else:
                    print(f"Ignoring src_path - does not exist: [{data['src_path']}].")
            if 'dst_dir' in data:
                if (Path(data['dst_dir']).is_relative_to("/scr") and 
                    Path(data['dst_dir']).name != "scr"):
                    self.dst_dir = data['dst_dir']
                    if not self.dst_dir.endswith("/"):
                        self.dst_dir += "/"
                else:
                    print(f"Ignoring dst_dir - is not a subdirectory of /scr: [{data['dst_dir']}].")
    
    def __iter__(self):
        self.round = 0
        self._hp = copy.deepcopy(self.hp)
        self.params = iter(self._get_params_grid())
        return self

    def __next__(self):
        try:
            param = next(self.params)
            param['round'] = self.round
            self.hp = Args(param)
            return self
        except StopIteration:
            self.round += 1
            if self.round >= self.meta.repeat:
                self.hp = self._hp
                raise StopIteration
            self.params = iter(self._get_params_grid())
            return self.__next__()

    def _get_params_grid(self):
        if self.meta.mode == "grid":
            return ParameterGrid(self._hp)
        elif self.meta.mode == "random":
            return ParameterSampler(self._hp, self.meta.sample)
