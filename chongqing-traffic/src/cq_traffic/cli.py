from .utils import setup_logging
import argparse
import sys
import logging
import os
from .api import AmapTrafficClient
import requests
from .mapgen import generate_traffic_map


def build_parser():
    parser = argparse.ArgumentParser(description="CQ Traffic CLI")

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("-r", "--rectangle", help="矩形 'lng1,lat1;lng2,lat2'，左下右上")
    mode.add_argument("-c", "--circle", help="圆心 'lng,lat'")
    mode.add_argument("--road", help="道路名称")
    parser.add_argument("--radius",help="圆形半径,单位:千米,最大值小于5千米,只配给--circle参数使用")
    parser.add_argument("--adcode",type=str, default="500000", help="城市编码，重庆=500000" )
    parser.add_argument("--center", default="29.56,106.55", help="中心点 'lat,lng'")
    parser.add_argument("--zoom", type=int, default=13, help="地图缩放级别,默认13")
    parser.add_argument("--key", type=str, default=None, help="高德地图API Key,默认值为None,请通过环境变量AMAP_API_KEY传入")
    parser.add_argument("--output", type=str, default="traffic_maps", help="输出文件名,默认 traffic_maps")  
    parser.add_argument("--verbose", action="store_true", help="显示详细日志信息,默认值为False,不显示详细日志信息")  


    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    setup_logging(level=logging.DEBUG if args.verbose else logging.INFO)
    api_key = args.key or os.environ.get("AMAP_API_KEY")
    if not api_key:
        logging.error("请提供高德地图API Key,可通过--key参数或环境变量AMAP_API_KEY传入")
        sys.exit("错误")

    client = AmapTrafficClient(api_key)

    try:
        if args.rectangle:
            roads = client.query_rectangle(args.rectangle)
        elif args.circle:
            roads = client.query_circle(args.circle, args.radius)
        elif args.road:
            roads = client.query_road(args.adcode, args.road)
        else:
            roads = client.query_rectangle("106.4,29.4;106.7,29.6")  # 默认重庆市中心区域
            
    except (requests.exceptions.RequestException,ValueError) as e:
        logging.error(f"请求失败: {e}")
        sys.exit("错误")
    
    if not roads:                               # 空数据兜底
        logging.warning("未获取到任何道路数据，请检查坐标或稍后重试。")
    
        return 1

    path = generate_traffic_map(roads,args.center,args.zoom,args.output)
    logging.info(f"地图已生成: {path}")
    return 0 



if __name__ == "__main__":
    sys.exit(main())