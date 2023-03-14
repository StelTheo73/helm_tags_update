"""Main module."""

# Python Libraries
import getopt
import json
import os
import os.path
import sys

# Program Libraries
from src.constants import (
    REQUIREMENTS_YAML_FILE,
    OLD_YAML_FILE,
    EXECUTION_LOG_FILE,
    ERROR_LOG_FILE
)
from src.exceptions import (
    FetchInfoFailedException
)
from src.utils import (
    is_string,
    write_text_to_file)
from src.requirements_yaml_updater import RequirementsYamlUpdater

# Constants
PWD = os.getcwd()
REQUIREMENTS_YAML_FILE_PATH = os.path.join(PWD, REQUIREMENTS_YAML_FILE)

def print_help():
    """Prints help message."""
    msg = """Options:
    -h, --help                          : Display help.
    -b, --branch <string: branch-name>  : (optional) The target branch for /tas/kubernetes project, 
                                                        can be specified later.
    -d, --deep <bool: True/False>       : (optional) 
                                            - [True / 1]  --> All tags of each helm project will be
                                                                fetched.
                                            - [False / 0] --> (default) Only the last 50 tags of each
                                                                helm project will be fetched.
        """
    print(msg)

def parse_arguments(argv):
    """Parses the provided arguments."""
    arg_branch = None
    arg_deep = False
    #arg_help = "{0} -b <branch name> -d <deep-search>".format(argv[0]) 

    try:
        opts, _ = getopt.getopt(argv[1:], "h:b:d:", ["help", "branch=", "deep="])
    except Exception:
        print_help()
        sys.exit(1)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_help()
            sys.exit(0)
        elif opt in ["-b", "--branch"]:
            if not is_string(arg):
                print_help()
                sys.exit(1)
            arg_branch = arg
        elif opt in ["-d", "--deep"]:
            if (not is_string(arg)) or (arg.capitalize() not in ("True", "False", "1", "0")):
                print_help()
                sys.exit(1)
            if arg.capitalize() in ("True", "1"):
                arg_deep = True
                # default is False

    return arg_branch, arg_deep

def setup():
    """Removes files created from previous execution."""

    files = [REQUIREMENTS_YAML_FILE, OLD_YAML_FILE, EXECUTION_LOG_FILE, ERROR_LOG_FILE]

    for file in files:
        _file = os.path.join(PWD, file)
        if os.path.exists(_file):
            os.remove(_file)

def success():
    """Prints the location of the updated file."""

    msg = "\nSUCCESS\n" +\
        f"{REQUIREMENTS_YAML_FILE} updated successfully.\n" +\
        "Move the file to your local kubernetes repository and\n" +\
        "commit your changes to gitlab.\n" +\
        f"File location: {REQUIREMENTS_YAML_FILE_PATH}\n"

    print(msg)
    write_text_to_file(msg, EXECUTION_LOG_FILE, mode = "a")

def partial_failure(failed):
    """Prints the location of the updated file and
    the helm projects whose tag could not be updated.
    """

    msg = "\nPARTIAL FAILURE\n" +\
        "Some tags could not be updated.\n" +\
        "Projects affected:\n" +\
        json.dumps(failed, indent=2) +\
        "\n\nYou have to update these tags manually.\n" +\
        "Then, move the file to your local kubernetes repository and\n" +\
        "commit your changes to gitlab.\n" +\
        f"File location: {REQUIREMENTS_YAML_FILE_PATH}\n"

    print(msg)
    write_text_to_file(msg, EXECUTION_LOG_FILE, mode = "a")
    write_text_to_file(msg, ERROR_LOG_FILE, mode = "a")

def failure(exception):
    """Prints failure message."""

    msg = "\nFAILURE\n" +\
        f"Reason: \n{exception}\n" +\
        f"See {ERROR_LOG_FILE} for more info.\n"

    print(msg)
    write_text_to_file(msg, EXECUTION_LOG_FILE, mode = "a")
    write_text_to_file(msg, ERROR_LOG_FILE, mode = "a")

def main(branch, deep_search):
    """Main function.
    
    Initializes RequirementsYamlUpdater and updates the tags.

    Args:
        branch(string): The target branch in /tas/kubernetes
        deep_search(boolean):
    """

    # Initialize RequirementsYamlUpdater
    yaml_updater = RequirementsYamlUpdater()
    yaml_updater.target_branch = branch

    try:
        # Get target branch
        yaml_updater.get_branch()
        # Fetch requirements.yaml file from gitlab
        yaml_updater.fetch_requirements_file()
        # Find which tags have changed
        helm_projects_with_changed_tag = yaml_updater.get_changed_tags(deep_search)
        # Update tags with the new ones
        updated_yaml_object = yaml_updater.update_helm_tags(helm_projects_with_changed_tag)
        # Write changes to requirements.yaml
        yaml_updater.write_yaml_to_file(updated_yaml_object)

        failed = yaml_updater.failed_update

        if not failed:
            success()
        else:
            partial_failure(failed)

    except KeyboardInterrupt:
        failure("Execution terminated by user.")
    except (FetchInfoFailedException, Exception) as exc:
        failure(str(exc))

if __name__ == "__main__":
    branch, deep_search = parse_arguments(sys.argv)
    # Remove remaining files from previous executions
    setup()
    main(branch, deep_search)
