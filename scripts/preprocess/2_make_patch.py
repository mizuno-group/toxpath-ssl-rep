# -*- coding: utf-8 -*-
"""
create patches from WSI files
"""
# import
import os
import sys
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

# import
sys.path.append(f"{root}/src")
from tggate.utils import make_patch


def main():
    df_all = pd.read_csv(f"{root}/data/processed/info_fold.csv", index_col=0)
    lst_compounds = list(set(df_all["COMPOUND_NAME"]))
    print(len(lst_compounds))
    print(len(lst_times))

    for time in lst_times:
        if "day" in time:
            folder = HDD_TGGATES_DAYS
        else:
            folder = HDD_TGGATES_HOURS

        for comp in tqdm(lst_compounds):
            df_temp = df_all[
                (df_all["SACRI_PERIOD"] == time) & (df_all["COMPOUND_NAME"] == comp)
            ]
            lst_names = df_temp["FILE"].tolist()
            for v, name in enumerate(lst_names):
                filein = f"{folder}/{time.replace(' ', '_')}/{name}"
                if os.path.isfile(f"{folder}/patch/{time}/{name}_sample.npy"):
                    pass

                else:
                    if os.path.isfile(filein):
                        try:
                            res, lst_number = make_patch(
                                filein=filein,
                                patch_size=patch_size,
                                patch_number=patch_number,
                                seed=seed,
                            )
                            # save
                            np.save(
                                f"{folder}/patch/{time}/{name}.npy",
                                res,
                            )
                            np.save(
                                f"{folder}/patch/{time}/{name}_sample.npy",
                                np.array(lst_number),
                            )

                        except:
                            print("Failed to load")
                            print(filein)

                    else:
                        print("Not Exist")
                        print(filein)


if __name__ == "__main__":
    print(datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S"))
    patch_size = 256
    patch_number = 2000  # per one WSI
    seed = 24771  # random seed

    lst_times = [
        "3 hr",
        "6 hr",
        "9 hr",
        "24 hr",
        "4 day",
        "8 day",
        "15 day",
        "29 day",
    ]
    main()
