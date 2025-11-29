import { useState, useEffect } from 'react'
import {
  BookOpen,
  MessageSquare,
  Upload,
  TrendingUp,
  FileText,
  Brain,
  Clock,
  Target
} from 'lucide-react'

export function Dashboard() {
  const [stats, setStats] = useState({
    totalFiles: 0,
    totalSizeMb: 0,
    fileTypes: {},
    recentActivity: []
  })

  useEffect(() => {
    // Fetch stats from API
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/documents/stats')
      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          setStats({
            totalFiles: data.total_files,
            totalSizeMb: data.total_size_mb,
            fileTypes: data.file_types,
            recentActivity: []
          })
        }
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    }
  }

  const quickActions = [
    {
      icon: Upload,
      title: 'Upload Documents',
      description: 'Add new files to your knowledge base',
      href: '/upload',
      color: 'bg-blue-500'
    },
    {
      icon: MessageSquare,
      title: 'Chat with AI',
      description: 'Get personalized learning guidance',
      href: '/chat',
      color: 'bg-green-500'
    },
    {
      icon: Brain,
      title: 'Knowledge Graph',
      description: 'Explore concept relationships',
      href: '/knowledge',
      color: 'bg-purple-500'
    }
  ]

  const learningMetrics = [
    {
      icon: FileText,
      label: 'Documents Processed',
      value: stats.totalFiles,
      change: '+2 this week',
      positive: true
    },
    {
      icon: BookOpen,
      label: 'Knowledge Base Size',
      value: `${stats.totalSizeMb} MB`,
      change: '+15% this month',
      positive: true
    },
    {
      icon: Clock,
      label: 'Study Time',
      value: '12.5 hrs',
      change: '+3 hrs this week',
      positive: true
    },
    {
      icon: Target,
      label: 'Goals Completed',
      value: '8/10',
      change: '2 pending',
      positive: false
    }
  ]

  return (
    <div className="space-y-8">
      {/* Welcome Header */}
      <div className="relative overflow-hidden rounded-3xl p-8 text-white animate-slide-in-up">
        <div
          className="absolute inset-0 bg-gradient-to-br from-purple-600 via-blue-600 to-indigo-700"
          style={{
            backgroundSize: '400% 400%',
            animation: 'gradient 15s ease infinite'
          }}
        ></div>
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="relative z-10">
          <h1 className="text-4xl font-bold mb-3 text-shadow-soft">Welcome to Entrepedia AI Platform! 🎓</h1>
          <p className="text-xl text-white/90 max-w-3xl">
            Your intelligent learning companion powered by advanced AI. Upload documents, chat with AI agents, and accelerate your learning journey.
          </p>
          <div className="mt-6 flex items-center space-x-4">
            <div className="flex items-center space-x-2 px-4 py-2 bg-white/20 backdrop-blur-sm rounded-xl">
              <div className="status-online"></div>
              <span className="text-sm font-medium">AI System Online</span>
            </div>
            <div className="flex items-center space-x-2 px-4 py-2 bg-white/20 backdrop-blur-sm rounded-xl">
              <TrendingUp className="w-4 h-4" />
              <span className="text-sm font-medium">Learning Optimized</span>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {quickActions.map((action, index) => {
          const Icon = action.icon
          return (
            <a
              key={action.title}
              href={action.href}
              className="group card card-hover interactive animate-scale-in"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="flex items-center mb-4">
                <div className="p-3 rounded-xl bg-gradient-to-br from-purple-500 to-blue-600 text-white mr-4 shadow-lg group-hover:shadow-xl transition-shadow duration-300">
                  <Icon className="w-7 h-7" />
                </div>
                <h3 className="font-bold text-slate-800 text-lg">{action.title}</h3>
              </div>
              <p className="text-slate-600 leading-relaxed">{action.description}</p>
              <div className="mt-4 flex items-center text-purple-600 font-medium">
                <span>Get started</span>
                <TrendingUp className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform duration-300" />
              </div>
            </a>
          )
        })}
      </div>

      {/* Learning Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {learningMetrics.map((metric, index) => {
          const Icon = metric.icon
          return (
            <div
              key={metric.label}
              className="metric-card hover-lift animate-slide-in-up"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="p-2 rounded-xl bg-gradient-to-br from-purple-100 to-blue-100">
                  <Icon className="w-6 h-6 text-purple-600" />
                </div>
                <span className={`text-xs font-semibold px-2 py-1 rounded-full ${
                  metric.positive
                    ? 'bg-green-100 text-green-700'
                    : 'bg-orange-100 text-orange-700'
                }`}>
                  {metric.change}
                </span>
              </div>
              <div className="space-y-2">
                <p className="metric-value">{metric.value}</p>
                <p className="metric-label">{metric.label}</p>
              </div>
            </div>
          )
        })}
      </div>

      {/* Recent Activity & File Types */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Activity */}
        <div className="card animate-slide-in-up" style={{ animationDelay: '0.2s' }}>
          <div className="flex items-center mb-6">
            <div className="p-2 bg-gradient-to-br from-purple-100 to-blue-100 rounded-xl mr-3">
              <Clock className="w-5 h-5 text-purple-600" />
            </div>
            <h3 className="text-xl font-bold text-slate-800">Recent Activity</h3>
          </div>
          <div className="space-y-4">
            <div className="flex items-center space-x-4 p-4 rounded-xl bg-gradient-to-r from-green-50/80 to-emerald-50/80 border border-white/30 hover:shadow-md transition-shadow duration-300">
              <div className="w-10 h-10 bg-gradient-to-br from-green-400 to-emerald-500 rounded-xl flex items-center justify-center shadow-lg">
                <Upload className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1">
                <p className="font-semibold text-slate-800">Document uploaded</p>
                <p className="text-sm text-slate-500">2 minutes ago</p>
              </div>
            </div>
            <div className="flex items-center space-x-4 p-4 rounded-xl bg-gradient-to-r from-blue-50/80 to-cyan-50/80 border border-white/30 hover:shadow-md transition-shadow duration-300">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-cyan-500 rounded-xl flex items-center justify-center shadow-lg">
                <MessageSquare className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1">
                <p className="font-semibold text-slate-800">AI chat session started</p>
                <p className="text-sm text-slate-500">1 hour ago</p>
              </div>
            </div>
            <div className="flex items-center space-x-4 p-4 rounded-xl bg-gradient-to-r from-purple-50/80 to-pink-50/80 border border-white/30 hover:shadow-md transition-shadow duration-300">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-400 to-pink-500 rounded-xl flex items-center justify-center shadow-lg">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1">
                <p className="font-semibold text-slate-800">Knowledge graph explored</p>
                <p className="text-sm text-slate-500">3 hours ago</p>
              </div>
            </div>
          </div>
        </div>

        {/* File Types Distribution */}
        <div className="card animate-slide-in-up" style={{ animationDelay: '0.3s' }}>
          <div className="flex items-center mb-6">
            <div className="p-2 bg-gradient-to-br from-purple-100 to-blue-100 rounded-xl mr-3">
              <FileText className="w-5 h-5 text-purple-600" />
            </div>
            <h3 className="text-xl font-bold text-slate-800">Document Types</h3>
          </div>
          <div className="space-y-4">
            {Object.entries(stats.fileTypes).length > 0 ? (
              Object.entries(stats.fileTypes).map(([type, count], index) => (
                <div
                  key={type}
                  className="flex items-center justify-between p-3 rounded-xl bg-gradient-to-r from-slate-50/80 to-gray-50/80 border border-white/30"
                >
                  <div className="flex items-center space-x-3">
                    <div className={`w-4 h-4 rounded-full ${
                      index === 0 ? 'bg-gradient-to-r from-blue-400 to-blue-600' :
                      index === 1 ? 'bg-gradient-to-r from-green-400 to-green-600' :
                      index === 2 ? 'bg-gradient-to-r from-purple-400 to-purple-600' :
                      'bg-gradient-to-r from-orange-400 to-orange-600'
                    }`}></div>
                    <span className="font-semibold text-slate-700">{type.toUpperCase()}</span>
                  </div>
                  <span className="text-lg font-bold text-gradient-purple">{count}</span>
                </div>
              ))
            ) : (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-gradient-to-br from-purple-100 to-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <FileText className="w-8 h-8 text-purple-500" />
                </div>
                <p className="font-semibold text-slate-700 mb-1">No documents uploaded yet</p>
                <p className="text-sm text-slate-500">Upload your first document to get started</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Getting Started Guide */}
      <div className="card animate-slide-in-up" style={{ animationDelay: '0.4s' }}>
        <div className="flex items-center mb-8">
          <div className="p-2 bg-gradient-to-br from-purple-100 to-blue-100 rounded-xl mr-3">
            <Target className="w-5 h-5 text-purple-600" />
          </div>
          <h3 className="text-xl font-bold text-slate-800">Getting Started</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center group">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-400 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg group-hover:shadow-xl transition-shadow duration-300">
              <span className="text-white text-xl font-bold">1</span>
            </div>
            <h4 className="font-bold text-slate-800 mb-2 text-lg">Upload Documents</h4>
            <p className="text-slate-600 leading-relaxed">
              Start by uploading your course materials, PDFs, or study documents to build your knowledge base
            </p>
          </div>
          <div className="text-center group">
            <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-green-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg group-hover:shadow-xl transition-shadow duration-300">
              <span className="text-white text-xl font-bold">2</span>
            </div>
            <h4 className="font-bold text-slate-800 mb-2 text-lg">Chat with AI</h4>
            <p className="text-slate-600 leading-relaxed">
              Ask questions and get personalized learning guidance from our hyperenhanced AI agents
            </p>
          </div>
          <div className="text-center group">
            <div className="w-16 h-16 bg-gradient-to-br from-purple-400 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg group-hover:shadow-xl transition-shadow duration-300">
              <span className="text-white text-xl font-bold">3</span>
            </div>
            <h4 className="font-bold text-slate-800 mb-2 text-lg">Explore Knowledge</h4>
            <p className="text-slate-600 leading-relaxed">
              Discover connections between concepts in your knowledge graph and accelerate learning
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}