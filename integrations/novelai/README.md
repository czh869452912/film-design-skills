# NovelAI 可选适配

这里保留原先的出场槽、宫格提示编译与实测裁图工具，仅在使用者选择 NovelAI 时使用。不随五个通用 skill 安装，也不决定导演、分镜或原画的默认流程。

在仓库根目录运行：

```text
python integrations/novelai/pageboard.py compile page.json --sequence plan.json --out page-input
python integrations/novelai/pageboard.py crop review.json --layout page-input/layout.json --out clean-panels
python integrations/novelai/selftest.py
```

输入与限制见 [reference.md](reference.md)。适配器读取仓库的 `shot-design/scripts/sequence.py`，本身不发网络请求或读取密钥。它编译已有页计划，不提供姿态控制，也不保证接触、格数或画面表达成功。

2026-10-25 的旧实验中，身份／画风相对稳定，但动作、空间与格数多次失败；见 [v0.7 记录](../../research/live-v0.7/report.md)。通用流程改用每镜 layout 与关键原画，宫格仍可由独立图片排版。
