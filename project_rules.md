# PB-BI 项目规则与经验总结

## ACP 敏捷开发流程

本项目采用 ACP（敏捷）开发方式，包含以下核心角色和流程：

### 1. 架构师职责
- 制定系统架构设计
- 汇总和确认需求分析
- 每次迭代时重新确认架构和需求是否变更
- 更新需求分析文档和架构设计文档

### 2. 项目经理职责
- 按照架构和需求制定开发计划
- 跟踪开发计划进度
- 如有更新需求，及时更新开发计划

### 3. 软件开发人员职责
- 前端使用 React 开发，保持编程风格一致
- 进行软件开发
- 如代码审查存在问题，修改并重新提交审查

### 4. 代码审查人员职责
- 对开发代码进行审查
- 反馈审查意见给开发人员
- 对整改后的代码进行重新审查

### 5. 软件测试人员职责
- 编制软件测试用例和测试大纲
- 对软件进行测试
- 反馈测试结果给软件开发人员
- 直到软件通过测试

### 6. ACP 推进专家职责
- 总结软件经验和教训
- 记录到 project_rules.md

---

## 迭代 1.1 经验总结

### 本次迭代完成的功能
1. ✅ 在数据流列表的"测试"按钮后添加"设置"按钮
2. ✅ 点击设置按钮后显示该数据流的所有字段列表
3. ✅ 支持配置字段属性（字段类型）
4. ✅ 支持选择是否使用该字段（启用/禁用）
5. ✅ 保存字段配置功能

### 经验教训

#### 1. 严格遵守ACP流程的重要性
**问题**：在本次迭代初期，没有先更新需求分析和架构设计文档就直接开始编码
**教训**：必须严格按照ACP流程执行，每次迭代都应该：
1. 架构师先确认并更新需求分析和架构设计
2. 项目经理更新开发计划
3. 开发人员进行开发
4. 代码审查人员进行审查
5. 测试人员更新测试大纲
6. ACP专家总结经验教训

#### 2. 数据库设计的灵活性
**经验**：在设计字段启用状态时，使用字符串存储（"true"/"false"）比布尔类型更简单，避免了类型转换的复杂性
**建议**：在前后端交互时，对于简单的布尔标志，可以考虑使用字符串格式

#### 3. 用户体验优化
**经验**：
- 添加"保存配置"按钮，让用户明确知道需要手动保存
- 在标题中显示当前配置的数据流名称，提供清晰的上下文
- 使用灰色的次要按钮样式区分"设置"按钮和其他操作按钮

#### 4. 代码质量
**经验**：
- 代码结构清晰，职责分离明确
- 错误处理完善，提供友好的提示信息
- 样式设计美观，用户体验良好

### 改进建议

1. **流程改进**：建立明确的迭代启动检查清单，确保每次迭代都按ACP流程执行
2. **文档改进**：在需求分析文档中添加用户故事，更清晰地描述用户需求
3. **测试改进**：在开发过程中同步编写单元测试，提高代码质量
4. **沟通改进**：在每次迭代开始前，先进行简短的团队沟通，确认需求和计划

---

## 迭代 2.13 经验总结（图表功能优化与第一阶段总结）

### 本次迭代完成的功能
1. ✅ 3D柱状图优化：透明效果、数据维度修复
2. ✅ 创建3D形貌图组件 - Surface3DChart
3. ✅ 创建联动图表组件 - LinkedChart
4. ✅ 创建LED晶圆分析图组件 - LEDWaferChart
5. ✅ 实现波长到RGB颜色转换算法
6. ✅ 数据看板图表高度加大（翻倍）
7. ✅ 第一阶段完成总结
8. ✅ 更新所有文档（需求分析、架构设计、开发计划）

### 经验教训

