# 镜头设计与情绪表达 Skill 使用说明

面向 Seedance 2.5、MiniMax H3 等视频生成模型的**镜头设计与预演**技能：从节拍 → 镜头表 → 分镜图 → 动态分镜，最后把设计稿交给对应模型的提示词规范技能。本技能不写提示词格式。

## 完整链路

```
创意/剧情 → 节拍(beats) → 镜头表(shot list) → 分镜绘制说明(storyboard brief)
        → 分镜图(panels, 由图片模型绘制) → 动态分镜(animatic) → 设计稿交付 → 提示词技能
```

## 边界：设计 vs 规格化

| 层 | 负责 | 不负责 |
|---|---|---|
| 本技能 `shot-design` | 意图、节拍、景别、调度、构图、运动、动作、声音设计、参考图角色、连续性、禁止项 | 字段名、段落顺序、`<Subject N>` 编号、保留度标记、`<d>` 标签、字数、负面词位置 |
| 提示词技能 | 最终提示词的结构与语法 | 设计判断本身 |

MiniMax H3 在本项目的 AutoDL 工作流里是 **Ref2VA**（多图多音参考、六段式）：工作流最多吃 9 图 + 3 音频，素材是"参考"而不只是首帧。提示词交给 `h3-prompt-writing` 写，本技能只负责把设计稿写清楚。

## 为什么需要它

视频模型负责执行，不负责调度。直接写"电影感、悲伤、推镜头"得到的是平均值：构图平淡、运动无动机、情绪靠形容词。这个 Skill 要求先回答三个问题——**观众此刻知道什么、被放在什么位置、这一镜改变了什么**——再决定景别、角度、镜头、运动与构图。

## 核心方法：六拨盘

一个情绪不是形容词，而是一组设置：

| 拨盘 | 低 | 高 |
|---|---|---|
| 距离 Proximity | 大全景——旁观评判 | 大特写——共处其中 |
| 权力 Power | 俯拍——被压制 | 仰拍——压迫感 |
| 压迫 Pressure | 留白开阔 | 遮挡、贴边、拥挤 |
| 稳定 Stability | 固定、水平、对称 | 手持、倾斜、失衡 |
| 明暗 Value | 平光、全可读 | 明暗对比、剪影、藏脸 |
| 时间 Time | 长镜头、停留 | 快切、压缩 |

每个镜头最多设定三个拨盘；每一剪最多改变两个。**每个段落保留一个"反常识"选择**（例如：用大全景拍悲伤、用固定机位拍慌乱），否则设计会退回套路。

## 工作流

1. **一句话与一个转折**：写 logline，以及情绪从 A 到 B 的变化。没有转折的段落只是情绪板。
2. **先排节拍**：用 `references/beats.md` 的节拍词表与节奏模板（降临/交锋/大招/对峙/追逐/情绪转折/揭示/告别/喜剧/恐怖/蒙太奇/钩子/训练），写张力曲线——峰值在 70–85%，之后留出收束。**时长按节拍功能分配，不做均分**：蓄力和收束长、爆发和命中短，`render --format rhythm` 会标出均分的段落。
3. **选择拨盘**：为目标情绪定值，并指定一个反常识处理。
4. **先比较观看方案，再选机制**：
   - 4a 为还没锁定的节拍写 2–3 个观看方案，每个方案写三帧：**起始帧 / 转折帧 / 结束帧**（谁在框内多大、什么同时可见、什么被藏起来），按"观众何时知道"排序取舍；
   - 4b 从机制库（`M01`–`M32`）选一个主机制 + 最多一个修饰机制，先读它的失败模式；
   - 4c 按景别 → 角度 → 镜头 → 构图（先明暗块面）→ 调度与视线 → 运动动机 → 出入画与转折帧 → 声音填镜头卡。
5. **画分镜说明**：按 `references/storyboard.md` 给每镜补 `storyboard` 块（画面、箭头、标注、简略等级），用 `render --format storyboard` 输出绘制说明；要图时交给 `gpt-image` / `novelai-image`。
6. **用脚本标注分镜**：`annotate.py` 按 `storyboard.overlays`（归一化坐标）画箭头、视线、冲击点与镜头标签——**不让图片模型画箭头**，标注可重跑、可修改。
7. **查剪辑优先级**：按 Murch 六法则（情绪 51 / 故事 23 / 节奏 10 / 视线 7 / 平面 5 / 空间 4）逐剪检查，`render --format cuts` 会列出每一剪还没声明的高权重项。
8. **做动态分镜**：`animatic.py` 按每镜时长拼接分镜图，生成带 EDL 的 animatic，用来看节奏而不是看图。
9. **交付设计稿**：参考图角色与排除项、连续性、禁止项、节拍窗口。然后由提示词技能写最终提示词：H3 走 `h3-prompt-writing` 的 Ref2VA 六段式。
10. **质检与风险**：跑 `references/qc-repair.md`，点名最可能失败的一镜，并给出 fallback。

## 输出

