'''
Author: cl cl@qq.com
Date: 2025-09-05 09:27:50
LastEditors: cl cl@qq.com
LastEditTime: 2025-09-05 22:06:23
FilePath: /chenli-flight-app/app.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
航班查询系统主程序
"""

import gradio as gr
from utils import create_route_network_chart,create_airport_bubble_chart,create_airport_distribution_map,load_flight_data, get_unique_airports, query_flights, create_flight_map, create_stats_chart, get_cached_tab_map, beautify_schedule, force_clear_all_caches
from app_resource_manager import get_app_global_resources_html
from ai_planner import FlightPlanner
import os
import base64



# 加载航班数据
flights = load_flight_data(r'data/hainan_plus_flights.jsonl')
departure_airports, arrival_airports = get_unique_airports(flights)

# 清理地图缓存，确保新的CDN配置生效
force_clear_all_caches()

# 初始化AI规划器
try:
    # 支持SiliconFlow API配置
    api_key = os.getenv('OPENAI_API_KEY')
    base_url = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
    
    # 如果环境变量未设置，使用SiliconFlow作为默认配置
    if not api_key:
        print("🔧 使用SiliconFlow API作为默认配置...")
        api_key = "sk-"
        base_url = "https://api.siliconflow.cn/v1"
    
    planner = FlightPlanner(flights, api_key, base_url)
    ai_available = True
    print(f"✅ AI规划器初始化成功，使用API: {base_url}")
except Exception as e:
    print(f"❌ AI规划器初始化失败: {e}")
    planner = None
    ai_available = False

def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return f"data:image/jpeg;base64,{base64.b64encode(img_file.read()).decode()}"

# 替换为你的实际图片路径
alipay_base64 = image_to_base64(r"data/alipay.jpg")
wechat_base64 = image_to_base64(r"data/wechat.jpg")

# 获取应用全局资源HTML
global_resources = get_app_global_resources_html()

css = f"""
{global_resources}
.gradio-container {{
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}}
.main-header {{
    text-align: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
}}
.search-section {{
    background: #f8f9fa;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
}}
.map-section {{
    background: #ffffff;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}}
.map-container {{
    height: 500px;
    width: 100%;
    border: 1px solid #ddd;
    border-radius: 5px;
    overflow: hidden;
}}
.stats-section {{
    background: #ffffff;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}}

/* AI规划专用样式 - 最高级别 */
.ai-main-section {{
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
    border-radius: 20px !important;
    padding: 25px !important;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1) !important;
    border: 1px solid rgba(102, 126, 234, 0.1) !important;
}}

/* 强制覆盖Gradio深色主题 */
.ai-main-section * {{
    color: #1a1a1a !important;
}}

.ai-main-section h1,
.ai-main-section h2,
.ai-main-section h3,
.ai-main-section h4,
.ai-main-section h5,
.ai-main-section h6 {{
    color: #1a1a1a !important;
}}

.ai-main-section p,
.ai-main-section span,
.ai-main-section div {{
    color: #1a1a1a !important;
}}

.ai-input {{
    border-radius: 8px !important;
    border: 2px solid #e9ecef !important;
    transition: all 0.3s ease !important;
    background: #ffffff !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    font-weight: 500 !important;
    font-size: 1em !important;
    color: #1a1a1a !important;
}}
.ai-input:focus {{
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1), 0 4px 15px rgba(102, 126, 234, 0.15) !important;
    transform: translateY(-1px) !important;
    background: #ffffff !important;
    color: #1a1a1a !important;
}}
.ai-slider {{
    margin: 15px 0 !important;
    padding: 10px 0 !important;
    background: #ffffff !important;
    border-radius: 8px !important;
    border: 1px solid #e9ecef !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04) !important;
}}

/* 机场选择区域背景 */
.airport-selection-group {{
    background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%) !important;
    border-radius: 15px !important;
    padding: 20px !important;
    margin: 15px 0 !important;
    border: 1px solid rgba(33, 150, 243, 0.2) !important;
    box-shadow: 0 4px 15px rgba(33, 150, 243, 0.1) !important;
}}

.airport-selection-group * {{
    color: #1a1a1a !important;
}}

/* 智能偏好设置区域背景 */
.preferences-group {{
    background: linear-gradient(135deg, #f3e5f5 0%, #e8f5e8 100%) !important;
    border-radius: 15px !important;
    padding: 20px !important;
    margin: 15px 0 !important;
    border: 1px solid rgba(156, 39, 176, 0.2) !important;
    box-shadow: 0 4px 15px rgba(156, 39, 176, 0.1) !important;
}}

.preferences-group * {{
    color: #1a1a1a !important;
}}

/* 中转次数设置区域背景 */
.stops-group {{
    background: linear-gradient(135deg, #fff3e0 0%, #f3e5f5 100%) !important;
    border-radius: 15px !important;
    padding: 20px !important;
    margin: 15px 0 !important;
    border: 1px solid rgba(255, 152, 0, 0.2) !important;
    box-shadow: 0 4px 15px rgba(255, 152, 0, 0.1) !important;
}}

.stops-group * {{
    color: #1a1a1a !important;
}}

/* 操作按钮区域背景 */
.buttons-group {{
    background: linear-gradient(135deg, #fff3e0 0%, #e8f5e8 100%) !important;
    border-radius: 15px !important;
    padding: 20px !important;
    margin: 15px 0 !important;
    border: 1px solid rgba(255, 152, 0, 0.2) !important;
    box-shadow: 0 4px 15px rgba(255, 152, 0, 0.1) !important;
}}

.buttons-group * {{
    color: #1a1a1a !important;
}}

/* 强制覆盖Gradio深色主题的所有文本元素 */
.ai-main-section .gr-textbox,
.ai-main-section .gr-dropdown,
.ai-main-section .gr-slider,
.ai-main-section .gr-button {{
    color: #1a1a1a !important;
}}

.ai-main-section .gr-textbox input,
.ai-main-section .gr-dropdown select,
.ai-main-section .gr-slider input {{
    color: #1a1a1a !important;
    background: #ffffff !important;
}}

.ai-main-section .gr-textbox label,
.ai-main-section .gr-dropdown label,
.ai-main-section .gr-slider label {{
    color: #1a1a1a !important;
}}

/* 确保所有文本在深色主题下可见 */
.ai-main-section .gr-form,
.ai-main-section .gr-group,
.ai-main-section .gr-row,
.ai-main-section .gr-column {{
    color: #1a1a1a !important;
}}

/* 覆盖Gradio的默认样式 */
.ai-main-section .gr-textbox .gr-textbox-label,
.ai-main-section .gr-dropdown .gr-dropdown-label,
.ai-main-section .gr-slider .gr-slider-label {{
    color: #1a1a1a !important;
    font-weight: 600 !important;
}}

.ai-main-section .gr-textbox .gr-textbox-info,
.ai-main-section .gr-dropdown .gr-dropdown-info,
.ai-main-section .gr-slider .gr-slider-info {{
    color: #6c757d !important;
}}
.ai-plan-btn {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
    border-radius: 30px !important;
    padding: 15px 35px !important;
    font-weight: 700 !important;
    font-size: 1.2em !important;
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    transition: all 0.3s ease !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}}
.ai-plan-btn:hover {{
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6) !important;
    background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%) !important;
}}
.ai-clear-btn {{
    border-radius: 30px !important;
    padding: 15px 35px !important;
    font-weight: 600 !important;
    font-size: 1.1em !important;
    transition: all 0.3s ease !important;
    border: 2px solid #dee2e6 !important;
    background: #ffffff !important;
    color: #6c757d !important;
}}
.ai-clear-btn:hover {{
    transform: translateY(-2px) !important;
    border-color: #adb5bd !important;
    background: #f8f9fa !important;
    color: #495057 !important;
}}
.ai-table {{
    border-radius: 15px !important;
    overflow: hidden !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1) !important;
    border: 1px solid #e9ecef !important;
}}

/* AI规划区域特殊样式 */
.ai-main-section {{
    background: linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%) !important;
    border-radius: 20px !important;
    padding: 30px !important;
    margin: 20px 0 !important;
    box-shadow: 0 10px 40px rgba(102, 126, 234, 0.1) !important;
    border: 1px solid rgba(102, 126, 234, 0.1) !important;
}}

/* 响应式设计 */
@media (max-width: 768px) {{
    .ai-plan-btn, .ai-clear-btn {{
        width: 100% !important;
        margin: 5px 0 !important;
    }}
}}

footer {{
    display: none !important;
}}
footer.gradio-footer-custom {{
    display: none !important;
}}
.gradio-footer {{
    display: none !important;
}}

/* 自定义组件样式 - 完全独立于Gradio主题 */
.custom-dropdown {{
    background: #ffffff !important;
    border: 2px solid #e9ecef !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
    font-size: 1em !important;
    color: #2c3e50 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    transition: all 0.3s ease !important;
    margin-bottom: 15px !important;
}}

.custom-dropdown:focus {{
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1), 0 4px 15px rgba(102, 126, 234, 0.15) !important;
    outline: none !important;
}}

.custom-dropdown label {{
    color: #2c3e50 !important;
    font-weight: 600 !important;
    font-size: 1em !important;
    margin-bottom: 8px !important;
}}

.custom-textbox {{
    background: #ffffff !important;
    border: 2px solid #e9ecef !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
    font-size: 1em !important;
    color: #2c3e50 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    transition: all 0.3s ease !important;
    margin-bottom: 15px !important;
    resize: vertical !important;
}}

.custom-textbox:focus {{
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1), 0 4px 15px rgba(102, 126, 234, 0.15) !important;
    outline: none !important;
}}

.custom-textbox label {{
    color: #2c3e50 !important;
    font-weight: 600 !important;
    font-size: 1em !important;
    margin-bottom: 8px !important;
}}

.custom-textbox textarea {{
    background: transparent !important;
    border: none !important;
    color: #2c3e50 !important;
    font-size: 1em !important;
    line-height: 1.5 !important;
}}

.custom-slider {{
    background: #ffffff !important;
    border: 2px solid #e9ecef !important;
    border-radius: 10px !important;
    padding: 20px 16px !important;
    margin-bottom: 15px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
}}

.custom-slider label {{
    color: #2c3e50 !important;
    font-weight: 600 !important;
    font-size: 1em !important;
    margin-bottom: 10px !important;
}}

.custom-slider input[type="range"] {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    height: 6px !important;
    border-radius: 3px !important;
    outline: none !important;
}}

.custom-slider input[type="range"]::-webkit-slider-thumb {{
    background: #667eea !important;
    border: 3px solid #ffffff !important;
    border-radius: 50% !important;
    width: 20px !important;
    height: 20px !important;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
}}

.custom-primary-btn {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 15px 30px !important;
    font-size: 1.1em !important;
    font-weight: 700 !important;
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3) !important;
    transition: all 0.3s ease !important;
    margin-bottom: 15px !important;
    width: 100% !important;
}}

.custom-primary-btn:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
}}

.custom-secondary-btn {{
    background: #ffffff !important;
    color: #667eea !important;
    border: 2px solid #667eea !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    font-size: 0.9em !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1) !important;
    transition: all 0.3s ease !important;
    margin: 0 5px !important;
}}

.custom-secondary-btn:hover {{
    background: #667eea !important;
    color: white !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2) !important;
}}

/* 强制覆盖所有Gradio默认样式 */
.custom-dropdown *,
.custom-textbox *,
.custom-slider *,
.custom-primary-btn *,
.custom-secondary-btn * {{
    color: inherit !important;
}}

/* 确保下拉框选项可见 */
.custom-dropdown .gr-dropdown-options {{
    background: #ffffff !important;
    border: 2px solid #e9ecef !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
}}

.custom-dropdown .gr-dropdown-option {{
    color: #2c3e50 !important;
    padding: 10px 16px !important;
}}

.custom-dropdown .gr-dropdown-option:hover {{
    background: #f8f9fa !important;
}}
"""

def update_all(dep, arr, cat):
    """统一更新查询结果、地图和统计图"""
    # Clean inputs
    dep = dep.strip() if dep else ""
    arr = arr.strip() if arr else ""
    
    # Query flights
    if not dep and not arr:
        # 如果没有选择机场，显示所有航班（限制数量以避免性能问题）
        results = flights[:100]  # 显示前100个航班作为示例
        message = f"🗺️ 显示所有航班示例（前100条），请选择机场进行精确查询"
    else:
        # 有选择机场时，进行精确查询
        results = query_flights(flights, dep if dep else None, arr if arr else None, None, cat if cat else None)
        if len(results) == 0:
            message = f"⚠️ 未找到符合条件的航班，请尝试其他机场组合"
        else:
            message = f"✅ 查询完成，找到 {len(results)} 条航班记录"
    
    # Convert results to array format for Dataframe
    if results:
        array_results = []
        for flight in results:
            row = [flight['航班号'], flight['起飞机场'], flight['降落机场'], 
                   flight['起飞时间'], beautify_schedule(flight['班期']), flight['适用产品']]
            array_results.append(row)
    else:
        array_results = []
    
    # Create map and stats (使用缓存优化)
    from utils import _map_cache
    
    # 生成缓存键
    cache_key = f"flight_map_{hash(str(results))}"
    
    # 检查地图缓存
    if cache_key in _map_cache:
        map_html = _map_cache[cache_key]
    else:
        map_html = create_flight_map(results)
        # 缓存地图HTML
        _map_cache[cache_key] = map_html
    
    stats_plot = create_stats_chart(results if results else None)
    return array_results, map_html, stats_plot, gr.update(visible=True, value=message)

def clear_all():
    """清空所有输入和输出"""
    # Convert sample flights to array format
    sample_flights = flights[:100]
    array_sample = []
    for flight in sample_flights:
        row = [flight['航班号'], flight['起飞机场'], flight['降落机场'], 
               flight['起飞时间'], beautify_schedule(flight['班期']), flight['适用产品']]
        array_sample.append(row)
    
    # 使用缓存优化
    from utils import _map_cache
    cache_key = "flight_map_default"
    
    if cache_key in _map_cache:
        map_html = _map_cache[cache_key]
    else:
        map_html = create_flight_map(sample_flights)
        _map_cache[cache_key] = map_html
    
    return None, None, None, array_sample, map_html, create_stats_chart(None)
def clear_departure():
    """清除起飞机场选择"""
    return gr.update(value=None)

def clear_arrival():
    """清除降落机场选择"""
    return gr.update(value=None)

def ai_plan_route(start_airport, end_airport, preferences, max_stops):
    """AI路线规划"""
    if not ai_available or not planner:
        error_msg = """
        <div style='background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%); color: white; padding: 15px; border-radius: 10px; margin: 10px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.2); text-align: center; font-size: 1.2em; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
            ❌ AI规划功能不可用，请检查OpenAI API配置
        </div>
        """
        return error_msg, ""
    
    if not start_airport or not end_airport:
        warning_msg = """
        <div style='background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); color: white; padding: 15px; border-radius: 10px; margin: 10px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.2); text-align: center; font-size: 1.2em; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
            ⚠️ 请选择起飞机场和目标机场
        </div>
        """
        return warning_msg, "", []
    
    try:
        # 执行AI规划
        result = planner.plan_trip(start_airport, end_airport, preferences, max_stops)
        
        if not result['success']:
            error_msg = f"""
            <div style='background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%); color: white; padding: 15px; border-radius: 10px; margin: 10px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.2); text-align: center; font-size: 1.2em; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
                ❌ {result['message']}
            </div>
            """
            return error_msg, ""
        
        # 格式化结果
        message = f"""
        <div style='background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); color: white; padding: 15px; border-radius: 10px; margin: 10px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.2); text-align: center; font-size: 1.2em; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
            ✅ {result['message']}
        </div>
        """
        
        # 生成路线详情HTML
        routes_html = generate_routes_html(result['routes'], result['recommendations'])
        
        return message, routes_html
        
    except Exception as e:
        error_msg = f"""
        <div style='background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%); color: white; padding: 15px; border-radius: 10px; margin: 10px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.2); text-align: center; font-size: 1.2em; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
            ❌ 规划过程中出现错误: {str(e)}
        </div>
        """
        return error_msg, ""

def generate_routes_html(routes, recommendations):
    """生成路线展示HTML"""
    if not routes:
        return """
        <div style="text-align: center; padding: 60px 20px; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 15px; border: 2px dashed #dee2e6;">
            <div style="font-size: 4em; margin-bottom: 20px;">❌</div>
            <h3 style="color: #2c3e50; margin: 0 0 15px 0; font-size: 1.5em; font-weight: 700;">暂无可用路线</h3>
            <p style="color: #495057; margin: 0; font-size: 1.1em; font-weight: 500;">请尝试调整起飞机场、目标机场或增加最大中转次数</p>
        </div>
        """
    
    html = """
    <div class="routes-container" style="max-height: 1300px; overflow-y: auto; padding: 25px; background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); border-radius: 25px; box-shadow: 0 12px 40px rgba(0,0,0,0.08); border: 1px solid rgba(102, 126, 234, 0.15); position: relative;">
        <style>
            /* 自定义滚动条样式 */
            .routes-container::-webkit-scrollbar {
                width: 8px;
            }
            .routes-container::-webkit-scrollbar-track {
                background: rgba(102, 126, 234, 0.1);
                border-radius: 10px;
            }
            .routes-container::-webkit-scrollbar-thumb {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 10px;
                transition: all 0.3s ease;
            }
            .routes-container::-webkit-scrollbar-thumb:hover {
                background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
            }
            
            /* 卡片悬停效果 */
            .route-card {
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                transform-origin: center;
            }
            .route-card:hover {
                transform: translateY(-8px) scale(1.02);
                box-shadow: 0 20px 40px rgba(0,0,0,0.15) !important;
            }
            
            /* 渐入动画 */
            .route-card {
                animation: fadeInUp 0.6s ease-out;
            }
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            /* 排名徽章动画 */
            .rank-badge {
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }
        </style>
    """
    
    # 显示推荐信息
    if recommendations:
        html += """
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 15px; margin-bottom: 25px; box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3); position: relative; overflow: hidden;">
            <div style="position: absolute; top: -50px; right: -50px; width: 100px; height: 100px; background: rgba(255,255,255,0.1); border-radius: 50%;"></div>
            <div style="position: absolute; bottom: -30px; left: -30px; width: 60px; height: 60px; background: rgba(255,255,255,0.1); border-radius: 50%;"></div>
            <h3 style="color: #ffffff; margin-top: 0; font-size: 1.6em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); position: relative; z-index: 1; font-weight: 700;">🤖 AI智能推荐</h3>
        """
        for rec in recommendations[:3]:  # 显示前3个推荐
            route_id = str(rec.get('route_id', 'N/A'))
            reason = str(rec.get('reason', '无理由'))
            html += f"""
            <div style="background: rgba(255,255,255,0.25); padding: 15px; border-radius: 10px; margin: 10px 0; backdrop-filter: blur(10px); position: relative; z-index: 1; border: 1px solid rgba(255,255,255,0.3);">
                <p style="margin: 0; color: #ffffff; font-size: 1.1em; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">
                    <strong>推荐路线 {route_id}:</strong> {reason}
                </p>
            </div>
            """
        html += "</div>"
    
    # 显示所有路线
    html += """
    <div style="text-align: center; margin-bottom: 35px; padding: 25px; background: linear-gradient(135deg, #f8f9ff 0%, #e8f4fd 100%); border-radius: 20px; border: 1px solid rgba(102, 126, 234, 0.15); box-shadow: 0 8px 25px rgba(102, 126, 234, 0.1); position: relative; overflow: hidden;">
        <div style="position: absolute; top: -20px; left: -20px; width: 40px; height: 40px; background: rgba(102, 126, 234, 0.1); border-radius: 50%;"></div>
        <div style="position: absolute; bottom: -15px; right: -15px; width: 30px; height: 30px; background: rgba(118, 75, 162, 0.1); border-radius: 50%;"></div>
        <h3 style="color: #1a1a1a; font-size: 2.2em; margin: 0; font-weight: 800; text-shadow: 1px 1px 2px rgba(0,0,0,0.1); background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; position: relative; z-index: 1;">📋 智能路线分析</h3>
        <p style="color: #4a5568; margin: 15px 0 0 0; font-size: 1.3em; font-weight: 600; position: relative; z-index: 1;">基于AI算法优化的航班路线推荐</p>
    </div>
    """
    
    for i, route in enumerate(routes[:10]):  # 限制显示前10条
        route_summary = planner.get_route_summary(route)
        
        # 根据路线排名选择不同的样式
        if i < 3:
            # 前3名推荐路线 - 更突出的样式
            if i == 0:
                card_style = "background: linear-gradient(135deg, #fff9c4 0%, #fef3c7 100%); border: 4px solid #f59e0b; box-shadow: 0 12px 35px rgba(245, 158, 11, 0.25);"
                rank_badge = f'<div class="rank-badge" style="position: absolute; top: -12px; right: 25px; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 10px 18px; border-radius: 25px; font-weight: bold; font-size: 1em; box-shadow: 0 6px 20px rgba(245, 158, 11, 0.5); z-index: 10;">🥇 金牌路线</div>'
            elif i == 1:
                card_style = "background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%); border: 4px solid #6b7280; box-shadow: 0 12px 35px rgba(107, 114, 128, 0.25);"
                rank_badge = f'<div class="rank-badge" style="position: absolute; top: -12px; right: 25px; background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%); color: white; padding: 10px 18px; border-radius: 25px; font-weight: bold; font-size: 1em; box-shadow: 0 6px 20px rgba(107, 114, 128, 0.5); z-index: 10;">🥈 银牌路线</div>'
            else:
                card_style = "background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border: 4px solid #d97706; box-shadow: 0 12px 35px rgba(217, 119, 6, 0.25);"
                rank_badge = f'<div class="rank-badge" style="position: absolute; top: -12px; right: 25px; background: linear-gradient(135deg, #d97706 0%, #b45309 100%); color: white; padding: 10px 18px; border-radius: 25px; font-weight: bold; font-size: 1em; box-shadow: 0 6px 20px rgba(217, 119, 6, 0.5); z-index: 10;">🥉 铜牌路线</div>'
        else:
            # 其他路线 - 更现代的样式
            card_style = f"background: linear-gradient(135deg, {'#ffffff' if i % 2 == 0 else '#f8fafc'} 0%, {'#f8f9fa' if i % 2 == 0 else '#f1f5f9'} 100%); border: 2px solid #e2e8f0; box-shadow: 0 8px 25px rgba(0,0,0,0.06);"
            rank_badge = ""
        
        html += f"""
        <div class="route-card" style="{card_style} border-radius: 25px; padding: 35px; margin-bottom: 35px; position: relative; cursor: pointer; backdrop-filter: blur(10px);">
            {rank_badge}
            <div style="text-align: center; margin-bottom: 30px;">
                <h4 style="color: #1a1a1a; margin: 0; font-size: 2em; font-weight: 800; text-shadow: 2px 2px 4px rgba(0,0,0,0.1); background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; letter-spacing: 0.5px;">{route[0]['起飞机场']} → {route[-1]['降落机场']}</h4>
                <div style="margin-top: 10px; height: 3px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 2px; width: 60px; margin-left: auto; margin-right: auto;"></div>
            </div>
            
            <div style="display: flex; flex-wrap: wrap; gap: 25px; margin-bottom: 30px; justify-content: center;">
                <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); color: #0d47a1; padding: 15px 25px; border-radius: 30px; font-weight: 700; font-size: 1.2em; border: 2px solid #90caf9; box-shadow: 0 6px 20px rgba(13, 71, 161, 0.25); display: flex; align-items: center; gap: 10px; transition: all 0.3s ease; cursor: pointer;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                    <span style="font-size: 1.4em;">🔄</span> 中转 {route_summary['stops']} 次
                </div>
                <div style="background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%); color: #4a148c; padding: 15px 25px; border-radius: 30px; font-weight: 700; font-size: 1.2em; border: 2px solid #ce93d8; box-shadow: 0 6px 20px rgba(74, 20, 140, 0.25); display: flex; align-items: center; gap: 10px; transition: all 0.3s ease; cursor: pointer;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                    <span style="font-size: 1.4em;">✈️</span> {route_summary['total_flights']} 个航班
                </div>
                <div style="background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%); color: #1b5e20; padding: 15px 25px; border-radius: 30px; font-weight: 700; font-size: 1.2em; border: 2px solid #a5d6a7; box-shadow: 0 6px 20px rgba(27, 94, 32, 0.25); display: flex; align-items: center; gap: 10px; transition: all 0.3s ease; cursor: pointer;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                    <span style="font-size: 1.4em;">🏢</span> {route_summary['total_airports']} 个机场
                </div>
            </div>
            
            <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 30px; border-radius: 20px; margin-bottom: 25px; border: 2px solid #e2e8f0; box-shadow: 0 8px 25px rgba(0,0,0,0.08); position: relative; overflow: hidden;">
                <div style="position: absolute; top: -10px; left: -10px; width: 20px; height: 20px; background: rgba(102, 126, 234, 0.1); border-radius: 50%;"></div>
                <div style="position: absolute; bottom: -5px; right: -5px; width: 15px; height: 15px; background: rgba(118, 75, 162, 0.1); border-radius: 50%;"></div>
                <h5 style="color: #1a1a1a; margin: 0 0 25px 0; font-size: 1.4em; font-weight: 700; text-shadow: 1px 1px 2px rgba(0,0,0,0.1); text-align: center; position: relative; z-index: 1;">✈️ 航班详情</h5>
                <div style="display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; position: relative; z-index: 1;">"""
        
        for j, flight in enumerate(route):
            # 根据航班在路线中的位置使用不同的颜色和图标
            if j == 0:
                flight_style = "background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); color: white; border: 2px solid #2e7d32;"
                icon = "🛫"
            elif j == len(route) - 1:
                flight_style = "background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); color: white; border: 2px solid #e65100;"
                icon = "🛬"
            else:
                flight_style = "background: linear-gradient(135deg, #2196F3 0%, #1976d2 100%); color: white; border: 2px solid #0d47a1;"
                icon = "🔄"
            
            arrow = " → " if j < len(route) - 1 else ""
            html += f"""
                <div style="{flight_style} padding: 18px 25px; border-radius: 35px; font-weight: 600; font-size: 1.1em; box-shadow: 0 8px 25px rgba(0,0,0,0.25); display: inline-flex; align-items: center; gap: 15px; text-shadow: 1px 1px 2px rgba(0,0,0,0.3); min-width: 220px; transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); cursor: pointer;" onmouseover="this.style.transform='translateY(-3px) scale(1.02)'" onmouseout="this.style.transform='translateY(0) scale(1)'">
                    <span style="font-size: 1.6em;">{icon}</span>
                    <div style="flex: 1;">
                        <div style="font-weight: 700; font-size: 1.3em; text-shadow: 1px 1px 2px rgba(0,0,0,0.3); margin-bottom: 6px;">{flight['航班号']}</div>
                        <div style="font-size: 1.1em; opacity: 0.95; text-shadow: 1px 1px 2px rgba(0,0,0,0.2); margin-bottom: 4px;">{flight['起飞机场']} → {flight['降落机场']}</div>
                        <div style="font-size: 1em; opacity: 0.9; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">{flight['起飞时间']} | {beautify_schedule(flight['班期'])}</div>
                    </div>
                </div>{arrow}"""
        
        html += """
                </div>
            </div>
        </div>"""
    
    html += """
        </div>
        
        <!-- 滚动到顶部按钮 -->
        <div style="position: sticky; bottom: 20px; text-align: center; margin-top: 20px;">
            <button onclick="document.querySelector('.routes-container').scrollTo({top: 0, behavior: 'smooth'})" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 12px 20px; border-radius: 25px; font-size: 1em; font-weight: 600; cursor: pointer; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3); transition: all 0.3s ease;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(102, 126, 234, 0.4)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(102, 126, 234, 0.3)'">
                ⬆️ 回到顶部
            </button>
        </div>
    </div>
    """
    return html

with gr.Blocks(css=css, theme=gr.themes.Soft()) as demo:
    # 在应用级别加载全局资源
    gr.HTML(get_app_global_resources_html())
    gr.HTML("""
    <div class="main-header">
        <h1 style="font-size: 2.8em; margin: 0 0 12px 0; background: linear-gradient(135deg, #ff0000, #ff8000, #ffff00, #80ff00, #00ff00, #00ff80, #00ffff, #0080ff, #0000ff, #8000ff, #ff00ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; text-shadow: 2px 2px 4px rgba(0,0,0,0.1); font-weight: 800;">✈️ 海航随心飞AI规划</h1>
        <p style="font-size: 1.4em; margin: 0; background: linear-gradient(135deg, #ff5252, #ff793f, #ffb142, #ffd700, #55acee, #34ace0, #22a6b3); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-weight: 600; letter-spacing: 1px;">航班搜索与路线可视化</p>
    </div>
    """)
    
    # 主要功能切换页面
    with gr.Tabs() as main_tabs:
        with gr.Tab("🤖 AI智能规划"):
            
            # AI规划主要区域 - 参考航班查询页面的简洁设计
            with gr.Row():
                # 左侧：简洁的输入控制面板
                with gr.Column(scale=1):
                    gr.Markdown("### 🤖 AI智能规划")
                    
                    # 起飞机场
                    ai_start_airport = gr.Dropdown(
                        choices=departure_airports,
                        label="起飞机场",
                        allow_custom_value=True,
                        info="选择您的出发机场",
                        value="上海浦东"
                    )
                    
                    # 目标机场
                    ai_end_airport = gr.Dropdown(
                        choices=arrival_airports,
                        label="目标机场", 
                        allow_custom_value=True,
                        info="选择您的目标机场",
                        value="成都天府"
                    )
                    
                    # 智能偏好设置
                    ai_preferences = gr.Textbox(
                        label="飞行偏好描述",
                        placeholder="例如：希望中转次数少、时间最短、避开某些机场、优先直飞等",
                        lines=4,
                        info="详细描述您的飞行偏好，AI将据此进行智能优化"
                    )
                    
                    # 中转次数设置
                    ai_max_stops = gr.Slider(
                        minimum=0,
                        maximum=3,
                        step=1,
                        value=2,
                        label="最大中转次数",
                        info="设置允许的最大中转次数（0=直飞，3=最多3次中转）"
                    )
                    
                    # 主要操作按钮
                    ai_plan_button = gr.Button(
                        "🤖 启动AI规划", 
                        variant="primary", 
                        size="lg",
                        interactive=ai_available
                    )
                    
                    # 辅助按钮
                    with gr.Row():
                        ai_clear_button = gr.Button(
                            "🗑️ 重置参数", 
                            variant="secondary"
                        )
                        
                        help_button = gr.Button(
                            "❓ 使用帮助", 
                            variant="secondary"
                        )
                        
                
                # 右侧：结果展示区域
                with gr.Column(scale=2):
                    # 结果状态区域
                    ai_result_message = gr.HTML("", visible=True)
                    
                    # 路线详情展示
                    ai_routes_html = gr.HTML(
                        value="""
                        <div style="text-align: center; padding: 60px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; position: relative; overflow: hidden; box-shadow: 0 10px 40px rgba(102, 126, 234, 0.2);">
                            <div style="position: absolute; top: -50px; right: -50px; width: 100px; height: 100px; background: rgba(255,255,255,0.1); border-radius: 50%;"></div>
                            <div style="position: absolute; bottom: -30px; left: -30px; width: 60px; height: 60px; background: rgba(255,255,255,0.1); border-radius: 50%;"></div>
                            <div style="position: relative; z-index: 1;">
                                <div style="font-size: 6em; margin-bottom: 30px; animation: float 3s ease-in-out infinite;">🤖</div>
                                <h3 style="color: white; margin: 0 0 20px 0; font-size: 2.2em; font-weight: 800; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">AI智能规划引擎</h3>
                                <p style="color: rgba(255,255,255,0.9); margin: 0 0 30px 0; font-size: 1.3em; font-weight: 500; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">基于深度学习的航班路线优化</p>
                                <div style="background: rgba(255,255,255,0.2); padding: 20px; border-radius: 15px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.3);">
                                    <p style="color: white; margin: 0; font-size: 1.1em; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">✨ 请配置左侧参数，然后点击"启动AI规划"开始智能分析</p>
                                </div>
                            </div>
                            <style>
                                @keyframes float {
                                    0%, 100% { transform: translateY(0px); }
                                    50% { transform: translateY(-10px); }
                                }
                            </style>
                        </div>
                        """,
                        label="",
                        show_label=False
                    )
                    
        
        with gr.Tab("🔍 航班查询"):
            # 航班查询功能
            gr.HTML("""
            <div style="text-align: center; padding: 30px 20px; background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); border-radius: 15px; margin-bottom: 25px; box-shadow: 0 8px 25px rgba(76, 175, 80, 0.2);">
                <h2 style="color: white; font-size: 2.2em; margin: 0 0 15px 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); font-weight: 700;">🔍 航班查询</h2>
                <p style="color: rgba(255,255,255,0.9); font-size: 1.2em; margin: 0; font-weight: 500;">快速搜索和浏览航班信息</p>
            </div>
            """)
            
            # 航班查询结果
            output = gr.Dataframe(
                headers=["航班号", "起飞机场", "降落机场", "起飞时间", "班期", "适用产品"],
                label="",
                interactive=True,
                wrap=True,
                datatype=["str", "str", "str", "str", "str", "str"]
            )
            
            # 航班查询和地图展示
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 🔍 航班搜索")
                    with gr.Row():
                        with gr.Column(scale=10):
                            departure_airport = gr.Dropdown(
                                choices=departure_airports,
                                label="起飞机场",
                                allow_custom_value=True,
                                info="选择或输入起飞机场（可选）",
                                value="成都天府"
                            )
                        with gr.Column(scale=1, min_width=40):
                            dep_clear_btn = gr.Button("✕", size="sm", variant="secondary")
                    
                    # Arrival airport with clear button
                    with gr.Row():
                        with gr.Column(scale=10):
                            arrival_airport = gr.Dropdown(
                                choices=arrival_airports,
                                label="降落机场",
                                allow_custom_value=True,
                                info="选择或输入降落机场（可选）",
                                value=None
                            )
                        with gr.Column(scale=1, min_width=40):
                            arr_clear_btn = gr.Button("✕", size="sm", variant="secondary")
                    
                    with gr.Row():
                        product_category = gr.Dropdown(
                            choices=["666", "2666", "666/2666"],
                            label="会员类型（选填）",
                            allow_custom_value=True,
                            info="选择会员类型",
                            value="666/2666"
                        )

                    with gr.Row():
                        submit_button = gr.Button("🔍 查询航班", variant="primary", size="lg")
                        clear_button = gr.Button("🗑️ 清空", variant="secondary")
                    gr.Markdown("""
                        > 💡 **搜索提示**: 
                        > - 至少选择一个机场（起飞或降落）
                        > - 可以只选择起飞机场查看所有从该机场出发的航班
                        > - 可以只选择降落机场查看所有到达该机场的航班
                        > - 也可以同时选择两个机场查看特定航线
                        > - 会员类型为选填项
                        """)
                    
                with gr.Column(scale=2):
                    with gr.Tabs() as query_tabs:
                        with gr.Tab("📊 统计分析"):
                            with gr.Row():
                                # 显示总体统计信息
                                unique_dep = set(flight['起飞机场'] for flight in flights)
                                unique_arr = set(flight['降落机场'] for flight in flights)
                                all_airports = unique_dep.union(unique_arr)
                                
                                gr.Markdown(f"""
                                ### 机场统计: 数据更新至2025年9月30日，2025年冬春航季（2025年10月26日-2025年12月25日）
                                - 总机场数量：{len(all_airports)} 个    
                                - 总航班数量：{len(flights)} 个
                                """)
                            
                            with gr.Tabs():
                                with gr.Tab("地理分布"):
                                    airport_map = gr.HTML(
                                        value=get_cached_tab_map("distribution", create_airport_distribution_map),
                                        label="机场分布",
                                        show_label=True
                                    )
                                with gr.Tab("频次分布"):
                                    bubble_output = gr.Plot(
                                        value=get_cached_tab_map("bubble", create_airport_bubble_chart, None),
                                        label="机场航班频次分布",
                                        show_label=True
                                    )

                                with gr.Tab("航线网络"):
                                    route_output = gr.HTML(
                                        value=get_cached_tab_map("route_network", create_route_network_chart, None),
                                        label="航线网络分布",
                                        show_label=True
                                    )
                                with gr.Tab("频次统计"):
                                    stats_output = gr.Plot(
                                        value=get_cached_tab_map("stats", create_stats_chart, None),
                                        label="机场航班频次统计",
                                        show_label=True
                                    )
                        
                        with gr.Tab("🗺️ 航班路线图"):
                            map_output = gr.HTML(
                                value=create_flight_map(flights[:100]),  # 初始显示前100个航班
                                label="航班地图",
                                show_label=True
                            )
                        with gr.Tab("💝 赞赏支持"):
                            gr.HTML(f"""
                            <div style="text-align: center; padding: 20px; background: #f8f9fa; border-radius: 10px;">
                                <h2 style="color: #e91e63; font-size: 2.2em; margin-bottom: 20px; text-shadow: 2px 2px 4px rgba(0,0,0,0.1); font-weight: bold;">💝 感谢您的支持</h2>
                                <p style="font-size: 16px; color: #333; max-width: 800px; margin: 0 auto 20px;">
                                    ～最近沉迷"飞飞乐"无法自拔，但每次规划航班都感觉像在解高数题。
                                    目前还在"从能用到好用"的进化阶段，欢迎来体验、吐槽、提建议——毕竟，一个人的懒，靠一群人拯救才显得高级！
                                </p>
                                <div style="display: flex; flex-wrap: wrap; gap: 20px; justify-content: center;">
                                    <div style="width: 200px; text-align: center;">
                                        <div style="width: 200px; height: 200px; display: flex; align-items: center; justify-content: center; border: 1px solid #ddd; border-radius: 10px;">
                                            <img src="{alipay_base64}" alt="赞赏码1" style="max-width: 100%; max-height: 100%; object-fit: contain;">
                                        </div>
                                        <p style="margin-top: 10px; font-weight: bold;">支付宝赞赏</p>
                                    </div>
                                    <div style="width: 200px; text-align: center;">
                                        <div style="width: 200px; height: 200px; display: flex; align-items: center; justify-content: center; border: 1px solid #ddd; border-radius: 10px;">
                                            <img src="{wechat_base64}" alt="赞赏码2" style="max-width: 100%; max-height: 100%; object-fit: contain;">
                                        </div>
                                        <p style="margin-top: 10px; font-weight: bold;">微信赞赏</p>
                                    </div>
                                </div>
                                <div style="margin-top: 20px; padding: 15px; background: #e3f2fd; border-radius: 8px; display: inline-block;">
                                    <p style="margin: 0; font-size: 16px;">
                                        <strong>📧 联系：</strong>
                                        <a href="mailto:openchatcl@outlook.com" style="color: #1976d2; text-decoration: none;">openchatcl@outlook.com</a>
                                    </p>
                                    <p style="margin: 5px 0 0 0; font-size: 14px; color: #666;">
                                        如有功能需求或建议，欢迎通过邮箱联系
                                    </p>
                                </div>
                                <p style="margin-top: 20px; font-style: italic; color: #666;">
                                    💖 每一份支持，无论大小，都是对我懒的拯救。感谢您的赞赏！
                                </p>
                            </div>
                            """)
    
    # 事件绑定
    submit_button.click(
        update_all,
        inputs=[departure_airport, arrival_airport, product_category],
        outputs=[output, map_output, stats_output]
    )
    
    clear_button.click(
        clear_all,
        outputs=[departure_airport, arrival_airport, product_category, output, map_output, stats_output]
    )

    dep_clear_btn.click(
        clear_departure,
        outputs=[departure_airport]
    )

    arr_clear_btn.click(
        clear_arrival,
        outputs=[arrival_airport]
    )
    
    # AI规划功能事件绑定
    ai_plan_button.click(
        ai_plan_route,
        inputs=[ai_start_airport, ai_end_airport, ai_preferences, ai_max_stops],
        outputs=[ai_result_message, ai_routes_html]
    )
    
    ai_clear_button.click(
        lambda: (None, None, "", "", ""),
        outputs=[ai_start_airport, ai_end_airport, ai_preferences, ai_result_message, ai_routes_html]
    )
    
    # 帮助按钮事件
    def show_help():
        help_html = """
        <div style="background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%); padding: 25px; border-radius: 15px; margin: 20px 0; border-left: 4px solid #2196F3;">
            <h3 style="color: #1a1a1a; margin-top: 0; font-size: 1.4em; font-weight: 700;">❓ AI智能规划使用帮助</h3>
            <div style="margin: 15px 0;">
                <h4 style="color: #2c3e50; margin: 10px 0 5px 0; font-size: 1.1em;">📍 机场选择</h4>
                <p style="color: #495057; margin: 0 0 15px 0; font-size: 0.95em;">• 选择起飞机场和目标机场<br>• 支持搜索和自定义输入<br>• 至少需要选择一个机场</p>
                
                <h4 style="color: #2c3e50; margin: 10px 0 5px 0; font-size: 1.1em;">⚙️ 智能偏好</h4>
                <p style="color: #495057; margin: 0 0 15px 0; font-size: 0.95em;">• 详细描述您的飞行需求<br>• 例如：中转次数少、时间最短、避开某些机场<br>• AI将根据您的偏好进行智能优化</p>
                
                <h4 style="color: #2c3e50; margin: 10px 0 5px 0; font-size: 1.1em;">🚀 开始规划</h4>
                <p style="color: #495057; margin: 0 0 15px 0; font-size: 0.95em;">• 点击"启动AI规划"开始分析<br>• AI将为您推荐最优路线<br>• 支持查看详细航班信息</p>
            </div>
        </div>
        """
        return help_html
    
    help_button.click(
        show_help,
        outputs=[ai_result_message]
    )

if __name__ == "__main__":

    
    # 启动 Gradio
    demo.launch(
        server_name="0.0.0.0",
        server_port=7171,
        share=False,
        show_error=True,
        allowed_paths=["data"]
    )