#### 1. 第一阶段完成的里程碑意义 ⭐重要
**经验**：
- 第一阶段从2026-02-14到2026-02-22，共8天
- 完成了5个核心模块：配置管理、数据获取、数据分析、数据可视化、操作介绍
- 实现了10+种图表类型
- 功能基本覆盖BI软件的核心需求
**里程碑**：
- 第一阶段是从0到1的过程，建立了完整的BI软件基础
- 为后续迭代（可部署版本、蒙特卡洛完善、可视化计算）打下了坚实基础

#### 2. 波长到RGB颜色转换的实现要点 ⭐重要
**经验**：
- 可见光波长范围380-780nm
- 分为8个区间进行线性插值
- 超出范围时显示灰色（#808080）
- 转换后需要归一化到0-255范围
- 使用toHex函数确保输出两位十六进制数

**实现的8个区间**：
1. 380-450nm: R从0到0, G从0到0, B从255到255（蓝色）
2. 450-500nm: R从0到0, G从0到255, B从255到0（青色）
3. 500-570nm: R从0到255, G从255到255, B从0到0（绿色）
4. 570-590nm: R从255到255, G从255到0, B从0到0（黄色）
5. 590-620nm: R从255到255, G从0到0, B从0到0（橙色）
6. 620-780nm: R从255到255, G从0到0, B从0到0（红色）

#### 3. ECharts 3D图表的数据结构要点
**经验**：
- 3D柱状图：数据格式 [[x, y, z], ...]，注意三个维度的顺序
- 3D形貌图：数据格式 [[z1, z2, ...], ...]，二维数组表示网格
- 透明效果：使用opacity配置，让多个柱子叠加时可以看到下方
- 视角控制：设置autoRotate提升用户体验

#### 4. 联动图表的实现要点
**经验**：
- 使用ECharts的updateAxisPointer事件实现联动
- 共享同一个dataset，确保数据一致性
- 折线图和饼图可以很好地配合展示
- 鼠标悬停时两个图表同步高亮，视觉效果好

#### 5. 代码审查的彻底性 ⭐重要
**经验**：
- 代码审查不仅要检查功能，还要检查代码质量
- 本次审查发现：Bar3DChart和Surface3DChart中有未使用的变量
- 及时清理未使用的变量，保持代码整洁
- 代码审查是质量保障的重要环节

#### 6. 用户反馈的快速响应
**经验**：
- 用户反馈"数据看板图表尺寸好像比较小"，立即响应并修复
- 将图表高度加大一倍，提升用户体验
- 用户体验优化是持续的过程

#### 7. 第一阶段待完善功能的记录
**经验**：
- 即使第一阶段完成，也要清楚记录待完善的功能
- 本次记录：
  - 蒙特卡洛分析模块：自定义模拟功能待开发
  - 可视化计算模块：尚未开展
- 为后续迭代明确方向

#### 8. 文档更新的同步性 ⭐重要
**经验**：
- 每次迭代都要同步更新三个文档：需求分析、架构设计、开发计划
- 文档版本号要保持同步递增
- 文档是项目的重要资产，要保持最新状态
- ACP流程要求先更新文档，再开始编码

### 改进建议（补充）

96. **版本管理改进**：建议初始化Git仓库，进行代码版本管理
97. **第一阶段回顾改进**：建议召开第一阶段回顾会议，总结经验教训
98. **部署准备改进**：提前规划部署方案，包括host配置、端口设置等
99. **功能优先级改进**：明确第二阶段功能的优先级排序
100. **用户测试改进**：第一阶段完成后，建议邀请用户进行测试，收集反馈

---

## 迭代 3.0 经验总结（可部署版本生成）

### 本次迭代完成的功能
1. ✅ 后端部署配置（host=0.0.0.0）
2. ✅ 前端构建优化（vite.config.js配置）
3. ✅ 创建启动脚本（start.bat、start-dev.bat、build.bat、start.sh）
4. ✅ 创建部署说明文档（DEPLOYMENT.md）
5. ✅ 创建项目说明文档（README.md）
6. ✅ 测试本地部署
7. ✅ 测试局域网访问
8. ✅ 代码审查和修复

### 经验教训

