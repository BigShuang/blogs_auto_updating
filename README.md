# blogs_auto_updating

博客园 文章自动发布

项目描述
- 一键发布专栏多篇文章，
- 一键生成目录
- 一键更新

[项目设计说明](./docs/design.md)


示例：
[Django笔记&教程](https://www.cnblogs.com/BigShuang/p/14266169.html)


### 目录结构：
#### info
存储各种设置的文件夹
该文件夹下有
- config.json: 项目的基础设置，
[具体说明](./docs/config.md)
  
- cnblog: 文件夹中指定博客开头和结尾：
```txt
|--cnblog
   |--blog
      |--start.md
      |--end.md
   |--catalog
      |--start.md
      |--end.md
```
- git_info: 文件夹中有json文件存储git提交信息，包含目录，链接对应关系等等

[具体说明](./docs/git_info.md)

- all.json: 更新的基础设置
`refresh_catalog`: 是否刷新所有
  
`cid`指定要刷新的章节名，不指定则自动检查刷新

`cid`格式：
示例： `["1"]`, `["1", "2"]`