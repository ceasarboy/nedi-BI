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
        '添加明道云数据流',
        '添加本地数据流',
        '配置字段类型',
        '启用/禁用字段',
        '导入CSV/Excel文件'
      ],
      steps: [
        '点击"增加明道云数据流"或"增加本地数据流"',
        '填写数据流信息并保存',
        '点击"设置"按钮进入字段配置',
        '导入文件或连接明道云获取字段',
        '配置字段类型和启用状态',
        '点击"保存配置"保存设置'
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
        '选择数据流查看数据',
        '分页浏览数据',
        '查看数据快照'
      ],
      steps: [
        '进入"数据"页面',
        '在左侧选择一个数据流',
        '查看该数据流的详细数据',
        '使用分页浏览更多数据'
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
        '多表聚合（UNION、JOIN等）',
        '字段筛选（按条件过滤数据）',
        '数据统计（计数、求和、平均值等）',
        '保存分析结果为新快照'
      ],
      steps: [
        '进入"分析"页面',
        '选择需要的功能标签页',
        '选择数据快照',
        '配置分析参数',
        '执行分析并查看结果',
        '保存结果为新快照'
      ],
      path: '/analysis'
    },
    {
      id: 'visual',
      title: '数据可视化',
      icon: '📊',
      color: '#ef4444',
      description: '创建和管理数据看板',
      features: [
        '创建数据看板',
        '多种图表类型（折线图、柱状图、饼图等）',
        '3D图表支持',
        '堆叠图表',
        '多Y轴图表',
        '图表配置自定义'
      ],
      steps: [
        '进入"可视化"页面',
        '选择或创建一个看板',
        '选择数据快照',
        '选择图表类型',
        '配置图表参数',
        '查看和保存看板'
      ],
      path: '/visual'
    }
  ]

  return (
    <div className="page-container" style={{ padding: '16px' }}>
      <div>
        <h1 className="page-title">操作指南</h1>
        
        <div style={{ 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: '12px',
          padding: '32px',
          marginBottom: '24px',
          color: 'white'
        }}>
          <h2 style={{ margin: '0 0 12px 0', fontSize: '24px' }}>欢迎使用 NEDI 数据分析平台</h2>
          <p style={{ margin: 0, fontSize: '16px', opacity: 0.9 }}>
            本平台提供完整的数据分析解决方案，支持数据连接、处理、分析和可视化。
            点击下方卡片了解各个功能模块的详细使用方法。
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))', gap: '20px' }}>
          {modules.map((module) => (
            <div
              key={module.id}
              style={{
                background: '#fff',
                borderRadius: '12px',
                padding: '24px',
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                border: `2px solid ${module.color}20`
              }}>
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
                <span style={{ fontSize: '32px', marginRight: '12px' }}>{module.icon}</span>
                <div>
                  <h3 style={{ margin: 0, fontSize: '20px', color: module.color }}>{module.title}</h3>
                  <p style={{ margin: '4px 0 0 0', color: '#64748b', fontSize: '14px' }}>{module.description}</p>
                </div>
              </div>

              <div style={{ marginBottom: '16px' }}>
                <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#374151', fontWeight: 600 }}>主要功能</h4>
                <ul style={{ margin: 0, paddingLeft: '20px', color: '#64748b', fontSize: '13px' }}>
                  {module.features.map((feature, i) => (
                    <li key={i} style={{ marginBottom: '4px' }}>{feature}</li>
                  ))}
                </ul>
              </div>

              <div style={{ marginBottom: '16px' }}>
                <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#374151', fontWeight: 600 }}>操作步骤</h4>
                <ol style={{ margin: 0, paddingLeft: '20px', color: '#64748b', fontSize: '13px' }}>
                  {module.steps.map((step, i) => (
                    <li key={i} style={{ marginBottom: '4px' }}>{step}</li>
                  ))}
                </ol>
              </div>

              <button
                style={{
                  width: '100%',
                  padding: '12px',
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
            <li>如果在使用过程中遇到问题，请查看各页面的操作提示</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default GuidePage
