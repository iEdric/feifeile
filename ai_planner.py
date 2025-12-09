#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI航班规划模块
使用OpenAI API进行智能路线规划
"""

import json
import os
from typing import List, Dict, Tuple, Optional
from collections import defaultdict, deque
from openai import OpenAI
import re

class FlightPlanner:
    def __init__(self, flights_data: List[Dict], openai_api_key: str = None, openai_base_url: str = None):
        """
        初始化航班规划器
        
        Args:
            flights_data: 航班数据列表
            openai_api_key: OpenAI API密钥，如果为None则从环境变量获取
            openai_base_url: OpenAI API基础URL，如果为None则使用默认值
        """
        self.flights = flights_data
        self.flight_graph = self._build_flight_graph()
        
        # 设置OpenAI API
        api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        base_url = openai_base_url or os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        
        if not api_key:
            raise ValueError("OpenAI API密钥未设置，请设置环境变量OPENAI_API_KEY或传入api_key参数")
        
        # 初始化OpenAI客户端
        self.client = OpenAI(api_key=api_key, base_url=base_url)
    
    def _build_flight_graph(self) -> Dict[str, List[Dict]]:
        """
        构建航班网络图
        返回格式: {机场名: [从该机场出发的航班列表]}
        """
        graph = defaultdict(list)
        for flight in self.flights:
            departure = flight['起飞机场']
            graph[departure].append(flight)
        return dict(graph)
    
    def find_all_routes(self, start_airport: str, end_airport: str, max_stops: int = 2) -> List[List[Dict]]:
        """
        查找从起点到终点的所有可能路线
        
        Args:
            start_airport: 起飞机场
            end_airport: 目标机场
            max_stops: 最大中转次数
            
        Returns:
            所有可能路线的列表，每个路线是一个航班列表
        """
        if start_airport not in self.flight_graph:
            return []
        
        all_routes = []
        queue = deque([(start_airport, [], 0)])  # (当前机场, 已飞路线, 中转次数)
        visited = set()
        
        while queue:
            current_airport, current_route, stops = queue.popleft()
            
            # 如果到达目标机场
            if current_airport == end_airport and current_route:
                all_routes.append(current_route)
                continue
            
            # 如果中转次数超过限制
            if stops >= max_stops:
                continue
            
            # 避免循环
            route_key = (current_airport, stops)
            if route_key in visited:
                continue
            visited.add(route_key)
            
            # 查找从当前机场出发的所有航班
            available_flights = self.flight_graph.get(current_airport, [])
            
            for flight in available_flights:
                next_airport = flight['降落机场']
                new_route = current_route + [flight]
                queue.append((next_airport, new_route, stops + 1))
        
        return all_routes
    
    
    def _is_valid_connection(self, flight1: Dict, flight2: Dict) -> bool:
        """
        检查两个航班是否可以连接（考虑时间间隔）
        """
        # 简单的时间检查：第二个航班起飞时间应该晚于第一个航班降落时间
        # 这里简化处理，实际应该考虑机场间转机时间
        return True
    
    def filter_valid_routes(self, routes: List[List[Dict]]) -> List[List[Dict]]:
        """
        过滤出有效的路线（考虑时间合理性）
        """
        valid_routes = []
        
        for route in routes:
            is_valid = True
            
            # 检查每个连接是否合理
            for i in range(len(route) - 1):
                if not self._is_valid_connection(route[i], route[i + 1]):
                    is_valid = False
                    break
            
            if is_valid:
                valid_routes.append(route)
        
        return valid_routes
    
    def get_route_summary(self, route: List[Dict]) -> Dict:
        """
        获取路线摘要信息
        """
        if not route:
            return {}
        
        total_flights = len(route)
        airports = [route[0]['起飞机场']] + [flight['降落机场'] for flight in route]
        unique_airports = list(set(airports))
        
        # 计算总飞行时间（简化计算）
        total_duration = 0
        for flight in route:
            # 这里简化处理，实际应该根据机场坐标计算飞行时间
            total_duration += 120  # 假设每个航班2小时
        
        return {
            'total_flights': total_flights,
            'total_airports': len(unique_airports),
            'route_airports': airports,
            'estimated_duration': total_duration,
            'stops': total_flights - 1
        }
    
    def ai_optimize_routes(self, routes: List[List[Dict]], user_preferences: str = "") -> List[Dict]:
        """
        使用OpenAI API优化路线推荐
        
        Args:
            routes: 所有可能的路线
            user_preferences: 用户偏好描述
            
        Returns:
            优化后的路线推荐列表
        """
        if not routes:
            return []
        
        # 准备路线数据给AI分析
        route_data = []
        for i, route in enumerate(routes[:10]):  # 限制前10条路线给AI分析
            summary = self.get_route_summary(route)
            route_info = {
                'route_id': i + 1,
                'flights': route,
                'summary': summary,
                'description': self._format_route_description(route)
            }
            route_data.append(route_info)
        
        # 构建AI提示
        prompt = self._build_ai_prompt(route_data, user_preferences)
        
        try:
            # 调用OpenAI API
            response = self.client.chat.completions.create(
                model="Qwen/Qwen2.5-7B-Instruct",
                messages=[
                    {"role": "system", "content": "你是一个专业的航班规划助手，帮助用户选择最优的飞行路线。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            ai_recommendations = self._parse_ai_response(response.choices[0].message.content)
            return ai_recommendations
            
        except Exception as e:
            print(f"OpenAI API调用失败: {e}")
            # 如果API调用失败，返回简单的排序结果
            return self._fallback_sort_routes(route_data)
    
    def _format_route_description(self, route: List[Dict]) -> str:
        """
        格式化路线描述
        """
        if not route:
            return ""
        
        description = f"从 {route[0]['起飞机场']} 出发"
        for flight in route:
            description += f" → {flight['降落机场']} ({flight['航班号']})"
        
        return description
    
    def _build_ai_prompt(self, route_data: List[Dict], user_preferences: str) -> str:
        """
        构建AI分析提示
        """
        prompt = f"""
