## config.json
位于 info文件夹下

- 存储项目的基础设置，比如项目各种路径和 基础信息
- 存储博客园的基础设置（TODO:  这部分未来将调整到本项目中）

示例
```json
{
  "common": {
    "project": "F:\\UP PIG\\blog\\Django-personal-note-course",
    "contents": "contents",
    "imgs": "imgs",
    "project-name": "Django-personal-note-course",
    "book-name": "Django笔记&教程"
  },
  "cnblogs":{
    "url": "https://www.cnblogs.com",
    "api_url": "http://rpc.cnblogs.com/metaweblog/%s",
    "view_url": "%s/%s/p/%.html",
    "edit": ""
  }
}
```

说明
```json
{
  "common": {
    "project": "项目文件夹绝对路径",
    "contents": "正文文件夹名",
    "imgs": "图片文件夹名",
    "project-name": "项目文件夹名",
    "book-name": "项目名"
  },
  "cnblogs":{
    "url": "https://www.cnblogs.com",
    "api_url": "http://rpc.cnblogs.com/metaweblog/%s",
    "view_url": "%s/%s/p/%.html",
    "edit": ""
  }
}
```