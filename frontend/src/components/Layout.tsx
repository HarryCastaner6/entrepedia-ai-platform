import { Link, useLocation } from 'react-router-dom'
import {
  Home,
  MessageSquare,
  Upload,
  Network,
  Settings,
  Brain,
  BookOpen,
  Target,
  BarChart3,
  LogOut,
  User
} from 'lucide-react'
import { useAuthStore } from '../stores/authStore'
import { useDocumentStore } from '../stores/documentStore'
import toast from 'react-hot-toast'

interface LayoutProps {
  children: React.ReactNode
}

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: Home },
  { name: 'AI Chat', href: '/chat', icon: MessageSquare },
  { name: 'Upload Files', href: '/upload', icon: Upload },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const { user, logout } = useAuthStore()
  const { stats } = useDocumentStore()

  const handleLogout = () => {
    logout()
    toast.success('Logged out successfully')
  }

  const getUserInitial = () => {
    if (user?.full_name) {
      return user.full_name.charAt(0).toUpperCase()
    }
    return user?.email?.charAt(0).toUpperCase() || 'U'
  }

  return (
    <div className="min-h-screen">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 z-50 w-64 sidebar">
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center px-6 py-6 border-b border-white/20">
            <div className="flex items-center">
              <div className="flex items-center justify-center w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-600 rounded-xl shadow-lg animate-float">
                <Brain className="w-7 h-7 text-white" />
              </div>
              <div className="ml-4">
                <h1 className="text-xl font-bold text-gradient-purple">Entrepedia AI</h1>
                <p className="text-sm text-slate-500 font-medium">Learning Platform</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              const Icon = item.icon

              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`${isActive ? 'nav-item nav-item-active' : 'nav-item'} ${isActive ? 'text-purple-700' : 'text-slate-600 hover:text-slate-800'}`}
                >
                  <Icon className="w-5 h-5 mr-3" />
                  {item.name}
                </Link>
              )
            })}
          </nav>

          {/* Quick Stats */}
          <div className="px-4 py-6 border-t border-white/20">
            <div className="space-y-4">
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Quick Stats</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 rounded-xl bg-gradient-to-r from-blue-50/50 to-purple-50/50 backdrop-blur-sm border border-white/20">
                  <span className="text-sm font-medium text-slate-600">Documents</span>
                  <span className="text-lg font-bold text-gradient-purple">
                    {stats?.total_documents || 0}
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 rounded-xl bg-gradient-to-r from-purple-50/50 to-pink-50/50 backdrop-blur-sm border border-white/20">
                  <span className="text-sm font-medium text-slate-600">Embeddings</span>
                  <span className="text-lg font-bold text-gradient-purple">
                    {stats?.total_embeddings || 0}
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 rounded-xl bg-gradient-to-r from-green-50/50 to-emerald-50/50 backdrop-blur-sm border border-white/20">
                  <span className="text-sm font-medium text-slate-600">Today</span>
                  <span className="text-lg font-bold text-green-600">
                    +{stats?.processed_today || 0}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* User Section */}
          <div className="px-4 py-4 border-t border-white/20">
            <div className="flex items-center justify-between p-3 rounded-xl bg-white/30 backdrop-blur-sm border border-white/20 hover:bg-white/40 transition-all duration-300">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
                  <span className="text-white text-sm font-semibold">
                    {getUserInitial()}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-slate-800 truncate">
                    {user?.full_name || 'User'}
                  </p>
                  <p className="text-xs text-slate-500 truncate">
                    {user?.email}
                  </p>
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 text-slate-400 hover:text-red-500 transition-colors rounded-lg hover:bg-white/50"
                title="Logout"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="pl-64">
        {/* Top bar */}
        <header className="header px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="animate-slide-in-up">
              <h2 className="text-3xl font-bold text-gradient-purple mb-1">
                {getPageTitle(location.pathname)}
              </h2>
              <p className="text-sm text-slate-500 font-medium">
                {getPageDescription(location.pathname)}
              </p>
            </div>

            <div className="flex items-center space-x-4 animate-slide-in-right">
              {/* Quick Actions */}
              <div className="flex items-center space-x-3">
                <Link to="/settings" className="btn btn-secondary flex items-center">
                  <Settings className="w-4 h-4 mr-2" />
                  Settings
                </Link>
                <button className="btn btn-primary flex items-center">
                  <Target className="w-4 h-4 mr-2" />
                  New Goal
                </button>
              </div>

              {/* Status indicator */}
              <div className="flex items-center space-x-2 px-3 py-2 bg-white/50 backdrop-blur-sm rounded-xl border border-white/30">
                <div className="status-online"></div>
                <span className="text-sm font-medium text-slate-600">Online</span>
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-6 animate-fade-in">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}

function getPageTitle(pathname: string): string {
  switch (pathname) {
    case '/dashboard':
      return 'Dashboard'
    case '/chat':
      return 'AI Assistant'
    case '/upload':
      return 'Upload Documents'
    case '/knowledge':
      return 'Knowledge Graph'
    case '/settings':
      return 'Settings'
    default:
      return 'Entrepedia AI'
  }
}

function getPageDescription(pathname: string): string {
  switch (pathname) {
    case '/dashboard':
      return 'Overview of your learning progress and recent activity'
    case '/chat':
      return 'Chat with AI agents for personalized learning guidance'
    case '/upload':
      return 'Upload and process documents for your knowledge base'
    case '/knowledge':
      return 'Explore connections between concepts and topics'
    case '/settings':
      return 'Manage your account and platform preferences'
    default:
      return 'AI-enhanced education platform'
  }
}