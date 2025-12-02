import { useState, useEffect } from 'react'
import {
  FileText,
  Image,
  Music,
  Video,
  File,
  Trash2,
  Download,
  Calendar,
  HardDrive,
  RefreshCw,
  FolderOpen,
  AlertCircle
} from 'lucide-react'

interface DocumentFile {
  filename: string
  size: number
  modified: number
  source: 'upload' | 'scraper'
  course?: string
}

interface DocumentsListProps {
  refreshTrigger?: number  // Optional prop to trigger refresh from parent
}

export function DocumentsList({ refreshTrigger }: DocumentsListProps) {
  const [documents, setDocuments] = useState<{
    upload_files: DocumentFile[]
    scraped_files: DocumentFile[]
    total_files: number
  }>({
    upload_files: [],
    scraped_files: [],
    total_files: 0
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchDocuments()
  }, [refreshTrigger]) // Refetch when refreshTrigger changes

  const fetchDocuments = async () => {
    try {
      setLoading(true)
      setError(null)

      // Get uploaded documents from localStorage
      const storedDocuments = localStorage.getItem('uploaded_documents')
      const uploadedDocs = storedDocuments ? JSON.parse(storedDocuments) : []

      const response = await fetch('/api/documents/processed')
      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          // Merge API data with localStorage data
          const mergedData = {
            ...data,
            upload_files: [...uploadedDocs, ...data.upload_files],
            total_files: uploadedDocs.length + data.upload_files.length + data.scraped_files.length
          }
          setDocuments(mergedData)
        } else {
          // If API fails, show at least localStorage data
          setDocuments({
            upload_files: uploadedDocs,
            scraped_files: [],
            total_files: uploadedDocs.length
          })
        }
      } else {
        // If API fails, show at least localStorage data
        setDocuments({
          upload_files: uploadedDocs,
          scraped_files: [],
          total_files: uploadedDocs.length
        })
      }
    } catch (error) {
      console.error('Failed to fetch documents:', error)
      // On error, try to show localStorage data
      const storedDocuments = localStorage.getItem('uploaded_documents')
      const uploadedDocs = storedDocuments ? JSON.parse(storedDocuments) : []
      setDocuments({
        upload_files: uploadedDocs,
        scraped_files: [],
        total_files: uploadedDocs.length
      })
      setError(error instanceof Error ? error.message : 'Unknown error occurred')
    } finally {
      setLoading(false)
    }
  }

  const deleteDocument = async (filename: string) => {
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
      return
    }

    try {
      // First try to delete from localStorage
      const storedDocuments = localStorage.getItem('uploaded_documents')
      if (storedDocuments) {
        const uploadedDocs = JSON.parse(storedDocuments)
        const filteredDocs = uploadedDocs.filter((doc: DocumentFile) => doc.filename !== filename)
        localStorage.setItem('uploaded_documents', JSON.stringify(filteredDocs))
      }

      // Then try to delete from API (this may fail for demo docs, that's ok)
      try {
        const response = await fetch(`/api/documents/delete/${encodeURIComponent(filename)}`, {
          method: 'DELETE'
        })

        if (!response.ok) {
          const data = await response.json()
          console.log('API deletion failed (expected for uploaded docs):', data.detail)
        }
      } catch (apiError) {
        console.log('API deletion failed (expected for uploaded docs):', apiError)
      }

      // Refresh the list after deletion
      fetchDocuments()
    } catch (error) {
      console.error('Delete error:', error)
      alert(`Failed to delete document: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  const getFileIcon = (filename: string) => {
    const extension = filename.toLowerCase().split('.').pop()

    switch (extension) {
      case 'pdf':
        return <FileText className="w-5 h-5 text-red-500" />
      case 'docx':
      case 'doc':
        return <FileText className="w-5 h-5 text-blue-500" />
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
        return <Image className="w-5 h-5 text-green-500" />
      case 'mp3':
      case 'wav':
      case 'm4a':
        return <Music className="w-5 h-5 text-purple-500" />
      case 'mp4':
      case 'avi':
      case 'mov':
        return <Video className="w-5 h-5 text-orange-500" />
      default:
        return <File className="w-5 h-5 text-gray-500" />
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (timestamp: number) => {
    // Handle both seconds and milliseconds timestamps
    const date = new Date(timestamp * (timestamp > 1e10 ? 1 : 1000))
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const renderDocumentRow = (doc: DocumentFile) => (
    <div
      key={`${doc.source}-${doc.filename}`}
      className="flex items-center justify-between p-4 hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
    >
      <div className="flex items-center space-x-3 flex-1 min-w-0">
        {getFileIcon(doc.filename)}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 truncate">
            {doc.filename}
          </p>
          <div className="flex items-center space-x-4 text-xs text-gray-500 mt-1">
            <span className="flex items-center">
              <HardDrive className="w-3 h-3 mr-1" />
              {formatFileSize(doc.size)}
            </span>
            <span className="flex items-center">
              <Calendar className="w-3 h-3 mr-1" />
              {formatDate(doc.modified)}
            </span>
            {doc.source === 'scraper' && doc.course && (
              <span className="flex items-center">
                <FolderOpen className="w-3 h-3 mr-1" />
                {doc.course}
              </span>
            )}
          </div>
        </div>
      </div>
      <div className="flex items-center space-x-2 ml-4">
        <button
          onClick={() => deleteDocument(doc.filename)}
          className="p-1 text-gray-400 hover:text-red-500 transition-colors"
          title="Delete document"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </div>
  )

  if (loading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-8">
        <div className="flex items-center justify-center space-x-2">
          <RefreshCw className="w-5 h-5 animate-spin text-blue-500" />
          <span className="text-gray-600">Loading documents...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center space-x-2 text-red-600 mb-4">
          <AlertCircle className="w-5 h-5" />
          <h3 className="font-medium">Error Loading Documents</h3>
        </div>
        <p className="text-red-700 text-sm mb-4">{error}</p>
        <button
          onClick={fetchDocuments}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Retry</span>
        </button>
      </div>
    )
  }

  const hasDocuments = documents.upload_files.length > 0 || documents.scraped_files.length > 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Your Documents</h2>
          <p className="text-sm text-gray-600 mt-1">
            {documents.total_files} document{documents.total_files !== 1 ? 's' : ''} in your knowledge base
          </p>
        </div>
        <button
          onClick={fetchDocuments}
          className="flex items-center space-x-2 px-3 py-2 text-gray-600 hover:text-gray-900 transition-colors"
          title="Refresh list"
        >
          <RefreshCw className="w-4 h-4" />
          <span className="text-sm">Refresh</span>
        </button>
      </div>

      {!hasDocuments ? (
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <FolderOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No documents yet</h3>
          <p className="text-gray-600 mb-6">
            Upload your first document to start building your AI-powered knowledge base
          </p>
          <a
            href="/upload"
            className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          >
            <FolderOpen className="w-4 h-4" />
            <span>Upload Documents</span>
          </a>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Uploaded Files */}
          {documents.upload_files.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="font-semibold text-gray-900">
                  Uploaded Documents ({documents.upload_files.length})
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                  Files you've uploaded directly to the platform
                </p>
              </div>
              <div className="divide-y divide-gray-100">
                {documents.upload_files.map(renderDocumentRow)}
              </div>
            </div>
          )}

          {/* Scraped Files */}
          {documents.scraped_files.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="font-semibold text-gray-900">
                  Scraped Documents ({documents.scraped_files.length})
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                  Documents automatically collected from course platforms
                </p>
              </div>
              <div className="divide-y divide-gray-100">
                {documents.scraped_files.map(renderDocumentRow)}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}