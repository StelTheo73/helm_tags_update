"""Legacy CI API."""

from src.constants import (
    LCI_GROUPS_URI,
    LCI_SUBGROUPS_URI,
    LCI_PROJECT_SEARCH_BY_NAME_URI,
    LCI_PROJECTS_URI,
    LCI_TAGS_URI,
    LCI_BRANCHES_URI
)
from src.gitlab_api import GitlabAPI

class LegacyCIAPI(GitlabAPI):
    """The LegacyCIAPI class is a subclass of GitlabAPI
    and is responsible for making requests to Nokia's Legacy CI
    Gitlab Repository (https://gitlabe1.ext.net.nokia.com/).
    """

    groups_uri = LCI_GROUPS_URI
    subgroups_uri = LCI_SUBGROUPS_URI
    project_search_by_name_uri = LCI_PROJECT_SEARCH_BY_NAME_URI
    projects_uri = LCI_PROJECTS_URI
    project_tags_uri = LCI_TAGS_URI
    branches_uri = LCI_BRANCHES_URI
