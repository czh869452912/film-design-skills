# 数据与工具

需要保存结构化方案或组装媒体时使用。所有脚本从 skill 目录运行；文字分镜无需先转 JSON。

## 最小数据

```json
{
  "title": "递杯",
  "shots": [{
    "id": "S01",
    "framing": {"size": "MS", "angle": "eye-level"},
    "camera": {"move": "locked"},
    "panels": [
      {"id": "S01-P01", "description": "甲持杯，乙伸手靠近。"},
      {"id": "S01-P02", "description": "乙托住杯底，甲仍握杯。"},
      {"id": "S01-P03", "description": "甲松手，乙独自持杯。"}
    ]
  }]
}
```

必需内容为非空 `shots`、各镜 `id`、各格 `id/description`。ID 使用字母、数字、下划线与连字符；镜头 ID、全序列画格 ID 各自唯一。数组顺序就是镜头和画格顺序。

| 可选字段 | 用途 |
|---|---|
| `scene` | 共享场地、地标、路径与摄影机位置 |
| `shots[].purpose/framing/camera` | 观看理由、取景与连续摄影机描述 |
| `beats` + `shots[].beat_ids` | 节拍表与多对多关联；引用须存在 |
| `panels[].state` | 位置、视线、持物与承托等状态记录 |
| `panels[].framing/composition/staging/sound` | 覆盖该镜对应字段，表达本格变化 |
| `review` | 检查过的材料、具体问题与修改记录 |

## 时间与图片

草稿可以未定时。动态分镜前填写各格 `duration_s`，所有时间为有限正数；镜头时间由画格相加。另填 `shot.duration_s` 时须与合计一致，单格镜头可沿用镜头时间。`target.duration_s` 表达总约束，完整定时后须与总和一致。多个未定时画格不会被自动均分。

`panels[].image` 可指向图片，相对路径以 JSON 所在目录解析。通常按画格命名，如 `S01-P02.png`。`--images` 覆盖图片根目录，该目录内同名画格优先，且不回退到原绝对路径。支持 png/jpg/jpeg/webp。

标注和参考包默认拒绝缺图，部分输出用 `--allow-missing`。动态分镜可显示占位图，`--require-images` 禁止占位。EDL 记录原 shot/panel、请求时间、帧位置和实际帧数；累计帧边界按 fps 量化，短到不足一帧的画格会报错。

## 命令

```text
python scripts/shotlist.py init plan.json
python scripts/shotlist.py validate plan.json --strict
python scripts/shotlist.py render plan.json --format sheet
python scripts/shotlist.py validate plan.json --timed --check-images --images panels
python scripts/annotate.py plan.json --images panels --out annotated --sheet sheet.png
python scripts/board.py plan.json --images panels --out review-board.png --columns 2
python scripts/animatic.py plan.json --images annotated --out animatic.mp4 --require-images
python scripts/build_refpack.py plan.json --images panels --out refs --select S02-P03
```

`init` 创建待填写的草稿；提供总时长与镜数时，均分仅用于初始化。`render --format` 支持 sheet、storyboard、cuts、csv 等视图，其余格式见 `--help`。按当前编辑任务选择输出。

`board.py` 将实际图片按原顺序排成审阅宫格，等比留边而不裁掉内容；输出同名 JSON 保存原图、shot/panel、原图摘要与画布位置。格数不必填满行，不增加切点，不会自动标记内容通过。默认拒绝缺图或覆盖已有输出。它用于比较，干净原图继续用于生成。

`build_refpack.py` 保留参考序号、原镜头和画格映射；`--first-frame` 只接受序列真正的第一格。图片和视频的模型选择、参考绑定与输入转换由当前媒体执行工具处理，数据格式不含任何供应商必填字段。

`inventory.py` 统计语料与结构；`selftest.py --verbose` 执行离线回归。JSON 工具需要 Python 3.10+，标注和裁图需要 Pillow，动态分镜需要 FFmpeg，媒体回归另用 FFprobe。

## 箭头与兼容格式

画格可带 `overlays`，坐标为左上原点的归一化 `[x,y]`：

```json
{"type":"arrow", "from":[0.2,0.6], "to":[0.6,0.6], "label":"REACH"}
```

`arrow/sight` 使用 from/to，`impact/orbit` 使用 at；curve、size、radius、start、end 控制外观。生成参考图时保留干净版本。

旧 `action.primary/storyboard.panel` 自动转为一格，格 ID 等于镜头 ID，可使用 `render.image` 或 `<shot_id>.png`。旧 `beat_id` 继续接受，与 `beat_ids` 同时出现时须一致。机制编号等旧附加字段仍可读，出现时检查引用；它们不是新草稿的必填项。
