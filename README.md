# 影视设计 skill 体系 · v0.8.0

帮助普通人把想法拍成专业、有表现力的画面。主动参与导演与画面设计，用具体拍法帮助人选择、发现和完善表达，再落实为分镜、关键原画与实际播放。

从当前问题进入，不要求用户先懂术语、写全剧本或走完固定流水线。图片、视频使用创作者能提供的模型与工具，设计不绑定供应商。

## 五个技能

| Skill | 负责的问题 | 典型请求 |
|---|---|---|
| [film-direction](film-direction/SKILL.md) · 导演共创 | 参与理解意图、提出画面表达、比较拍法并引导完善 | “他已经接受好意，但不愿先让步，怎么拍？” |
| [shot-design](shot-design/SKILL.md) · 镜头设计 | 调度、机位、构图、镜序与镜内变化 | “把选定拍法展开成十二秒内的分镜。” |
| [keyframe-design](keyframe-design/SKILL.md) · 关键画面 | 共享 layout、关键姿态、必要转折帧与原画回改 | “把这段落实为能画出来的关键原画，先解决接触。” |
| [screen-media](screen-media/SKILL.md) · 媒体执行 | 按可用模型能力组织参考、转换输入、生成和局部修正 | “用我手头的图片编辑模型出原画，再用另一家视频模型生成。” |
| [animatic-review](animatic-review/SKILL.md) · 动态预演与回改 | 时间、声音、剪接、实际观看和最早失效处 | “为什么图都对，连起来却没有表现出我想要的意思？” |

技能可以协作或单独使用。导演共创是面向模糊创作意图的入口，不额外增加只负责转发的总控 skill；已有原画、分镜或视频可直接进入相应技能。技能之间传递当前所选方案与素材，不重做已确认的工作，不逐阶段制造审批。

## 从一句话开始

> 用 $film-direction 帮我设计一个十二秒内的片段：甲递杯，乙接了。我想让人感觉乙接受了好意，却不愿先让步；别煽情。我不懂镜头，请带着我一起把画面做出来。

应得到可想象的拍法与推荐，例如同框呈现“回避对视却接住”，或最后揭示杯子已在手中；比较观看差异，再随用户反馈改变距离、构图、镜序或时间。不会先让人填写焦段、机位与专业参数，也不会只交一张术语齐全的表。

体系重点处理约十五秒以内的片段，但时长不决定镜数或原画张数。原画可以反过来改变导演方案；宫格用来并排审阅，时间线检查信息显露、表演与声音。实际模型能力不足时说明损失与替代，不悄悄重写表达。

## 安装与工具

将以上五个同名目录复制到同一宿主技能目录。每个都有 SKILL.md 和 agents/openai.yaml，保持自动发现；已安装旧版时先保存本机改动。各技能没有必须读取仓库 research、书籍 OCR 或外部服务才能设计的依赖。

[下载 v0.8.0 安装包](https://github.com/czh869452912/film-design-skills/releases/tag/v0.8.0)，解压后复制五个技能目录即可。包内包含文件 SHA256 清单，外部附压缩包校验值；研究资料、模型客户端和生成素材不进入安装包。本地构建运行 `python tools/build_release.py`，产物在 `dist/`。

模型无关的本地工具集中保留在 [shot-design/scripts](shot-design/scripts/)，由有需要的技能使用，避免复制多套实现。[数据与命令](shot-design/references/shot-list-spec.md) 支持文字方案、独立图片排宫格、标注、参考包和动态分镜。Python 工具需要 3.10+；图像需要 Pillow；媒体需要 FFmpeg／FFprobe。

需要图像工具时运行 `python -m pip install -r requirements.txt`。只做文字设计不需要安装 Python 依赖或配置模型账号。

```text
python shot-design/scripts/selftest.py --verbose
python shot-design/scripts/board.py plan.json --images panels --out review-board.png --columns 2
python integrations/novelai/selftest.py
```

[NovelAI 可选适配](integrations/novelai/README.md) 保留在仓库，独立于通用技能安装。旧 H3、NovelAI 实验留作证据；不因为存在本机账号或某个字段就强制选择它们。

## 研究与验证

[关键原画调研](research/key-animation-workflow.md) 与 [导演能力及社区工具调研](research/ai-drama-directing-landscape.md) 是本次改造依据。[v0.8 改造与验证](research/suite-v0.8.md) 区分结构／工具检查、行为推演与尚待生成及观众验证的内容。[完整研究索引](research/README.md)

工具验证能检查文件、像素、帧序与时间，不能给艺术质量背书。历史 [v0.7 复测](research/live-v0.7/report.md) 的动作与版式失败仍然成立，不因改版改称通过。

代码与原创文本采用 [MIT License](LICENSE)；方法出处与署名见各自参考资料及 [NOTICE](NOTICE)。[版本记录](CHANGELOG.md)。

| 目录 | 内容 |
|---|---|
| 五个同名技能目录 | 可独立安装的运行指引、按需方法与共用工具 |
| `examples/` | 不进入安装包的公开导演方案对照 |
| `integrations/` | 可选供应商适配，独立于通用技能 |
| `research/` | 调研、实际实验与明确标识的历史归档 |
| `tests/fixtures/legacy/` | 旧数据格式回归样本 |
| `tools/` | 打包与仓库研究辅助工具 |
| `artifacts/`、`build/`、`reference/`、`dist/` | 忽略的本地资料、生成结果和构建产物 |
