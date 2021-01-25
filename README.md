# blogs_auto_updating

博客园 文章自动发布

项目描述
- 一键发布专栏多篇文章，
- 一键生成目录
- 一键更新


示例：
[Django笔记&教程](https://www.cnblogs.com/BigShuang/p/14266169.html)




### 目录结构：
contents： 放正文md文档
info  文件夹路径在config.json中设置
指定各个博客开头和结尾：
```txt
|--cnblog
   |--blog
      |--start.md
      |--end.md
   |--catalog
      |--start.md
      |--end.md
```

git_info  文件夹路径在config.json中设置
内置json存储git提交信息，包含目录，链接对应关系等等

|--cnblogs.json

### all.json
`cid`指定要刷新的章节名，不指定则自动检查刷新
`cid`格式：
示例： `["1"]`, `["1", "2"]`