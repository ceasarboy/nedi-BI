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
- 经验教训记录到 project_rules.md
- 进度信息记录到 docs/开发计划.md

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

## 迭代 3.6 经验总结（便携版数据库迁移修复与测试）

### 本次迭代完成的功能
1. ✅ 修复数据库迁移脚本，添加data_snapshots表的user_id列检查
2. ✅ 修复数据库迁移脚本，添加dashboards表的user_id列检查
3. ✅ 更新便携版后端代码到最新版本
4. ✅ 在测试环境运行数据库迁移验证
5. ✅ 编写测试脚本验证修复效果
6. ✅ 测试快照保存功能（带user_id）
7. ✅ 便携版在其他电脑上运行成功

### 经验教训

#### 1. 数据库迁移脚本的完整性 ⭐重要
**问题**：
- 之前的迁移脚本只检查了data_flows表的user_id列
- 但data_snapshots和dashboards表也需要user_id列
- 导致在其他电脑上保存快照时出现"no such column: user_id"错误

**解决**：
```python
# 必须检查所有包含user_id的表
print("检查 data_snapshots 表结构...")
cursor.execute("PRAGMA table_info(data_snapshots)")
columns = [column[1] for column in cursor.fetchall()]

if 'user_id' not in columns:
    print("添加 user_id 列...")
    cursor.execute("ALTER TABLE data_snapshots ADD COLUMN user_id INTEGER")

# 同样检查dashboards表
print("\n检查 dashboards 表结构...")
cursor.execute("PRAGMA table_info(dashboards)")
columns = [column[1] for column in cursor.fetchall()]

if 'user_id' not in columns:
    print("添加 user_id 列...")
    cursor.execute("ALTER TABLE dashboards ADD COLUMN user_id INTEGER")
```

**教训**：
- 数据库迁移脚本必须完整覆盖所有受影响的表
- 每次添加新字段时，要检查所有相关模型
- 不能只检查一部分表，要系统性地检查

#### 2. 测试验证的重要性 ⭐重要
**经验**：
- 修复问题后，必须编写测试脚本验证
- 测试脚本应该：
  1. 检查数据库表结构
  2. 测试插入带user_id的数据
  3. 验证数据是否正确保存
  4. 清理测试数据

**测试脚本要点**：
```python
# 1. 检查表结构
cursor.execute("PRAGMA table_info(data_snapshots)")
columns = [column[1] for column in cursor.fetchall()]
print(f"✓ user_id 列存在: {'user_id' in columns}")

# 2. 测试插入
cursor.execute("""
    INSERT INTO data_snapshots (user_id, data_flow_id, name, worksheet_id, fields, data)
    VALUES (?, ?, ?, ?, ?, ?)
""", (test_user_id, test_dataflow_id, test_name, test_worksheet_id, test_fields, test_data))

# 3. 验证数据
cursor.execute("SELECT id, user_id, name FROM data_snapshots WHERE id = ?", (snapshot_id,))
result = cursor.fetchone()
print(f"✓ user_id 正确设置为: {result[1]}")
```

#### 3. 便携版数据库路径一致性
**问题**：
- 迁移脚本从 backend/config/pb_bi.db 读取
- 但实际运行时从 config/pb_bi.db 读取
- 导致两个数据库不一致

**教训**：
- 迁移脚本和应用必须使用同一个数据库路径
- 要明确数据库位置，避免混淆
- 测试前要确认数据库路径正确

#### 4. 用户反馈驱动的修复 ⭐重要
**经验**：
- 用户反馈"便携版在其他机子上运行出现问题"
- 立即响应，分析错误信息
- 错误信息很明确："no such column: user_id"
- 快速定位问题并修复
- 修复后立即测试验证

**流程**：
1. 接收用户反馈 → 2. 分析错误信息 → 3. 定位问题根因 → 4. 修复问题 → 5. 测试验证 → 6. 交付用户

#### 5. 便携版使用流程标准化
**经验**：
- 便携版在其他电脑上使用时，必须有明确的流程
- 标准流程：
  1. 复制便携版文件夹到目标电脑
  2. 先运行数据库迁移：cd backend; python migrate_db.py
  3. 然后启动服务：start.bat
- 必须在文档中明确说明

**使用说明文档要点**：
```
## 首次使用便携版

1. 复制 pb-bi-portable 文件夹到目标位置
2. 运行数据库迁移（重要！）：
   cd backend
   python migrate_db.py
3. 启动服务：
   start.bat
```

#### 6. 问题复现与验证
**经验**：
- 修复问题后，要在类似环境中复现验证
- 本次在本地测试环境模拟了其他电脑的情况
- 使用测试脚本验证修复效果
- 确保所有功能正常后再交付

### 改进建议（补充）

130. **数据库迁移自动化**：建议在便携版启动时自动检测并运行迁移
131. **迁移日志记录**：建议记录每次数据库迁移的日志
132. **回滚机制**：建议添加数据库迁移的回滚机制
133. **迁移版本管理**：建议为每次迁移添加版本号
134. **集成测试**：建议添加便携版的集成测试流程
135. **用户提示优化**：建议在启动脚本中提示用户先运行迁移

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
| 3.5 | 2026-02-22 | 迭代 3.5 | 记录迭代 3.5 经验教训，私有化部署支持完成 |
| 3.6 | 2026-02-23 | 迭代 3.6 | 记录迭代 3.6 经验教训，便携版数据库迁移修复与测试 |

