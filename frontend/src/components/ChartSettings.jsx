function ChartSettings({ chartType, config, fields, onConfigChange }) {
  const handleChange = (key, value) => {
    onConfigChange({ ...config, [key]: value })
  }

  const renderColorSchemeSettings = () => (
    <div style={{ marginBottom: '16px' }}>
      <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>配色方案</label>
      <select
        value={config.colorScheme || 'default'}
        onChange={(e) => handleChange('colorScheme', e.target.value)}
        style={{
          width: '100%',
          padding: '8px',
          border: '1px solid #d1d5db',
          borderRadius: '4px'
        }}>
        <option value="default">默认</option>
        <option value="blue">蓝色</option>
        <option value="green">绿色</option>
        <option value="purple">紫色</option>
        <option value="orange">橙色</option>
        <option value="red">红色</option>
        <option value="cyan">青色</option>
        <option value="pink">粉色</option>
        <option value="yellow">黄色</option>
        <option value="warm">暖色</option>
        <option value="cool">冷色</option>
        <option value="vintage">复古</option>
        <option value="rainbow">彩虹</option>
      </select>
    </div>
  )

  const renderCommonSettings = () => (
    <>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>图表标题</label>
        <input
          type="text"
          value={config.title || ''}
          onChange={(e) => handleChange('title', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}
        />
      </div>
      {renderColorSchemeSettings()}
    </>
  )

  const renderAxisSettings = () => (
    <>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>X轴字段</label>
        <select
          value={config.xAxisField || ''}
          onChange={(e) => handleChange('xAxisField', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}>
          <option value="">请选择</option>
          {fields.map(field => (
            <option key={field} value={field}>{field}</option>
          ))}
        </select>
      </div>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>Y轴字段</label>
        <select
          value={config.yAxisField || ''}
          onChange={(e) => handleChange('yAxisField', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}>
          <option value="">请选择</option>
          {fields.map(field => (
            <option key={field} value={field}>{field}</option>
          ))}
        </select>
      </div>
    </>
  )

  const renderPieSettings = () => (
    <>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>名称字段</label>
        <select
          value={config.nameField || ''}
          onChange={(e) => handleChange('nameField', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}>
          <option value="">请选择</option>
          {fields.map(field => (
            <option key={field} value={field}>{field}</option>
          ))}
        </select>
      </div>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>数值字段</label>
        <select
          value={config.valueField || ''}
          onChange={(e) => handleChange('valueField', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}>
          <option value="">请选择</option>
          {fields.map(field => (
            <option key={field} value={field}>{field}</option>
          ))}
        </select>
      </div>
    </>
  )

  const renderRadarSettings = () => (
    <div style={{ marginBottom: '16px' }}>
      <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>维度字段（多选）</label>
      <div style={{ maxHeight: '150px', overflowY: 'auto', border: '1px solid #d1d5db', borderRadius: '4px', padding: '8px' }}>
        {fields.map(field => (
          <label key={field} style={{ display: 'flex', alignItems: 'center', marginBottom: '4px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={(config.fields || []).includes(field)}
              onChange={(e) => {
                const newFields = e.target.checked
                  ? [...(config.fields || []), field]
                  : (config.fields || []).filter(f => f !== field)
                handleChange('fields', newFields)
              }}
              style={{ marginRight: '8px' }}
            />
            {field}
          </label>
        ))}
      </div>
    </div>
  )

  const renderGaugeSettings = () => (
    <>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>数值字段</label>
        <select
          value={config.valueField || ''}
          onChange={(e) => handleChange('valueField', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}>
          <option value="">请选择</option>
          {fields.map(field => (
            <option key={field} value={field}>{field}</option>
          ))}
        </select>
      </div>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>最大值</label>
        <input
          type="number"
          value={config.max || 100}
          onChange={(e) => handleChange('max', Number(e.target.value))}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}
        />
      </div>
    </>
  )

  const renderHeatMapSettings = () => (
    <>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>X轴字段</label>
        <select
          value={config.xAxisField || ''}
          onChange={(e) => handleChange('xAxisField', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}>
          <option value="">请选择</option>
          {fields.map(field => (
            <option key={field} value={field}>{field}</option>
          ))}
        </select>
      </div>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>Y轴字段</label>
        <select
          value={config.yAxisField || ''}
          onChange={(e) => handleChange('yAxisField', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}>
          <option value="">请选择</option>
          {fields.map(field => (
            <option key={field} value={field}>{field}</option>
          ))}
        </select>
      </div>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>数值字段</label>
        <select
          value={config.valueField || ''}
          onChange={(e) => handleChange('valueField', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}>
          <option value="">请选择</option>
          {fields.map(field => (
            <option key={field} value={field}>{field}</option>
          ))}
        </select>
      </div>
    </>
  )

  const renderNumberFlipSettings = () => (
    <>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>数值字段</label>
        <select
          value={config.valueField || ''}
          onChange={(e) => handleChange('valueField', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}>
          <option value="">请选择</option>
          {fields.map(field => (
            <option key={field} value={field}>{field}</option>
          ))}
        </select>
      </div>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>前缀</label>
        <input
          type="text"
          value={config.prefix || ''}
          onChange={(e) => handleChange('prefix', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}
        />
      </div>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>后缀</label>
        <input
          type="text"
          value={config.suffix || ''}
          onChange={(e) => handleChange('suffix', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}
        />
      </div>
    </>
  )

  const renderWaterLevelSettings = () => (
    <>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>数值字段</label>
        <select
          value={config.valueField || ''}
          onChange={(e) => handleChange('valueField', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}>
          <option value="">请选择</option>
          {fields.map(field => (
            <option key={field} value={field}>{field}</option>
          ))}
        </select>
      </div>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>最大值</label>
        <input
          type="number"
          value={config.max || 100}
          onChange={(e) => handleChange('max', Number(e.target.value))}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}
        />
      </div>
    </>
  )

  const renderMultiYAxisSettings = () => (
    <>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>X轴字段</label>
        <select
          value={config.xAxisField || ''}
          onChange={(e) => handleChange('xAxisField', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}>
          <option value="">请选择</option>
          {fields.map(field => (
            <option key={field} value={field}>{field}</option>
          ))}
        </select>
      </div>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>Y轴字段（多选）</label>
        <div style={{ maxHeight: '150px', overflowY: 'auto', border: '1px solid #d1d5db', borderRadius: '4px', padding: '8px' }}>
          {fields.map(field => (
            <label key={field} style={{ display: 'flex', alignItems: 'center', marginBottom: '4px', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={(config.yAxisFields || []).includes(field)}
                onChange={(e) => {
                  const newFields = e.target.checked
                    ? [...(config.yAxisFields || []), field]
                    : (config.yAxisFields || []).filter(f => f !== field)
                  handleChange('yAxisFields', newFields)
                }}
                style={{ marginRight: '8px' }}
              />
              {field}
            </label>
          ))}
        </div>
      </div>
    </>
  )

  const renderBar3DSettings = () => (
    <>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>X轴字段</label>
        <select
          value={config.xAxisField || ''}
          onChange={(e) => handleChange('xAxisField', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}>
          <option value="">请选择</option>
          {fields.map(field => (
            <option key={field} value={field}>{field}</option>
          ))}
        </select>
      </div>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>Y轴字段</label>
        <select
          value={config.yAxisField || ''}
          onChange={(e) => handleChange('yAxisField', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}>
          <option value="">请选择</option>
          {fields.map(field => (
            <option key={field} value={field}>{field}</option>
          ))}
        </select>
      </div>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>Z轴字段（高度）</label>
        <select
          value={config.zAxisField || ''}
          onChange={(e) => handleChange('zAxisField', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}>
          <option value="">请选择</option>
          {fields.map(field => (
            <option key={field} value={field}>{field}</option>
          ))}
        </select>
      </div>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'flex', alignItems: 'center', marginBottom: '4px', fontWeight: 500, cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={config.transparent !== false}
            onChange={(e) => handleChange('transparent', e.target.checked)}
            style={{ marginRight: '8px' }}
          />
          透明效果
        </label>
      </div>
      {config.transparent !== false && (
        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>
            透明度: {(config.opacity ?? 0.7).toFixed(2)}
          </label>
          <input
            type="range"
            min="0.1"
            max="1"
            step="0.1"
            value={config.opacity ?? 0.7}
            onChange={(e) => handleChange('opacity', parseFloat(e.target.value))}
            style={{ width: '100%' }}
          />
        </div>
      )}
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'flex', alignItems: 'center', marginBottom: '4px', fontWeight: 500, cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={config.useVisualMap !== false}
            onChange={(e) => handleChange('useVisualMap', e.target.checked)}
            style={{ marginRight: '8px' }}
          />
          显示视觉映射（颜色渐变）
        </label>
      </div>
    </>
  )

  const renderScatter3DSettings = () => (
    <>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>X轴字段</label>
        <select
          value={config.xAxisField || ''}
          onChange={(e) => handleChange('xAxisField', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}>
          <option value="">请选择</option>
          {fields.map(field => (
            <option key={field} value={field}>{field}</option>
          ))}
        </select>
      </div>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>Y轴字段</label>
        <select
          value={config.yAxisField || ''}
          onChange={(e) => handleChange('yAxisField', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}>
          <option value="">请选择</option>
          {fields.map(field => (
            <option key={field} value={field}>{field}</option>
          ))}
        </select>
      </div>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>Z轴字段</label>
        <select
          value={config.zAxisField || ''}
          onChange={(e) => handleChange('zAxisField', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}>
          <option value="">请选择</option>
          {fields.map(field => (
            <option key={field} value={field}>{field}</option>
          ))}
        </select>
      </div>
    </>
  )

  const renderLinkedSettings = () => (
    <>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>X轴字段（时间/类别）</label>
        <select
          value={config.xAxisField || ''}
          onChange={(e) => handleChange('xAxisField', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}>
          <option value="">请选择</option>
          {fields.map(field => (
            <option key={field} value={field}>{field}</option>
          ))}
        </select>
      </div>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>名称字段（系列名）</label>
        <select
          value={config.nameField || ''}
          onChange={(e) => handleChange('nameField', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}>
          <option value="">请选择</option>
          {fields.map(field => (
            <option key={field} value={field}>{field}</option>
          ))}
        </select>
      </div>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>数值字段</label>
        <select
          value={config.valueField || ''}
          onChange={(e) => handleChange('valueField', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}>
          <option value="">请选择</option>
          {fields.map(field => (
            <option key={field} value={field}>{field}</option>
          ))}
        </select>
      </div>
    </>
  )

  const renderLEDWaferSettings = () => (
    <>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>X轴字段</label>
        <select
          value={config.xAxisField || ''}
          onChange={(e) => handleChange('xAxisField', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}>
          <option value="">请选择</option>
          {fields.map(field => (
            <option key={field} value={field}>{field}</option>
          ))}
        </select>
      </div>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>Y轴字段</label>
        <select
          value={config.yAxisField || ''}
          onChange={(e) => handleChange('yAxisField', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}>
          <option value="">请选择</option>
          {fields.map(field => (
            <option key={field} value={field}>{field}</option>
          ))}
        </select>
      </div>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>Z轴字段（高度）</label>
        <select
          value={config.zAxisField || ''}
          onChange={(e) => handleChange('zAxisField', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}>
          <option value="">请选择</option>
          {fields.map(field => (
            <option key={field} value={field}>{field}</option>
          ))}
        </select>
      </div>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>波长字段（nm）</label>
        <select
          value={config.wavelengthField || ''}
          onChange={(e) => handleChange('wavelengthField', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}>
          <option value="">请选择</option>
          {fields.map(field => (
            <option key={field} value={field}>{field}</option>
          ))}
        </select>
      </div>
    </>
  )

  const renderSurface3DSettings = () => (
    <>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>X轴字段</label>
        <select
          value={config.xAxisField || ''}
          onChange={(e) => handleChange('xAxisField', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}>
          <option value="">请选择</option>
          {fields.map(field => (
            <option key={field} value={field}>{field}</option>
          ))}
        </select>
      </div>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>Y轴字段</label>
        <select
          value={config.yAxisField || ''}
          onChange={(e) => handleChange('yAxisField', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}>
          <option value="">请选择</option>
          {fields.map(field => (
            <option key={field} value={field}>{field}</option>
          ))}
        </select>
      </div>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>Z轴字段（高度）</label>
        <select
          value={config.zAxisField || ''}
          onChange={(e) => handleChange('zAxisField', e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}>
          <option value="">请选择</option>
          {fields.map(field => (
            <option key={field} value={field}>{field}</option>
          ))}
        </select>
      </div>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>X轴起始点</label>
        <input
          type="number"
          value={config.xStart ?? 0}
          onChange={(e) => handleChange('xStart', Number(e.target.value))}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}
        />
      </div>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>X轴间隔</label>
        <input
          type="number"
          value={config.xInterval ?? 1}
          onChange={(e) => handleChange('xInterval', Number(e.target.value))}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}
        />
      </div>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>Y轴起始点</label>
        <input
          type="number"
          value={config.yStart ?? 0}
          onChange={(e) => handleChange('yStart', Number(e.target.value))}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}
        />
      </div>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>Y轴间隔</label>
        <input
          type="number"
          value={config.yInterval ?? 1}
          onChange={(e) => handleChange('yInterval', Number(e.target.value))}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}
        />
      </div>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>Z轴起始点</label>
        <input
          type="number"
          value={config.zStart ?? 0}
          onChange={(e) => handleChange('zStart', Number(e.target.value))}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}
        />
      </div>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>Z轴间隔</label>
        <input
          type="number"
          value={config.zInterval ?? 10}
          onChange={(e) => handleChange('zInterval', Number(e.target.value))}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #d1d5db',
            borderRadius: '4px'
          }}
        />
      </div>
    </>
  )

  return (
    <div style={{ padding: '16px' }}>
      <h3 style={{ marginBottom: '16px', fontSize: '16px', fontWeight: 600 }}>图表设置</h3>
      {renderCommonSettings()}
      {['line', 'bar', 'scatter', 'stacked_line', 'stacked_bar'].includes(chartType) && renderAxisSettings()}
      {['pie', 'funnel'].includes(chartType) && renderPieSettings()}
      {chartType === 'radar' && renderRadarSettings()}
      {chartType === 'gauge' && renderGaugeSettings()}
      {chartType === 'heatmap' && renderHeatMapSettings()}
      {chartType === 'bar3d' && renderBar3DSettings()}
      {chartType === 'scatter3d' && renderScatter3DSettings()}
      {chartType === 'surface3d' && renderSurface3DSettings()}
      {chartType === 'linked' && renderLinkedSettings()}
      {chartType === 'led_wafer' && renderLEDWaferSettings()}
      {['stacked_line', 'stacked_bar', 'multiple_y'].includes(chartType) && renderMultiYAxisSettings()}
    </div>
  )
}

export default ChartSettings
