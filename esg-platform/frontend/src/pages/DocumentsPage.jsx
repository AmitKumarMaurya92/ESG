import { useState, useEffect, useRef } from 'react'
import { FileText, Upload, Trash2, File as FileIcon, FileImage, FileSpreadsheet, AlertCircle } from 'lucide-react'
import { supabase } from '../lib/supabase'

export default function DocumentsPage() {
  const [documents, setDocuments] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState('')
  const fileInputRef = useRef(null)

  const fetchDocuments = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) return

      const response = await fetch('/api/v1/documents/', {
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      })
      if (response.ok) {
        const data = await response.json()
        setDocuments(data)
      }
    } catch (error) {
      console.error('Failed to fetch documents', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchDocuments()
  }, [])

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    setIsUploading(true)
    setError('')

    const formData = new FormData()
    formData.append('file', file)

    try {
      const { data: { session } } = await supabase.auth.getSession()
      const response = await fetch('/api/v1/documents/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        },
        body: formData
      })

      if (response.ok) {
        fetchDocuments()
      } else {
        const err = await response.json()
        setError(err.detail || 'Failed to upload document')
      }
    } catch (err) {
      setError('An error occurred during upload')
    } finally {
      setIsUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this document?')) return

    try {
      const { data: { session } } = await supabase.auth.getSession()
      const response = await fetch(`/api/v1/documents/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      })

      if (response.ok) {
        setDocuments(docs => docs.filter(d => d.id !== id))
      }
    } catch (err) {
      console.error('Failed to delete', err)
    }
  }

  const getFileIcon = (mimeType) => {
    if (mimeType.includes('pdf')) return <FileText className="text-red-400" />
    if (mimeType.includes('image')) return <FileImage className="text-blue-400" />
    if (mimeType.includes('spreadsheet') || mimeType.includes('csv')) return <FileSpreadsheet className="text-green-400" />
    return <FileIcon className="text-gray-400" />
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Documents</h1>
          <p className="text-[#8b949e]">Upload invoices, utility bills, and ESG reports for AI processing</p>
        </div>
        
        <div>
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileUpload} 
            className="hidden" 
            accept=".pdf,.png,.jpg,.jpeg,.csv,.xlsx,.docx"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="bg-[#14b869] text-white px-4 py-2 rounded-lg font-medium hover:bg-[#059669] transition-colors flex items-center gap-2 disabled:opacity-50"
          >
            {isUploading ? 'Uploading...' : <><Upload size={18} /> Upload Document</>}
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-lg flex items-start gap-3" style={{ background: 'rgba(248, 81, 73, 0.1)', border: '1px solid rgba(248, 81, 73, 0.4)' }}>
          <AlertCircle size={18} style={{ color: '#f85149', marginTop: '2px', flexShrink: 0 }} />
          <p className="text-sm" style={{ color: '#f85149' }}>{error}</p>
        </div>
      )}

      <div className="bg-[#161b22] border border-white/10 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-white/10 bg-white/5">
                <th className="p-4 text-sm font-medium text-[#8b949e]">Filename</th>
                <th className="p-4 text-sm font-medium text-[#8b949e]">Type</th>
                <th className="p-4 text-sm font-medium text-[#8b949e]">Size</th>
                <th className="p-4 text-sm font-medium text-[#8b949e]">Status</th>
                <th className="p-4 text-sm font-medium text-[#8b949e]">Date</th>
                <th className="p-4 text-sm font-medium text-[#8b949e] w-10"></th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan="6" className="p-8 text-center text-[#8b949e]">Loading documents...</td>
                </tr>
              ) : documents.length === 0 ? (
                <tr>
                  <td colSpan="6" className="p-12 text-center">
                    <FileText size={40} className="mx-auto mb-3 text-[#8b949e] opacity-50" />
                    <p className="text-[#c9d1d9] mb-1">No documents uploaded yet</p>
                    <p className="text-sm text-[#8b949e]">Upload utility bills or data files to begin.</p>
                  </td>
                </tr>
              ) : (
                documents.map(doc => (
                  <tr key={doc.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="p-4">
                      <div className="flex items-center gap-3">
                        {getFileIcon(doc.mime_type)}
                        <span className="text-white font-medium truncate max-w-[300px]">{doc.filename}</span>
                      </div>
                    </td>
                    <td className="p-4 text-[#8b949e] text-sm">{doc.mime_type.split('/')[1]?.toUpperCase() || 'FILE'}</td>
                    <td className="p-4 text-[#8b949e] text-sm">{(doc.size_bytes / 1024).toFixed(1)} KB</td>
                    <td className="p-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${
                        doc.processing_status === 'UPLOADED' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' :
                        doc.processing_status === 'PROCESSING' ? 'bg-orange-500/10 text-orange-400 border-orange-500/20' :
                        doc.processing_status === 'EXTRACTED' ? 'bg-green-500/10 text-green-400 border-green-500/20' :
                        'bg-gray-500/10 text-gray-400 border-gray-500/20'
                      }`}>
                        {doc.processing_status}
                      </span>
                    </td>
                    <td className="p-4 text-[#8b949e] text-sm">{new Date(doc.created_at).toLocaleDateString()}</td>
                    <td className="p-4">
                      <button 
                        onClick={() => handleDelete(doc.id)}
                        className="text-[#8b949e] hover:text-[#f85149] transition-colors"
                      >
                        <Trash2 size={18} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