#### 1. 部署配置的关键要点 ⭐重要
**经验**：
- 后端必须绑定到 `0.0.0.0` 而不是 `127.0.0.1`，否则只能本机访问
- 前端 vite.config.js 需要配置 `server.host` 和 `preview.host` 为 `'0.0.0.0'`
- 前端构建后使用 `npm run preview` 启动预览服务

**配置示例**：
```javascript
// vite.config.js
server: {
  host: '0.0.0.0',
  port: 3000
},
preview: {
  host: '0.0.0.0',
  port: 3000
}
```

#### 2. 启动脚本的路径处理 ⭐重要
**问题**：启动脚本放在 scripts 目录下，路径引用需要正确处理
**解决**：
- Windows: 使用 `%~dp0` 获取脚本所在目录，然后用 `..` 获取项目根目录
- Linux/macOS: 使用 `$(dirname "${BASH_SOURCE[0]}")` 获取脚本目录

**正确示例**：
```batch
set PROJECT_DIR=%~dp0..
start "PB-BI Backend" cmd /k "cd /d %PROJECT_DIR% && venv\Scripts\activate && ..."
```

#### 3. 局域网访问的验证
**经验**：
- Vite 启动后会自动显示 Network 地址
- 例如：`http://192.168.1.6:3000/`
- 可以直接从其他电脑访问该地址
- 需要确保防火墙允许对应端口

#### 4. 部署文档的重要性
**经验**：
- DEPLOYMENT.md 应该包含完整的部署步骤
- 包括环境要求、安装步骤、启动命令、常见问题
- README.md 应该包含项目简介和快速开始指南
- 文档是用户的第一印象，要清晰明了

#### 5. 前端构建优化
**经验**：
- 使用 `vite build` 构建生产版本
- 输出目录默认为 `dist`
- 构建时会提示 chunk 大小警告，可以考虑代码分割优化
- 使用 `sourcemap: false` 减小构建体积

#### 6. Windows PowerShell 的命令语法
**问题**：PowerShell 不支持 `&&` 作为命令分隔符
**解决**：使用 `;` 代替 `&&`
```powershell
# 错误
cd f:\PB-BI\frontend && npm run build

# 正确
cd f:\PB-BI\frontend; npm run build
```

#### 7. 服务启动顺序
**经验**：
- 先启动后端服务，等待几秒后再启动前端
- 前端启动时会尝试连接后端 API
- 如果后端未启动，前端可能显示错误

#### 8. ACP流程的持续执行 ⭐重要
**经验**：
- 即使是部署任务，也要严格按照ACP流程执行
- 本次迭代严格执行了：
  1. 架构师：确认部署需求
  2. 项目经理：制定部署计划
  3. 开发人员：进行部署配置
  4. 代码审查人员：审查配置并修复问题
  5. ACP专家：总结经验教训
- 流程是质量的保障

### 改进建议（补充）

101. **Docker化改进**：建议创建 Dockerfile 和 docker-compose.yml，简化部署流程
102. **进程管理改进**：建议使用 pm2 或 supervisor 管理进程，支持自动重启
103. **Nginx反向代理改进**：生产环境建议使用 Nginx 作为反向代理
104. **环境变量改进**：建议使用 .env 文件管理环境变量
105. **日志管理改进**：建议添加日志收集和分析功能
106. **监控告警改进**：建议添加服务监控和告警功能
107. **HTTPS支持改进**：生产环境建议启用 HTTPS
108. **数据库备份改进**：建议添加数据库自动备份功能

---

## 迭代 3.2 经验总结（用户认证模块）

