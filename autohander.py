import json
import os
from hander_cnblogs import CnblogsHander
import sys


config_path = "config.json"
git_info_path = "git_info/"
user_path = r"C:\Users\Administrator\Desktop\secret\user.json"
default_user_path = "user.json"


def read_configs(all_setting):
    global user_path, git_info_path, config_path
    user_path = all_setting.get("user", user_path)
    git_info_path = all_setting.get("git_info", git_info_path)
    config_path = all_setting.get("config", config_path)

    if not os.path.exists(user_path):
        with open(default_user_path, "r", encoding="utf-8") as f:
            user = json.load(f)
        for k in user:
            print(k, user[k])

        exit()

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    common = config["common"]
    del config["common"]

    for k in config:
        config[k].update(common)

    with open(user_path, "r", encoding="utf-8") as f:
        user = json.load(f)

    user = {k: user[k] for k in config}

    git_info = {}
    for k in config:

        kp = os.path.join(git_info_path, "%s.json"%k)
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
                "catalog": "14266169"
            }

        git_info[k]["path"] = kp

    return config, user, git_info


def hander(all_setting={}):
    # 1 read config
    config, user, git_info = read_configs(all_setting)
    # 2 for blog in configs do something
    for blog_root in config:
        if blog_root == "cnblogs":

            hander = CnblogsHander(config[blog_root], user[blog_root], git_info[blog_root])
            # print(hander.git_info)
            if all_setting.get("refresh_catalog", False):
                hander.run(catalog=True)
            else:
                hander.run()
            # hander.run(chapter="0", section="2")


def hander_from_json(all_json):
    with open(all_json, "r", encoding="utf-8") as f:
        all_setting = json.load(f)

    hander(all_setting)

    print(all_setting)

if __name__ == '__main__':
    argvs = sys.argv
    print("starting with argvs:", argvs)
    if len(argvs) < 2:
        print("need a json for all setting")
    else:
        hander_from_json(argvs[1])

    print("Finishing")
    # hander()