# Agent Skills

个人智能体 skills 总览，共收录 14 项，按用途分为 6 类。适用于 Claude Code 和 Codex。

本仓库以索引为主：每个 skill 的内容仍在各自的仓库中维护，这里只记录用途、触发场景和链接。

## 来源类型

| 类型 | 含义 |
| --- | --- |
| 独立仓库 | 整个仓库就是一个 skill |
| 混合仓库子目录 | skill 嵌在某个项目仓库的子目录中 |
| 本仓库收录 | 原来只有本地版本，内容直接放在本仓库 |
| 提示词工作流 | 手动使用的提示词，没有 `SKILL.md` |
| 第三方改版 | 基于他人的 skill 做了本地修改，链接指向上游 |

## [科研写作](01-scientific-writing/README.md)

英文论文的结构诊断、翻译、润色。两者粒度不同：`agu-writing-workflow` 管全文故事线和机制链，`sci-writing-expert` 管翻译、章节修改和句子润色。

| Skill | 用途 | 触发场景 | 类型 |
| --- | --- | --- | --- |
| [agu-writing-workflow](https://github.com/shizaishiwo323/agu-writing-workflow-skill) | 面向 AGU 系期刊（GRL、JGR、WRR、JGR: Solid Earth 等）的论文写作流程，按“故事线 > 结构 > 前后呼应 > 机制 > 段落 > 句子 > 用词”的顺序诊断和修改。 | 论文故事线不稳；Introduction 与 Results 前后呼应、铺垫与兑现；Results 小节衔接；机制驱动型地学论文；反应输运、多孔介质、水文地球物理、NMR 论文。 | 独立仓库 |
| [sci-writing-expert](https://github.com/shizaishiwo323/sci-writing-expert-skill) | 把 SCI 稿件翻译、润色、诊断、重排成自然且符合发表习惯的英文，不改变科学含义和证据强度，不虚构数据、引用或机制。 | 中译英；句段润色；逻辑和衔接修复；IMRaD 章节修改；摘要和标题；全文审查；去除 AI 味的自造复合词。 | 独立仓库 |

## [文献检索与阅读](02-literature-reading/README.md)

找到真实可引的文献，并把论文按原文顺序读透。

| Skill | 用途 | 触发场景 | 类型 |
| --- | --- | --- | --- |
| [researching-academic-literature](https://github.com/shizaishiwo323/researching-academic-literature) | 查找、逐篇核实、筛选和组织真实且高相关的学术文献，用于支撑论文写作。 | 为研究主题、论文章节、实验、模型、理论、综述、方法对比、讨论部分找文献，或加强参考文献列表。 | 独立仓库 |
| [paper-walkthrough](02-literature-reading/paper-walkthrough/) | 按原文顺序对论文做章、节、段三级拆解，每段写出“核心内容 → 作用”，完整保留公式、数值、图表编号、引文、假设和局限。 | 论文梳理、逐段精读、整理逻辑骨架、“这篇论文每段在说什么”。只要几句话的摘要时不适用。 | 本仓库收录 |

## [图件、图像与演示](03-figures-and-slides/README.md)

科研配图、位图生成，以及从论文到可编辑 PPT 的流程。

| Skill | 用途 | 触发场景 | 类型 |
| --- | --- | --- | --- |
| [nature-figure](https://github.com/Yuan1z0825/nature-skills/tree/main/skills/nature-figure) | 用 Python 或 R 创建、修改、审查和导出投稿级科研图件，包括多面板图、机制示意图和图形摘要草稿。 | 论文配图、科研绘图、多面板图、投稿图件审查。不用于交互看板、数据清洗或纯统计分析。 | 第三方改版 |
| [image-gen](https://github.com/shizaishiwo323/claude-relay-public/tree/main/extras/skills/image-gen) | 让 Claude 调用本机 Codex 的图像生成能力，生成或编辑插画、海报、封面、配图、Logo 草图和照片风格图。 | 用户要一张真实的位图时自动使用。流程图、SVG 和数据图不用它。 | 混合仓库子目录 |
| [rebuild-scientific-poster-ppt](https://github.com/shizaishiwo323/rebuild-scientific-poster-ppt) | 把科研海报、图形摘要或高密度单页参考图高保真重建为可编辑 PowerPoint。参考图决定版式，论文决定科研图、公式、单位和结论。 | 手上有 PNG、JPG 或 PDF 参考图和配套论文，需要可编辑 PPTX、子图拆分还原、渲染对比和逐子图审核。 | 独立仓库 |
| [学术PPT制作流程](https://github.com/shizaishiwo323/gpt-literature-management/tree/main/%E5%AD%A6%E6%9C%AFPPT%E5%88%B6%E4%BD%9C%E6%B5%81%E7%A8%8B) | 两阶段提示词流程：先根据论文、实验数据和结果图生成 16:9 开题答辩 PPT 图片，再按原顺序重建为可编辑 PPTX。 | 在支持创建图片的 GPT 网页对话中制作开题答辩或组会 PPT。 | 提示词工作流 |

## [视频与笔记](04-video-and-notes/README.md)

把文档变成讲解视频，把视频和字幕变成笔记。

| Skill | 用途 | 触发场景 | 类型 |
| --- | --- | --- | --- |
| [doc-to-manim-video](https://github.com/shizaishiwo323/doc-to-manim-video-skill) | 把知识文档和模型图做成带旁白的讲解动画视频，用 manimlib、edge-tts 和 HyperFrames 制作，并校验公式按 LaTeX 渲染。 | 公式推导视频、科研教学视频、文档转讲解动画、把概念图或模型图矢量重绘后做动态讲解。 | 独立仓库 |
| [video-subtitle-notes](https://github.com/shizaishiwo323/video-subtitle-notes) | 把视频和字幕转换为中文 Markdown 笔记，保留全部字幕文字，并在合适位置插入从视频截取的画面。 | 手上有视频和 `.srt`、`.vtt`、`.ass`、`.ssa` 字幕，需要课堂笔记、转录笔记或插入截图。 | 独立仓库 |

## [内容运营自动化](05-content-automation/README.md)

小红书图文从素材到发布的流水线。三个 skill 配合使用，并绑定 `xhs-auto-workflow` 项目的本地路径和环境，换机器使用前需要改路径。

| Skill | 用途 | 触发场景 | 类型 |
| --- | --- | --- | --- |
| [xhs-auto-workflow-material-pipeline](https://github.com/shizaishiwo323/xhs-auto-workflow/tree/main/.codex/skills/xhs-auto-workflow-material-pipeline) | 编排小红书图文全流程：盘点素材、必要时爬取、移交素材生成、校验素材包、定时发布、邮件汇报。 | 运行小红书自动化全流程或定时发布。 | 混合仓库子目录 |
| [xhs-material-pipeline](https://github.com/shizaishiwo323/xhs-auto-workflow/tree/main/.codex/skills/xhs-material-pipeline) | 分析素材、爆款参考、账号数据和历史违规记录，生成可自动发布的小红书图文素材包。 | 生成标题、正文、封面、配图，或根据账号数据和爆款参考做新笔记。 | 混合仓库子目录 |
| [xhs-shared-rules](https://github.com/shizaishiwo323/xhs-auto-workflow/tree/main/.codex/skills/xhs-shared-rules) | 上面两个 skill 共用的硬规则：字数和话题限制、humanizer 与 imagegen 留痕、manifest、同主题去重、删除限制。 | 由另外两个 skill 引用，也用于其他小红书相关维护任务。 | 混合仓库子目录 |

## [智能体协作](06-agent-collaboration/README.md)

调整与智能体协作方式的 skill。

| Skill | 用途 | 触发场景 | 类型 |
| --- | --- | --- | --- |
| [grill-me](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me) | 就计划或设计方案对用户连续追问，沿决策树逐支确认，直到双方理解一致。 | “拷问我”“审一下这个方案”“帮我找方案的漏洞”，或需要压力测试计划和设计时。 | 第三方改版 |

## 目录结构

```text
01-scientific-writing/    科研写作
02-literature-reading/    文献检索与阅读
03-figures-and-slides/    图件、图像与演示
04-video-and-notes/    视频与笔记
05-content-automation/    内容运营自动化
06-agent-collaboration/    智能体协作
```

每个类别目录下的 `README.md` 列出各 skill 的用途、何时使用、输入、输出和链接。

## 安装

把 skill 所在的目录（含 `SKILL.md`）复制到以下位置之一，目录名与 `SKILL.md` 中的 `name` 保持一致：

```text
~/.claude/skills/<skill-name>/    Claude Code
~/.codex/skills/<skill-name>/     Codex
```

`学术PPT制作流程` 是提示词，不需要安装。

## 新增 skill

1. 按用途选择类别，在该类别的 `README.md` 中按现有格式增加一节。
2. 在本文件对应类别的表格中增加一行。
3. 优先使用链接；只有没有其他仓库可放的 skill，才把内容放进类别目录。
