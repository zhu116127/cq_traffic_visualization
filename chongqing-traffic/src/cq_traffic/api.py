# API 客户端
from .utils import get_logger
import requests as req
from .models import RoadData
from .utils import to_float



logger = get_logger(__name__)
BASE_URL = "https://restapi.amap.com/v3/traffic/status"



class AmapTrafficClient:
    '''交通态势查寻 API客户端'''
    
#---------------初始化----------------------
    def __init__(self, api_key: str, timeout: float = 10.0):
        if not api_key:
            raise ValueError("api_key 不能为空。")
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
            r.raise_for_status()
        except req.exceptions.Timeout:
            raise req.exceptions.Timeout("请求超时,请重试。")
        except req.exceptions.HTTPError as e:
            raise req.exceptions.HTTPError(f"网络请求失败：状态码 {e.response.status_code}")
        except Exception as e:
            logger.error(f"发现未知错误：{e} ")
            raise
        else:
            logger.info('成功获取！')

        return self._parse_roads(r.json())

#——————————————————————数据清洗过滤 并 创建ClassData对象——————————————————
    def _parse_roads(self, data: dict):
        if data.get('status') != '1':
            infocode = data.get('infocode')
            raise ValueError(f"高德业务报错：请前往高德开放平台 Web服务API 错误码说明里 查 {infocode} 哦。")  
            
        result: list[RoadData] = []
        for road in data['trafficinfo']['roads']:
            polyline = road.get('polyline')
            if not polyline or not polyline.strip():
                continue

            rd = RoadData(
                        name=road.get('name', ""),
                        status= str(road.get('status', "0")),
                        speed=to_float(road.get('speed')),
                        polyline=road.get('polyline'),
            )
                        
            result.append(rd)

        
        return result
            






    






            






    


