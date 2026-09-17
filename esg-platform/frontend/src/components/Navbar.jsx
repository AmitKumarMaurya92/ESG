import { useAuth } from '../contexts/AuthContext'
import { LogOut, User, Bell } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    try {
      await logout()
      navigate('/login')
    } catch (error) {
      console.error('Failed to log out', error)
    }
  }

  return (
    <nav className="h-16 border-b flex items-center justify-between px-8 bg-[#0d1117]" style={{ borderColor: 'rgba(255,255,255,0.08)' }}>
      <div className="flex-1">
        {/* Breadcrumbs or page title could go here */}
      </div>
      
      <div className="flex items-center gap-6">
        <button className="text-[#8b949e] hover:text-white transition-colors relative">
          <Bell size={20} />
          <span className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>

        <div className="flex items-center gap-3 pl-6 border-l" style={{ borderColor: 'rgba(255,255,255,0.08)' }}>
          <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-white">
            <User size={16} />
          </div>
          <div className="hidden md:block">
            <p className="text-sm font-medium text-white">{user?.email}</p>
            <p className="text-xs text-[#8b949e]">Admin</p>
          </div>
          <button
            onClick={handleLogout}
            className="ml-2 text-[#8b949e] hover:text-white transition-colors"
            title="Logout"
          >
            <LogOut size={18} />
          </button>
        </div>
      </div>
    </nav>
  )
}
