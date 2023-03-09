# Python Libraries
import json
import re
from inspect import stack
from halo import Halo

# Program Libraries
from src.exceptions import (
    ElementNotFoundException,
    FetchInfoFailedException
)
from src.RequestMaker import RequestMaker

class GitlabAPI(RequestMaker):
    groups_uri = None
    subgroups_uri = None
    projects_uri = None
    project_search_by_name_uri = None
    project_tags_uri = None
    branches_uri = None

    def __init__(self):
        super().__init__()

    def recursive_request(self, uri, deep_search = True, spinner_text = None):
        page_number = 1
        json_list = []
        spinner_text = "Fetching {}...".format(spinner_text)
        spinner = Halo(text = spinner_text, spinner = "dots")
        spinner.start()
        
        while True:
            page_uri = uri.format(page_number = page_number)

            try:
                response = self._make_request(page_uri)
            except FetchInfoFailedException:
                spinner.fail(text = spinner_text)
                caller = stack()[0].function
                msg = "RequestFailedException was raised."
                raise   FetchInfoFailedException(caller, msg)

            if response.text == "[]":
                break
            json_list += json.loads(response.text)

            if not(deep_search):
                break

            page_number +=1

        spinner.succeed(text = spinner_text)

        return json_list

    def get_subgroups_of_group(self, group_name):
        uri = self.subgroups_uri.format(group_name = group_name)
        json_list = self.recursive_request(uri, spinner_text = "subgroups")
        return json_list

    def get_projects_of_group(self, group_id):
        uri = self.projects_uri.format(group_id = group_id)
        json_list = self.recursive_request(uri, spinner_text = "projects")
        return json_list

    def get_group_id_from_name(self, group_name):
        uri = self.groups_uri.format(group_name = group_name)
        response = self._make_request(uri)
        group_info = json.loads(response.text)
        if group_info["name"] == group_name:
            return group_info["id"]
        else:
            raise ElementNotFoundException("get_group_id_from_name", group_name)

    def get_subgroup_id_from_name(self, group_name, subgroup_name):
        json_list = self.get_subgroups_of_group(group_name)
        subgroup_id = self._get_id_from_name(json_list, subgroup_name)
        return subgroup_id

    def _get_id_from_name(self, json_list, name):
        for element in json_list:
            if element["name"] == name:
                return element["id"]
        raise ElementNotFoundException("_get_id_from_name", name)

    def get_project_id_from_project_name(self, project_name, group_name):
        id = self.get_group_id_from_name(group_name)
        uri = self.project_search_by_name_uri.format(group_id = id)
        uri = uri.format(project_name = project_name)

        response = self._make_request(uri)
        json_list = json.loads(response.text)

        for element in json_list:
            if element["name"] == project_name:
                return element["id"]
        
        raise ElementNotFoundException("get_project_id_from_project_name", project_name)

    def get_project_tags_from_project_id(self, project_id, deep_search = False):
        uri = self.project_tags_uri.format(project_id = project_id)
        json_list = self.recursive_request(uri, deep_search, spinner_text = "project {} tags".format(project_id))
        return json_list

    def get_branch_info(self, group_name, project_name, branch_name):
        project_id = self.get_project_id_from_project_name(project_name, group_name)
        uri = self.branches_uri.format(project_id = project_id) + "/{}".format(branch_name)
        response = self._make_request(uri)
        return json.loads(response.text)

    def find_tags_of_projects(self, projects_list, deep_search = False):
        projects_tags = []
        for project in projects_list:
            tags_list = self.get_project_tags_from_project_id(project["id"], deep_search)
            tags_list = self.extract_tag_name_and_title(tags_list)
            projects_tags.append({
                "name"  : project["name"],
                "id"    : project["id"],
                "tags"  : tags_list
            })
        return  projects_tags

    def match_tag_with_title(self, tags_list, keyword):
        """Returns the first tag whose title starts with the given keyword."""
        matches = []
        pattern = "^{}".format(keyword.lower())
        for element in tags_list:
            title = element["title"].lower()
            if re.match(pattern, title):
                matches.append(element["name"])
        
        return matches

    def extract_project_name_and_id(self, json_list):
        project_info = []
        for element in json_list:
            project_info.append({
                "name" : element["name"],
                "id"   : element["id"]
            })
        return project_info

    def extract_tag_name_and_title(self, json_list):
        tag_info = []
        for element in json_list:
            tag_info.append({
                "name"  : element["name"],
                "title" : element["commit"]["title"]
            })
        return tag_info
