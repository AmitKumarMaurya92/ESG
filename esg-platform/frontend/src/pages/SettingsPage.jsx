import { useState, useEffect } from 'react'
import { User, Building2, Bell, Shield, Save, Key } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { supabase } from '../lib/supabase'

export default function SettingsPage() {
  const { user } = useAuth()
  const [activeTab, setActiveTab] = useState('profile')
  const [isLoading, setIsLoading] = useState(false)
  const [isSaved, setIsSaved] = useState(false)
  
  const [profileData, setProfileData] = useState({
    fullName: '',
    email: user?.email || '',
    role: 'Organization Admin'
  })

  const [orgData, setOrgData] = useState({
    name: 'Acme Corp',
    industry: 'Manufacturing',
    country: 'United States',
    fiscalYearEnd: 'December'
  })

  const handleSave = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    
    // Simulate API save
    setTimeout(() => {
      setIsLoading(false)
      setIsSaved(true)
      setTimeout(() => setIsSaved(false), 3000)
    }, 800)
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
          <p className="text-[#8b949e]">Manage your account, organization, and preferences.</p>
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-8">
        {/* Sidebar Nav */}
        <div className="w-full md:w-64 flex-shrink-0">
          <nav className="space-y-1">
            {[
              { id: 'profile', name: 'Profile', icon: User },
              { id: 'organization', name: 'Organization', icon: Building2 },
              { id: 'notifications', name: 'Notifications', icon: Bell },
              { id: 'security', name: 'Security', icon: Shield },
              { id: 'api', name: 'API Keys', icon: Key },
            ].map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === item.id
                    ? 'bg-[#14b869]/10 text-[#14b869]'
                    : 'text-[#8b949e] hover:bg-white/5 hover:text-white'
                }`}
              >
                <item.icon size={18} />
                {item.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Main Content */}
        <div className="flex-1">
          <div className="bg-[#161b22] border border-white/10 rounded-2xl overflow-hidden shadow-xl">
            {activeTab === 'profile' && (
              <form onSubmit={handleSave} className="p-8">
                <h2 className="text-xl font-bold text-white mb-6">Profile Settings</h2>
                
                <div className="flex items-center gap-6 mb-8">
                  <div className="w-20 h-20 rounded-full bg-[#14b869]/20 border border-[#14b869]/30 flex items-center justify-center text-[#14b869]">
                    <User size={32} />
                  </div>
                  <div>
                    <button type="button" className="bg-white/5 border border-white/10 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-white/10 transition-colors">
                      Change Avatar
                    </button>
                    <p className="text-xs text-[#8b949e] mt-2">JPG, GIF or PNG. 1MB max.</p>
                  </div>
                </div>

                <div className="space-y-6 max-w-lg">
                  <div>
                    <label className="block text-sm font-medium text-[#8b949e] mb-1">Full Name</label>
                    <input
                      type="text"
                      value={profileData.fullName}
                      onChange={(e) => setProfileData({...profileData, fullName: e.target.value})}
                      className="w-full bg-[#0d1117] border border-white/10 rounded-lg px-4 py-2 text-white outline-none focus:border-[#14b869] transition-colors"
                      placeholder="Jane Doe"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-[#8b949e] mb-1">Email Address</label>
                    <input
                      type="email"
                      value={profileData.email}
                      disabled
                      className="w-full bg-[#0d1117]/50 border border-white/5 rounded-lg px-4 py-2 text-[#8b949e] outline-none cursor-not-allowed"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-[#8b949e] mb-1">Role</label>
                    <input
                      type="text"
                      value={profileData.role}
                      disabled
                      className="w-full bg-[#0d1117]/50 border border-white/5 rounded-lg px-4 py-2 text-[#8b949e] outline-none cursor-not-allowed"
                    />
                  </div>
                </div>
                
                <div className="mt-8 pt-6 border-t border-white/10 flex items-center gap-4">
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="bg-[#14b869] text-white px-6 py-2 rounded-lg font-medium hover:bg-[#059669] transition-colors flex items-center gap-2 disabled:opacity-50"
                  >
                    <Save size={18} />
                    {isLoading ? 'Saving...' : 'Save Changes'}
                  </button>
                  {isSaved && <span className="text-sm text-[#14b869] flex items-center gap-1.5 animate-in fade-in">Saved successfully!</span>}
                </div>
              </form>
            )}

            {activeTab === 'organization' && (
              <form onSubmit={handleSave} className="p-8">
                <h2 className="text-xl font-bold text-white mb-6">Organization Details</h2>
                <div className="space-y-6 max-w-lg">
                  <div>
                    <label className="block text-sm font-medium text-[#8b949e] mb-1">Organization Name</label>
                    <input
                      type="text"
                      value={orgData.name}
                      onChange={(e) => setOrgData({...orgData, name: e.target.value})}
                      className="w-full bg-[#0d1117] border border-white/10 rounded-lg px-4 py-2 text-white outline-none focus:border-[#14b869] transition-colors"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-[#8b949e] mb-1">Industry</label>
                    <input
                      type="text"
                      value={orgData.industry}
                      onChange={(e) => setOrgData({...orgData, industry: e.target.value})}
                      className="w-full bg-[#0d1117] border border-white/10 rounded-lg px-4 py-2 text-white outline-none focus:border-[#14b869] transition-colors"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-[#8b949e] mb-1">Country HQ</label>
                    <input
                      type="text"
                      value={orgData.country}
                      onChange={(e) => setOrgData({...orgData, country: e.target.value})}
                      className="w-full bg-[#0d1117] border border-white/10 rounded-lg px-4 py-2 text-white outline-none focus:border-[#14b869] transition-colors"
                    />
                  </div>
                </div>
                
                <div className="mt-8 pt-6 border-t border-white/10">
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="bg-[#14b869] text-white px-6 py-2 rounded-lg font-medium hover:bg-[#059669] transition-colors flex items-center gap-2 disabled:opacity-50"
                  >
                    <Save size={18} />
                    {isLoading ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              </form>
            )}

            {['notifications', 'security', 'api'].includes(activeTab) && (
              <div className="p-16 text-center">
                <Shield size={48} className="mx-auto mb-4 text-[#8b949e] opacity-30" />
                <h3 className="text-xl font-bold text-white mb-2">Module Under Construction</h3>
                <p className="text-[#8b949e]">These settings will be available in the next release phase.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
