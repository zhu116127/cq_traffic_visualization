# 重庆交通态势可视化 — 项目升级计划

## Context

当前 `chongqing-traffic/` 是一个单文件 Python 脚本（~103 行），功能是调用高德地图 API 获取矩形区域交通态势，用 Folium 生成交互式地图。代码能正常工作，但存在以下问题：

- **单文件单体**：所有逻辑混在一个函数里，难以维护和扩展
- **功能单一**：仅支持矩形查询，高德 API 还支持圆形、道路名查询
- **无 CLI**：坐标硬编码在 `main()` 中，每次换区域要改代码
- **用 print() 代替日志**：无法控制输出级别
- **无类型标注**：代码可读性和 IDE 提示不足
- **错误处理不完整**：无 HTTP 状态码检查、无超时、无重试
- **无测试**：改动代码无法验证是否破坏现有功能
- **地图功能基础**：无图例、无统计面板

本计划将项目从一个"能跑的脚本"升级为"规范的 Python 工具包"，分 4 个阶段逐步实施，每个阶段结束后都可独立交付。

---

## Phase 0: 项目骨架搭建（预计 1-2 小时）

### 目标
建立标准的 Python 项目结构，不修改业务逻辑。

### 新目录结构
```
chongqing-traffic/
├── .gitignore
├── README.md
├── UPGRADE_PLAN.md              # 本文件
├── pyproject.toml              # 依赖声明 + CLI 入口
#【一个包装盒，上面写着名字、版本、需要的零件，以及一个开始按钮CLI入口】
├── config.yaml                 # 运行时配置
├── src/                        ##项目主模块，放置所有业务逻辑代码
│   └── cq_traffic/
│       ├── __init__.py
│       ├── api.py              # 高德 API 客户端
│       ├── models.py           # 数据模型 (dataclass)
│       ├── mapgen.py           # Folium 地图生成
│       ├── cli.py              # argparse 命令行入口
│       ├── config.py           # 配置文件加载
│       └── utils.py            # 日志、常量、工具函数
├── tests/                      ##用于存放单元测试和集成测试，确保修改代码后文件安全
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_models.py
│   └── test_mapgen.py
├── scripts/                   ##存放辅助脚本
│   └── schedule_collect.py     # Phase 3: 定时采集
└── web_dashboard/              ##未来数据看板
    └── app.py                  # Phase 3: Streamlit 看板
```

### 操作步骤
1. 创建 `pyproject.toml`（setuptools 后端，依赖：requests, pandas, folium, pyyaml）
2. 创建 `src/cq_traffic/` 包目录及 `__init__.py`
3. 更新 `.gitignore`（增加 `data/`, `*.log`, `config.local.yaml`）
4. `pip install -e .` 可编辑安装

### 技术选型
| 项目 | 选择 | 理由 |
|------|------|------|
| 构建系统 | setuptools + pyproject.toml | 标准方式，不引入 Poetry 学习成本 |
| 项目布局 | `src/` 布局 | 防止开发时意外导入包本身 |

---

## Phase 1: 模块化与代码质量（预计 3-5 小时）

### 目标
将单体脚本拆分为独立模块，添加日志、类型标注、错误处理。生成的 Folium 地图效果与原版一致。

### 1a. `utils.py` — 日志与常量
- 提取状态码→颜色映射（`get_color()`）
- 添加状态码→中文标签映射（拥堵/缓行/畅通）
- 用 `logging` 模块替代 `print()`

### 1b. `models.py` — 数据模型
- `Road` dataclass：name, status, speed, polyline, direction
- 属性方法：`status_color`, `status_label`, `first_point`

### 1c. `api.py` — API 客户端
- `AmapTrafficClient` 类，封装三种查询模式：
  - `query_rectangle(rectangle, level)` — 矩形查询
  - `query_circle(location, radius, level)` — 圆形查询（新增）
  - `query_road(name, city)` — 道路名查询（新增）
- 错误处理增强：`raise_for_status()`、API 业务错误检查、超时设置
- `_parse_roads()` 统一解析道路数据，过滤空 polyline

### 1d. `mapgen.py` — 地图生成
- `generate_traffic_map(roads, center, zoom, output_dir)` — 纯函数
- **新增功能**：
  - 图例面板（左下角浮动 HTML）
  - 统计面板（右上角，显示各状态道路数量）
  - 可通过参数开关

### 1e. `cli.py` — 命令行接口
- 使用 `argparse`（标准库，零依赖）
- 支持三种查询模式互斥选择
- 支持 `-k` 传入 API Key，或从环境变量读取
- 支持 `--center`, `--zoom`, `-o` 输出目录, `-v` 详细日志

### 验收标准
- `pip install -e .` 成功
- `cq-traffic`（无参数）效果等同原 `learn.practice.py`
- `cq-traffic -r "...", -c "...", --road "..."` 三种模式正常工作
- 地图包含图例和统计面板
- API Key 缺失时显示友好提示而非堆栈跟踪

---

## Phase 2: 配置与数据持久化（预计 2-3 小时）

### 目标
将硬编码设置移到配置文件，支持多区域快速切换，保存原始 API 响应。

### 2a. `config.yaml` — 运行时配置
```yaml
defaults:
  rectangle: "106.56516,29.549718;106.588001,29.568082"
  center: "29.56,106.55"
  zoom: 13

output:
  dir: traffic_maps
  save_raw_response: true
  raw_data_dir: data/raw

areas:
  yuzhong:    # 渝中半岛
    type: rectangle
    value: "106.56516,29.549718;106.588001,29.568082"
  nanan:      # 南岸区（示例）
    type: rectangle
    value: "106.550,29.520;106.580,29.540"
```

