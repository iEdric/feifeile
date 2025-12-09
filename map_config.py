#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地图服务配置模块
提供统一的地图瓦片服务配置和管理功能
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceCategory(Enum):
    """地图服务分类"""
    CHINA_MAIN = "china_main"      # 中国主要服务
    CHINA_BACKUP = "china_backup"  # 中国备用服务
    INTERNATIONAL = "international" # 国际服务
    SPECIAL = "special"            # 特殊服务（需要密钥等）
    UNKNOWN = "unknown"            # 未知分类

class ServiceStatus(Enum):
    """服务状态"""
    AVAILABLE = "available"        # 可用
    UNAVAILABLE = "unavailable"    # 不可用
    REQUIRES_KEY = "requires_key"  # 需要密钥
    UNKNOWN = "unknown"           # 未知状态

# 地图服务配置
MAP_SERVICES = {
    # 默认底图服务（用户指定）
    'OSM HOT': {
        'tiles': 'https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
        'attr': '© OpenStreetMap contributors',
        'name': 'OSM HOT',
        'category': ServiceCategory.INTERNATIONAL,
        'priority': 1,
        'default': False,
        'status': ServiceStatus.AVAILABLE,
        'description': 'OpenStreetMap HOT 地图'
    },
    'CyclOSM': {
        'tiles': 'https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png',
        'attr': '© OpenStreetMap contributors',
        'name': 'CyclOSM',
        'category': ServiceCategory.INTERNATIONAL,
        'priority': 2,
        'default': True,
        'status': ServiceStatus.AVAILABLE,
        'description': 'CyclOSM'
    },
    'Carto Light': {
        'tiles': 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
        'attr': '© OpenStreetMap contributors, © CARTO',
        'name': 'Carto Light',
        'category': ServiceCategory.INTERNATIONAL,
        'priority': 3,
        'default': False,
        'status': ServiceStatus.AVAILABLE,
        'description': 'CartoDB 浅色地图'
    },
    'OSM DE': {
        'tiles': 'https://{s}.tile.openstreetmap.de/{z}/{x}/{y}.png',
        'attr': '© OpenStreetMap DE',
        'name': 'OSM DE',
        'category': ServiceCategory.INTERNATIONAL,
        'priority': 4,
        'default': False,
        'status': ServiceStatus.AVAILABLE,
        'description': 'OpenStreetMap 德国服务器'
    },
    # 中国主要服务
    '高德地图': {
        'tiles': 'https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
        'attr': '© 高德地图',
        'name': '高德地图',
        'category': ServiceCategory.CHINA_MAIN,
        'priority': 5,
        'default': False,
        'status': ServiceStatus.AVAILABLE,
        'description': '高德地图标准街道视图，国内访问速度快'
    },
    '高德卫星': {
        'tiles': 'https://webst0{s}.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}',
        'attr': '© 高德地图',
        'name': '高德卫星',
        'category': ServiceCategory.CHINA_MAIN,
        'priority': 2,
        'default': False,
        'status': ServiceStatus.AVAILABLE,
        'description': '高德卫星影像，适合查看地形地貌'
    },
    '高德路网': {
        'tiles': 'https://webst0{s}.is.autonavi.com/appmaptile?style=7&x={x}&y={y}&z={z}',
        'attr': '© 高德地图',
        'name': '高德路网',
        'category': ServiceCategory.CHINA_MAIN,
        'priority': 3,
        'default': False,
        'status': ServiceStatus.AVAILABLE,
        'description': '高德路网视图，突出显示道路信息'
    },
    
    # 中国备用服务
    '百度地图': {
        'tiles': 'https://maponline{s}.bdimg.com/tile/?qt=vtile&x={x}&y={y}&z={z}&styles=pl&scaler=1&udt=20200101',
        'attr': '© 百度地图',
        'name': '百度地图',
        'category': ServiceCategory.CHINA_BACKUP,
        'priority': 4,
        'default': False,
        'status': ServiceStatus.AVAILABLE,
        'description': '百度地图标准视图，国内访问稳定'
    },
    
    # 特殊服务（需要密钥）
    '天地图街道': {
        'tiles': 'https://t{s}.tianditu.gov.cn/vec_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=vec&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=您的天地图密钥',
        'attr': '© 天地图',
        'name': '天地图街道',
        'category': ServiceCategory.SPECIAL,
        'priority': 5,
        'default': False,
        'status': ServiceStatus.REQUIRES_KEY,
        'description': '国家地理信息公共服务平台街道地图',
        'requires_key': True
    },
    '天地图影像': {
        'tiles': 'https://t{s}.tianditu.gov.cn/img_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=img&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=您的天地图密钥',
        'attr': '© 天地图',
        'name': '天地图影像',
        'category': ServiceCategory.SPECIAL,
        'priority': 6,
        'default': False,
        'status': ServiceStatus.REQUIRES_KEY,
        'description': '国家地理信息公共服务平台影像地图',
        'requires_key': True
    },
    
    # 国际服务
    'OpenStreetMap': {
        'tiles': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        'attr': '© OpenStreetMap contributors',
        'name': 'OpenStreetMap',
        'category': ServiceCategory.INTERNATIONAL,
        'priority': 7,
        'default': False,
        'status': ServiceStatus.AVAILABLE,
        'description': '开源地图服务，全球可用'
    }
}

