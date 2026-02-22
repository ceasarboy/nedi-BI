# PB-BI 数据分析平台

一个基于 React + FastAPI 的商业智能软件，用于连接明道云数据源，进行数据提取、处理、分析和可视化展示。

## 功能特性

### 配置管理
- 明道云 API 配置
- 数据流管理（增删改查）
- 字段配置（字段类型、启用/禁用）

### 数据获取
- 从明道云读取数据
- 导入本地数据（CSV、Excel）
- 数据快照管理

### 数据分析
- 多表聚合（UNION ALL、UNION、JOIN等）
- 字段筛选
- 数据统计
- 高级统计分析（统计描述、分布拟合、回归分析）
- 相关性分析（支持多数据流）
- 相关性探索
- 蒙特卡洛分析

### 数据可视化
- 10+ 种 ECharts 图表类型
- 3D 图表支持
- LED 晶圆分析图
- 数据看板

## 技术栈

### 前端
- React 18
- React Router
- ECharts + echarts-gl
- Axios

### 后端
- FastAPI
- SQLAlchemy
- pandas
- statsmodels
- scikit-learn

### 数据库
- SQLite（开发环境）

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+

### 安装与启动

1. **克隆项目**
```bash
git clone <repository-url>
cd PB-BI
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
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 部署

详见 [DEPLOYMENT.md](./DEPLOYMENT.md)

## 项目结构

```
PB-BI/
├── config/              # 配置文件
├── docs/               # 文档
├── frontend/           # 前端项目
│   ├── src/
│   │   ├── charts/    # 图表组件
│   │   ├── components/# 通用组件
│   │   ├── pages/     # 页面组件
│   │   └── services/  # API服务
│   └── package.json
├── scripts/            # 启动脚本
├── src/                # 后端源代码
│   ├── api/           # API路由
│   ├── core/          # 核心配置
│   ├── models/        # 数据模型
│   └── services/      # 业务服务
├── requirements.txt    # Python依赖
└── DEPLOYMENT.md      # 部署说明
```

## 开发团队

本项目采用 ACP 敏捷开发流程。

## 许可证

MIT License
