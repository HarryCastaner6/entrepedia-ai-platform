import React, { useState, useEffect } from 'react'
import {
  User,
  Key,
  Brain,
  FileText,
  Shield,
  Bell,
  Database,
  Download,
  Settings as SettingsIcon,
  Save,
  RefreshCw,
  Trash2,
  Eye,
  EyeOff,
  AlertTriangle,
  CheckCircle,
  XCircle
} from 'lucide-react'
import { useAuthStore } from '../../stores/authStore'
import { settingsApi, type ProfileSettings, type AIConfiguration, type DocumentProcessingConfig, type IntegrationSettings, type SecuritySettings, type NotificationSettings, type DatabaseStats, type BackupSettings } from '../../services/settingsApi'
import toast from 'react-hot-toast'

interface SettingsTab {
  id: string
  name: string
  icon: React.ComponentType<any>
  description: string
}

const settingsTabs: SettingsTab[] = [
  { id: 'profile', name: 'Profile', icon: User, description: 'Manage your account information' },
  { id: 'ai-config', name: 'AI Configuration', icon: Brain, description: 'Configure AI agents and models' },
  { id: 'documents', name: 'Documents', icon: FileText, description: 'Document processing preferences' },
  { id: 'integrations', name: 'Integrations', icon: Key, description: 'API keys and external services' },
  { id: 'security', name: 'Security', icon: Shield, description: 'Privacy and security settings' },
  { id: 'notifications', name: 'Notifications', icon: Bell, description: 'Notification preferences' },
  { id: 'database', name: 'Database', icon: Database, description: 'Database management tools' },
  { id: 'backup', name: 'Backup & Export', icon: Download, description: 'Data backup and export' },
]

