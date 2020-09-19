import pickle
import os 
import platform
import pandas as pd
from misc import cached

dir_path = os.path.dirname(os.path.realpath(__file__))

def extract_all_raw_data():
    path = dir_path + "/raw_data"
    if platform.system() == "Windows":
        path = path.replace('/', '\\')
    directory = os.fsencode(path)
    dataframes = {}
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        filepath = os.path.join(path, filename)
        dataframes[filename.replace(".csv", "")] = pd.read_csv(filepath)
    return dataframes


def set_nan_values(df, column, value):
    df[column][df[column] != df[column]] = value

def remove_faulty_rows(dfs):
    set_nan_values(dfs["transactions"], "merchant_group_rk", -1)
    set_nan_values(dfs["transactions"], "category", "Другое")
    # set_nan_values(dfs["party_x_socdem"], "marital_status_desc", "Неизвестно")
    for name in dfs:
        print("Before cleansing: %d. " % len(dfs[name]), end="")
        for column in dfs[name].columns:
            dfs[name] = dfs[name][dfs[name][column].notna()]
        print("After cleansing: %d." % len(dfs[name]),)
    return dfs


def dump_dataframes(dfs):
    for name in dfs:
        save_data(dfs[name], name)

        
def extract_cleanse_and_dump_raw_data():
    dump_dataframes(remove_faulty_rows(extract_all_raw_data()))


def save_data(data, name):
    path = dir_path + ("/data/%s.dat" % name)
    if platform.system() == "Windows":
        path = path.replace('/', '\\')
    f = open(path, "wb")
    pickle.dump(data, f)
    f.close()


cache = {}

def load_data(name):
    global cache
    if name in cache:
        return cache[name]
    path = dir_path + ("/data/%s.dat" % name)
    if platform.system() == "Windows":
        path = path.replace('/', '\\')
    f = open(path, "rb")
    data = pickle.load(f)
    f.close()
    cache[name] = data
    return data

@cached
def get_subjects():
    return load_data("party_x_socdem")['party_rk'].to_list()
    
