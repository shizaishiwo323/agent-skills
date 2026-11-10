# 内容运营自动化

小红书图文从素材到发布的流水线。三个 skill 配合使用，并绑定 `xhs-auto-workflow` 项目的本地路径和环境，换机器使用前需要改路径。

[返回总览](../README.md)

## xhs-auto-workflow-material-pipeline

**来源类型：** 混合仓库子目录

**用途：** 编排小红书图文全流程：盘点素材、必要时爬取、移交素材生成、校验素材包、定时发布、邮件汇报。

**何时使用：** 运行小红书自动化全流程或定时发布。

**输入：** 主题、已有素材、本地项目环境。

**输出：** 校验通过的素材包、定时发布结果、汇报邮件。

**链接：** [xhs-auto-workflow-material-pipeline](https://github.com/shizaishiwo323/xhs-auto-workflow/tree/main/.codex/skills/xhs-auto-workflow-material-pipeline)

## xhs-material-pipeline

**来源类型：** 混合仓库子目录

**用途：** 分析素材、爆款参考、账号数据和历史违规记录，生成可自动发布的小红书图文素材包。

**何时使用：** 生成标题、正文、封面、配图，或根据账号数据和爆款参考做新笔记。

**输入：** Excel/CSV 素材、账号数据、违规历史。

**输出：** 标题、正文、封面配图方案、`publish_manifest.json`、发布适配表和校验结果。

**链接：** [xhs-material-pipeline](https://github.com/shizaishiwo323/xhs-auto-workflow/tree/main/.codex/skills/xhs-material-pipeline)

## xhs-shared-rules

**来源类型：** 混合仓库子目录

**用途：** 上面两个 skill 共用的硬规则：字数和话题限制、humanizer 与 imagegen 留痕、manifest、同主题去重、删除限制。

**何时使用：** 由另外两个 skill 引用，也用于其他小红书相关维护任务。

**输入：** 无独立输入。

**输出：** 作为约束生效，不单独产出内容。

**链接：** [xhs-shared-rules](https://github.com/shizaishiwo323/xhs-auto-workflow/tree/main/.codex/skills/xhs-shared-rules)
