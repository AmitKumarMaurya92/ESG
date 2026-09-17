import React from 'react'
import { useSupabaseStatus } from '../hooks/useSupabaseStatus'

export function SupabaseStatusWidget() {
  const { statusData, loading, error, refresh } = useSupabaseStatus()

  const isHealthy = statusData?.status === 'healthy'
  const isDegraded = statusData?.status === 'degraded'

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-5 shadow-2xl backdrop-blur-md text-slate-100 max-w-md">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="relative flex h-3 w-3">
            <span
              className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                isHealthy ? 'bg-emerald-400' : isDegraded ? 'bg-amber-400' : 'bg-rose-400'
              }`}
            ></span>
            <span
              className={`relative inline-flex rounded-full h-3 w-3 ${
                isHealthy ? 'bg-emerald-500' : isDegraded ? 'bg-amber-500' : 'bg-rose-500'
              }`}
            ></span>
          </div>
          <div>
            <h3 className="font-semibold text-sm tracking-wide text-slate-200">
              Supabase Status
            </h3>
            <p className="text-xs text-slate-400">
              {loading
                ? 'Checking connection...'
                : isHealthy
                ? 'All services operational'
                : 'Degraded connection'}
            </p>
          </div>
        </div>

        <button
          onClick={refresh}
          disabled={loading}
          className="px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors cursor-pointer disabled:opacity-50"
        >
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {error ? (
        <div className="mt-4 p-3 rounded-lg bg-rose-950/40 border border-rose-800/50 text-rose-300 text-xs">
          {error}
        </div>
      ) : (
        <div className="mt-4 space-y-2.5 text-xs">
          <div className="flex items-center justify-between py-1 px-2 rounded bg-slate-950/50">
            <span className="text-slate-400">PostgreSQL DB</span>
            <span
              className={`font-mono font-medium ${
                statusData?.database?.connected ? 'text-emerald-400' : 'text-rose-400'
              }`}
            >
              {statusData?.database?.connected ? 'Connected' : 'Offline'}
            </span>
          </div>

          <div className="flex items-center justify-between py-1 px-2 rounded bg-slate-950/50">
            <span className="text-slate-400">Supabase Client</span>
            <span
              className={`font-mono font-medium ${
                statusData?.supabase?.client_ready ? 'text-emerald-400' : 'text-amber-400'
              }`}
            >
              {statusData?.supabase?.client_ready ? 'Ready' : 'Mock / Standby'}
            </span>
          </div>

          <div className="flex items-center justify-between py-1 px-2 rounded bg-slate-950/50">
            <span className="text-slate-400">Storage Bucket</span>
            <span className="font-mono text-slate-300">
              {statusData?.config?.storage_bucket || 'esg-documents'}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
