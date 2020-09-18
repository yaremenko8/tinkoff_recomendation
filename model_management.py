import pickle
import os 
import platform
dir_path = os.path.dirname(os.path.realpath(__file__))

def save_model(model, name):
    try:
        model = model.fitted_pipeline_
    except AttributeError:
        pass
    path = dir_path + ("/models/%s.mdl" % name)
    if platform.system() == "Windows":
        path = path.reaplce('/', '\\')
    f = open(path, "wb")
    pickle.dump(model, f)
    f.close()


def load_model(name):
    path = dir_path + ("/models/%s.mdl" % name)
    if platform.system() == "Windows":
        path = path.reaplce('/', '\\')
    f = open(path, "rb")
    model = pickle.load(f)
    f.close()
    return model
    
