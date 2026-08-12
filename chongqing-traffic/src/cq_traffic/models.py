#数据模型：使用dataclasses定义高德返回的交通数据

from __future__ import annotations    #让python支持在类型注解中使用前向引用（forward references），即在类型注解中引用尚未定义的类或类型。这在定义递归数据结构或相互引用的类时非常有用。
from dataclasses import dataclass
from typing import Optional         #用来表示一个类型可以是某个类型或者是 None 的类型提示

from .utils import STATUS_COLORS, STATUS_LABELS      #   .xxx 是同级文件夹里找 xxx.py ,  ..yyy 是从上一级（父级）里找 yyy.py
                                                     #一、三两个库不太懂，以后可了解，似乎是规范性的东西，可记住。

@dataclass        #放在类的定义之前，作用于整个类，自动生成 __init__（初始化）、__repr__（字符串表示）、__eq__（相等性比较）等方法，简化类的定义。适用于主要用于存储数据的类。
class RoadData:
    '''道路数据的纯数据结构'''
    name: str
    status: str
    speed: Optional[float] = None     #可以是 None，表示没有速度数据，也可以是 float，表示有速度数据，当没有速度数据时，speed 字段的值默认为 None
    polyline: str
    direction: str = ''   #可选字段，默认为空字符串，表示没有方向信息。可以根据需要在实例化对象时传入具体的方向信息。
                    #属于面对对象编程的概念，类的属性和方法可以被实例化对象访问和使用。实例化对象是类的具体表现形式，通过类创建的对象可以拥有类定义的属性和方法，从而实现对数据的封装和操作。
                    #有点绕，好难啊[哭唧唧]
    @property       #作用于类方法，表示该方法可以像访问属性一样访问，而不需要加括号调用。即可以通过 road_data.status_color 访问，而不是 road_data.status_color()。
    def status_color(self) -> str:
        return STATUS_COLORS.get(self.status, 'gray')

    @property
    def status_label(self) -> str:
        return STATUS_LABELS.get(self.status, '未知')

    @property
    def first_point(self) -> tuple[float, float] | None:      # | 或的意思
        """解析 polyline 第一个坐标点，返回 (lng, lat)"""
        if not self.polyline or not self.polyline.strip():       #防御性编程，判断 polyline 是否为空或仅包含空白字符，如果是，则返回 None，表示没有有效的坐标点。
            return None                                            #.strip()可去除空白字符（tab、空格），将"     "转换为""，再判断是否为空字符串。它的两个兄弟是 lstrip() 和 rstrip()，分别用于去除字符串左侧和右侧的空白字符。
        first = self.polyline.split(";")[0]         #分割提取，可print一下传回来的数据，自行理解
        lng, lat = first.split(",")                  #注意区分 .strip() 和 .split() 的区别，前者是去除空白字符，后者是分割字符串
        return (float(lng), float(lat))

    



