import json
import os
from hander_cnblogs import CnblogsHander

config_path = "config.json"
git_info_path = "git_info/"
user_path = r"C:\Users\Administrator\Desktop\secret\user.json"
default_user_path = "user.json"


BOOKNAME = "Django笔记&教程"


def read_configs():
    if not os.path.exists(user_path):
        with open(default_user_path, "r", encoding="utf-8") as f:
            user = json.load(f)
        for k in user:
            print(k, user[k])

        exit()

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    with open(user_path, "r", encoding="utf-8") as f:
        user = json.load(f)

    user = {k: user[k] for k in config}

    git_info = {}
    for k in config:
        config[k]["bookname"] = BOOKNAME

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

    return config, user, git_info


def hander():
    # 1 read config
    config, user, git_info = read_configs()
    # 2 for blog in configs do something
    for blog_root in config:
        if blog_root == "cnblogs":

            hander = CnblogsHander(config[blog_root], user[blog_root], git_info[blog_root])
            # print(hander.git_info)
            # hander.run()
            hander.run(catalog=True)
            # hander.run(chapter="0", section="2")

    # 3

if __name__ == '__main__':
    hander()