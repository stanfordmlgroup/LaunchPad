import fire
import time
import os
import nni
import numpy as np
import pandas as pd

def main(**kwargs):
    params = nni.get_next_parameter()
    wait = params.get("wait")
    exp_name = "nni" + str(time.time())
    
    print(f"\tIn [main_metrics.py] -- {exp_name}")
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
