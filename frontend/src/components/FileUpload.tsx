import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import {
  Upload,
  File,
  FileText,
  Image,
  Music,
  Video,
  CheckCircle,
  XCircle,
  Loader2,
  AlertCircle
} from 'lucide-react'

interface UploadedFile {
  file: File
  status: 'uploading' | 'processing' | 'success' | 'error'
  result?: any
  error?: string
  id: string
}

interface FileUploadProps {
  onUploadSuccess?: () => void  // Callback for when upload completes successfully
}

export function FileUpload({ onUploadSuccess }: FileUploadProps) {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles: UploadedFile[] = acceptedFiles.map(file => ({
      file,
      status: 'uploading',
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9)
    }))

    setUploadedFiles(prev => [...prev, ...newFiles])

    // Process each file
    newFiles.forEach(uploadedFile => {
      uploadFile(uploadedFile)
    })
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'image/*': ['.jpg', '.jpeg', '.png', '.gif'],
      'audio/*': ['.mp3', '.wav', '.m4a'],
      'video/*': ['.mp4', '.avi', '.mov']
    },
    maxSize: 100 * 1024 * 1024 // 100MB
  })

  const uploadFile = async (uploadedFile: UploadedFile) => {
    try {
      // Update status to uploading
      setUploadedFiles(prev =>
        prev.map(f => f.id === uploadedFile.id ? { ...f, status: 'uploading' } : f)
      )

      const formData = new FormData()
      formData.append('file', uploadedFile.file)
      formData.append('create_embeddings', 'true')

      const response = await fetch('/api/documents/upload', {
        method: 'POST',
        body: formData
      })

      const result = await response.json()

      if (response.ok && result.success) {
        setUploadedFiles(prev =>
          prev.map(f =>
            f.id === uploadedFile.id
              ? { ...f, status: 'success', result }
              : f
          )
        )
        // Trigger parent component refresh if callback provided
        onUploadSuccess?.()
      } else {
        throw new Error(result.error || 'Upload failed')
      }
    } catch (error) {
      console.error('Upload error:', error)
      setUploadedFiles(prev =>
        prev.map(f =>
          f.id === uploadedFile.id
            ? { ...f, status: 'error', error: error instanceof Error ? error.message : 'Unknown error' }
            : f
        )
      )
    }
  }

  const getFileIcon = (fileName: string) => {
    const extension = fileName.toLowerCase().split('.').pop()

    switch (extension) {
      case 'pdf':
        return <FileText className="w-8 h-8 text-red-500" />
      case 'docx':
      case 'doc':
        return <FileText className="w-8 h-8 text-blue-500" />
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
        return <Image className="w-8 h-8 text-green-500" />
      case 'mp3':
      case 'wav':
      case 'm4a':
        return <Music className="w-8 h-8 text-purple-500" />
      case 'mp4':
      case 'avi':
      case 'mov':
        return <Video className="w-8 h-8 text-orange-500" />
      default:
        return <File className="w-8 h-8 text-gray-500" />
    }
  }

  const getStatusIcon = (status: UploadedFile['status']) => {
    switch (status) {
      case 'uploading':
      case 'processing':
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />
    }
  }

  const getStatusText = (status: UploadedFile['status']) => {
    switch (status) {
      case 'uploading':
        return 'Uploading...'
      case 'processing':
        return 'Processing...'
      case 'success':
        return 'Complete'
      case 'error':
        return 'Failed'
    }
  }

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-blue-400 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        {isDragActive ? (
          <p className="text-blue-600">Drop the files here...</p>
        ) : (
          <div>
            <p className="text-gray-900 font-medium mb-1">
              Drop files here, or click to select
            </p>
            <p className="text-gray-500 text-sm">
              Supports PDF, DOCX, images, audio, and video files (max 100MB)
            </p>
          </div>
        )}
      </div>

      {/* Supported Formats */}
      <div className="bg-blue-50 rounded-lg p-4">
        <div className="flex items-start space-x-2">
          <AlertCircle className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
          <div>
            <h3 className="font-medium text-blue-900 mb-1">Supported File Types</h3>
            <div className="text-sm text-blue-700 space-y-1">
              <p><strong>Documents:</strong> PDF, DOCX, DOC</p>
              <p><strong>Images:</strong> JPG, PNG, GIF (OCR will extract text)</p>
              <p><strong>Audio:</strong> MP3, WAV, M4A (transcription available with full setup)</p>
              <p><strong>Video:</strong> MP4, AVI, MOV (audio transcription available)</p>
            </div>
          </div>
        </div>
      </div>

      {/* Upload Progress */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-gray-900">Upload Progress</h3>
          <div className="space-y-2">
            {uploadedFiles.map((uploadedFile) => (
              <div
                key={uploadedFile.id}
                className="flex items-center space-x-3 p-3 bg-white border border-gray-200 rounded-lg"
              >
                {getFileIcon(uploadedFile.file.name)}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {uploadedFile.file.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {(uploadedFile.file.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(uploadedFile.status)}
                  <span className="text-sm text-gray-600">
                    {getStatusText(uploadedFile.status)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Processing Results */}
      {uploadedFiles.some(f => f.status === 'success') && (
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-gray-900">Processing Results</h3>
          <div className="space-y-4">
            {uploadedFiles
              .filter(f => f.status === 'success')
              .map((uploadedFile) => (
                <div
                  key={uploadedFile.id}
                  className="bg-white border border-gray-200 rounded-lg p-4"
                >
                  <div className="flex items-center space-x-3 mb-3">
                    {getFileIcon(uploadedFile.file.name)}
                    <div>
                      <h4 className="font-medium text-gray-900">{uploadedFile.file.name}</h4>
                      <p className="text-sm text-gray-500">
                        Processed successfully
                      </p>
                    </div>
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  </div>

                  {uploadedFile.result && (
                    <div className="space-y-2">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="font-medium text-gray-700">File Type:</span>
                          <span className="ml-2 text-gray-600">
                            {uploadedFile.result.file_type.toUpperCase()}
                          </span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Status:</span>
                          <span className="ml-2 text-green-600">Successfully processed</span>
                        </div>
                      </div>

                      {uploadedFile.result.processing_result?.text && (
                        <div>
                          <span className="font-medium text-gray-700 text-sm">Extracted Text Preview:</span>
                          <div className="mt-1 p-3 bg-gray-50 rounded border max-h-32 overflow-y-auto">
                            <p className="text-sm text-gray-600">
                              {uploadedFile.result.processing_result.text.substring(0, 500)}
                              {uploadedFile.result.processing_result.text.length > 500 && '...'}
                            </p>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Error Messages */}
      {uploadedFiles.some(f => f.status === 'error') && (
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-red-900">Errors</h3>
          <div className="space-y-2">
            {uploadedFiles
              .filter(f => f.status === 'error')
              .map((uploadedFile) => (
                <div
                  key={uploadedFile.id}
                  className="flex items-center space-x-3 p-3 bg-red-50 border border-red-200 rounded-lg"
                >
                  {getFileIcon(uploadedFile.file.name)}
                  <div className="flex-1">
                    <p className="text-sm font-medium text-red-900">
                      {uploadedFile.file.name}
                    </p>
                    <p className="text-xs text-red-700">
                      {uploadedFile.error || 'Unknown error occurred'}
                    </p>
                  </div>
                  <XCircle className="w-5 h-5 text-red-500" />
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  )
}