import { useState } from 'react'

const API_URL = '/api'

function App() {
  const [url, setUrl] = useState('')
  const [result, setResult] = useState(null)
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [recentUrls, setRecentUrls] = useState([])

  const shortenUrl = async (e) => {
    e.preventDefault()
    if (!url.trim()) return

    setLoading(true)
    setError('')
    setResult(null)
    setStats(null)

    try {
      const response = await fetch(`${API_URL}/shorten`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      })

      if (!response.ok) {
        const errData = await response.json()
        throw new Error(errData.detail || 'Failed to shorten URL')
      }

      const data = await response.json()
      setResult(data)
      setRecentUrls(prev => [data, ...prev].slice(0, 5))
      setUrl('')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getStats = async (shortCode) => {
    try {
      const response = await fetch(`${API_URL}/stats/${shortCode}`)
      if (!response.ok) throw new Error('Failed to fetch stats')
      const data = await response.json()
      setStats(data)
    } catch (err) {
      setError(err.message)
    }
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
  }

  return (
    <div className="app">
      {/* Background Effects */}
      <div className="bg-gradient"></div>
      <div className="bg-grid"></div>

      {/* Main Content */}
      <div className="container">
        {/* Header */}
        <header className="header">
          <div className="logo">
            <span className="logo-icon">⚡</span>
            <h1>Shortn</h1>
          </div>
          <p className="tagline">Lightning-fast URL shortening</p>
        </header>

        {/* URL Input Form */}
        <form onSubmit={shortenUrl} className="form-card">
          <div className="input-group">
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Paste your long URL here..."
              required
              className="url-input"
            />
            <button type="submit" disabled={loading} className="shorten-btn">
              {loading ? (
                <span className="spinner"></span>
              ) : (
                'Shorten'
              )}
            </button>
          </div>
          {error && <p className="error">{error}</p>}
        </form>

        {/* Result */}
        {result && (
          <div className="result-card">
            <div className="result-header">
              <span className="success-badge">✓ Created</span>
            </div>
            <div className="result-body">
              <div className="short-url-row">
                <a
                  href={result.short_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="short-url"
                >
                  {result.short_url}
                </a>
                <button
                  onClick={() => copyToClipboard(result.short_url)}
                  className="copy-btn"
                  title="Copy to clipboard"
                >
                  📋
                </button>
              </div>
              <p className="original-url">{result.original_url}</p>
              <button
                onClick={() => getStats(result.short_code)}
                className="stats-btn"
              >
                📊 View Stats
              </button>
            </div>
          </div>
        )}

        {/* Stats */}
        {stats && (
          <div className="stats-card">
            <h3>📊 URL Statistics</h3>
            <div className="stats-grid">
              <div className="stat-item">
                <span className="stat-value">{stats.clicks}</span>
                <span className="stat-label">Total Clicks</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">{stats.short_code}</span>
                <span className="stat-label">Short Code</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">
                  {new Date(stats.created_at).toLocaleDateString()}
                </span>
                <span className="stat-label">Created</span>
              </div>
            </div>
          </div>
        )}

        {/* Recent URLs */}
        {recentUrls.length > 0 && (
          <div className="recent-card">
            <h3>🕐 Recent URLs</h3>
            <ul className="recent-list">
              {recentUrls.map((item, index) => (
                <li key={index} className="recent-item">
                  <a
                    href={item.short_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="recent-short"
                  >
                    {item.short_code}
                  </a>
                  <span className="recent-original">
                    {item.original_url.length > 50
                      ? item.original_url.substring(0, 50) + '...'
                      : item.original_url}
                  </span>
                  <button
                    onClick={() => getStats(item.short_code)}
                    className="mini-stats-btn"
                  >
                    📊
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Footer */}
        <footer className="footer">
          <p>Built with FastAPI + React + PostgreSQL + Redis</p>
          <p>Deployed on Kubernetes with Helm | Monitored by Prometheus + Grafana</p>
        </footer>
      </div>
    </div>
  )
}

export default App
