import { useState, useEffect } from 'react'
import { FileCheck, Download, Plus, Search, Eye } from 'lucide-react'
import { supabase } from '../lib/supabase'

export default function ReportsPage() {
  const [reports, setReports] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    report_type: 'Carbon',
    period: new Date().getFullYear().toString(),
    format: 'PDF'
  })

  const fetchReports = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) return

      const response = await fetch('/api/v1/reports/', {
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      })
      if (response.ok) {
        setReports(await response.json())
      }
    } catch (error) {
      console.error('Failed to fetch reports', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchReports()
    
    // Polling for generating reports
    const interval = setInterval(() => {
      fetchReports()
    }, 10000)
    
    return () => clearInterval(interval)
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const { data: { session } } = await supabase.auth.getSession()
      const response = await fetch('/api/v1/reports/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify(formData)
      })

      if (response.ok) {
        setIsModalOpen(false)
        setFormData({ title: '', report_type: 'Carbon', period: new Date().getFullYear().toString(), format: 'PDF' })
        fetchReports()
      }
    } catch (error) {
      console.error('Failed to create report', error)
    }
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Automated Reports</h1>
          <p className="text-[#8b949e]">Generate and download ESG disclosures and internal reports</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="bg-[#14b869] text-white px-4 py-2 rounded-lg font-medium hover:bg-[#059669] transition-colors flex items-center gap-2"
        >
          <Plus size={18} /> Generate Report
        </button>
      </div>

      <div className="bg-[#161b22] border border-white/10 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-white/10 flex justify-between items-center bg-white/5">
          <div className="relative">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#8b949e]" />
            <input 
              type="text" 
              placeholder="Search reports..." 
              className="bg-[#0d1117] border border-white/10 rounded-lg pl-9 pr-4 py-1.5 text-sm text-white outline-none focus:border-[#14b869]"
            />
          </div>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-white/10 bg-[#0d1117]/50">
                <th className="p-4 text-sm font-medium text-[#8b949e]">Title</th>
                <th className="p-4 text-sm font-medium text-[#8b949e]">Type</th>
                <th className="p-4 text-sm font-medium text-[#8b949e]">Period</th>
                <th className="p-4 text-sm font-medium text-[#8b949e]">Format</th>
                <th className="p-4 text-sm font-medium text-[#8b949e]">Status</th>
                <th className="p-4 text-sm font-medium text-[#8b949e]">Date</th>
                <th className="p-4 text-sm font-medium text-[#8b949e] w-20">Actions</th>
              </tr>
            </thead>
            <tbody>
              {isLoading && reports.length === 0 ? (
                <tr><td colSpan="7" className="p-8 text-center text-[#8b949e]">Loading...</td></tr>
              ) : reports.length === 0 ? (
                <tr>
                  <td colSpan="7" className="p-12 text-center">
                    <FileCheck size={40} className="mx-auto mb-3 text-[#8b949e] opacity-50" />
                    <p className="text-[#c9d1d9] mb-1">No reports generated</p>
                    <p className="text-sm text-[#8b949e]">Create your first report to see it here.</p>
                  </td>
                </tr>
              ) : (
                reports.map(report => (
                  <tr key={report.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="p-4 text-sm text-white font-medium">{report.title}</td>
                    <td className="p-4 text-sm text-[#8b949e]">{report.report_type}</td>
                    <td className="p-4 text-sm text-[#8b949e]">{report.period}</td>
                    <td className="p-4 text-sm text-[#8b949e]">{report.format}</td>
                    <td className="p-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${
                        report.status === 'COMPLETED' ? 'bg-green-500/10 text-green-400 border-green-500/20' :
                        report.status === 'GENERATING' ? 'bg-orange-500/10 text-orange-400 border-orange-500/20' :
                        'bg-red-500/10 text-red-400 border-red-500/20'
                      }`}>
                        {report.status}
                      </span>
                    </td>
                    <td className="p-4 text-sm text-[#8b949e]">{new Date(report.created_at).toLocaleDateString()}</td>
                    <td className="p-4">
                      <div className="flex gap-2">
                        <button 
                          disabled={report.status !== 'COMPLETED'}
                          className="text-[#8b949e] hover:text-[#14b869] transition-colors disabled:opacity-30 disabled:hover:text-[#8b949e]"
                          title="View"
                        >
                          <Eye size={18} />
                        </button>
                        <button 
                          disabled={report.status !== 'COMPLETED'}
                          className="text-[#8b949e] hover:text-[#14b869] transition-colors disabled:opacity-30 disabled:hover:text-[#8b949e]"
                          title="Download"
                        >
                          <Download size={18} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
          <div className="bg-[#161b22] border border-white/10 rounded-xl w-full max-w-md shadow-2xl overflow-hidden">
            <div className="px-6 py-4 border-b border-white/10 flex justify-between items-center bg-white/5">
              <h2 className="text-lg font-bold text-white">Generate Report</h2>
              <button onClick={() => setIsModalOpen(false)} className="text-[#8b949e] hover:text-white text-2xl leading-none">&times;</button>
            </div>
            
            <form onSubmit={handleSubmit} className="p-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-[#8b949e] mb-1">Report Title</label>
                  <input
                    required
                    type="text"
                    value={formData.title}
                    onChange={e => setFormData({...formData, title: e.target.value})}
                    className="w-full bg-[#0d1117] border border-white/10 rounded-lg px-4 py-2 text-white outline-none focus:border-[#14b869]"
                    placeholder="e.g. Q3 2024 Carbon Report"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#8b949e] mb-1">Report Type</label>
                  <select
                    required
                    value={formData.report_type}
                    onChange={e => setFormData({...formData, report_type: e.target.value})}
                    className="w-full bg-[#0d1117] border border-white/10 rounded-lg px-4 py-2 text-white outline-none focus:border-[#14b869]"
                  >
                    <option value="Carbon">Carbon Emissions</option>
                    <option value="ESG">Full ESG Disclosure</option>
                    <option value="Compliance">Compliance Status</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#8b949e] mb-1">Reporting Period</label>
                  <input
                    required
                    type="text"
                    value={formData.period}
                    onChange={e => setFormData({...formData, period: e.target.value})}
                    className="w-full bg-[#0d1117] border border-white/10 rounded-lg px-4 py-2 text-white outline-none focus:border-[#14b869]"
                    placeholder="e.g. 2024"
                  />
                </div>
              </div>
              
              <div className="mt-8 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-lg text-sm font-medium text-[#8b949e] hover:text-white transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg text-sm font-medium bg-[#14b869] text-white hover:bg-[#059669] transition-colors"
                >
                  Generate
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
