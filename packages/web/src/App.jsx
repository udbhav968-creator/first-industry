import React, { useState } from 'react'

export default function App() {
  const [items, setItems] = useState([
    { name: 'node', version: '18.15.0' },
    { name: 'react', version: '17.0.2' },
  ])
  const [component, setComponent] = useState('')
  const [version, setVersion] = useState('')

  const handleAdd = (e) => {
    e.preventDefault()
    if (!component || !version) return
    setItems([...items, { name: component.toLowerCase(), version }])
    setComponent('')
    setVersion('')
  }

  const handleRemove = (index) => {
    setItems(items.filter((_, i) => i !== index))
  }

  return (
    <div>
      <div className="header">
        <h1>Tech Stack Issues Finder</h1>
        <p>Audit dependencies and versions for known CVEs, EOL milestones, and upgrade paths.</p>
      </div>

      <div className="card">
        <h2>Enter Tech Stack</h2>
        <form onSubmit={handleAdd} className="input-row">
          <input
            type="text"
            placeholder="Component (e.g. node, react, postgres)"
            value={component}
            onChange={(e) => setComponent(e.target.value)}
          />
          <input
            type="text"
            placeholder="Version (e.g. 18.15.0)"
            value={version}
            onChange={(e) => setVersion(e.target.value)}
          />
          <button type="submit">Add Component</button>
        </form>

        <div>
          <h3>Active Stack ({items.length})</h3>
          <ul>
            {items.map((item, idx) => (
              <li key={idx} style={{ marginBottom: '0.5rem' }}>
                <strong>{item.name}</strong> @ {item.version}
                <button
                  onClick={() => handleRemove(idx)}
                  style={{ marginLeft: '1rem', background: '#ef4444', padding: '0.2rem 0.5rem', fontSize: '0.8rem' }}
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="card">
        <h2>Sample Findings</h2>
        <div className="finding-item">
          <div>
            <span className="badge badge-high">HIGH</span>{' '}
            <strong>CVE-2023-32006</strong> - node 18.15.0
          </div>
          <p>Permissions policy bypass through process.binding() in Node.js 18.x.</p>
          <small>Target fix: Upgrade to 18.16.1 (Effort: 1/5)</small>
        </div>

        <div className="finding-item">
          <div>
            <span className="badge badge-medium">MEDIUM</span>{' '}
            <strong>CVE-2022-21703</strong> - react 17.0.2
          </div>
          <p>Potential Cross-Site Scripting (XSS) in server-side rendered React applications.</p>
          <small>Target fix: Upgrade to 17.0.3 (Effort: 1/5)</small>
        </div>
      </div>
    </div>
  )
}
