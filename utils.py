#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
航班查询系统工具模块
"""

import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from map_config import get_available_services, create_tile_layer, add_all_map_layers, add_fallback_layers
from cdn_replacer import optimize_html_for_china
from app_resource_manager import create_optimized_map_html_app

# 加载机场坐标数据
def load_airport_coords():
    coords_file = Path(__file__).parent / 'data' / 'airport_coords.json'
    if coords_file.exists():
        with open(coords_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# 机场坐标数据
airport_coords = load_airport_coords()

# 地图缓存
_map_cache = {}
_base_map_templates = {}
_global_map_instances = {}  # 全局地图实例缓存  # 基础地图模板缓存

def clear_map_cache():
    """清理地图缓存"""
    global _map_cache, _base_map_templates, _global_map_instances
    _map_cache.clear()
    _base_map_templates.clear()
    _global_map_instances.clear()
    print("🗑️ 地图缓存已清理")

def force_clear_all_caches():
    """强制清理所有缓存（包括标签页缓存）"""
    clear_map_cache()
    clear_tab_map_cache()
    print("🗑️ 所有地图缓存已强制清理")

def get_cache_stats():
    """获取缓存统计信息"""
    return {
        'map_cache_size': len(_map_cache),
        'template_cache_size': len(_base_map_templates),
        'global_instances_size': len(_global_map_instances),
        'cached_maps': list(_map_cache.keys()),
        'cached_templates': list(_base_map_templates.keys()),
        'global_instances': list(_global_map_instances.keys())
    }

def get_global_map_instance(map_type="flight", location=[35.8617, 104.1954], zoom_start=4):
    """获取全局地图实例，只初始化一次"""
    global _global_map_instances
    
    # 创建实例键
    instance_key = f"global_{map_type}"
    
    if instance_key not in _global_map_instances:
        import folium
        from folium.plugins import Fullscreen
        
        # 创建全局地图实例（不添加默认瓦片，让add_all_map_layers处理）
        global_map = folium.Map(
            location=location,
            zoom_start=zoom_start,
            tiles=None,  # 不添加默认瓦片，让add_all_map_layers处理
            prefer_canvas=True,
            control_scale=True
        )
        
        # 添加所有地图图层（只添加一次）
        add_all_map_layers(global_map)
        
        # 添加全屏控件
        Fullscreen(
            position='topleft',
            title='全屏显示',
            title_cancel='退出全屏',
            force_separate_button=True
        ).add_to(global_map)
        
        # 缓存全局实例
        _global_map_instances[instance_key] = global_map
        print(f"🗺️ 初始化全局地图实例: {map_type}")
    
    return _global_map_instances[instance_key]

def create_base_map(location=[35.8617, 104.1954], zoom_start=4, map_type="flight"):
    """创建基础地图，使用全局实例"""
    import copy
    
    # 获取全局地图实例
    global_map = get_global_map_instance(map_type, location, zoom_start)
    
    # 创建深拷贝以避免修改原始实例
    base_map = copy.deepcopy(global_map)
    
    # 更新位置和缩放级别（如果需要）
    if base_map.location != location or base_map.options['zoom'] != zoom_start:
        base_map.location = location
        base_map.options['zoom'] = zoom_start
    
    return base_map

def create_map_html(map_obj, config=None):
    """创建地图HTML，应用CDN优化"""
    # 直接使用Folium的HTML生成并应用CDN优化
    html = map_obj._repr_html_()
    return optimize_html_for_china(html)

def load_flight_data(file_path):
    """加载航班数据"""
    flights = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                flights.append(json.loads(line.strip()))
    return flights

def get_unique_airports(flights):
    """获取所有唯一机场"""
    departure_airports = sorted(list(set(flight['起飞机场'] for flight in flights)))
    arrival_airports = sorted(list(set(flight['降落机场'] for flight in flights)))
    return departure_airports, arrival_airports

def beautify_schedule(schedule_str):
    """美化班期显示，将数字转换为周一到周日"""
    if not schedule_str:
        return ""
    
    # 数字到星期的映射
    day_mapping = {
        '1': '周一',
        '2': '周二', 
        '3': '周三',
        '4': '周四',
        '5': '周五',
        '6': '周六',
        '7': '周日'
    }
    
    # 将数字字符串转换为星期
    days = []
    for char in str(schedule_str):
        if char in day_mapping:
            days.append(day_mapping[char])
    
    # 如果包含所有7天，显示"每日"
    if len(days) == 7:
        return "每日"
    
    # 如果包含工作日（周一到周五），显示"工作日"
    if set(days) == {'周一', '周二', '周三', '周四', '周五'}:
        return "工作日"
    
    # 如果包含周末（周六和周日），显示"周末"
    if set(days) == {'周六', '周日'}:
        return "周末"
    
    # 其他情况按顺序显示
    return " ".join(days)

def query_flights(flights, departure=None, arrival=None, flight_id=None, category=None):
    """查询航班"""
    results = []
    for flight in flights:
        match = True
        
        if departure and flight['起飞机场'] != departure:
            match = False
        if arrival and flight['降落机场'] != arrival:
            match = False
        if flight_id and flight['航班号'] != flight_id:
            match = False
        if category and category not in flight['适用产品']:
            match = False
            
        if match:
            results.append(flight)
    
    return results

def create_flight_map(flights_data=None):
    """创建航班地图（带缓存）"""
    import folium
    from folium.plugins import GroupedLayerControl, Fullscreen
    
    # 检查缓存（仅当使用默认数据时）
    if flights_data is None:
        cache_key = "flight_map_default"
        if cache_key in _map_cache:
            return _map_cache[cache_key]
    
    # 如果没有提供数据，加载默认数据
    if flights_data is None:
        flights_data = load_flight_data('data/hainan_plus_flights.jsonl')
    
    print(f"🗺️ 创建航班地图，数据量: {len(flights_data)}")
    
    # 初始化已显示机场集合
    shown_airports = set()
    # 创建基础地图
    flight_map = create_base_map(location=[35.8617, 104.1954], zoom_start=4, map_type="flight")
    
    # 创建航线图层组
    flight_group = folium.FeatureGroup(
        name='航线和机场',
        overlay=True,
        control=True,
        show=True
    )
    
    if flights_data and len(flights_data) > 0:
        print(f"🗺️ 处理航班数据，共 {len(flights_data)} 条记录")
        # 首先按起降点对航班进行分组
        route_groups = {}
        for flight in flights_data:
            # 处理字典格式的数据
            if isinstance(flight, dict):
                dep = flight['起飞机场']
                arr = flight['降落机场']
                flight_id = flight['航班号']
                flight_time = flight['起飞时间']
                flight_schedule = flight['班期']
            else:
                # 处理列表格式的数据（向后兼容）
                dep = flight[1]
                arr = flight[2]
                flight_id = flight[0]
                flight_time = flight[3]
                flight_schedule = flight[4]
            
            route_key = (dep, arr)
            if route_key not in route_groups:
                route_groups[route_key] = []
            route_groups[route_key].append(flight)
        
        print(f"🗺️ 找到 {len(route_groups)} 条航线")
        # 为每个起降点对绘制航线
        valid_routes = 0
        for route_key, flights in route_groups.items():
            dep, arr = route_key
            if dep in airport_coords and arr in airport_coords:
                valid_routes += 1
                dep_coords = airport_coords[dep]
                arr_coords = airport_coords[arr]
                
                # 计算基础距离和方向
                dist = ((dep_coords[1] - arr_coords[1]) ** 2 + 
                       (dep_coords[0] - arr_coords[0]) ** 2) ** 0.5
                base_curve = dist * 0.15
                
                # 根据同航线数量调整曲率
                num_flights = len(flights)
                for idx, flight in enumerate(flights):
                    # 提取航班信息
                    if isinstance(flight, dict):
                        flight_id = flight['航班号']
                        flight_time = flight['起飞时间']
                        flight_schedule = flight['班期']
                    else:
                        flight_id = flight[0]
                        flight_time = flight[3]
                        flight_schedule = flight[4]
                    
                    # 计算每条航线的偏移量
                    if num_flights > 1:
                        # 将多条航线分散开
                        offset = (idx - (num_flights - 1) / 2) * (base_curve * 0.5)
                    else:
                        offset = 0
                    
                    # 计算中点位置
                    mid_lat = (dep_coords[0] + arr_coords[0]) / 2
                    mid_lon = (dep_coords[1] + arr_coords[1]) / 2
                    
                    # 根据经度和航班索引调整曲率方向
                    if (dep_coords[1] + arr_coords[1]) / 2 < 105:
                        mid_lat += base_curve + offset
                    else:
                        mid_lat -= base_curve + offset
                    
                    # 创建弧线坐标列表
                    line_coords = [
                        dep_coords,
                        [mid_lat, mid_lon],
                        arr_coords
                    ]
                    
                    # 生成渐变色
                    color = f'#{hash(flight_id) % 0xFFFFFF:06x}'  # 根据航班号生成不同颜色
                    
                    # 添加航线
                    folium.PolyLine(
                        locations=line_coords,
                        weight=3,
                        color=color,
                        opacity=0.7,
                        popup=f"""
                        <div style='font-family: Arial; font-size: 12px;'>
                            <b>航班号:</b> {flight_id}<br>
                            <b>航线:</b> {dep} → {arr}<br>
                            <b>时间:</b> {flight_time}<br>
                            <b>班期:</b> {flight_schedule}
                        </div>
                        """,
                        tooltip=f"{flight_id}: {dep} → {arr}",
                        smooth_factor=0.2,
                        dash_array='5, 10'
                    ).add_to(flight_group)
                
                # 只添加一次起降点标记
                if dep not in shown_airports:
                    # 计算起飞机场的航班数
                    if isinstance(flights_data[0], dict):
                        dep_count = len([f for f in flights_data if f['起飞机场'] == dep])
                    else:
                        dep_count = len([f for f in flights_data if f[1] == dep])
                    
                    folium.CircleMarker(
                        location=dep_coords,
                        radius=6,
                        color='#ef4444',
                        fill=True,
                        fillOpacity=0.7,
                        weight=2,
                        popup=f"""
                        <div style='font-family: Arial; font-size: 12px;'>
                            <b>{dep}</b><br>
                            起飞机场<br>
                            航班数: {dep_count}
                        </div>
                        """,
                        tooltip=dep
                    ).add_to(flight_group)
                    shown_airports.add(dep)
                
                if arr not in shown_airports:
                    # 计算降落机场的航班数
                    if isinstance(flights_data[0], dict):
                        arr_count = len([f for f in flights_data if f['降落机场'] == arr])
                    else:
                        arr_count = len([f for f in flights_data if f[2] == arr])
                    
                    folium.CircleMarker(
                        location=arr_coords,
                        radius=6,
                        color='#22c55e',
                        fill=True,
                        fillOpacity=0.7,
                        weight=2,
                        popup=f"""
                        <div style='font-family: Arial; font-size: 12px;'>
                            <b>{arr}</b><br>
                            降落机场<br>
                            航班数: {arr_count}
                        </div>
                        """,
                        tooltip=arr
                    ).add_to(flight_group)
                    shown_airports.add(arr)
        
        print(f"🗺️ 有效航线数量: {valid_routes}，显示机场数量: {len(shown_airports)}")
    
    # 添加航线图层组到地图
    flight_group.add_to(flight_map)
    
    # 添加图层控制器
    folium.LayerControl(
        position='topright',
        collapsed=False
    ).add_to(flight_map)
    
    # 全屏控件已在全局地图实例中添加，无需重复添加
    
    # 使用应用级资源管理器创建优化的地图HTML
    try:
        map_html = create_optimized_map_html_app(flight_map, "flight_map")
    except Exception as e:
        print(f"地图HTML生成失败，使用备用方法: {e}")
        # 备用方法：直接生成HTML
        map_html = flight_map._repr_html_()
    
    # 缓存结果（仅当使用默认数据时）
    if flights_data is None:
        _map_cache["flight_map_default"] = map_html
    
    return map_html

def create_airport_distribution_map():
    """创建机场分布地图（带缓存）"""
    import folium
    from folium.plugins import HeatMap
    
    # 检查缓存
    cache_key = "airport_distribution_map"
    if cache_key in _map_cache:
        return _map_cache[cache_key]
    
    # 加载航班数据（只加载一次）
    flights_data = load_flight_data('data/hainan_plus_flights.jsonl')
    
    # 创建基础地图
    distribution_map = create_base_map(location=[35.8617, 104.1954], zoom_start=4, map_type="distribution")
    
    # 准备热力图数据
    heat_data = []
    airport_stats = {}  # 缓存机场统计
    
    for airport, coords in airport_coords.items():
        # 计算该机场的航班数量
        dep_count = len([f for f in flights_data if f['起飞机场'] == airport])
        arr_count = len([f for f in flights_data if f['降落机场'] == airport])
        total_count = dep_count + arr_count
        
        airport_stats[airport] = {'dep': dep_count, 'arr': arr_count, 'total': total_count}
        
        if total_count > 0:
            heat_data.append([coords[0], coords[1], total_count])
    
    # 创建热力图图层组
    heatmap_group = folium.FeatureGroup(name='机场航班密度', show=True)
    
    # 添加热力图
    if heat_data:
        HeatMap(
            heat_data,
            name='机场航班密度',
            min_opacity=0.3,
            max_opacity=0.8,
            max_zoom=18,
            radius=30,
            blur=20,
            gradient={
                0.0: 'blue',      # 低密度 - 蓝色
                0.2: 'cyan',      # 中低密度 - 青色
                0.4: 'lime',      # 中密度 - 绿色
                0.6: 'yellow',    # 中高密度 - 黄色
                0.8: 'orange',    # 高密度 - 橙色
                1.0: 'red'        # 极高密度 - 红色
            }
        ).add_to(heatmap_group)
    
    # 添加热力图图层组到地图
    heatmap_group.add_to(distribution_map)
    
    # 创建机场标记图层组
    airport_markers_group = folium.FeatureGroup(name='机场标记', show=True)
    
    # 添加机场标记
    for airport, coords in airport_coords.items():
        stats = airport_stats[airport]
        total_count = stats['total']
        
        if total_count > 0:
            # 根据航班数量调整标记大小和颜色
            radius = max(6, min(25, total_count / 8))
            
            # 根据航班数量选择颜色
            if total_count >= 100:
                color = '#e74c3c'  # 红色 - 高密度
                fill_color = '#c0392b'
            elif total_count >= 50:
                color = '#f39c12'  # 橙色 - 中高密度
                fill_color = '#e67e22'
            elif total_count >= 20:
                color = '#f1c40f'  # 黄色 - 中密度
                fill_color = '#f39c12'
            else:
                color = '#27ae60'  # 绿色 - 低密度
                fill_color = '#2ecc71'
            
            # 创建机场标记
            folium.CircleMarker(
                location=coords,
                radius=radius,
                popup=folium.Popup(
                    f"""
                    <div style='
                        font-family: "Segoe UI", Arial, sans-serif;
                        font-size: 14px;
                        line-height: 1.4;
                        min-width: 200px;
                        padding: 10px;
                    '>
                        <div style='
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            padding: 8px 12px;
                            margin: -10px -10px 10px -10px;
                            border-radius: 5px 5px 0 0;
                            font-weight: bold;
                            font-size: 16px;
                            text-align: center;
                        '>
                            ✈️ {airport}
                        </div>
                        <div style='padding: 5px 0;'>
                            <div style='display: flex; justify-content: space-between; margin: 5px 0;'>
                                <span style='color: #e74c3c; font-weight: bold;'>🛫 起飞:</span>
                                <span style='font-weight: bold;'>{stats['dep']} 班</span>
                            </div>
                            <div style='display: flex; justify-content: space-between; margin: 5px 0;'>
                                <span style='color: #27ae60; font-weight: bold;'>🛬 降落:</span>
                                <span style='font-weight: bold;'>{stats['arr']} 班</span>
                            </div>
                            <hr style='margin: 10px 0; border: none; border-top: 2px solid #ecf0f1;'>
                            <div style='display: flex; justify-content: space-between; margin: 5px 0;'>
                                <span style='color: #2c3e50; font-weight: bold; font-size: 15px;'>📊 总计:</span>
                                <span style='font-weight: bold; font-size: 15px; color: #e74c3c;'>{total_count} 班</span>
                            </div>
                        </div>
                        <div style='
                            background: #f8f9fa;
                            padding: 8px;
                            margin: 10px -10px -10px -10px;
                            border-radius: 0 0 5px 5px;
                            font-size: 12px;
                            color: #6c757d;
                            text-align: center;
                        '>
                            📍 坐标: {coords[0]:.4f}, {coords[1]:.4f}
                        </div>
                    </div>
                    """,
                    max_width=250
                ),
                tooltip=f"{airport} ({total_count} 班)",
                color=color,
                fill=True,
                fillColor=fill_color,
                fillOpacity=0.8,
                weight=2
            ).add_to(airport_markers_group)
    
    # 添加机场标记图层组到地图
    airport_markers_group.add_to(distribution_map)
    
    # 添加图层控制器
    folium.LayerControl(
        position='topright',
        collapsed=False,
        autoZIndex=True
    ).add_to(distribution_map)
    
    # 使用应用级资源管理器创建优化的地图HTML
    try:
        map_html = create_optimized_map_html_app(distribution_map, "airport_distribution")
    except Exception as e:
        print(f"地理分布地图HTML生成失败，使用备用方法: {e}")
        # 备用方法：直接生成HTML
        map_html = distribution_map._repr_html_()
    
    # 缓存结果
    _map_cache[cache_key] = map_html
    return map_html

def create_route_network_chart(flights_data=None):
    """创建航线网络图（带缓存）"""
    import folium
    
    # 检查缓存
    cache_key = "route_network_map"
    if cache_key in _map_cache and flights_data is None:
        return _map_cache[cache_key]
    
    # 如果没有提供数据，加载默认数据
    if flights_data is None:
        flights_data = load_flight_data('data/hainan_plus_flights.jsonl')
    
    # 创建基础地图
    network_map = create_base_map(location=[35.8617, 104.1954], zoom_start=4, map_type="network")
    
    # 统计航线频次
    route_counts = {}
    for flight in flights_data:
        dep = flight['起飞机场']
        arr = flight['降落机场']
        route = f"{dep} → {arr}"
        route_counts[route] = route_counts.get(route, 0) + 1
    
    # 统计机场使用频次
    airport_usage = {}
    for route, count in route_counts.items():
        dep, arr = route.split(' → ')
        if dep in airport_coords and arr in airport_coords:
            airport_usage[dep] = airport_usage.get(dep, 0) + count
            airport_usage[arr] = airport_usage.get(arr, 0) + count
    
    # 绘制航线
    for route, count in route_counts.items():
        dep, arr = route.split(' → ')
        if dep in airport_coords and arr in airport_coords:
            dep_coords = airport_coords[dep]
            arr_coords = airport_coords[arr]
            
            # 根据频次调整线条粗细
            weight = max(1, min(8, count / 5))
            
            # 绘制航线
            folium.PolyLine(
                locations=[dep_coords, arr_coords],
                weight=weight,
                color='#3186cc',
                opacity=0.6,
                popup=f"""
                <div style='font-family: Arial; font-size: 12px;'>
                    <b>{route}</b><br>
                    航班数: {count}
                </div>
                """,
                tooltip=f"{route}: {count} 班"
            ).add_to(network_map)
    
    # 添加机场标记和名称标签
    for airport, coords in airport_coords.items():
        if airport in airport_usage:
            usage_count = airport_usage[airport]
            
            # 根据使用频次调整标记大小
            radius = max(4, min(12, usage_count / 20))
            
            # 添加机场标记
            folium.CircleMarker(
                location=coords,
                radius=radius,
                color='#e74c3c',
                fill=True,
                fillOpacity=0.8,
                weight=2,
                popup=f"""
                <div style='font-family: Arial; font-size: 12px;'>
                    <b>{airport}</b><br>
                    总航班数: {usage_count}
                </div>
                """,
                tooltip=airport
            ).add_to(network_map)
            
            # 添加机场名称标签
            folium.Marker(
                location=[coords[0] + 0.5, coords[1] + 0.5],  # 稍微偏移避免重叠
                icon=folium.DivIcon(
                    html=f"""
                    <div style="
                        font-family: Arial, sans-serif;
                        font-size: 11px;
                        font-weight: bold;
                        color: #2c3e50;
                        background-color: rgba(255, 255, 255, 0.8);
                        padding: 2px 4px;
                        border-radius: 3px;
                        border: 1px solid #bdc3c7;
                        white-space: nowrap;
                        text-shadow: 1px 1px 1px rgba(255, 255, 255, 0.8);
                    ">
                        {airport}
                    </div>
                    """,
                    icon_size=(60, 20),
                    icon_anchor=(30, 10)
                )
            ).add_to(network_map)
    
    # 使用应用级资源管理器创建优化的地图HTML
    try:
        map_html = create_optimized_map_html_app(network_map, "route_network")
    except Exception as e:
        print(f"航线网络地图HTML生成失败，使用备用方法: {e}")
        # 备用方法：直接生成HTML
        map_html = network_map._repr_html_()
    
    # 缓存结果（仅当使用默认数据时）
    if flights_data is None:
        _map_cache[cache_key] = map_html
    
    return map_html

def create_airport_bubble_chart(flights_data=None):
    """创建机场气泡图（使用经纬度坐标）"""
    if not flights_data:
        flights_data = load_flight_data('data/hainan_plus_flights.jsonl')
    
    # 统计机场航班数
    airport_counts = {}
    for flight in flights_data:
        dep = flight['起飞机场']
        arr = flight['降落机场']
        airport_counts[dep] = airport_counts.get(dep, 0) + 1
        airport_counts[arr] = airport_counts.get(arr, 0) + 1
    
    # 准备经纬度数据
    lats = []
    lons = []
    counts = []
    airports = []
    
    for airport, count in airport_counts.items():
        if airport in airport_coords:
            coords = airport_coords[airport]
            lats.append(coords[0])  # 纬度
            lons.append(coords[1])  # 经度
            counts.append(count)
            airports.append(airport)
    
    # 创建气泡图
    fig = go.Figure(data=go.Scatter(
        x=lons,  # 经度作为x轴
        y=lats,  # 纬度作为y轴
        mode='markers',
        marker=dict(
            size=counts,
            sizemode='diameter',
            sizeref=max(counts)/50 if counts else 1,
            color=counts,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="航班数量"),
            line=dict(width=1, color='white')
        ),
        text=[f"{airport}<br>航班数: {count}<br>经度: {lon:.4f}<br>纬度: {lat:.4f}" 
              for airport, count, lat, lon in zip(airports, counts, lats, lons)],
        hovertemplate='%{text}<extra></extra>'
    ))
    
    fig.update_layout(
        title='机场航班频次分布（经纬度坐标）',
        xaxis_title='经度',
        yaxis_title='纬度',
        height=600,
        showlegend=False,
        xaxis=dict(
            scaleanchor="y",
            scaleratio=1,
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        ),
        plot_bgcolor='white'
    )
    
    return fig

def create_stats_chart(flights_data=None):
    """创建统计图表"""
    if not flights_data:
        flights_data = load_flight_data('data/hainan_plus_flights.jsonl')
    
    # 统计起飞机场
    dep_counts = {}
    arr_counts = {}
    
    for flight in flights_data:
        dep = flight['起飞机场']
        arr = flight['降落机场']
        dep_counts[dep] = dep_counts.get(dep, 0) + 1
        arr_counts[arr] = arr_counts.get(arr, 0) + 1
    
    # 获取所有机场
    all_airports = sorted(set(dep_counts.keys()) | set(arr_counts.keys()))
    
    # 准备数据
    dep_values = [dep_counts.get(airport, 0) for airport in all_airports]
    arr_values = [arr_counts.get(airport, 0) for airport in all_airports]
    
    # 创建柱状图
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='起飞航班数',
        x=all_airports,
        y=dep_values,
        marker_color='#667eea'
    ))
    
    fig.add_trace(go.Bar(
        name='降落航班数',
        x=all_airports,
        y=arr_values,
        marker_color='#764ba2'
    ))
    
    fig.update_layout(
        title='机场航班频次统计',
        xaxis_title='机场名称',
        yaxis_title='航班数量',
        barmode='group',
        height=600,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(b=100, t=100),
        xaxis=dict(
            tickangle=45,
            tickfont=dict(size=10)
        )
    )
    
    return fig

# 标签页地图缓存
_tab_map_cache = {}

def get_cached_tab_map(map_type, create_func, *args, **kwargs):
    """获取缓存的标签页地图"""
    global _tab_map_cache
    
    cache_key = f"tab_{map_type}"
    
    if cache_key not in _tab_map_cache:
        print(f"🗺️ 创建标签页地图缓存: {map_type}")
        _tab_map_cache[cache_key] = create_func(*args, **kwargs)
    
    return _tab_map_cache[cache_key]

def clear_tab_map_cache():
    """清空标签页地图缓存"""
    global _tab_map_cache
    _tab_map_cache.clear()
    print("🗑️ 标签页地图缓存已清理")

def get_tab_cache_stats():
    """获取标签页缓存统计"""
    global _tab_map_cache
    return {
        'tab_cache_size': len(_tab_map_cache),
        'cached_tabs': list(_tab_map_cache.keys())
    }
