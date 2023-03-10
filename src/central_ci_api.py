"""Central CI API."""

from src.constants import (
    CCI_GROUPS_URI,
    CCI_SUBGROUPS_URI,
    CCI_PROJECT_SEARCH_BY_NAME_URI,
    CCI_PROJECTS_URI,
    CCI_TAGS_URI,
    CCI_BRANCHES_URI
)
from src.gitlab_api import GitlabAPI

class CentralCIAPI(GitlabAPI):
    """The CentralCIAPI class is a subclass of GitlabAPI
    and is responsible for making requests to Nokia's Central CI
    Gitlab Repository (https://scm.cci.nokia.net/).
    """

    groups_uri = CCI_GROUPS_URI
    subgroups_uri = CCI_SUBGROUPS_URI
    project_search_by_name_uri = CCI_PROJECT_SEARCH_BY_NAME_URI
    projects_uri = CCI_PROJECTS_URI
    project_tags_uri = CCI_TAGS_URI
    branches_uri = CCI_BRANCHES_URI
