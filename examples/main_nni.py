import fire
import time
import os
import nni
import numpy as np
import pandas as pd

def main(**kwargs):
    wait = kwargs.get("wait")
    exp_name = kwargs.get("exp_name")
    
    metrics_path = os.path.expanduser(f"~/.launchpad/{exp_name}/metrics.csv")
    os.makedirs(os.path.dirname(metrics_path), exist_ok=True)

    print(f"\tIn [main_metrics.py] -- {exp_name}:")
    metrics = None
    while wait:
        time.sleep(1)
        wait -= 1
        metrics = {"timestamp": str(time.time()),
                   "accuracy": np.random.rand(),
                   "default": np.random.rand()}
        nni.report_intermediate_result(metrics) 
        print(f"Report intermediate metrics: {metrics}")
    
    nni.report_final_result(metrics) 
    print(f"Report final metrics: {metrics}")
    print(f"\tDone!")

if __name__ == "__main__":
    fire.Fire(main)
