import { useState, useEffect } from 'react'
import { BarChart3, Plus, Search, Filter, AlertCircle, ArrowUpRight, Droplet, Flame } from 'lucide-react'
import { supabase } from '../lib/supabase'

export default function EmissionsPage() {
  const [activeTab, setActiveTab] = useState('scope1') // scope1, scope2, scope3
  const [emissions, setEmissions] = useState([])
  const [facilities, setFacilities] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  
  const [formData, setFormData] = useState({
    facility_id: '',
    category: '',
    activity_value: '',
    activity_unit: 'kWh',
    period: new Date().getFullYear().toString()
  })

  useEffect(() => {
    fetchData()
  }, [activeTab])

  const fetchData = async () => {
    setIsLoading(true)
    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) return

      // Fetch facilities
      const facRes = await fetch('/api/v1/facilities/', {
        headers: { 'Authorization': `Bearer ${session.access_token}` }
      })
      if (facRes.ok) setFacilities(await facRes.json())

      // Fetch emissions for active tab
      const emRes = await fetch(`/api/v1/emissions/${activeTab}`, {
        headers: { 'Authorization': `Bearer ${session.access_token}` }
      })
      if (emRes.ok) setEmissions(await emRes.json())

    } catch (error) {
      console.error('Failed to fetch data', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const { data: { session } } = await supabase.auth.getSession()
      const payload = {
        ...formData,
        activity_value: parseFloat(formData.activity_value)
      }

      const response = await fetch(`/api/v1/emissions/${activeTab}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify(payload)
      })

      if (response.ok) {
        setIsModalOpen(false)
        setFormData({ ...formData, activity_value: '', category: '' })
        fetchData()
      }
    } catch (error) {
      console.error('Failed to create emission record', error)
    }
  }

  const getScopeDetails = () => {
    switch (activeTab) {
      case 'scope1':
        return {
          title: 'Scope 1: Direct Emissions',
          desc: 'Emissions from owned or controlled sources (e.g., company vehicles, fuel combustion).',
          icon: <Flame className="text-orange-500" />,
          categories: ['Stationary Combustion', 'Mobile Combustion', 'Fugitive Emissions', 'Process Emissions']
        }
      case 'scope2':
        return {
          title: 'Scope 2: Indirect Emissions',
          desc: 'Emissions from the generation of purchased electricity, steam, heating and cooling.',
          icon: <Droplet className="text-blue-500" />,
          categories: ['Purchased Electricity', 'Purchased Heat/Steam', 'Purchased Cooling']
        }
      case 'scope3':
        return {
          title: 'Scope 3: Value Chain',
          desc: 'All other indirect emissions that occur in a company’s value chain.',
          icon: <ArrowUpRight className="text-purple-500" />,
          categories: ['Purchased Goods', 'Capital Goods', 'Fuel-and-Energy-Related Activities', 'Upstream Transportation', 'Waste Generated in Operations', 'Business Travel', 'Employee Commuting']
        }
      default: return {}
    }
  }

  const details = getScopeDetails()
  const totalCo2e = emissions.reduce((acc, curr) => acc + curr.co2e, 0)

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Carbon Emissions</h1>
          <p className="text-[#8b949e]">Track and manage your greenhouse gas inventory</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="bg-[#14b869] text-white px-4 py-2 rounded-lg font-medium hover:bg-[#059669] transition-colors flex items-center gap-2"
        >
          <Plus size={18} /> Add Record
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 mb-8 border-b" style={{ borderColor: 'rgba(255,255,255,0.08)' }}>
        {['scope1', 'scope2', 'scope3'].map((scope) => (
          <button
            key={scope}
            onClick={() => setActiveTab(scope)}
            className={`pb-3 px-2 text-sm font-medium transition-colors border-b-2 ${
              activeTab === scope 
                ? 'border-[#14b869] text-white' 
                : 'border-transparent text-[#8b949e] hover:text-[#c9d1d9]'
            }`}
          >
            {scope.toUpperCase().replace('E', 'E ')}
          </button>
        ))}
      </div>

      {/* Summary Card */}
      <div className="bg-[#161b22] border rounded-xl p-6 mb-8" style={{ borderColor: 'rgba(255,255,255,0.08)' }}>
        <div className="flex justify-between items-start">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-white/5 flex items-center justify-center">
              {details.icon}
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">{details.title}</h2>
              <p className="text-[#8b949e] text-sm mt-1">{details.desc}</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-[#8b949e] mb-1">Total Emissions (YTD)</p>
            <p className="text-3xl font-bold text-white">{totalCo2e.toLocaleString(undefined, {maximumFractionDigits: 1})} <span className="text-sm font-normal text-[#8b949e]">tCO₂e</span></p>
          </div>
        </div>
      </div>

      {/* Data Table */}
      <div className="bg-[#161b22] border border-white/10 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-white/10 flex justify-between items-center bg-white/5">
          <div className="relative">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#8b949e]" />
            <input 
              type="text" 
              placeholder="Search records..." 
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
                <th className="p-4 text-sm font-medium text-[#8b949e]">Category</th>
                <th className="p-4 text-sm font-medium text-[#8b949e]">Facility</th>
                <th className="p-4 text-sm font-medium text-[#8b949e]">Period</th>
                <th className="p-4 text-sm font-medium text-[#8b949e]">Activity Data</th>
                <th className="p-4 text-sm font-medium text-[#8b949e]">Emissions (tCO₂e)</th>
                <th className="p-4 text-sm font-medium text-[#8b949e]">Date Added</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr><td colSpan="6" className="p-8 text-center text-[#8b949e]">Loading...</td></tr>
              ) : emissions.length === 0 ? (
                <tr>
                  <td colSpan="6" className="p-12 text-center">
                    <BarChart3 size={40} className="mx-auto mb-3 text-[#8b949e] opacity-50" />
                    <p className="text-[#c9d1d9] mb-1">No emission records found</p>
                    <p className="text-sm text-[#8b949e]">Add your first activity data record to start calculating emissions.</p>
                  </td>
                </tr>
              ) : (
                emissions.map(record => (
                  <tr key={record.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="p-4 text-sm text-white font-medium">{record.category}</td>
                    <td className="p-4 text-sm text-[#8b949e]">
                      {facilities.find(f => f.id === record.facility_id)?.name || 'Unknown Facility'}
                    </td>
                    <td className="p-4 text-sm text-[#8b949e]">{record.period}</td>
                    <td className="p-4 text-sm text-[#c9d1d9]">{record.activity_value.toLocaleString()} {record.activity_unit}</td>
                    <td className="p-4 text-sm font-semibold text-[#14b869]">{record.co2e.toLocaleString(undefined, {maximumFractionDigits: 2})}</td>
                    <td className="p-4 text-sm text-[#8b949e]">{new Date(record.created_at).toLocaleDateString()}</td>
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
              <h2 className="text-lg font-bold text-white">Add {activeTab.toUpperCase().replace('E', 'E ')} Record</h2>
              <button onClick={() => setIsModalOpen(false)} className="text-[#8b949e] hover:text-white text-2xl leading-none">&times;</button>
            </div>
            
            <form onSubmit={handleSubmit} className="p-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-[#8b949e] mb-1">Facility</label>
                  <select
                    required
                    value={formData.facility_id}
                    onChange={e => setFormData({...formData, facility_id: e.target.value})}
                    className="w-full bg-[#0d1117] border border-white/10 rounded-lg px-4 py-2 text-white outline-none focus:border-[#14b869]"
                  >
                    <option value="">Select Facility</option>
                    {facilities.map(f => (
                      <option key={f.id} value={f.id}>{f.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#8b949e] mb-1">Category</label>
                  <select
                    required
                    value={formData.category}
                    onChange={e => setFormData({...formData, category: e.target.value})}
                    className="w-full bg-[#0d1117] border border-white/10 rounded-lg px-4 py-2 text-white outline-none focus:border-[#14b869]"
                  >
                    <option value="">Select Category</option>
                    {details.categories.map(c => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-[#8b949e] mb-1">Activity Value</label>
                    <input
                      required
                      type="number"
                      step="any"
                      value={formData.activity_value}
                      onChange={e => setFormData({...formData, activity_value: e.target.value})}
                      className="w-full bg-[#0d1117] border border-white/10 rounded-lg px-4 py-2 text-white outline-none focus:border-[#14b869]"
                      placeholder="e.g. 5000"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-[#8b949e] mb-1">Unit</label>
                    <select
                      required
                      value={formData.activity_unit}
                      onChange={e => setFormData({...formData, activity_unit: e.target.value})}
                      className="w-full bg-[#0d1117] border border-white/10 rounded-lg px-4 py-2 text-white outline-none focus:border-[#14b869]"
                    >
                      <option value="kWh">kWh</option>
                      <option value="liters">Liters</option>
                      <option value="gallons">Gallons</option>
                      <option value="tons">Tons</option>
                      <option value="miles">Miles</option>
                      <option value="km">Km</option>
                      <option value="USD">USD</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#8b949e] mb-1">Period (Year)</label>
                  <input
                    required
                    type="text"
                    value={formData.period}
                    onChange={e => setFormData({...formData, period: e.target.value})}
                    className="w-full bg-[#0d1117] border border-white/10 rounded-lg px-4 py-2 text-white outline-none focus:border-[#14b869]"
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
                  Save Record
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