### 本次迭代完成的功能
1. ✅ 用户认证系统设计（登录/注册、权限控制、角色管理）
2. ✅ 数据库模型设计（User模型、现有模型添加user_id外键）
3. ✅ 密码加密与验证（bcrypt）
4. ✅ 会话管理（Starlette SessionMiddleware）
5. ✅ 权限检查装饰器（admin可查看所有数据，普通用户只看自己数据）
6. ✅ 后端认证API（注册、登录、登出、获取用户信息）
7. ✅ 后端权限控制（所有API端点添加权限检查）
8. ✅ 前端认证服务和上下文
9. ✅ 前端登录/注册页面和组件
10. ✅ 前端路由保护
11. ✅ 内置admin用户自动初始化
12. ✅ 代码审查和修复

### 经验教训

#### 1. 用户认证系统的设计要点 ⭐重要
**经验**：
- 角色设计：内置admin角色，普通用户可注册
- 权限控制：admin可查看所有数据，普通用户只看自己的数据
- 数据隔离：所有业务模型（DataFlow、DataSnapshot、Dashboard）都要关联user_id
- 会话管理：使用SessionMiddleware管理用户会话
- 密码安全：使用bcrypt加密存储密码，不存储明文

**权限检查逻辑**：
```python
def can_access_resource(user: User, resource_user_id: int) -> bool:
    if user.role == "admin":
        return True
    return user.id == resource_user_id
```

#### 2. 会话管理库的选择 ⭐重要
**问题**：最初选择fastapi-session库，但遇到兼容性问题
**解决**：改用Starlette自带的SessionMiddleware，更稳定可靠
**经验**：
- Starlette的SessionMiddleware是内置的，无需额外安装
- 配置简单，只需设置secret_key
- 与FastAPI完美兼容
- 避免了第三方库的版本兼容性问题

**正确配置示例**：
```python
from starlette.middleware.sessions import SessionMiddleware

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="pbbi_session",
    max_age=86400 * 7  # 7天
)
```

#### 3. 数据库模型外键关联设计
**经验**：
- 所有业务模型都要添加user_id外键
- 使用ForeignKey关联User模型
- 设置ondelete="CASCADE"，删除用户时级联删除相关数据
- 添加索引提升查询性能

**模型设计示例**：
```python
class DataFlow(Base):
    __tablename__ = "data_flows"
    # ... 其他字段 ...
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user = relationship("User", back_populates="data_flows")
```

#### 4. 前端认证上下文设计
**经验**：
- 使用React Context管理认证状态
- 提供useAuth钩子方便组件访问认证信息
- 使用ProtectedRoute组件保护需要登录的路由
- 未登录用户自动跳转到登录页
- 登录状态持久化（可选）

**认证上下文设计**：
```javascript
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const login = async (username, password) => { ... };
  const register = async (username, password) => { ... };
  const logout = async () => { ... };
  
  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
```

#### 5. 密码安全最佳实践
**经验**：
- 使用bcrypt进行密码哈希
- 哈希轮数设置为12（平衡安全性和性能）
- 不存储明文密码
- 密码验证时使用bcrypt.checkpw
- 注册时检查用户名唯一性

**密码处理示例**：
```python
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
```

#### 6. 内置admin用户的自动初始化
**经验**：
- 应用启动时检查admin用户是否存在
- 不存在则自动创建
- admin用户名和密码可通过配置文件设置
- 首次登录后建议修改admin密码

**初始化示例**：
```python
@app.on_event("startup")
async def startup_event():
    await init_admin_user()
```

#### 7. API权限控制的实现方式
**经验**：
- 使用依赖注入获取当前用户
- 每个API端点都要检查权限
- admin用户可以访问所有资源
- 普通用户只能访问自己的资源
- 查询时添加user_id过滤条件

**权限检查示例**：
```python
@router.get("/data-flows")
async def get_data_flows(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(DataFlow)
    if current_user.role != "admin":
        query = query.filter(DataFlow.user_id == current_user.id)
    return query.all()
```

#### 8. ACP流程的完整执行 ⭐重要
**经验**：
- 本次迭代完整执行了ACP流程：
  1. 架构师：更新需求分析和架构设计
  2. 项目经理：更新开发计划
  3. 开发人员：实现用户认证模块
  4. 代码审查人员：审查代码
  5. ACP专家：总结经验教训
