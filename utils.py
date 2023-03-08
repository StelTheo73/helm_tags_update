import os
import os.path

def sort_list_dict_by_name(_dict):
    return sorted(_dict, key = lambda d: (d["name"]))

def write_text_to_file(text, file_name, path = None, mode = "w"):
    if not path:
        path = os.getcwd()
    
    if not os.path.isdir(path):
        raise NotADirectoryError

    path_to_file = os.path.join(path, file_name)

    with open(path_to_file, mode) as fstream:
            fstream.writelines(text)
    