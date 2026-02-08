# -*- coding: utf-8 -*-
"""
create batches for model training, evaluation of cross valudation accuracy
"""
# import
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
    # load
    info_df = pd.read_csv(f"{root}/data/processed/info_fold.csv", index_col=0)
    info_df["SAMPLE"] = [
        [int(sample) for sample in sample_lst.split("[")[1].split("]")[0].split(", ")]
        for sample_lst in info_df["SAMPLE"]
    ]
    _info_df = info_df[info_df["FOLD"] != 4]
    _info_df = _info_df.sample(frac=1, random_state=seed)
    lst_names = _info_df["FILE"].tolist()
    lst_times = _info_df["SACRI_PERIOD"].tolist()
    lst_samples = _info_df["SAMPLE"].tolist()

    # save
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
        patch_arr = np.load(f"{folder}/patch/{time}/{name}.npy")[lst_samples[i]].astype(
            np.uint8
        )
        arr_res = np.concatenate([arr_res, patch_arr])
        if ((i + 1) % 256 == 0) and (i != 0):  # 1 minibatch / 256 WSIs * 200 patch
            np.save(f"{folder}/batch/batch_{v}.npy", arr_res)
            arr_res = np.zeros((0, 256, 256, 3), dtype=np.uint8)
            v += 1
    np.save(f"{folder}/batch/batch_{v}.npy", arr_res)


if __name__ == "__main__":
    print(datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S"))
    patch_size = 256
    patch_number = 2000  # per one WSI
    seed = 24771  # random seed
    main()
