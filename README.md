# LaunchPad
[![Build Status](https://circleci.com/gh/stanfordmlgroup/LaunchPad.svg?style=svg&circle-token=00b64008c5dc07a73a311815b5ca0e935291dbb3)](https://circleci.com/gh/stanfordmlgroup/LaunchPad)
[![CodeFactor](https://www.codefactor.io/repository/github/stanfordmlgroup/launchpad/badge)](https://www.codefactor.io/repository/github/stanfordmlgroup/launchpad)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) <br>
LaunchPad is a light-weighted Slurm job launcher designed for hyper-parameter search.

## Features
- Consolidated configuration file. 
- Random and grid hyper-parameter search.   
- Experiments status and metrics tracking.

## Installation 
```
 pip install git+https://github.com/stanfordmlgroup/LaunchPad.git
```

## Config file and example usage
Here is one config file (`example/config.yaml`):
```YAML
hp:
  lr:
    - 0.1
    - 0.5
  optimizer:
    - SGD
    - Adam
meta:
  gpus: 1
  mode: grid
  prefix: demo
  repeat: 1
  sandbox: ~/.launchpad  #optional; default to $HOME/.launchpad
  script: 'python main_key.py'
sbatch:
  exclude: deep[1-9]
```

You can print out the experiment CLI lists by `lp examples/config.yaml` or simply `cd examples && lp`:
```
$ lp
--------------------------------------------------------
Experiment No.1 -- [demo_key_0.1_SGD]:
python /sailhome/haosheng/workspace/LaunchPad/examples/main_key.py --lr 0.1 --optimizer SGD --round 0 --exp_name demo_key_0.1_SGD
Current State: Compiled
--------------------------------------------------------
Experiment No.2 -- [demo_key_0.1_Adam]:
python /sailhome/haosheng/workspace/LaunchPad/examples/main_key.py --lr 0.1 --optimizer Adam --round 0 --exp_name demo_key_0.1_Adam
Current State: Compiled
--------------------------------------------------------
Experiment No.3 -- [demo_key_0.5_SGD]:
python /sailhome/haosheng/workspace/LaunchPad/examples/main_key.py --lr 0.5 --optimizer SGD --round 0 --exp_name demo_key_0.5_SGD
Current State: Compiled
--------------------------------------------------------
Experiment No.4 -- [demo_key_0.5_Adam]:
python /sailhome/haosheng/workspace/LaunchPad/examples/main_key.py --lr 0.5 --optimizer Adam --round 0 --exp_name demo_key_0.5_Adam
Current State: Compiled
```

If you want auto-generate meaningful `exp_name` you can specify the `key` arguments under `meta` section:
```YAML
...
   key:
    - lr
    - optimizer
...
```
and, 
```
$ lp config_key.yaml
--------------------------------------------------------
Experiment No.1 -- [demo_key_0.1_SGD]:
python /sailhome/haosheng/workspace/LaunchPad/examples/main_key.py --lr 0.1 --optimizer SGD --round 0 --exp_name demo_key_0.1_SGD
Current State: Compiled
--------------------------------------------------------
Experiment No.2 -- [demo_key_0.1_Adam]:
python /sailhome/haosheng/workspace/LaunchPad/examples/main_key.py --lr 0.1 --optimizer Adam --round 0 --exp_name demo_key_0.1_Adam
Current State: Compiled
--------------------------------------------------------
Experiment No.3 -- [demo_key_0.5_SGD]:
python /sailhome/haosheng/workspace/LaunchPad/examples/main_key.py --lr 0.5 --optimizer SGD --round 0 --exp_name demo_key_0.5_SGD
Current State: Compiled
--------------------------------------------------------
Experiment No.4 -- [demo_key_0.5_Adam]:
python /sailhome/haosheng/workspace/LaunchPad/examples/main_key.py --lr 0.5 --optimizer Adam --round 0 --exp_name demo_key_0.5_Adam
Current State: Compiled
```

Once you think the configuration is ready, you can launch sbatch experiments:
```
lp config.yaml --run sbatch
```

Auto-generated sbatch scripts and logs can be found in `sbatch` and `log` folder under `sandbox` specified in the config. 

## Parameters
### Meta parameters
`meta` section contains all the parameters that control the compiling of the sbatch scripts. 
- `script`: The bash command line to run.
- `prefix`: A prefix tag that will be added to all `exp_name`.
- `sandbox`: A temp folder path to store all sbatch scripts and logs.
- `mode`: One of `["grid", "random"]`. Either to perform grid search or random search for the hyper-parameters combinations. 
- `repeat`: Round of repeat experiments. Only effective when `mode` is `grid`.
- `gpus`: Number of gpus to use. 
- `samples`: Number of total samples. Only effective when `mode` is `random`. 
- `keys`: Key experiment parameters to identify each experiment. The `exp_name` will be a underline concatenation of all the parameters specified here. If not given a random uuid is used as `exp_name`. 

### Sbatch parameters
`sbatch` section contains all extra parameters that will be passed to the sbatch. 
Please refer to [online sbatch documentation via SchedMD](https://slurm.schedmd.com/sbatch.html) for the complete list of parameters. 

### Experiment parameters
`hp` section is fully customized by user. They are hyper-parameters we want to scan for the training experiments. 
 
---
Maintainers: [@Hao](mailto:haosheng@cs.stanford.edu)
