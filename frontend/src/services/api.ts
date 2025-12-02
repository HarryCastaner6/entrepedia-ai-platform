import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export interface QueryRequest {
  query: string
  agent_type?: string
  context?: Record<string, any>
  include_knowledge_base?: boolean
}

export interface AgentResponse {
  success: boolean
  response: {
    agent: string
    content: string
    metadata: Record<string, any>
    timestamp: string
  }
  knowledge_base_results: number
  agent_used: string
}

export interface DocumentStats {
  success: boolean
  total_files: number
  total_size_bytes: number
  total_size_mb: number
  file_types: Record<string, number>
}

export interface ProcessedDocument {
  filename: string
  size: number
  modified: number
  source: string
  course?: string
}

export interface DocumentsResponse {
  success: boolean
  upload_files: ProcessedDocument[]
  scraped_files: ProcessedDocument[]
  total_files: number
}

export interface LearningPlanRequest {
  topic: string
  level: string
  duration: string
}

export interface GamePlanRequest {
  objective: string
  deadline: string
  resources?: Record<string, any>
}

// Query API
export const queryApi = {
  ask: async (request: QueryRequest): Promise<AgentResponse> => {
    const response = await api.post('/query/ask', request)
    return response.data
  },

  searchKnowledgeBase: async (query: string, limit = 10) => {
    const response = await api.post('/query/search', {
      query,
      limit,
      threshold: 0.7
    })
    return response.data
  },

  createLearningPlan: async (request: LearningPlanRequest) => {
    const response = await api.post('/query/learning-plan', request)
    return response.data
  },

  createGamePlan: async (request: GamePlanRequest) => {
    const response = await api.post('/query/game-plan', request)
    return response.data
  },

  createMasterStrategy: async (goals: string[], constraints?: Record<string, any>, timeline = '6 months') => {
    const response = await api.post('/query/master-strategy', {
      goals,
      constraints,
      timeline
    })
    return response.data
  },

  listAgents: async () => {
    const response = await api.get('/query/agents')
    return response.data
  }
}

// Documents API
export const documentsApi = {
  upload: async (file: File, createEmbeddings = true) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('create_embeddings', createEmbeddings.toString())

    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  scrapeEntrepedia: async () => {
    const response = await api.post('/documents/scrape-entrepedia')
    return response.data
  },

  listProcessed: async (): Promise<DocumentsResponse> => {
    const response = await api.get('/documents/processed')
    return response.data
  },

  getStats: async (): Promise<DocumentStats> => {
    const response = await api.get('/documents/stats')
    return response.data
  },

  delete: async (filename: string) => {
    const response = await api.delete(`/documents/delete/${filename}`)
    return response.data
  },

  getScrapingStatus: async () => {
    const response = await api.get('/documents/scraping-status')
    return response.data
  }
}

// Auth API
export const authApi = {
  login: async (username: string, password: string) => {
    const response = await api.post('/auth', {
      username,
      password
    })
    return response.data
  },

  register: async (userData: {
    username: string
    email: string
    password: string
    full_name: string
  }) => {
    const response = await api.post('/auth/register', userData)
    return response.data
  },

  logout: async () => {
    const response = await api.post('/auth', {}, {
      params: { action: 'logout' }
    })
    return response.data
  },

  getProfile: async () => {
    const response = await api.get('/auth')
    return response.data
  },

  verifyToken: async () => {
    const response = await api.get('/auth/verify-token')
    return response.data
  }
}

// Integrations API
export const integrationsApi = {
  getStatus: async () => {
    const response = await api.get('/integrations/status')
    return response.data
  },

  createCalendarEvent: async (event: {
    title: string
    description: string
    start_time: string
    end_time: string
    timezone?: string
  }) => {
    const response = await api.post('/integrations/google-calendar/event', event)
    return response.data
  },

  createNotionPage: async (page: {
    title: string
    content: string
    database_id: string
  }) => {
    const response = await api.post('/integrations/notion/page', page)
    return response.data
  },

  syncLearningPlan: async (learningPlan: any, integrations: string[]) => {
    const response = await api.post('/integrations/sync-learning-plan', {
      learning_plan: learningPlan,
      integrations
    })
    return response.data
  }
}

export default api