# 重庆交通态势可视化 🚗

基于高德地图 API 的**实时交通态势**获取与可视化工具，使用 Folium 生成交互式地图。

## 功能

- 调用 [高德地图交通态势 API](https://restapi.amap.com/v3/traffic/status/rectangle) 获取矩形区域内实时路况
- 用 **Pandas** 清洗和解析道路数据
- 用 **Folium** 生成交互式交通地图（红色=拥堵、橙色=缓行、绿色=畅通）
- 按时段自动归档，方便对比不同时段的路况变化

## 依赖

```bash
pip install requests pandas folium
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

### 2. 运行脚本

```bash
python learn.practice.py
```

地图会保存在 `traffic_maps/日期/` 目录下，用浏览器打开 `.html` 文件即可查看。

## 示例区域

默认查询**重庆渝中半岛** (`106.565,29.549` ~ `106.588,29.568`)，可在代码中修改 `rectangle` 参数为目标区域。

## 项目结构

```
├── learn.practice.py   # 主程序
├── .gitignore          # 忽略规则
├── README.md           # 本文件
└── traffic_maps/       # 输出的地图文件（不提交）
```

## License

MIT
