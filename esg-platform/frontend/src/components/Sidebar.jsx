import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, Factory, FileText, BarChart3, ShieldCheck, FileCheck, Settings, Users, ArrowLeftRight, Sparkles } from 'lucide-react'

export default function Sidebar() {
  const location = useLocation()
  
  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Emissions', path: '/emissions', icon: BarChart3 },
    { name: 'ESG Metrics', path: '/esg', icon: ArrowLeftRight },
    { name: 'Compliance', path: '/compliance', icon: ShieldCheck },
    { name: 'Documents', path: '/documents', icon: FileText },
    { name: 'Facilities', path: '/facilities', icon: Factory },
    { name: 'Suppliers', path: '/suppliers', icon: Users },
    { name: 'Reports', path: '/reports', icon: FileCheck },
    { name: 'AI Assistant', path: '/assistant', icon: Sparkles },
    { name: 'Settings', path: '/settings', icon: Settings },
  ]

  return (
    <div className="w-64 border-r flex flex-col h-screen fixed" style={{ background: '#0d1117', borderColor: 'rgba(255,255,255,0.08)' }}>
      <div className="p-6">
        <Link to="/dashboard" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #14b869, #059669)' }}>
            <span className="font-bold text-white text-sm">E</span>
          </div>
          <span className="font-bold text-white tracking-wide">
            ESG<span style={{ color: '#14b869' }}>Intelligence</span>
          </span>
        </Link>
      </div>

      <nav className="flex-1 px-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path || location.pathname.startsWith(`${item.path}/`)
          return (
            <Link
              key={item.name}
              to={item.path}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors duration-200 text-sm font-medium ${
                isActive 
                  ? 'bg-[#14b869]/10 text-[#14b869]' 
                  : 'text-[#8b949e] hover:bg-white/5 hover:text-white'
              }`}
            >
              <item.icon size={18} className={isActive ? 'text-[#14b869]' : 'text-[#8b949e]'} />
              {item.name}
            </Link>
          )
        })}
      </nav>

      <div className="p-4 border-t" style={{ borderColor: 'rgba(255,255,255,0.08)' }}>
        <div className="bg-[#14b869]/10 rounded-lg p-4">
          <p className="text-xs text-[#14b869] font-medium mb-1">PRO Plan</p>
          <p className="text-xs text-[#8b949e]">Using 45% of data limits</p>
          <div className="h-1.5 w-full bg-black/40 rounded-full mt-2 overflow-hidden">
            <div className="h-full bg-[#14b869] rounded-full" style={{ width: '45%' }}></div>
          </div>
        </div>
      </div>
    </div>
  )
}
