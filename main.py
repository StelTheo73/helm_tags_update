"""Main module."""

# Python Libraries
import json
import os
import os.path

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
from src.utils import write_text_to_file
from src.requirements_yaml_updater import RequirementsYamlUpdater

# Constants
PWD = os.getcwd()
REQUIREMENTS_YAML_FILE_PATH = os.path.join(PWD, REQUIREMENTS_YAML_FILE)

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

def main():
    """Main function.
    
    Removes remaining files from previous executions.
    Initializes RequirementsYamlUpdater.
    """

    # Remove remaining files from previous executions
    setup()

    # Initialize RequirementsYamlUpdater
    yaml_updater = RequirementsYamlUpdater()

    try:
        # Get target branch
        yaml_updater.get_branch()
        # Fetch requirements.yaml file from gitlab
        yaml_updater.fetch_requirements_file()
        # Find which tags have changed
        helm_projects_with_changed_tag = yaml_updater.get_changed_tags()
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
        print("\n\nExecution terminated by user.")
    except FetchInfoFailedException as exc:
        print(exc)
        print("\n\nUpdate failed!")
    except Exception as exc:
        print("\n\nUpdate failed!")
        raise FetchInfoFailedException("main", str(exc)) from exc


if __name__ == "__main__":
    # from src.central_ci_api import CentralCIAPI
    # import json
    # api = CentralCIAPI()
    # # json_list = api.get_subgroups_of_group("ntas")
    # # helm_id = api.get_project_id_from_project_name

    # jl = api.get_project_tags_from_project_id(8518)
    # print(json.dumps(jl, indent=2))
    
    main()
