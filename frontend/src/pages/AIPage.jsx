import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import '../styles/AIPage.css'

function AIPage() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [modalImage, setModalImage] = useState(null)
  const [currentSessionId, setCurrentSessionId] = useState(null)
  const [sessions, setSessions] = useState([])
  const [feedbacks, setFeedbacks] = useState({})
  const [showCorrection, setShowCorrection] = useState(null)
  const [correctionText, setCorrectionText] = useState('')
  const [contextWarning, setContextWarning] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [isSearching, setIsSearching] = useState(false)
  const [imageZoom, setImageZoom] = useState(1)
  const [imagePan, setImagePan] = useState({ x: 0, y: 0 })
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const [thinkingProcess, setThinkingProcess] = useState([])
  const [showThinking, setShowThinking] = useState(true)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    loadSessions()
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const loadSessions = async () => {
    try {
      const response = await fetch('/api/conversation/list')
      if (response.ok) {
        const data = await response.json()
        setSessions(data)
        
        const activeRes = await fetch('/api/conversation/active/default')
        if (activeRes.ok) {
          const activeData = await activeRes.json()
          if (activeData.has_active_session) {
            loadSession(activeData.session_id)
          } else {
            createNewSession()
          }
        }
      }
    } catch (error) {
      console.error('Load sessions error:', error)
    }
  }

  const loadSession = async (sessionId) => {
    try {
      const response = await fetch(`/api/conversation/${sessionId}`)
      if (response.ok) {
        const data = await response.json()
        setCurrentSessionId(sessionId)
        setMessages(data.messages.map(m => ({
          role: m.role,
          content: m.content,
          toolCalls: m.tool_calls
        })))
        
        if (data.context_info.is_near_limit) {
          setContextWarning(data.context_info)
        }
      }
    } catch (error) {
      console.error('Load session error:', error)
    }
  }

  const createNewSession = async () => {
    try {
      const response = await fetch('/api/conversation/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      if (response.ok) {
        const data = await response.json()
        setCurrentSessionId(data.session_id)
        setMessages([])
        setFeedbacks({})
        setContextWarning(null)
        loadSessions()
      }
    } catch (error) {
      console.error('Create session error:', error)
    }
  }

  const archiveAndNew = async () => {
    if (currentSessionId) {
      try {
        await fetch(`/api/conversation/${currentSessionId}/archive`, { method: 'POST' })
      } catch (error) {
        console.error('Archive error:', error)
      }
    }
    await createNewSession()
  }

  const deleteCurrentSession = async () => {
    if (!currentSessionId) return
    
    if (!confirm('确定要删除当前对话吗？此操作不可恢复。')) return
    
    try {
      await fetch(`/api/conversation/${currentSessionId}`, { method: 'DELETE' })
      setMessages([])
      setFeedbacks({})
      setCurrentSessionId(null)
      loadSessions()
      
      const activeRes = await fetch('/api/conversation/active/default')
      if (activeRes.ok) {
        const activeData = await activeRes.json()
        if (activeData.has_active_session) {
          loadSession(activeData.session_id)
        } else {
          createNewSession()
        }
      }
    } catch (error) {
      console.error('Delete session error:', error)
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)
    setThinkingProcess([])

    const aiMessage = { role: 'assistant', content: '', thinking: true }
    setMessages(prev => [...prev, aiMessage])

    try {
      const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: input,
          session_id: currentSessionId
        })
      })

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let fullContent = ''
      let streamDone = false

      setMessages(prev => prev.map((msg, idx) =>
        idx === prev.length - 1 ? { ...msg, thinking: false } : msg
      ))

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') {
              // 流结束，标记为完成
              streamDone = true
              break
            }
            
            try {
              const event = JSON.parse(data)
              
              if (event.type === 'thinking_start') {
                setThinkingProcess(prev => [...prev, {
                  type: 'start',
                  message: event.message,
                  timestamp: Date.now()
                }])
              } else if (event.type === 'thinking') {
                setThinkingProcess(prev => [...prev, {
                  type: 'thinking',
                  stage: event.stage,
                  message: event.message,
                  timestamp: Date.now()
                }])
              } else if (event.type === 'tool_call_start') {
                setThinkingProcess(prev => [...prev, {
                  type: 'tool_call',
                  tool: event.tool,
                  display_name: event.display_name,
                  step: event.step,
                  total: event.total,
                  timestamp: Date.now()
                }])
              } else if (event.type === 'content') {
                fullContent += event.content
                setMessages(prev => prev.map((msg, idx) =>
                  idx === prev.length - 1 ? { ...msg, content: fullContent } : msg
                ))
              } else if (event.type === 'tool_result') {
                const result = event.result
                const summary = event.summary
                setThinkingProcess(prev => [...prev, {
                  type: 'tool_result',
                  tool: event.tool,
                  summary: summary,
                  success: result?.success,
                  timestamp: Date.now()
                }])
                
                // 检查图表URL - 可能在 result.chart_url 或 result.data.chart_url
                const chartUrl = result?.chart_url || result?.data?.chart_url
                const chartTitle = result?.title || result?.data?.title || '图表'
                
                if (result && result.success && chartUrl) {
                  const chartMarkdown = `\n\n![${chartTitle}](${chartUrl})\n`
                  fullContent += chartMarkdown
                  setMessages(prev => prev.map((msg, idx) =>
                    idx === prev.length - 1 ? { ...msg, content: fullContent } : msg
                  ))
                } else if (result && !result.success) {
                  const errorMsg = result?.error || result?.data?.error || '未知错误'
                  fullContent += `\n\n❌ 工具执行失败: ${errorMsg}\n`
                  setMessages(prev => prev.map((msg, idx) =>
                    idx === prev.length - 1 ? { ...msg, content: fullContent } : msg
                  ))
                }
              } else if (event.type === 'tool_call') {
                fullContent += `\n\n🔧 正在执行: ${event.tool}...\n`
                setMessages(prev => prev.map((msg, idx) =>
                  idx === prev.length - 1 ? { ...msg, content: fullContent } : msg
                ))
              }
            } catch (e) {
              // 忽略解析错误
            }
          }
        }
        
        // 检查是否需要退出 while 循环
        if (streamDone) break
      }

      if (currentSessionId && fullContent) {
        await fetch(`/api/conversation/${currentSessionId}/messages`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            role: 'user',
            content: userMessage.content,
            tokens: userMessage.content.length
          })
        })
        
        await fetch(`/api/conversation/${currentSessionId}/messages`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            role: 'assistant',
            content: fullContent,
            tokens: fullContent.length
          })
        })
        
        loadSessions()
      }

    } catch (error) {
      setMessages(prev => prev.map((msg, idx) =>
        idx === prev.length - 1 ? { ...msg, content: `错误: ${error.message}`, error: true } : msg
      ))
    } finally {
      setLoading(false)
    }
  }

  const clearChat = async () => {
    try {
      await fetch('/api/ai/clear', { method: 'POST' })
      setMessages([])
      setFeedbacks({})
    } catch (error) {
      console.error('Clear error:', error)
    }
  }

  const submitFeedback = async (messageIdx, rating, userQuery, aiResponse) => {
    try {
      const response = await fetch('/api/feedback/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: currentSessionId || 'default',
          message_id: `${currentSessionId}_${messageIdx}`,
          rating: rating,
          user_query: userQuery,
          ai_response: aiResponse,
          chart_generated: aiResponse.includes('![') || aiResponse.includes('chart')
        })
      })
      
      if (response.ok) {
        setFeedbacks(prev => ({ ...prev, [messageIdx]: rating }))
        
        if (rating < 0) {
          setShowCorrection(messageIdx)
        }
      }
    } catch (error) {
      console.error('Feedback error:', error)
    }
  }

  const submitCorrection = async (messageIdx, userQuery, aiResponse) => {
    if (!correctionText.trim()) return
    
    try {
      await fetch('/api/feedback/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: currentSessionId || 'default',
          message_id: `${currentSessionId}_${messageIdx}`,
          rating: -1,
          user_query: userQuery,
          ai_response: aiResponse,
          user_correction: correctionText,
          correction_type: 'user_edit'
        })
      })
      
      setShowCorrection(null)
      setCorrectionText('')
    } catch (error) {
      console.error('Correction error:', error)
    }
  }

  const exportToMarkdown = async () => {
    if (!currentSessionId) return
    
    try {
      const response = await fetch(`/api/conversation/${currentSessionId}/download`)
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `conversation_${currentSessionId}.md`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }
    } catch (error) {
      console.error('Export error:', error)
    }
  }

  const saveToArchive = async () => {
    if (!currentSessionId) return
    
    try {
      const response = await fetch(`/api/conversation/${currentSessionId}/export`)
      if (response.ok) {
        const data = await response.json()
        alert(`对话已存档到: ${data.filepath}`)
      }
    } catch (error) {
      console.error('Archive error:', error)
    }
  }

  const searchConversations = async (query) => {
    setSearchQuery(query)
    
    if (!query || query.trim().length < 2) {
      setSearchResults([])
      return
    }
    
    setIsSearching(true)
    try {
      const response = await fetch(`/api/conversation/search?q=${encodeURIComponent(query)}`)
      if (response.ok) {
        const data = await response.json()
        setSearchResults(data)
      }
    } catch (error) {
      console.error('Search error:', error)
    } finally {
      setIsSearching(false)
    }
  }

  const clearSearch = () => {
    setSearchQuery('')
    setSearchResults([])
  }

  const openImageModal = (src) => {
    setModalImage(src)
    setImageZoom(1)
    setImagePan({ x: 0, y: 0 })
  }

  const handleZoomIn = () => {
    setImageZoom(prev => Math.min(prev + 0.25, 5))
  }

  const handleZoomOut = () => {
    setImageZoom(prev => Math.max(prev - 0.25, 0.25))
  }

  const handleResetZoom = () => {
    setImageZoom(1)
    setImagePan({ x: 0, y: 0 })
  }

  const handleMouseDown = (e) => {
    if (e.button === 0) {
      setIsDragging(true)
      setDragStart({ x: e.clientX - imagePan.x, y: e.clientY - imagePan.y })
    }
  }

  const handleMouseMove = (e) => {
    if (isDragging) {
      setImagePan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      })
    }
  }

  const handleMouseUp = () => {
    setIsDragging(false)
  }

  const handleWheel = (e) => {
    e.preventDefault()
    if (e.deltaY < 0) {
      setImageZoom(prev => Math.min(prev + 0.1, 5))
    } else {
      setImageZoom(prev => Math.max(prev - 0.1, 0.25))
    }
  }

  const downloadImage = (format = 'png') => {
    if (!modalImage) return
    const filename = modalImage.split('/').pop() || 'chart.png'
    const chartFilename = filename.replace('.png', '')
    
    const downloadUrl = `/api/chart-export/${chartFilename}/download?format=${format}`
    
    const a = document.createElement('a')
    a.href = downloadUrl
    a.download = `${chartFilename}.${format}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  }

  const downloadAsPng = () => downloadImage('png')
  const downloadAsPdf = () => downloadImage('pdf')
  const downloadAsSvg = () => downloadImage('svg')

  const closeModal = () => {
    setModalImage(null)
    setImageZoom(1)
    setImagePan({ x: 0, y: 0 })
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="ai-page">
      <div className="sidebar">
        <div className="sidebar-header">
          <button className="new-chat-btn" onClick={archiveAndNew} title="新建对话">
            ➕ 新建
          </button>
          <button className="close-chat-btn" onClick={deleteCurrentSession} title="关闭对话">
            ✖ 关闭
          </button>
        </div>
        
        <div className="search-container">
          <input
            type="text"
            className="search-input"
            placeholder="搜索对话..."
            value={searchQuery}
            onChange={(e) => searchConversations(e.target.value)}
          />
          {searchQuery && (
            <button className="clear-search-btn" onClick={clearSearch}>✕</button>
          )}
        </div>
        
        {isSearching && <div className="search-loading">搜索中...</div>}
        
        <div className="session-list">
          {searchResults.length > 0 ? (
            searchResults.map(result => (
              <div 
                key={result.session_id}
                className={`session-item search-result ${result.session_id === currentSessionId ? 'active' : ''}`}
                onClick={() => {
                  loadSession(result.session_id)
                  clearSearch()
                }}
              >
                <div className="session-title">{result.title}</div>
                <div className="session-meta">
                  <span>{result.match_count}处匹配</span>
                  <span>{new Date(result.created_at).toLocaleDateString()}</span>
                </div>
                {result.highlights && result.highlights.length > 0 && (
                  <div className="search-highlight">
                    {result.highlights[0].content.substring(0, 100)}...
                  </div>
                )}
              </div>
            ))
          ) : (
            sessions.map(session => (
              <div 
                key={session.session_id}
                className={`session-item ${session.session_id === currentSessionId ? 'active' : ''}`}
                onClick={() => loadSession(session.session_id)}
              >
                <div className="session-title">{session.title}</div>
                <div className="session-meta">
                  <span>{session.message_count}条消息</span>
                  <span>{new Date(session.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="chat-container">
        <div className="chat-header">
          <h2>AI 数据分析助手</h2>
          <button className="clear-btn" onClick={clearChat}>清空对话</button>
        </div>

        {contextWarning && (
          <div className={`context-warning ${contextWarning.level}`}>
            ⚠️ {contextWarning.message}
          </div>
        )}

        {thinkingProcess.length > 0 && showThinking && (
          <div className="thinking-panel">
            <div className="thinking-panel-header">
              <span className="thinking-title">🧠 思考过程</span>
              <button className="toggle-thinking-btn" onClick={() => setShowThinking(false)}>
                收起
              </button>
            </div>
            <div className="thinking-steps">
              {thinkingProcess.map((step, idx) => (
                <div key={idx} className={`thinking-step ${step.type}`}>
                  {step.type === 'start' && (
                    <div className="step-content">
                      <span className="step-icon">🎯</span>
                      <span className="step-message">{step.message}</span>
                    </div>
                  )}
                  {step.type === 'thinking' && (
                    <div className="step-content">
                      <span className="step-icon">
                        {step.stage === 'intent_analysis' && '🔍'}
                        {step.stage === 'llm_call' && '💭'}
                        {step.stage === 'tool_planning' && '📋'}
                        {step.stage === 'tool_executing' && '⚡'}
                        {step.stage === 'generating_response' && '✍️'}
                      </span>
                      <span className="step-message">{step.message}</span>
                    </div>
                  )}
                  {step.type === 'tool_call' && (
                    <div className="step-content tool-step">
                      <span className="step-icon">🔧</span>
                      <span className="step-message">
                        [{step.step}/{step.total}] {step.display_name}
                      </span>
                    </div>
                  )}
                  {step.type === 'tool_result' && (
                    <div className={`step-content result-step ${step.success ? 'success' : 'error'}`}>
                      <span className="step-icon">{step.success ? '✅' : '❌'}</span>
                      <span className="step-message">{step.summary}</span>
                    </div>
                  )}
                </div>
              ))}
              {loading && (
                <div className="thinking-step active">
                  <div className="step-content">
                    <span className="step-icon spinner-small"></span>
                    <span className="step-message">处理中...</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {!showThinking && thinkingProcess.length > 0 && (
          <button className="show-thinking-btn" onClick={() => setShowThinking(true)}>
            🧠 显示思考过程 ({thinkingProcess.length}步)
          </button>
        )}

        <div className="messages-container">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <div className="message-avatar">
                {msg.role === 'user' ? (
                  <svg viewBox="0 0 24 24" fill="none" className="avatar-icon user-icon">
                    <circle cx="12" cy="8" r="4" fill="currentColor"/>
                    <path d="M4 20c0-4 4-6 8-6s8 2 8 6" fill="currentColor"/>
                  </svg>
                ) : (
                  <svg viewBox="0 0 32 32" fill="none" className="avatar-icon assistant-icon">
                    <rect x="6" y="8" width="20" height="18" rx="4" fill="currentColor"/>
                    <rect x="10" y="12" width="4" height="4" rx="1" fill="white"/>
                    <rect x="18" y="12" width="4" height="4" rx="1" fill="white"/>
                    <circle cx="12" cy="14" r="1" fill="#7c3aed"/>
                    <circle cx="20" cy="14" r="1" fill="#7c3aed"/>
                    <path d="M13 20h6" stroke="white" strokeWidth="2" strokeLinecap="round"/>
                    <rect x="14" y="4" width="4" height="4" rx="2" fill="currentColor"/>
                    <circle cx="16" cy="6" r="1" fill="white"/>
                    <rect x="4" y="14" width="2" height="4" rx="1" fill="currentColor"/>
                    <rect x="26" y="14" width="2" height="4" rx="1" fill="currentColor"/>
                  </svg>
                )}
              </div>
              <div className="message-content">
                {msg.role === 'user' ? (
                  <div className="user-text">{msg.content}</div>
                ) : (
                  <div className={`assistant-message ${msg.error ? 'error' : ''}`}>
                    {msg.thinking && (
                      <div className="thinking">
                        <span className="spinner"></span>
                        正在思考...
                      </div>
                    )}
                    <div className="markdown-content">
                      <ReactMarkdown 
                        remarkPlugins={[remarkGfm]}
                        components={{
                          img: ({ node, ...props }) => (
                            <img 
                              {...props} 
                              style={{ cursor: 'pointer' }}
                              onClick={() => openImageModal(props.src)}
                              title="点击放大"
                            />
                          )
                        }}
                      >
                        {msg.content}
                      </ReactMarkdown>
                    </div>
                    {!msg.error && !msg.thinking && msg.content && (
                      <div className="feedback-buttons">
                        <button 
                          className={`feedback-btn ${feedbacks[idx] === 1 ? 'active positive' : ''}`}
                          onClick={() => {
                            const prevMsg = messages[idx - 1]
                            if (prevMsg && prevMsg.role === 'user') {
                              submitFeedback(idx, 1, prevMsg.content, msg.content)
                            }
                          }}
                          title="满意"
                        >
                          👍
                        </button>
                        <button 
                          className={`feedback-btn ${feedbacks[idx] === -1 ? 'active negative' : ''}`}
                          onClick={() => {
                            const prevMsg = messages[idx - 1]
                            if (prevMsg && prevMsg.role === 'user') {
                              submitFeedback(idx, -1, prevMsg.content, msg.content)
                            }
                          }}
                          title="不满意"
                        >
                          👎
                        </button>
                        <button 
                          className="feedback-btn archive-btn"
                          onClick={saveToArchive}
                          title="存档到本地"
                        >
                          📁
                        </button>
                        <button 
                          className="feedback-btn download-btn"
                          onClick={exportToMarkdown}
                          title="下载Markdown"
                        >
                          ⬇️
                        </button>
                      </div>
                    )}
                    {showCorrection === idx && (
                      <div className="correction-input">
                        <textarea
                          value={correctionText}
                          onChange={(e) => setCorrectionText(e.target.value)}
                          placeholder="请告诉我们正确的答案或建议..."
                          rows={3}
                        />
                        <div className="correction-actions">
                          <button 
                            className="submit-correction-btn"
                            onClick={() => {
                              const prevMsg = messages[idx - 1]
                              if (prevMsg && prevMsg.role === 'user') {
                                submitCorrection(idx, prevMsg.content, msg.content)
                              }
                            }}
                          >
                            提交修正
                          </button>
                          <button 
                            className="cancel-correction-btn"
                            onClick={() => {
                              setShowCorrection(null)
                              setCorrectionText('')
                            }}
                          >
                            取消
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="输入消息... (Enter发送, Shift+Enter换行)"
            disabled={loading}
            rows={3}
          />
          <button 
            className="send-btn" 
            onClick={sendMessage}
            disabled={loading || !input.trim()}
          >
            {loading ? '发送中...' : '发送'}
          </button>
        </div>
      </div>

      {modalImage && (
        <div className="image-modal" onClick={(e) => e.target === e.currentTarget && closeModal()}>
          <div className="image-modal-toolbar">
            <button className="toolbar-btn" onClick={handleZoomOut} title="缩小">
              🔍-
            </button>
            <span className="zoom-level">{Math.round(imageZoom * 100)}%</span>
            <button className="toolbar-btn" onClick={handleZoomIn} title="放大">
              🔍+
            </button>
            <button className="toolbar-btn" onClick={handleResetZoom} title="重置">
              ↺
            </button>
            <div className="toolbar-divider"></div>
            <button className="toolbar-btn download-btn" onClick={downloadAsPng} title="下载PNG">
              PNG
            </button>
            <button className="toolbar-btn download-btn" onClick={downloadAsPdf} title="下载PDF">
              PDF
            </button>
            <button className="toolbar-btn download-btn" onClick={downloadAsSvg} title="下载SVG">
              SVG
            </button>
            <div className="toolbar-divider"></div>
            <button className="toolbar-btn close-btn" onClick={closeModal} title="关闭">
              ✕
            </button>
          </div>
          <div 
            className="image-modal-content"
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            onWheel={handleWheel}
            style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
          >
            <img 
              src={modalImage} 
              alt="放大图片" 
              style={{
                transform: `scale(${imageZoom}) translate(${imagePan.x / imageZoom}px, ${imagePan.y / imageZoom}px)`,
                transition: isDragging ? 'none' : 'transform 0.1s ease'
              }}
              draggable={false}
            />
          </div>
          <div className="image-modal-hint">
            滚轮缩放 | 拖拽平移 | 点击空白处关闭
          </div>
        </div>
      )}
    </div>
  )
}

export default AIPage
