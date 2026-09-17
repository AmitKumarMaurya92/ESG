import { useState, useEffect } from 'react'
import { Users, Search, Plus, Filter, AlertTriangle, ShieldCheck } from 'lucide-react'
import { supabase } from '../lib/supabase'

export default function SuppliersPage() {
  const [suppliers, setSuppliers] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    contact_email: '',
    category: 'Manufacturing',
    status: 'ACTIVE',
    risk_level: 'UNKNOWN'
  })

  const fetchSuppliers = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) return

      const response = await fetch('/api/v1/suppliers/', {
        headers: { 'Authorization': `Bearer ${session.access_token}` }
      })
      if (response.ok) {
        setSuppliers(await response.json())
      }
    } catch (error) {
      console.error('Failed to fetch suppliers', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchSuppliers()
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const { data: { session } } = await supabase.auth.getSession()
      const response = await fetch('/api/v1/suppliers/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify(formData)
      })

      if (response.ok) {
        setIsModalOpen(false)
        setFormData({ name: '', contact_email: '', category: 'Manufacturing', status: 'ACTIVE', risk_level: 'UNKNOWN' })
        fetchSuppliers()
      }
    } catch (error) {
      console.error('Failed to create supplier', error)
    }
  }

  const getRiskBadge = (level) => {
    const styles = {
      'LOW': 'bg-green-500/10 text-green-400 border-green-500/20',
      'MEDIUM': 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
      'HIGH': 'bg-orange-500/10 text-orange-400 border-orange-500/20',
      'CRITICAL': 'bg-red-500/10 text-red-400 border-red-500/20',
      'UNKNOWN': 'bg-gray-500/10 text-gray-400 border-gray-500/20'
    }
    return <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${styles[level] || styles['UNKNOWN']}`}>{level}</span>
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Supplier Network</h1>
          <p className="text-[#8b949e]">Manage supply chain partners and monitor Scope 3 upstream risk.</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="bg-[#14b869] text-white px-4 py-2 rounded-lg font-medium hover:bg-[#059669] transition-colors flex items-center gap-2"
        >
          <Plus size={18} /> Add Supplier
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="p-6 rounded-xl border bg-[#161b22]" style={{ borderColor: 'rgba(255,255,255,0.08)' }}>
          <div className="flex items-center gap-3 mb-3 text-blue-500">
            <Users size={20} />
            <span className="text-sm font-medium text-[#8b949e]">Total Suppliers</span>
          </div>
          <div className="text-3xl font-bold text-white mb-1">{suppliers.length}</div>
        </div>
        <div className="p-6 rounded-xl border bg-[#161b22]" style={{ borderColor: 'rgba(255,255,255,0.08)' }}>
          <div className="flex items-center gap-3 mb-3 text-orange-500">
            <AlertTriangle size={20} />
            <span className="text-sm font-medium text-[#8b949e]">High Risk</span>
          </div>
          <div className="text-3xl font-bold text-white mb-1">
            {suppliers.filter(s => ['HIGH', 'CRITICAL'].includes(s.risk_level)).length}
          </div>
        </div>
        <div className="p-6 rounded-xl border bg-[#161b22]" style={{ borderColor: 'rgba(255,255,255,0.08)' }}>
          <div className="flex items-center gap-3 mb-3 text-green-500">
            <ShieldCheck size={20} />
            <span className="text-sm font-medium text-[#8b949e]">Data Covered</span>
          </div>
          <div className="text-3xl font-bold text-white mb-1">0%</div>
        </div>
      </div>

      <div className="bg-[#161b22] border border-white/10 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-white/10 flex justify-between items-center bg-white/5">
          <div className="relative">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#8b949e]" />
            <input 
              type="text" 
              placeholder="Search suppliers..." 
              className="bg-[#0d1117] border border-white/10 rounded-lg pl-9 pr-4 py-1.5 text-sm text-white outline-none focus:border-[#14b869]"
            />
          </div>
          <button className="flex items-center gap-2 text-sm text-[#8b949e] hover:text-white transition-colors">
            <Filter size={16} /> Filter
          </button>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-white/10 bg-[#0d1117]/50">
                <th className="p-4 text-sm font-medium text-[#8b949e]">Name</th>
                <th className="p-4 text-sm font-medium text-[#8b949e]">Category</th>
                <th className="p-4 text-sm font-medium text-[#8b949e]">Contact</th>
                <th className="p-4 text-sm font-medium text-[#8b949e]">Status</th>
                <th className="p-4 text-sm font-medium text-[#8b949e]">Risk Level</th>
                <th className="p-4 text-sm font-medium text-[#8b949e]">Added</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr><td colSpan="6" className="p-8 text-center text-[#8b949e]">Loading...</td></tr>
              ) : suppliers.length === 0 ? (
                <tr>
                  <td colSpan="6" className="p-12 text-center">
                    <Users size={40} className="mx-auto mb-3 text-[#8b949e] opacity-50" />
                    <p className="text-[#c9d1d9] mb-1">No suppliers found</p>
                    <p className="text-sm text-[#8b949e]">Add your tier-1 suppliers to begin tracking value chain emissions.</p>
                  </td>
                </tr>
              ) : (
                suppliers.map(sup => (
                  <tr key={sup.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="p-4 text-sm text-white font-medium">{sup.name}</td>
                    <td className="p-4 text-sm text-[#8b949e]">{sup.category}</td>
                    <td className="p-4 text-sm text-[#8b949e]">{sup.contact_email || '-'}</td>
                    <td className="p-4 text-sm">
                      <span className="flex items-center gap-1.5 text-[#8b949e]">
                        <span className={`w-2 h-2 rounded-full ${sup.status === 'ACTIVE' ? 'bg-green-500' : 'bg-gray-500'}`}></span>
                        {sup.status}
                      </span>
                    </td>
                    <td className="p-4">{getRiskBadge(sup.risk_level)}</td>
                    <td className="p-4 text-sm text-[#8b949e]">{new Date(sup.created_at).toLocaleDateString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
          <div className="bg-[#161b22] border border-white/10 rounded-xl w-full max-w-md shadow-2xl overflow-hidden">
            <div className="px-6 py-4 border-b border-white/10 flex justify-between items-center bg-white/5">
              <h2 className="text-lg font-bold text-white">Add Supplier</h2>
              <button onClick={() => setIsModalOpen(false)} className="text-[#8b949e] hover:text-white text-2xl leading-none">&times;</button>
            </div>
            
            <form onSubmit={handleSubmit} className="p-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-[#8b949e] mb-1">Supplier Name</label>
                  <input
                    required
                    type="text"
                    value={formData.name}
                    onChange={e => setFormData({...formData, name: e.target.value})}
                    className="w-full bg-[#0d1117] border border-white/10 rounded-lg px-4 py-2 text-white outline-none focus:border-[#14b869]"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#8b949e] mb-1">Contact Email</label>
                  <input
                    type="email"
                    value={formData.contact_email}
                    onChange={e => setFormData({...formData, contact_email: e.target.value})}
                    className="w-full bg-[#0d1117] border border-white/10 rounded-lg px-4 py-2 text-white outline-none focus:border-[#14b869]"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#8b949e] mb-1">Category</label>
                  <select
                    value={formData.category}
                    onChange={e => setFormData({...formData, category: e.target.value})}
                    className="w-full bg-[#0d1117] border border-white/10 rounded-lg px-4 py-2 text-white outline-none focus:border-[#14b869]"
                  >
                    <option value="Manufacturing">Manufacturing</option>
                    <option value="IT & Software">IT & Software</option>
                    <option value="Logistics">Logistics</option>
                    <option value="Raw Materials">Raw Materials</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#8b949e] mb-1">Initial Risk Assessment</label>
                  <select
                    value={formData.risk_level}
                    onChange={e => setFormData({...formData, risk_level: e.target.value})}
                    className="w-full bg-[#0d1117] border border-white/10 rounded-lg px-4 py-2 text-white outline-none focus:border-[#14b869]"
                  >
                    <option value="UNKNOWN">Unknown</option>
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                    <option value="CRITICAL">Critical</option>
                  </select>
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
                  Save Supplier
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
