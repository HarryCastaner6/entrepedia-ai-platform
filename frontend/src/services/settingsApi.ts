interface ProfileSettings {
  full_name?: string
  email?: string
  bio?: string
  timezone: string
  language: string
}

interface AIConfiguration {
  preferred_model: string
  response_style: string
  coaching_mode: string
  strategy_depth: string
  enable_follow_ups: boolean
  context_window: number
}

interface DocumentProcessingConfig {
  auto_generate_embeddings: boolean
  chunk_size: number
  overlap_size: number
  processing_quality: string
  auto_ocr: boolean
  supported_formats: string[]
}

interface IntegrationSettings {
  openai_api_key?: string
  gemini_api_key?: string
  google_calendar_connected: boolean
  notion_connected: boolean
  trello_connected: boolean
}

interface SecuritySettings {
  two_factor_enabled: boolean
  session_timeout: number
  data_retention_days: number
  allow_data_export: boolean
  share_analytics: boolean
}

interface NotificationSettings {
  email_notifications: boolean
  processing_complete: boolean
  ai_suggestions: boolean
  weekly_summary: boolean
  security_alerts: boolean
}

interface DatabaseStats {
  total_documents: number
  total_embeddings: number
  database_size: string
  last_backup: string
}

interface BackupSettings {
  auto_backup_enabled: boolean
  backup_frequency: string
  email_backup_notifications: boolean
}

interface AllSettings {
  profile: ProfileSettings
  ai_config: AIConfiguration
  documents: DocumentProcessingConfig
  integrations: IntegrationSettings
  security: SecuritySettings
  notifications: NotificationSettings
  database_stats: DatabaseStats
  backup: BackupSettings
}

class SettingsAPI {
  private baseUrl = 'http://localhost:8000/settings'

  private getToken(): string | null {
    return localStorage.getItem('auth_token')
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const token = this.getToken()
    const headers = {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    }

    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }

    return response.json()
  }

  // Profile Settings
  async getProfileSettings(): Promise<ProfileSettings> {
    return this.request<ProfileSettings>('/profile')
  }

  async updateProfileSettings(profile: ProfileSettings): Promise<{ success: boolean; message: string }> {
    return this.request('/profile', {
      method: 'POST',
      body: JSON.stringify(profile),
    })
  }

  // AI Configuration
  async getAIConfiguration(): Promise<AIConfiguration> {
    return this.request<AIConfiguration>('/ai-config')
  }

  async updateAIConfiguration(config: AIConfiguration): Promise<{ success: boolean; message: string }> {
    return this.request('/ai-config', {
      method: 'POST',
      body: JSON.stringify(config),
    })
  }

  // Document Processing
  async getDocumentProcessingConfig(): Promise<DocumentProcessingConfig> {
    return this.request<DocumentProcessingConfig>('/documents')
  }

  async updateDocumentProcessingConfig(config: DocumentProcessingConfig): Promise<{ success: boolean; message: string }> {
    return this.request('/documents', {
      method: 'POST',
      body: JSON.stringify(config),
    })
  }

  // Integration Settings
  async getIntegrationSettings(): Promise<IntegrationSettings> {
    return this.request<IntegrationSettings>('/integrations')
  }

  async updateIntegrationSettings(settings: IntegrationSettings): Promise<{ success: boolean; message: string }> {
    return this.request('/integrations', {
      method: 'POST',
      body: JSON.stringify(settings),
    })
  }

  // Security Settings
  async getSecuritySettings(): Promise<SecuritySettings> {
    return this.request<SecuritySettings>('/security')
  }

  async updateSecuritySettings(settings: SecuritySettings): Promise<{ success: boolean; message: string }> {
    return this.request('/security', {
      method: 'POST',
      body: JSON.stringify(settings),
    })
  }

  // Notification Settings
  async getNotificationSettings(): Promise<NotificationSettings> {
    return this.request<NotificationSettings>('/notifications')
  }

  async updateNotificationSettings(settings: NotificationSettings): Promise<{ success: boolean; message: string }> {
    return this.request('/notifications', {
      method: 'POST',
      body: JSON.stringify(settings),
    })
  }

  // Database Management
  async getDatabaseStats(): Promise<DatabaseStats> {
    return this.request<DatabaseStats>('/database/stats')
  }

  async resetDatabase(): Promise<{ success: boolean; message: string }> {
    return this.request('/database/reset', {
      method: 'POST',
    })
  }

  // Backup & Export
  async getBackupSettings(): Promise<BackupSettings> {
    return this.request<BackupSettings>('/backup')
  }

  async updateBackupSettings(settings: BackupSettings): Promise<{ success: boolean; message: string }> {
    return this.request('/backup', {
      method: 'POST',
      body: JSON.stringify(settings),
    })
  }

  async exportData(): Promise<{ success: boolean; message: string; download_url?: string }> {
    return this.request('/backup/export', {
      method: 'POST',
    })
  }

  // Get All Settings
  async getAllSettings(): Promise<AllSettings> {
    return this.request<AllSettings>('/all')
  }
}

export const settingsApi = new SettingsAPI()
export type {
  ProfileSettings,
  AIConfiguration,
  DocumentProcessingConfig,
  IntegrationSettings,
  SecuritySettings,
  NotificationSettings,
  DatabaseStats,
  BackupSettings,
  AllSettings
}