---

## 迭代 4.0 经验总结（技术栈升级：AI集成准备）

### 本次迭代完成的功能
1. ✅ 创建技术栈调整实施计划
2. ✅ 更新requirements.txt添加新依赖（sqlmodel, aiosqlite, sqlglot, chromadb）
3. ✅ 创建异步数据库连接模块（database_async.py）
4. ✅ 创建SQLGlot PostgreSQL到SQLite转换模块
5. ✅ 集成ChromaDB PersistentClient向量检索
6. ✅ 创建SQLModel版本的数据库模型
7. ✅ 创建向量检索API端点
8. ✅ 创建技术栈验证测试脚本
9. ✅ 修复SQL转换模块的语法错误
10. ✅ 创建异步权限验证模块（permissions_async.py）
11. ✅ 创建异步API示例（config_async.py）
12. ✅ 项目测试通过，基本功能正常运行

### 经验教训

#### 1. 异步数据库架构要点 ⭐重要
**经验**：
- 使用SQLModel + aiosqlite实现异步数据库操作
- 通过DATABASE_URL替换为sqlite+aiosqlite:///实现异步驱动
- 使用async_sessionmaker创建异步会话工厂
- 所有数据库操作使用await异步调用

**配置示例**：
```python
DATABASE_URL_ASYNC = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///"\)

engine = create_async_engine(DATABASE_URL_ASYNC, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

#### 2. SQLGlot语法转换要点 ⭐重要
**经验**：
- PostgreSQL有大量SQLite不支持的语法
- 需要开发专门的转换模块处理
- Python re.sub() 支持 flags 参数，但 str.replace() 不支持
- 修复了多次使用 flags 导致的语法错误

**常见转换规则**：
- INTERVAL → 移除或转换
- NOW() → datetime('now')
- CURRENT_TIMESTAMP → datetime('now')
- DATE_TRUNC → strftime
- EXTRACT → strftime
- ILIKE → LIKE
- TRUE/FALSE → 1/0
- ::类型转换 → 移除
- RETURNING → 移除
- 窗口函数 → 标记（需SQLite 3.25.0+）

**双重保障策略**：
1. 开发SQL语法自动转换模块
2. 在AI提示词中明确声明SQLite语法要求

#### 3. ChromaDB持久化配置要点
**经验**：
- 使用PersistentClient指定持久化路径
- 向量数据存储在本地SQLite文件中
- 服务重启后数据不丢失
- 支持元数据和向量一体化存储

**配置示例**：
```python
from chromadb.config import Settings

client = chromadb.PersistentClient(
    path="./config/vector_data"
)
```

#### 4. SQLModel模型设计
**经验**：
- SQLModel是SQLAlchemy和Pydantic的结合
- 同时支持ORM和数据验证
- 使用Field定义字段，支持默认值、外键等
- Relationship定义模型关系

**模型示例**：
```python
class DataFlow(SQLModel, table=True):
    __tablename__ = "data_flows"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    name: str = Field(default="", index=True)
