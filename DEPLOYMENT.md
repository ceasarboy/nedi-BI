# PB-BI 数据分析平台 - 部署说明

## 部署方式概览

| 方式 | 适用场景 | 环境要求 |
|------|----------|----------|
| **便携式打包** | 局域网快速分发，目标机器无开发环境 | 无需安装任何依赖 |
| **开发模式** | 本地开发测试 | Python + Node.js |
| **生产部署** | 服务器部署 | Python + Node.js + Nginx |

---

## 方式一：便携式打包（推荐用于局域网分发）

### 特点
- ✅ 目标机器无需安装 Python 和 Node.js
- ✅ 解压即用，一键启动
- ✅ 完全独立，不依赖系统环境
- ✅ 适合快速分发到其他电脑

### 打包步骤（在开发机器上执行）

```bash
# 双击运行
scripts\package-full.bat
```

打包脚本会自动：
1. 复制后端代码和配置文件
2. 构建前端生产版本
3. 下载 Python 便携版（约 15MB）
4. 下载 Node.js 便携版（约 80MB）
5. 安装所有 Python 依赖到 `backend/libs`
6. 预安装 `serve` 包用于前端服务
7. 创建启动和停止脚本

### 分发和使用

1. 将整个 `dist\pb-bi-portable` 文件夹复制到目标机器
2. 双击运行 `start.bat`
3. 等待服务启动完成（约 5 秒）
4. 浏览器自动打开或访问 http://localhost:3000

### 便携版目录结构

```
pb-bi-portable/
├── backend/              # 后端代码和依赖
│   ├── src/             # 源代码
│   ├── libs/            # Python依赖包（约150MB）
│   └── requirements.txt
├── frontend/             # 前端构建产物
│   └── dist/
├── config/               # 配置文件和数据库
│   └── pb_bi.db
├── runtime/              # 运行时环境
│   ├── python/          # Python 3.11 便携版
│   │   ├── python.exe
│   │   └── python311._pth  # 配置文件（指向 backend/libs）
│   ├── node/            # Node.js 20 便携版
│   └── npm-global/      # 预装的 serve 包
├── start.bat             # 主启动脚本
├── start-backend.bat     # 后端启动脚本
├── start-frontend.bat    # 前端启动脚本
├── stop.bat              # 停止脚本
└── README.md             # 说明文档
```

### 启动脚本说明

| 脚本 | 功能 |
|------|------|
| `start.bat` | 主启动脚本，同时启动前后端服务 |
| `start-backend.bat` | 单独启动后端服务（端口 8000） |
| `start-frontend.bat` | 单独启动前端服务（端口 3000） |
| `stop.bat` | 停止所有服务 |

### 技术实现细节

#### Python 依赖隔离
通过修改 `python311._pth` 文件，将 Python 的模块搜索路径指向 `backend/libs`：

```
python311.zip
.
libs
../../backend/libs
```

**关键点**：
- 相对路径 `../../backend/libs` 是相对于 `python.exe` 所在目录（`runtime/python/`）
- 无论便携版放在哪个盘或文件夹，路径都会正确解析
- 移除了 `import site`，完全隔离系统 Python 环境

**路径解析示例**：
```
便携版位置: D:\some\folder\pb-bi-portable\
python.exe: D:\some\folder\pb-bi-portable\runtime\python\python.exe
相对路径 ../../backend/libs 解析为:
  D:\some\folder\pb-bi-portable\backend\libs ✅
```

#### Node.js 依赖隔离
预安装 `serve` 包到 `runtime/npm-global`，启动时直接使用 Node.js 运行 serve 模块：

```batch
%SCRIPT_DIR%runtime\node\node.exe "%SCRIPT_DIR%runtime\npm-global\node_modules\serve\build\main.js" -s . -l 3000
```

**关键点**：
- 直接使用便携版 `node.exe` 运行 `serve` 模块
- 不依赖 PATH 环境变量或系统 Node.js
- 无论便携版放在哪个位置，路径都会正确解析

**路径解析示例**：
```
便携版位置: D:\apps\pb-bi-portable\
start.bat: D:\apps\pb-bi-portable\start.bat
%~dp0 解析为: D:\apps\pb-bi-portable\
%SCRIPT_DIR%runtime\python 解析为:
  D:\apps\pb-bi-portable\runtime\python ✅
```

#### 已验证的依赖包
| 包名 | 版本 | 状态 |
|------|------|------|
| fastapi | 0.129.2 | ✅ |
| uvicorn | 0.41.0 | ✅ |
| pydantic | 2.12.5 | ✅ |
| sqlalchemy | 2.0.46 | ✅ |
| python-multipart | - | ✅ |
| cryptography | 46.0.5 | ✅ |
| requests | 2.32.5 | ✅ |
| pandas | 3.0.1 | ✅ |
| openpyxl | 3.1.5 | ✅ |
| statsmodels | 0.14.6 | ✅ |
| scikit-learn | 1.8.0 | ✅ |
| scipy | 1.17.0 | ✅ |

### 包体积估算