- 流程确保了开发质量和进度
- 每个环节都有明确的输出文档

### 改进建议（补充）

109. **双因素认证改进**：建议添加双因素认证（2FA）提升安全性
110. **密码重置改进**：建议添加密码重置功能（通过邮箱或短信）
111. **用户管理改进**：admin用户可以管理其他用户（禁用、删除等）
112. **权限细化改进**：建议添加更细粒度的权限控制（如只读、编辑等）
113. **审计日志改进**：建议添加用户操作审计日志
114. **会话超时改进**：建议添加会话超时自动登出功能
115. **CSRF保护改进**：建议添加CSRF保护
116. **Rate Limiting改进**：建议添加API限流防止暴力破解

---

## 迭代 3.3 经验总结（UI/UX优化）

### 本次迭代完成的功能
1. ✅ 设计商业数据分析项目的配色方案和设计系统
2. ✅ 优化登录页面设计（左右分栏布局、品牌展示）
3. ✅ 优化导航栏样式（白色简约风格）
4. ✅ 优化按钮和表单样式（统一圆角、阴影、过渡动画）
5. ✅ 优化页面容器样式（更大圆角、更柔和阴影）

### 经验教训

#### 1. 商业数据分析软件的配色要点 ⭐重要
**经验**：
- 主色调选择蓝色系（#2563eb），传达专业、信任的感觉
- 辅助色使用紫色渐变（#667eea → #764ba2），增加现代感
- 中性色使用灰色系，确保良好的可读性
- 避免过于鲜艳的颜色，保持专业稳重的风格

**配色方案**：
```css
--primary: #2563eb;          /* 主色 - 蓝色 */
--bg-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
--text-primary: #111827;     /* 深灰 - 正文 */
--text-secondary: #4b5563;   /* 中灰 - 辅助文字 */
--bg-primary: #f3f4f6;       /* 浅灰 - 背景 */
```

#### 2. 登录页面的设计要点 ⭐重要
**经验**：
- 采用左右分栏布局，左侧展示品牌信息，右侧是登录表单
- 左侧使用渐变背景，右侧使用白色卡片，形成鲜明对比
- 品牌展示区包含：logo、产品名称、标语、数据统计
- 登录/注册切换采用标签页式设计，视觉清晰
- 登录按钮使用渐变背景，悬停时上浮效果

**布局结构**：
```
┌───────────────────────────────────────────┐
│  渐变背景 (左侧)  │  白色卡片 (右侧)    │
│                    │                      │
│  • Logo            │  • 登录/注册切换   │
│  • 产品名称        │  • 登录表单        │
│  • 标语            │  • 注册表单        │
│  • 数据统计        │  • 管理员账号提示 │
│                    │                      │
└───────────────────────────────────────────┘
```

#### 3. 导航栏的设计要点
**经验**：
- 从彩色渐变改为白色简约风格，更显专业
- 添加底部边框，与内容区形成清晰分隔
- 导航链接采用标签页式设计，激活状态使用主色
- 品牌logo使用渐变色块，提升识别度

#### 4. 按钮和表单的设计要点
**经验**：
- 按钮使用渐变背景，悬停时上浮并增强阴影
- 表单输入框使用圆角设计，聚焦时显示蓝色边框和阴影
- 统一使用rem单位，确保响应式一致性
- 过渡动画时间控制在200ms，既流畅又不拖沓

#### 5. CSS变量的使用要点
**经验**：
- 定义完整的设计系统变量（颜色、圆角、阴影、过渡）
- 统一使用变量，便于后续主题切换
- 变量命名清晰，易于理解和维护

**变量示例**：
```css
--radius-sm: 6px;
--radius-md: 10px;
--radius-lg: 14px;
--radius-xl: 20px;
--transition-fast: 150ms;
--transition-base: 200ms;
--transition-slow: 300ms;
```

