import mimetypes

import os
import time
import json
import re

from hander_base import Hander
from util import get_idstr

CHAPTERINDEX = ['', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十']


def refresh_title_by_cid(title_map, cid, title):
    refresh_catalog = True
    if isinstance(cid, list) or isinstance(cid, tuple):
        if len(cid) == 2:
            if cid[0] not in title_map:
                title_map[cid[0]] = {cid[1]: title}
            elif cid[1] not in title_map[cid[0]] or title != title_map[cid[0]][cid[1]]:
                title_map[cid[0]][cid[1]] = title
            else:
                refresh_catalog = False

            return refresh_catalog
        elif len(cid) == 1:
            cid = str(cid[0])

    if cid not in title_map or title_map[cid] != title:
        title_map[cid] = title
    else:
        refresh_catalog = False

    return refresh_catalog


class CnblogsHander(Hander):
    def hander_contents(self):
        id_list, path_list = self.get_iter_contents()
        # Chapter one section one
        for i, cid in enumerate(id_list):
            i_path = path_list[i]

            if i <= self.last_update:
                continue

            if self.diffs["git"] and cid not in self.diffs["content"]:
                continue

            self.run_for_one(cid, i_path)

            self.last_update = i

        self.last_update = -1

    def get_iter_contents(self):
        contents_path = os.path.join(self.config["project"], self.config["contents"])

        content_list = os.listdir(contents_path)

        # res: content id list, path list
        id_list = []
        path_list = []

        layer_kind = self.config["layer"]
        if layer_kind.startswith("two"):
            for ci, chapter in enumerate(content_list):
                chapter_path = os.path.join(contents_path, chapter)
                chapter_list = os.listdir(chapter_path)

                for si, section in enumerate(chapter_list):
                    section_id, section_suffix = os.path.splitext(section)

                    if section_suffix == ".md":
                        section_path = os.path.join(chapter_path, section)
                        ids = (chapter, section_id)
                        id_list.append(ids)
                        path_list.append(section_path)

        elif layer_kind.startswith("one"):
            for ci, chapter in enumerate(content_list):
                chapter_id, chapter_suffix = os.path.splitext(chapter)

                if chapter_suffix == ".md":
                    chapter_path = os.path.join(contents_path, chapter)
                    id_list.append((chapter_id, ))
                    path_list.append(chapter_path)

        return id_list, path_list

    def regen_catalog(self):
        id_list, path_list = self.get_iter_contents()
        # Chapter one section one
        for i, cid in enumerate(id_list):
            i_path = path_list[i]
            self.get_blog_md(cid, i_path)

            self.last_update = i

        self.refresh_catalog = True
        self.last_update = -1

    def genrate_catalog_md(self):
        print("=== genrate catalog markdown")
        blog_body = self.info["catalog"].get("start", '')

        blog_body = blog_body.strip() + "\n" + "### 总目录\n"

        layer_kind = self.config["layer"]

        if layer_kind == "two-linked":
            for i in range(len(self.title_map) + 10):
                si = str(i)
                if si in self.title_map:
                    title = self.git_info["chapters"][si]
                    if CHAPTERINDEX[i]:
                        title = "第%s章 " % CHAPTERINDEX[i] + title

                    blog_body += "### %s\n" % title
                    sections = self.title_map[si]
                    for j in range(len(sections) + 5):
                        sj = str(j)
                        if sj in sections:
                            stitle = sections[sj]

                            idstr = get_idstr((si, sj))
                            if idstr in self.git_info["file_map"]:
                                url = "https://www.cnblogs.com/BigShuang/p/%s.html" % self.git_info["file_map"][idstr]
                                blog_body += "#### [%s %s](%s)\n" % (sj, stitle, url)
                            else:
                                blog_body += "#### %s %s\n" % (sj, stitle)

        elif layer_kind == "one-linked":
            for i in range(len(self.title_map) + 10):
                si = str(i)
                if si in self.title_map:

                    title = self.title_map[si]
                    if CHAPTERINDEX[i]:
                        title = "第%s节 " % CHAPTERINDEX[i] + title

                    idstr = get_idstr(si)
                    if idstr in self.git_info["file_map"]:
                        url = "https://www.cnblogs.com/BigShuang/p/%s.html" % self.git_info["file_map"][idstr]
                        title = "[%s](%s)" % (title, url)

                    blog_body += "#### %s\n" % (title)

        blog_body += self.info["catalog"].get("end", '')

        return blog_body

    def save_git_info(self):
        print("=== save git info")
        if self.last_update >= 0:
            self.git_info["last_update"] = self.last_update
        else:
            if "last_update" in self.git_info:
                del self.git_info["last_update"]

        self.git_info["title_map"] = self.title_map

        with open(self.git_info["path"], "w", encoding="utf-8") as fw:
            json.dump(self.git_info, fw, ensure_ascii=False)

    def get_blog_md(self, cid, cpath):
        # process one
        with open(cpath, "r", encoding="utf-8") as f:
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

        # refresh title for every article of contents in title_map
        if refresh_title_by_cid(self.title_map, cid, title):
            self.refresh_catalog = True

        return title, blog_body

    def process_one(self, cpath, cid):
        title, blog_body = self.get_blog_md(cid, cpath)

        if "start" in self.info["blog"]:
            start = self.info["blog"]["start"]
            if "%s" in start:
                start = start % (*cid, title)
            start = start.strip()
            blog_body = start + "\n\n" + blog_body

        blog_body = self.reset_href(blog_body)

        title = "%s %s %s" % (self.config["book-name"], get_idstr(cid), title)

        postData = {
            "description": blog_body,
            "title": title,
            "categories": ['[Markdown]']
        }

        return postData

    def repl_img_by_index(self, match_obj):
        img_id = "%s_%s" % (self.current, self.img_index)
        if img_id in self.git_info["imgs_map"]:
            img_url = self.git_info["imgs_map"][img_id]
        else:
            img_path = os.path.join(self.config["project"], self.config.get("imgs", "imgs"), "%s.png" % img_id)
            if os.path.exists(img_path):
                img_url_dic = self.post_image(img_path)
                img_url = img_url_dic["url"]
                self.git_info["imgs_map"][img_id] = img_url
            else:
                print("Lack of image files locally:", img_id)

                self.img_index += 1
                return match_obj.group(0)

        self.img_index += 1
        repl_str = "![%s](%s)" % (match_obj.group(1), img_url)
        return repl_str

    def repl_img_by_path(self, match_obj):
        img_id = match_obj.group(2).replace("/", "_")
        if img_id in self.git_info["imgs_map"]:
            img_url = self.git_info["imgs_map"][img_id]
        else:
            img_file = "%s.%s" % (match_obj.group(2), match_obj.group(3))
            img_path = os.path.join(self.config["project"], self.config.get("imgs", "imgs"),
                                    img_file)
            if os.path.exists(img_path):
                img_url_dic = self.post_image(img_path)
                img_url = img_url_dic["url"]
                self.git_info["imgs_map"][img_id] = img_url
            else:
                print("Lack of image files locally:", img_file)
                return match_obj.group(0)

        repl_str = "![](%s)" % img_url
        return repl_str

    def repl_md_url(self, match_obj):
        title = match_obj.group(1)
        md_id = match_obj.group(3)
        if self.config["layer"].startswith("two"):
            chapter, section = md_id.split("/")
            file_id = "%s-%s" % (chapter, section)
        elif self.config["layer"].startswith("one"):
            file_id = md_id
        else:
            return title

        if file_id in self.git_info["file_map"]:
            file_url = self.git_info["file_map"][file_id]
            return "![%s](%s)" % (title, file_url)

        return title

    def reset_href(self, blog_body):
        # 1 - 替换图片链接
        # csdn image
        # ![在这里插入图片描述](https://img-blog.csdnimg.cn/20200322153603826.png)
        # github image
        # ![](https://raw.githubusercontent.com/BigShuang/Django-personal-note-course/main/imgs/3_1_01.png)
        csdn_img_pattern = "img\-blog\.csdnimg\.cn/\d*"
        img_path = self.config.get("imgs", "imgs").replace("\\", "/")
        git_img_pattern = "raw\.githubusercontent\.com/BigShuang/%s/(main|master)/%s/\w*" % \
                          (self.config["project-name"], img_path)
        pattern = '!\[(.*?)\]\(https\://(?:%s|%s)\.png\)' % (csdn_img_pattern, git_img_pattern)
        self.img_index = 1
        blog_body = re.sub(pattern, self.repl_img_by_index, blog_body)

        # 2 - 替换项目文档中的图片地址为图片链接
        local_img_pattern = "!\[\]\((\.\.\/){1,3}%s\/(.*?)\.(png|jpg|bmp)\)" % img_path
        blog_body = re.sub(local_img_pattern, self.repl_img_by_path, blog_body)

        # 3 - 替换项目文档中其他项目文章链接
        git_md_pattern = '\[(.*?)\]\(https\://github\.com/BigShuang/%s/blob/(main|master)/%s/(.*?)\.md\)'\
                         % (self.config["project-name"], self.config["contents"])
        # handle url chapter
        blog_body = re.sub(git_md_pattern, self.repl_md_url, blog_body)

        return blog_body

    def post_image(self, img_path):
        file_data = self.get_file_data(img_path)

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

    def run_for_one(self, cid, cpath):
        print("Start updating blog:", cpath, end=", ")
        file_key = get_idstr(cid)
        self.current = file_key

        postData = self.process_one(cpath, cid)

        if file_key not in self.git_info["file_map"]:
            post_id = self.post_blog(postData)
            self.git_info["file_map"][file_key] = post_id
        else:
            post_id = self.git_info["file_map"][file_key]
            self.edit_blog(post_id, postData)

        print("Successfully updated to:", post_id)

    def run(self, *args, **kwargs):
        self.link_server()
        self.get_general_info()
        if True:
        # try:
            if "catalog" in kwargs and kwargs["catalog"]:
                self.regen_catalog()

            elif "cid" in kwargs:
                file_path = os.path.join(*kwargs["cid"]) + ".md"
                section_path = os.path.join(self.config["project"], self.config["contents"], file_path)
                if not os.path.exists(section_path):
                    file_path = file_path.replace("-", "/")
                    section_path = os.path.join(self.config["project"], self.config["contents"], file_path)

                if not os.path.exists(section_path):
                    print("cid not valid: ")
                    print(section_path)
                    exit(1)

                self.run_for_one(kwargs["cid"], section_path)
            else:
                self.hander_contents()
                self.git_info["git_sha"] = self.current_sha

            if self.refresh_catalog:
                postData = {
                    "description": self.genrate_catalog_md(),
                    "title": "%s 总目录" % self.config["book-name"],
                    "categories": ['[Markdown]']
                }
                if not self.git_info.get("catalog", ""):
                    post_id = self.post_blog(postData)
                    self.git_info["catalog"] = post_id
                else:
                    post_id = self.git_info["catalog"]
                    self.edit_blog(post_id, postData)

        # except Exception as e:
        #     print("### Error: ", str(e))
        #     self.git_info["error"] = str(e)

        self.save_git_info()


