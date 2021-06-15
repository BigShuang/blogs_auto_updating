import json
import os
from hander_cnblogs import CnblogsHander
import sys


common_json = "default/common.json"

default_user_path = "default/user.json"  # user.json 样式参考
user_json = r"C:\Users\admin\Desktop\secret\user.json"


def read_configs(all_setting):
    """
    读取设置
    :param all_setting:
    :return:
    """
    project_path = all_setting["project"]
    user_path = all_setting.get("user", user_json)
    git_info_path = all_setting["git_info"]
    config_path = all_setting["config"]

    abs_config_path = os.path.join(project_path, config_path)
    abs_git_info_path = os.path.join(project_path, git_info_path)

    if not os.path.exists(user_path):
        with open(default_user_path, "r", encoding="utf-8") as f:
            user = json.load(f)

        print("请设置user.json的路径")
        print("样式请参考")
        print("{")
        for k in user:
            print("    '{}': '{}',".format(k, user[k]))
        print("}")

        exit(1)

    with open(abs_config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    with open(common_json, "r", encoding="utf-8") as f:
        common = json.load(f)

    for k in common:
        common[k]["project"] = project_path
        common[k].update(config)

    with open(user_path, "r", encoding="utf-8") as f:
        user = json.load(f)

    user = {k: user[k] for k in common}

    git_info = {}
    for k in common:
        kp = os.path.join(abs_git_info_path, "%s.json"%k)
        if os.path.exists(kp):
            with open(kp, "r", encoding="utf-8") as f:
                git_info[k] = json.load(f)
        else:
            git_info[k] = {
                "git_sha": "",
                "file_map": {
                },
                "imgs_map": {
                },
                "chapters": {
                },
                "catalog": ""
            }

        git_info[k]["path"] = kp

    return common, user, git_info


def hander(all_json_fp):
    # 0 read all.json:
    # get git_info path, config path, whether refresh_catalog
    # whether refresh specific md by cid
    with open(all_json_fp, "r", encoding="utf-8") as f:
        all_setting = json.load(f)

    # 1 read config
    common_config, user, git_info = read_configs(all_setting)
    # 2 for blog in configs do something
    for blog_root in common_config:
        if blog_root == "cnblogs":
            hander = CnblogsHander(common_config[blog_root],
                                   user[blog_root], git_info[blog_root])
            if all_setting.get("refresh_catalog", False):
                hander.run(catalog=True)
            elif all_setting.get("cid"):
                hander.run(cid=all_setting.get("cid"))
            else:
                hander.run()


if __name__ == '__main__':
    # json_file = "H://github projects//2021//Django-personal-note-course//info//all.json"
    json_file = "H://github projects//big-shuang-python-introductory-course//info//all.json"
    hander(json_file)
