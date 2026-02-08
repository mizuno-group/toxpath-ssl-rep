# -*- coding: utf-8 -*-
"""
create info csv files from tggates raw data.
notebooks/230406_preprocessing_info.ipynbを書き下したもの。
実際にrunしたことはない。
"""

import sys
import copy
import os
from collections import defaultdict

from dotenv import load_dotenv
import pandas as pd
import numpy as np


# load env
load_dotenv()
root = os.getenv("ROOT_PATH")


def main():
    # path for data folders
    ORIGINAL_DIR = f"{root}/data/original"
    PROCESSED_DIR = f"{root}/data/processed"

    # load raw data
    ind_df = pd.read_csv(
        f"{ORIGINAL_DIR}/open_tggates_individual.csv", encoding="shift_jis"
    )
    image_df = pd.read_csv(
        f"{ORIGINAL_DIR}/open_tggates_pathological_image.csv", encoding="shift_jis"
    )
    path_df = pd.read_csv(
        f"{ORIGINAL_DIR}/open_tggates_pathology.csv", encoding="shift_jis"
    )
    compound_df = pd.read_csv(
        f"{ORIGINAL_DIR}/tggates_in_vivo_compound_info.txt",
        encoding="shift_jis",
        sep="\t",
    )

    ind_df.columns = [i.upper() for i in ind_df.columns]
    image_df.columns = [i.upper() for i in image_df.columns]
    path_df.columns = [i.upper() for i in path_df.columns]
    compound_df.columns = [i.upper() for i in compound_df.columns]

    image_df = image_df[image_df["ORGAN"] == organ]
    path_df = path_df[path_df["ORGAN"] == organ]
    # sort kidney first and delete duplicates
    compound_df = compound_df.sort_values(by="ORGAN")
    compound_df = compound_df.drop_duplicates(subset="COMPOUND_NAME")

    ind_df["INDV_ID"] = (
        ind_df["EXP_ID"] * 1000 + ind_df["GROUP_ID"] * 10 + ind_df["INDIVIDUAL_ID"]
    )

    image_df["INDV_ID"] = (
        image_df["EXP_ID"] * 1000
        + image_df["GROUP_ID"] * 10
        + image_df["INDIVIDUAL_ID"]
    )
    path_df["INDV_ID"] = (
        path_df["EXP_ID"] * 1000 + path_df["GROUP_ID"] * 10 + path_df["INDIVIDUAL_ID"]
    )
    ind_df["COMPOUND_NAME"] = ind_df["COMPOUND_NAME"].where(
        ind_df["COMPOUND_NAME"] != "TNFﾎｱ", "TNFα"
    )
    finding_lst = list(set(path_df["FIND_TYPE"].dropna()))
    print(len(finding_lst))
    one_hot = pd.get_dummies(
        path_df[["INDV_ID", "FIND_TYPE"]].dropna(),
        columns=["FIND_TYPE"],
        prefix="",
        prefix_sep="",
    )
    one_hot = one_hot.groupby("INDV_ID").max()
    ind_ft_df = pd.merge(ind_df, one_hot, on="INDV_ID", how="left").fillna(0)
    ind_ft_com_df = pd.merge(
        ind_ft_df,
        compound_df[["COMPOUND_NAME", "VEHICLE"]],
        on="COMPOUND_NAME",
        how="left",
    )

    ind_ft_com_df["COMPOUND_NAME"] = ind_ft_com_df["COMPOUND_NAME"].where(
        ind_ft_com_df["DOSE"] != 0, ind_ft_com_df["VEHICLE"]
    )
    compound_list = list(set(ind_ft_com_df["COMPOUND_NAME"]))
    # saving the compound list
    open(f"{PROCESSED_DIR}/compound_list.txt", "w").write(
        "\n".join(compound_list) + "\n"
    )

    one_hot = pd.get_dummies(
        ind_ft_com_df[["INDV_ID", "COMPOUND_NAME"]], prefix="", prefix_sep=""
    )
    ind_ft_com_df = pd.merge(ind_ft_df, one_hot, on="INDV_ID", how="left")
    image_df["FILE"] = [f[-1] for f in image_df["FILE_LOCATION"].str.split("/")]
    info_df = pd.merge(
        ind_ft_com_df,
        image_df[["INDV_ID", "FILE", "FILE_LOCATION"]],
        on="INDV_ID",
        how="left",
    )
    info_df.to_csv(f"{PROCESSED_DIR}/info.csv", index=False)


if __name__ == "__main__":
    # seed for control sampling
    seed = 24771
    # target organ
    organ = "Liver"
    main()
