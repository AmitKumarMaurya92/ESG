import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Check, Building2, Factory, FileCheck, ArrowRight } from 'lucide-react'

export default function OnboardingPage() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [isLoading, setIsLoading] = useState(false)
  
  // Form state
  const [companyInfo, setCompanyInfo] = useState({
    industry: '',
    country: '',
    employee_count: '',
    revenue: '',
    financial_year: 'December',
    reporting_year: new Date().getFullYear()
  })

  const [frameworks, setFrameworks] = useState({
    GHG_PROTOCOL: true,
    GRI: false,
    BRSR: false,
    ESRS: false
  })

  const handleComplete = async () => {
    setIsLoading(true)
    try {
      // Get the token from session
      // const session = await supabase.auth.getSession()
      
      // Update organization details
      // await fetch('/api/v1/organizations/me', { ... })
      
      setTimeout(() => {
        setIsLoading(false)
        navigate('/dashboard')
      }, 1000)
    } catch (err) {
      console.error(err)
      setIsLoading(false)
    }
  }

  const steps = [
    { id: 1, name: 'Company Details', icon: Building2 },
    { id: 2, name: 'Reporting Frameworks', icon: FileCheck },
    { id: 3, name: 'Finish', icon: Check }
  ]

  return (
    <div className="min-h-screen bg-[#0d1117] text-[#c9d1d9] flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-3xl">
        <div className="mb-12 text-center">
          <h1 className="text-3xl font-bold text-white mb-4">Welcome to ESG Intelligence</h1>
          <p className="text-[#8b949e]">Let's set up your organization's workspace.</p>
        </div>

        {/* Stepper */}
        <div className="flex items-center justify-between mb-12 relative">
          <div className="absolute left-0 top-1/2 w-full h-0.5 bg-white/10 -z-10 -translate-y-1/2"></div>
          {steps.map((s) => (
            <div key={s.id} className="flex flex-col items-center gap-2 bg-[#0d1117] px-4">
              <div 
                className={`w-12 h-12 rounded-full flex items-center justify-center transition-colors ${
                  step >= s.id 
                    ? 'bg-[#14b869] text-white shadow-[0_0_15px_rgba(20,184,105,0.4)]' 
                    : 'bg-white/5 text-[#8b949e] border border-white/10'
                }`}
              >
                <s.icon size={20} />
              </div>
              <span className={`text-sm font-medium ${step >= s.id ? 'text-white' : 'text-[#8b949e]'}`}>
                {s.name}
              </span>
            </div>
          ))}
        </div>

        {/* Form Container */}
        <div className="bg-[#161b22] border border-white/10 rounded-2xl p-8 shadow-2xl">
          {step === 1 && (
            <div className="space-y-6 animate-in fade-in">
              <h2 className="text-xl font-bold text-white mb-6">Company Information</h2>
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-[#8b949e] mb-2">Industry</label>
                  <select 
                    className="w-full bg-[#0d1117] border border-white/10 rounded-lg px-4 py-3 text-white outline-none focus:border-[#14b869]"
                    value={companyInfo.industry}
                    onChange={(e) => setCompanyInfo({...companyInfo, industry: e.target.value})}
                  >
                    <option value="">Select Industry</option>
                    <option value="Manufacturing">Manufacturing</option>
                    <option value="Technology">Technology</option>
                    <option value="Energy">Energy</option>
                    <option value="Finance">Finance</option>
                    <option value="Retail">Retail</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#8b949e] mb-2">Country HQ</label>
                  <input 
                    type="text" 
                    placeholder="e.g. United States"
                    className="w-full bg-[#0d1117] border border-white/10 rounded-lg px-4 py-3 text-white outline-none focus:border-[#14b869]"
                    value={companyInfo.country}
                    onChange={(e) => setCompanyInfo({...companyInfo, country: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#8b949e] mb-2">Employee Count</label>
                  <input 
                    type="number" 
                    placeholder="e.g. 1500"
                    className="w-full bg-[#0d1117] border border-white/10 rounded-lg px-4 py-3 text-white outline-none focus:border-[#14b869]"
                    value={companyInfo.employee_count}
                    onChange={(e) => setCompanyInfo({...companyInfo, employee_count: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#8b949e] mb-2">Annual Revenue (USD M)</label>
                  <input 
                    type="number" 
                    placeholder="e.g. 50"
                    className="w-full bg-[#0d1117] border border-white/10 rounded-lg px-4 py-3 text-white outline-none focus:border-[#14b869]"
                    value={companyInfo.revenue}
                    onChange={(e) => setCompanyInfo({...companyInfo, revenue: e.target.value})}
                  />
                </div>
              </div>
              <div className="flex justify-end pt-4">
                <button 
                  onClick={() => setStep(2)}
                  className="bg-[#14b869] text-white px-6 py-2.5 rounded-lg font-medium hover:bg-[#059669] transition-colors flex items-center gap-2"
                >
                  Continue <ArrowRight size={18} />
                </button>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-6 animate-in fade-in">
              <h2 className="text-xl font-bold text-white mb-6">Select Reporting Frameworks</h2>
              <p className="text-sm text-[#8b949e] mb-6">Choose the frameworks you need to report against. You can change these later.</p>
              
              <div className="grid grid-cols-2 gap-4">
                {Object.entries(frameworks).map(([key, value]) => (
                  <label 
                    key={key}
                    className={`flex items-start gap-4 p-5 rounded-xl border cursor-pointer transition-all ${
                      value 
                        ? 'bg-[#14b869]/10 border-[#14b869]' 
                        : 'bg-[#0d1117] border-white/10 hover:border-white/30'
                    }`}
                  >
                    <div className={`w-6 h-6 rounded flex items-center justify-center mt-0.5 ${
                      value ? 'bg-[#14b869] text-white' : 'border border-[#8b949e]'
                    }`}>
                      {value && <Check size={16} />}
                    </div>
                    <input 
                      type="checkbox" 
                      className="hidden" 
                      checked={value}
                      onChange={() => setFrameworks({...frameworks, [key]: !value})}
                    />
                    <div>
                      <h3 className="font-semibold text-white">{key.replace('_', ' ')}</h3>
                      <p className="text-xs text-[#8b949e] mt-1">Standard ESG and sustainability reporting.</p>
                    </div>
                  </label>
                ))}
              </div>

              <div className="flex justify-between pt-6">
                <button 
                  onClick={() => setStep(1)}
                  className="px-6 py-2.5 rounded-lg font-medium text-[#8b949e] hover:text-white transition-colors"
                >
                  Back
                </button>
                <button 
                  onClick={() => setStep(3)}
                  className="bg-[#14b869] text-white px-6 py-2.5 rounded-lg font-medium hover:bg-[#059669] transition-colors flex items-center gap-2"
                >
                  Continue <ArrowRight size={18} />
                </button>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-6 animate-in fade-in text-center py-8">
              <div className="w-20 h-20 bg-[#14b869]/20 rounded-full flex items-center justify-center mx-auto mb-6">
                <Check size={40} className="text-[#14b869]" />
              </div>
              <h2 className="text-2xl font-bold text-white">You're all set!</h2>
              <p className="text-[#8b949e] max-w-md mx-auto">
                Your workspace is ready. You can now start tracking your emissions, uploading documents, and managing ESG metrics.
              </p>
              
              <div className="pt-8">
                <button 
                  onClick={handleComplete}
                  disabled={isLoading}
                  className="bg-[#14b869] text-white px-8 py-3 rounded-lg font-medium hover:bg-[#059669] transition-colors shadow-[0_0_20px_rgba(20,184,105,0.3)]"
                >
                  {isLoading ? 'Setting up...' : 'Go to Dashboard'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
