import pickle
import os 
import platform
dir_path = os.path.dirname(os.path.realpath(__file__))

def save_data(data, name):
    path = dir_path + ("/data/%s.dat" % name)
    if platform.system() == "Windows":
        path = path.reaplce('/', '\\')
    f = open(path, "wb")
    pickle.dump(data, f)
    f.close()


def load_data(name):
    path = dir_path + ("/data/%s.dat" % name)
    if platform.system() == "Windows":
        path = path.reaplce('/', '\\')
    f = open(path, "rb")
    data = pickle.load(f)
    f.close()
    return data
    
