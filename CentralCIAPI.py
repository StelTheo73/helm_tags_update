from contants import (
    CCI_GROUPS_URI,
    CCI_SUBGROUPS_URI,
    CCI_PROJECT_SEARCH_BY_NAME_URI,
    CCI_PROJECTS_URI,
    CCI_TAGS_URI,
    CCI_BRANCHES_URI
)
from GitlabAPI import GitlabAPI

class CentralCIAPI(GitlabAPI):
    def __init__(self):
        super().__init__()

    groups_uri = CCI_GROUPS_URI
    subgroups_uri = CCI_SUBGROUPS_URI
    project_search_by_name_uri = CCI_PROJECT_SEARCH_BY_NAME_URI
    projects_uri = CCI_PROJECTS_URI
    project_tags_uri = CCI_TAGS_URI
    branches_uri = CCI_BRANCHES_URI

