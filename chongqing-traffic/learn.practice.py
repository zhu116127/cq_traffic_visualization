import requests as req
import pandas as pd
import os
import folium
from datetime import datetime
from datetime import date

def fetch_traffic(key,rectangle):
    url = 'https://restapi.amap.com/v3/traffic/status/rectangle'
    params = {
        'key':key,
        'level':'5',
        'rectangle':rectangle,
        'extensions':'all'
    }

    r = req.get(url, params=params)             
    data_traffic = r.json()                      
    print(data_traffic)                          
    roads = data_traffic['trafficinfo']['roads']      
    print(f"获取到了 {len(roads)} 条道路。")

    data_list = []
    for road in roads:
        data_list.append({
            'name':road['name'],
            'status': road['status'],
            'speed': road.get('speed'),
            'polyline':road['polyline']
        }
        )

    df = pd.DataFrame(data_list)                         
    df = df[df['polyline'].notna() & (df['polyline'].str.strip() != '')].copy()
    print(f'过滤后剩余的道路数: {len(df)}。')
    if len(df) == 0:
        print("数据异常，请重新获取。")
    else:
        df['first_point'] = df['polyline'].str.split(';').str[0]
        df['lng'] = df['first_point'].str.split(',').str[0].astype(float)
        df['lat'] = df['first_point'].str.split(',').str[1].astype(float)
    print(df[['name','lng','lat','status']].head())

    m = folium.Map(location=[29.56, 106.55], zoom_start=13)

    def get_color(status):
        if status == '3':
            return 'red'
        elif status == '2':
            return 'orange'
        elif status == '1':
            return 'green'
        else:
            return 'gray'

    for _, row in df.iterrows():
        try:
            points = []
            for coord in row['polyline'].split(';'):
                lng, lat = coord.split(',')
                points.append([float(lat), float(lng)])

            folium.PolyLine(
                locations=points,
                color=get_color(row['status']),
                weight=4,
                opacity=0.8,
                popup=f"{row['name']} | 状态:{row['status']}"
            ).add_to(m)
        except Exception as e:
            print(f'错误: {e}')

    # m.save('chongqing_traffic_latest.html')  覆盖原文件

    today = f"{date.today().year}{date.today().month:02d}{date.today().day:02d}"
    folder = f"traffic_maps/{today}"
    os.makedirs(folder, exist_ok=True)

    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"{folder}/traffic_{timestamp}.html"
    m.save(filename)
    print(f'地图已保存: {filename},共处理 {len(df)} 条道路。')





    


if __name__ == '__main__':
    API_KEY = os.environ.get('AMAP_API_KEY')
    if not API_KEY:
        print("错误：请设置环境变量 AMAP_API_KEY")
        print("  Windows CMD: set AMAP_API_KEY=你的key")
        print("  Windows PowerShell: $env:AMAP_API_KEY='你的key'")
        exit(1)

    fetch_traffic(
        key=API_KEY,
        rectangle='106.56516,29.549718;106.588001,29.568082'
    )

#'106.56516,29.549718;106.588001,29.568082' 渝中半岛的坐标
