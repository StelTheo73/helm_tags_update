"""Updater for requirements.yaml file"""

# Python Libraries
from inspect import stack
import os
import os.path
import yaml

# Program Libraries
from src.central_ci_api import CentralCIAPI
from src.legacy_ci_api import LegacyCIAPI
from src.constants import (
    GITLAB1_URI
)
from src.exceptions import (
    BranchNotFoundException,
    FetchInfoFailedException
)
from src.utils import (
    write_text_to_file
)

# Some helm projects do not have the same name as in
# the requirements.yaml file, so a map is added.
# Format:
# {"name-in-yaml-file" : "project-name"}
MAP_DIFFERENT_NAMES = {
    "anomaly-detector" : "anomaly",
    "auto-attendant"   : "autoattendant",
    "oapi-docs"        : "oapidocs",
    "sftp-server"      : "sftp",
    "ss7-mgmt"         : "ss7",
    "topology-routing-assistant" : "TopologyAndRoutingAssistant"
}

class RequirementsYamlUpdater():
    """The RequirementsYamlUpdater is responsible for updating requirements.yaml file
    from /tas/kubernetes/helm/nokia-tas with the official tags related to the specified branch.
    """
    default_project = "/tas/kubernetes"
    default_path = "/helm/nokia-tas"
    default_filename = "requirements.yaml"
    target_branch = None
    # URI to requirements.yaml file
    yaml_uri = GITLAB1_URI +\
                "{project}" + "/raw" +\
                "/{branch}" + "{path}" + "/{filename}"
    # Dictionary containing helm projects whose tag
    # could not be updated.
    failed_update = {}

    def __init__(self):
        """Instantiates a RequirementsYamlUpdater object.

        Creates a CentralCIAPI object to access Central CI.
        Creates a LegacyCIAPI object to access Legacy CI.

        """
        self.central_ci_api = CentralCIAPI()
        self.legacy_ci_api = LegacyCIAPI()

    def get_branch(self):
        """Executes iteratively get_branch_name inside a try-except block
           until a branch with the specified name is found in
           Central CI.
        """
        while (self.target_branch is None):
            try:
                self.target_branch = self.get_branch_name()
            except BranchNotFoundException:
                continue

    def get_branch_name(self):
        """Prompts user to give a branch name and fetches branch info 
        from Central CI.

        Ensures that branch_input is an existing branch in Central CI.

        Returns:
            branch_input(string): The branch name (if it was found in Central CI). 

        Raises:
            BranchNotFoundException: If the given branch is not found. 

        """
        message = "Type the target branch name: "
        error_message = "Branch name cannot be empty!"

        _, group, project = self.default_project.split("/")

        while True:
            branch_input = input(message)

            if branch_input == "":
                print(error_message)
                continue

            try:
                response = self.legacy_ci_api.get_branch_info(group, project, branch_input)

                if response["name"] == branch_input:
                    return branch_input
                else:
                    name = response["name"]
                    exc_msg = "Fetched branch name and specified target branch name " +\
                        f"are different (\"{name}\" != \"{branch_input}\")"
                    raise BranchNotFoundException(stack()[0], branch_input, exc_msg)

            except FetchInfoFailedException as exc:
                exc_msg = str(exc)
                if "Response status code was: 404" in exc_msg:
                    msg = f"\nBranch \"{branch_input}\" was not found. " +\
                        "Make sure it exists or check for typo.\n"
                    print(msg)
                raise BranchNotFoundException(stack()[0], branch_input, exc_msg) \
                    from exc
            except KeyError as exc:
                raise BranchNotFoundException(stack()[0], branch_input, exc) \
                    from exc

    def fetch_helm_tags(self, deep_search):
        """Fetches tags of the helm projects from gitlab.
        
        Args:
            deep_search(boolean): If true, all tags of the project will be
                                  fetched.
                                  If False, only the last 50 tags will be fetched.

        Returns:
            helm_project_tags(list): A list with dictionaries containing:
                                        - "name" : Project name,
                                        - "id" : Project id,
                                        - "tags" : Project tags.

        """
        helm_group_id = self.central_ci_api.get_subgroup_id_from_name("ntas", "helm")
        helm_projects_list = self.central_ci_api.get_projects_of_group(helm_group_id)
        helm_projects_list = self.central_ci_api.extract_project_name_and_id(helm_projects_list)
        helm_project_tags = self.central_ci_api.find_tags_of_projects(helm_projects_list,
                                                                      deep_search)

        return helm_project_tags

    def fetch_requirements_file(self):
        """Fetches requirements.yaml file from gitlab and saves it locally."""

        uri = self.yaml_uri.format(project = self.default_project,
                                   branch = self.target_branch,
                                   path = self.default_path,
                                   filename = self.default_filename)
        response = self.legacy_ci_api.make_request_and_expect_200(uri)
        write_text_to_file(str(response.text), self.default_filename, mode = "w")

    def get_changed_tags(self, deep_search = False):
        """Finds which tags have changed in the target branch.
        
        Args:
            deep_search(boolean): If true, all tags of the project will be
                                    checked.
                                    If False, only the last 50 tags will be checked.
            
        Returns:
            helm_projects_with_changed_tag(list): A list with dictionaries containing:
                                        - "name" : Project name,
                                        - "id" : Project id,
                                        - "tags" : Project tags related to target branch.

        """


        helm_projects_with_changed_tag = []
        
        helm_projects_with_tags = self.fetch_helm_tags(deep_search)

        helm_projects_with_changed_tag = self.find_projects_related_with_branch(helm_projects_with_tags)

        # for helm_project in helm_projects_with_changed_tag:
        #     helm_project["changed-tag"] = self.get_simple_tag(helm_project["tags"])

        return helm_projects_with_changed_tag

    def get_simple_tag(self, tags_list):
        """Selects one tag from the tags_list:
            
        Args:
            tags_list(list): A list containing tags.

        Returns:
            - First tag of the list : If tags_list contains only one tag,
            - "X.Y.Z" : If tags_list contains two tags, tag-1 = "X.Y.Z" and
              tag-2 = "vX.Y.Z",
        
        Raises:
            AssertionError:
                - If tags_list contains more than two tags,
                - If tags_list has two elements, but tag-1 = "X.Y.Z" and 
                  tag-2 = "vU.V.W"

        """
        simple_tag = ""
        v_tag = ""

        if len(tags_list) > 2:
            raise AssertionError

        if len(tags_list) == 1:
            return tags_list[0]

        if tags_list[0][0] == "v":
            v_tag = tags_list[0]
            simple_tag = tags_list[1]
        elif tags_list[1][0] == "v":
            v_tag = tags_list[1]
            simple_tag = tags_list[0]

        if (v_tag[1:] != simple_tag) or (simple_tag == ""):
            raise AssertionError

        return simple_tag

    def update_helm_tags(self, helm_projects_with_changed_tag):
        """Creates a yaml object (dictionary) from requirements.yaml file
        ad updates the tags that have changed.

        Args:
            helm_projects_with_changed_tag(list): A list with dictionaries containing
                                                  (at least):
                                                    - "name" : Project name,
                                                    - "tags" : Changed tags.

        Returns:
            yaml_object(dictionary): The yaml object with the new tags.
        
        """
        with open(self.default_filename, "r", encoding = "utf-8") as yaml_stream:
            yaml_object = yaml.safe_load(yaml_stream)

        # Transform the json object "helm_projects_with_changed_tag"
        # into a dict of the form: {'helm-name-1' : 'tag-1',
        #                           'helm-name-2' : 'tag-2',
        #                          . . . }
        # in order to reduce time complexity of the replacement operation:
        # O(n^2) [nested for loop] to O(2n) [2 individual for loops]
        helm_projects_with_changed_tag = \
            self.transform_list_of_dicts_to_single_kv_pair_dict(helm_projects_with_changed_tag,
                                                                "name",
                                                                "tags")
        helm_projects_with_changed_tag = \
            self.remove_helm_prefix_from_project_name(helm_projects_with_changed_tag)

        for yaml_helm_repo in yaml_object["dependencies"]:
            try:
                name = yaml_helm_repo["name"]

                if name in MAP_DIFFERENT_NAMES.keys():
                    name = MAP_DIFFERENT_NAMES[name]

                tags_list = helm_projects_with_changed_tag[name]
                new_tag = self.get_simple_tag(tags_list)

                if yaml_helm_repo["version"].split("-")[1] == "ntas":
                    yaml_helm_repo["version"] = new_tag + "-ntas"
                else:
                    yaml_helm_repo["version"] = new_tag

                helm_projects_with_changed_tag.pop(name)

            except (AssertionError, KeyError):
                continue

        self.failed_update = helm_projects_with_changed_tag

        return yaml_object

    def find_projects_related_with_branch(self, helm_projects_list_with_tags):
        """Finds which projects are associated with the target branch by comparing
        the title of each tag with the branch name.
        
        Args:
            helm_projects_with_tags(list): A list with dictionaries containing
                                           (at least):
                                            - "name" : Project name,
                                            - "id" : Project id,
                                            - "tags" : Project tags.

        Returns:
            related_projects(list): A list with dictionaries containing the
                                    projects that are related to the target branch.

        """
        related_projects = []
        tags_related_to_branch = None

        for helm_project in helm_projects_list_with_tags:
            tags = helm_project["tags"]

            # TODO : tags_related_to_branch = self.central_ci_api.match_tag_with_title(tags, self.target_branch)
            tags_related_to_branch = self.central_ci_api.match_tag_with_title(tags, "Update helm-common version to use new zts_BRM_labels")

            if len(tags_related_to_branch) > 0:
                helm_project["tags"] = tags_related_to_branch
                related_projects.append(helm_project)

        return related_projects

    def transform_list_of_dicts_to_single_kv_pair_dict(self, _list, key_for_key, key_for_value):
        _dict = {}
        for element in _list:
            name, id = element[key_for_key], element[key_for_value]
            _dict[name] = id
        return _dict

    def remove_helm_prefix_from_project_name(self, helm_projects_dict):
        helm_projects = {}
        
        for helm_project_name in helm_projects_dict.keys():
            if helm_project_name.split("-")[0] == "helm":
                new_name = helm_project_name[5:]
            else:
                new_name = helm_project_name
            helm_projects[new_name] = helm_projects_dict[helm_project_name]
        
        return helm_projects

    def write_yaml_to_file(self, yaml_object):
        comments_dict = self.find_comments()
        line_counter = 1

        os.rename(self.default_filename, "old.yaml")

        write_text_to_file("dependencies:\n", self.default_filename, mode = "w")
        line_counter += 1

        for element in yaml_object["dependencies"]:
            if line_counter in comments_dict.keys():
                write_text_to_file(comments_dict[line_counter], self.default_filename, mode = "a")
                line_counter += 1

            name = element["name"]
            version = element["version"]
            repository = element["repository"]

            write_text_to_file(f"  - name: {name}\n", self.default_filename, mode = "a")
            line_counter += 1
            write_text_to_file(f"    version: {version}\n", self.default_filename, mode = "a")
            line_counter += 1
            write_text_to_file(f"    repository: {repository}\n", self.default_filename, mode = "a")
            line_counter += 1

            if "alias" in element.keys():
                alias = element["alias"]
                write_text_to_file(f"    alias: {alias}\n", self.default_filename, mode = "a")
                line_counter += 1

            if "condition" in element.keys():
                condition = element["condition"]
                write_text_to_file(f"    condition: {condition}\n", self.default_filename, mode = "a")
                line_counter += 1
            
            if "metadata" in element.keys():
                metadata = element["metadata"]
                write_text_to_file(f"    metadata: {metadata}\n", self.default_filename, mode = "a")
                line_counter += 1

    def find_comments(self):
        comments_dict = {}
        line_counter = 1

        with open(self.default_filename, "r", encoding = "utf-8") as yaml_stream:
            for line in yaml_stream.readlines():
                if line[0].strip() == "#":
                    comments_dict[line_counter] = line
                line_counter += 1

        return comments_dict
