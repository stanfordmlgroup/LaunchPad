import fire
import time

def main(**kwargs):
    wait = kwargs.get("wait")
    print(f"\tIn [main_wait.py]: Start counting down {wait} seconds:")
    while wait:
        time.sleep(1)
        wait -= 1
        print(f"\t{wait}..")
    print(f"\tDone!")
if __name__ == "__main__":
    fire.Fire(main)
