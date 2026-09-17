import { useState, useEffect } from 'react'
import { Shield, CheckCircle, XCircle, Clock, AlertCircle, ChevronDown, ChevronUp, RefreshCw } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext.jsx'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const STATUS_CONFIG = {
  COMPLETE: { label: 'Complete', icon: CheckCircle, color: 'text-emerald-400', bg: 'bg-emerald-900/30 border-emerald-800' },
  PARTIAL: { label: 'Partial', icon: Clock, color: 'text-amber-400', bg: 'bg-amber-900/30 border-amber-800' },
  MISSING: { label: 'Missing', icon: XCircle, color: 'text-red-400', bg: 'bg-red-900/30 border-red-800' },
  NEEDS_REVIEW: { label: 'Needs Review', icon: AlertCircle, color: 'text-blue-400', bg: 'bg-blue-900/30 border-blue-800' },
  NOT_APPLICABLE: { label: 'N/A', icon: Shield, color: 'text-gray-500', bg: 'bg-gray-800 border-gray-700' },
}

function StatusBadge({ status }) {
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.MISSING
  const Icon = cfg.icon
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border ${cfg.bg} ${cfg.color}`}>
      <Icon size={10} />
      {cfg.label}
    </span>
  )
}

function ProgressBar({ value, color = 'emerald' }) {
  const colorMap = { emerald: 'bg-emerald-500', blue: 'bg-blue-500', amber: 'bg-amber-500' }
  return (
    <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
      <div
        className={`h-full ${colorMap[color]} transition-all duration-700`}
        style={{ width: `${Math.min(value, 100)}%` }}
      />
    </div>
  )
}

function FrameworkCard({ fw, onStatusChange }) {
  const [expanded, setExpanded] = useState(false)
  const [updating, setUpdating] = useState(null)

  const handleStatusChange = async (requirementId, newStatus) => {
    setUpdating(requirementId)
    await onStatusChange(requirementId, newStatus)
    setUpdating(null)
  }

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
      {/* Header */}
      <div className="p-5">
        <div className="flex items-start justify-between mb-3">
          <div>
            <h3 className="text-lg font-bold text-white">{fw.framework}</h3>
            <span className="text-xs text-gray-500">Version {fw.version}</span>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-white">{fw.compliance_pct}%</div>
            <div className="text-xs text-gray-500">compliant</div>
          </div>
        </div>
        <ProgressBar value={fw.compliance_pct} color={fw.compliance_pct >= 80 ? 'emerald' : fw.compliance_pct >= 50 ? 'amber' : 'blue'} />

        {/* Counts */}
        <div className="grid grid-cols-5 gap-2 mt-4">
          {[
            { label: 'Complete', count: fw.complete, color: 'text-emerald-400' },
            { label: 'Partial', count: fw.partial, color: 'text-amber-400' },
            { label: 'Missing', count: fw.missing, color: 'text-red-400' },
            { label: 'Review', count: fw.needs_review, color: 'text-blue-400' },
            { label: 'N/A', count: fw.not_applicable, color: 'text-gray-500' },
          ].map(({ label, count, color }) => (
            <div key={label} className="text-center">
              <div className={`text-lg font-bold ${color}`}>{count}</div>
              <div className="text-xs text-gray-500">{label}</div>
            </div>
          ))}
        </div>

        <button
          onClick={() => setExpanded(!expanded)}
          className="mt-4 w-full flex items-center justify-center gap-2 text-sm text-gray-400 hover:text-white transition-colors"
        >
          {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          {expanded ? 'Hide' : 'Show'} {fw.total} requirements
        </button>
      </div>

      {/* Requirements Table */}
      {expanded && (
        <div className="border-t border-gray-700">
          <table className="w-full text-sm">
            <thead className="bg-gray-900">
              <tr>
                <th className="px-4 py-3 text-left text-xs text-gray-500 font-medium uppercase">Code</th>
                <th className="px-4 py-3 text-left text-xs text-gray-500 font-medium uppercase">Requirement</th>
                <th className="px-4 py-3 text-center text-xs text-gray-500 font-medium uppercase">Status</th>
                <th className="px-4 py-3 text-center text-xs text-gray-500 font-medium uppercase">Update</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {fw.requirements.map((req) => (
                <tr key={req.requirement_id} className="hover:bg-gray-750 transition-colors">
                  <td className="px-4 py-3 font-mono text-xs text-gray-400">{req.requirement_code}</td>
                  <td className="px-4 py-3 text-gray-200">{req.requirement_title}</td>
                  <td className="px-4 py-3 text-center">
                    <StatusBadge status={req.status} />
                  </td>
                  <td className="px-4 py-3 text-center">
                    <select
                      disabled={updating === req.requirement_id}
                      defaultValue={req.status}
                      onChange={(e) => handleStatusChange(req.requirement_id, e.target.value)}
                      className="bg-gray-700 border border-gray-600 text-gray-200 text-xs rounded-lg px-2 py-1 cursor-pointer disabled:opacity-50"
                    >
                      <option value="COMPLETE">Complete</option>
                      <option value="PARTIAL">Partial</option>
                      <option value="MISSING">Missing</option>
                      <option value="NEEDS_REVIEW">Needs Review</option>
                      <option value="NOT_APPLICABLE">N/A</option>
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default function CompliancePage() {
  const { session } = useAuth()
  const [matrix, setMatrix] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchMatrix = async () => {
    if (!session?.access_token) return
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API}/compliance/matrix`, {
        headers: { Authorization: `Bearer ${session.access_token}` },
      })
      if (res.ok) {
        setMatrix(await res.json())
      } else {
        setError('Failed to load compliance data.')
      }
    } catch (e) {
      setError('Network error. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  const handleStatusChange = async (requirementId, newStatus) => {
    try {
      const res = await fetch(`${API}/compliance/records/${requirementId}`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus }),
      })
      if (res.ok) {
        // Refresh the matrix
        await fetchMatrix()
      }
    } catch (e) {
      console.error('Status update failed:', e)
    }
  }

  useEffect(() => { fetchMatrix() }, [session])

  const overallPct = matrix.length
    ? Math.round(matrix.reduce((acc, fw) => acc + fw.compliance_pct, 0) / matrix.length)
    : 0

  const totalComplete = matrix.reduce((acc, fw) => acc + fw.complete, 0)
  const totalReqs = matrix.reduce((acc, fw) => acc + fw.total, 0)

  return (
    <div className="p-6 space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Shield className="text-purple-400" size={24} />
            Compliance
          </h1>
          <p className="text-gray-400 text-sm mt-1">
            Manage compliance status across ESG reporting frameworks
          </p>
        </div>
        <button
          onClick={fetchMatrix}
          disabled={loading}
          className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-300 px-4 py-2 rounded-lg text-sm transition-colors"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Overall Summary */}
      {!loading && matrix.length > 0 && (
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-4">
            <div className="text-3xl font-bold text-white">{overallPct}%</div>
            <div className="text-sm text-gray-400 mt-1">Overall Compliance</div>
          </div>
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-4">
            <div className="text-3xl font-bold text-emerald-400">{totalComplete}</div>
            <div className="text-sm text-gray-400 mt-1">Complete Requirements</div>
          </div>
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-4">
            <div className="text-3xl font-bold text-white">{totalReqs}</div>
            <div className="text-sm text-gray-400 mt-1">Total Requirements</div>
          </div>
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-4">
            <div className="text-3xl font-bold text-blue-400">{matrix.length}</div>
            <div className="text-sm text-gray-400 mt-1">Frameworks Tracked</div>
          </div>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center h-48">
          <RefreshCw size={24} className="text-gray-500 animate-spin" />
          <span className="ml-3 text-gray-400">Loading compliance data...</span>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-900/30 border border-red-800 rounded-xl p-4 text-red-400">
          {error}
        </div>
      )}

      {/* Framework Cards */}
      {!loading && matrix.length > 0 && (
        <div className="space-y-4">
          {matrix.map((fw) => (
            <FrameworkCard
              key={`${fw.framework}-${fw.version}`}
              fw={fw}
              onStatusChange={handleStatusChange}
            />
          ))}
        </div>
      )}

      {/* Empty state */}
      {!loading && matrix.length === 0 && !error && (
        <div className="bg-gray-800 border border-dashed border-gray-600 rounded-xl p-12 text-center">
          <Shield size={48} className="text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-white mb-2">No compliance frameworks loaded</h3>
          <p className="text-gray-400 text-sm max-w-md mx-auto">
            Run the database seed script to load GHG Protocol, GRI, BRSR, and ESRS frameworks.
          </p>
          <code className="mt-3 block text-xs text-emerald-400 bg-gray-900 rounded-lg p-3">
            cd backend && python -m app.db.seed
          </code>
        </div>
      )}
    </div>
  )
}