请分析以下航班路线选项，并为用户推荐最优路线。

用户偏好: {user_preferences if user_preferences else "无特殊偏好"}

可用路线选项:
"""
        
        for route_info in route_data:
            prompt += f"""
路线 {route_info['route_id']}:
- 描述: {route_info['description']}
- 总航班数: {route_info['summary']['total_flights']}
- 中转次数: {route_info['summary']['stops']}
- 涉及机场: {', '.join(route_info['summary']['route_airports'])}
- 航班详情:
"""
            for flight in route_info['flights']:
                prompt += f"  * {flight['航班号']}: {flight['起飞机场']} → {flight['降落机场']} ({flight['起飞时间']}, {flight['班期']})\n"
        
        prompt += """
请根据以下标准分析并推荐路线:
1. 总飞行时间最短
2. 中转次数最少
3. 航班时间安排合理
4. 机场便利性
5. 用户偏好

请返回JSON格式的推荐结果，包含:
- 推荐路线ID列表（按优先级排序）
- 每个推荐路线的理由
- 总体建议

格式示例:
{
  "recommendations": [
    {
      "route_id": 1,
      "reason": "直飞路线，时间最短",
      "priority": 1
    }
  ],
  "overall_advice": "建议选择直飞路线以获得最佳体验"
}
"""
        
        return prompt
    
    def _parse_ai_response(self, response: str) -> List[Dict]:
        """
        解析AI响应
        """
        try:
            # 尝试提取JSON部分
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data.get('recommendations', [])
        except:
            pass
        
        # 如果解析失败，返回空列表
        return []
    
    def _fallback_sort_routes(self, route_data: List[Dict]) -> List[Dict]:
        """
        AI API失败时的备用排序方法
        """
        # 按中转次数和总航班数排序
        sorted_routes = sorted(route_data, key=lambda x: (x['summary']['stops'], x['summary']['total_flights']))
        
        recommendations = []
        for i, route in enumerate(sorted_routes[:5]):  # 返回前5条
            recommendations.append({
                'route_id': route['route_id'],
                'reason': f"中转{route['summary']['stops']}次，共{route['summary']['total_flights']}个航班",
                'priority': i + 1
            })
        
        return recommendations
    
    def plan_trip(self, start_airport: str, end_airport: str, user_preferences: str = "", max_stops: int = 2) -> Dict:
        """
        完整的行程规划
        
        Args:
            start_airport: 起飞机场
            end_airport: 目标机场
            user_preferences: 用户偏好
            max_stops: 最大中转次数
            
        Returns:
            规划结果字典
        """
        # 查找所有可能路线
        all_routes = self.find_all_routes(start_airport, end_airport, max_stops)
        
        if not all_routes:
            return {
                'success': False,
                'message': f'未找到从 {start_airport} 到 {end_airport} 的路线',
                'routes': [],
                'recommendations': []
            }
        
        # 过滤有效路线
        valid_routes = self.filter_valid_routes(all_routes)
        
        if not valid_routes:
            return {
                'success': False,
                'message': '未找到有效的飞行路线',
                'routes': [],
                'recommendations': []
            }
        
        # AI优化推荐
        recommendations = self.ai_optimize_routes(valid_routes, user_preferences)
        
        return {
            'success': True,
            'message': f'找到 {len(valid_routes)} 条可能的路线',
            'routes': valid_routes,
            'recommendations': recommendations,
            'total_routes': len(valid_routes)
        }
