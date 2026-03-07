import { useNavigate } from 'react-router-dom'

function GuidePage() {
  const navigate = useNavigate()

  const modules = [
    {
      id: 'config',
      title: '配置管理',
      icon: '⚙️',
      color: '#3b82f6',
      description: '管理数据流连接和字段配置',
      features: [
        '添加明道云数据流（支持API连接）',
        '添加本地数据流（CSV/Excel导入）',
        '配置字段类型（文本、数字、日期等）',
        '启用/禁用字段',
        '测试数据流连接'
      ],
      steps: [
        '点击"增加明道云数据流"或"增加本地数据流"',
        '填写数据流名称和连接信息',
        '点击"保存"创建数据流',
        '点击"设置"按钮进入字段配置',
        '导入文件或连接明道云获取字段',
        '配置字段类型和启用状态',
        '点击"保存配置"保存设置'
      ],
      tips: [
        '明道云数据流需要配置AppKey和Sign',
        '本地数据流支持CSV和Excel格式',
        '字段类型影响后续分析和可视化效果'
      ],
      path: '/'
    },
    {
      id: 'data',
      title: '数据获取',
      icon: '📊',
      color: '#10b981',
      description: '查看和管理数据快照',
      features: [
        '查看数据流列表',
        '选择数据流查看详细数据',
        '分页浏览数据',
        '创建和管理数据快照',
        '查看字段统计信息'
      ],
      steps: [
        '进入"数据"页面',
        '在左侧选择一个数据流',
        '查看该数据流的详细数据',
        '使用分页浏览更多数据',
        '点击"创建快照"保存当前数据状态'
      ],
      tips: [
        '快照是数据分析的基础，建议定期创建',
        '快照保存后可用于后续分析和可视化'
      ],
      path: '/data'
    },
    {
      id: 'analysis',
      title: '数据分析',
      icon: '📈',
      color: '#f59e0b',
      description: '多表聚合、字段筛选和数据统计',
      features: [
        '多表聚合（UNION、JOIN）',
        '字段筛选（按条件过滤数据）',
        '数据统计（计数、求和、平均值等）',
        '高级统计（分布拟合、回归分析）',
        '保存分析结果为新快照'
      ],
      steps: [
        '进入"分析"页面',
        '选择需要的功能标签页（聚合/筛选/统计/高级统计）',
        '选择数据快照',
        '配置分析参数',
        '点击"执行"运行分析',
        '查看分析结果',
        '保存结果为新快照（可选）'
      ],
      tips: [
        '聚合功能支持UNION合并和JOIN关联',
        '高级统计支持正态分布拟合、线性回归等'
      ],
      path: '/analysis'
    },
    {
      id: 'ai',
      title: 'AI智能对话',
      icon: '🤖',
      color: '#8b5cf6',
      description: '自然语言交互，智能数据分析助手',
      features: [
        '自然语言查询数据',
        '自动生成图表',
        '数据洞察分析',
        '多轮对话上下文记忆',
        '对话历史管理',
        '反馈与纠错机制'
      ],
      steps: [
        '进入"AI对话"页面',
        '在输入框输入问题或指令',
        'AI会自动理解意图并执行相应操作',
        '查看AI生成的回答和图表',
        '点击👍👎对回答进行反馈',
        '使用"新对话"开始新的会话'
      ],
      tips: [
        '可以直接说"帮我分析XX数据的趋势"',
        '支持生成折线图、柱状图、饼图等多种图表',
        '反馈会帮助AI学习您的偏好'
      ],
      path: '/ai'
    },
    {
      id: 'visual',
      title: '数据可视化',
      icon: '📊',
      color: '#ef4444',
      description: '创建和管理数据看板',
      features: [
        '16种图表类型',
        '基础图表：折线图、柱状图、饼图、散点图、雷达图',
        '高级图表：热力图、漏斗图、仪表盘',
        '3D图表：3D柱状图、3D散点图、3D形貌图',
        '组合图表：堆叠图、多Y轴图、联动图表',
        '专业图表：LED晶圆图'
      ],
      steps: [
        '进入"可视化"页面',
        '点击"新增图表"创建看板',
        '选择数据快照',
        '选择图表类型',
        '配置图表参数（X轴、Y轴、颜色等）',
        '点击"保存"保存看板'
      ],
      tips: [
        '图表支持切换显示模式（切换/平铺）',
        '可以随时修改和删除已创建的看板'
      ],
      path: '/visual'
    },
    {
      id: 'correlation',
      title: '相关性分析',
      icon: '🔗',
      color: '#06b6d4',
      description: '跨数据流字段相关性分析',
      features: [
        '支持多数据流字段选择',
        '三种相关系数：皮尔逊、斯皮尔曼、肯德尔',
        '相关系数热力图可视化',
        '高相关字段对识别',
        '相关性探索模式'
      ],
      steps: [
        '进入"相关性分析"页面',
        '选择"相关性分析"或"相关性探索"标签',
        '选择数据快照',
        '勾选需要分析的字段（至少2个）',
        '选择相关系数类型',
        '设置相关性阈值',
        '点击"执行"查看分析结果'
      ],
      tips: [
        '皮尔逊适用于线性关系',
        '斯皮尔曼适用于非线性单调关系',
        '阈值越高，筛选出的相关性越强'
      ],
      path: '/correlation'
    },
    {
      id: 'montecarlo',
      title: '蒙特卡洛分析',
      icon: '🎲',
      color: '#ec4899',
      description: '随机模拟分析，经典案例演示',
      features: [
        '计算圆周率π（蒙特卡洛投点法）',
        '定积分计算（面积估算）',
        '排队问题模拟',
        '自定义参数设置',
        '可视化结果展示'
      ],
      steps: [
        '进入"蒙特卡洛分析"页面',
        '选择案例类型（圆周率/定积分/排队问题）',
        '配置模拟参数',
        '点击"执行模拟"',
        '查看模拟结果和可视化图表'
      ],
      tips: [
        '模拟点数越多，结果越精确',
        '排队问题可设置到达时间和服务时间分布'
      ],
      path: '/montecarlo'
    },
    {
      id: 'settings',
      title: '系统设置',
      icon: '🎨',
      color: '#6366f1',
      description: 'UI风格配置、AI模型设置、记忆管理',
      features: [
        'UI风格切换（现代专业/Bloomberg终端）',
        '主色调自定义',
        '字体大小调整',
        'AI模型配置（DeepSeek/OpenAI/智谱等）',
        '三层记忆系统管理'
      ],
      steps: [
        '进入"设置"页面',
        '选择"UI设置"标签配置界面风格',
        '选择"AI设置"标签配置AI模型',
        '选择"记忆管理"标签管理AI记忆',
        '配置完成后自动保存'
      ],
      tips: [
        'Bloomberg终端风格适合金融数据分析',
        'AI设置需要配置API密钥才能使用',
        '记忆系统帮助AI学习您的偏好'
      ],
      path: '/settings'
    }
  ]

  const quickStartSteps = [
    { step: 1, title: '配置数据源', desc: '在配置管理中添加明道云或本地数据流', icon: '⚙️' },
    { step: 2, title: '创建快照', desc: '在数据页面创建数据快照', icon: '📸' },
    { step: 3, title: '分析数据', desc: '使用分析功能或AI对话进行数据分析', icon: '📈' },
    { step: 4, title: '可视化展示', desc: '创建图表看板展示分析结果', icon: '📊' }
  ]

  return (
    <div className="page-container" style={{ padding: '16px', maxWidth: '1400px', margin: '0 auto' }}>
      <div>
        <h1 className="page-title">操作指南</h1>
        
        <div style={{ 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: '12px',
          padding: '32px',
          marginBottom: '24px',
          color: 'white'
        }}>
          <h2 style={{ margin: '0 0 12px 0', fontSize: '24px' }}>欢迎使用 PB-BI 数据分析平台</h2>
          <p style={{ margin: 0, fontSize: '16px', opacity: 0.9 }}>
            本平台提供完整的数据分析解决方案，支持数据连接、处理、分析、AI智能对话和可视化。
            点击下方卡片了解各个功能模块的详细使用方法。
          </p>
        </div>

        <div style={{ 
          marginBottom: '32px', 
          background: '#fff', 
          borderRadius: '12px', 
          padding: '24px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
        }}>
          <h3 style={{ margin: '0 0 20px 0', fontSize: '18px', color: '#374151', display: 'flex', alignItems: 'center' }}>
            <span style={{ marginRight: '8px' }}>🚀</span>
            快速开始
          </h3>
          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
            {quickStartSteps.map((item, index) => (
              <div key={item.step} style={{ 
                flex: '1', 
                minWidth: '200px',
                background: '#f8fafc',
                borderRadius: '8px',
                padding: '16px',
                position: 'relative'
              }}>
                <div style={{ 
                  position: 'absolute', 
                  top: '-8px', 
                  left: '-8px', 
                  width: '28px', 
                  height: '28px', 
                  background: '#667eea',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontWeight: 'bold',
                  fontSize: '14px'
                }}>
                  {item.step}
                </div>
                <div style={{ fontSize: '24px', marginBottom: '8px' }}>{item.icon}</div>
                <div style={{ fontWeight: 600, color: '#374151', marginBottom: '4px' }}>{item.title}</div>
                <div style={{ fontSize: '13px', color: '#64748b' }}>{item.desc}</div>
              </div>
            ))}
          </div>
        </div>

        <h2 style={{ margin: '0 0 16px 0', fontSize: '20px', color: '#374151' }}>功能模块</h2>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '20px' }}>
          {modules.map((module) => (
            <div
              key={module.id}
              style={{
                background: '#fff',
                borderRadius: '12px',
                padding: '24px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                border: `2px solid ${module.color}15`,
                transition: 'transform 0.2s, box-shadow 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)'
                e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.12)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)'
              }}>
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
                <span style={{ fontSize: '32px', marginRight: '12px' }}>{module.icon}</span>
                <div>
                  <h3 style={{ margin: 0, fontSize: '18px', color: module.color }}>{module.title}</h3>
                  <p style={{ margin: '4px 0 0 0', color: '#64748b', fontSize: '13px' }}>{module.description}</p>
                </div>
              </div>

              <div style={{ marginBottom: '16px' }}>
                <h4 style={{ margin: '0 0 8px 0', fontSize: '13px', color: '#374151', fontWeight: 600 }}>主要功能</h4>
                <ul style={{ margin: 0, paddingLeft: '18px', color: '#64748b', fontSize: '13px' }}>
                  {module.features.map((feature, i) => (
                    <li key={i} style={{ marginBottom: '3px' }}>{feature}</li>
                  ))}
                </ul>
              </div>

              <div style={{ marginBottom: '16px' }}>
                <h4 style={{ margin: '0 0 8px 0', fontSize: '13px', color: '#374151', fontWeight: 600 }}>操作步骤</h4>
                <ol style={{ margin: 0, paddingLeft: '18px', color: '#64748b', fontSize: '13px' }}>
                  {module.steps.map((step, i) => (
                    <li key={i} style={{ marginBottom: '3px' }}>{step}</li>
                  ))}
                </ol>
              </div>

              {module.tips && module.tips.length > 0 && (
                <div style={{ 
                  marginBottom: '16px', 
                  background: '#f8fafc', 
                  borderRadius: '6px', 
                  padding: '12px',
                  borderLeft: `3px solid ${module.color}`
                }}>
                  <h4 style={{ margin: '0 0 6px 0', fontSize: '12px', color: '#64748b', fontWeight: 600 }}>💡 小提示</h4>
                  {module.tips.map((tip, i) => (
                    <div key={i} style={{ fontSize: '12px', color: '#64748b', marginBottom: '2px' }}>• {tip}</div>
                  ))}
                </div>
              )}

              <button
                style={{
                  width: '100%',
                  padding: '10px',
                  background: module.color,
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'opacity 0.2s'
                }}
                onClick={() => navigate(module.path)}>
                前往 {module.title} →
              </button>
            </div>
          ))}
        </div>

        <div style={{ 
          marginTop: '32px', 
          background: '#f9fafb', 
          borderRadius: '12px', 
          padding: '24px',
          border: '1px solid #e5e7eb'
        }}>
          <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', color: '#374151' }}>💡 使用提示</h3>
          <ul style={{ margin: 0, paddingLeft: '20px', color: '#64748b', fontSize: '14px' }}>
            <li style={{ marginBottom: '8px' }}>所有分析结果都可以保存为新的数据快照，方便后续使用</li>
            <li style={{ marginBottom: '8px' }}>图表支持多种自定义配置，可以调整颜色、标题、图例等</li>
            <li style={{ marginBottom: '8px' }}>本地数据流支持导入 CSV 和 Excel 格式的文件</li>
            <li style={{ marginBottom: '8px' }}>AI对话支持自然语言交互，可以直接描述分析需求</li>
            <li style={{ marginBottom: '8px' }}>设置页面可以切换Bloomberg终端风格，适合金融数据分析</li>
            <li>如果在使用过程中遇到问题，请查看各页面的操作提示</li>
          </ul>
        </div>

        <div style={{ 
          marginTop: '24px', 
          background: '#fffbeb', 
          borderRadius: '12px', 
          padding: '24px',
          border: '1px solid #fcd34d'
        }}>
          <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', color: '#92400e' }}>🎯 AI对话示例</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '12px' }}>
            <div style={{ background: 'white', padding: '12px', borderRadius: '8px', fontSize: '13px', color: '#374151' }}>
              <strong>数据查询：</strong>"帮我查看销售数据中金额最高的10条记录"
            </div>
            <div style={{ background: 'white', padding: '12px', borderRadius: '8px', fontSize: '13px', color: '#374151' }}>
              <strong>趋势分析：</strong>"分析最近一个月的销售趋势，生成折线图"
            </div>
            <div style={{ background: 'white', padding: '12px', borderRadius: '8px', fontSize: '13px', color: '#374151' }}>
              <strong>对比分析：</strong>"对比各部门的销售业绩，用柱状图展示"
            </div>
            <div style={{ background: 'white', padding: '12px', borderRadius: '8px', fontSize: '13px', color: '#374151' }}>
              <strong>占比分析：</strong>"展示各产品类别的销售占比，生成饼图"
            </div>
          </div>
        </div>

        <div style={{ 
          marginTop: '24px', 
          background: '#f0fdf4', 
          borderRadius: '12px', 
          padding: '24px',
          border: '1px solid #86efac'
        }}>
          <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', color: '#166534' }}>📊 支持的图表类型</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '8px' }}>
            {[
              { name: '折线图', icon: '📈' },
              { name: '柱状图', icon: '📊' },
              { name: '饼图', icon: '🥧' },
              { name: '散点图', icon: '⚪' },
              { name: '雷达图', icon: '🎯' },
              { name: '热力图', icon: '🔥' },
              { name: '漏斗图', icon: '🔻' },
              { name: '仪表盘', icon: '⏱️' },
              { name: '3D柱状图', icon: '🏗️' },
              { name: '3D散点图', icon: '🔵' },
              { name: '3D形貌图', icon: '🏔️' },
              { name: '堆叠图', icon: '📉' },
              { name: '多Y轴图', icon: '📐' },
              { name: '联动图表', icon: '🔗' },
              { name: 'LED晶圆图', icon: '💡' }
            ].map((chart) => (
              <div key={chart.name} style={{ 
                background: 'white', 
                padding: '8px 12px', 
                borderRadius: '6px', 
                fontSize: '13px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <span>{chart.icon}</span>
                <span>{chart.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default GuidePage
