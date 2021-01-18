import xmlrpc.client as xmlrpclib
import mimetypes

import os
import time
import json
import re
import git
from util import splitall, get_commit_by_sha


CHAPTERINDEX = ['', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十']


class Hander():
    def __init__(self, config, user, git_info):
        self.config = config
        self.user = user
        self.git_info = git_info

        self.refresh_catalog = False
        self.refresh_all = True  # refresh all contents

        self.server = None
        self.mwb = None
        self.info = {
            "blog": {},
            "catalog": {}
        }

        self.title_map = {}
        self.diffs = {}

        self.last_update = ["-1", "-1"]
        self.current = ["0", "0"]

    def get_general_info(self):
        for kind in ["start", "end"]:
            for key in self.info:
                kind_path = os.path.join(self.config["project"], "info", "cnblogs", key, "%s.md" % kind)
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

        current_sha = repo.head.commit.sha
        if self.git_info.get("git_sha", ""):
            sha = self.git_info["git_sha"]
            last_commit = get_commit_by_sha(repo, sha)
            if last_commit:
                diffs = last_commit.diff(current_sha)
                for d in diffs:
                    if d.change_type in "ARM":
                        updated_files.append(d.b_path)

                self.git_info["git_sha"] = current_sha
                self.diffs["git"] = True

                updated_content = []
                updated_imgs = []
                for file in updated_files:
                    file_parts = splitall(file)
                    if file_parts[0] == self.config["contents"]:
                        updated_content.append(file_parts[1: -1])  # element e.g. ['0', '2']
                    elif file_parts[0] == self.config.get("imgs", "imgs"):
                        updated_imgs.append(file_parts[1])  # element e.g. ['7_1_1']

    def get_api_url(self):
        return self.config["api_url"] % self.user["bloger"]

    def link_server(self):
        self.server = xmlrpclib.ServerProxy(self.get_api_url())
        self.mwb = self.server.metaWeblog
        userInfo = self.server.blogger.getUsersBlogs(
                self.user["bloger"], self.user["username"], self.user["password"])

        self.user["blogid"] = userInfo[0]["blogid"]


class CnblogsHander(Hander):
    def hander_contents(self):
        contents_path = os.path.join(self.config["project"], self.config["contents"])

        contents = os.listdir(contents_path)
        # Chapter one section one
        for ci, chapter in enumerate(contents):
            chapter_path = os.path.join(contents_path, chapter)
            chapter_list = os.listdir(chapter_path)

            for si, section in enumerate(chapter_list):
                section_id, section_suffix = os.path.splitext(section)

                self.current = [chapter, section_id]

                if chapter < self.last_update[0] or \
                        (chapter == self.last_update[0]
                         and section_id <= self.last_update[1]):
                    continue

                if section_suffix == ".md":
                    section_path = os.path.join(chapter_path, section)
                    self.run_for_one(section_path, chapter, section_id)

                    self.last_update = [chapter, section_id]

        self.last_update = ["-1", "-1"]

    def regen_catalog(self):
        print("=== regenrate catalog list for every chapter and sections:")
        contents_path = os.path.join(self.config["project"], self.config["contents"])

        contents = os.listdir(contents_path)
        # Chapter one section one
        for ci, chapter in enumerate(contents):
            chapter_path = os.path.join(contents_path, chapter)
            chapter_list = os.listdir(chapter_path)

            for si, section in enumerate(chapter_list):
                section_id, section_suffix = os.path.splitext(section)

                self.current = [chapter, section_id]

                if section_suffix == ".md":
                    section_path = os.path.join(chapter_path, section)

                    # process one
                    self.get_blog_md(section_path, chapter, section_id)

                    self.last_update = [chapter, section_id]

        self.refresh_catalog = True
        self.last_update = ["-1", "-1"]

    def genrate_catalog_md(self):
        print("=== genrate catalog markdown")
        blog_body = self.info["catalog"].get("start", '')

        blog_body = blog_body.strip() + "\n" + "### 总目录\n"

        for i in range(len(self.title_map) + 10):
            si = str(i)
            if si in self.title_map:
                title = self.git_info["chapters"][si]
                if CHAPTERINDEX[i]:
                    title = "第%s章" % CHAPTERINDEX[i] + title

                blog_body += "### %s\n" % title
                sections = self.title_map[si]
                for j in range(len(sections) + 5):
                    sj = str(j)
                    if sj in sections:
                        stitle = sections[sj]
                        url = "https://www.cnblogs.com/BigShuang/p/%s.html" % self.git_info["file_map"]["%s-%s" % (si, sj)]
                        blog_body += "#### [%s %s](%s)\n" % (sj, stitle, url)

        blog_body += self.info["catalog"].get("end", '')

        return blog_body

    def save_git_info(self):
        print("=== save git info")
        if self.last_update[0] >= "0":
            self.git_info["last_update"] = self.last_update
        else:
            if "last_update" in self.git_info:
                del self.git_info["last_update"]

        self.git_info["title_map"] = self.title_map

        with open("git_info/cnblogs.json", "w", encoding="utf-8") as fw:
            json.dump(self.git_info, fw, ensure_ascii=False)

    def get_blog_md(self, section_path, chapter, section_id):
        # process one
        with open(section_path, "r", encoding="utf-8") as f:
            blog_body = f.read()

        blog_body = blog_body.strip()
        title = ""

        if blog_body.startswith("## "):
            split_res = blog_body.split("\n", 1)
            if len(split_res) < 2:
                title = split_res[0]
                blog_body = ""
            else:
                title, blog_body = split_res
                title = title[3:]

                title.strip()
                blog_body = blog_body.strip()
        else:
            print("no title")
            return "", blog_body

        refresh_catalog = True
        if chapter not in self.title_map:
            self.title_map[chapter] = {section_id: title}
        elif section_id not in self.title_map[chapter]:
            self.title_map[chapter][section_id] = title
        elif section_id != self.title_map[chapter][section_id]:
            self.title_map[chapter][section_id] = title
        else:
            refresh_catalog = False

        if refresh_catalog:
            self.refresh_catalog = True

        return title, blog_body

    def process_one(self, section_path, chapter, section_id):
        title, blog_body = self.get_blog_md(section_path, chapter, section_id)

        if "start" in self.info["blog"]:
            start = self.info["blog"]["start"] % (chapter, section_id, title)
            start = start.strip()
            blog_body = start + "\n\n" + blog_body

        self.reset_href(blog_body)

        title = "%s %s-%s %s" % (self.config["bookname"], chapter, section_id, title)

        postData = {
            "description": blog_body,
            "title": title,
            "categories": ['[Markdown]']
        }

        return postData

    def repl_img(self, match_obj):
        img_id = "%s_%s_%s" % (self.current[0], self.current[1], self.img_index)
        if img_id in self.git_info["imgs_map"]:
            img_url = self.git_info["imgs_map"][img_id]
        else:
            img_url = os.path.join(self.config["project"], "imgs", "%s.png" % img_id)
            self.git_info["imgs_map"][img_id] = img_url

        self.img_index += 1
        repl_str = "![%s](%s)" % (match_obj.group(1), img_url)

        return repl_str

    def repl_md_url(self, match_obj):
        title = match_obj.group(1)
        md_id = match_obj.group(2)
        chapter, section = md_id.split("/")

        file_id = "%s-%s" % (chapter, section)
        if file_id in self.git_info["file_map"]:
            file_url = self.git_info["file_map"][file_id]
            return "![%s](%s)" % (title, file_url)

        return title

    def reset_href(self, blog_body):
        # TODO edit image
        # TODO 章节跳转

        # csdn image
        # ![在这里插入图片描述](https://img-blog.csdnimg.cn/20200322153603826.png)
        # github image
        # ![](https://raw.githubusercontent.com/BigShuang/Django-personal-note-course/main/imgs/3_1_01.png)

        csdn_img_pattern = "img\-blog\.csdnimg\.cn/\d*"
        git_img_patthern = "raw\.githubusercontent\.com/BigShuang/%s/main/imgs/\w*" % self.config["project-name"]
        pattern = '!\[(.*?)\]\(https\://(?:%s|%s)\.png\)' % (csdn_img_pattern, git_img_patthern)

        self.img_index = 1

        blog_body = re.sub(pattern, self.repl_img, blog_body)

        git_md_pattern = '\[(.*?)\]\(https\://github\.com/BigShuang/%s/blob/main/contents/(.*?)\.md\)'\
                         % self.config["project-name"]

        # handle url chapter
        blog_body = re.sub(git_md_pattern, self.repl_md_url, blog_body)

        return blog_body

    def post_image(self, img_path):
        with open(img_path, "rb") as f:
            bits = xmlrpclib.Binary(f.read())

        name = os.path.basename(img_path)
        img_type = mimetypes.guess_type(img_path)[0]

        file_data = {
            "bits": bits,
            "name": name,
            "type": img_type
        }

        while True:
            try:
                return self.mwb.newMediaObject(self.user["blogid"], self.user["username"],
                                               self.user["password"], file_data)
            except:
                time.sleep(5)

    def post_blog(self, postData):
        while True:
            try:
                return self.mwb.newPost(self.user["blogid"], self.user["username"], self.user["password"], postData, True)
            except:
                print("post new blog failed, try post again.")
                time.sleep(5)

    def edit_blog(self, postid, postData):
        self.mwb.editPost(postid, self.user["username"], self.user["password"], postData, True)

    def run_for_one(self, section_path, chapter, section_id):
        postData = self.process_one(section_path, chapter, section_id)
        file_key = "%s-%s" % (chapter, section_id)
        if file_key not in self.git_info["file_map"]:
            post_id = self.post_blog(postData)
            self.git_info["file_map"][file_key] = post_id
        else:
            post_id = self.git_info["file_map"][file_key]
            self.edit_blog(post_id, postData)

    def run(self, *args, **kwargs):
        self.link_server()
        self.get_general_info()
        try:
            if "catalog" in kwargs and kwargs["catalog"]:
                self.regen_catalog()

            elif "chapter" in kwargs and "section" in kwargs:
                section_path = os.path.join(self.config["project"], self.config["contents"],
                                            kwargs["chapter"], "%s.md" % kwargs["section"])

                self.run_for_one(section_path, kwargs["chapter"], kwargs["section"])
            else:
                self.hander_contents()

            if self.refresh_catalog:
                postData = {
                    "description": self.genrate_catalog_md(),
                    "title": "%s 总目录" % self.config["bookname"],
                    "categories": ['[Markdown]']
                }
                if not self.git_info.get("catalog", ""):
                    post_id = self.post_blog(postData)
                    self.git_info["catalog"] = post_id
                else:
                    post_id = self.git_info["catalog"]
                    self.edit_blog(post_id, postData)

        except Exception as e:
            self.git_info["error"] = str(e)
        self.save_git_info()


