"""Gitlab API"""

# Python Libraries
import json
import re
from inspect import stack

# Program Libraries
from src.exceptions import (
    ElementNotFoundException
)
from src.request_maker import RequestMaker

class GitlabAPI(RequestMaker):
    """The GitLabAPI class is a subclass of RequestMaker
    and is responsible for making HTTP requests to Gitlab."""
    groups_uri = None
    subgroups_uri = None
    projects_uri = None
    project_search_by_name_uri = None
    project_tags_uri = None
    branches_uri = None

    def get_subgroups_of_group(self, group_name):
        """Fetches all the subgroups of a group (from gitlab).
        
        Args:
            group_name(string): The name of the group in gitlab.

        Returns:
            json_list(list): A list with dictionaries containing
                             info about the subgroups.

        """
        uri = self.subgroups_uri.format(group_name = group_name)
        json_list = self.recursive_request(uri, spinner_text = "subgroups")
        return json_list

    def get_projects_of_group(self, group_id):
        """Fetches all the projects of a group (from gitlab).

        Args:
            group_id(int): The id of the group. 
                           The id can be retrieved with:
                                (A) get_group_id_from_group_name for a group,
                                (B) get_subgroup_id_from_name for a subgroup. 

        Returns:
        json_list(list): A list with dictionaries containing
                         info about the projects.

        """
        uri = self.projects_uri.format(group_id = group_id)
        json_list = self.recursive_request(uri, spinner_text = "projects")
        return json_list

    def get_group_id_from_name(self, group_name):
        """Finds the group id from its name.

        Args:
            group_name(string): Group's name.

        Returns:
            (int): Group's id.

        """
        uri = self.groups_uri.format(group_name = group_name)
        response = self.make_request_and_expect_200(uri)
        group_info = json.loads(response.text)
        return group_info["id"]


    def get_subgroup_id_from_name(self, group_name, subgroup_name):
        """Finds the subgroup id from the name of the group it belongs to.
        
        Args:
            group_name(string): The name of the group to which the
                                subgroup belongs.
            subgroup_name(string): Subgroup's name.

        Returns: Subgroup's id.

        """
        json_list = self.get_subgroups_of_group(group_name)
        subgroup_id = self._get_id_from_name(json_list, subgroup_name)
        return subgroup_id

    def _get_id_from_name(self, json_list, name):
        """Finds the id of an element from a list with dictionaries.

        Args:
            json_list(list): A list with dictionaries
                             Each dictionary should contain 'id' and 'name' keys.
            name(string): The name of the element (value of 'name' key).        

        Returns:
            (int): The id of the element (value of 'id' key).

        """
        for element in json_list:
            if element["name"] == name:
                return element["id"]
        raise ElementNotFoundException(stack()[0], name)

    def get_project_id_from_project_name(self, project_name, group_name):
        """Finds the id of a project that belongs to a group.
        
        Args:
            project_name(string): Project's name.
            group_name(string): Group's name.

        Returns:
            (integer): THe id of the project.

        Raises:
            ElementNotFoundException: If the specified project is not found.

        """
        group_id = self.get_group_id_from_name(group_name)

        uri = self.project_search_by_name_uri.format(group_id = group_id)
        uri = uri.format(project_name = project_name)

        response = self.make_request_and_expect_200(uri)
        json_list = json.loads(response.text)

        for element in json_list:
            if element["name"] == project_name:
                return element["id"]

        raise ElementNotFoundException(stack()[0], project_name)

    def get_project_tags_from_project_id(self, project_id, deep_search = False):
        """Fetches info about the tags of a project from gitlab.
        If deep_search is set to True then all tags of this projects
        will be fetched, else only the last 50 tags will be fetched.

        Args:
            project_id(integer): Project's id.
            deep_search(boolean): If true, all tags of the project will be
                                  fetched.
                                  If False, only the last 50 tags will be fetched.
            
        Returns:
            json_list(list): A list with dictionaries containing
                             info about tags.

        """
        uri = self.project_tags_uri.format(project_id = project_id)
        json_list = self.recursive_request(uri, deep_search,
                                           spinner_text = f"project {project_id} tags")
        return json_list

    def get_branch_info(self, group_name, project_name, branch_name):
        """Fetches info about a branch from gitlab.

        Args:
            group_name(string): The name of the group to which the
                                project and the branch belong.
            project_name(string): The name of the project to which the
                                branch belongs.

        Returns:
            (list): A list with dictionaries containing info
                    about the branch.

        """
        project_id = self.get_project_id_from_project_name(project_name, group_name)
        uri = self.branches_uri.format(project_id = project_id) + f"/{branch_name}"
        spinner_text = f"info for branch {branch_name} of /{group_name}/{project_name}"
        response = self.make_request_and_display_spinner(uri, spinner_text)
        return json.loads(response.text)

    def find_tags_of_projects(self, projects_list, deep_search = False):
        """Fetches info about the tags of every project (in projects_list) 
        and constructs a list of dictionaries containing:
            - "name" : project name,
            - "id" : project id,
            - "tags" : a list with the name and title of each 
                       tag of the project.
        
        Args:
            projects_list(list): A list with dictionaries containing
                                 (at least):
                                    - "name" : Project name,
                                    - "id" : Project id.
            deep_search(boolean): If true, all tags of the project will be
                        fetched.
                        If False, only the last 50 tags will be fetched.

        Returns:
            project_tags(list): The constructed list of dictionaries.
                                    
        """
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
        """Finds the tags whose title starts with the given keyword.

        Args:
            tags_list(list): A list with dictionaries containing
                             (at least):
                                - "name" : Tag name e.g. 1.0.0,
                                - "title" : Tag title.
            keyword(string): The word with which the title should begin.
        
        Returns:
            matches(list): A list containing the matching tags

        """
        matches = []
        pattern = f"^{keyword.lower()}"
        for element in tags_list:
            title = element["title"].lower()
            if re.match(pattern, title):
                matches.append(element["name"])

        return matches

    def extract_project_name_and_id(self, json_list):
        """Constructs a new list with dictionaries containing only the
        name and the id of each project in the initial list.

        Args:
            json_list(list): A list with dictionaries containing
                             (at least):
                                - "name" : Project name,
                                - "id" : Project id.

        Returns:
            project_info(list): A list with dictionaries containing
                                only project's name and id.

        """

        project_info = []
        for element in json_list:
            project_info.append({
                "name" : element["name"],
                "id"   : element["id"]
            })
        return project_info

    def extract_tag_name_and_title(self, json_list):
        """Constructs a new list with dictionaries containing only the
        name and the commit title of each tag in the initial list.

        Args:
            json_list(list): A list with dictionaries containing
                             (at least):
                                - "name" : Tag name,
                                - "commit"."title"  : Commit title.
        Returns:
            tag_info(list): A list with dictionaries containing
                             only:
                                - "name" : Tag name,
                                - "title"  : Commit title.

        """

        tag_info = []
        for element in json_list:
            tag_info.append({
                "name"  : element["name"],
                "title" : element["commit"]["title"]
            })
        return tag_info
