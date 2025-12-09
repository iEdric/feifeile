#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用级资源管理器
直接在Gradio应用中实现全局资源管理
"""

import uuid
from typing import Dict, Set
from cdn_replacer import optimize_html_for_china

class AppResourceManager:
    """应用级资源管理器"""
    
    def __init__(self):
        self._global_resources_loaded = False
        self._global_resources_html = None
        self._loaded_maps = set()
        
    def get_global_resources_html(self) -> str:
        """获取全局资源HTML（只生成一次）"""
        if self._global_resources_html is not None:
            return self._global_resources_html
            
        # 全局资源ID
        global_id = "app_global_resources"
        
        # 共享的CDN资源（使用中国可访问的CDN）
        resources = [
            ('https://cdn.bootcdn.net/ajax/libs/leaflet/1.9.3/leaflet.js', 'script'),
            ('https://cdn.bootcdn.net/ajax/libs/leaflet/1.9.3/leaflet.css', 'style'),
            ('https://cdn.bootcdn.net/ajax/libs/jquery/3.7.1/jquery.min.js', 'script'),
            ('https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/5.2.2/js/bootstrap.bundle.min.js', 'script'),
            ('https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/5.2.2/css/bootstrap.min.css', 'style'),
            ('https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.min.js', 'script'),
            ('https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.css', 'style'),
            ('https://cdn.bootcdn.net/ajax/libs/bootstrap/3.0.0/css/bootstrap-glyphicons.css', 'style')
        ]
        
        # 生成资源HTML
        resource_html = []
        for url, resource_type in resources:
            if resource_type == 'script':
                resource_html.append(f'<script src="{url}" defer></script>')
            elif resource_type == 'style':
                resource_html.append(f'<link rel="stylesheet" href="{url}">')
            else:
                resource_html.append(f'<link rel="stylesheet" href="{url}">')
        
        # 生成全局资源管理脚本
        script_html = f"""
        <script>
        (function() {{
            // 应用级资源管理器
            window.AppResourceManager = window.AppResourceManager || {{
                loaded: false,
                loading: false,
                callbacks: [],
                loadedMaps: new Set(),
                resourceCount: 0,
                loadedResources: new Set(),
                initializedMaps: new Set(),
                executedScripts: new Set()
            }};
            
            // 检查所有资源是否已加载
            function checkAllResourcesLoaded() {{
                let loadedCount = 0;
                
                // 检查Leaflet
                if (window.L) {{
                    loadedCount++;
                    window.AppResourceManager.loadedResources.add('leaflet');
                }}
                
                // 检查jQuery
                if (window.jQuery || window.$) {{
                    loadedCount++;
                    window.AppResourceManager.loadedResources.add('jquery');
                }}
                
                // 检查Bootstrap
                if (window.bootstrap) {{
                    loadedCount++;
                    window.AppResourceManager.loadedResources.add('bootstrap');
                }}
                
                // 检查Awesome Markers
                if (window.L && L.AwesomeMarkers) {{
                    loadedCount++;
                    window.AppResourceManager.loadedResources.add('awesome-markers');
                }}
                
                // 检查CSS资源
                const cssResources = document.querySelectorAll('link[href*="leaflet"], link[href*="bootstrap"], link[href*="awesome-markers"]');
                loadedCount += Math.min(cssResources.length, 4);
                
                return loadedCount >= 4; // 至少需要4个核心资源
            }}
            
            // 等待所有资源加载完成
            function waitForAllResources(callback) {{
                if (window.AppResourceManager.loaded || checkAllResourcesLoaded()) {{
                    window.AppResourceManager.loaded = true;
                    if (callback) callback();
                    return;
                }}
                
                // 添加到回调队列
                if (callback) {{
                    window.AppResourceManager.callbacks.push(callback);
                }}
                
                // 如果正在加载，直接返回
                if (window.AppResourceManager.loading) {{
                    return;
                }}
                
                // 开始加载
                window.AppResourceManager.loading = true;
                
                // 设置检查间隔
                const checkInterval = setInterval(() => {{
                    if (checkAllResourcesLoaded()) {{
                        window.AppResourceManager.loaded = true;
                        window.AppResourceManager.loading = false;
                        clearInterval(checkInterval);
                        
                        // 执行所有回调
                        window.AppResourceManager.callbacks.forEach(cb => {{
                            try {{
                                cb();
                            }} catch (e) {{
                                console.warn('资源加载回调执行失败:', e);
                            }}
                        }});
                        window.AppResourceManager.callbacks = [];
                    }}
                }}, 100);
                
                // 设置超时
                setTimeout(() => {{
                    clearInterval(checkInterval);
                    window.AppResourceManager.loaded = true;
                    window.AppResourceManager.loading = false;
                    window.AppResourceManager.callbacks.forEach(cb => {{
                        try {{
                            cb();
                        }} catch (e) {{
                            console.warn('资源加载回调执行失败:', e);
                        }}
                    }});
                    window.AppResourceManager.callbacks = [];
                }}, 5000);
            }}
            
            // 注册地图
            function registerMap(mapId) {{
                window.AppResourceManager.loadedMaps.add(mapId);
                console.log('注册地图:', mapId, '总地图数:', window.AppResourceManager.loadedMaps.size);
            }}
            
            // 检查地图是否已注册
            function isMapRegistered(mapId) {{
                return window.AppResourceManager.loadedMaps.has(mapId);
            }}
            
            // 防止重复加载资源的函数
            function preventDuplicateResourceLoading() {{
                // 拦截script标签的创建
                const originalCreateElement = document.createElement;
                document.createElement = function(tagName) {{
                    const element = originalCreateElement.call(this, tagName);
                    
                    if (tagName.toLowerCase() === 'script' && element.src) {{
                        // 检查是否已经加载过这个资源
                        if (element.src.includes('leaflet') && window.AppResourceManager.loadedResources.has('leaflet') ||
                            element.src.includes('jquery') && window.AppResourceManager.loadedResources.has('jquery') ||
                            element.src.includes('bootstrap') && window.AppResourceManager.loadedResources.has('bootstrap') ||
                            element.src.includes('awesome-markers') && window.AppResourceManager.loadedResources.has('awesome-markers')) {{
                            console.log('阻止重复加载资源:', element.src);
                            return document.createElement('div'); // 返回空div而不是script
                        }}
                    }}
                    
                    return element;
                }};
                
                // 拦截内联JavaScript的执行
                const originalAppendChild = Node.prototype.appendChild;
                Node.prototype.appendChild = function(child) {{
                    if (child.tagName === 'SCRIPT' && child.textContent) {{
                        // 检查是否已经执行过这个脚本
                        const scriptHash = btoa(child.textContent).substring(0, 16);
                        if (window.AppResourceManager.executedScripts.has(scriptHash)) {{
                            console.log('阻止重复执行脚本:', scriptHash);
                            return child; // 不执行，直接返回
                        }}
                        window.AppResourceManager.executedScripts.add(scriptHash);
                    }}
                    return originalAppendChild.call(this, child);
                }};
                
                // 拦截link标签的创建
                const originalCreateElementLink = document.createElement;
                document.createElement = function(tagName) {{
                    const element = originalCreateElementLink.call(this, tagName);
                    
                    if (tagName.toLowerCase() === 'link' && element.href) {{
                        // 检查是否已经加载过这个CSS资源
                        if (element.href.includes('leaflet') && window.AppResourceManager.loadedResources.has('leaflet') ||
                            element.href.includes('bootstrap') && window.AppResourceManager.loadedResources.has('bootstrap') ||
                            element.href.includes('awesome-markers') && window.AppResourceManager.loadedResources.has('awesome-markers')) {{
                            console.log('阻止重复加载CSS资源:', element.href);
                            return document.createElement('div'); // 返回空div而不是link
                        }}
                    }}
                    
                    return element;
                }};
                
                // 拦截动态添加的script和link标签
                const observer = new MutationObserver(function(mutations) {{
                    mutations.forEach(function(mutation) {{
                        mutation.addedNodes.forEach(function(node) {{
                            if (node.nodeType === 1) {{ // Element node
                                if (node.tagName === 'SCRIPT' && node.src) {{
                                    if (node.src.includes('leaflet') && window.AppResourceManager.loadedResources.has('leaflet') ||
                                        node.src.includes('jquery') && window.AppResourceManager.loadedResources.has('jquery') ||
                                        node.src.includes('bootstrap') && window.AppResourceManager.loadedResources.has('bootstrap') ||
                                        node.src.includes('awesome-markers') && window.AppResourceManager.loadedResources.has('awesome-markers')) {{
                                        console.log('阻止重复加载动态资源:', node.src);
                                        node.remove();
                                    }}
                                }}
                                if (node.tagName === 'LINK' && node.href) {{
                                    if (node.href.includes('leaflet') && window.AppResourceManager.loadedResources.has('leaflet') ||
                                        node.href.includes('bootstrap') && window.AppResourceManager.loadedResources.has('bootstrap') ||
                                        node.href.includes('awesome-markers') && window.AppResourceManager.loadedResources.has('awesome-markers')) {{
                                        console.log('阻止重复加载动态CSS资源:', node.href);
                                        node.remove();
                                    }}
                                }}
                            }}
                        }});
                    }});
                }});
                
                // 开始观察DOM变化
                observer.observe(document, {{
                    childList: true,
                    subtree: true
                }});
            }}
            
            // 导出全局函数
            window.waitForAppResources = waitForAllResources;
            window.registerAppMap = registerMap;
            window.isAppMapRegistered = isMapRegistered;
            window.preventDuplicateResourceLoading = preventDuplicateResourceLoading;
            
            // 立即开始检查资源
            waitForAllResources();
            
            // 初始化防重复加载机制
            preventDuplicateResourceLoading();
        }})();
        </script>
        """
        
        self._global_resources_html = '\n'.join(resource_html) + script_html
        return self._global_resources_html
    
    def create_optimized_map_html(self, map_obj, map_type="map", width="100%", height="500px") -> str:
        """
        创建优化的地图HTML，使用全局资源
        
        Args:
            map_obj: Folium地图对象
            map_type: 地图类型（用于生成唯一ID）
            width: 地图宽度
            height: 地图高度
        
        Returns:
            优化后的地图HTML字符串
        """
        # 生成固定ID（基于地图类型）
        map_id = f"app_map_{map_type}"
        
        # 获取原始地图HTML
        map_html = map_obj._repr_html_()
        
        # 处理信任相关问题（简化版本）
        import re
        map_html = re.sub(r'data-notebook-trusted="[^"]*"', '', map_html)
        map_html = re.sub(r'data-notebook-trusted', '', map_html)
        
        # 优化CDN资源为中国可访问的CDN
        map_html = optimize_html_for_china(map_html)
        
        # 移除重复的资源引用
        map_html = self._remove_duplicate_resources(map_html)
        
        # 创建优化的HTML结构
        optimized_html = f"""
        <div id="{map_id}" class="app-map-container" 
             style="width: {width}; height: {height}; border: 1px solid #ddd; border-radius: 5px; position: relative; overflow: hidden;">
            {map_html}
        </div>
        
        <script>
        // 地图初始化脚本
        (function() {{
            const mapContainer = document.getElementById('{map_id}');
            if (!mapContainer) return;
            
            // 检查地图是否已经初始化
            if (window.AppResourceManager && window.AppResourceManager.initializedMaps) {{
                if (window.AppResourceManager.initializedMaps.has('{map_id}')) {{
                    console.log('地图 {map_id} 已经初始化，跳过重复初始化');
                    return;
                }}
            }}
            
            // 注册地图
            if (window.registerAppMap) {{
                window.registerAppMap('{map_id}');
            }}
            
            // 等待全局资源加载完成
            if (window.waitForAppResources) {{
                window.waitForAppResources(() => {{
                    console.log('地图 {map_id} 应用资源加载完成');
                    
                    // 标记地图已初始化
                    if (window.AppResourceManager) {{
                        if (!window.AppResourceManager.initializedMaps) {{
                            window.AppResourceManager.initializedMaps = new Set();
                        }}
                        window.AppResourceManager.initializedMaps.add('{map_id}');
                    }}
                }});
            }}
        }})();
        </script>
        
        <style>
        .app-map-container {{
            position: relative;
            overflow: hidden;
        }}
        
        .app-map-container iframe {{
            border: none !important;
            width: 100% !important;
            height: 100% !important;
        }}
        </style>
        """
        
        # 标记资源已加载
        self._global_resources_loaded = True
        self._loaded_maps.add(map_id)
        
        return optimized_html
    
    def _remove_duplicate_resources(self, html_content: str) -> str:
        """移除所有资源引用，因为全局资源已在应用级别加载"""
        import re
        
        # 要移除的所有资源模式（完全移除，因为全局资源已加载）
        resource_patterns = [
            r'<script[^>]*src=["\'][^"\']*leaflet[^"\']*["\'][^>]*></script>',
            r'<link[^>]*href=["\'][^"\']*leaflet[^"\']*["\'][^>]*>',
            r'<script[^>]*src=["\'][^"\']*jquery[^"\']*["\'][^>]*></script>',
            r'<script[^>]*src=["\'][^"\']*bootstrap[^"\']*["\'][^>]*></script>',
            r'<link[^>]*href=["\'][^"\']*bootstrap[^"\']*["\'][^>]*>',
            r'<script[^>]*src=["\'][^"\']*awesome-markers[^"\']*["\'][^>]*></script>',
            r'<link[^>]*href=["\'][^"\']*awesome-markers[^"\']*["\'][^>]*>',
            r'<link[^>]*href=["\'][^"\']*bootstrap-glyphicons[^"\']*["\'][^>]*>'
        ]
        
        # 移除所有资源引用
        for pattern in resource_patterns:
            html_content = re.sub(pattern, '', html_content, flags=re.IGNORECASE)
        
        return html_content

# 全局应用资源管理器实例
_app_resource_manager = AppResourceManager()

def get_app_resource_manager() -> AppResourceManager:
    """获取应用资源管理器实例"""
    return _app_resource_manager

def create_optimized_map_html_app(map_obj, map_type="map", width="100%", height="500px") -> str:
    """
    创建优化的地图HTML，使用应用级资源管理
    
    Args:
        map_obj: Folium地图对象
        map_type: 地图类型
        width: 地图宽度
        height: 地图高度
    
    Returns:
        优化后的地图HTML字符串
    """
    # 创建地图HTML（不包含全局资源，因为全局资源在应用级别加载）
    return _app_resource_manager.create_optimized_map_html(map_obj, map_type, width, height)

def get_app_global_resources_html() -> str:
    """获取应用全局资源HTML"""
    return _app_resource_manager.get_global_resources_html()