| 组件 | 大小 |
|------|------|
| Python 便携版 | ~15 MB |
| Node.js 便携版 | ~80 MB |
| Python 依赖包 | ~150 MB |
| 前端构建产物 | ~5 MB |
| 后端代码 | ~1 MB |
| **总计** | **~250 MB** |

---

## 方式二：开发模式部署

### 环境要求
- Python 3.8+
- Node.js 16+

### Windows 系统

#### 开发模式启动
```bash
scripts\start-dev.bat
```

#### 生产模式启动
```bash
# 首先构建前端
scripts\build.bat

# 然后启动服务
scripts\start.bat
```

### Linux/macOS 系统

```bash
# 添加执行权限
chmod +x scripts/start.sh

# 运行
./scripts/start.sh
```

---

## 方式三：手动部署

### 1. 安装后端依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 安装前端依赖

```bash
cd frontend
npm install
```

### 3. 构建前端（生产模式）

```bash
cd frontend
npm run build
```

### 4. 启动后端服务

```bash
# 开发模式（支持热重载）
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# 生产模式
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### 5. 启动前端服务

```bash
cd frontend

# 开发模式
npm run dev

# 生产模式（预览构建结果）
npm run preview
```

---

## 访问地址

### 本地访问
- 前端界面: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

### 局域网访问

1. 查看本机IP地址：
   - Windows: `ipconfig`
   - Linux/macOS: `ifconfig` 或 `ip addr`

2. 从其他电脑访问：
   - 前端界面: `http://YOUR_IP:3000`
   - 后端API: `http://YOUR_IP:8000`

**注意**: 确保防火墙允许 3000 和 8000 端口的入站连接。

---

## 防火墙配置

### Windows 防火墙

```powershell
# 添加入站规则（以管理员身份运行）
netsh advfirewall firewall add rule name="PB-BI Backend" dir=in action=allow protocol=tcp localport=8000
netsh advfirewall firewall add rule name="PB-BI Frontend" dir=in action=allow protocol=tcp localport=3000
```

### Linux 防火墙（ufw）

```bash
# 允许端口
sudo ufw allow 8000
sudo ufw allow 3000
```

---

## 端口配置

如需修改端口，请编辑以下文件：

### 后端端口
- `src/main.py` 中的 `port=8000`
- `frontend/vite.config.js` 中的 `proxy.target`

### 前端端口
- `frontend/vite.config.js` 中的 `port: 3000`

---

## 生产环境建议

### 1. 使用进程管理器

推荐使用 `pm2` 或 `supervisor` 管理进程：

```bash
# 安装 pm2
npm install -g pm2

# 启动后端
pm2 start "python -m uvicorn src.main:app --host 0.0.0.0 --port 8000" --name pb-bi-backend

# 启动前端
pm2 start "npm run preview --prefix frontend" --name pb-bi-frontend
```

### 2. 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 后端API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. 数据库迁移

生产环境建议使用 PostgreSQL：

1. 安装 PostgreSQL
2. 修改 `src/core/database.py` 中的数据库连接字符串
3. 运行数据库迁移

---

## 常见问题

### 1. 端口被占用

```bash
# Windows 查看端口占用
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Linux/macOS 查看端口占用
lsof -i :8000
lsof -i :3000
```

### 2. 前端无法连接后端

检查：
- 后端服务是否正常运行
- 防火墙是否允许端口
- vite.config.js 中的 proxy 配置是否正确

### 3. 局域网无法访问

检查：
- 防火墙是否允许入站连接
- 服务是否绑定到 0.0.0.0（而不是 127.0.0.1）
- IP 地址是否正确

### 4. 便携版启动失败

检查：
- 是否完整复制了整个文件夹
- `runtime/python` 和 `runtime/node` 目录是否存在
- `backend/libs` 目录是否存在
- 是否被杀毒软件拦截

### 5. Python 依赖导入失败

便携版已配置 `python311._pth` 指向 `backend/libs`，如果仍有问题：
- 检查 `runtime/python/python311._pth` 文件是否包含 `../../backend/libs`
- 确保从便携版根目录运行 `start.bat`

---

## 目录结构

```
PB-BI/
├── config/              # 配置文件目录
│   └── pb_bi.db        # SQLite 数据库
├── dist/               # 打包输出目录
│   └── pb-bi-portable/ # 便携版
├── docs/               # 文档目录
├── frontend/           # 前端项目
│   ├── dist/          # 构建输出（生产）
│   ├── src/           # 源代码
│   └── package.json   # 前端依赖
├── scripts/            # 启动脚本
│   ├── start.bat      # Windows 生产启动
│   ├── start-dev.bat  # Windows 开发启动
│   ├── build.bat      # Windows 构建
│   ├── package-full.bat # 完整便携式打包
│   └── start.sh       # Linux/macOS 启动
├── src/                # 后端源代码
│   ├── api/           # API 路由
│   ├── core/          # 核心配置
│   ├── models/        # 数据模型
│   └── services/      # 业务服务
├── venv/               # Python 虚拟环境
├── requirements.txt    # Python 依赖
├── README.md          # 项目说明
└── DEPLOYMENT.md      # 部署说明
```

---

## 技术支持

如有问题，请查看项目文档或联系开发团队。
