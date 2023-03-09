# ------------------- URIs & PATHS -------------------

# Gitlab URIs
GITLAB_URI  = "https://scm.cci.nokia.net"
GITLAB1_URI = "https://gitlabe1.ext.net.nokia.com"
API_V4 = "/api/v4"
GITLAB_API_URI_V4  = GITLAB_URI + API_V4
GITLAB1_API_URI_V4 = GITLAB1_URI + API_V4

# URI Paths
GROUPS_PATH    = "/groups/{group_name}"
SUBGROUPS_PATH = "/groups/{group_name}/subgroups" +\
                    "?page={{page_number}}&per_page=50"
PROJECT_SEARCH_BY_NAME_PATH = "/groups/{group_id}/projects?search={{project_name}}"
PROJECTS_PATH  = "/groups/{group_id}/projects" +\
                    "?include_subgroups=true&page={{page_number}}&per_page=50"
TAGS_PATH      = "/projects/{project_id}/repository/tags" +\
                    "?order_by=updated&page={{page_number}}&per_page=50"
FILE_PATH      = "/projects/{project_id}/repository/files/{{path_to_file}}"
BRANCH_PATH    = "/projects/{project_id}/repository/branches"

# Full URIs
# CCI -> URI for Central CI
CCI_GROUPS_URI = GITLAB_API_URI_V4 + GROUPS_PATH
CCI_SUBGROUPS_URI = GITLAB_API_URI_V4 + SUBGROUPS_PATH
CCI_PROJECT_SEARCH_BY_NAME_URI = GITLAB_API_URI_V4 + PROJECT_SEARCH_BY_NAME_PATH
CCI_PROJECTS_URI = GITLAB_API_URI_V4 + PROJECTS_PATH
CCI_TAGS_URI = GITLAB_API_URI_V4 + TAGS_PATH
CCI_BRANCHES_URI = GITLAB_API_URI_V4 + BRANCH_PATH
# LCI -> URI for Legacy CI
LCI_GROUPS_URI = GITLAB1_API_URI_V4 + GROUPS_PATH
LCI_SUBGROUPS_URI = GITLAB1_API_URI_V4 + SUBGROUPS_PATH
LCI_PROJECT_SEARCH_BY_NAME_URI = GITLAB1_API_URI_V4 + PROJECT_SEARCH_BY_NAME_PATH
LCI_PROJECTS_URI = GITLAB1_API_URI_V4 + PROJECTS_PATH
LCI_TAGS_URI = GITLAB1_API_URI_V4 + TAGS_PATH
LCI_BRANCHES_URI = GITLAB1_API_URI_V4 + BRANCH_PATH


# ------------------- HTTP CONSTANTS -------------------

# HTTP Methods
GET  = "GET"
POST = "POST"

# HTTP Status Codes
OK = 200
BAD_REQUEST = 400
UNAUTHORIZED = 401
FORBIDDEN = 403
NOT_FOUND = 404
UNPROCESSABLE_ENTITY = 422
INTERNAL_SERVER_ERROR = 500

# ------------------- FILE NAMES -------------------

# Log Files
ERROR_LOG_FILE = "err.log"
EXECUTION_LOG_FILE = "execution.log"

# Yaml Files
REQUIREMENTS_YAML_FILE = "requirements.yaml"
OLD_YAML_FILE = "old.yaml"