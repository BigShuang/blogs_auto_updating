import os
import git
from util import splitall, get_commit_by_sha, start_with

import xmlrpc.client as xmlrpclib
import mimetypes


class Hander():
    def __init__(self, config, user, git_info):
        self.config = config
        self.user = user
        self.git_info = git_info

        self.refresh_catalog = False

        self.server = None
        self.mwb = None
        self.info = {
            "blog": {},
            "catalog": {}
        }

        self.title_map = {}
        self.diffs = {
            "git": False,  # True: refresh git contents, False: refresh all contents
            "content": [],
            "imgs": []
        }

        self.last_update = -1
        self.current = None

        self.current_sha = ""

    def get_general_info(self):
        for kind in ["start", "end"]:
            for key in self.info:
                kind_path = os.path.join(self.config["project"], self.config.get("info", "info"),
                                         "cnblogs", key, "%s.md" % kind)
                if os.path.exists(kind_path):
                    with open(kind_path, "r", encoding="utf-8") as f:
                        self.info[key][kind] = f.read()

        if "last_update" in self.git_info:
            self.last_update = self.git_info["last_update"]

        if "title_map" in self.git_info:
            self.title_map = self.git_info["title_map"]

        # git compare
        updated_files = []
        repo = git.Repo(self.config["project"])

        current_sha = repo.head.commit.hexsha
        if self.git_info.get("git_sha", ""):
            sha = self.git_info["git_sha"]
            last_commit = get_commit_by_sha(repo, sha)
            if last_commit:
                diffs = last_commit.diff(current_sha)
                for d in diffs:
                    if d.change_type in "ARM":
                        updated_files.append(d.b_path)

                self.diffs["git"] = True

                for file in updated_files:
                    file_parts = splitall(file)
                    if file_parts[0] == self.config["contents"] and file_parts[-1] == ".md":
                        file_id = tuple(file_parts[1: -1])  # e.g. ('0', '2')
                        if file_id not in self.diffs["content"]:
                            self.diffs["content"].append(file_id)

                    elif start_with(file_parts, splitall(self.config.get("imgs", "imgs"))):
                        img_id = file_parts[-2]  # e.g. '7_1_1'
                        file_id = tuple(img_id.split("_")[:-1])
                        if file_id not in self.diffs["content"]:
                            self.diffs["content"].append(file_id)

                        if img_id not in self.diffs["imgs"]:
                            self.diffs["imgs"].append(img_id)

        self.current_sha = current_sha

    def get_api_url(self):
        return self.config["api_url"] % self.user["bloger"]

    def link_server(self):
        self.server = xmlrpclib.ServerProxy(self.get_api_url())
        self.mwb = self.server.metaWeblog
        userInfo = self.server.blogger.getUsersBlogs(
                self.user["bloger"], self.user["username"], self.user["password"])

        self.user["blogid"] = userInfo[0]["blogid"]

    def get_file_data(self, file_path):
        with open(file_path, "rb") as f:
            bits = xmlrpclib.Binary(f.read())

        name = os.path.basename(file_path)
        img_type = mimetypes.guess_type(file_path)[0]

        file_data = {
            "bits": bits,
            "name": name,
            "type": img_type
        }

        return file_data