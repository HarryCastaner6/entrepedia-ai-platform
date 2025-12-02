// Node.js Vercel function for settings API

// Mock settings data for demo
const mockSettings = {
  profile: {
    full_name: "Demo User",
    email: "demo@entrepedia.ai",
    bio: "Learning enthusiast exploring AI and entrepreneurship",
    timezone: "UTC",
    language: "en"
  },
  ai_config: {
    preferred_model: "gemini-pro",
    response_style: "balanced",
    coaching_mode: "adaptive",
    strategy_depth: "detailed",
    enable_follow_ups: true,
    context_window: 4000
  },
  documents: {
    auto_generate_embeddings: true,
    chunk_size: 500,
    overlap_size: 50,
    processing_quality: "high",
    auto_ocr: true,
    supported_formats: ["pdf", "docx", "txt", "md", "png", "jpg", "mp3", "wav"]
  },
  integrations: {
    openai_api_key: "",
    gemini_api_key: "",
    google_calendar_connected: false,
    notion_connected: false,
    trello_connected: false
  },
  security: {
    two_factor_enabled: false,
    session_timeout: 30,
    data_retention_days: 365,
    allow_data_export: true,
    share_analytics: false
  },
  notifications: {
    email_notifications: true,
    processing_complete: true,
    ai_suggestions: true,
    weekly_summary: true,
    security_alerts: true
  },
  database_stats: {
    total_documents: 12,
    total_embeddings: 1450,
    database_size: "23.5 MB",
    last_backup: "2024-11-30"
  },
  backup: {
    auto_backup_enabled: true,
    backup_frequency: "daily",
    email_backup_notifications: false
  }
};

