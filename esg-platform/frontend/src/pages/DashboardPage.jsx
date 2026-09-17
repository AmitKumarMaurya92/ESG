import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { BarChart3, Factory, FileText, Activity } from 'lucide-react'
import { supabase } from '../lib/supabase'

export default function DashboardPage() {
  const { user } = useAuth()
  const [summary, setSummary] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession()
        if (!session) return

        const res = await fetch('/api/v1/analytics/summary', {
          headers: { 'Authorization': `Bearer ${session.access_token}` }
        })
        if (res.ok) {
          setSummary(await res.json())
        }
      } catch (err) {
        console.error('Failed to load dashboard summary', err)
      } finally {
        setIsLoading(false)
      }
    }
    fetchSummary()
  }, [])

  return (
    <div>
      <h1 className="text-3xl font-bold text-white mb-6">Welcome to ESG Intelligence</h1>
      
      <div 
        className="p-6 rounded-xl border mb-8 flex justify-between items-center"
        style={{ 
          background: 'linear-gradient(135deg, rgba(20,184,105,0.1), rgba(22, 27, 34, 0.4))', 
          borderColor: 'rgba(20,184,105,0.2)'
        }}
      >
        <div>
          <h2 className="text-xl font-semibold text-white mb-1">Company Dashboard</h2>
          <p className="text-[#8b949e]">Your live ESG performance overview.</p>
        </div>
        <div className="bg-black/30 px-4 py-2 rounded-lg text-sm font-mono text-[#14b869]">
          Phase 19: Interactive Dashboard
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="p-6 rounded-xl border bg-[#161b22]" style={{ borderColor: 'rgba(255,255,255,0.08)' }}>
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center text-green-500">
              <BarChart3 size={20} />
            </div>
            <span className="text-sm font-medium text-[#8b949e]">Total Emissions</span>
          </div>
          <div className="text-3xl font-bold text-white mb-1">
            {isLoading ? '...' : (summary?.total_emissions_tco2e || 0).toLocaleString(undefined, {maximumFractionDigits: 1})}
          </div>
          <div className="text-sm text-[#8b949e]">tCO₂e</div>
        </div>

        <div className="p-6 rounded-xl border bg-[#161b22]" style={{ borderColor: 'rgba(255,255,255,0.08)' }}>
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-500">
              <Factory size={20} />
            </div>
            <span className="text-sm font-medium text-[#8b949e]">Active Facilities</span>
          </div>
          <div className="text-3xl font-bold text-white mb-1">
            {isLoading ? '...' : (summary?.active_facilities || 0)}
          </div>
          <div className="text-sm text-[#8b949e]">Global locations</div>
        </div>

        <div className="p-6 rounded-xl border bg-[#161b22]" style={{ borderColor: 'rgba(255,255,255,0.08)' }}>
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center text-purple-500">
              <FileText size={20} />
            </div>
            <span className="text-sm font-medium text-[#8b949e]">Processed Docs</span>
          </div>
          <div className="text-3xl font-bold text-white mb-1">
            {isLoading ? '...' : (summary?.processed_documents || 0)}
          </div>
          <div className="text-sm text-[#8b949e]">Invoices & files</div>
        </div>

        <div className="p-6 rounded-xl border bg-[#161b22]" style={{ borderColor: 'rgba(255,255,255,0.08)' }}>
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-orange-500/10 flex items-center justify-center text-orange-500">
              <Activity size={20} />
            </div>
            <span className="text-sm font-medium text-[#8b949e]">Compliance Score</span>
          </div>
          <div className="text-3xl font-bold text-white mb-1">
            {isLoading ? '...' : (summary?.compliance_score || 0)}%
          </div>
          <div className="text-sm text-[#8b949e]">Target: 100%</div>
        </div>
      </div>
      
      {/* Visual Chart Placeholder */}
      <div className="bg-[#161b22] border rounded-xl p-6 h-80 flex flex-col items-center justify-center text-center" style={{ borderColor: 'rgba(255,255,255,0.08)' }}>
        <BarChart3 size={48} className="text-[#8b949e] opacity-30 mb-4" />
        <h3 className="text-xl font-bold text-white mb-2">Emissions by Scope</h3>
        <p className="text-[#8b949e] max-w-md">Detailed visual analytics component will render here utilizing Recharts to show a breakdown of Scope 1, 2, and 3.</p>
      </div>
    </div>
  )
}
