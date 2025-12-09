#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CDN替换工具
将国外CDN替换为中国可访问的CDN或本地资源
"""

import re
from typing import Dict, List, Tuple

# 中国可访问的CDN映射
CHINA_CDN_MAPPING = {
    # Leaflet相关
    'https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js': 'https://cdn.bootcdn.net/ajax/libs/leaflet/1.9.3/leaflet.js',
    'https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.css': 'https://cdn.bootcdn.net/ajax/libs/leaflet/1.9.3/leaflet.css',
    'https://unpkg.com/leaflet@1.9.3/dist/leaflet.js': 'https://cdn.bootcdn.net/ajax/libs/leaflet/1.9.3/leaflet.js',
    'https://unpkg.com/leaflet@1.9.3/dist/leaflet.css': 'https://cdn.bootcdn.net/ajax/libs/leaflet/1.9.3/leaflet.css',
    
    # jQuery相关
    'https://code.jquery.com/jquery-3.7.1.min.js': 'https://cdn.bootcdn.net/ajax/libs/jquery/3.7.1/jquery.min.js',
    
    # Bootstrap相关
    'https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/js/bootstrap.bundle.min.js': 'https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/5.2.2/js/bootstrap.bundle.min.js',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css': 'https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/5.2.2/css/bootstrap.min.css',
    'https://netdna.bootstrapcdn.com/bootstrap/3.0.0/css/bootstrap-glyphicons.css': 'https://cdn.bootcdn.net/ajax/libs/bootstrap/3.0.0/css/bootstrap-glyphicons.css',
    
    # FontAwesome相关
    'https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.2.0/css/all.min.css': 'https://cdn.bootcdn.net/ajax/libs/font-awesome/6.2.0/css/all.min.css',
    
    # Leaflet插件相关
    'https://cdn.bootcdn.net/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.min.js': 'https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.min.js',
    'https://cdn.bootcdn.net/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.css': 'https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.css',
    
    # Folium特定资源
    'https://cdn.jsdelivr.net/gh/python-visualization/folium/folium/templates/leaflet.awesome.rotate.min.css': 'https://unpkg.com/leaflet.awesome.rotate@0.0.1/leaflet.awesome.rotate.min.css',
}

# 备用CDN映射（如果主要CDN不可用）
BACKUP_CDN_MAPPING = {
    # 使用国内CDN作为备用
    'https://unpkg.com/leaflet@1.9.3/dist/leaflet.js': 'https://cdn.bootcdn.net/ajax/libs/leaflet/1.9.3/leaflet.js',
    'https://unpkg.com/leaflet@1.9.3/dist/leaflet.css': 'https://cdn.bootcdn.net/ajax/libs/leaflet/1.9.3/leaflet.css',
    'https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js': 'https://cdn.bootcdn.net/ajax/libs/leaflet/1.9.3/leaflet.js',
    'https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.css': 'https://cdn.bootcdn.net/ajax/libs/leaflet/1.9.3/leaflet.css',
}

def replace_cdn_urls(html_content: str, use_backup: bool = False) -> str:
    """
    替换HTML内容中的CDN URL
    
    Args:
        html_content: 原始HTML内容
        use_backup: 是否使用备用CDN
    
    Returns:
        替换后的HTML内容
    """
    mapping = CHINA_CDN_MAPPING.copy()
    if use_backup:
        mapping.update(BACKUP_CDN_MAPPING)
    
    # 替换CDN URL
    for original_url, new_url in mapping.items():
        # 替换script标签中的URL
        html_content = re.sub(
            rf'src="{re.escape(original_url)}"',
            f'src="{new_url}"',
            html_content
        )
        # 替换link标签中的URL
        html_content = re.sub(
            rf'href="{re.escape(original_url)}"',
            f'href="{new_url}"',
            html_content
        )
    
    return html_content

def get_cdn_replacements(html_content: str) -> List[Tuple[str, str]]:
    """
    获取需要替换的CDN URL列表
    
    Args:
        html_content: HTML内容
    
    Returns:
        需要替换的URL对列表
    """
    replacements = []
    
    for original_url, new_url in CHINA_CDN_MAPPING.items():
        if original_url in html_content:
            replacements.append((original_url, new_url))
    
    return replacements

def create_local_assets_html(html_content: str) -> str:
    """
    创建使用本地资源的HTML（如果CDN都不可用）
    
    Args:
        html_content: 原始HTML内容
    
    Returns:
        使用本地资源的HTML内容
    """
    # 这里可以添加本地资源路径
    # 目前先使用备用CDN
    return replace_cdn_urls(html_content, use_backup=True)

def validate_cdn_accessibility(html_content: str) -> Dict[str, bool]:
    """
    验证CDN的可访问性（模拟检查）
    
    Args:
        html_content: HTML内容
    
    Returns:
        CDN可访问性状态字典
    """
    # 这里可以添加实际的网络检查
    # 目前返回模拟结果
    return {
        'cdn.jsdelivr.net': False,
        'unpkg.com': True,
        'cdn.bootcdn.net': True,
        'cdnjs.cloudflare.com': False
    }

def optimize_html_for_china(html_content: str) -> str:
    """
    为中国网络环境优化HTML内容
    
    Args:
        html_content: 原始HTML内容
    
    Returns:
        优化后的HTML内容
    """
    # 1. 替换CDN URL
    html_content = replace_cdn_urls(html_content)
    
    # 2. 处理iframe中的srcdoc属性
    html_content = _optimize_iframe_srcdoc(html_content)
    
    # 3. 添加CDN加载失败处理
    cdn_fallback_script = """
    <script>
    // CDN加载失败处理
    function handleCDNError() {
        console.warn('CDN资源加载失败，尝试使用备用资源');
        // 这里可以添加备用资源加载逻辑
    }
    
    // 监听资源加载错误
    document.addEventListener('error', function(e) {
        if (e.target.tagName === 'SCRIPT' || e.target.tagName === 'LINK') {
            console.warn('资源加载失败:', e.target.src || e.target.href);
            handleCDNError();
        }
    }, true);
    </script>
    """
    
    # 在</body>标签前插入错误处理脚本
    html_content = html_content.replace('</body>', cdn_fallback_script + '</body>')
    
    return html_content

def _optimize_iframe_srcdoc(html_content: str) -> str:
    """
    优化iframe中的srcdoc属性内容
    
    Args:
        html_content: HTML内容
    
    Returns:
        优化后的HTML内容
    """
    import html
    
    # 查找iframe的srcdoc属性
    srcdoc_pattern = r'srcdoc="([^"]*)"'
    
    def replace_srcdoc(match):
        srcdoc_content = match.group(1)
        # 解码HTML实体
        decoded_content = html.unescape(srcdoc_content)
        # 应用CDN替换
        optimized_content = replace_cdn_urls(decoded_content)
        # 重新编码HTML实体
        encoded_content = html.escape(optimized_content, quote=True)
        return f'srcdoc="{encoded_content}"'
    
    # 替换iframe中的srcdoc内容
    optimized_html = re.sub(srcdoc_pattern, replace_srcdoc, html_content)
    
    return optimized_html

def get_cdn_statistics(html_content: str) -> Dict[str, int]:
    """
    获取CDN使用统计
    
    Args:
        html_content: HTML内容
    
    Returns:
        CDN使用统计字典
    """
    cdn_domains = [
        'cdn.jsdelivr.net',
        'unpkg.com',
        'cdn.bootcdn.net',
        'cdnjs.cloudflare.com',
        'code.jquery.com',
        'netdna.bootstrapcdn.com'
    ]
    
    stats = {}
    for domain in cdn_domains:
        count = len(re.findall(rf'https://[^"\']*{re.escape(domain)}[^"\']*', html_content))
        stats[domain] = count
    
    return stats

if __name__ == "__main__":
    # 测试CDN替换功能
    test_html = """
    <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.css"/>
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    """
    
    print("🔍 测试CDN替换功能...")
    print(f"原始HTML: {test_html}")
    
    optimized_html = optimize_html_for_china(test_html)
    print(f"优化后HTML: {optimized_html}")
    
    stats = get_cdn_statistics(test_html)
    print(f"CDN统计: {stats}")
