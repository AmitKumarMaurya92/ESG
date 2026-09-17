import { useState, useEffect } from 'react'
import { ShieldCheck, BookOpen, ChevronRight, CheckCircle, AlertCircle } from 'lucide-react'
import { supabase } from '../lib/supabase'

export default function CompliancePage() {
  const [records, setRecords] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  const fetchCompliance = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) return

      const response = await fetch('/api/v1/compliance/', {
        headers: { 'Authorization': `Bearer ${session.access_token}` }
      })
      if (response.ok) {
        setRecords(await response.json())
      }
    } catch (error) {
      console.error('Failed to fetch compliance', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchCompliance()
  }, [])

  // Dummy frameworks for UI demonstration of Phase 24
  const frameworks = [
    { id: 'csrd', name: 'CSRD (EU)', progress: 65, reqs: 12 },
    { id: 'sec', name: 'SEC Climate Disclosure', progress: 40, reqs: 8 },
    { id: 'ifrs', name: 'IFRS S1 & S2', progress: 85, reqs: 15 },
  ]

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Compliance Hub</h1>
          <p className="text-[#8b949e]">Map your ESG data against global regulatory frameworks.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {frameworks.map(fw => (
          <div key={fw.id} className="p-6 rounded-xl border bg-[#161b22] hover:border-[#14b869]/50 transition-colors cursor-pointer group" style={{ borderColor: 'rgba(255,255,255,0.08)' }}>
            <div className="flex justify-between items-start mb-4">
              <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-500">
                <BookOpen size={20} />
              </div>
              <ChevronRight size={20} className="text-[#8b949e] group-hover:text-white transition-colors" />
            </div>
            <h3 className="text-lg font-bold text-white mb-1">{fw.name}</h3>
            <p className="text-sm text-[#8b949e] mb-4">{fw.reqs} requirements tracked</p>
            
            <div className="w-full bg-[#0d1117] h-2 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full ${fw.progress > 80 ? 'bg-green-500' : fw.progress > 50 ? 'bg-yellow-500' : 'bg-orange-500'}`}
                style={{ width: `${fw.progress}%` }}
              ></div>
            </div>
            <div className="flex justify-between text-xs mt-2 text-[#8b949e]">
              <span>Progress</span>
              <span className="font-medium">{fw.progress}%</span>
            </div>
          </div>
        ))}
      </div>

      <h2 className="text-xl font-bold text-white mb-4">Recent Requirements</h2>
      <div className="bg-[#161b22] border border-white/10 rounded-xl overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-[#8b949e]">Loading compliance records...</div>
        ) : records.length === 0 ? (
          <div className="p-12 text-center border-t border-white/10">
            <ShieldCheck size={40} className="mx-auto mb-3 text-[#8b949e] opacity-50" />
            <p className="text-[#c9d1d9] mb-1">No specific requirements mapped yet.</p>
            <p className="text-sm text-[#8b949e]">Select a framework above to begin mapping data.</p>
          </div>
        ) : (
          <div className="divide-y divide-white/10">
             {/* Render records if they existed */}
          </div>
        )}
      </div>
    </div>
  )
}
