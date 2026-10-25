# 参考资源清单（2026-10）

给 `shot-design` 找"还能从哪里借"的调研。分五类：公开 Agent Skills、书、模型侧官方指南、学术与数据、可落地的采纳清单。

**版权提醒**：`smixs/visual-skills` 是 CC BY 4.0，任何衍生必须保留署名；`ai-film-skills` 是 Apache-2.0。**借结构与方法，不抄原文**，这样最省事也最安全。

---

## 1. 公开的 Agent Skills

| 资源 | 是什么 | 值得借的点 | 许可 |
|---|---|---|---|
| [62656456/ai-film-skills](https://github.com/62656456/ai-film-skills) | 21 个影视 Agent Skills（18 常规 + 3 实验），含编剧、分镜、资产、类型视觉、白模预演 | **FCML 运动机制索引**（115 条，短索引 + 按需读单条）；"观看组织先于术语"的比较仪式（起/转/终画框）；五列分镜表；白模 → 生成的检查链；21 张分镜研究，逐图记录问题 | Apache-2.0 |
| [smixs/visual-skills](https://github.com/smixs/visual-skills) | `video` + `image` 两个技能，含 `dramaturgy.md`、七条法则、逐模型参考文件 | **dramaturgy 先行**（语法不值钱，调度才值钱）；Murch 剪辑六法则量化表；场景公式 `desire + obstacle + geometry + gaze + rhythm`；每条镜头三个物理事实；14 字段分镜行；禁词表 | CC BY 4.0（须署名） |
| [anthropics/skills](https://github.com/anthropics/skills) | Anthropic 官方技能实现 | SKILL.md 的写法与目录结构基线；渐进披露的官方示范 | 见仓库 |
| [skills.sh](https://skills.sh) | 技能注册表（`npx skills add …`） | 发现与安装生态；我们的技能也可以按这个格式发布 | — |
| [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) / [Chat2AnyLLM/awesome-claude-skills](https://github.com/Chat2AnyLLM/awesome-claude-skills) / [itgoyo/awesome-claude-code-skills](https://github.com/itgoyo/awesome-claude-code-skills) | 三个清单仓库 | 快速扫同类技能；注意大量条目是薄包装 | 各自 |
| [alphaparkinc/genpark-cinematic-storyboard-…](https://github.com/alphaparkinc/genpark-cinematic-storyboard-scene-sequence-synthesizer-skill) | 一个"电影分镜合成"技能 | 反面样本：README 只有 quickstart 与 MCP 入口，没有分镜方法论——**说明这个领域真正稀缺的是 craft，不是 wrapper** | MIT |

**结论**：这个领域已经有人做了"技能矩阵"，但**没人把"镜头设计方法"做成可校验的数据结构 + 可执行的校验器 + 可审阅的 animatic**。我们的差异点仍然成立：`validate` + `brief` + `animatic.py`。

---

## 2. 书

### 2.1 镜头语言与语法（补 `shot-grammar.md`）

| 书 | 补什么 |
|---|---|
| Steven D. Katz, *Film Directing: Shot by Shot* (1991) | 已有。景别/角度/轴线/取景的骨架 |
| Steven D. Katz, *Cinematic Motion* (2nd ed., 2004) | Shot by Shot 的续作，专攻**移动摄影与调度**，比现有 `shot-grammar` 的运镜段深得多 |
| Daniel Arijon, *Grammar of the Film Language* (1976) | 分镜语法最系统的一本：对话场景的**机位图解法**、越轴的 N 种合法方式、多人调度 |
| Gustavo Mercado, *The Filmmaker's Eye* (2nd ed., 2019) | 每种景别/构图"为什么用、什么时候别用"，一页一例，适合做**模板卡的写法** |
| Joseph V. Mascelli, *The Five C's of Cinematography* (1965) | 构图、连续、剪辑、特写、机位五章，老但极准，尤其"镜头内的连续" |
| Jeremy Vineyard, *Setting Up Your Shots* (2nd ed., 2008) | 100+ 条"镜头配方"，适合与 `templates.md` 对照补条目 |
| Christopher Kenworthy, *Master Shots* Vol.1–3 | 按场景类型（追逐、对峙、亲密、恐怖）给机位方案，**最接近我们要的模板库** |

### 2.2 构图与视觉结构（补 `composition.md`）

| 书 | 补什么 |
|---|---|
| Bruce Block, *The Visual Story* (3rd ed., 2020) | 把"视觉结构"拆成对比、空间、线条、形状、色彩、节奏六个变量——正好补我们"明暗块面"之外的结构层 |
| Marcos Mateu-Mestre, *Framed Ink* (2010) | 已有 |
| Marcos Mateu-Mestre, *Framed Perspective* Vol.1–2 (2016/2017) | 透视与空间可信度；分镜里"空间不成立"的根源多半在这里 |
| Scott McCloud, *Understanding Comics* (1993) | 分格、时间、视线引导；**animatic 的节奏与"格子之间发生了什么"** |
| 理查德·威廉姆斯《原动画基础教程》 | 见 2.4 |

### 2.3 分镜与导演叙事（补 `storyboard.md` / `beats.md`）

| 书 | 补什么 |
|---|---|
| Francis Glebas, *Directing the Story* (2008) | 迪士尼分镜导演的方法论：故事→情绪→分镜，**"观众该看哪里"** 的完整推导 |
| Mark Simon, *Storyboards: Motion in Art* (3rd ed., 2006) | 行业实务：分镜的交付规格、箭头与标注惯例、与客户/导演的沟通格式 |
| John Hart, *The Art of the Storyboard* (2nd ed., 2007) | 分镜的视觉语言与构图，案例多 |
| Giuseppe Cristiano, *The Storyboard Artist* (2011) | 职业分镜师的取舍：什么该画细、什么该省略 |
| 《动画分镜头台本设计》（第三版，中文教材） | 国内教学体系的分镜术语与格式，适合对齐中文用户词汇 |

### 2.4 动画时间与表演（补 `beats.md` 的时长感）

| 书 | 补什么 |
|---|---|
| Richard Williams, *The Animator's Survival Kit* (2001) | 时间、间距、预备/跟随；**打斗节奏**的原始教材 |
| Harold Whitaker & John Halas, *Timing for Animation* (2nd ed., 2009) | 帧级时间感：多少帧算"停顿"、多少帧算"爆发" |
| Frank Thomas & Ollie Johnston, *The Illusion of Life* (1981) | 12 条动画原则；表演与重量的来源 |
| Ed Hooks, *Acting for Animators* (4th ed.) | 把"情绪"翻译成**意图 + 动作 + 反应**，正好对应我们的 cues/subtext |

### 2.5 剪辑与节奏（补 `sequence-rhythm.md`）

| 书 | 补什么 |
|---|---|
| Walter Murch, *In the Blink of an Eye* (2nd ed., 2001) | **剪辑六法则**（情绪 51% > 故事 23% > 节奏 10% > 视线 7% > 平面 5% > 空间 4%）——可直接变成校验器的权重 |
| David Bordwell & Kristin Thompson, *Film Art* (12th ed., 2019) | 学院派的分镜/剪辑术语与例证，做术语校准 |

---

## 3. 模型侧公开指南（只借"执行约束"，不借写法）

| 资源 | 可借的点 |
|---|---|
| [OpenAI Cookbook — Sora 2 Prompting Guide](https://github.com/openai/openai-cookbook/tree/main/examples/sora)（2026-03 更新） | 官方明确"一个镜头一个运动 + 一个主体动作"；动作按 **beat/count** 写（"四步到窗边、停、最后一秒拉帘"）；长提示词给控制、短提示词给创造；分镜式结构（Cinematography / Actions / Dialogue / Background Sound）；图像输入锁首帧 |
| [Kling 3.0 Omni 用户指南](https://klingai.com/quickstart/klingai-video-3-omni-model-user-guide) | 多模态参考与多镜头的官方口径 |
| [Runway Gen-4 Prompting Guide](https://help.runwayml.com/hc/en-us/articles/39789879462419-Gen-4-Video-Prompting-Guide) | 参考图角色绑定、镜头语言词表（页面有反爬，需浏览器打开） |
| [BytePlus Dreamina Seedance 2.5 提示词指南](https://docs.byteplus.com/zh-CN/docs/ModelArk/seedance-2-5-prompt-guide) | 已用于 `handoff.md` 的时长/阶段预算 |
| [Reallusion AI Studio — Multi-Shot & Multi-Dialogue](https://manual.reallusion.com/ai-studio/custom-tool/prompt-multi-shot-dialogue.htm) | 多镜头 + 对白的提示词组织方式，可作为第三家对照 |

**用法**：这些只能决定"设计时给多少预算、留多少自由度"，不能回流成 `shot-design` 的提示词语法（上一轮已经踩过这个坑）。

---

## 4. 学术与数据资源

| 资源 | 用途 |
|---|---|
| [Shot2Story (ICLR 2025)](https://proceedings.iclr.cc/paper_files/paper/2025/hash/672d794a6052b6beab0e2e002204d974-Abstract-Conference.html) | 多镜头视频的 shot-level 描述基准，可用来**校准"一镜一句"的信息密度** |
| [MovieNet (ECCV 2020)](https://github.com/LokiXun/diffusion_video_paper_list/blob/master/2020_07_ECCV_MovieNet--A-Holistic-Dataset-for-Movie-Understanding_Note.md) | 电影级标注（镜头边界、场景、人物），可用于**评测"我们的镜头表是否能被机器读懂"** |
| [影视镜头类别的自动识别研究 (TCLT 2025)](https://tc.computer.org/tclt/10-1109-2025-0101002/) | 景别分类的机器判定口径；未来可让校验器**按景别序列**做节奏检查 |

---

## 5. 采纳清单（按性价比排序）

1. **P0 — 把 `templates.md` 升级成"带编号的机制库"**：像 FCML 那样每条一个 ID + 一句规范 + 失败模式，按需检索；`shotlist.py` 可校验"用了不存在的机制"。
2. **P0 — 加"起/转/终画框"比较仪式**：同一剧情下比较三种观看方案（谁在框内多大、什么同时可见、何时显露），选定后才排机位。这条能直接提升"设计感"，且不增加提示词负担。
3. **P1 — 把 Murch 六法则做成校验权重**：切断/时长建议按 情绪 > 故事 > 节奏 > 视线 > 平面 > 空间 排序，写进 `qc-repair.md`。
4. **P1 — 五列分镜表作为默认输出之一**：`时间｜景别机位｜摄影机｜画面与动作｜台词声音`，与现有 JSON 并存（人读表、机读 JSON）。
5. **P2 — 白模预演**：`ai-film-skills` 的白模 → 生成检查链值得抄流程，但需要 3D 工具，先记为实验。
6. **P2 — 数据化评测**：拿 Shot2Story / MovieNet 的子集，测"我们的 shot card 能否还原镜头"，作为技能迭代的客观指标。

## 6. 不建议借的

- **六模块母提示词**之类的 prompt 规格：那是提示词技能的职责，回流会重犯上一轮的错误。
- 大而全的"21 技能矩阵"：我们的单技能分层更适合高频迭代。
- 只有 README 没有 craft 的包装型技能。
