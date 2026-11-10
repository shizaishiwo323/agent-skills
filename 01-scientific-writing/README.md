# 科研写作

英文论文的结构诊断、翻译、润色。三者粒度不同：`agu-writing-workflow` 管全文故事线和机制链，`sci-writing-expert` 管翻译和章节修改，`academic-sentence-polisher` 只动句子。

[返回总览](../README.md)

## agu-writing-workflow

**来源类型：** 独立仓库

**用途：** 面向 AGU 系期刊（GRL、JGR、WRR、JGR: Solid Earth 等）的论文写作流程，按“故事线 > 结构 > 前后呼应 > 机制 > 段落 > 句子 > 用词”的顺序诊断和修改。

**何时使用：** 论文故事线不稳；Introduction 与 Results 前后呼应、铺垫与兑现；Results 小节衔接；机制驱动型地学论文；反应输运、多孔介质、水文地球物理、NMR 论文。

**输入：** 稿件或段落、目标期刊、当前写作阶段。

**输出：** 诊断单（当前阶段、期刊画像、核心矛盾、推荐子技能、当前禁止项、本轮目标、下一步），或与该阶段对应的修改稿和提示词。

**链接：** [agu-writing-workflow](https://github.com/shizaishiwo323/agu-writing-workflow-skill)

## sci-writing-expert

**来源类型：** 独立仓库

**用途：** 把 SCI 稿件翻译、润色、诊断、重排成自然且符合发表习惯的英文，不改变科学含义和证据强度，不虚构数据、引用或机制。

**何时使用：** 中译英；句段润色；逻辑和衔接修复；IMRaD 章节修改；摘要和标题；全文审查；去除 AI 味的自造复合词。

**输入：** 中文或英文科研文本，可附目标期刊和代表论文。

**输出：** 先给修改稿或译文，再给简短说明；较大任务先给诊断，再给修改方案。

**链接：** [sci-writing-expert](https://github.com/shizaishiwo323/sci-writing-expert-skill)

## academic-sentence-polisher

**来源类型：** 独立仓库

**用途：** 只做句子层面的学术润色，保留原有含义、证据强度、引用、公式、图号和段落顺序，不动论文结构。

**何时使用：** 降低 AI 感；简化论文句子；解释含糊术语；去掉无依据的夸大；处理连字符和破折号复合词。

**输入：** 英文句子或段落。

**输出：** 修改后的文本、主要改动、含义是否保持的判断。

**链接：** [academic-sentence-polisher](https://github.com/shizaishiwo323/academic-sentence-polisher)
