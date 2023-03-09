from src.contants import (
    LCI_GROUPS_URI,
    LCI_SUBGROUPS_URI,
    LCI_PROJECT_SEARCH_BY_NAME_URI,
    LCI_PROJECTS_URI,
    LCI_TAGS_URI,
    LCI_BRANCHES_URI
)
from src.GitlabAPI import GitlabAPI

class LegacyCIAPI(GitlabAPI):
    def __init__(self):
        super().__init__()

    groups_uri = LCI_GROUPS_URI
    subgroups_uri = LCI_SUBGROUPS_URI
    project_search_by_name_uri = LCI_PROJECT_SEARCH_BY_NAME_URI
    projects_uri = LCI_PROJECTS_URI
    project_tags_uri = LCI_TAGS_URI
    branches_uri = LCI_BRANCHES_URI