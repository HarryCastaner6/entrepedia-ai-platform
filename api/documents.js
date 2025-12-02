// Node.js Vercel function for documents API

// Mock data for demo - in production this would connect to a database
const mockDocuments = {
  upload_files: [
    {
      filename: "sample-document.pdf",
      size: 1024000,
      modified: Date.now() / 1000,
      source: "upload"
    }
  ],
  scraped_files: [
    {
      filename: "course-material.pdf",
      size: 2048000,
      modified: Date.now() / 1000,
      source: "scraper",
      course: "AI Fundamentals"
    }
  ],
  total_files: 2
};

const mockStats = {
  success: true,
  total_files: 2,
  total_size_bytes: 3072000,
  total_size_mb: 3.07,
  file_types: {
    "pdf": 2
  }
};

module.exports = async (req, res) => {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  // Handle preflight
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  const { url, method } = req;
  console.log('Documents API:', method, url);

  // GET /api/documents - List processed documents
  if (method === 'GET' && (url === '/api/documents/processed' || url.endsWith('/processed'))) {
    res.status(200).json({
      success: true,
      ...mockDocuments
    });
    return;
  }

  // GET /api/documents/stats - Get document statistics
  if (method === 'GET' && (url === '/api/documents/stats' || url.endsWith('/stats'))) {
    res.status(200).json(mockStats);
    return;
  }

  // POST /api/documents/upload - Upload document
  if (method === 'POST' && (url === '/api/documents/upload' || url.endsWith('/upload'))) {
    try {
      console.log('Upload request received:', method, url);

      // In a real implementation, this would:
      // 1. Parse the uploaded file using formidable or similar
      // 2. Store it in cloud storage
      // 3. Process it for embeddings
      // 4. Save metadata to database

      // For demo purposes, simulate successful upload with expected response structure
      const filename = `uploaded-document-${Date.now()}.pdf`;
      const fileType = 'pdf';
      const sampleText = 'This is a sample document that has been successfully uploaded and processed. In a real implementation, this would contain the actual extracted text content from your document.';

      // Add to mock documents list
      const newDocument = {
        filename: filename,
        size: 1024000 + Math.random() * 2000000, // Random size between 1-3MB
        modified: Date.now() / 1000,
        source: "upload"
      };

      mockDocuments.upload_files.unshift(newDocument);
      mockDocuments.total_files = mockDocuments.upload_files.length + mockDocuments.scraped_files.length;

      // Update stats
      mockStats.total_files = mockDocuments.total_files;
      mockStats.total_size_bytes += newDocument.size;
      mockStats.total_size_mb = Math.round((mockStats.total_size_bytes / (1024 * 1024)) * 100) / 100;
      mockStats.file_types[fileType] = (mockStats.file_types[fileType] || 0) + 1;

      // Return response structure expected by frontend
      res.status(200).json({
        success: true,
        message: "File uploaded and processed successfully",
        filename: filename,
        file_type: fileType,
        size: newDocument.size,
        processed: true,
        processing_result: {
          text: sampleText,
          chunks_created: 5,
          embeddings_generated: true
        },
        metadata: {
          upload_time: new Date().toISOString(),
          processing_time: "2.3s"
        }
      });
      return;
    } catch (error) {
      console.error('Upload error:', error);
      res.status(500).json({
        success: false,
        detail: "Upload failed: " + error.message
      });
      return;
    }
  }

  // DELETE /api/documents/delete/{filename} - Delete document
  if (method === 'DELETE' && url.includes('/delete/')) {
    try {
      const filename = url.split('/delete/')[1];

      // In a real implementation, this would:
      // 1. Delete the file from storage
      // 2. Remove embeddings from vector database
      // 3. Update metadata in database

      res.status(200).json({
        success: true,
        message: `Document ${decodeURIComponent(filename)} deleted successfully`
      });
      return;
    } catch (error) {
      res.status(500).json({
        success: false,
        detail: "Delete failed: " + error.message
      });
      return;
    }
  }

  // Default response for unsupported endpoints
  res.status(404).json({
    success: false,
    detail: "Documents API endpoint not found",
    available_endpoints: [
      "GET /processed - List all processed documents",
      "GET /stats - Get document statistics",
      "POST /upload - Upload a new document",
      "DELETE /delete/{filename} - Delete a document"
    ]
  });
};