import yaml
import os


class Args(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__.update(args[0])

    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

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
        self.hp = Args(_config['hp'])
