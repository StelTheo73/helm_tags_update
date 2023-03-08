# Python Libraries
import json
import os
import os.path
import yaml

# Program Libraries
from CentralCIAPI import CentralCIAPI
from LegacyCIAPI import LegacyCIAPI
from contants import (
    GITLAB1_URI
)                      
from exceptions import (
    BranchNotFoundException,
    FetchInfoFailedException,
    PathNotFoundException
)
from utils import write_text_to_file

class KubernetesRequirementsYamlUpdater():
    default_project = "/tas/kubernetes"
    default_path = "/helm/nokia-tas"
    default_filename = "/requirements.yaml"
    target_branch = None
    yaml_uri = GITLAB1_URI +\
                "{project}" + "/raw" +\
                "/{branch}" + "{path}" + "{filename}"

    def __init__(self):
        self.central_ci_api = CentralCIAPI()
        self.legacy_ci_api = LegacyCIAPI()
        self.helm_project_tags = None

    def get_branch(self):
        while (self.target_branch == None):
            try:
                self.target_branch = self.get_branch_name()
            except BranchNotFoundException:
                continue

    def get_branch_name(self):
        message = "Type the target branch name: "
        error_message = "Branch name cannot be empty!"

        _, group, project = self.default_project.split("/")

        while (True):
            branch_input = input(message)

            if branch_input == "":
                print(error_message)
                continue

            try:
                response = self.legacy_ci_api.get_branch_info(group, project, branch_input)

                if response["name"] == branch_input:
                    return branch_input
                else:
                    exc_msg = "Fetched branch name and specified target branch name are different (\"{}\" != \"{}\")"\
                        .format(response["name"], branch_input)
                    raise BranchNotFoundException("get_branch", branch_input, exc_msg)
                
            except FetchInfoFailedException as exc:
                    exc_msg = "FetchInfoFailedException was raised."
                    
                    if "Response status code was: 404" in exc.__str__():
                        print("Branch \"{}\" was not found.\nMake sure it exists or check for typo.".format(branch_input))
                    raise BranchNotFoundException("get_branch", branch_input, exc_msg)
            
            except KeyError as exc:
                raise BranchNotFoundException("get_branch", branch_input, exc)

    def fetch_helm_tags(self):
        helm_subgroup_id = self.central_ci_api.get_subgroup_id_from_name("ntas", "helm")
        helm_projects = self.central_ci_api.get_projects_of_group(helm_subgroup_id)
        helm_projects = self.central_ci_api.extract_project_name_and_id(helm_projects)
        self.helm_project_tags = self.central_ci_api.find_tags_of_projects(helm_projects)

    def fetch_requirements_file(self):
        uri = self.yaml_uri.format(project = self.default_project,
                                   branch = self.target_branch,
                                   path = self.default_path,
                                   filename = self.default_filename)
        print(uri)
        response = self.legacy_ci_api._make_request(uri)
        write_text_to_file(str(response.text), "requirements.yaml", mode = "w")

    def update_tags(self):
        pass
