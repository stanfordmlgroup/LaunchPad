import yaml
from sklearn.model_selection import ParameterGrid, ParameterSampler
from config import Config
import uuid
import fire

def launch(config="config.yaml"):
    config = Config(config)
    
    meta, hp = config.meta, config.hp
    for _ in range(meta.repeat):
        if meta.mode == "grid":
            config_list = list(ParameterGrid(hp))
        elif meta.mode == "random":
            config_list = list(ParameterSampler(hp, meta.sample))
            
        for idx, c in enumerate(config_list):
            c['exp_name'] = exp_name = uuid.uuid4().hex
            exec_line = f"python {meta.script} train" + " ".join([f"--{k} {v}" for k, v in c.items()])

            with open(f'{meta.sandbox}/{exp_name}.sh', 'w') as outfile:
                outfile.write("#!/bin/bash\n")
                outfile.write(f"rm -rf {meta.sandbox}/{exp_name}\n")
                outfile.write(f"rm -rf {meta.sandbox}/tb/{exp_name}\n")
                outfile.write(exec_line)
                
            with open(f'{meta.sandbox}/{exp_name}.sh', 'w') as outfile: