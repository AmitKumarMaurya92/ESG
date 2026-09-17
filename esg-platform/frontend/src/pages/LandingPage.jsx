import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Leaf,
  BarChart3,
  Shield,
  Brain,
  ArrowRight,
  CheckCircle2,
  Globe2,
  Zap,
  FileText,
  ChevronRight,
} from 'lucide-react'

/* ── Sub-components ───────────────────────────────────────────────────────── */

function NavBar() {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', handler, { passive: true })
    return () => window.removeEventListener('scroll', handler)
  }, [])

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled ? 'glass border-b border-white/10 shadow-lg' : 'bg-transparent'
      }`}
    >
      <nav className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center animate-pulse-glow"
            style={{ background: 'linear-gradient(135deg, #14b869, #059669)' }}
          >
            <Leaf size={16} className="text-white" />
          </div>
          <span className="font-bold text-lg text-white">
            ESG<span style={{ color: '#14b869' }}>Intelligence</span>
          </span>
        </div>

        {/* Nav links */}
        <div className="hidden md:flex items-center gap-8">
          {['Platform', 'Features', 'Compliance', 'Pricing'].map((item) => (
            <a
              key={item}
              href={`#${item.toLowerCase()}`}
              className="text-sm font-medium transition-colors duration-200"
              style={{ color: '#8b949e' }}
              onMouseEnter={(e) => (e.target.style.color = '#f0f6fc')}
              onMouseLeave={(e) => (e.target.style.color = '#8b949e')}
            >
              {item}
            </a>
          ))}
        </div>

        {/* CTA buttons */}
        <div className="flex items-center gap-3">
          <Link
            to="/login"
            id="nav-login-btn"
            className="hidden md:inline-flex text-sm font-medium px-4 py-2 rounded-lg transition-colors duration-200"
            style={{ color: '#8b949e' }}
            onMouseEnter={(e) => (e.target.style.color = '#f0f6fc')}
            onMouseLeave={(e) => (e.target.style.color = '#8b949e')}
          >
            Login
          </Link>
          <Link
            to="/register"
            id="nav-get-started-btn"
            className="text-sm font-semibold px-4 py-2 rounded-lg transition-all duration-200 hover:opacity-90 hover:scale-105"
            style={{
              background: 'linear-gradient(135deg, #14b869, #059669)',
              color: '#fff',
            }}
          >
            Get Started
          </Link>
        </div>
      </nav>
    </header>
  )
}

function FeatureCard({ icon: Icon, title, description, color, delay }) {
  return (
    <div
      className="glass glass-hover rounded-2xl p-6 cursor-default transition-all duration-300 hover:-translate-y-1 animate-fade-in-up"
      style={{ animationDelay: delay }}
    >
      <div
        className="w-12 h-12 rounded-xl flex items-center justify-center mb-4"
        style={{ background: `${color}20`, border: `1px solid ${color}30` }}
      >
        <Icon size={22} style={{ color }} />
      </div>
      <h3 className="font-semibold text-white mb-2 text-base">{title}</h3>
      <p className="text-sm leading-relaxed" style={{ color: '#8b949e' }}>
        {description}
      </p>
    </div>
  )
}

function StatCard({ value, label, trend }) {
  return (
    <div className="text-center">
      <div className="text-4xl font-black mb-1 gradient-text">{value}</div>
      <div className="text-sm font-medium" style={{ color: '#8b949e' }}>
        {label}
      </div>
      {trend && (
        <div className="text-xs mt-1" style={{ color: '#14b869' }}>
          {trend}
        </div>
      )}
    </div>
  )
}

function ScopeCard({ scope, label, examples, color }) {
  return (
    <div
      className="glass rounded-2xl p-6 border-t-2 transition-all duration-300 hover:scale-105"
      style={{ borderTopColor: color }}
    >
      <div
        className="text-xs font-bold uppercase tracking-widest mb-1"
        style={{ color }}
      >
        {scope}
      </div>
      <div className="text-lg font-bold text-white mb-3">{label}</div>
      <ul className="space-y-2">
        {examples.map((ex) => (
          <li key={ex} className="flex items-center gap-2 text-sm" style={{ color: '#8b949e' }}>
            <CheckCircle2 size={14} style={{ color, flexShrink: 0 }} />
            {ex}
          </li>
        ))}
      </ul>
    </div>
  )
}

/* ── Main page ────────────────────────────────────────────────────────────── */

export default function LandingPage() {
  return (
    <div className="min-h-screen" style={{ background: '#030712' }}>
      <NavBar />

      {/* ── Hero ─────────────────────────────────────────────────────────── */}
      <section
        id="platform"
        className="relative min-h-screen flex items-center justify-center overflow-hidden"
      >
        {/* Background image */}
        <div
          className="absolute inset-0 bg-cover bg-center opacity-20"
          style={{ backgroundImage: "url('/hero-bg.jpg')" }}
        />
        {/* Gradient overlay */}
        <div
          className="absolute inset-0"
          style={{
            background:
              'radial-gradient(ellipse 80% 60% at 50% 0%, rgba(20,184,105,0.15) 0%, transparent 70%), radial-gradient(ellipse 60% 40% at 80% 80%, rgba(59,130,246,0.1) 0%, transparent 60%)',
          }}
        />

        {/* Animated orbit ring */}
        <div
          className="absolute w-[800px] h-[800px] rounded-full opacity-10 animate-spin-slow"
          style={{ border: '1px solid #14b869' }}
        />
        <div
          className="absolute w-[600px] h-[600px] rounded-full opacity-10"
          style={{ border: '1px dashed #3b82f6', animation: 'spin-slow 18s linear infinite reverse' }}
        />

        {/* Hero content */}
        <div className="relative z-10 max-w-5xl mx-auto px-6 text-center">
          {/* Badge */}
          <div
            className="inline-flex items-center gap-2 text-xs font-semibold px-3 py-1.5 rounded-full mb-6 animate-fade-in-up"
            style={{
              background: 'rgba(20,184,105,0.1)',
              border: '1px solid rgba(20,184,105,0.3)',
              color: '#14b869',
            }}
          >
            <Zap size={12} />
            AI-Powered ESG Intelligence Platform
          </div>

          {/* Headline */}
          <h1
            className="text-5xl md:text-7xl font-black leading-tight tracking-tight mb-6 animate-fade-in-up delay-100"
            style={{ color: '#f0f6fc' }}
          >
            ESG Intelligence
            <br />
            <span className="gradient-text">Platform</span>
          </h1>

          {/* Subheadline */}
          <p
            className="text-xl md:text-2xl font-light max-w-2xl mx-auto mb-10 animate-fade-in-up delay-200"
            style={{ color: '#8b949e', lineHeight: 1.7 }}
          >
            AI-powered ESG intelligence and carbon accounting.
            <br />
            Scope 1, 2 &amp; 3 emissions, compliance mapping, and AI-driven insights.
          </p>

          {/* CTA buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-in-up delay-300">
            <Link
              to="/register"
              id="hero-get-started-btn"
              className="group flex items-center gap-2 px-8 py-4 rounded-xl font-bold text-base transition-all duration-300 hover:scale-105 hover:shadow-2xl"
              style={{
                background: 'linear-gradient(135deg, #14b869, #059669)',
                color: '#fff',
                boxShadow: '0 0 30px rgba(20,184,105,0.3)',
              }}
            >
              Get Started
              <ArrowRight size={18} className="transition-transform group-hover:translate-x-1" />
            </Link>
            <Link
              to="/login"
              id="hero-login-btn"
              className="flex items-center gap-2 px-8 py-4 rounded-xl font-semibold text-base glass glass-hover transition-all duration-300 hover:scale-105"
              style={{ color: '#f0f6fc' }}
            >
              Login
              <ChevronRight size={18} />
            </Link>
          </div>

          {/* Trust indicators */}
          <div
            className="mt-12 flex flex-wrap items-center justify-center gap-6 text-xs animate-fade-in-up delay-400"
            style={{ color: '#484f58' }}
          >
            {['GHG Protocol', 'GRI Standards', 'BRSR', 'ESRS', 'TCFD'].map((item) => (
              <span key={item} className="flex items-center gap-1.5">
                <CheckCircle2 size={12} style={{ color: '#14b869' }} />
                {item}
              </span>
            ))}
          </div>
        </div>

        {/* Scroll hint */}
        <div
          className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 animate-float"
          style={{ color: '#484f58' }}
        >
          <span className="text-xs font-medium">Scroll to explore</span>
          <div
            className="w-5 h-8 rounded-full border flex items-start justify-center pt-1"
            style={{ borderColor: '#30363d' }}
          >
            <div
              className="w-1 h-2 rounded-full animate-bounce"
              style={{ background: '#14b869' }}
            />
          </div>
        </div>
      </section>

      {/* ── Stats ──────────────────────────────────────────────────────────── */}
      <section className="py-16 border-y" style={{ borderColor: '#21262d' }}>
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <StatCard value="Scope 1/2/3" label="Complete GHG Coverage" trend="GHG Protocol aligned" />
            <StatCard value="35+" label="Reporting Phases" trend="Built incrementally" />
            <StatCard value="4" label="Compliance Frameworks" trend="GRI · BRSR · ESRS · GHG" />
            <StatCard value="AI-First" label="Architecture" trend="RAG + deterministic engine" />
          </div>
        </div>
      </section>

      {/* ── Features ───────────────────────────────────────────────────────── */}
      <section id="features" className="py-24 max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <div
            className="inline-flex items-center gap-2 text-xs font-semibold px-3 py-1.5 rounded-full mb-4"
            style={{
              background: 'rgba(59,130,246,0.1)',
              border: '1px solid rgba(59,130,246,0.3)',
              color: '#3b82f6',
            }}
          >
            <BarChart3 size={12} />
            Platform Capabilities
          </div>
          <h2 className="text-4xl font-black text-white mb-4">
            Everything you need for{' '}
            <span className="gradient-text">enterprise ESG</span>
          </h2>
          <p className="text-lg max-w-2xl mx-auto" style={{ color: '#8b949e' }}>
            From raw data ingestion to board-ready reports — all in one platform.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <FeatureCard
            icon={Leaf}
            title="Carbon Accounting Engine"
            description="Deterministic Scope 1, 2 & 3 calculations with full audit trails. Every CO₂e value is traceable back to the source document."
            color="#14b869"
            delay="0s"
          />
          <FeatureCard
            icon={Brain}
            title="AI ESG Assistant"
            description="RAG-powered assistant that answers questions using your own organizational data. Never fabricates emission factors or compliance requirements."
            color="#3b82f6"
            delay="0.1s"
          />
          <FeatureCard
            icon={Shield}
            title="Compliance Mapping"
            description="Automated mapping to GHG Protocol, GRI, BRSR, and ESRS frameworks. Know exactly what's complete, partial, or missing."
            color="#8b5cf6"
            delay="0.2s"
          />
          <FeatureCard
            icon={FileText}
            title="Document AI & OCR"
            description="Upload electricity bills, fuel invoices, and travel documents. AI extracts structured data with human review before it enters calculations."
            color="#f59e0b"
            delay="0.3s"
          />
          <FeatureCard
            icon={Globe2}
            title="Supplier Portal"
            description="Send ESG questionnaires to suppliers, collect evidence, and track Scope 3 data completeness across your entire value chain."
            color="#f43f5e"
            delay="0.4s"
          />
          <FeatureCard
            icon={BarChart3}
            title="Executive Dashboard"
            description="Real-time ESG scores, emission trends, compliance status, and risk alerts — designed for sustainability teams and C-suite executives."
            color="#14b8a6"
            delay="0.5s"
          />
        </div>
      </section>

      {/* ── Scope coverage ─────────────────────────────────────────────────── */}
      <section
        id="compliance"
        className="py-24"
        style={{ background: 'rgba(255,255,255,0.02)' }}
      >
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-black text-white mb-4">
              Complete GHG Scope Coverage
            </h2>
            <p className="text-lg" style={{ color: '#8b949e' }}>
              Deterministic, reproducible calculations — never LLM-generated numbers.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <ScopeCard
              scope="Scope 1"
              label="Direct Emissions"
              color="#f43f5e"
              examples={[
                'Stationary combustion',
                'Company vehicles',
                'Refrigerants',
                'Industrial processes',
                'Generator diesel',
              ]}
            />
            <ScopeCard
              scope="Scope 2"
              label="Indirect Energy"
              color="#f59e0b"
              examples={[
                'Purchased electricity',
                'Purchased steam',
                'Purchased heat',
                'Location-based method',
                'Market-based method',
              ]}
            />
            <ScopeCard
              scope="Scope 3"
              label="Value Chain"
              color="#3b82f6"
              examples={[
                'Business travel',
                'Employee commuting',
                'Purchased goods',
                'Waste generated',
                'Upstream transport',
              ]}
            />
          </div>
        </div>
      </section>

      {/* ── Architecture ───────────────────────────────────────────────────── */}
      <section className="py-24 max-w-7xl mx-auto px-6">
        <div className="grid md:grid-cols-2 gap-16 items-center">
          <div>
            <div
              className="inline-flex items-center gap-2 text-xs font-semibold px-3 py-1.5 rounded-full mb-4"
              style={{
                background: 'rgba(139,92,246,0.1)',
                border: '1px solid rgba(139,92,246,0.3)',
                color: '#8b5cf6',
              }}
            >
              <Brain size={12} />
              AI Architecture
            </div>
            <h2 className="text-4xl font-black text-white mb-6 leading-tight">
              AI where it helps.
              <br />
              <span className="gradient-text">Math where it matters.</span>
            </h2>
            <p className="text-lg mb-6" style={{ color: '#8b949e', lineHeight: 1.8 }}>
              Our architecture keeps the LLM in its lane. Carbon calculations use a
              deterministic engine with versioned emission factors — not an AI guess.
            </p>
            <div className="space-y-3">
              {[
                ['AI does', 'Extract data from documents, explain trends, answer questions'],
                ['AI does NOT', 'Invent emission factors, fabricate compliance rules, or generate audit evidence'],
                ['Calculations', '100% deterministic — every result is reproducible and traceable'],
              ].map(([label, desc]) => (
                <div
                  key={label}
                  className="flex gap-3 p-4 rounded-xl"
                  style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)' }}
                >
                  <CheckCircle2 size={16} style={{ color: '#14b869', marginTop: 2, flexShrink: 0 }} />
                  <div>
                    <span className="text-sm font-semibold text-white">{label}: </span>
                    <span className="text-sm" style={{ color: '#8b949e' }}>{desc}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Architecture diagram */}
          <div className="glass rounded-2xl p-8 font-mono text-sm">
            <div className="text-xs font-semibold mb-4 uppercase tracking-widest" style={{ color: '#484f58' }}>
              Data Flow Architecture
            </div>
            {[
              { label: 'Raw Data (CSV / PDF / Image)', color: '#8b949e' },
              { label: 'Validation & Normalization', color: '#f59e0b' },
              { label: 'Deterministic Calculation Engine', color: '#3b82f6' },
              { label: 'Verified Database (Supabase)', color: '#14b869' },
              { label: 'AI / RAG for Explanation & Analysis', color: '#8b5cf6' },
              { label: 'Dashboard / Reports / Assistant', color: '#14b869' },
            ].map((step, i) => (
              <div key={i} className="flex items-start gap-3 mb-3">
                <div className="flex flex-col items-center">
                  <div
                    className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
                    style={{ background: step.color + '33', border: `1px solid ${step.color}55`, color: step.color }}
                  >
                    {i + 1}
                  </div>
                  {i < 5 && (
                    <div className="w-px h-4 my-1" style={{ background: '#21262d' }} />
                  )}
                </div>
                <span className="text-sm pt-0.5" style={{ color: step.color }}>
                  {step.label}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA Section ────────────────────────────────────────────────────── */}
      <section
        id="pricing"
        className="py-24"
        style={{ background: 'rgba(20,184,105,0.04)', borderTop: '1px solid rgba(20,184,105,0.1)' }}
      >
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-5xl font-black text-white mb-6 leading-tight">
            Start your ESG journey
            <br />
            <span className="gradient-text">today.</span>
          </h2>
          <p className="text-xl mb-10" style={{ color: '#8b949e' }}>
            Register your organization, set up facilities, and begin tracking
            emissions in minutes.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/register"
              id="cta-get-started-btn"
              className="group flex items-center gap-2 px-10 py-4 rounded-xl font-bold text-lg transition-all duration-300 hover:scale-105"
              style={{
                background: 'linear-gradient(135deg, #14b869, #059669)',
                color: '#fff',
                boxShadow: '0 0 40px rgba(20,184,105,0.25)',
              }}
            >
              Get Started — Free
              <ArrowRight size={20} className="transition-transform group-hover:translate-x-1" />
            </Link>
            <Link
              to="/login"
              id="cta-login-btn"
              className="flex items-center gap-2 px-10 py-4 rounded-xl font-semibold text-lg glass glass-hover transition-all duration-300 hover:scale-105"
              style={{ color: '#f0f6fc' }}
            >
              Login
            </Link>
          </div>
          <p className="mt-6 text-sm" style={{ color: '#484f58' }}>
            No credit card required · Multi-tenant · Enterprise-ready
          </p>
        </div>
      </section>

      {/* ── Footer ─────────────────────────────────────────────────────────── */}
      <footer
        className="py-10 border-t"
        style={{ borderColor: '#21262d' }}
      >
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div
              className="w-6 h-6 rounded-md flex items-center justify-center"
              style={{ background: 'linear-gradient(135deg, #14b869, #059669)' }}
            >
              <Leaf size={12} className="text-white" />
            </div>
            <span className="text-sm font-semibold text-white">ESG Intelligence Platform</span>
          </div>
          <p className="text-xs" style={{ color: '#484f58' }}>
            © 2026 ESG Intelligence Platform · Phase 1 Foundation
          </p>
          <div className="flex items-center gap-4 text-xs" style={{ color: '#484f58' }}>
            <a href="#" className="hover:text-white transition-colors">Privacy</a>
            <a href="#" className="hover:text-white transition-colors">Terms</a>
            <a href="/api/v1/docs" className="hover:text-white transition-colors">API Docs</a>
          </div>
        </div>
      </footer>
    </div>
  )
}
