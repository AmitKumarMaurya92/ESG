import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext.jsx'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, LineChart, Line, AreaChart, Area
} from 'recharts'
import {
  Activity, Factory, FileText, AlertTriangle, TrendingUp, TrendingDown,
  Shield, Leaf, Users, CheckCircle2, XCircle, Clock, RefreshCw, Zap
} from 'lucide-react'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const SCOPE_COLORS = {
  scope1: '#10b981',
  scope2: '#3b82f6',
  scope3: '#f59e0b',
}

const PIE_COLORS = ['#10b981', '#3b82f6', '#f59e0b']

function StatCard({ title, value, subtitle, icon: Icon, color = 'blue', trend }) {
  const colorMap = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-emerald-500 to-emerald-600',
    amber: 'from-amber-500 to-amber-600',
    red: 'from-red-500 to-red-600',
    purple: 'from-purple-500 to-purple-600',
    teal: 'from-teal-500 to-teal-600',
  }
  return (
    <div className="bg-gray-800 border border-gray-700 rounded-xl p-5 flex flex-col gap-3 hover:border-gray-600 transition-colors">
      <div className="flex items-center justify-between">
        <span className="text-sm text-gray-400 font-medium">{title}</span>
        <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${colorMap[color]} flex items-center justify-center`}>
          <Icon size={18} className="text-white" />
        </div>
      </div>
      <div>
        <div className="text-2xl font-bold text-white">
          {value !== null && value !== undefined ? value : '—'}
        </div>
        {subtitle && <div className="text-xs text-gray-500 mt-1">{subtitle}</div>}
      </div>
      {trend && (
        <div className={`flex items-center gap-1 text-xs font-medium ${trend > 0 ? 'text-red-400' : 'text-emerald-400'}`}>
          {trend > 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
          {Math.abs(trend)}% from last period
        </div>
      )}
    </div>
  )
}

function ESGScoreGauge({ score, label, color }) {
  const rotation = score ? (score / 100) * 180 - 90 : -90
  const colorMap = { green: '#10b981', blue: '#3b82f6', amber: '#f59e0b' }
  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative w-24 h-12 overflow-hidden">
        <div className="absolute w-24 h-24 rounded-full border-8 border-gray-700 bottom-0" />
        <div
          className="absolute w-24 h-24 rounded-full border-8 bottom-0 transition-transform duration-1000"
          style={{
            borderColor: colorMap[color] || '#10b981',
            clipPath: 'polygon(0 50%, 100% 50%, 100% 100%, 0 100%)',
            transform: `rotate(${rotation}deg)`,
            transformOrigin: '50% 100%',
          }}
        />
        <div className="absolute bottom-0 w-full text-center">
          <span className="text-xl font-bold text-white">{score || '—'}</span>
        </div>
      </div>
      <span className="text-xs text-gray-400">{label}</span>
    </div>
  )
}

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-gray-900 border border-gray-700 rounded-lg p-3 text-sm shadow-xl">
        <p className="text-gray-300 font-medium mb-2">{label}</p>
        {payload.map((p, i) => (
          <div key={i} className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: p.color }} />
            <span className="text-gray-400">{p.name}:</span>
            <span className="text-white font-medium">{typeof p.value === 'number' ? p.value.toLocaleString() : p.value} kgCO2e</span>
          </div>
        ))}
      </div>
    )
  }
  return null
}

export default function DashboardPage() {
  const { session } = useAuth()
  const [summary, setSummary] = useState(null)
  const [trend, setTrend] = useState([])
  const [scopeDist, setScopeDist] = useState([])
  const [facilityData, setFacilityData] = useState([])
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState(null)

  const fetchAll = async () => {
    if (!session?.access_token) return
    const headers = { Authorization: `Bearer ${session.access_token}` }

    try {
      setLoading(true)
      const [summaryRes, trendRes, distRes, facRes] = await Promise.all([
        fetch(`${API}/analytics/summary`, { headers }),
        fetch(`${API}/analytics/emissions/trend`, { headers }),
        fetch(`${API}/analytics/emissions/scope-distribution`, { headers }),
        fetch(`${API}/analytics/emissions/by-facility`, { headers }),
      ])

      if (summaryRes.ok) setSummary(await summaryRes.json())
      if (trendRes.ok) setTrend(await trendRes.json())
      if (distRes.ok) setScopeDist(await distRes.json())
      if (facRes.ok) setFacilityData(await facRes.json())
      setLastUpdated(new Date())
    } catch (err) {
      console.error('Dashboard fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchAll() }, [session])

  const fmtCO2 = (v) => v != null ? `${(v / 1000).toFixed(2)} tCO2e` : '—'
  const fmtScore = (v) => v != null ? v.toFixed(1) : null

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* ── Header ─────────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">ESG Dashboard</h1>
          <p className="text-gray-400 text-sm mt-1">
            {lastUpdated
              ? `Last updated: ${lastUpdated.toLocaleTimeString()}`
              : 'Loading organization data...'}
          </p>
        </div>
        <button
          onClick={fetchAll}
          disabled={loading}
          className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-300 px-4 py-2 rounded-lg text-sm transition-colors disabled:opacity-50"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* ── Summary Cards ────────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total GHG Emissions"
          value={fmtCO2(summary?.total_co2e)}
          subtitle="Scope 1 + 2 + 3 combined"
          icon={Leaf}
          color="green"
        />
        <StatCard
          title="ESG Score"
          value={fmtScore(summary?.esg_score)}
          subtitle="Overall weighted score"
          icon={Activity}
          color="blue"
        />
        <StatCard
          title="Compliance Rate"
          value={summary?.compliance_pct != null ? `${summary.compliance_pct}%` : '—'}
          subtitle="Across all active frameworks"
          icon={Shield}
          color="purple"
        />
        <StatCard
          title="Open Risks"
          value={summary?.open_risks ?? '—'}
          subtitle="Requiring investigation"
          icon={AlertTriangle}
          color={summary?.open_risks > 5 ? 'red' : 'amber'}
        />
      </div>

      {/* ── Second Row Cards ─────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Scope 1 (Direct)"
          value={fmtCO2(summary?.scope1_co2e)}
          subtitle="Stationary & mobile combustion"
          icon={Factory}
          color="green"
        />
        <StatCard
          title="Scope 2 (Energy)"
          value={fmtCO2(summary?.scope2_co2e)}
          subtitle="Purchased electricity & heat"
          icon={Zap}
          color="blue"
        />
        <StatCard
          title="Scope 3 (Value Chain)"
          value={fmtCO2(summary?.scope3_co2e)}
          subtitle="Supply chain & travel"
          icon={Users}
          color="amber"
        />
        <StatCard
          title="Documents"
          value={summary?.documents_count ?? '—'}
          subtitle={`Across ${summary?.facilities_count ?? 0} facilities`}
          icon={FileText}
          color="teal"
        />
      </div>

      {/* ── ESG Score Breakdown ──────────────────────────────────────────── */}
      {summary?.esg_score && (
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
          <h2 className="text-sm font-semibold text-gray-300 mb-4 uppercase tracking-wider">ESG Score Breakdown</h2>
          <div className="flex items-center justify-around">
            <ESGScoreGauge score={fmtScore(summary.overall_score)} label="Overall" color="blue" />
            <ESGScoreGauge score={fmtScore(summary.environmental_score)} label="Environmental" color="green" />
            <ESGScoreGauge score={fmtScore(summary.social_score)} label="Social" color="amber" />
            <ESGScoreGauge score={fmtScore(summary.governance_score)} label="Governance" color="green" />
          </div>
          <p className="text-xs text-gray-500 text-center mt-3">
            Methodology v1.0.0 — Weighted: Environmental 40%, Social 30%, Governance 30%
          </p>
        </div>
      )}

      {/* ── Charts Row ──────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Emissions Trend Chart */}
        <div className="lg:col-span-2 bg-gray-800 border border-gray-700 rounded-xl p-6">
          <h2 className="text-sm font-semibold text-gray-300 mb-4 uppercase tracking-wider">
            Emissions Trend
          </h2>
          {trend.length > 0 ? (
            <ResponsiveContainer width="100%" height={260}>
              <AreaChart data={trend} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
                <defs>
                  <linearGradient id="colorS1" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorS2" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorS3" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="period" tick={{ fill: '#9ca3af', fontSize: 12 }} />
                <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} />
                <Tooltip content={<CustomTooltip />} />
                <Legend wrapperStyle={{ color: '#9ca3af', fontSize: '12px' }} />
                <Area type="monotone" dataKey="scope1" name="Scope 1" stroke="#10b981" fill="url(#colorS1)" strokeWidth={2} />
                <Area type="monotone" dataKey="scope2" name="Scope 2" stroke="#3b82f6" fill="url(#colorS2)" strokeWidth={2} />
                <Area type="monotone" dataKey="scope3" name="Scope 3" stroke="#f59e0b" fill="url(#colorS3)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center text-gray-500">
              <Leaf size={40} className="mb-3 opacity-30" />
              <p className="text-sm">No emissions data recorded yet.</p>
              <p className="text-xs mt-1">Add Scope 1/2/3 records to see trends.</p>
            </div>
          )}
        </div>

        {/* Scope Distribution Pie */}
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
          <h2 className="text-sm font-semibold text-gray-300 mb-4 uppercase tracking-wider">
            Scope Distribution
          </h2>
          {scopeDist.some(d => d.value > 0) ? (
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={scopeDist}
                  cx="50%"
                  cy="50%"
                  innerRadius={65}
                  outerRadius={100}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {scopeDist.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [`${value.toLocaleString()} kgCO2e`, '']} />
                <Legend wrapperStyle={{ color: '#9ca3af', fontSize: '12px' }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center text-gray-500">
              <Activity size={40} className="mb-3 opacity-30" />
              <p className="text-sm">No emissions yet</p>
            </div>
          )}
        </div>
      </div>

      {/* ── Facility Emissions Chart ─────────────────────────────────────── */}
      {facilityData.length > 0 && (
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
          <h2 className="text-sm font-semibold text-gray-300 mb-4 uppercase tracking-wider">
            Emissions by Facility
          </h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={facilityData} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="facility_name" tick={{ fill: '#9ca3af', fontSize: 12 }} />
              <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="co2e" name="Total CO2e" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* ── Getting Started (if no data) ────────────────────────────────── */}
      {!loading && !summary?.total_co2e && (
        <div className="bg-gray-800 border border-dashed border-gray-600 rounded-xl p-8 text-center">
          <CheckCircle2 size={48} className="text-emerald-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-white mb-2">Welcome to your ESG Dashboard</h3>
          <p className="text-gray-400 text-sm max-w-md mx-auto mb-4">
            Your dashboard will populate as you add facilities, emissions records, and ESG metrics.
          </p>
          <div className="flex gap-3 justify-center flex-wrap">
            <a href="/facilities" className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg text-sm transition-colors">Add a Facility</a>
            <a href="/emissions" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm transition-colors">Record Emissions</a>
            <a href="/documents" className="bg-gray-700 hover:bg-gray-600 text-gray-200 px-4 py-2 rounded-lg text-sm transition-colors">Upload Documents</a>
          </div>
        </div>
      )}
    </div>
  )
}