```

#### 5. 向量检索API设计
**经验**：
- 提供embedding生成接口
- 支持向量添加、查询、删除
- 支持元数据过滤
- 提供集合管理接口

**API端点**：
- POST /api/vector/embeddings - 生成embedding
- POST /api/vector/add - 添加向量
- POST /api/vector/query - 查询向量
- GET /api/vector/collections - 列出集合

#### 6. 异步API开发要点 ⭐重要
**经验**：
- 异步API需要使用AsyncSession
- 使用select()替代query()
- 使用await执行数据库操作
- 需要创建独立的异步权限验证模块

**异步API示例**：
```python
@router.get("/{dataflow_id}")
async def get_dataflow(
    dataflow_id: int,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    query = select(DataFlow).where(DataFlow.id == dataflow_id)
    result = await db.execute(query)
    dataflow = result.scalar_one_or_none()
    return dataflow
```

#### 7. 模块导入路径问题
**经验**：
- 异步模块需要正确导入依赖
- User模型在 src.models.user 中，不在 src.models.config 中
- 修复了 ImportError: cannot import name 'User' from 'src.models.config'

### 改进建议（补充）

136. **异步API改造**：建议将现有同步API逐步改造为异步模式
137. **embedding模型优化**：建议使用轻量级embedding模型以提升性能
138. **向量索引优化**：建议配置合适的索引类型以提升检索速度
139. **SQL转换测试**：建议创建完整的100种PostgreSQL语法测试集
140. **性能监控**：建议添加API响应时间监控

### 技术栈升级文件清单

| 文件 | 说明 |
|------|------|
| requirements.txt | 添加sqlmodel, aiosqlite, sqlglot, chromadb |
| src/core/database_async.py | 异步数据库连接模块 |
| src/core/sql_converter.py | PostgreSQL到SQLite转换模块 |
| src/core/vector_store.py | ChromaDB向量检索模块 |
| src/core/permissions_async.py | 异步权限验证模块 |
| src/models/config_sqlmodel.py | SQLModel版本模型 |
| src/api/vector.py | 向量检索API |
| src/api/config_async.py | 异步数据流API（示例） |
| src/mcp/service.py | MCP服务基类 |
| src/mcp/tools.py | PB-BI MCP工具集 |
| src/api/mcp.py | MCP API端点 |
| src/main.py | 注册MCP API路由 |
| docs/技术栈调整实施计划.md | 实施计划文档 |
| docs/JoyAgent整合方案.md | JoyAgent整合方案 |
| docs/元数据增强与语义映射Prompt.md | LLM提示词 |
| docs/图表推荐Prompt.md | 图表推荐提示词 |
| docs/PB-BI-MCP集成测试计划.md | 测试计划 |
| scripts/chart_recommend.py | 图表推荐CLI工具 |
| scripts/ingest_schema_docs.py | Schema文档导入脚本 |
| scripts/sync_metadata.py | 元数据同步脚本 |
| tests/test_mcp_unit.py | MCP单元测试 (27个) |
| tests/test_mcp_integration.py | MCP集成测试 (17个) |
| test_tech_stack.py | 技术栈验证测试脚本 |

---

### 迭代 4.1 经验总结（MCP工具集成与测试）

#### 本次迭代完成的功能
1. ✅ 创建JoyAgent整合方案文档
2. ✅ 创建MCP服务基类（src/mcp/service.py）
3. ✅ 创建7个PB-BI MCP工具
   - pbbi_get_dataflows - 获取数据流列表
   - pbbi_get_dataflow - 获取单个数据流
   - pbbi_query_data - 数据查询
   - pbbi_get_schema - 获取数据库Schema
   - pbbi_get_snapshots - 获取快照列表
   - pbbi_get_snapshot_data - 获取快照数据
   - pbbi_get_dashboards - 获取看板列表
4. ✅ 创建MCP API端点
5. ✅ 创建测试计划文档
6. ✅ 编写单元测试（27个测试用例）
7. ✅ 编写集成测试（17个测试用例）
8. ✅ 全部44个测试用例通过

#### 经验教训

##### 1. MCP工具设计模式 ⭐重要
**经验**：
- MCP服务需要分离元数据（MCPTool）和执行逻辑（handler）
- 使用register_tool注册元数据，使用register_handler注册执行器
- 工具执行时需要先检查handler是否存在

##### 2. 测试驱动开发
**经验**：
- 先编写测试用例，再实现功能
- 测试覆盖正常流程、边界条件、异常场景
- 单元测试：27个，覆盖所有工具类
- 集成测试：17个，覆盖API端点

##### 3. API响应格式设计
**经验**：
- 统一响应格式：{"success": true/false, "data": ..., "error": ...}
- 嵌套数据需要正确处理：response.data.data

##### 4. ACP开发模式实践
**经验**：
- 架构师：输出Prompt文档和方案
- 开发人员：实现代码和测试
- 测试人员：执行测试验证
- 完整记录经验教训

## ⚠️ 重要提醒：执行计划前请先温习经验教训

在开始任何任务之前，请先执行以下步骤：

1. **阅读project_rules.md**：搜索是否有类似任务的经验教训
2. **检查历史问题**：查看是否遇到过类似问题及解决方案
3. **避免重复踩坑**：应用之前的经验教训，避免犯同样的错误

**搜索关键词示例**：
- 便携版 → 搜索"便携版"、"CORS"、"serve"
- 认证 → 搜索"认证"、"session"、"bcrypt"
- 数据库 → 搜索"数据库"、"migration"、"user_id"
- AI集成 → 搜索"向量"、"ChromaDB"、"SQLModel"、"异步"

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
| 3.5 | 2026-02-22 | 迭代 3.5 | 记录迭代 3.5 经验教训，私有化部署支持完成 |
| 3.6 | 2026-02-23 | 迭代 3.6 | 记录迭代 3.6 经验教训，便携版数据库迁移修复与测试 |
| 4.0 | 2026-02-23 | 迭代 4.0 | 记录迭代 4.0 经验教训，技术栈升级AI集成准备完成 |
| 4.2 | 2026-03-05 | 迭代 4.2 | AI Agent与MCP工具集成、图表生成功能完成 |
| 4.3 | 2026-03-05 | 迭代 4.3 | 图表功能完善（中文字体、缓存、验证、放大下载） |
| 4.4 | 2026-03-06 | 迭代 4.4 | 图表类型扩展至11种，测试覆盖率88% |
| 4.5 | 2026-03-06 | 迭代 4.5 | 图表类型扩展至19种，覆盖前端所有图表 |
| 4.6 | 2026-03-06 | 迭代 4.6 | AI对话列表功能、设置页面、UI风格切换 |

---

## 迭代 4.6 经验总结（AI对话列表与设置页面）

### 本次迭代完成的功能
1. ✅ AI对话列表功能
   - 左侧显示历史对话列表
   - 点击切换对话，加载历史消息
   - 新建/关闭对话功能
   - 上下文超限提醒
2. ✅ 设置页面
   - 3种UI风格切换（现代/经典/极简）
   - 8种主色调选择
   - 字体大小调整
   - 暗黑模式开关
3. ✅ AI模型设置
   - 支持4个AI提供商（DeepSeek/OpenAI/硅基流动/智谱AI）
   - 动态获取用户可用模型（硅基流动API集成）
   - API密钥管理
   - 温度/Token参数配置
4. ✅ AI助手图标优化
   - 使用SVG替代emoji
   - 可爱的机器人形象

### 经验教训

#### 1. 数据库字段类型一致性 ⭐重要
**问题**：`is_enabled` 字段在数据库中是字符串类型，但前端获取到的是布尔值

**解决**：
- 前端统一使用 `String(field.is_enabled).toLowerCase() === 'true'` 判断
- 保存时确保发送字符串 `'true'` 或 `'false'`

**教训**：前后端数据类型必须保持一致，建议使用布尔类型而非字符串

#### 2. 硅基流动API集成 ⭐重要
**问题**：获取用户可用模型需要正确的API参数

**解决**：
```python
response = await client.get(
    "https://api.siliconflow.cn/v1/models",
    headers={"Authorization": f"Bearer {api_key}"},
    params={"type": "text"},  # 只获取文本模型
    timeout=15.0
)
```

**教训**：第三方API集成需要仔细阅读官方文档

#### 3. CSS变量实现全局主题切换 ⭐重要
**经验**：
- 创建 `variables.css` 定义CSS变量
- 使用 `document.documentElement.style.setProperty()` 动态修改变量
- 使用 `document.body.setAttribute('data-style', style)` 切换风格
- 暗黑模式使用 `body.dark-mode` 类选择器

**变量设计**：
```css
:root {
  --primary-color: #3b82f6;
  --primary-hover: #2563eb;
  --primary-light: #eff6ff;
  --font-size-base: 16px;
  --bg-primary: #ffffff;
  --text-primary: #1e293b;
  --border-radius: 12px;
}

body.dark-mode {
  --bg-primary: #0f172a;
  --text-primary: #f1f5f9;
}
```

#### 4. 前端SSE流解析 ⭐重要
**问题**：前端没有正确解析SSE流式数据格式 `data: {...}`

**解决**：
```javascript
const lines = buffer.split('\n')
for (const line of lines) {
  if (line.startsWith('data: ')) {
    const event = JSON.parse(line.slice(6))
    if (event.type === 'content') {
      fullContent += event.content
    }
  }
}
```

#### 5. React Router Future Flags警告
**问题**：控制台显示React Router v7兼容性警告

**解决**：在BrowserRouter中添加future flags：
```jsx
<BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
```

### 待解决问题

| 问题 | 优先级 | 状态 |
|------|--------|------|
| 数据设置字段勾选失效 | 高 | 待修复 |
| UI设置全局生效范围 | 中 | 部分生效 |

### 文件变更清单

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| src/models/conversation.py | 新增 | 对话数据库模型 |
| src/models/settings.py | 新增 | 设置数据库模型 |
| src/api/conversation.py | 新增 | 对话API接口 |
| src/api/settings.py | 新增 | 设置API接口 |
| src/ai/agent.py | 更新 | 支持session_id和历史加载 |
| src/api/ai.py | 更新 | 支持session_id |
| frontend/src/pages/AIPage.jsx | 更新 | 对话列表UI |
| frontend/src/pages/SettingsPage.jsx | 新增 | 设置页面 |
| frontend/src/styles/AIPage.css | 更新 | 对话列表样式 |
| frontend/src/styles/SettingsPage.css | 新增 | 设置页面样式 |
| frontend/src/styles/variables.css | 新增 | CSS变量定义 |

### 改进建议

151. **字段勾选问题**：需要深入排查React状态更新和渲染问题
152. **UI设置持久化**：建议将UI设置保存到localStorage
153. **对话搜索**：建议添加对话搜索功能
154. **模型价格显示**：建议显示各模型的调用价格
155. **API密钥加密**：建议对API密钥进行加密存储

## 迭代 4.2 经验总结（AI Agent与图表生成功能）

### 本次迭代完成的功能
1. ✅ AI Agent与MCP工具集成测试
2. ✅ 修复数据快照查询问题（database_mcp.py使用正确的数据库pb_bi.db）
3. ✅ 创建图表生成MCP工具（chart_mcp.py）
   - pbbi_generate_bar_chart - 柱状图
   - pbbi_generate_pie_chart - 饼图
   - pbbi_generate_line_chart - 折线图
   - pbbi_generate_scatter_chart - 散点图
   - pbbi_generate_box_plot - 箱线图
4. ✅ 安装matplotlib依赖
5. ✅ 前端AI页面支持markdown渲染图片（react-markdown）
6. ✅ 更新AI Agent系统提示，支持图表生成能力

### 经验教训

#### 1. MCP工具数据库路径问题 ⭐重要
**问题**：database_mcp.py 原本使用独立的 snapshots.db 数据库，实际数据存储在 pb_bi.db

**解决**：重写 database_mcp.py 使用 `_get_main_db_connection()` 连接 pb_bi.db

**教训**：MCP工具必须与主应用使用同一数据库

#### 2. 图表生成工具设计要点
**经验**：
- 使用matplotlib生成图表，保存为PNG文件
- 图表存储在 config/charts/ 目录
- 通过 /api/charts/{filename} 静态文件服务访问
- 返回 chart_url 供前端展示

#### 3. 前端Markdown渲染图片 ⭐重要
**问题**：AI返回的图表URL是纯文本，前端不渲染图片

**解决**：
- 安装 react-markdown 和 remark-gfm
- 使用 `<ReactMarkdown>` 组件渲染AI回复
- AI系统提示要求使用markdown图片格式：`![图表标题](URL)`

#### 4. matplotlib安装问题
**解决**：使用清华镜像源安装：`pip install matplotlib -i https://pypi.tuna.tsinghua.edu.cn/simple`

#### 5. AI系统提示设计要点
**经验**：
- 明确告知服务器地址：http://localhost:8000
- 要求AI返回完整URL而非相对路径
- 要求使用markdown图片格式展示图表

### 文件变更清单

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| src/mcp/database_mcp.py | 重写 | 使用pb_bi.db数据库 |
| src/mcp/chart_mcp.py | 新增 | 图表生成MCP工具 |
| src/mcp/analysis_mcp.py | 更新 | 使用pb_bi.db数据库 |
| src/api/mcp.py | 更新 | 注册图表工具 |
| src/main.py | 更新 | 添加图表静态文件服务 |
| src/ai/agent.py | 更新 | 系统提示添加图表能力 |
| src/ai/llm_client.py | 更新 | 添加图表工具定义 |
| frontend/src/pages/AIPage.jsx | 更新 | 使用ReactMarkdown渲染 |
| frontend/src/styles/AIPage.css | 更新 | 添加图片样式 |
| frontend/package.json | 更新 | 添加react-markdown依赖 |
| tests/test_database_mcp_unit.py | 更新 | 适配新API |
| tests/test_ai_agent_integration.py | 新增 | AI Agent集成测试 |

### 改进建议

141. **图表样式优化**：建议添加中文字体支持，避免中文乱码
142. **图表交互**：建议前端支持图表放大、下载功能
143. **图表缓存**：建议添加图表缓存机制，避免重复生成
144. **错误处理**：建议图表生成失败时返回友好提示
145. **数据验证**：建议添加字段类型验证，数值字段才能生成图表

---

## 迭代 4.3 经验总结（图表功能完善）

### 本次迭代完成的功能
1. ✅ 图表中文字体支持（SimHei/Microsoft YaHei）
2. ✅ 图表缓存机制（内存缓存，避免重复生成）
3. ✅ 字段类型验证（数值字段验证）
4. ✅ 图表放大/下载功能（前端模态框）

### 经验教训

#### 1. matplotlib中文字体配置要点 ⭐重要
**经验**：
- Windows系统使用SimHei或Microsoft YaHei字体
- macOS使用PingFang字体
- Linux使用WenQuanYi Micro Hei字体
- 需要设置`plt.rcParams['axes.unicode_minus'] = False`解决负号显示问题

**配置代码**：
```python
def _setup_chinese_font():
    import matplotlib.pyplot as plt
    import platform
    
    system = platform.system()
    if system == "Windows":
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
    elif system == "Darwin":
        plt.rcParams['font.sans-serif'] = ['PingFang']
    plt.rcParams['axes.unicode_minus'] = False
```

#### 2. 图表缓存设计要点
**经验**：
- 使用内存字典缓存图表结果
- 缓存键使用MD5哈希（图表类型+参数）
- 设置缓存上限（100个），超过时清理最旧的
- 相同参数直接返回缓存结果，避免重复生成

#### 3. 字段类型验证要点 ⭐重要
**经验**：
- 数值图表需要验证字段是否为数值类型
- 使用`pd.api.types.is_numeric_dtype()`检查
- 尝试转换为数值类型`pd.to_numeric()`
- 非数值字段返回友好错误提示

#### 4. 前端图片模态框设计
**经验**：
- 使用React状态管理模态框显示
- 点击图片打开模态框
- 模态框支持点击关闭
- 提供下载按钮，- CSS使用`position: fixed`实现全屏遮罩

### 文件变更清单

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| src/mcp/chart_mcp.py | 重写 | 添加中文字体、缓存、验证功能 |
| frontend/src/pages/AIPage.jsx | 更新 | 添加图片模态框 |
| frontend/src/styles/AIPage.css | 更新 | 添加模态框样式 |
| docs/架构设计.md | 更新 | 添加图表功能设计 |
| docs/开发计划.md | 更新 | 添加迭代4.3计划 |

### 改进建议（补充）

146. **图表持久化**：建议将图表保存到数据库而非文件系统
147. **图表模板**：建议支持自定义图表样式模板
148. **图表导出**：建议支持导出为PDF/SVG格式
149. **图表标注**：建议支持在图表上添加数据标注
150. **图表交互**：建议支持图表缩放、平移功能

#### 5. DeepSeek工具调用解析 ⭐重要
**问题**：
- DeepSeek模型返回的工具调用使用文本格式，而非API级别的`tool_calls`字段
- 使用全角字符：`｜`(U+FF5C) 和 `▁`(U+2581)
- 正则表达式必须使用正确的Unicode字符

**解决**：
```python
# 错误（半角字符）
pattern = r'<\|tool_calls_begin\|>...'

# 正确（全角字符）
pattern = r'function<｜tool▁sep｜>(\w+).*?```json\s*(\{.*?\})\s*```'
```

**教训**：
- 不同LLM模型返回的工具调用格式可能不同
- 需要编写单元测试验证解析逻辑
- 正则表达式中的字符编码必须与实际字符完全匹配

### 单元测试覆盖

| 模块 | 测试文件 | 测试数量 | 覆盖内容 |
|------|----------|----------|----------|
| chart_mcp.py | test_chart_mcp_unit.py | 17 | 缓存、验证、工具参数、工具执行 |
| agent.py | test_agent_tool_parsing.py | 11 | 工具解析、全角字符、系统提示 |

---

## 迭代 4.4 经验总结（图表类型扩展至100%覆盖）

### 本次迭代完成的功能
1. ✅ 扩展图表类型从5种到11种
   - 基础图表：柱状图、饼图、折线图、散点图、箱线图、直方图
   - 高级图表：热力图、雷达图、漏斗图、仪表盘
   - 联动图表：组合图（柱状图+折线图）
2. ✅ 设计统一的BaseChartTool抽象基类
3. ✅ 编写64个单元测试，覆盖率88%
4. ✅ 更新AI Agent系统提示，支持所有图表类型

### 经验教训

#### 1. 抽象基类设计模式 ⭐重要
**经验**：
- 使用ABC抽象基类定义统一接口
- 子类必须实现：get_name()、get_description()、get_parameters()、execute()
- 公共方法放在基类：_get_data_from_snapshot()、_create_result()、_create_error()
- 代码复用率大幅提升

**基类设计**：
```python
class BaseChartTool(ABC):
    @abstractmethod
    def get_name(self) -> str: pass
    
    @abstractmethod
    def get_description(self) -> str: pass
    
    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]: pass
    
    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]: pass
    
    def _get_data_from_snapshot(self, snapshot_id: int) -> Tuple[Optional[List[Dict]], Optional[str]]: ...
    def _create_result(self, chart_type, chart_url, title, data=None, statistics=None): ...
    def _create_error(self, error_msg): ...
```

#### 2. 测试驱动开发实践 ⭐重要
**经验**：
- 先编写测试用例，再实现功能
- 使用pytest + pytest-cov测量覆盖率
- 使用monkeypatch模拟数据库和文件路径
- 使用tmp_path创建临时测试目录

**测试分类**：
- 参数验证测试：测试必需参数缺失、参数类型错误
- 执行流程测试：测试正常执行、缓存命中、错误处理
- 边界条件测试：测试数据不足、字段不存在、维度不足
- 覆盖率测试：测试所有工具的方法存在性、名称唯一性

#### 3. 图表类型与数据特征匹配
**经验**：
- 柱状图：分类对比数据
- 饼图：占比/构成数据
- 折线图：时间序列数据
- 散点图：关系/相关性数据
- 箱线图：分布数据（含异常值）
- 直方图：频率分布数据
- 热力图：相关性矩阵/密度分布
- 雷达图：多维度评估对比
- 漏斗图：转化率分析
- 仪表盘：KPI指标展示
- 组合图：多指标对比

#### 4. numpy导入遗漏问题
**问题**：漏斗图使用`np.linspace()`但未导入numpy
**解决**：在execute方法中添加`import numpy as np`
**教训**：每个图表工具的依赖导入要完整，不能依赖外部导入

#### 5. 测试覆盖率提升策略
**经验**：
- 从33%提升到88%
- 添加模拟数据库测试（使用tmp_path创建临时数据库）
- 添加实际执行测试（验证图表生成成功）
- 添加边界条件测试（数据不足、字段不存在等）
- 添加缓存集成测试

### 文件变更清单

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| src/mcp/chart_mcp.py | 重写 | 添加BaseChartTool基类，扩展到11种图表 |
| src/ai/agent.py | 更新 | 系统提示添加所有图表类型 |
| tests/test_chart_mcp_unit.py | 重写 | 64个测试用例，覆盖率88% |

### 图表类型对照表

| 图表类型 | 工具名称 | 用途 | 参数 |
|----------|----------|------|------|
| 柱状图 | pbbi_generate_bar_chart | 分类对比 | snapshot_id, x_field, y_field, aggregation, stacked, horizontal |
| 饼图 | pbbi_generate_pie_chart | 占比分析 | snapshot_id, category_field, value_field, donut |
| 折线图 | pbbi_generate_line_chart | 趋势分析 | snapshot_id, x_field, y_field, show_area, show_markers |
| 散点图 | pbbi_generate_scatter_chart | 相关性分析 | snapshot_id, x_field, y_field, size_field |
| 箱线图 | pbbi_generate_box_plot | 分布分析 | snapshot_id, field, group_field |
| 直方图 | pbbi_generate_histogram | 频率分布 | snapshot_id, field, bins |
| 热力图 | pbbi_generate_heatmap | 相关性矩阵 | snapshot_id, x_field, y_field, value_field |
| 雷达图 | pbbi_generate_radar_chart | 多维评估 | snapshot_id, category_field, value_field |
| 漏斗图 | pbbi_generate_funnel_chart | 转化分析 | snapshot_id, stage_field, value_field |
| 仪表盘 | pbbi_generate_gauge_chart | KPI展示 | snapshot_id, value_field, min_value, max_value, thresholds |
| 组合图 | pbbi_generate_combo_chart | 多指标对比 | snapshot_id, x_field, bar_field, line_field |

### 改进建议（补充）

151. **3D图表支持**：建议添加3D柱状图、3D曲面图等
152. **图表动画**：建议前端使用ECharts实现图表动画效果
153. **图表联动**：建议实现图表间的数据联动
154. **图表导出**：建议支持导出为Excel、PDF格式
155. **图表主题**：建议支持多种配色主题
156. **智能推荐**：建议根据数据特征自动推荐图表类型

---

## 迭代 4.5 经验总结（图表类型扩展至19种，覆盖前端所有图表）

### 本次迭代完成的功能
1. ✅ 扩展图表类型从11种到19种
   - 新增3D图表：3D柱状图、3D散点图、3D曲面图、LED晶圆分析图
   - 新增组合图表：多Y轴图、堆叠柱状图、堆叠折线图、联动图表
2. ✅ 与前端ECharts图表组件对齐（共16个前端组件）
3. ✅ 编写76个单元测试，覆盖率57%
4. ✅ 更新AI Agent系统提示，支持所有图表类型

### 经验教训

#### 1. 前后端图表对齐的重要性 ⭐重要
**问题**：
- MCP图表工具原本只实现了11种图表
- 前端已有16种ECharts图表组件
- 存在重复开发和不一致问题

**解决**：
- 对比前端图表组件清单
- 补充缺失的图表类型
- 保持命名和参数一致性

#### 2. 3D图表实现要点
**经验**：
- 使用matplotlib的`mpl_toolkits.mplot3d`
- 3D柱状图：`ax.bar3d()`方法
- 3D散点图：`ax.scatter()`配合3D投影
- 3D曲面图：使用`scipy.interpolate.griddata`进行插值

**依赖安装**：
```bash
pip install scipy  # 曲面图插值需要
```

#### 3. LED晶圆图波长转RGB算法
**经验**：
- 可见光波长范围：380-780nm
- 分为多个区间进行线性插值
- 超出范围显示灰色（#808080）
- 输出格式：`#{R:02x}{G:02x}{B:02x}`

#### 4. 多Y轴图实现要点
**经验**：
- 使用`ax.twinx()`创建共享X轴的第二个Y轴
- 多个Y轴需要设置`spines['right'].set_position()`偏移
- 每个Y轴使用不同颜色区分

#### 5. 堆叠图表实现要点
**经验**：
- 堆叠柱状图：使用`bottom`参数叠加
- 堆叠折线图：使用`fill_between`填充区域
- 需要计算累积值

#### 6. 联动图表实现要点
**经验**：
- 使用`matplotlib.gridspec.GridSpec`创建子图布局
- 上方折线图展示趋势
- 下方饼图展示分布
- 共享颜色映射保持一致性

### 文件变更清单

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| src/mcp/chart_mcp.py | 扩展 | 新增8种图表工具类 |
| src/ai/agent.py | 更新 | 系统提示添加所有图表类型 |
| tests/test_chart_mcp_unit.py | 扩展 | 新增12个测试用例 |

### 图表类型完整对照表（19种）

| 分类 | 图表类型 | 工具名称 | 用途 |
|------|----------|----------|------|
| **基础图表** | 柱状图 | pbbi_generate_bar_chart | 分类对比 |
| | 饼图 | pbbi_generate_pie_chart | 占比分析 |
| | 折线图 | pbbi_generate_line_chart | 趋势分析 |
| | 散点图 | pbbi_generate_scatter_chart | 相关性分析 |
| | 箱线图 | pbbi_generate_box_plot | 分布分析 |
| | 直方图 | pbbi_generate_histogram | 频率分布 |
| **高级图表** | 热力图 | pbbi_generate_heatmap | 相关性矩阵 |
| | 雷达图 | pbbi_generate_radar_chart | 多维评估 |
| | 漏斗图 | pbbi_generate_funnel_chart | 转化分析 |
| | 仪表盘 | pbbi_generate_gauge_chart | KPI展示 |
| **3D图表** | 3D柱状图 | pbbi_generate_bar_3d_chart | 三维数据展示 |
| | 3D散点图 | pbbi_generate_scatter_3d_chart | 三维关系分析 |
| | 3D曲面图 | pbbi_generate_surface_3d_chart | 形貌数据 |
| | LED晶圆图 | pbbi_generate_led_wafer_chart | 波长颜色映射 |
| **组合图表** | 组合图 | pbbi_generate_combo_chart | 柱状图+折线图 |
| | 多Y轴图 | pbbi_generate_multiple_y_axis_chart | 多指标对比 |
| | 堆叠柱状图 | pbbi_generate_stacked_bar_chart | 构成分析 |
| | 堆叠折线图 | pbbi_generate_stacked_line_chart | 趋势构成 |
| | 联动图表 | pbbi_generate_linked_chart | 折线图+饼图 |

### 改进建议（补充）

157. **图表渲染优化**：建议前端使用ECharts渲染，后端只返回配置数据
158. **图表交互增强**：建议支持图表缩放、平移、数据点悬停提示
159. **图表导出功能**：建议支持导出PNG、PDF、SVG格式
160. **图表模板系统**：建议支持保存和复用图表配置模板

---

## 迭代 4.6 经验总结（工具定义同步与解析修复）

### 本次迭代发现的问题

#### 问题1：工具定义不同步 ⭐重要
**现象**：AI无法感知新增的14种图表工具

**根本原因**：
- 工具定义存在两处：`src/mcp/chart_mcp.py`（MCP实现）和 `src/ai/llm_client.py`（LLM工具定义）
- 只更新了MCP实现，未同步更新LLM工具定义
- LLM无法调用不存在的工具

**修复方案**：
在 `llm_client.py` 的 `get_tools_definition()` 方法中添加14种新图表工具定义

**经验教训**：
- MCP工具定义需要在两处同步更新
- 建议将工具定义统一管理，避免两处维护导致不一致

#### 问题2：DeepSeek工具调用解析失败 ⭐重要
**现象**：AI返回原始工具调用文本，未执行工具

**实际返回格式**：
```
<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>function<｜tool▁sep｜>pbbi_query_snapshot 
 
 {"snapshot_id": 1} 
 
 ```<｜tool▁call▁end｜><｜tool▁calls▁end｜>
```

**原正则表达式期望格式**：
```
function<｜tool▁sep｜>tool_name```json {...} ```
```

**问题分析**：
- DeepSeek返回的JSON参数没有包裹在 ` ```json ``` ` 代码块中
- 原正则表达式无法匹配

**修复方案**：
添加多种匹配模式：
```python
# 模式1: 带有 ```json 标记
pattern1 = r'function<｜tool▁sep｜>(\w+).*?```json\s*(\{.*?\})\s*```'

# 模式2: 没有json标记，JSON直接跟在工具名后面
pattern2 = r'function<｜tool▁sep｜>(\w+)\s*\n?\s*(\{[^{}]*\})\s*\n?\s*```'

# 模式3: 更宽松的匹配
pattern3 = r'function<｜tool▁sep｜>(\w+)\s*(\{[^{}]*\})\s*```'
```

### 文件变更清单

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| src/ai/llm_client.py | 扩展 | 添加14种图表工具定义 |
| src/ai/agent.py | 修复 | 修复工具调用解析正则表达式 |

### 改进建议（补充）

161. **工具定义统一管理**：建议将MCP工具定义抽取为独立配置文件，避免两处维护
162. **工具调用解析测试**：建议添加DeepSeek工具调用格式的单元测试
163. **日志增强**：建议在工具解析失败时输出详细日志，便于调试

---

## 迭代 4.7 经验总结（字段勾选功能修复）

### 本次迭代完成的功能
1. ✅ 修复数据设置中字段勾选失效问题
2. ✅ 统一后端API返回格式
3. ✅ 编写综合测试用例（6/6通过）
4. ✅ 修复数据导入时字段过滤问题

### 经验教训

#### 1. API返回格式一致性 ⭐重要
**问题**：`config_async.py` 直接返回数组，而 `config.py` 返回 `{"success": True, "data": [...]}` 格式

**根本原因**：
- 两个文件由不同开发人员编写，返回格式不一致
- 前端期望统一格式 `{"success": True, "data": [...]}`

**修复方案**：
```python
# 修复前
return [{"field_id": f.field_id, ...} for f in fields]

# 修复后
return {
    "success": True,
    "data": [{"field_id": f.field_id, ...} for f in fields]
}
```

**教训**：API返回格式必须在整个项目中保持一致，建议使用统一的响应模型

#### 2. CSS变量命名一致性 ⭐重要
**问题**：CSS中使用 `var(--primary)` 但variables.css定义的是 `--primary-color`

**修复方案**：
```css
/* 修复前 */
accent-color: var(--primary);

/* 修复后 */
accent-color: var(--primary-color, #3b82f6);
```

**教训**：CSS变量命名需要在整个项目中保持一致，建议使用统一的命名规范

#### 3. 测试驱动开发实践 ⭐重要
**经验**：
- 先编写测试脚本验证后端API
- 确认后端正常后再检查前端代码
- 编写综合测试用例覆盖多种场景

**测试用例设计**：
| 测试项 | 测试内容 | 结果 |
|--------|----------|------|
| API响应格式 | 验证返回格式一致性 | ✅ 通过 |
| 字段数据类型 | 验证is_enabled为字符串 | ✅ 通过 |
| 切换单个字段 | 验证单个字段切换 | ✅ 通过 |
| 批量切换字段 | 验证批量切换 | ✅ 通过 |
| 数据持久化 | 验证保存后数据正确 | ✅ 通过 |
| 边界情况 | 验证异常值处理 | ✅ 通过 |

### 文件变更清单

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| src/api/config_async.py | 修复 | 统一API返回格式 |
| src/api/data.py | 修复 | 数据导入保留字段配置、获取快照过滤禁用字段 |
| frontend/src/App.css | 修复 | CSS变量命名一致性 |
| tests/test_field_toggle.py | 新增 | 字段勾选功能测试脚本 |
| tests/test_field_comprehensive.py | 新增 | 综合测试用例 |

### 经验教训（补充）

#### 4. 数据导入保留用户配置 ⭐重要
**问题**：导入新数据时会删除所有字段配置，导致用户勾选的配置丢失

**修复方案**：
```python
# 修复前：删除所有字段，重新创建
db.query(FieldType).filter(FieldType.data_flow_id == dataflow_id).delete()
for field in fields:
    db.add(FieldType(..., is_enabled="true"))

# 修复后：保留已有字段配置，只添加新字段
existing_fields_dict = {f.field_id: f for f in existing_fields}
for field in fields:
    if field_id in existing_fields_dict:
        # 保留已有配置
        existing_field.field_name = field["field_name"]
    else:
        # 只添加新字段
        db.add(FieldType(..., is_enabled="true"))
```

**教训**：数据导入应保留用户的配置，只更新必要的信息

#### 5. 数据查询过滤禁用字段 ⭐重要
**问题**：获取快照数据时返回了所有字段，包括 `is_enabled="false"` 的字段

**修复方案**：
```python
# 过滤禁用字段
enabled_field_ids = {f.get("field_id") for f in fields if f.get("is_enabled") == "true"}
filtered_fields = [f for f in fields if f.get("is_enabled") == "true"]
filtered_data = [{k: v for k, v in row.items() if k in enabled_field_ids} for row in data]
```

**教训**：数据查询应根据字段配置过滤，只返回用户启用的字段

### 改进建议（补充）

164. **API响应模型统一**：建议创建统一的API响应模型，确保所有接口返回格式一致
165. **前端数据类型处理**：建议前端统一处理字符串类型的布尔值
166. **自动化测试集成**：建议将测试脚本集成到CI/CD流程