module.exports = async (req, res) => {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  // Handle preflight
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  const { url, method } = req;
  console.log('Settings API:', method, url);

  // GET /api/settings/all - Get all settings
  if (method === 'GET' && (url === '/api/settings/all' || url.endsWith('/all'))) {
    res.status(200).json(mockSettings);
    return;
  }

  // GET /api/settings/profile - Get profile settings
  if (method === 'GET' && (url === '/api/settings/profile' || url.endsWith('/profile'))) {
    res.status(200).json(mockSettings.profile);
    return;
  }

  // POST /api/settings/profile - Update profile settings
  if (method === 'POST' && (url === '/api/settings/profile' || url.endsWith('/profile'))) {
    try {
      let body;
      if (req.body) {
        body = req.body;
      } else {
        const rawBody = await getRawBody(req);
        body = JSON.parse(rawBody);
      }

      // Update mock data (in real app, save to database)
      Object.assign(mockSettings.profile, body);

      res.status(200).json({
        success: true,
        message: "Profile settings updated successfully"
      });
      return;
    } catch (error) {
      res.status(400).json({
        success: false,
        detail: "Invalid profile data: " + error.message
      });
      return;
    }
  }

  // GET /api/settings/ai-config - Get AI configuration
  if (method === 'GET' && (url === '/api/settings/ai-config' || url.endsWith('/ai-config'))) {
    res.status(200).json(mockSettings.ai_config);
    return;
  }

  // POST /api/settings/ai-config - Update AI configuration
  if (method === 'POST' && (url === '/api/settings/ai-config' || url.endsWith('/ai-config'))) {
    try {
      let body;
      if (req.body) {
        body = req.body;
      } else {
        const rawBody = await getRawBody(req);
        body = JSON.parse(rawBody);
      }

      Object.assign(mockSettings.ai_config, body);

      res.status(200).json({
        success: true,
        message: "AI configuration updated successfully"
      });
      return;
    } catch (error) {
      res.status(400).json({
        success: false,
        detail: "Invalid AI configuration: " + error.message
      });
      return;
    }
  }

  // GET /api/settings/documents - Get document processing config
  if (method === 'GET' && (url === '/api/settings/documents' || url.endsWith('/documents'))) {
    res.status(200).json(mockSettings.documents);
    return;
  }

  // POST /api/settings/documents - Update document processing config
  if (method === 'POST' && (url === '/api/settings/documents' || url.endsWith('/documents'))) {
    try {
      let body;
      if (req.body) {
        body = req.body;
      } else {
        const rawBody = await getRawBody(req);
        body = JSON.parse(rawBody);
      }

      Object.assign(mockSettings.documents, body);

      res.status(200).json({
        success: true,
        message: "Document settings updated successfully"
      });
      return;
    } catch (error) {
      res.status(400).json({
        success: false,
        detail: "Invalid document configuration: " + error.message
      });
      return;
    }
  }

  // GET /api/settings/integrations - Get integration settings
  if (method === 'GET' && (url === '/api/settings/integrations' || url.endsWith('/integrations'))) {
    res.status(200).json(mockSettings.integrations);
    return;
  }

  // POST /api/settings/integrations - Update integration settings
  if (method === 'POST' && (url === '/api/settings/integrations' || url.endsWith('/integrations'))) {
    try {
      let body;
      if (req.body) {
        body = req.body;
      } else {
        const rawBody = await getRawBody(req);
        body = JSON.parse(rawBody);
      }

      Object.assign(mockSettings.integrations, body);

      res.status(200).json({
        success: true,
        message: "Integration settings updated successfully"
      });
      return;
    } catch (error) {
      res.status(400).json({
        success: false,
        detail: "Invalid integration settings: " + error.message
      });
      return;
    }
  }

  // GET /api/settings/security - Get security settings
  if (method === 'GET' && (url === '/api/settings/security' || url.endsWith('/security'))) {
    res.status(200).json(mockSettings.security);
    return;
  }

  // POST /api/settings/security - Update security settings
  if (method === 'POST' && (url === '/api/settings/security' || url.endsWith('/security'))) {
    try {
      let body;
      if (req.body) {
        body = req.body;
      } else {
        const rawBody = await getRawBody(req);
        body = JSON.parse(rawBody);
      }

      Object.assign(mockSettings.security, body);

      res.status(200).json({
        success: true,
        message: "Security settings updated successfully"
      });
      return;
    } catch (error) {
      res.status(400).json({
        success: false,
        detail: "Invalid security settings: " + error.message
      });
      return;
    }
  }

  // GET /api/settings/notifications - Get notification settings
  if (method === 'GET' && (url === '/api/settings/notifications' || url.endsWith('/notifications'))) {
    res.status(200).json(mockSettings.notifications);
    return;
  }

  // POST /api/settings/notifications - Update notification settings
  if (method === 'POST' && (url === '/api/settings/notifications' || url.endsWith('/notifications'))) {
    try {
      let body;
      if (req.body) {
        body = req.body;
      } else {
        const rawBody = await getRawBody(req);
        body = JSON.parse(rawBody);
      }

      Object.assign(mockSettings.notifications, body);

      res.status(200).json({
        success: true,
        message: "Notification settings updated successfully"
      });
      return;
    } catch (error) {
      res.status(400).json({
        success: false,
        detail: "Invalid notification settings: " + error.message
      });
      return;
    }
  }

  // GET /api/settings/database/stats - Get database stats
  if (method === 'GET' && (url.includes('/database/stats') || url.endsWith('/stats'))) {
    res.status(200).json(mockSettings.database_stats);
    return;
  }

  // POST /api/settings/database/reset - Reset database
  if (method === 'POST' && (url.includes('/database/reset') || url.endsWith('/reset'))) {
    // In real app, this would reset the database
    mockSettings.database_stats = {
      total_documents: 0,
      total_embeddings: 0,
      database_size: "0 MB",
      last_backup: "Never"
    };

    res.status(200).json({
      success: true,
      message: "Database reset successfully"
    });
    return;
  }

  // GET /api/settings/backup - Get backup settings
  if (method === 'GET' && (url === '/api/settings/backup' || url.endsWith('/backup'))) {
    res.status(200).json(mockSettings.backup);
    return;
  }

  // POST /api/settings/backup - Update backup settings
  if (method === 'POST' && (url === '/api/settings/backup' || url.endsWith('/backup'))) {
    try {
      let body;
      if (req.body) {
        body = req.body;
      } else {
        const rawBody = await getRawBody(req);
        body = JSON.parse(rawBody);
      }

      Object.assign(mockSettings.backup, body);

      res.status(200).json({
        success: true,
        message: "Backup settings updated successfully"
      });
      return;
    } catch (error) {
      res.status(400).json({
        success: false,
        detail: "Invalid backup settings: " + error.message
      });
      return;
    }
  }

  // POST /api/settings/backup/export - Export data
  if (method === 'POST' && (url.includes('/backup/export') || url.endsWith('/export'))) {
    res.status(200).json({
      success: true,
      message: "Data export completed",
      download_url: "/api/downloads/export-" + Date.now() + ".zip"
    });
    return;
  }

  // Default response for unsupported endpoints
  res.status(404).json({
    success: false,
    detail: "Settings API endpoint not found",
    available_endpoints: [
      "GET /all - Get all settings",
      "GET /profile - Get profile settings",
      "POST /profile - Update profile settings",
      "GET /ai-config - Get AI configuration",
      "POST /ai-config - Update AI configuration",
      "GET /documents - Get document processing config",
      "POST /documents - Update document processing config",
      "GET /integrations - Get integration settings",
      "POST /integrations - Update integration settings",
      "GET /security - Get security settings",
      "POST /security - Update security settings",
      "GET /notifications - Get notification settings",
      "POST /notifications - Update notification settings",
      "GET /database/stats - Get database statistics",
      "POST /database/reset - Reset database",
      "GET /backup - Get backup settings",
      "POST /backup - Update backup settings",
      "POST /backup/export - Export all data"
    ]
  });
};

// Helper function to parse request body
function getRawBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => {
      body += chunk.toString();
    });
    req.on('end', () => {
      resolve(body);
    });
    req.on('error', reject);
  });
}