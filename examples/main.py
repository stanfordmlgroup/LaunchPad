import fire

def main(**kwargs):
    print("\tIn [main.py]: Start printing out the parameters passed in:")
    for k, v in kwargs.items():
        print(f"\t{k}: {v}")

if __name__ == "__main__":
    fire.Fire(main)
