import fire
import time
import os
import numpy as np
import pandas as pd

def main(**kwargs):
    wait = kwargs.get("wait")
    exp_name = kwargs.get("exp_name")
    
    metrics_path = f"~/.launchpad/{exp_name}/metrics.csv"
    os.makedirs(os.path.dirname(metrics_path), exist_ok=True)

    print(f"\tIn [main_metrics.py] -- {exp_name}:")
    rows = []
    while wait:
        time.sleep(1)
        wait -= 1
        rows.append({"timestamp": str(time.time()),
                     "accuracy": np.random.rand(),
                     "f1": np.random.rand()})
        pd.DataFrame(rows).to_csv(metrics_path, index=False)
        print(f"\t{wait}.. write to file {metrics_path}")
    print(f"\tDone!")

if __name__ == "__main__":
    fire.Fire(main)
