# -*- coding: utf-8 -*-
"""
add cross validatio fold number to info csv
"""

import random
import datetime
import sys
import os

from dotenv import load_dotenv
import numpy as np
import pandas as pd

# load env
load_dotenv()
root = os.getenv("ROOT_PATH")

sys.path.append(f"{root}/src")
import tggate


def drop_lst(df, lst, name=""):
    for i in lst:
        df = df[df[name] != i]
    return df


# load
def main():
    info_df = pd.read_csv(f"{root}/data/processed/info.csv")
    print(info_df.shape)
    info_df = info_df.dropna(subset=["FILE"])
    print(info_df.shape)

    # extract compounds which have no sample of set times
    lst_compounds = list(set(info_df["COMPOUND_ABBR"]))
    lst_comp_exc = []
    for comp in lst_compounds:
        df_temp = info_df[info_df["COMPOUND_ABBR"] == comp]
        df_temp = df_temp[df_temp["DOSE"] != 0]
        times = set(df_temp["SACRI_PERIOD"])
        flag = False
        for time in set_times:
            if time not in times:
                flag = True
        if flag:
            print(comp)
            print(times)
            lst_comp_exc.append(comp)
    print(len(lst_comp_exc))
    # drop compounds
    info_df = drop_lst(info_df, lst_comp_exc, name="COMPOUND_ABBR")
    print(info_df.shape)
    # drop exclude times
    info_df = drop_lst(info_df, lst_time_exc, name="SACRI_PERIOD")
    print(info_df.shape)

    # extract highest concentration
    lst_compounds = list(set(info_df["COMPOUND_ABBR"]))
    lst_comp_conc = list()
    for comp in lst_compounds:
        df_temp = info_df[info_df["COMPOUND_ABBR"] == comp]
        df_temp = df_temp[df_temp["DOSE"] != 0]
        lst_conc = list(set(df_temp["DOSE"]))
        flag1 = False
        for conc in sorted(lst_conc, reverse=True):
            flag2 = True
            df_temp_conc = df_temp[df_temp["DOSE"] == conc]
            times = set(df_temp_conc["SACRI_PERIOD"])
            for time in set_times:
                df_temp_temp = df_temp_conc[df_temp_conc["SACRI_PERIOD"] == time]
                if len(df_temp_temp.index) < 3:
                    flag2 = False
                if time not in times:
                    flag2 = False
            if flag2:
                lst_comp_conc.append([comp, conc])
                break

    random.seed(seed)

    # extract control samples (one sample for each time point x each compound)
    df_ctrl = list()
    for i, comp in enumerate(lst_compounds):
        df_temp = info_df[info_df["COMPOUND_ABBR"] == comp]
        df_temp = df_temp[df_temp["DOSE"] == 0]
        for time in set_times:
            df_temp_time = df_temp[df_temp["SACRI_PERIOD"] == time]
            lst_number = list(range(df_temp_time.shape[0]))
            if len(lst_number) > 0:
                df_ctrl.append(df_temp_time.iloc[[random.choice(lst_number)], :])
    df_ctrl = pd.concat(df_ctrl, axis=0)
    print(f"control: {df_ctrl.shape}")

    # extract treatment samples (one sample for one indivisual ID)
    df_treat = list()
    for comp, conc in lst_comp_conc:
        df_temp = info_df[
            (info_df["COMPOUND_ABBR"] == comp) & (info_df["DOSE"] == conc)
        ]
        for time in set_times:
            df_temp_time = df_temp[df_temp["SACRI_PERIOD"] == time]
            for ind_id in set(df_temp_time["INDIVIDUAL_ID"]):
                df_temp_time_id = df_temp_time[df_temp_time["INDIVIDUAL_ID"] == ind_id]
                length = df_temp_time_id.shape[0]
                if length == 1:
                    df_treat.append(df_temp_time_id)
                else:
                    df_treat.append(
                        df_temp_time_id.iloc[[random.choice(list(range(length)))], :]
                    )
    df_treat = pd.concat(df_treat, axis=0)
    print(f"traet: {df_treat.shape}")

    # concat
    df_all = pd.concat([df_treat, df_ctrl], axis=0)
    print(df_all.shape)

    # Group
    df_all["GROUP"] = 100 * df_all["EXP_ID"] + df_all["GROUP_ID"]
    # Set folder
    df_all["DIR"] = tggate.utils.set_dir(
        df_all["SACRI_PERIOD"].tolist(), df_all["FILE"]
    )
    # Sampling from WSI
    df_all["SAMPLE"] = tggate.utils.sampling_patch_from_wsi(
        patch_number=patch_number, all_number=2000, len_df=len(df_all.index), seed=seed
    )
    # Set Folding
    df_all["FOLD"] = tggate.utils.make_groupkfold(df_all["GROUP"], n_splits=5)
    # export
    df_all.to_csv(f"{root}/data/processed/info_fold.csv", index=False)
    print(datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S"))


if __name__ == "__main__":
    #
    print(datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S"))
    seed = 24771
    patch_number = 200  # No. of patches / WSI
    set_times = {
        "3 hr",
        "6 hr",
        "9 hr",
        "24 hr",
        "4 day",
        "8 day",
        "15 day",
        "29 day",
    }
    lst_time_exc = [
        "72 hr",
    ]

    main()
