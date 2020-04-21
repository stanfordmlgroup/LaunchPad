# LaunchPad
---
LaunchPad is a quick sbatch launcher for hyper-parameter search.

## Features
- Consolidated configuration file. 
- Support random and grid hyperparameter search.   

## Installation 
```
 pip install git+https://github.com/haossr/LaunchPad.git
```

## Config file and example usage
Here is one config file (config.yaml):
```YAML
meta:
    script: python /deep/group/haosheng/LaunchPad/main.py
    sandbox: /deep/group/haosheng/temp/
    mode: grid 
    sample: 20
    repeat: 1
    gpus: 1
    logpath: /deep/group/haosheng/temp/log
    
hp: 
    lr: [0.1, 0.5]
    optimizer: [SGD, Adam]
```

You can print out the command lists by `lp config.py` or simply `lp`:
```
$ lp
python /deep/group/haosheng/LaunchPad/main.py --lr 0.1 --optimizer SGD --exp_name ff2623c422c8422a875af14545d3ce6f
python /deep/group/haosheng/LaunchPad/main.py --lr 0.1 --optimizer Adam --exp_name deaa30dce4344a888276c6097e7201b2
python /deep/group/haosheng/LaunchPad/main.py --lr 0.5 --optimizer SGD --exp_name ba68e25a460649e5888bb4e178e070f4
python /deep/group/haosheng/LaunchPad/main.py --lr 0.5 --optimizer Adam --exp_name 456744e1553e4726a4dfb9e02b530d7c
```

If you want auto-generate meaningful `exp_name` you can specify the `key` arguments under meta:
```YAML
...
    key: ['lr', 'optimizer']
...
```
and, 
```
$ lp config_key.yaml
python /deep/group/haosheng/LaunchPad/main.py --lr 0.1 --optimizer SGD --exp_name 0.1_SGD_round_0
python /deep/group/haosheng/LaunchPad/main.py --lr 0.1 --optimizer Adam --exp_name 0.1_Adam_round_0
python /deep/group/haosheng/LaunchPad/main.py --lr 0.5 --optimizer SGD --exp_name 0.5_SGD_round_0
python /deep/group/haosheng/LaunchPad/main.py --lr 0.5 --optimizer Adam --exp_name 0.5_Adam_round_0
```

Once you think the configuration is ready for launching over the cluster, you can run 
```
lp config.py --run sbatch
```