#### 6. 内联样式vs CSS类的权衡
**经验**：
- 登录页面使用内联样式，便于快速迭代和调整
- 通用组件使用CSS类，确保样式复用和一致性
- 根据具体场景选择合适的方式，不必拘泥于一种

### 改进建议（补充）

117. **图标系统改进**：建议引入一致的图标库（如Heroicons或Lucide）
118. **主题切换改进**：建议添加深色/浅色主题切换功能
119. **响应式优化改进**：建议完善移动端响应式布局
120. **加载状态改进**：建议添加骨架屏加载状态
121. **动画系统改进**：建议统一页面切换和交互动画
122. **设计文档改进**：建议创建组件库和设计系统文档

---

## 迭代 3.4 经验总结（便携版生成）

### 本次迭代遇到的问题

1. ❌ CORS配置只允许localhost:3000，便携版在其他机器无法使用
2. ❌ serve包安装不完整，缺少build目录
3. ❌ 前端启动脚本路径错误

### 经验教训

#### 1. 便携版CORS配置要点 ⭐重要
**问题**：CORS配置只允许`http://localhost:3000`，便携版在其他IP访问时跨域失败

**解决方案**：使用正则表达式匹配任何端口3000的origin
```python
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://.*:3000|http://localhost:3000",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**教训**：便携版可能在任何网络环境下运行，CORS配置必须支持动态origin

#### 2. serve包安装要点 ⭐重要
**问题**：npm install -g serve时，有时只安装元数据，不安装build目录

**解决方案**：
```powershell
# 方法1：指定prefix安装
npm install -g serve --prefix ./npm-global

# 方法2：进入目录安装
cd npm-global
npm install serve
```

**验证**：安装后必须检查`node_modules/serve/build/main.js`是否存在

#### 3. 前端启动脚本要点
**问题**：serve.cmd脚本使用相对路径，在便携版中可能找不到node.exe

**解决方案**：直接使用node.exe执行serve的main.js
```batch
"%SCRIPT_DIR%runtime\node\node.exe" "%SCRIPT_DIR%runtime\npm-global\node_modules\serve\build\main.js" -s . -l 3000
```

#### 4. 便携版目录结构要点
**正确的目录结构**：
```
pb-bi-portable/
├── backend/
│   ├── src/           # 后端代码
│   ├── libs/          # Python依赖
│   └── requirements.txt
├── frontend/
│   ├── index.html     # 前端入口
│   └── assets/        # 前端资源
├── runtime/
│   ├── python/        # Python便携版
│   │   └── python311._pth  # 必须配置正确
│   ├── node/          # Node.js便携版
│   └── npm-global/
│       └── node_modules/serve/build/main.js  # 必须存在
├── start.bat
├── start-backend.bat
├── start-frontend.bat
└── stop.bat
```

#### 5. Python便携版配置要点
**python311._pth文件配置**：
```
python311.zip
.
libs
../../backend/libs
Scripts

import site
```
**注意**：必须添加`import site`才能使用pip

### 改进建议（补充）

123. **便携版验证脚本**：建议创建验证脚本，检查所有必需文件是否存在
124. **便携版测试流程**：每次生成便携版后，在干净环境测试
125. **依赖版本锁定**：建议锁定Python和Node.js版本号

---

## 迭代 3.5 经验总结（私有化部署支持）

### 本次迭代完成的功能
1. ✅ 数据库模型添加is_private和private_api_url字段
2. ✅ MingDaoService支持自定义base_url参数
3. ✅ 后端API更新创建/更新接口
4. ✅ 前端添加私有化部署勾选框
5. ✅ 前端添加API地址输入框和格式提示
6. ✅ 修复is_private字段类型转换问题
7. ✅ 更新便携版

### 经验教训

#### 1. 数据库布尔字段处理要点 ⭐重要
**问题**：
- SQLite数据库中布尔值存储为整数(0/1)
- Pydantic模型期望布尔值
- 直接使用会导致类型不匹配错误

**解决方案**：
```python
class DataFlowResponse(BaseModel):
    is_private: bool = False
    
    @model_validator(mode='before')
    @classmethod
    def convert_is_private(cls, data):
        if hasattr(data, 'is_private'):
            val = data.is_private
            if isinstance(val, int):
                data.is_private = bool(val)
        return data
