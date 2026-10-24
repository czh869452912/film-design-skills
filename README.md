# 镜头设计与预演 Skill

给 AI 视频生成模型（Seedance 2.5 / MiniMax H3）做**镜头设计、情绪表达与分镜预演**的 Agent Skill，外加一套可校验、可标注、可拼 animatic 的工具，以及一次盲评 A/B 实验的完整归档。

技能本身只做设计与预演，**不写提示词规格**——MiniMax H3 的提示词交给 `h3-prompt-writing`（Ref2VA 六段式），Seedance 交给对应的提示词指南。

```
创意/剧情 → 节拍 → 观看方案 → 机制 → 镜头卡 → 分镜图 → animatic → 交付设计稿 → 提示词技能
```

## 目录

| 目录 | 内容 | 入库 |
|---|---|---|
| [`shot-design/`](shot-design) | 技能本体：SKILL.md、14 篇 reference、5 个脚本、3 个示例、许可与变更记录 | ✅ |
| [`ab-test/`](ab-test) | 文本盲评实验：简报、四份设计输出、评委全文、报告、两张对照分镜 | ✅ |
| [`duel-test/`](duel-test) | H3 实拍对比：和服 vs 水手服刀战，两份设计 + Ref2VA 提示词 + 盲评结论 + 切点检测 | ✅（原始帧与视频忽略） |
| [`research/`](research) | 外部参考调研（公开 skill、书籍、官方指南、数据集） | ✅ |
| [`tools/`](tools) | 把参考书 PDF 转 Markdown 的流水线（MinerU）、PDF 切分、示例维护脚本 | ✅ |
| [`reference/`](reference) | 原始参考书 PDF（Katz、Mateu-Mestre） | 🚫 忽略 |
| `build/` | OCR 产物（Markdown + 插图） | 🚫 忽略 |
| `artifacts/` | 本地运行产物：分镜图、animatic、临时镜头卡 | 🚫 忽略 |
| `.dsh/` | 本机安装的项目内技能（NovelAI / H3 / gpt-image 等） | 🚫 忽略 |

## 快速开始

```bash
# 1. 安装到本机技能目录（Windows）
Copy-Item -Recurse shot-design "$env:USERPROFILE\.agents\skills\shot-design"
# macOS / Linux: cp -r shot-design ~/.agents/skills/

# 2. 跑回归测试（不需要网络）
python shot-design/scripts/selftest.py

# 3. 校验并渲染一个示例
python shot-design/scripts/shotlist.py validate shot-design/examples/descent.json --strict
python shot-design/scripts/shotlist.py render shot-design/examples/descent.json --format rhythm
```

在支持技能调用的宿主里（Claude Code、Codex、DSH 等），直接说"用 shot-design 把这段设计成镜头"即可，或以 `skill(name="shot-design")` 加载。

## 技能能做什么

**设计层**：节拍表（13 套节奏模板）、起/转/终观看方案比较、42 条机制库（M01–M42）+ 8 个修饰项、六拨盘情绪系统、构图（含竖屏与色彩结构）、问答链与剪辑六法则。

**预演层**：分镜绘制规范（箭头、标注、版式、简略等级）→ `annotate.py` 用脚本画箭头与标签（不交给图片模型）→ `build_refpack.py` 把干净分镜打包成有序参考（`<Picture N>` ↔ `[Shot N]`）→ `animatic.py` 按每镜时长拼接，可加淡入淡出与音轨 → EDL。

分镜不光是用来看的，**默认就是视频模型的参考图**：一镜一张、声明为"构图与调度"、排除草图风格；需要风格时再加一张彩色关键帧（实测结论见 [handoff.md](shot-design/references/handoff.md)）。

**交付层**：设计稿（参考图角色、连续性、禁止项、节拍窗口）交给提示词技能；H3 走 Ref2VA。

**校验**：`validate --strict` 检查结构、节拍、机制、时长、剪辑就绪度、均分节奏、竖屏景别等；`eval.py` 做语料统计与文档表格完整性检查；`selftest.py` 是 5 项回归门。

## 示例

| 文件 | 内容 |
|---|---|
| [`examples/descent.json`](shot-design/examples/descent.json) | 10 s 动作段：3.6 / 1.8 / 2.2 / 2.4，hold-snap-hold |
| [`examples/last-train.json`](shot-design/examples/last-train.json) | 12 s 情绪段：5.0 / 3.0 / 4.0 |
| [`examples/the-interview.json`](shot-design/examples/the-interview.json) | 15 s 对话与权力反转 |
| [`worked-example.md`](shot-design/references/worked-example.md) | 从设计到交付的完整叙事案例 |
| [`worked-example-action.md`](shot-design/references/worked-example-action.md) | 动作段：观看方案对比、机制选择、剪辑就绪 |

本地运行产物（分镜图、animatic、H3 成片）在 `artifacts/`，不入库。

## 评测

[`ab-test/report.md`](ab-test/report.md)：2 份简报 × 2 条件（有无技能），独立子代理执行、匿名盲评。

- 技能方 2 胜 0 负：36 vs 32（情绪向）、37 vs 30（动作向），满分 40。
- 结构检查：技能 6/6、6/6；基线 2/6、2/6。
- 基线并非全面落后：光学与距离描述更硬、单镜信息密度更高；技能赢在节拍、观看方案、机制、风险预案。
- 实验暴露的三条共性问题（信息负荷、禁止项缺正向替代、"看错"而非"画错"）已修入 0.4.1。

[`duel-test/report.md`](duel-test/report.md)：同一简报用 MiniMax H3 实拍对比（和服 vs 水手服刀战）。

- 这次**基线赢**（21 : 19）：技能把峰值押在"刀咬鞘"的物件特写上，1.2 s 内模型保不住"谁握着什么"；基线用 B 的瞳孔反应承担"一击之后空气变了"。
- 切点执行无差异：两版检测到的画面突变都落在各自宣告的切点 ±0.5 s 内。
- 结论已修入 0.4.3：接触帧必须有人（手或脸），否则下一镜补反应。

## 依赖

| 用途 | 依赖 |
|---|---|
| 校验、渲染、语料评估 | Python 3.9+（仅标准库） |
| 分镜标注 `annotate.py` | Pillow |
| animatic `animatic.py` | FFmpeg（PATH 中） |
| A/B 实验与分镜图 | NovelAI、MiniMax H3（AutoDL）——**仅测试时使用，不是技能运行依赖** |

## 版本与许可

当前 `shot-design/meta.yaml` 为 **0.4.2**，变更见 [`CHANGELOG.md`](shot-design/CHANGELOG.md)。

MIT（见 [`LICENSE`](shot-design/LICENSE)）。设计原则来自 Katz《Film Directing: Shot by Shot》、Mateu-Mestre《Framed Ink》等；结构上受公开项目启发，逐项署名见 [`NOTICE`](shot-design/NOTICE)。
