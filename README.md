# 海航飞飞乐查询系统

一个基于Gradio的航班查询和可视化系统，支持航班搜索、地图展示和统计分析。

## 功能特性

- 🔍 **航班搜索**: 支持按起飞机场、降落机场、航班号、会员类型查询
- 🤖 **AI智能规划**: 
  - 智能路线推荐：基于OpenAI API的智能路线规划
  - 多路线展示：显示从起点到终点的所有可能路线
  - 偏好设置：支持用户自定义飞行偏好
  - 中转优化：智能推荐最优中转方案
- 🗺️ **地图可视化**: 
  - 航班路线图：显示航线网络和机场分布
  - 机场分布图：热力图显示机场航班密度
  - 航线网络图：展示航线连接关系
- 📊 **统计分析**: 
  - 机场航班频次统计
  - 机场气泡图
  - 起降航班对比分析
- 🚀 **性能优化**: 
  - CDN优化，支持中国网络环境
  - 地图资源缓存
  - 页面切换优化

## 技术栈

- **前端**: Gradio, Folium, Plotly
- **后端**: Python 3.8+
- **地图服务**: OpenStreetMap, 高德地图, 百度地图, 天地图
- **数据处理**: Pandas, JSON

## 安装和运行

### 环境要求

- Python 3.8+
- 依赖包见 `requirements.txt`

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行应用

#### 基础运行（无AI功能）
```bash
python app.py
```

#### 启用AI智能规划功能
```bash
# 使用SiliconFlow API（推荐，更便宜）
export OPENAI_API_KEY="sk-lwpjzcxdyn"
export OPENAI_API_BASE="https://api.siliconflow.cn/v1"
python app.py

# 或使用OpenAI官方API
export OPENAI_API_KEY="your_openai_api_key_here"
export OPENAI_API_BASE="https://api.openai.com/v1"
python app.py
```

#### 测试AI规划功能
```bash
python test_ai_planner.py
```

应用将在 `http://localhost:7171` 启动。

## 项目结构

```
chenli-flight-app/
├── app.py                    # 主应用文件
├── utils.py                  # 工具函数
├── map_config.py            # 地图配置
├── cdn_replacer.py          # CDN优化
├── app_resource_manager.py  # 资源管理
├── data/                    # 数据文件
│   ├── hainan_plus_flights.jsonl  # 航班数据
│   ├── airport_coords.json        # 机场坐标
│   ├── alipay.jpg                 # 支付宝赞赏码
│   └── wechat.jpg                 # 微信赞赏码
├── scripts/                 # 脚本文件
│   └── generate_airport_coords.py
├── requirements.txt         # 依赖包
├── dockerfile              # Docker配置
├── docker-compose.yaml     # Docker Compose配置
└── README.md              # 说明文档
```

## 主要功能

### 1. 航班搜索
- 支持按起飞机场、降落机场查询
- 支持会员类型筛选（666、2666、666/2666）
- 支持模糊搜索和精确匹配

### 2. 地图可视化
- **航班路线图**: 显示查询结果的航线网络，支持弧线显示多条航线
- **机场分布图**: 热力图显示各机场的航班密度
- **航线网络图**: 展示所有航线的连接关系

### 3. 统计分析
- **频次统计**: 柱状图显示各机场的起降航班数
- **气泡图**: 气泡大小表示机场航班数量
- **数据概览**: 显示总机场数、总航班数等统计信息

## 地图服务配置

系统支持多种地图服务，自动选择最适合的服务：

- **OpenStreetMap**: 默认底图
- **高德地图**: 中国地区优化
- **百度地图**: 备用服务
- **天地图**: 官方地图服务

## 性能优化

### CDN优化
- 自动替换不可访问的CDN资源
- 使用中国可访问的CDN镜像
- 支持多种资源类型（JS、CSS、字体等）

### 资源管理
- 全局资源加载，避免重复请求
- 地图资源缓存
- 页面切换优化

## 数据格式

### 航班数据格式
```json
{
  "航班号": "HU1234",
  "起飞机场": "北京首都",
  "降落机场": "上海浦东",
  "起飞时间": "08:00",
  "班期": "1234567",
  "适用产品": "666/2666"
}
```

### 机场坐标格式
```json
{
  "机场名称": [纬度, 经度]
}
```

## 开发说明

### 添加新的地图服务
在 `map_config.py` 中添加新的地图服务配置。

### 自定义CDN替换
在 `cdn_replacer.py` 中配置CDN替换规则。

### 扩展统计功能
在 `utils.py` 中添加新的统计函数。

## 部署

### Docker部署
```bash
docker-compose up -d
```

### 直接部署
```bash
python app.py
```

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

MIT License

## 联系方式

- 邮箱: openchatcl@outlook.com
- 项目地址: [GitHub Repository]

---

💖 感谢使用海航飞飞乐查询系统！
