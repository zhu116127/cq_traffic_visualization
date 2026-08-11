#工具函数：日志、常量、状态映射。
#左侧注释为原代码注释，右侧注释为我对代码的理解和解释，供学习参考。



from __future__ import annotations    #让python支持在类型注解中使用前向引用（forward references），即在类型注解中引用尚未定义的类或类型。这在定义递归数据结构或相互引用的类时非常有用。

import logging                        #日志记录器
import sys                            #与python解释器及其环境进行交互的模块
from pathlib import Path              #面向对象的文件系统路径操作模块，好用多用。
from typing import Optional           #用来表示一个类型可以是某个类型或者是 None 的类型提示S

# ---------------------------------------------------------------------------
# 状态码 → 颜色 / 中文标签映射
# ---------------------------------------------------------------------------
# 高德地图交通态势 API 返回的道路状态码：
#   0 — 未知
#   1 — 畅通
#   2 — 缓行
#   3 — 拥堵
#   4 — 严重拥堵

STATUS_COLORS: dict[str, str] = {
    "0": "gray",
    "1": "green",
    "2": "orange",
    "3": "red",
    "4": "darkred",
}

STATUS_LABELS: dict[str, str] = {
    "0": "未知",
    "1": "畅通",
    "2": "缓行",
    "3": "拥堵",
    "4": "严重拥堵",
}


def get_color(status: str) -> str:           #括号里是参数和类型注解，箭头后是返回值类型注解
                                              #文档注释（Docstring），具体格式见小白学python教程
    """根据高德道路状态码返回对应颜色。         

    Args:
        status: 道路状态码字符串（"0"~"4"）

    Returns:
        HTML 颜色名（如 "green", "red"）
    """
    return STATUS_COLORS.get(status, "gray")     #.get() 方法用于从字典中获取指定键的值，如果键不存在，则返回默认值 "gray"。
                                                 #[]取值，若没有则报错，get()取值，若没有则返回None或指定的默认值

def get_status_label(status: str) -> str:
    """根据高德道路状态码返回中文标签。

    Args:
        status: 道路状态码字符串（"0"~"4"）

    Returns:
        中文状态描述（如 "畅通", "拥堵"）
    """
    return STATUS_LABELS.get(status, "未知")


# ---------------------------------------------------------------------------
#日志配置
# ---------------------------------------------------------------------------
                                                #注释规范
def setup_logging(                              #basicConfig()函数用于配置日志系统的基本设置，包括日志级别、日志格式、输出位置等。它是logging模块中最常用的配置方法之一，适用于简单的日志记录需求。
    level: int = logging.INFO,                  #这里是basicConfig（）的进阶版
    log_file: Optional[str | Path] = None,      #可选的日志文件路径，选字符串（也就是文件）或选Path对象（pathlib.Path），默认值为None，表示不写入日志文件。
) -> None:
    """配置根 Logger（仅在 CLI 入口调用一次）。

    日志可以输出到终端（stderr）或可选的日志文件。该函数设计幂等。
    重复调用时若根 Logger 已有 handler 则跳过，避免重复输出。
m
    Args:
        level:  日志级别，默认 INFO。调试时传 logging.DEBUG。
        log_file: 可选的文件路径，日志将追加写入该文件。
    """
    root = logging.getLogger()

    # 幂等保护：如果已经配置过 handler，不再重复添加
    if root.handlers:                            #如果根 Logger 已经有 handler，则说明已经配置过日志，直接返回，避免重复输出。
        return

    root.setLevel(level)                         #水闸

    # 终端 handler（stderr，避免和正常的 stdout 输出混在一起）
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)              #水龙头，水闸和水龙头同时打开，才会输出日志。
    console_fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler.setFormatter(console_fmt)
    root.addHandler(console_handler)

    # 可选的文件 handler
    if log_file is not None:
        file_handler = logging.FileHandler(
            str(log_file), mode="a", encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_fmt = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        file_handler.setFormatter(file_fmt)
        root.addHandler(file_handler)
                                                ##似乎有一个什么Propagate的东西，暂时不管它，先用这个吧。

def get_logger(name: str) -> logging.Logger:
    """获取指定名称的 Logger。

    各模块在顶部调用：
        logger = get_logger(__name__)

    Args:
        name: Logger 名称（通常传 __name__）

    Returns:
        配置好的 Logger 实例。
    """
    return logging.getLogger(name)
