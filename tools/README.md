# 仓库辅助工具

模型无关的分镜生产工具集中在 [shot-design/scripts](../shot-design/scripts/)，包括独立图片排审阅宫格，命令说明见 [数据与工具](../shot-design/references/shot-list-spec.md)。[NovelAI 可选适配](../integrations/novelai/README.md) 单独维护；这里仅保留研究和实验辅助脚本。

| 脚本 | 用途 |
|---|---|
| `build_release.py` | 只打包五个通用 skill、依赖说明和许可；生成可复现 ZIP、文件清单与 SHA256 |
| `run_storyboard_live_test.py` | 按保存的 manifest 顺序调用已有 NovelAI 客户端，记录结果；不自动重试 |
| `inspect_live_video.py` | 对现有视频提取元数据和带时间的检查帧；依赖 FFmpeg / FFprobe |
| `mineru_extract.py` | 将本地资料提交 MinerU，保存提取结果；使用本机 `.env` 中的配置 |
| `split_pdf.py` | 将本地 PDF 按页数拆分 |

从仓库根目录运行，参数见各脚本 `--help`。生成与提取需要已有账号配置；检查现有媒体和拆分 PDF 可在本地完成。原始资料与运行产物放在 Git 忽略的 `reference/`、`build/`、`artifacts/`。

一次性修改旧示例的脚本已移到 [research/archive/migrations](../research/archive/migrations/)，只保留为历史记录。
