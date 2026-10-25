# NovelAI 可选整页适配（历史路径）

将一个短段的关键状态放在同一张图中，保留稳定人物与画风，再检查和裁分。

## 先分清四类信息

| 内容 | 放置处 |
|---|---|
| 画风、媒介、配色、全页布局、共享环境与光线 | base prompt |
| 每格景别、机位、道具状态、两人关系、行动证据 | 按阅读顺序加入 base prompt 的 panel summary |
| 固定发型、脸、服装、身份 | 本地 character 表，组装时复用 |
| 该人该格的动作、表情、视角、位置 | 该次出场的 character caption 与 center |

**同一个人跨四格出现，使用四个出场槽。** 两人在四格都可见就是八槽，不是八个不同人物。每槽包含足以识别该人的稳定外观，以及本格动作。不要让一个多中心 caption 同时承担“伸手、共握、松开”等不同状态。局部特写可显式提供 `visible_appearance`，只写可见特征，避免全身服装把特写撑回全身。

V5 支持最多 22 个 character 槽。按格顺序、格内从左到右组织出场；人数标签写主场景的实际人数。人物 ID 只用于本地映射，模型靠外观提示辨认人物。共同动作放 summary，个人动作放其 caption。`source#`、`target#`、`mutual#` 可辅助官方支持的互动标签，接触对象仍需写清楚。

空镜没有人物槽，以 `no humans` 加环境描述留在 summary。旁白、台词和标号可后期排版；本工具面向无字粗板，固定追加 no text / no speech bubbles，不用于生成带对白的正式漫画。

## 宫格与坐标

先完成必要状态，再决定分页。常用 2×2；六格通常为 3 列×2 行。动作和手部需要可见尺寸，拥挤时减少每页格数。不要为了填满格子制造新镜头；最后一页可换为较小网格。跨页复用相同人物表、风格和场地锚点，但不同页仍可能漂移，不能以相同 seed 代替检查。

若目标单格比例为 a:b，C 列 R 行的整页约为 C×a : R×b；边框会占少量空间。四个 16:9 画格可用 2048×1152，六个可用 1536×576（每格约 512×288，细部较小）。这些是候选尺寸，不是固定质量标准；实际可用尺寸、点数和模型限制由现有生成工具确认。

`local_center=[u,v]` 是格内坐标；第 c 列、第 r 行从 0 起算，转为整页：

```text
x = (c + u) / C
y = (r + v) / R
```

例如四格页右下格中偏左的人：`u=.25,v=.5` → `x=.625,y=.75`。坐标引导人物中心，画框与接触关系需读图确认。布局使用自然语言明确行列和阅读顺序，正向保留 `comic, multiple views`，UC 与所需宫格保持一致。

## 可重复的组装与裁图

`integrations/novelai/pageboard.py` 在本地输出提示与计划布局，生成交给现有 NovelAI 客户端。示例输入：

```json
{
  "page_id": "page-01", "columns": 2, "rows": 1,
  "width": 1536, "height": 448,
  "style": "clean lineart, restrained flat colors",
  "global_prompt": "1girl, comic, same woman in both panels, quiet kitchen",
  "negative": "watermark, bad anatomy",
  "characters": {"A": {"appearance": "girl, black bob hair, red cardigan"}},
  "panels": [
    {"panel_id":"S01-P01", "shot_id":"S01", "summary":"Medium shot, woman reaches toward a cup on the table.",
     "instances":[{"character_id":"A", "prompt":"reaching right hand toward cup", "local_center":[0.5,0.5]}]},
    {"panel_id":"S01-P02", "shot_id":"S01", "summary":"Same camera, cup raised clear of table.",
     "instances":[{"character_id":"A", "prompt":"holding single cup above table", "local_center":[0.5,0.5]}]}
  ]
}
```

```text
python integrations/novelai/pageboard.py compile page.json --sequence sequence.json --out page-input
```

`--sequence` 检查 shot/panel 归属；可以选择原序列的一个子集分页，不改变镜头或时间。输出 `prompt.txt`、`negative.txt`、`characters.json`、`layout.json`。生成由可用适配器执行，例如已有 CLI 的 `--prompt-file`、`--negative-file`、`--characters`。计划 bounds 只表示意图，不能直接当实际裁图坐标。

出图后先打开原图，确认格数、阅读顺序和边框；实际分格可能偏离等分线。给这张原图制作 review JSON：

```json
{
  "image":"raw/image_0.png", "image_sha256":"完整原图的SHA256",
  "layout_reviewed":true,
  "panels":[
    {"panel_id":"S01-P01", "box":[10,8,760,440], "content_approved":false,
     "observation":"记录实际可见动作，以及与设计的差异"},
    {"panel_id":"S01-P02", "box":[775,8,1526,440], "content_approved":false,
     "observation":"记录实际可见动作，以及与设计的差异"}
  ]
}
```

box 为像素 `[left,top,right,bottom]`，右下边界不含在裁图内。路径相对于 review JSON。用 Python `hashlib.sha256(Path(image).read_bytes()).hexdigest()` 计算原图摘要。

```text
python integrations/novelai/pageboard.py crop review.json --layout page-input/layout.json --out clean-panels
```

工具保留原图，输出按 panel ID 命名的干净裁图与 manifest；manifest 保留页、镜头、画格、裁框、原图摘要和逐格意见。**layout_reviewed 不表示 content_approved**；失败画格可以裁出用于诊断，不能因此充当已批准关键帧。更新 sequence 的 panel.image 后，再交给 annotate / animatic / build_refpack；不要把四格页当一张视频首帧。

整页检查分别看人物／画风和动作／空间；局部失败时按体系的动态预演与回改方法修改。接口调用与失败停止遵循所用客户端。来源见下方。

## 来源

- [NovelAI 多角色文档](https://docs.novelai.net/en/image/multiplecharacters/)：主提示、人物提示与坐标；当前接口参数仍由实际客户端确认。
- [novelai_local_web 提示文档](https://github.com/YILING0013/novelai_local_web/blob/a30d510a4f4eece69bed56958e9468196114c95e/docs/comic-prompts-current.zh-CN.md)：稳定人物与逐次出场分开。编译器为独立实现。

本页保留已有适配约定，不代表当前通用技能优先推荐整页一次生成。
