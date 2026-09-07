# 重庆交通态势可视化与交通流预测 🚗

基于高德地图 API 的**实时交通态势获取与可视化**工具，长期目标是从「路况抓取可视化」走向「交通流预测与智慧交通」完整链路。

> 用 Folium 生成交互式地图：🔴 红色 = 拥堵，🟠 橙色 = 缓行，🟢 绿色 = 畅通。

## 项目定位

- **短期（工程化）**：把一个能跑的单文件脚本，升级成规范的 Python CLI 工具包，支持矩形 / 圆形 / 道路名三种查询，生成带图例和统计面板的交互式地图。
- **长期（数据科学）**：从数据采集 → EDA → 特征工程 → ML / DL 预测 → 部署 → 监控仿真，打通一条完整的智慧交通数据科学链路。

> 详细的开发步骤见

## 当前进度

工程化改造已推进到 **Phase 2**：前两阶段（项目骨架 + 模块化 CLI）已完成，配置加载与数据持久化正在开发中。

## 功能

- 调用高德地图交通态势 API，获取指定区域实时路况
- 三种查询模式：矩形（`-r`）、圆形（`-c`）、道路名（`--road`）
- 用 Pandas 清洗解析道路数据（`RoadData` 数据模型）
- 用 Folium 生成交互式地图，含图例面板 + 统计面板
- 按日期自动归档地图文件，便于对比不同时段的路况变化
- API Key 支持命令行参数或环境变量，缺失时友好提示（不抛堆栈）

## 技术栈

Python · Requests · Pandas · Folium · PyYAML · 高德地图 API

## 安装

```bash
pip install -e .
```

## 使用方法

### 1. 设置 API Key

在高德开放平台申请 key：https://lbs.amap.com/

```bash
# Windows CMD
set AMAP_API_KEY=你的高德key

# Windows PowerShell
$env:AMAP_API_KEY='你的高德key'
```

也可以在运行时通过 `--key` 传入。

### 2. 运行

```bash
# 无参数：默认查询重庆渝中半岛
cq-traffic

# 矩形查询（左下,右上）
cq-traffic -r "106.4,29.4;106.7,29.6"

# 圆形查询（圆心 + 半径，单位千米，上限 5 千米）
cq-traffic -c "106.55,29.56" --radius 3

# 道路名查询（城市编码 + 道路名）
cq-traffic --road 中山四路 --adcode 500000

# 查看全部参数
cq-traffic --help
```

地图保存在 `traffic_maps/日期/` 目录下，用浏览器打开 `.html` 文件即可查看。

> 早期单文件版本保留在 `learn.practice.py`，向后兼容。

## 项目结构

```
├── src/cq_traffic/
│   ├── api.py          # 高德 API 客户端（三种查询模式）
│   ├── models.py       # RoadData 数据模型
│   ├── mapgen.py       # Folium 地图生成（图例 + 统计面板）
│   ├── cli.py          # argparse 命令行入口
│   ├── config.py       # 配置加载（Phase 2）
│   └── utils.py        # 日志、常量、工具函数
├── learn.practice.py   # 原始脚本（向后兼容）
├── tests/              # 单元测试（Phase 4）
├── pyproject.toml      # 项目元数据 + CLI 入口
├── config.yaml         # 运行时配置（Phase 2）
├── 开发说明书.md        # 详细开发路线（长期计划拆解）
└── traffic_maps/       # 输出的地图文件（不提交）
```

## 路线图

### 近期 · 工程化改造

| 阶段 | 目标 | 状态 |
|------|------|------|
| Phase 0 | 项目骨架：`pyproject.toml` + `src/` 布局 + `pip install -e .` | ✅ 完成 |
| Phase 1 | 模块化 + CLI + 图例/统计面板（utils/models/api/mapgen/cli） | ✅ 完成 |
| Phase 2 | 配置与数据持久化：`config.py` + `config.yaml` + 原始响应保存 + 多区域 | 🚧 进行中 |
| Phase 3 | 自动化与看板：定时采集 + 历史地图索引 + Streamlit 看板 | ⬜ 未开始 |
| Phase 4 | 测试与文档：pytest 覆盖 + README 完善 | ⬜ 未开始 |

### 长期 · 数据科学链路（2027–2029）

| 里程碑 | 内容 | 截止 |
|--------|------|------|
| 项目规范化 | Git、目录结构、README、环境变量 | 2027-01-15 |
| EDA + Streamlit | 数据清洗、时空分析、交互面板 | 2027-03-15 |
| 特征工程 | 时间 / 滞后 / 滚动 / 空间 / 天气特征 | 2027-07-01 |
| XGBoost 预测 | 基线模型、交叉验证、实验报告 | 2027-09-15 |
| LSTM 预测 | DataLoader、LSTM、ML vs DL 对比 | 2028-01-15 |
| Transformer | PatchTST / Informer、注意力可视化 | 2028-03-30 |
| 模型对比收尾 | 三方对比、技术文章 | 2028-07-01 |
| FastAPI + Docker | API 服务、阿里云、负载测试 | 2029-01-15 |
| 监控 + 仿真 | Prometheus、Grafana、SUMO | 2029-03-30 |

## License

MIT
