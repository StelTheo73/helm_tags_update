# Python Libraries
import os
import os.path

# Program Libraries
from src.exceptions import (
    FetchInfoFailedException
)
from src.YamlUpdater import KubernetesRequirementsYamlUpdater

def setup():
    pwd = os.getcwd()
    err_log_file = os.path.join(pwd, "err.log")
    exec_log_file = os.path.join(pwd, "execution.log")
    old_yaml_file = os.path.join(pwd, "old.yaml")
    req_yaml_file = os.path.join(pwd, "requirements.yaml")

    if os.path.exists(err_log_file):
        os.remove(err_log_file)
    if os.path.exists(exec_log_file):
        os.remove(exec_log_file)
    if os.path.exists(old_yaml_file):
        os.remove(old_yaml_file)
    if os.path.exists(req_yaml_file):
        os.remove(req_yaml_file)

def main():
    setup()
    
    try:
        yamlUpdater = KubernetesRequirementsYamlUpdater()
        yamlUpdater.get_branch()
        yamlUpdater.fetch_requirements_file()
        helm_projects_with_changed_tag = yamlUpdater.get_changed_tags()
        updated_yaml_object = yamlUpdater.update_helm_tags(helm_projects_with_changed_tag)
        yamlUpdater.write_yaml_to_file(updated_yaml_object)
    except KeyboardInterrupt:
        print("\nExecution terminated by user.")
    except FetchInfoFailedException as exc:
        print(exc)


if __name__ == "__main__":
    main()


# mgr = GitlabAPIManager()
# id = mgr.get_subgroup_id_from_name("ntas", "helm")
# projects_list = mgr.get_projects_of_group(id)
# projects_list = mgr.extract_project_name_and_id(projects_list)

# projetcs_with_tags = mgr.find_tags_of_projects(projects_list)
# print(json.dumps(projetcs_with_tags[0:10], indent = 2))

#------------------------------------------------------------------------
# mgr1 = Gitlab1APIManager()
# print(mgr1.get_project_id_from_project_name("kubernetes", "tas"))
#------------------------------------------------------------------------
# projects_list = sort_list_dict_by_name(projects_list)
# for el in projects_list:
#     print(el["name"], el["id"], sep = ", ")

#projects_dict = GitlabAPIManager.transform_list_of_dicts_to_single_kv_pair_dict(projects_list, "name", "id")
#id = projects_dict["helm-base"]
#tags_list = mgr.get_project_tags_from_project_id(id) 
#tags_list = mgr.extract_tag_name_and_title(tags_list)

#response_list = sorted(response_list, key = lambda d: (d["commit"]["committed_date"], d["name"]), reverse = True)
#print(json.dumps(tags_list[0:10], indent = 2))
#tags_list = GitlabAPIManager.transform_list_of_dicts_to_single_kv_pair_dict(tags_list, "name", "title")
#for el in tags_list.keys():
#    print(el, tags_list[el])

#mgr.find_tag_by_title(tags_list, "fc")