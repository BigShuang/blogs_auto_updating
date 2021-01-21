import json
import os
import re
import git


demostr = """
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200322153603826.png)
# github image
# ![123456](https://raw.githubusercontent.com/BigShuang/Django-personal-note-course/main/imgs/3_1_01.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/20200322153603826.png)
# github image
# ![123456](https://raw.githubusercontent.com/BigShuang/Django-personal-note-course/main/imgs/3_1_01.png)
"""


str2 = """
其中，用到的关联代码还有：
- `register.html` 见 [6-1 基于类的视图（Class-based views）介绍](https://github.com/BigShuang/Django-personal-note-course/blob/main/contents/6/1.md)
- `Student`模型见[Django自学笔记 4-1 模型（Models）介绍](https://github.com/BigShuang/Django-personal-note-course/blob/main/contents/4/1.md)中的示例。
- *其他代码见本专栏之前博客（实际上本文用不到）*
"""
# 匹配并替换

csdn_img_pattern = "img\-blog\.csdnimg\.cn/\d*"
git_img_patthern = "raw\.githubusercontent\.com/BigShuang/Django\-personal\-note\-course/main/imgs/\w*"
img_pattern = '!\[(.*?)\]\(https\://(?:%s|%s)\.png\)' % (csdn_img_pattern, git_img_patthern)

git_md_pattern = '\[(.*?)\]\(https\://github\.com/BigShuang/Django-personal-note-course/blob/main/contents/(.*?)\.md\)'


# obj = re.search(git_md_pattern, str2)
# print(obj.group())
# print(obj.group(0))
# print(obj.group(1))
# print(obj.group(2))
i = 0

def repl(matchObj):
    global i
    print(i)
    i += 1
    return str(i) + matchObj.group(1) + matchObj.group(2)

newKey = re.sub(git_md_pattern, repl, str2)

print(newKey)


# with open("temp.json", "r", encoding="utf-8") as f:
#     data = json.load(f)
#
# print(data)
#
# with open("temp.json", "w", encoding="utf-8") as f:
#     json.dump(data, f, ensure_ascii=False)

# project = "F:\\UP PIG\\blog\\Django-personal-note-course"
# r = git.Repo(project)
#
# last_one = "c6656735a4b1bc1a0d79609de43e4280acda8be4"
# cur = r.head.commit.hexsha
# for c in r.iter_commits():
#     if c.hexsha == last_one:
#         diffs = c.diff(cur)
#         break
#
# from util import splitall
# print(r.head.commit.hexsha)
# for d in diffs:
#     if d.change_type in "ARM":
#         p = d.b_path
#         p1 = splitall(p)
#         print(p1)
        # break