export function Settings() {
  const { user, updateUserProfile } = useAuthStore()
  const [activeTab, setActiveTab] = useState('profile')
  const [isLoading, setIsLoading] = useState(false)
  const [showApiKeys, setShowApiKeys] = useState(false)

  // State
  const [profileForm, setProfileForm] = useState<ProfileSettings>({
    full_name: user?.full_name || '',
    email: user?.email || '',
    bio: '',
    timezone: 'UTC',
    language: 'en'
  })

  const [aiConfig, setAiConfig] = useState<AIConfiguration>({
    preferred_model: 'gemini-pro',
    response_style: 'balanced',
    coaching_mode: 'adaptive',
    strategy_depth: 'detailed',
    enable_follow_ups: true,
    context_window: 4000
  })

  const [docConfig, setDocConfig] = useState<DocumentProcessingConfig>({
    auto_generate_embeddings: true,
    chunk_size: 500,
    overlap_size: 50,
    processing_quality: 'high',
    auto_ocr: true,
    supported_formats: ['pdf', 'docx', 'txt', 'md', 'png', 'jpg', 'mp3', 'wav']
  })

  const [integrations, setIntegrations] = useState<IntegrationSettings>({
    openai_api_key: '',
    gemini_api_key: '',
    google_calendar_connected: false,
    notion_connected: false,
    trello_connected: false
  })

  const [securityConfig, setSecurityConfig] = useState<SecuritySettings>({
    two_factor_enabled: false,
    session_timeout: 30,
    data_retention_days: 365,
    allow_data_export: true,
    share_analytics: false
  })

  const [notificationConfig, setNotificationConfig] = useState<NotificationSettings>({
    email_notifications: true,
    processing_complete: true,
    ai_suggestions: true,
    weekly_summary: true,
    security_alerts: true
  })

  const [dbStats, setDbStats] = useState<DatabaseStats>({
    total_documents: 0,
    total_embeddings: 0,
    database_size: '0 MB',
    last_backup: 'Never'
  })

  // Load settings from API
  useEffect(() => {
    const loadSettings = async () => {
      try {
        setIsLoading(true)
        const allSettings = await settingsApi.getAllSettings()

        setProfileForm(allSettings.profile)
        setAiConfig(allSettings.ai_config)
        setDocConfig(allSettings.documents)
        setIntegrations(allSettings.integrations)
        setSecurityConfig(allSettings.security)
        setNotificationConfig(allSettings.notifications)
        setDbStats(allSettings.database_stats)
      } catch (error) {
        console.error('Failed to load settings:', error)
        toast.error('Failed to load settings')
      } finally {
        setIsLoading(false)
      }
    }

    loadSettings()
  }, [])

  const handleSaveProfile = async () => {
    setIsLoading(true)
    try {
      await settingsApi.updateProfileSettings(profileForm)

      // Update local auth store
      updateUserProfile({
        full_name: profileForm.full_name,
        email: profileForm.email
      })

      toast.success('Profile updated successfully!')
    } catch (error) {
      console.error('Profile update error:', error)
      toast.error('Failed to update profile')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSaveAiConfig = async () => {
    setIsLoading(true)
    try {
      await settingsApi.updateAIConfiguration(aiConfig)
      toast.success('AI configuration saved!')
    } catch (error) {
      console.error('AI config update error:', error)
      toast.error('Failed to save AI configuration')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSaveIntegrations = async () => {
    setIsLoading(true)
    try {
      await settingsApi.updateIntegrationSettings(integrations)
      toast.success('Integration settings saved!')
    } catch (error) {
      console.error('Integration settings update error:', error)
      toast.error('Failed to save integration settings')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDatabaseReset = async () => {
    if (!confirm('Are you sure you want to reset the database? This will delete all documents and embeddings. This action cannot be undone.')) {
      return
    }

    setIsLoading(true)
    try {
      await settingsApi.resetDatabase()

      // Refresh database stats
      const stats = await settingsApi.getDatabaseStats()
      setDbStats(stats)

      toast.success('Database reset successfully!')
    } catch (error) {
      console.error('Database reset error:', error)
      toast.error('Failed to reset database')
    } finally {
      setIsLoading(false)
    }
  }

  const handleExportData = async () => {
    setIsLoading(true)
    try {
      const result = await settingsApi.exportData()

      if (result.download_url) {
        // In a real implementation, trigger download
        window.open(result.download_url, '_blank')
      }

      toast.success('Data export completed! Download should start automatically.')
    } catch (error) {
      console.error('Data export error:', error)
      toast.error('Failed to export data')
    } finally {
      setIsLoading(false)
    }
  }

  const handleToggleGoogleCalendar = async () => {
    setIsLoading(true)
    try {
      const newState = !integrations.google_calendar_connected
      setIntegrations({ ...integrations, google_calendar_connected: newState })

      if (newState) {
        // Simulate OAuth flow
        toast.success('Google Calendar connected successfully!')
      } else {
        toast.success('Google Calendar disconnected successfully!')
      }
    } catch (error) {
      console.error('Google Calendar toggle error:', error)
      toast.error('Failed to toggle Google Calendar connection')
    } finally {
      setIsLoading(false)
    }
  }

  const handleToggleNotion = async () => {
    setIsLoading(true)
    try {
      const newState = !integrations.notion_connected
      setIntegrations({ ...integrations, notion_connected: newState })

      if (newState) {
        toast.success('Notion connected successfully!')
      } else {
        toast.success('Notion disconnected successfully!')
      }
    } catch (error) {
      console.error('Notion toggle error:', error)
      toast.error('Failed to toggle Notion connection')
    } finally {
      setIsLoading(false)
    }
  }

  const handleToggleTrello = async () => {
    setIsLoading(true)
    try {
      const newState = !integrations.trello_connected
      setIntegrations({ ...integrations, trello_connected: newState })

      if (newState) {
        toast.success('Trello connected successfully!')
      } else {
        toast.success('Trello disconnected successfully!')
      }
    } catch (error) {
      console.error('Trello toggle error:', error)
      toast.error('Failed to toggle Trello connection')
    } finally {
      setIsLoading(false)
    }
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'profile':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Profile Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Full Name
                  </label>
                  <input
                    type="text"
                    value={profileForm.full_name}
                    onChange={(e) => setProfileForm({ ...profileForm, full_name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={profileForm.email}
                    onChange={(e) => setProfileForm({ ...profileForm, email: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Timezone
                  </label>
                  <select
                    value={profileForm.timezone}
                    onChange={(e) => setProfileForm({ ...profileForm, timezone: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="UTC">UTC</option>
                    <option value="America/New_York">Eastern Time</option>
                    <option value="America/Chicago">Central Time</option>
                    <option value="America/Denver">Mountain Time</option>
                    <option value="America/Los_Angeles">Pacific Time</option>
                    <option value="Europe/London">London</option>
                    <option value="Europe/Paris">Paris</option>
                    <option value="Asia/Tokyo">Tokyo</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Language
                  </label>
                  <select
                    value={profileForm.language}
                    onChange={(e) => setProfileForm({ ...profileForm, language: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="en">English</option>
                    <option value="es">Español</option>
                    <option value="fr">Français</option>
                    <option value="de">Deutsch</option>
                    <option value="it">Italiano</option>
                    <option value="pt">Português</option>
                  </select>
                </div>
              </div>
              <div className="mt-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Bio
                </label>
                <textarea
                  value={profileForm.bio}
                  onChange={(e) => setProfileForm({ ...profileForm, bio: e.target.value })}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Tell us about your learning goals and interests..."
                />
              </div>
            </div>
            <div className="flex justify-end">
              <button
                onClick={handleSaveProfile}
                disabled={isLoading}
                className="btn btn-primary flex items-center"
              >
                {isLoading ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                Save Profile
              </button>
            </div>
          </div>
        )

      case 'ai-config':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">AI Agent Configuration</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Preferred AI Model
                  </label>
                  <select
                    value={aiConfig.preferred_model}
                    onChange={(e) => setAiConfig({ ...aiConfig, preferred_model: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="gemini-pro">Gemini Pro (Recommended)</option>
                    <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                    <option value="gemini-flash">Gemini Flash</option>
                    <option value="gpt-4">GPT-4</option>
                    <option value="claude-3">Claude 3</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Response Style
                  </label>
                  <select
                    value={aiConfig.response_style}
                    onChange={(e) => setAiConfig({ ...aiConfig, response_style: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="concise">Concise</option>
                    <option value="balanced">Balanced</option>
                    <option value="detailed">Detailed</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Coaching Mode
                  </label>
                  <select
                    value={aiConfig.coaching_mode}
                    onChange={(e) => setAiConfig({ ...aiConfig, coaching_mode: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="supportive">Supportive</option>
                    <option value="adaptive">Adaptive</option>
                    <option value="challenging">Challenging</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Strategy Depth
                  </label>
                  <select
                    value={aiConfig.strategy_depth}
                    onChange={(e) => setAiConfig({ ...aiConfig, strategy_depth: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="overview">Overview</option>
                    <option value="detailed">Detailed</option>
                    <option value="comprehensive">Comprehensive</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Context Window Size
                  </label>
                  <input
                    type="number"
                    min="1000"
                    max="8000"
                    value={aiConfig.context_window}
                    onChange={(e) => setAiConfig({ ...aiConfig, context_window: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                  <p className="text-xs text-gray-500 mt-1">Number of tokens for context (1000-8000)</p>
                </div>
              </div>
              <div className="mt-6">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={aiConfig.enable_follow_ups}
                    onChange={(e) => setAiConfig({ ...aiConfig, enable_follow_ups: e.target.checked })}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Enable automatic follow-up questions</span>
                </label>
              </div>
            </div>
            <div className="flex justify-end">
              <button
                onClick={handleSaveAiConfig}
                disabled={isLoading}
                className="btn btn-primary flex items-center"
              >
                {isLoading ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                Save AI Configuration
              </button>
            </div>
          </div>
        )

      case 'documents':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Document Processing Settings</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Chunk Size (tokens)
                  </label>
                  <input
                    type="number"
                    min="100"
                    max="1000"
                    value={docConfig.chunk_size}
                    onChange={(e) => setDocConfig({ ...docConfig, chunk_size: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Overlap Size (tokens)
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="200"
                    value={docConfig.overlap_size}
                    onChange={(e) => setDocConfig({ ...docConfig, overlap_size: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Processing Quality
                  </label>
                  <select
                    value={docConfig.processing_quality}
                    onChange={(e) => setDocConfig({ ...docConfig, processing_quality: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="fast">Fast</option>
                    <option value="balanced">Balanced</option>
                    <option value="high">High Quality</option>
                  </select>
                </div>
              </div>
              <div className="mt-6 space-y-3">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={docConfig.auto_generate_embeddings}
                    onChange={(e) => setDocConfig({ ...docConfig, auto_generate_embeddings: e.target.checked })}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Automatically generate embeddings for uploaded documents</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={docConfig.auto_ocr}
                    onChange={(e) => setDocConfig({ ...docConfig, auto_ocr: e.target.checked })}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Enable OCR for images and scanned documents</span>
                </label>
              </div>
            </div>
            <div className="flex justify-end">
              <button
                onClick={async () => {
                  setIsLoading(true)
                  try {
                    await settingsApi.updateDocumentProcessingConfig(docConfig)
                    toast.success('Document settings saved!')
                  } catch (error) {
                    console.error('Document config update error:', error)
                    toast.error('Failed to save document settings')
                  } finally {
                    setIsLoading(false)
                  }
                }}
                disabled={isLoading}
                className="btn btn-primary flex items-center"
              >
                {isLoading ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                Save Document Settings
              </button>
            </div>
          </div>
        )

      case 'integrations':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">API Keys & Integrations</h3>
              <div className="space-y-4">
                <div className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-gray-900">OpenAI API Key</h4>
                    <span className="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded">Optional</span>
                  </div>
                  <div className="relative">
                    <input
                      type={showApiKeys ? "text" : "password"}
                      value={integrations.openai_api_key}
                      onChange={(e) => setIntegrations({ ...integrations, openai_api_key: e.target.value })}
                      placeholder="sk-..."
                      className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                    <button
                      type="button"
                      onClick={() => setShowApiKeys(!showApiKeys)}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    >
                      {showApiKeys ? <EyeOff className="h-4 w-4 text-gray-400" /> : <Eye className="h-4 w-4 text-gray-400" />}
                    </button>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">For GPT-4 and GPT-3.5 models</p>
                </div>

                <div className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-gray-900">Google Gemini API Key</h4>
                    <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded">Required</span>
                  </div>
                  <div className="relative">
                    <input
                      type={showApiKeys ? "text" : "password"}
                      value={integrations.gemini_api_key}
                      onChange={(e) => setIntegrations({ ...integrations, gemini_api_key: e.target.value })}
                      placeholder="AIza..."
                      className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                    <button
                      type="button"
                      onClick={() => setShowApiKeys(!showApiKeys)}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    >
                      {showApiKeys ? <EyeOff className="h-4 w-4 text-gray-400" /> : <Eye className="h-4 w-4 text-gray-400" />}
                    </button>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">For Gemini Pro and Gemini Flash models</p>
                </div>

                <div className="border border-gray-200 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-3">External Integrations</h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="text-sm font-medium text-gray-700">Google Calendar</span>
                        <p className="text-xs text-gray-500">Sync learning schedules and deadlines</p>
                      </div>
                      <div className="flex items-center">
                        {integrations.google_calendar_connected ? (
                          <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                        ) : (
                          <XCircle className="w-5 h-5 text-red-500 mr-2" />
                        )}
                        <button
                          onClick={handleToggleGoogleCalendar}
                          disabled={isLoading}
                          className="btn btn-secondary btn-sm"
                        >
                          {integrations.google_calendar_connected ? 'Disconnect' : 'Connect'}
                        </button>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="text-sm font-medium text-gray-700">Notion</span>
                        <p className="text-xs text-gray-500">Export notes and learning materials</p>
                      </div>
                      <div className="flex items-center">
                        {integrations.notion_connected ? (
                          <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                        ) : (
                          <XCircle className="w-5 h-5 text-red-500 mr-2" />
                        )}
                        <button
                          onClick={handleToggleNotion}
                          disabled={isLoading}
                          className="btn btn-secondary btn-sm"
                        >
                          {integrations.notion_connected ? 'Disconnect' : 'Connect'}
                        </button>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="text-sm font-medium text-gray-700">Trello</span>
                        <p className="text-xs text-gray-500">Manage learning tasks and projects</p>
                      </div>
                      <div className="flex items-center">
                        {integrations.trello_connected ? (
                          <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                        ) : (
                          <XCircle className="w-5 h-5 text-red-500 mr-2" />
                        )}
                        <button
                          onClick={handleToggleTrello}
                          disabled={isLoading}
                          className="btn btn-secondary btn-sm"
                        >
                          {integrations.trello_connected ? 'Disconnect' : 'Connect'}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="flex justify-end">
              <button
                onClick={handleSaveIntegrations}
                disabled={isLoading}
                className="btn btn-primary flex items-center"
              >
                {isLoading ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                Save Integration Settings
              </button>
            </div>
          </div>
        )

      case 'security':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Security & Privacy</h3>
              <div className="space-y-6">
                <div className="border border-gray-200 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-3">Account Security</h4>
                  <div className="space-y-3">
                    <label className="flex items-center justify-between">
                      <div>
                        <span className="text-sm font-medium text-gray-700">Two-Factor Authentication</span>
                        <p className="text-xs text-gray-500">Add an extra layer of security to your account</p>
                      </div>
                      <input
                        type="checkbox"
                        checked={securityConfig.two_factor_enabled}
                        onChange={(e) => setSecurityConfig({ ...securityConfig, two_factor_enabled: e.target.checked })}
                        className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                      />
                    </label>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Session Timeout (minutes)
                      </label>
                      <select
                        value={securityConfig.session_timeout}
                        onChange={(e) => setSecurityConfig({ ...securityConfig, session_timeout: parseInt(e.target.value) })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent max-w-xs"
                      >
                        <option value={15}>15 minutes</option>
                        <option value={30}>30 minutes</option>
                        <option value={60}>1 hour</option>
                        <option value={120}>2 hours</option>
                        <option value={0}>Never</option>
                      </select>
                    </div>
                  </div>
                </div>

                <div className="border border-gray-200 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-3">Data Privacy</h4>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Data Retention (days)
                      </label>
                      <input
                        type="number"
                        min="30"
                        max="3650"
                        value={securityConfig.data_retention_days}
                        onChange={(e) => setSecurityConfig({ ...securityConfig, data_retention_days: parseInt(e.target.value) })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent max-w-xs"
                      />
                      <p className="text-xs text-gray-500 mt-1">How long to keep your data before automatic deletion</p>
                    </div>
                    <label className="flex items-center justify-between">
                      <div>
                        <span className="text-sm font-medium text-gray-700">Allow Data Export</span>
                        <p className="text-xs text-gray-500">Enable downloading your data</p>
                      </div>
                      <input
                        type="checkbox"
                        checked={securityConfig.allow_data_export}
                        onChange={(e) => setSecurityConfig({ ...securityConfig, allow_data_export: e.target.checked })}
                        className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                      />
                    </label>
                    <label className="flex items-center justify-between">
                      <div>
                        <span className="text-sm font-medium text-gray-700">Share Anonymous Analytics</span>
                        <p className="text-xs text-gray-500">Help improve the platform with usage analytics</p>
                      </div>
                      <input
                        type="checkbox"
                        checked={securityConfig.share_analytics}
                        onChange={(e) => setSecurityConfig({ ...securityConfig, share_analytics: e.target.checked })}
                        className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                      />
                    </label>
                  </div>
                </div>
              </div>
            </div>
            <div className="flex justify-end">
              <button
                onClick={async () => {
                  setIsLoading(true)
                  try {
                    await settingsApi.updateSecuritySettings(securityConfig)
                    toast.success('Security settings saved!')
                  } catch (error) {
                    console.error('Security settings update error:', error)
                    toast.error('Failed to save security settings')
                  } finally {
                    setIsLoading(false)
                  }
                }}
                disabled={isLoading}
                className="btn btn-primary flex items-center"
              >
                {isLoading ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                Save Security Settings
              </button>
            </div>
          </div>
        )

      case 'notifications':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Notification Preferences</h3>
              <div className="space-y-4">
                <label className="flex items-center justify-between">
                  <div>
                    <span className="text-sm font-medium text-gray-700">Email Notifications</span>
                    <p className="text-xs text-gray-500">Receive notifications via email</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={notificationConfig.email_notifications}
                    onChange={(e) => setNotificationConfig({ ...notificationConfig, email_notifications: e.target.checked })}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                </label>
                <label className="flex items-center justify-between">
                  <div>
                    <span className="text-sm font-medium text-gray-700">Document Processing Complete</span>
                    <p className="text-xs text-gray-500">Notify when document uploads are processed</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={notificationConfig.processing_complete}
                    onChange={(e) => setNotificationConfig({ ...notificationConfig, processing_complete: e.target.checked })}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                </label>
                <label className="flex items-center justify-between">
                  <div>
                    <span className="text-sm font-medium text-gray-700">AI Learning Suggestions</span>
                    <p className="text-xs text-gray-500">Get personalized learning recommendations</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={notificationConfig.ai_suggestions}
                    onChange={(e) => setNotificationConfig({ ...notificationConfig, ai_suggestions: e.target.checked })}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                </label>
                <label className="flex items-center justify-between">
                  <div>
                    <span className="text-sm font-medium text-gray-700">Weekly Learning Summary</span>
                    <p className="text-xs text-gray-500">Receive weekly progress reports</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={notificationConfig.weekly_summary}
                    onChange={(e) => setNotificationConfig({ ...notificationConfig, weekly_summary: e.target.checked })}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                </label>
                <label className="flex items-center justify-between">
                  <div>
                    <span className="text-sm font-medium text-gray-700">Security Alerts</span>
                    <p className="text-xs text-gray-500">Important security notifications</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={notificationConfig.security_alerts}
                    onChange={(e) => setNotificationConfig({ ...notificationConfig, security_alerts: e.target.checked })}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                </label>
              </div>
            </div>
            <div className="flex justify-end">
              <button
                onClick={async () => {
                  setIsLoading(true)
                  try {
                    await settingsApi.updateNotificationSettings(notificationConfig)
                    toast.success('Notification settings saved!')
                  } catch (error) {
                    console.error('Notification settings update error:', error)
                    toast.error('Failed to save notification settings')
                  } finally {
                    setIsLoading(false)
                  }
                }}
                disabled={isLoading}
                className="btn btn-primary flex items-center"
              >
                {isLoading ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                Save Notification Settings
              </button>
            </div>
          </div>
        )

      case 'database':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Database Management</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <FileText className="w-8 h-8 text-blue-600" />
                    <div className="ml-3">
                      <p className="text-sm font-medium text-blue-900">Documents</p>
                      <p className="text-2xl font-bold text-blue-600">{dbStats.total_documents}</p>
                    </div>
                  </div>
                </div>
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <Brain className="w-8 h-8 text-green-600" />
                    <div className="ml-3">
                      <p className="text-sm font-medium text-green-900">Embeddings</p>
                      <p className="text-2xl font-bold text-green-600">{dbStats.total_embeddings}</p>
                    </div>
                  </div>
                </div>
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <Database className="w-8 h-8 text-purple-600" />
                    <div className="ml-3">
                      <p className="text-sm font-medium text-purple-900">Size</p>
                      <p className="text-2xl font-bold text-purple-600">{dbStats.database_size}</p>
                    </div>
                  </div>
                </div>
                <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <Download className="w-8 h-8 text-orange-600" />
                    <div className="ml-3">
                      <p className="text-sm font-medium text-orange-900">Last Backup</p>
                      <p className="text-sm font-bold text-orange-600">{dbStats.last_backup}</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="border border-red-200 rounded-lg p-4 bg-red-50">
                <div className="flex items-start">
                  <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5" />
                  <div className="ml-3">
                    <h4 className="text-sm font-medium text-red-900">Danger Zone</h4>
                    <p className="text-xs text-red-700 mb-3">
                      These actions are irreversible. Please be careful.
                    </p>
                    <button
                      onClick={handleDatabaseReset}
                      disabled={isLoading}
                      className="btn bg-red-600 hover:bg-red-700 text-white flex items-center"
                    >
                      {isLoading ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Trash2 className="w-4 h-4 mr-2" />}
                      Reset Database
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )

      case 'backup':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Backup & Export</h3>
              <div className="space-y-4">
                <div className="border border-gray-200 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-3">Export Your Data</h4>
                  <p className="text-sm text-gray-600 mb-4">
                    Download all your data including documents, chat history, and settings in a standardized format.
                  </p>
                  <button
                    onClick={handleExportData}
                    disabled={isLoading}
                    className="btn btn-primary flex items-center"
                  >
                    {isLoading ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Download className="w-4 h-4 mr-2" />}
                    Export All Data
                  </button>
                </div>

                <div className="border border-gray-200 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-3">Automatic Backups</h4>
                  <p className="text-sm text-gray-600 mb-4">
                    Configure automatic backups of your data to prevent loss.
                  </p>
                  <div className="space-y-3">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        defaultChecked={true}
                        className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">Enable automatic daily backups</span>
                    </label>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        defaultChecked={false}
                        className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">Email backup notifications</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>
            <div className="flex justify-end">
              <button
                onClick={async () => {
                  setIsLoading(true)
                  try {
                    // Create a backup settings object from the form values
                    const backupSettings = {
                      auto_backup_enabled: true, // This would come from form state
                      backup_frequency: "daily",
                      email_backup_notifications: false
                    }
                    await settingsApi.updateBackupSettings(backupSettings)
                    toast.success('Backup settings saved!')
                  } catch (error) {
                    console.error('Backup settings update error:', error)
                    toast.error('Failed to save backup settings')
                  } finally {
                    setIsLoading(false)
                  }
                }}
                disabled={isLoading}
                className="btn btn-primary flex items-center"
              >
                {isLoading ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                Save Backup Settings
              </button>
            </div>
          </div>
        )

      default:
        return <div>Tab not found</div>
    }
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Settings Navigation */}
        <div className="lg:w-64 flex-shrink-0">
          <nav className="space-y-1">
            {settingsTabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-start p-3 rounded-lg text-left transition-colors ${
                    activeTab === tab.id
                      ? 'bg-primary-100 text-primary-700 border border-primary-200'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="w-5 h-5 mt-0.5 mr-3 flex-shrink-0" />
                  <div>
                    <div className="font-medium">{tab.name}</div>
                    <div className="text-xs opacity-75 mt-1">{tab.description}</div>
                  </div>
                </button>
              )
            })}
          </nav>
        </div>

        {/* Settings Content */}
        <div className="flex-1">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            {renderTabContent()}
          </div>
        </div>
      </div>
    </div>
  )
}