# API 客户端
from .utils import get_logger
import requests as req
from .models import RoadData
from .utils import to_float



logger = get_logger(__name__)               #之前在utils里写的，不要再写import logging 了。
BASE_URL = "https://restapi.amap.com/v3/traffic/status"          #从这里开始，到下面_get()函数结束，运用了很绝的拆分组装方法。
                                                                 #第一个拆分，是三个查询模式的 url ，因为他们有很长一节是重复的，只有最后一个单词的不同。
                                                                 #第二个拆分，是参数 params 的拆分，直接将重复的一部分参数（key 和 extensions）写入params = {……}里，其他各不相同的参数用_get()传参，再用**params方法写入。
                                                                 #关于 ** 这两个星星是 字典解包 里的知识点，**字典名，就是把这个字典拆开的意思，相关知识点还有 *arg 、 **kwargs，我感觉不难，但自己暂时还用不上，等遇到了再说吧。
                                                                 #第三个拆分，是最核心的，把三个查询模式的必经之路 request 请求、解析拆出来，统一req.get(),最后还r.json()统一解析。
class AmapTrafficClient:
    '''交通态势查寻 API客户端'''
    
#---------------初始化----------------------
    def __init__(self, api_key: str, timeout: float = 10.0):
        if not api_key:
            raise ValueError("api_key 不能为空。")                 #raise 是异常处理里面的内容，可见github上的开源教程（学python的利器）：https://walter201230.github.io/Python/PythonBasis/python19/1/  ，另外要注意理解“接”异常和“抛”异常两个概念
        self.api_key = api_key                                    
        self.timeout = timeout

        
#-------------三种查询模式-------------------------------
    def query_rectangle(self, rectangle: str, level: int =5) -> list[RoadData]:
        '''矩形区域查询。rectangle 形如 "lng1,lat1;lng2,lat2", 坐标点分别为左下右上，在高德免费调取额度中，对角线不超过10公里'''
        return self._get("/rectangle", {"rectangle": rectangle, "level": level})

    def query_circle(self, location: str, radius: str, level: int =5) -> list[RoadData]:
        '''圆形区域查询。location为圆心坐标，radius小于5公里，单位为米'''
        return self._get("/circle", {"location": location, "radius": radius, "level": level})

    def query_road(self, adcode: str, name: str, level: int =5) -> list[RoadData]:
        '''道路名查询。adcode为城市编码（如重庆市 500000）。'''
        return self._get("/road", {"adcode": adcode, "name": name, "level": level})


#-------------完成收束，统一发出请求，并解析-----------------
    def _get(self, path: str, params: dict):
        '''拼接组装所有所需要的参数'''
        url = BASE_URL + path
        params = {"key": self.api_key, "extensions": "all", **params}
        try:
            r = req.get(url, params=params, timeout=self.timeout)
            r.raise_for_status()                             # request库里的异常处理，如果 HTTP 请求返回了不成功的状态码， Response.raise_for_status() 会抛出一个 HTTPError 异常
        except req.exceptions.Timeout:                       #若请求超时，则抛出一个 Timeout 异常，总感觉和上面的功能重了。
            raise req.exceptions.Timeout("请求超时,请重试。")
        except req.exceptions.HTTPError as e:
            raise req.exceptions.HTTPError(f"网络请求失败：状态码 {e.response.status_code}")
        except Exception as e:                               #Exception是绝大部分异常的的祖宗，放最后垫底，万能兜底。
            logger.error(f"发现未知错误：{e} ")               #logger 日志相关utils里有介绍，另外，上面教程链接里也都有，略过了。
            raise
        else:
            logger.info('成功获取！')

        return self._parse_roads(r.json())                 # ٩(๑´0`๑)۶ 神之一手，把_parse_roads()和_get()联系起来，再一起交给query_xxx(), 彻底打通整个链路。

#——————————————————————数据清洗过滤 并 创建ClassData对象——————————————————
    def _parse_roads(self, data: dict):
        if data.get('status') != '1':
            infocode = data.get('infocode')
            raise ValueError(f"高德业务报错：请前往高德开放平台 Web服务API 错误码说明里 查 {infocode} 哦。")  
            
        result: list[RoadData] = []                            # 类型注解里的内容，一会儿看看。
        for road in data['trafficinfo']['roads']:
            polyline = road.get('polyline')                    #下面一行，我原来写成了road.polyline.strip(),错了。
            if not polyline or not polyline.strip():           #注意road 是高德给的字典 → 用 road.get('polyline')；rd 是 RoadData 实例 → 才能用 rd.polyline。
                continue

            rd = RoadData(
                        name=road.get('name', ""),
                        status= str(road.get('status', "0")),
                        speed=to_float(road.get('speed')),           #数据类型的转换，to_float是我存在utils里的之自定义函数，一个小工具
                        polyline=road.get('polyline'),
            )
                        
            result.append(rd)            #@dataclass是装饰器，自动给 RoadData 生成了 __init__ 等方法；rd = RoadData(...) 就是调用它造出的一个实例。
                                         #DataFrame（pandas） 、 dataclass 、 pydantic都是处理数据的工具，pydantic 后续会用到，以后再说。
        
        return result






    






            






    


