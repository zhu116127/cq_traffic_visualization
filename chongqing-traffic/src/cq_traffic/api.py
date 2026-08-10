#src/cq_traffic/api.py
import requests as req
def fetch_traffic_api (key="你的key",rectangle="你要查询的矩形区域"):
    url = 'https://restapi.amap.com/v3/traffic/status/rectangle'
    params = {
        'key':key,
        'level':'5',
        'rectangle':rectangle,
        'extensions':'all'
    }
    r = req.get(url, params=params)
    Data_traffic = r.json()
    roads = Data_traffic['trafficinfo']['roads']
    print(f"获取到了 {len(roads)} 条道路。")
    return roads