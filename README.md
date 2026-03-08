# PB-BI 数据分析平台

可以用明道云的BI平台 - 一个基于 React + FastAPI 的商业智能软件，用于连接明道云数据源，进行数据提取、处理、分析和可视化展示。

## 功能特性

### 配置管理
- 明道云 API 配置
- 数据流管理（增删改查）
- 字段配置（字段类型、启用/禁用）
- 本地数据导入（CSV、Excel）

### 数据获取
- 从明道云读取数据
- 导入本地数据（CSV、Excel）
- 数据快照管理
- 字段统计信息

### 数据分析
- 多表聚合（UNION ALL、UNION、JOIN等）
- 字段筛选
- 数据统计
- 高级统计分析（统计描述、分布拟合、回归分析）
- 相关性分析（支持多数据流）
- 相关性探索
- 蒙特卡洛分析

### AI智能对话
- 自然语言查询数据
- 自动生成图表
- 数据洞察分析
- 多轮对话上下文记忆
- 对话历史管理
- 反馈与纠错机制
- 三层记忆系统（用户偏好、成功案例、失败教训）

### 数据可视化
- 16种 ECharts 图表类型
- 基础图表：折线图、柱状图、饼图、散点图、雷达图
- 高级图表：热力图、漏斗图、仪表盘
- 3D图表：3D柱状图、3D散点图、3D形貌图
- 组合图表：堆叠图、多Y轴图、联动图表
- 专业图表：LED晶圆图
- 数据看板管理

### 系统设置
- UI风格切换（现代专业/Bloomberg终端）
- 主色调自定义
- 字体大小调整
- AI模型配置（**推荐使用Kimi** / DeepSeek / OpenAI / 智谱AI / 硅基流动）
- 三层记忆系统管理

## 技术栈

### 前端
- React 18
- React Router
- ECharts + echarts-gl
- react-markdown + remark-gfm
- Axios

### 后端
- FastAPI
- SQLAlchemy
- pandas
- numpy
- scipy
- statsmodels
- scikit-learn

### 数据库
- SQLite（开发环境）

## 快速开始

### 推荐使用Kimi模型

经过实际测试，**强烈推荐使用 Kimi (Moonshot) 模型**，原因如下：
- ✅ 工具调用格式规范稳定
- ✅ 支持标准的 OpenAI function calling API
- ✅ 中文理解和生成能力强
- ✅ 响应速度快，可靠性高

配置方法：在系统设置中选择 "硅基流动" 提供商，模型选择 "moonshot-v1-8k" 或 "moonshot-v1-32k"。

### 环境要求
- Python 3.8+
- Node.js 16+

### 安装与启动

1. **克隆项目**
```bash
git clone https://github.com/ceasarboy/nedi-BI.git
cd nedi-BI
```

2. **安装后端依赖**
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
pip install -r requirements.txt
```

3. **安装前端依赖**
```bash
cd frontend
npm install
```

4. **启动服务**

Windows:
```bash
# 开发模式
scripts\start-dev.bat

# 生产模式
scripts\build.bat
scripts\start.bat
```

Linux/macOS:
```bash
chmod +x scripts/start.sh
./scripts/start.sh
```

### 访问地址
- 前端界面: http://localhost:3000
- 后端API: http://localhost:8001
- API文档: http://localhost:8001/docs

## 功能模块导航

| 模块 | 路径 | 功能描述 |
|------|------|----------|
| 配置管理 | `/` | 数据源配置、字段管理 |
| 数据获取 | `/data` | 数据查看、快照管理 |
| 数据分析 | `/analysis` | 聚合、筛选、统计、高级分析 |
| AI对话 | `/ai` | 自然语言数据分析 |
| 数据可视化 | `/visual` | 图表创建、看板管理 |
| 相关性分析 | `/correlation` | 多数据流相关性分析 |
| 蒙特卡洛分析 | `/montecarlo` | 随机模拟分析 |
| 系统设置 | `/settings` | UI配置、AI模型、记忆管理 |
| 操作指南 | `/guide` | 功能使用说明 |

## 部署

详见 [DEPLOYMENT.md](./DEPLOYMENT.md)

## 生成便携版（可选）

如果需要生成不依赖系统环境的便携版，可以运行打包脚本：

```bash
# Windows
scripts\package-full.bat
```

生成的便携版将包含：
- Python 3.11 便携版
- Node.js 20 便携版
- 所有 Python 依赖
- 预构建的前端
- 配置文件示例

便携版可以直接复制到任何 Windows 机器运行，无需安装 Python 和 Node.js。

### 便携版配置

便携版支持通过 `config.ini` 自定义配置：

1. 复制 `config.example.ini` 为 `config.ini`
2. 根据需要修改配置值
3. 重启服务

支持的配置项：
- Python/Node.js 运行时路径
- 依赖库路径
- 端口配置
- API 地址
- 后端绑定地址

## 项目结构

```
nedi-BI/
├── config/              # 配置文件
├── docs/               # 文档
│   ├── 需求分析.md      # 功能需求文档
│   ├── 架构设计.md      # 系统架构设计
│   ├── 开发计划.md      # 迭代开发计划
│   └── ...
├── frontend/           # 前端项目
│   ├── src/
│   │   ├── charts/    # 图表组件（16种图表）
│   │   ├── components/# 通用组件
│   │   ├── pages/     # 页面组件
│   │   ├── services/  # API服务
│   │   └── styles/    # 样式文件
│   └── package.json
├── scripts/            # 启动脚本和打包脚本
├── src/                # 后端源代码
│   ├── api/           # API路由
│   ├── core/          # 核心配置
│   ├── models/        # 数据模型
│   └── services/      # 业务服务
│       ├── mingdao.py      # 明道云服务
│       ├── memory_service.py # 记忆系统服务
│       └── chart_recommendation.py # 图表推荐服务
├── requirements.txt    # Python依赖
├── config.example.ini  # 便携版配置示例
└── DEPLOYMENT.md      # 部署说明
```

## AI对话示例

```
用户: 帮我查看销售数据中金额最高的10条记录
AI: [执行数据查询并展示结果]

用户: 分析最近一个月的销售趋势，生成折线图
AI: [生成折线图并展示]

用户: 对比各部门的销售业绩，用柱状图展示
AI: [生成柱状图并展示]

用户: 展示各产品类别的销售占比，生成饼图
AI: [生成饼图并展示]
```

## 开发团队

本项目采用 ACP 敏捷开发流程。

## 许可证

MIT License
