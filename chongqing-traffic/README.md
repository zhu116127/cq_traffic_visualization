# 重庆交通态势可视化 🚗

基于高德地图 API 的**实时交通态势**获取与可视化工具，使用 Folium 生成交互式地图。

> 🚧 项目正在持续开发中，CLI 命令行工具即将上线。

## 功能

- 调用高德地图交通态势 API 获取矩形区域内实时路况
- 用 Pandas 清洗和解析道路数据
- 用 Folium 生成交互式交通地图（红色=拥堵、橙色=缓行、绿色=畅通）
- 按时段自动归档，方便对比不同时段的路况变化

## 技术栈

Python · Requests · Pandas · Folium · 高德地图 API

## 依赖

```bash
pip install requests pandas folium pyyaml
```

或可编辑安装：

```bash
pip install -e .
```

## 使用方法

### 1. 设置 API Key

```bash
# Windows CMD
set AMAP_API_KEY=你的高德key

# Windows PowerShell
$env:AMAP_API_KEY='你的高德key'
```

> 在高德开放平台申请：https://lbs.amap.com/

### 2. 运行

```bash
# 当前版本（单文件脚本）
python learn.practice.py

# 模块化 CLI 版本（开发中，即将上线）
cq-traffic
```

地图保存在 `traffic_maps/日期/` 目录下，用浏览器打开 `.html` 文件即可查看。

## 示例区域

默认查询**重庆渝中半岛** (`106.565,29.549` ~ `106.588,29.568`)。

## 项目结构

```
├── src/cq_traffic/     # 模块化源码（开发中）
│   ├── api.py          # 高德 API 客户端
│   ├── models.py       # 数据模型
│   ├── mapgen.py       # 地图生成
│   ├── cli.py          # 命令行入口
│   ├── config.py       # 配置加载
│   └── utils.py        # 日志与工具函数
├── learn.practice.py   # 原始脚本（可运行）
├── tests/              # 单元测试
├── pyproject.toml      # 项目元数据
├── config.yaml         # 运行时配置
└── traffic_maps/       # 输出的地图文件（不提交）
```

## License

MIT
