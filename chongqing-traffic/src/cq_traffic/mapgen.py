import folium
import os
from .utils import get_logger
from datetime import datetime,date

#右边依旧为学习注解

logger = get_logger(__name__)

def generate_traffic_map(road_data, center, zoom, out_dir, show_legend=True, show_stats=True):            #show_legend和show_stats ，默认传True ，不想用就传 False
    '''绘制可视化交互地图'''
    lat, lng = (float(x) for x in center.split(","))
    m = folium.Map(location=[lat, lng], zoom_start=zoom)
    for road in road_data:                               #road_data 是list[RoadData]，road 是 RoadData 实例 → 用 road.xxx（属性）；而 api.py 里 road 是高德返回的 dict → 用 road.get('xxx')。
        points = [(a_lat, a_lng) for a_lng, a_lat in road.all_points]                 #这里有两个不同的变量  lat 和 lng
        # a + _ 用以区分中心坐标，和划线坐标
        folium.PolyLine(
            locations=points,
            color=road.status_color,
            popup=f"{road.name}",                        #点进去，标在里面的那个
            tooltip=road.status_label,                   #标在外面的那个
            weight=4,
            opacity=0.8,                                 #不透明度， opacity=0.8 表示这条路 80% 不透明（也就是 20% 透明，能隐约看到底下的地图）
        ).add_to(m)


    #图例功能                                             #下面的这两大串代码，是html（超文本记录语言，用来创建网页的） 和 css （层叠样式表， 其实就是让HTML网页变好看的）相关知识点，都属于前端的内容，从这里，我们第一次跨技术栈做业。
    if show_legend:                                      #这些代码，等一段时间，要去找资源学习一下，理解即可。
        legend_html = '''
        <div style="
            position: fixed;
            bottom: 50px;
            left: 50px;
            width: 150px;
            height: auto;
            border: 2px solid grey;
            z-index: 9999;
            font-size: 14px;
            background-color: white;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
            ">
            <b>道路状态图例</b><br>
            <i style="background: green; width: 12px; height: 12px; display: inline-block;"></i>畅通<br>
            <i style="background: orange; width: 12px; height: 12px; display: inline-block;"></i>缓行<br>
            <i style="background: red; width: 12px; height: 12px; display: inline-block;"></i>拥堵<br>
            <i style="background: darkred; width: 12px; height: 12px; display: inline-block;"></i>严重拥堵<br>
            <i style="background: gray; width: 12px; height: 12px; display: inline-block;"></i>未知状态<br>
        </div> 
        '''
        m.get_root().html.add_child(folium.Element(legend_html))              #标记1


    #统计每种状态的数量， 完成统计面板功能
    stats = {"畅通": 0, "缓行": 0, "拥堵": 0,"严重拥堵": 0,"未知": 0}

    for road in road_data:                                                    #一段计数小代码
        label = road.status_label
        if label in stats:
            stats[label] += 1
        

    if show_stats:
        stats_html = f'''
        <div style="
            position: fixed;
            top: 50px;
            right: 50px;
            width: fit-content;
            padding: 10px;
            border: 2px solid grey;
            background: white;
            z-index: 9999;
            border-radius: 5px;
            font-size: 14px;
            ">
            <b>道路统计</b><br>
            畅通：{stats['畅通']} 条<br>
            缓行：{stats['缓行']} 条<br>
            拥堵：{stats['拥堵']} 条<br>
            严重拥堵：{stats['严重拥堵']} 条<br>
            未知：{stats['未知']} 条
        </div>
        '''
        m.get_root().html.add_child(folium.Element(stats_html))                                               #拆解一下： m 是地图对象 ； .get_root（）大概就是取得编辑地图的最高权限的意思吧 ； .html 要添加内容的格式（这里不太明白）； add_child()是folium的一个函数， 用于在地图上添加一个子元素 ； folium.Element() 把括号里的东西变成folium认可的元素。

                                                                                                             #python内置库 datatime， 也不知道要不要去找文档学一学
    today = f"{date.today().year}{date.today().month:02d}{date.today().day:02d}"                             #关于时间戳所有内容，好像是一个模板可以拿到utils里去，标记5
    folder = os.path.join(out_dir, today)                                                                    #用来拼接 folder的， 这个方法可以自动匹配操作系统的斜杠符号。
    os.makedirs(folder, exist_ok=True)                                                                       # os 库，不理解是什么，好像是来处理文件路径的， 这一步是防御性编程，但我不太清楚里面每一个部分时怎么来的。

    timestamp = datetime.now().strftime("%H%M%S")                                                            #strftime是"格式化成字符串"，strptime 是"从字符串解析回时间"，一对兄弟，方向相反。其它都用的时候查。
    filename = f"{folder}/traffic_{timestamp}.html"                                                          #最后格式的拼接
    
    
    m.save(filename)
    logger.info(f'地图已保存: {filename},共处理 {len(road_data)} 条道路。')                                    #logger日志代替print（）

    return filename

