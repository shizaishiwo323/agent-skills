# 图件、图像与演示

科研配图、位图生成，以及从论文到可编辑 PPT 的流程。

[返回总览](../README.md)

## nature-figure

**来源类型：** 第三方改版

**用途：** 用 Python 或 R 创建、修改、审查和导出投稿级科研图件，包括多面板图、机制示意图和图形摘要草稿。

**何时使用：** 论文配图、科研绘图、多面板图、投稿图件审查。不用于交互看板、数据清洗或纯统计分析。

**输入：** 数据、图注或论文结论，可附已有图件。

**输出：** 绘图脚本、图件文件和质检结果。本地改版只输出 PNG（默认 600 dpi）。

**说明：** 上游为 `Yuan1z0825/nature-skills`（Apache-2.0）。本地改版增加了优先级最高的本地规则，改动未发布，这里只保留索引。

**链接：** [nature-figure](https://github.com/Yuan1z0825/nature-skills/tree/main/skills/nature-figure)

## image-gen

**来源类型：** 混合仓库子目录

**用途：** 让 Claude 调用本机 Codex 的图像生成能力，生成或编辑插画、海报、封面、配图、Logo 草图和照片风格图。

**何时使用：** 用户要一张真实的位图时自动使用。流程图、SVG 和数据图不用它。

**输入：** 图片描述、比例、数量，可附参考图或待编辑图片。

**输出：** 保存到 `outputs/images/` 的图片文件。需要本机已登录的 Codex CLI。

**链接：** [image-gen](https://github.com/shizaishiwo323/claude-relay-public/tree/main/extras/skills/image-gen)

## rebuild-scientific-poster-ppt

**来源类型：** 独立仓库

**用途：** 把科研海报、图形摘要或高密度单页参考图高保真重建为可编辑 PowerPoint。参考图决定版式，论文决定科研图、公式、单位和结论。

**何时使用：** 手上有 PNG、JPG 或 PDF 参考图和配套论文，需要可编辑 PPTX、子图拆分还原、渲染对比和逐子图审核。

**输入：** 视觉参考图、配套论文或 PDF。

**输出：** 可编辑 `.pptx`、独立科研图素材、同尺寸预览、叠加图和差异图、结构校验、逐子图审核结果。

**链接：** [rebuild-scientific-poster-ppt](https://github.com/shizaishiwo323/rebuild-scientific-poster-ppt)

## 学术PPT制作流程

**来源类型：** 提示词工作流

**用途：** 两阶段提示词流程：先根据论文、实验数据和结果图生成 16:9 开题答辩 PPT 图片，再按原顺序重建为可编辑 PPTX。

**何时使用：** 在支持创建图片的 GPT 网页对话中制作开题答辩或组会 PPT。

**输入：** 论文、实验数据、结果图、版式参考材料。

**输出：** 按序保存的页面图片（`slide_01.png` 等）和最终 `.pptx`。

**说明：** 没有 `SKILL.md`，是手动使用的提示词，不能作为 skill 安装。

**链接：** [学术PPT制作流程](https://github.com/shizaishiwo323/gpt-literature-management/tree/main/%E5%AD%A6%E6%9C%AFPPT%E5%88%B6%E4%BD%9C%E6%B5%81%E7%A8%8B)
