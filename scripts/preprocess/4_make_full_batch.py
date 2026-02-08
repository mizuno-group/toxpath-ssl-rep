# -*- coding: utf-8 -*-
"""
create batches for full-model training, evaluation of extrapolability
"""
# import
import gc
import os
from tqdm import tqdm
import datetime

from dotenv import load_dotenv
import pandas as pd
import numpy as np

# load env
load_dotenv()
root = os.getenv("ROOT_PATH")
HDD_TGGATES_DAYS = os.getenv("HDD_TGGATES_DAYS")
HDD_TGGATES_HOURS = os.getenv("HDD_TGGATES_HOURS")


def main():
    info_df = pd.read_csv(f"{root}/data/processed/info_fold.csv")
    info_df["SAMPLE"] = [
        [int(sample) for sample in sample_lst.split("[")[1].split("]")[0].split(", ")]
        for sample_lst in info_df["SAMPLE"]
    ]
    info_df = info_df.sample(frac=1, random_state=seed)
    lst_names = info_df["FILE"].tolist()
    lst_times = info_df["SACRI_PERIOD"].tolist()
    lst_samples = info_df["SAMPLE"].tolist()

    arr_res = np.zeros((0, 256, 256, 3), dtype=np.uint8)
    v = 0
    for i in tqdm(range(len(lst_names))):
        time = lst_times[i]
        name = lst_names[i]
        if "day" in time:
            folder = HDD_TGGATES_DAYS
        else:
            folder = HDD_TGGATES_HOURS
        # load / sampling
        with open(f"{folder}/patch/{time}/{name}.npy", "rb") as f:
            patch_arr = np.load(f)[lst_samples[i]].astype(np.uint8)
            arr_res = np.concatenate([arr_res, patch_arr])
            if ((i + 1) % 256 == 0) and (i != 0):  # 1 minibatch / 256 WSIs * 200 patch
                np.save(f"{folder}/batch_full/batch_{v}.npy", arr_res)
                arr_res = np.zeros((0, 256, 256, 3), dtype=np.uint8)
                v += 1
        gc.collect()
    # save last array
    np.save(f"{folder}/batch_full/batch_{v}.npy", arr_res)


if __name__ == "__main__":
    print(datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S"))  # time stamp
    seed = 24771  # random seed
    main()
    print(datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S"))  # time stamp
