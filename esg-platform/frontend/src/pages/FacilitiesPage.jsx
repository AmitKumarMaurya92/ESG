import { useState, useEffect } from 'react'
import { Plus, Factory, MoreVertical, MapPin, CheckCircle, Clock } from 'lucide-react'
import { supabase } from '../lib/supabase'

export default function FacilitiesPage() {
  const [facilities, setFacilities] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    country: '',
    facility_type: 'office',
    is_active: true
  })

  const fetchFacilities = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) return

      const response = await fetch('/api/v1/facilities/', {
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      })
      if (response.ok) {
        const data = await response.json()
        setFacilities(data)
      }
    } catch (error) {
      console.error('Failed to fetch facilities', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchFacilities()
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const { data: { session } } = await supabase.auth.getSession()
      const response = await fetch('/api/v1/facilities/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify(formData)
      })

      if (response.ok) {
        setIsModalOpen(false)
        setFormData({ name: '', country: '', facility_type: 'office', is_active: true })
        fetchFacilities()
      }
    } catch (error) {
      console.error('Failed to create facility', error)
    }
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Facilities</h1>
          <p className="text-[#8b949e]">Manage your operational sites and properties</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="bg-[#14b869] text-white px-4 py-2 rounded-lg font-medium hover:bg-[#059669] transition-colors flex items-center gap-2"
        >
          <Plus size={18} /> Add Facility
        </button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-64 text-[#8b949e]">
          Loading facilities...
        </div>
      ) : facilities.length === 0 ? (
        <div className="text-center py-16 border border-dashed rounded-xl" style={{ borderColor: 'rgba(255,255,255,0.1)', background: 'rgba(22,27,34,0.3)' }}>
          <Factory size={48} className="mx-auto mb-4 text-[#8b949e] opacity-50" />
          <h3 className="text-xl font-medium text-white mb-2">No facilities yet</h3>
          <p className="text-[#8b949e] max-w-sm mx-auto mb-6">
            Add your first facility to start tracking emissions across different locations.
          </p>
          <button
            onClick={() => setIsModalOpen(true)}
            className="text-[#14b869] font-medium hover:underline"
          >
            Add a facility
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {facilities.map(facility => (
            <div key={facility.id} className="p-6 rounded-xl border bg-[#161b22]" style={{ borderColor: 'rgba(255,255,255,0.08)' }}>
              <div className="flex justify-between items-start mb-4">
                <div className="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center text-[#14b869]">
                  <Factory size={20} />
                </div>
                <button className="text-[#8b949e] hover:text-white transition-colors">
                  <MoreVertical size={18} />
                </button>
              </div>
              <h3 className="text-lg font-bold text-white mb-1">{facility.name}</h3>
              <p className="text-sm text-[#8b949e] capitalize">{facility.facility_type.replace('_', ' ')}</p>
              
              <div className="mt-6 pt-4 border-t flex flex-col gap-3" style={{ borderColor: 'rgba(255,255,255,0.08)' }}>
                <div className="flex items-center gap-2 text-sm text-[#c9d1d9]">
                  <MapPin size={14} className="text-[#8b949e]" /> {facility.country}
                </div>
                <div className="flex items-center gap-2 text-sm text-[#c9d1d9]">
                  {facility.is_active ? (
                    <><CheckCircle size={14} className="text-green-500" /> Active Site</>
                  ) : (
                    <><Clock size={14} className="text-orange-500" /> Inactive</>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
          <div className="bg-[#161b22] border border-white/10 rounded-xl w-full max-w-md shadow-2xl overflow-hidden">
            <div className="px-6 py-4 border-b border-white/10 flex justify-between items-center bg-white/5">
              <h2 className="text-lg font-bold text-white">Add New Facility</h2>
              <button onClick={() => setIsModalOpen(false)} className="text-[#8b949e] hover:text-white text-2xl leading-none">&times;</button>
            </div>
            
            <form onSubmit={handleSubmit} className="p-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-[#8b949e] mb-1">Facility Name</label>
                  <input
                    required
                    type="text"
                    value={formData.name}
                    onChange={e => setFormData({...formData, name: e.target.value})}
                    className="w-full bg-[#0d1117] border border-white/10 rounded-lg px-4 py-2 text-white outline-none focus:border-[#14b869]"
                    placeholder="e.g. London HQ"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#8b949e] mb-1">Country</label>
                  <input
                    required
                    type="text"
                    value={formData.country}
                    onChange={e => setFormData({...formData, country: e.target.value})}
                    className="w-full bg-[#0d1117] border border-white/10 rounded-lg px-4 py-2 text-white outline-none focus:border-[#14b869]"
                    placeholder="e.g. United Kingdom"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#8b949e] mb-1">Facility Type</label>
                  <select
                    value={formData.facility_type}
                    onChange={e => setFormData({...formData, facility_type: e.target.value})}
                    className="w-full bg-[#0d1117] border border-white/10 rounded-lg px-4 py-2 text-white outline-none focus:border-[#14b869]"
                  >
                    <option value="office">Office</option>
                    <option value="manufacturing">Manufacturing</option>
                    <option value="warehouse">Warehouse</option>
                    <option value="data_center">Data Center</option>
                    <option value="retail">Retail</option>
                  </select>
                </div>
                <div className="flex items-center gap-2 pt-2">
                  <input
                    type="checkbox"
                    id="is_active"
                    checked={formData.is_active}
                    onChange={e => setFormData({...formData, is_active: e.target.checked})}
                    className="w-4 h-4 rounded border-white/10 bg-[#0d1117]"
                  />
                  <label htmlFor="is_active" className="text-sm text-[#8b949e]">This facility is currently active</label>
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
                  Create Facility
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
