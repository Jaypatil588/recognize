import { useEffect, useState } from 'react'
import { useStore } from './store'
import { api } from './api'

const TYPE_DOT = {
  CONCEPT: '#B8422E',
  PERSON: '#d48a50',
  ORGANIZATION: '#4a90d9',
  PLACE: '#5cb87a',
  TECHNOLOGY: '#50c8c8',
  EVENT: '#c8b840',
}

export function Sidebar() {
  const setGraphData = useStore(s => s.setGraphData)
  const graphData = useStore(s => s.graphData)
  const backendOk = useStore(s => s.backendOk)
  const setBackendOk = useStore(s => s.setBackendOk)
  const setPage = useStore(s => s.setPage)
  const [stats, setStats] = useState({ docs: 0, entities: 0, chunks: 0, communities: 0 })

  useEffect(() => {
    async function loadNeo4j() {
      const [nextGraph, nextStats] = await Promise.all([api.graph(), api.stats()])
      setGraphData(nextGraph)
      setStats(nextStats)
      setBackendOk(true)
    }

    loadNeo4j().catch(err => {
      setBackendOk(false)
      console.error('Neo4j load failed:', err)
    })
  }, [setBackendOk, setGraphData])

  const entityTypes = graphData.nodes.reduce((acc, n) => {
    acc[n.type || 'CONCEPT'] = (acc[n.type || 'CONCEPT'] || 0) + 1
    return acc
  }, {})

  return (
    <aside className="sidebar">
      <div className="logo" style={{ cursor: 'pointer' }} onClick={() => setPage('home')}>
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="3" fill="#B8422E" />
          <circle cx="4" cy="6" r="1.8" fill="#6C7278" />
          <circle cx="20" cy="6" r="1.8" fill="#6C7278" />
          <circle cx="4" cy="18" r="1.8" fill="#6C7278" />
          <circle cx="20" cy="18" r="1.8" fill="#6C7278" />
          <line x1="12" y1="12" x2="4" y2="6" stroke="#6C7278" strokeWidth="1" />
          <line x1="12" y1="12" x2="20" y2="6" stroke="#6C7278" strokeWidth="1" />
          <line x1="12" y1="12" x2="4" y2="18" stroke="#6C7278" strokeWidth="1" />
          <line x1="12" y1="12" x2="20" y2="18" stroke="#6C7278" strokeWidth="1" />
        </svg>
        <span className="logo-text">CONTEXT GRAPH</span>
      </div>

      <div className="nav-tabs">
        <button className="nav-tab active" onClick={() => setPage('graph')}>
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="4"/><line x1="12" y1="2" x2="12" y2="5"/><line x1="12" y1="19" x2="12" y2="22"/><line x1="2" y1="12" x2="5" y2="12"/><line x1="19" y1="12" x2="22" y2="12"/></svg>
          Graph
        </button>
        <button className="nav-tab" onClick={() => setPage('dashboard')}>
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
          Analytics
        </button>
      </div>
      <button className="nav-home-link" onClick={() => setPage('home')}>
        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
        Back to Home
      </button>

      <div className="sidebar-section">
        <span className="label">HOSTED NEO4J</span>
        <div className="stats-grid">
          <div className="stat-box">
            <div className="stat-value">{stats.docs}</div>
            <div className="stat-label">docs</div>
          </div>
          <div className="stat-box">
            <div className="stat-value">{stats.entities || graphData.nodes.length}</div>
            <div className="stat-label">entities</div>
          </div>
          <div className="stat-box">
            <div className="stat-value">{stats.chunks}</div>
            <div className="stat-label">chunks</div>
          </div>
          <div className="stat-box">
            <div className="stat-value">{stats.communities}</div>
            <div className="stat-label">communities</div>
          </div>
        </div>
      </div>

      <div className="sidebar-section">
        <span className="label">RELATIONS</span>
        <div className="stat-box">
          <div className="stat-value">{graphData.links.length}</div>
          <div className="stat-label">rendered links</div>
        </div>
      </div>

      {Object.keys(entityTypes).length > 0 && (
        <div className="sidebar-section">
          <span className="label">ENTITY TYPES</span>
          <div className="files-list">
            {Object.entries(entityTypes).map(([type, count]) => (
              <div key={type} className="file-tag" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ width: 7, height: 7, borderRadius: '50%', background: TYPE_DOT[type] ?? '#6C7278', flexShrink: 0, display: 'inline-block' }} />
                <span style={{ flex: 1 }}>{type}</span>
                <span style={{ color: 'var(--secondary)', fontSize: '0.6rem' }}>{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="sidebar-footer">
        <div className={`status-dot ${backendOk ? 'online' : 'offline'}`} />
        <span className="status-text">{backendOk ? 'Neo4j connected' : 'Neo4j disconnected'}</span>
      </div>
    </aside>
  )
}