### 2b. `config.py` — 配置加载器
- 支持 `${ENV_VAR}` 环境变量替换
- 搜索路径：`./config.yaml` → `~/.cq-traffic/config.yaml`
- 配置文件缺失时回退到默认值

### 2c. 原始响应持久化
- 在 `api.py` 中增加 `_save_raw_response()` 方法
- 保存到 `data/raw/query-type_YYYYMMDD_HHMMSS.json`

### 2d. 多区域查询
- `cq-traffic --area yuzhong` 从配置文件读取预设区域
- `cq-traffic --area all` 遍历所有区域生成多张地图

### 验收标准
- 配置文件可正常加载，命名区域可用
- 原始 JSON 响应保存到 `data/raw/`
- 配置文件缺失时不崩溃

---

## Phase 3: 自动化与看板（预计 3-5 小时）

### 目标
支持定时自动采集数据，提供历史数据浏览方式。

### 3a. `scripts/schedule_collect.py` — 定时采集
- `--interval N` 每 N 分钟采集一次
- `--area all` 采集所有配置区域
- `--max-runs N` 限制最大采集次数
- `time.sleep` 循环（简单直观，不用学 cron/APScheduler）
- Ctrl+C 优雅退出

### 3b. 历史地图索引页
- `traffic_maps/index.html`：按日期列出所有地图文件
- 纯 HTML 生成，无需服务器

### 3c. Streamlit 看板（进阶可选）
- `web_dashboard/app.py`
- 区域选择下拉框 + "获取实时数据"按钮
- 内嵌 Folium 地图展示
- 依赖：`pip install cq-traffic[web]`

### 验收标准
- 定时采集脚本正常运行，Ctrl+C 可优雅退出
- `index.html` 可浏览历史地图
- （进阶）Streamlit 看板可交互

---

## Phase 4: 测试与文档（预计 2-4 小时）

### 目标
添加测试覆盖，完善 README，让项目达到"可贡献"标准。

### 4a. 测试套件
- `tests/test_models.py`：Road dataclass 属性测试
- `tests/test_api.py`：用 `responses` 库 mock HTTP，测试三种查询 + 错误路径
- `tests/test_mapgen.py`：测试地图文件生成（用 `tmp_path` fixture）
- 目标：核心模块 80%+ 覆盖率

### 4b. README 更新
- 快速开始（clone → install → run 三步）
- 三种查询模式的 CLI 示例
- 配置文件说明表格
- 开发指南（可编辑安装 + pytest）
- 更新日志

### 4c. 开发者工具
- `pyproject.toml` 添加 `[tool.pytest.ini_options]`
- 可选：`[tool.ruff]` 代码检查配置

### 验收标准
- `pytest` 全部通过
- `cq-traffic --help` 显示完整帮助

---

## 阶段总览

```
Phase 0 (1-2h)  → 项目骨架，pip install -e . 可用
Phase 1 (3-5h)  → 模块化 + CLI + 图例统计面板
Phase 2 (2-3h)  → 配置文件 + 多区域 + 原始数据保存
Phase 3 (3-5h)  → 定时采集 + 历史浏览 + Streamlit 看板
Phase 4 (2-4h)  → 测试 + 文档完善
```

## 注意事项

1. **高德 API 限流**：免费版有 QPS 限制，多区域查询时需 `time.sleep(1)` 间隔
2. **Polyline 点数过多**：部分道路有数百个坐标点，大区域地图可能在浏览器中变慢
3. **Windows 兼容**：所有路径使用 `pathlib.Path`，确保跨平台
4. **Python 版本**：要求 `>=3.9`（dataclass + `list[Road]` 类型语法）

## 关键文件

| 文件 | 操作 | 说明 |
|------|------|------|
| `chongqing-traffic/pyproject.toml` | 新建 | 项目元数据与依赖 |
| `chongqing-traffic/src/cq_traffic/__init__.py` | 新建 | 包初始化 |
| `chongqing-traffic/src/cq_traffic/api.py` | 新建 | API 客户端（核心逻辑） |
| `chongqing-traffic/src/cq_traffic/models.py` | 新建 | Road dataclass |
| `chongqing-traffic/src/cq_traffic/mapgen.py` | 新建 | 地图生成（新增图例/统计） |
| `chongqing-traffic/src/cq_traffic/cli.py` | 新建 | 命令行入口 |
| `chongqing-traffic/src/cq_traffic/utils.py` | 新建 | 日志与常量 |
| `chongqing-traffic/src/cq_traffic/config.py` | 新建 | 配置加载 |
| `chongqing-traffic/config.yaml` | 新建 | 默认配置文件 |
| `chongqing-traffic/learn.practice.py` | 保留 | 原始脚本（向后兼容） |
| `chongqing-traffic/.gitignore` | 修改 | 增加忽略项 |
| `chongqing-traffic/README.md` | 修改 | Phase 4 更新 |

## 验证方式

1. **Phase 0**：`pip install -e .` 无报错，`python learn.practice.py` 仍可运行
2. **Phase 1**：`cq-traffic` 默认模式生成的地图与原版一致；`-r/-c/--road` 三种模式正常
3. **Phase 2**：`cq-traffic --area yuzhong` 正常工作；`data/raw/` 下有 JSON 文件
4. **Phase 3**：`python scripts/schedule_collect.py --interval 1 --max-runs 2` 正常运行后退出
5. **Phase 4**：`pytest` 全部通过；README 对新用户友好
