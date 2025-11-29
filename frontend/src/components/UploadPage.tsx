import { useState } from 'react'
import { FileUpload } from './FileUpload'
import { DocumentsList } from './DocumentsList'

export function UploadPage() {
  // State to trigger refresh of document list when uploads complete
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const handleUploadSuccess = () => {
    // Increment trigger to refresh document list
    setRefreshTrigger(prev => prev + 1)
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Upload Documents</h1>
          <p className="mt-2 text-gray-600">
            Upload files to build your AI-powered knowledge base. Supported formats include PDFs,
            Word documents, images, audio, and video files.
          </p>
        </div>

        {/* Upload Section */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Add New Documents</h2>
          <FileUpload onUploadSuccess={handleUploadSuccess} />
        </div>

        {/* Documents List Section */}
        <DocumentsList refreshTrigger={refreshTrigger} />
      </div>
    </div>
  )
}