- 设计意图（logline、转折、情绪曲线）
- 节拍表（beat sheet，含张力与信息变化）
- 镜头表（一镜一行，含机制编号与时长）
- 节奏表（每镜时长/占比/形状，均分会被拦下）
- 五列生产表（时间｜景别机位｜摄影机｜画面与动作｜台词声音）
- 镜头卡 JSON（可用脚本校验、渲染）
- 分镜绘制说明（每格画面、箭头、标注）
- 分镜图 / animatic（需要时）
- 交付设计稿（参考图角色、连续性、禁止项、节拍窗口）
- 质检结果 + 风险与修复

## 脚本

```bash
python scripts/shotlist.py init new.json --title "新片段" --duration 12 --shots 3   # 生成骨架
python scripts/shotlist.py mechanisms                                           # 列出 M01–M42
python scripts/shotlist.py validate examples/descent.json                       # 结构、节拍、机制、时长自检
python scripts/shotlist.py render   examples/descent.json --format md           # 镜头表
python scripts/shotlist.py render   examples/descent.json --format beats        # 节拍表
python scripts/shotlist.py render   examples/descent.json --format framing      # 观看方案对比
python scripts/shotlist.py render   examples/descent.json --format cuts         # 逐剪六法则就绪度
python scripts/shotlist.py render   examples/descent.json --format sheet        # 五列生产表
python scripts/shotlist.py render   examples/descent.json --format timeline     # 时间条
python scripts/shotlist.py render   examples/descent.json --format rhythm       # 时长形状（是否均分）
python scripts/shotlist.py render   examples/descent.json --format load         # 每镜信息密度
python scripts/shotlist.py render   examples/descent.json --format csv          # 表格导出
python scripts/shotlist.py render   examples/descent.json --format storyboard   # 分镜绘制说明
python scripts/shotlist.py render   examples/descent.json --format brief        # 交付给提示词技能的设计稿
python scripts/annotate.py examples/descent.json --images storyboard --out annotated --sheet sheet.png
python scripts/animatic.py examples/descent.json --images annotated --out animatic/animatic.mp4 --transition fade
python scripts/eval.py examples/                                                # 语料统计 + 文档完整性
python scripts/selftest.py                                                      # 工具回归测试（改脚本后跑）
```

脚本不做设计，也不写模型提示词语法：`shotlist.py` 检查并打印设计，`annotate.py` 画标注与箭头，`animatic.py` 拼动态分镜，`eval.py` 做语料统计与文档完整性检查。

## 文件地图

| 文件 | 内容 |
|---|---|
| `SKILL.md` | 工作流、原则、输出契约 |
| `references/beats.md` | 节拍词表、张力曲线、13 种节奏模板、类型节拍要点、节拍→镜头映射 |
| `references/framing-decision.md` | 起始/转折/结束三帧的观看方案比较仪式 |
| `references/templates.md` | 机制库 M01–M42 + 8 种修饰项：用法、配对、失败模式 |
| `references/shot-grammar.md` | 景别、角度、镜头、运动、画框装置、转场及其心理效果 |
| `references/emotion-design.md` | 六拨盘、情绪配方、权力反转、表演可观察线索 |
| `references/composition.md` | 明暗块面、剪影、负空间、线条语言、尺度、视觉路径、竖屏与色彩结构 |
| `references/sequence-rhythm.md` | 问答链、信息差、攀爬与对比、剪辑六法则、银幕方向 |
| `references/storyboard.md` | 分镜绘制规范：箭头、标注、版式、简略等级、审阅标准 |
| `references/shot-list-spec.md` | 镜头卡 / 节拍表 / 分镜块 / 叠加标记的字段与校验规则 |
| `references/handoff.md` | 分工、交付给提示词技能的内容、参考图角色、模型时长预算 |
| `references/qc-repair.md` | 检查表与故障→修复对照（含分镜与 animatic） |
| `references/worked-example.md` | 12 秒完整案例（《末班车》） |
| `references/sources.md` | 两本书的出处、章节与页码锚点 |
| `scripts/shotlist.py` | 校验、骨架生成、11 种格式渲染（md/beats/framing/cuts/sheet/timeline/csv/storyboard/brief…） |
| `scripts/annotate.py` | 给分镜图叠加标签、箭头、视线、冲击点，并拼联系表 |
| `scripts/animatic.py` | 分镜图 → 按时长的 animatic（可加淡入淡出与音轨）+ EDL |
| `scripts/eval.py` | 语料统计（机制覆盖、节拍与景别分布、剪辑就绪度）+ 文档表格完整性 |
| `scripts/selftest.py` | 全工具回归测试（示例 + 合成面板，缺 ffmpeg 时跳过 animatic） |

## 来源

- Steven D. Katz, *Film Directing: Shot by Shot*（调度、连续性、轴线、景别、运动、视点）
- Marcos Mateu-Mestre, *Framed Ink*（构图、明暗、剪影、负空间、情绪化取景）

两本书经 MinerU 转为 Markdown 后提炼；六拨盘系统、情绪配方表、交付协议是在原理之上的原创结构，详见 `references/sources.md`。