# =============================================================================
# 基础查询函数
# =============================================================================

def get_map_services() -> Dict[str, Dict[str, Any]]:
    """获取所有地图服务配置"""
    return MAP_SERVICES.copy()

def get_service_by_name(service_name: str) -> Optional[Dict[str, Any]]:
    """根据名称获取地图服务配置"""
    return MAP_SERVICES.get(service_name)

def get_services_by_category(category: ServiceCategory) -> Dict[str, Dict[str, Any]]:
    """根据分类获取地图服务"""
    return {
        name: config for name, config in MAP_SERVICES.items()
        if config.get('category') == category
    }

def get_available_services() -> Dict[str, Dict[str, Any]]:
    """获取可用的地图服务（排除需要密钥的服务）"""
    return {
        name: config for name, config in MAP_SERVICES.items()
        if config.get('status') == ServiceStatus.AVAILABLE
    }

def get_default_service() -> Tuple[str, Dict[str, Any]]:
    """获取默认地图服务"""
    for service_name, config in MAP_SERVICES.items():
        if config.get('default', False):
            return service_name, config
    # 如果没有找到默认服务，返回优先级最高的可用服务
    return get_priority_services()[0] if get_priority_services() else ('高德地图', MAP_SERVICES['高德地图'])

def get_priority_services() -> List[Tuple[str, Dict[str, Any]]]:
    """按优先级获取地图服务列表"""
    services = [(name, config) for name, config in MAP_SERVICES.items()]
    return sorted(services, key=lambda x: x[1].get('priority', 999))

# =============================================================================
# 服务验证和状态管理
# =============================================================================

def validate_service(service_name: str) -> bool:
    """验证地图服务配置是否有效"""
    if service_name not in MAP_SERVICES:
        logger.warning(f"地图服务 {service_name} 不存在")
        return False
    
    config = MAP_SERVICES[service_name]
    required_fields = ['tiles', 'attr', 'name']
    
    for field in required_fields:
        if field not in config:
            logger.warning(f"地图服务 {service_name} 缺少必需字段: {field}")
            return False
    
    return True

def update_service_status(service_name: str, status: ServiceStatus) -> bool:
    """更新地图服务状态"""
    if service_name not in MAP_SERVICES:
        logger.error(f"无法更新不存在的服务状态: {service_name}")
        return False
    
    MAP_SERVICES[service_name]['status'] = status
    logger.info(f"地图服务 {service_name} 状态已更新为: {status.value}")
    return True

def get_service_info(service_name: str) -> Dict[str, Any]:
    """获取地图服务详细信息"""
    if service_name not in MAP_SERVICES:
        return {}
    
    config = MAP_SERVICES[service_name]
    return {
        'name': config.get('name', service_name),
        'description': config.get('description', ''),
        'category': config.get('category', ServiceCategory.UNKNOWN),
        'status': config.get('status', ServiceStatus.UNKNOWN),
        'priority': config.get('priority', 999),
        'requires_key': config.get('requires_key', False),
        'default': config.get('default', False)
    }

# =============================================================================
# 地图图层创建和管理
# =============================================================================

def create_tile_layer(service_name: str, **kwargs) -> Optional[Any]:
    """创建地图瓦片图层"""
    import folium
    
    # 验证服务
    if not validate_service(service_name):
        logger.error(f"无法创建无效的地图服务图层: {service_name}")
        return None
    
    config = MAP_SERVICES[service_name]
    
    # 检查服务状态
    if config.get('status') == ServiceStatus.REQUIRES_KEY:
        logger.warning(f"地图服务 {service_name} 需要API密钥")
        return None
    
    # 构建图层配置
    layer_config = {
        'tiles': config['tiles'],
        'attr': config['attr'],
        'name': config['name'],
        'control': True,
        'overlay': False,
        'show': config.get('default', False)
    }
    
    # 更新用户提供的参数
    layer_config.update(kwargs)
    
    try:
        return folium.TileLayer(**layer_config)
    except Exception as e:
        logger.error(f"创建地图图层失败 {service_name}: {e}")
        return None

