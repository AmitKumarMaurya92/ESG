import Sidebar from '../components/Sidebar'
import Navbar from '../components/Navbar'

export default function DashboardLayout({ children }) {
  return (
    <div className="flex min-h-screen bg-[#0d1117] text-[#c9d1d9]">
      <Sidebar />
      <div className="flex-1 ml-64 flex flex-col min-h-screen">
        <Navbar />
        <main className="flex-1 p-8 overflow-y-auto">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
