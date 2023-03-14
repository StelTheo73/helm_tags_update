"""Module containing utility functions."""

# Python libraries
from datetime import datetime
import os
import os.path

# Program libraries
from src.constants import (
    EXECUTION_LOG_FILE,
    ERROR_LOG_FILE
)

def sort_list_dict_by_name(_dict):
    """Sorts the given dictionary by key "name".
    
    Args:
        _dict(dict): The dictionary to be sorted.

    Returns:
        (dict): The sorted dictionary
    """
    return sorted(_dict, key = lambda d: (d["name"]))

def write_text_to_file(text, file_name, mode = "w"):
    """Writes a text to the specified file.
    If the specified file is EXECUTION_LOG_FILE or ERROR_LOG_FILE,
    a time stamp is added in front of the text.

    Args:
        text(string): The text to be written.
        file_name(string): The name of the file.
        mode(string): The mode in which the file is opened (default is w).
    """

    if (file_name == EXECUTION_LOG_FILE) or (file_name == ERROR_LOG_FILE):
        text = add_timestamp_to_text(text)

    path = os.getcwd()
    path_to_file = os.path.join(path, file_name)

    with open(path_to_file, mode, encoding = "utf-8") as fstream:
        fstream.writelines(text)

def add_timestamp_to_text(text):
    """Adds a time stamp in front of a text.

    Args:
        text(string)

    Returns:
        (string): The text with a time stamp in front of it.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} {text}"

def is_string(obj):
    """Returns True if the given object's value is a string.

    Args:
        obj(object): The object to check.

    Returns:
        (bool): True if the given object's value is a string.
    """
    return isinstance(obj, str)