def add_services_to_map(map_obj: Any, 
                       services: Optional[List[str]] = None,
                       exclude_services: Optional[List[str]] = None,
                       category_filter: Optional[ServiceCategory] = None) -> Any:
    """为地图对象添加指定的地图服务图层"""
    if exclude_services is None:
        exclude_services = []
    
    # 确定要添加的服务
    if services is None:
        if category_filter:
            target_services = get_services_by_category(category_filter)
        else:
            target_services = get_available_services()
    else:
        target_services = {name: config for name, config in MAP_SERVICES.items() if name in services}
    
    # 过滤排除的服务
    target_services = {name: config for name, config in target_services.items() 
                      if name not in exclude_services}
    
    # 按优先级排序
    sorted_services = sorted(target_services.items(), 
                           key=lambda x: x[1].get('priority', 999))
    
    # 添加图层
    added_count = 0
    for service_name, config in sorted_services:
        try:
            layer = create_tile_layer(service_name)
            if layer:
                layer.add_to(map_obj)
                added_count += 1
                logger.info(f"成功添加地图服务: {service_name}")
        except Exception as e:
            logger.warning(f"无法添加地图服务 {service_name}: {e}")
            continue
    
    logger.info(f"地图图层添加完成，共添加 {added_count} 个服务")
    return map_obj

def add_fallback_layers(map_obj: Any) -> Any:
    """添加备用地图图层，确保地图始终可用"""
    # 按优先级获取可用服务
    priority_services = get_priority_services()
    
    added_count = 0
    for service_name, config in priority_services:
        if config.get('status') != ServiceStatus.AVAILABLE:
            continue
            
        try:
            # 第一个服务设为默认显示
            show_default = (added_count == 0)
            layer = create_tile_layer(service_name, show=show_default)
            
            if layer:
                layer.add_to(map_obj)
                added_count += 1
                logger.info(f"添加备用地图服务: {service_name}")
                
                # 成功添加默认服务后停止
                if show_default:
                    break
                    
        except Exception as e:
            logger.warning(f"无法添加备用地图服务 {service_name}: {e}")
            continue
    
    if added_count == 0:
        logger.error("无法添加任何地图服务，地图可能无法正常显示")
    
    return map_obj

# =============================================================================
# 兼容性函数（保持向后兼容）
# =============================================================================

def get_default_map_service():
    """获取默认地图服务（兼容性函数）"""
    return get_default_service()

def add_all_map_layers(map_obj, exclude_services=None):
    """为地图对象添加默认底图图层"""
    import folium
    
    # 用户指定的默认底图配置
    base_layers = {
        'OSM HOT': {
            'tiles': 'https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
            'attr': '© OpenStreetMap contributors',
            'name': 'OSM HOT',
            'control': True,
            'overlay': False,
            'show': True  # 默认显示
        },
        'CyclOSM': {
            'tiles': 'https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png',
            'attr': '© OpenStreetMap contributors',
            'name': 'CyclOSM',
            'control': True,
            'overlay': False,
            'show': False  # 默认不显示
        },
        'Carto Light': {
            'tiles': 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
            'attr': '© OpenStreetMap contributors, © CARTO',
            'name': 'Carto Light',
            'control': True,
            'overlay': False,
            'show': False  # 默认不显示
        },
        'OSM DE': {
            'tiles': 'https://{s}.tile.openstreetmap.de/{z}/{x}/{y}.png',
            'attr': '© OpenStreetMap DE',
            'name': 'OSM DE',
            'control': True,
            'overlay': False,
            'show': False  # 默认不显示
        }
    }
    
    # 添加底图图层到地图
    for layer_name, layer_config in base_layers.items():
        if exclude_services and layer_name in exclude_services:
            continue
            
        try:
            layer = folium.TileLayer(**layer_config)
            layer.add_to(map_obj)
            logger.info(f"成功添加底图图层: {layer_name}")
        except Exception as e:
            logger.error(f"添加底图图层失败 {layer_name}: {e}")
    
    return map_obj

# =============================================================================
# 工具函数
# =============================================================================

def list_services_by_status(status: ServiceStatus) -> List[str]:
    """列出指定状态的地图服务"""
    return [name for name, config in MAP_SERVICES.items() 
            if config.get('status') == status]

def get_service_statistics() -> Dict[str, int]:
    """获取地图服务统计信息"""
    stats = {}
    for status in ServiceStatus:
        stats[status.value] = len(list_services_by_status(status))
    return stats

def print_service_info():
    """打印所有地图服务信息"""
    print("🗺️ 地图服务配置信息")
    print("=" * 50)
    
    for service_name, config in get_priority_services():
        info = get_service_info(service_name)
        status_icon = "✅" if info['status'] == ServiceStatus.AVAILABLE else "❌"
        key_icon = "🔑" if info['requires_key'] else "🔓"
        default_icon = "⭐" if info['default'] else "  "
        
        print(f"{status_icon} {key_icon} {default_icon} {service_name}")
        print(f"   分类: {info['category'].value}")
        print(f"   状态: {info['status'].value}")
        print(f"   优先级: {info['priority']}")
        print(f"   描述: {info['description']}")
        print()