```

**教训**：
- 使用SQLAlchemy+SQLite时，布尔字段会自动转换为整数
- 需要使用Pydantic的model_validator显式转换
- 或者在所有使用点显式用bool()转换

#### 2. 条件字段清空要点 ⭐重要
**问题**：
- 当不勾选"私有化部署"时，private_api_url应该清空
- 如果不清空，会残留旧值导致连接错误

**解决方案**：
```python
# 创建时
is_private_val = 1 if dataflow.is_private else 0
private_api_url_val = dataflow.private_api_url if dataflow.is_private else None

# 更新时
if 'is_private' in update_data:
    is_private_val = 1 if update_data['is_private'] else 0
    update_data['is_private'] = is_private_val
    
    if not is_private_val:
        update_data['private_api_url'] = None
```

**教训**：
- 互斥的条件字段需要联动处理
- 当条件不满足时，相关字段必须清空
- 这可以避免残留数据导致的bug

#### 3. API地址格式提示要点
**问题**：
- 用户容易填写包含路径的完整URL（如https://api.mingdao.com/v3/app）
- 应该只填写基础URL（如https://api.mingdao.com）

**解决方案**：
- 在输入框下方添加清晰的提示文字
- 示例："只填写基础地址，不要包含 /v3/app 等路径"
- placeholder也要正确示例

#### 4. 现有数据修复要点
**问题**：
- 已有数据可能包含错误值（如is_private=1但private_api_url格式错误）
- 需要在发现问题后修复现有数据

**解决方案**：
```python
# 创建临时脚本修复数据
dataflow = db.query(DataFlow).filter(DataFlow.id == 3).first()
dataflow.is_private = 0
dataflow.private_api_url = None
db.commit()
```

### 改进建议（补充）

126. **API地址验证**：建议添加API地址格式验证（只包含域名和端口）
127. **数据库迁移脚本**：建议创建数据库迁移脚本，而不是临时脚本
128. **表单验证**：建议添加前端表单验证，确保数据格式正确
129. **输入提示**：建议在输入框内添加内联提示（如tooltip）

---

## ⚠️ 重要提醒：执行计划前请先温习经验教训

在开始任何任务之前，请先执行以下步骤：

1. **阅读project_rules.md**：搜索是否有类似任务的经验教训
2. **检查历史问题**：查看是否遇到过类似问题及解决方案
3. **避免重复踩坑**：应用之前的经验教训，避免犯同样的错误

**搜索关键词示例**：
- 便携版 → 搜索"便携版"、"CORS"、"serve"
- 认证 → 搜索"认证"、"session"、"bcrypt"
- 数据库 → 搜索"数据库"、"migration"、"user_id"

---

## 版本历史

| 版本 | 日期 | 迭代 | 说明 |
|------|------|------|------|
| 1.0 | 2026-02-14 | 迭代 1.1 | 初始版本，记录迭代 1.1 的经验教训 |
| 2.13 | 2026-02-22 | 迭代 2.13 | 记录迭代 2.13 经验教训，第一阶段完成总结 |
| 3.0 | 2026-02-22 | 迭代 3.0 | 记录迭代 3.0 经验教训，可部署版本生成完成 |
| 3.2 | 2026-02-22 | 迭代 3.2 | 记录迭代 3.2 经验教训，用户认证模块完成 |
| 3.3 | 2026-02-22 | 迭代 3.3 | 记录迭代 3.3 经验教训，UI/UX优化完成 |
| 3.4 | 2026-02-22 | 迭代 3.4 | 记录迭代 3.4 经验教训，便携版生成问题修复 |
| 3.5 | 2026-02-22 | 迭代 3.5 | 记录迭代 3.5 经验教训，私有化部署支持完成
