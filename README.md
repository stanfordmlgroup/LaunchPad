# LaunchPad
[![Build Status](https://circleci.com/gh/stanfordmlgroup/LaunchPad.svg?style=svg&circle-token=00b64008c5dc07a73a311815b5ca0e935291dbb3)](https://circleci.com/gh/stanfordmlgroup/LaunchPad)
[![CodeFactor](https://www.codefactor.io/repository/github/stanfordmlgroup/launchpad/badge)](https://www.codefactor.io/repository/github/stanfordmlgroup/launchpad)
[![PyPI version](https://badge.fury.io/py/launch-pad.svg)](https://badge.fury.io/py/launch-pad)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) <br>
LaunchPad is a light-weighted Slurm job launcher designed for hyper-parameter search.

## Features
- Consolidated configuration file. 
- Integrated with Slurm cluster.
- Experiments status and metrics tracking.
- Support automl with [NNI](https://github.com/microsoft/nni) 🆕  

## Installation 
```
 pip install launch-pad
```
or
```
 pip install git+https://github.com/stanfordmlgroup/LaunchPad.git
```

## Config file and example usage
### Basic usage
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

### Auto `exp_name` generation 
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

Once you think the configuration is ready, you can launch slurm experiments:
```
lp config.yaml --run slurm
```

Auto-generated sbatch scripts and logs can be found in `sbatch` and `log` folder under `sandbox` specified in the config. 

### NNI integration 
Launchpad is also integrated with [NNI](https://github.com/microsoft/nni). By filling the `nni` section in the config file like `example/config_nni.yaml`, one can launch jobs like the following:
```
(launchpad) haosheng@deep21:~/workspace/LaunchPad$ lp examples/config_nni.yaml --run
Password:
Launching 2 slurm jobs:
sbatch: spank: option "x11" provided by both x11.so and x11.so
sbatch: spank: option "x11" provided by both x11.so and x11.so
Sleep 3 seconds before retrieving slurm jobs status ...
[2 / 2] is ready.
GPU resources is ready: ['deep14', 'deep10']
Dump HP json file to [/sailhome/haosheng/.launchpad/demo_nni/nni/demo_nni.json].
Dump nni config file to [/sailhome/haosheng/.launchpad/demo_nni/nni/demo_nni.yaml].
Output from NNI:
INFO:  Starting restful server...
INFO:  Successfully started Restful server!
INFO:  Setting remote config...
INFO:  Successfully set remote config!
INFO:  Starting experiment...
INFO:  Successfully started experiment!
------------------------------------------------------------------------------------
The experiment id is lyB7sHfD
The Web UI urls are: deep21.stanford.edu:8082
------------------------------------------------------------------------------------

You can use these commands to get more information about the experiment
------------------------------------------------------------------------------------
         commands                       description
1. nnictl experiment show        show the information of experiments
2. nnictl trial ls               list all of trial jobs
3. nnictl top                    monitor the status of running experiments
4. nnictl log stderr             show stderr log content
5. nnictl log stdout             show stdout log content
6. nnictl stop                   stop an experiment
7. nnictl trial kill             kill a trial job by id
8. nnictl --help                 get help information about nnictl
------------------------------------------------------------------------------------
Command reference document https://nni.readthedocs.io/en/latest/Tutorial/Nnictl.html
------------------------------------------------------------------------------------
```            

## Parameters
### Meta parameters
`meta` section contains all the parameters that control the compiling of the sbatch scripts. 
- `script`: The bash command line to run.
- `prefix`: A prefix tag that will be added to all `exp_name`.
- `sandbox`: A temp folder path to store all sbatch scripts and logs.
- `run`: One of `["shell", "slurm", "nni"]`. The job launching mode. Could be current shell (sequential, `"shell"`), slurm (`"slurm"`) or nni (via slurm, `"nni"`).
- `gpus`: Number of gpus to use. 
Following meta parameters are only effective when `run != "nni"`.
- `keys`: Key experiment parameters to identify each experiment. The `exp_name` will be a underline concatenation of all the parameters specified here. If not given a random uuid is used as `exp_name`. 
- `mode`: One of `["grid", "random"]`. Either to perform grid search or random search for the hyper-parameters combinations. 
- `repeat`: Round of repeat experiments. Only effective when `mode` is `grid`. 
- `samples`: Number of total samples. Only effective when `mode` is `random`. 

### Sbatch parameters
`sbatch` section contains all extra parameters that will be passed to the sbatch. 
Please refer to [online sbatch documentation via SchedMD](https://slurm.schedmd.com/sbatch.html) for the complete list of parameters. 

### Experiment parameters
`hp` section is fully customized by user. They are hyper-parameters we want to scan for the training experiments. 

### Data parameters
`data` section is optional and can be used to transfer data files (ie, hdf5 dataset) to a machine.
This is useful for preventing excessive reads from `/deep`.
- `src_paths`: list of paths that we want to transfer (ie, hdf5 dataset(s))
- `dst_dir`: path where we want to transfer `src_paths` (ie, `/scr`). `dst_dir` will be removed upon script completion.

### NNI parameters
`nni` section is optional and only effective when `run == "nni"`. A detailed description can be found [here](https://nni.readthedocs.io/en/latest/Tutorial/ExperimentConfig.html).

 
---
Maintainers: [@Hao](mailto:haosheng@cs.stanford.edu)
