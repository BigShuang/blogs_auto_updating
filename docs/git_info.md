## git_info
位于info文件夹下

文件夹中有json文件存储git提交信息，包含目录，链接对应关系等等
json文件为项目运行时自动生成


示例：
```json
{
  "git_sha": "af4b6436236c86b019640d6155446d160fb0dc7a",
  "file_map": {
    "0-1": "14274828",
    "0-2": "14285538",
    "1-1": "14285573",
    "1-2": "14285578",
    "2-1": "14285579",
    "2-2": "14285580",
    "2-3": "14285581"
  },
  "imgs_map": {
    "1_1_1": "F:\\UP PIG\\blog\\Django-personal-note-course\\imgs\\1_1_1.png",
    "1_1_2": "F:\\UP PIG\\blog\\Django-personal-note-course\\imgs\\1_1_2.png",
    "1_1_3": "F:\\UP PIG\\blog\\Django-personal-note-course\\imgs\\1_1_3.png",
    "1_1_4": "F:\\UP PIG\\blog\\Django-personal-note-course\\imgs\\1_1_4.png"
    },
  "chapters": {
    "0": "简介",
    "1": "入门",
    "2": "URL与View"
  },
  "catalog": "14266169",
  "title_map": {
    "0": {
      "1": "前言",
      "2": " 框架版本与相关工具"
    },
    "1": {
      "1": "一 新建项目",
      "2": "二 常用配置"
    },
    "2": {
      "1": "URL与View关系",
      "2": "URL详细匹配规则",
      "3": "视图（view）函数"
    }
  },
  "path": "F:\\UP PIG\\blog\\Django-personal-note-course\\info\\git_info\\cnblogs.json"
}
```

说明

```json
{
  "git_sha": "git sha码",
  "file_map": "字典，文章id: 博客链接id",
  "imgs_map": "字典，图片id: 图片路径",
  "chapters": "字典，章id: 章名称",
  "catalog": "目录博客链接id",
  "title_map": "字典，章id：{节id: 节名称}",
  "path": "本文件路径"
}
```