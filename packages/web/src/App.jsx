import React, { useState, useEffect } from 'react'

const API_BASE = 'http://127.0.0.1:8000'

export default function App() {
  const [components, setComponents] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [backendOnline, setBackendOnline] = useState(false)

  // Form State
  const [name, setName] = useState('')
  const [version, setVersion] = useState('')
  const [category, setCategory] = useState('general')

  // Edit State
  const [editingId, setEditingId] = useState(null)
  const [editName, setEditName] = useState('')
  const [editVersion, setEditVersion] = useState('')
  const [editCategory, setEditCategory] = useState('')

  // Analysis State
  const [analysis, setAnalysis] = useState(null)
  const [analyzing, setAnalyzing] = useState(false)

  // Fetch components (GET)
  const fetchComponents = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/api/components`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setComponents(data)
      setBackendOnline(true)
    } catch (err) {
      console.warn('Backend not reachable, using fallback:', err)
      setBackendOnline(false)
      setError('Could not reach backend directly; checking proxy or local cache.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchComponents()
  }, [])

  // Create component (POST)
  const handleCreate = async (e) => {
    e.preventDefault()
    if (!name.trim() || !version.trim()) return

    try {
      const res = await fetch(`${API_BASE}/api/components`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: jsonBody({ name, version, category }),
      })
      if (!res.ok) throw new Error(`Failed to create: HTTP ${res.status}`)
      const created = await res.json()
      setComponents([created, ...components])
      setName('')
      setVersion('')
      setCategory('general')
      setError(null)
    } catch (err) {
      setError(err.message)
    }
  }

  function jsonBody(obj) {
    return JSON.stringify(obj)
  }

  // Start edit
  const startEditing = (comp) => {
    setEditingId(comp.id)
    setEditName(comp.name)
    setEditVersion(comp.version)
    setEditCategory(comp.category)
  }

  // Cancel edit
  const cancelEditing = () => {
    setEditingId(null)
  }

  // Save edit (PUT)
  const handleUpdate = async (id) => {
    try {
      const res = await fetch(`${API_BASE}/api/components/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: jsonBody({
          name: editName,
          version: editVersion,
          category: editCategory,
        }),
      })
      if (!res.ok) throw new Error(`Failed to update: HTTP ${res.status}`)
      const updated = await res.json()
      setComponents(components.map((c) => (c.id === id ? updated : c)))
      setEditingId(null)
      setError(null)
    } catch (err) {
      setError(err.message)
    }
  }

  // Delete component (DELETE)
  const handleDelete = async (id) => {
    try {
      const res = await fetch(`${API_BASE}/api/components/${id}`, {
        method: 'DELETE',
      })
      if (!res.ok) throw new Error(`Failed to delete: HTTP ${res.status}`)
      setComponents(components.filter((c) => c.id !== id))
      setError(null)
    } catch (err) {
      setError(err.message)
    }
  }

  // Analyze Database
  const handleAnalyze = async () => {
    setAnalyzing(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/api/components/analyze`, {
        method: 'POST',
      })
      if (!res.ok) throw new Error(`Analysis failed: HTTP ${res.status}`)
      const data = await res.json()
      setAnalysis(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setAnalyzing(false)
    }
  }

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', padding: '1.5rem' }}>
      {/* Header */}
      <div className="header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ margin: '0 0 0.5rem 0' }}>Tech Stack Issues Finder</h1>
            <p style={{ margin: 0, color: '#64748b' }}>
              Full In-Memory CRUD (GET, POST, PUT, DELETE) & Vulnerability Intelligence Pipeline
            </p>
          </div>
          <div>
            <span
              style={{
                background: backendOnline ? '#dcfce7' : '#fee2e2',
                color: backendOnline ? '#15803d' : '#b91c1c',
                padding: '0.35rem 0.75rem',
                borderRadius: '9999px',
                fontWeight: 600,
                fontSize: '0.85rem',
              }}
            >
              {backendOnline ? '● Backend Connected (Port 8000)' : '○ Backend Offline'}
            </span>
          </div>
        </div>
      </div>

      {error && (
        <div style={{ background: '#fef2f2', border: '1px solid #fecaca', color: '#991b1b', padding: '0.75rem 1rem', borderRadius: '6px', marginBottom: '1rem' }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* 1. Create Component Form (POST) */}
      <div className="card">
        <h2 style={{ marginTop: 0 }}>Add Component to Database (POST)</h2>
        <form onSubmit={handleCreate} className="input-row" style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <input
            id="input-name"
            type="text"
            placeholder="Name (e.g. react, node, postgres)"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            style={{ flex: 2, minWidth: '150px' }}
          />
          <input
            id="input-version"
            type="text"
            placeholder="Version (e.g. 17.0.2)"
            value={version}
            onChange={(e) => setVersion(e.target.value)}
            required
            style={{ flex: 1, minWidth: '100px' }}
          />
          <select
            id="input-category"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            style={{ padding: '0.5rem', border: '1px solid #cbd5e1', borderRadius: '6px' }}
          >
            <option value="general">General</option>
            <option value="frontend">Frontend</option>
            <option value="backend">Backend</option>
            <option value="database">Database</option>
            <option value="runtime">Runtime</option>
          </select>
          <button id="btn-add-component" type="submit" style={{ background: '#2563eb' }}>
            + Add Component
          </button>
        </form>
      </div>

      {/* 2. In-Memory Database List (GET, PUT, DELETE) */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h2 style={{ margin: 0 }}>In-Memory Database Stack ({components.length})</h2>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              onClick={fetchComponents}
              style={{ background: '#e2e8f0', color: '#334155', padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}
            >
              🔄 Refresh (GET)
            </button>
            <button
              id="btn-audit-stack"
              onClick={handleAnalyze}
              disabled={analyzing || components.length === 0}
              style={{ background: '#059669', color: '#ffffff', fontWeight: 600 }}
            >
              {analyzing ? 'Auditing...' : '⚡ Audit Stack (Analyze)'}
            </button>
          </div>
        </div>

        {loading && <p>Loading database components...</p>}

        {!loading && components.length === 0 && (
          <p style={{ color: '#64748b' }}>No components stored in memory. Add one above!</p>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {components.map((c) => {
            const isEditing = editingId === c.id

            return (
              <div
                key={c.id}
                style={{
                  border: '1px solid #e2e8f0',
                  borderRadius: '6px',
                  padding: '0.75rem 1rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  background: isEditing ? '#f8fafc' : '#ffffff',
                }}
              >
                {isEditing ? (
                  <div style={{ display: 'flex', gap: '0.5rem', flex: 1, alignItems: 'center' }}>
                    <input
                      type="text"
                      value={editName}
                      onChange={(e) => setEditName(e.target.value)}
                      style={{ flex: 2 }}
                    />
                    <input
                      type="text"
                      value={editVersion}
                      onChange={(e) => setEditVersion(e.target.value)}
                      style={{ flex: 1 }}
                    />
                    <input
                      type="text"
                      value={editCategory}
                      onChange={(e) => setEditCategory(e.target.value)}
                      style={{ flex: 1 }}
                    />
                    <button
                      onClick={() => handleUpdate(c.id)}
                      style={{ background: '#16a34a', padding: '0.35rem 0.75rem', fontSize: '0.85rem' }}
                    >
                      Save (PUT)
                    </button>
                    <button
                      onClick={cancelEditing}
                      style={{ background: '#94a3b8', padding: '0.35rem 0.75rem', fontSize: '0.85rem' }}
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <>
                    <div>
                      <strong style={{ fontSize: '1.05rem' }}>{c.name}</strong>
                      <span style={{ color: '#475569', marginLeft: '0.5rem' }}>@{c.version}</span>
                      <span
                        style={{
                          marginLeft: '0.75rem',
                          background: '#f1f5f9',
                          color: '#475569',
                          padding: '0.2rem 0.5rem',
                          borderRadius: '4px',
                          fontSize: '0.75rem',
                          textTransform: 'uppercase',
                        }}
                      >
                        {c.category}
                      </span>
                    </div>

                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button
                        onClick={() => startEditing(c)}
                        style={{ background: '#3b82f6', padding: '0.3rem 0.65rem', fontSize: '0.8rem' }}
                      >
                        Edit (PUT)
                      </button>
                      <button
                        onClick={() => handleDelete(c.id)}
                        style={{ background: '#ef4444', padding: '0.3rem 0.65rem', fontSize: '0.8rem' }}
                      >
                        Delete
                      </button>
                    </div>
                  </>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* 3. Live Research Findings & Upgrade Recommendations */}
      {analysis && (
        <div className="card" style={{ borderTop: '4px solid #059669' }}>
          <h2>Audit Report & Vulnerability Intelligence</h2>

          {/* Severity Badges */}
          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem' }}>
            <span style={{ background: '#fee2e2', color: '#991b1b', padding: '0.3rem 0.6rem', borderRadius: '4px', fontSize: '0.85rem', fontWeight: 600 }}>
              CRITICAL: {analysis.severity_distribution.critical}
            </span>
            <span style={{ background: '#ffedd5', color: '#9a3412', padding: '0.3rem 0.6rem', borderRadius: '4px', fontSize: '0.85rem', fontWeight: 600 }}>
              HIGH: {analysis.severity_distribution.high}
            </span>
            <span style={{ background: '#fef3c7', color: '#92400e', padding: '0.3rem 0.6rem', borderRadius: '4px', fontSize: '0.85rem', fontWeight: 600 }}>
              MEDIUM: {analysis.severity_distribution.medium}
            </span>
          </div>

          <h3>Identified Advisories ({analysis.findings.length})</h3>
          {analysis.findings.length === 0 ? (
            <p style={{ color: '#16a34a' }}>No known CVEs or EOL dates affecting your exact versions!</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.5rem' }}>
              {analysis.findings.map((f, idx) => (
                <div key={idx} className="finding-item" style={{ borderLeftColor: f.severity === 'high' ? '#ef4444' : '#f59e0b' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span className={`badge badge-${f.severity}`}>{f.severity}</span>
                    <strong>{f.id}</strong> — {f.component} (Affected: {f.affected_versions})
                  </div>
                  <p style={{ margin: '0.3rem 0' }}>{f.description}</p>
                  <small style={{ color: '#64748b' }}>
                    Target Fix: {f.fixed_in || 'N/A'} | Impact: {f.impact_score}/5 | Upgrade Effort: {f.effort_score}/5
                    {f.end_of_life_date && ` | EOL: ${f.end_of_life_date}`}
                  </small>
                </div>
              ))}
            </div>
          )}

          {/* Upgrade Paths */}
          {analysis.upgrade_paths.length > 0 && (
            <div style={{ marginBottom: '1.5rem' }}>
              <h3>Recommended Upgrade Paths ({analysis.upgrade_paths.length})</h3>
              <ul>
                {analysis.upgrade_paths.map((u, idx) => (
                  <li key={idx} style={{ marginBottom: '0.4rem' }}>
                    <strong>{u.component}</strong>: Upgrade from <code>{u.current_version}</code> &rarr; <code>{u.target_version}</code> ({u.breaking_changes_note})
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Sources */}
          {analysis.sources.length > 0 && (
            <div>
              <h3>Verified Public Sources</h3>
              <ul style={{ fontSize: '0.85rem' }}>
                {analysis.sources.map((s, idx) => (
                  <li key={idx}>
                    <a href={s} target="_blank" rel="noreferrer" style={{ color: '#2563eb' }}>
                      {s}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
