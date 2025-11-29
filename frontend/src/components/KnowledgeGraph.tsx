import { useState, useEffect } from 'react'
import {
  Network,
  Search,
  Filter,
  Download,
  Maximize2,
  Info,
  BookOpen,
  Brain,
  Lightbulb
} from 'lucide-react'

export function KnowledgeGraph() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedFilter, setSelectedFilter] = useState('all')
  const [documents, setDocuments] = useState([])
  const [stats, setStats] = useState({ total_files: 0, file_types: {} })

  useEffect(() => {
    fetchDocuments()
    fetchStats()
  }, [])

  const fetchDocuments = async () => {
    try {
      const response = await fetch('/api/documents/processed')
      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          setDocuments([...data.upload_files, ...data.scraped_files])
        }
      }
    } catch (error) {
      console.error('Failed to fetch documents:', error)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/documents/stats')
      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          setStats(data)
        }
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    }
  }

  const mockNodes = [
    { id: 'ai', label: 'Artificial Intelligence', type: 'concept', connections: 5, color: 'bg-blue-500' },
    { id: 'ml', label: 'Machine Learning', type: 'concept', connections: 8, color: 'bg-green-500' },
    { id: 'nn', label: 'Neural Networks', type: 'concept', connections: 6, color: 'bg-purple-500' },
    { id: 'dl', label: 'Deep Learning', type: 'concept', connections: 4, color: 'bg-red-500' },
    { id: 'nlp', label: 'Natural Language Processing', type: 'concept', connections: 3, color: 'bg-yellow-500' },
    { id: 'cv', label: 'Computer Vision', type: 'concept', connections: 2, color: 'bg-pink-500' }
  ]

  const mockConnections = [
    { from: 'ai', to: 'ml', strength: 'strong' },
    { from: 'ml', to: 'nn', strength: 'strong' },
    { from: 'nn', to: 'dl', strength: 'strong' },
    { from: 'ml', to: 'nlp', strength: 'medium' },
    { from: 'ml', to: 'cv', strength: 'medium' },
    { from: 'dl', to: 'nlp', strength: 'medium' },
    { from: 'dl', to: 'cv', strength: 'strong' }
  ]

  const filteredNodes = mockNodes.filter(node =>
    node.label.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">Knowledge Graph Explorer 🕸️</h1>
        <p className="text-purple-100">
          Visualize connections between concepts in your learning materials and discover new insights.
        </p>
      </div>

      {/* Controls */}
      <div className="flex flex-col lg:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search concepts, topics, or documents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>
        </div>
        <div className="flex space-x-2">
          <select
            value={selectedFilter}
            onChange={(e) => setSelectedFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="all">All Types</option>
            <option value="concept">Concepts</option>
            <option value="document">Documents</option>
            <option value="topic">Topics</option>
          </select>
          <button className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
            <Filter className="w-4 h-4 mr-2" />
            Filter
          </button>
          <button className="flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Graph Visualization */}
        <div className="lg:col-span-2 space-y-4">
          {/* Graph Canvas */}
          <div className="bg-white border border-gray-200 rounded-lg p-6 h-96 relative">
            <div className="absolute top-4 right-4 flex space-x-2">
              <button className="p-2 bg-gray-100 rounded-lg hover:bg-gray-200">
                <Maximize2 className="w-4 h-4 text-gray-600" />
              </button>
              <button className="p-2 bg-gray-100 rounded-lg hover:bg-gray-200">
                <Info className="w-4 h-4 text-gray-600" />
              </button>
            </div>

            {/* Simulated Graph */}
            <div className="relative w-full h-full">
              <div className="text-center mt-20">
                <Network className="w-16 h-16 text-purple-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Knowledge Graph Visualization</h3>
                <p className="text-gray-500 text-sm mb-4">
                  Interactive graph will appear here once documents are processed and embeddings are generated.
                </p>

                {stats.total_files === 0 ? (
                  <div className="bg-blue-50 rounded-lg p-4 text-left">
                    <h4 className="font-medium text-blue-900 mb-2">Getting Started</h4>
                    <ul className="text-sm text-blue-700 space-y-1">
                      <li>• Upload some documents to begin</li>
                      <li>• Process them to extract knowledge</li>
                      <li>• Watch connections form automatically</li>
                    </ul>
                  </div>
                ) : (
                  <div className="bg-green-50 rounded-lg p-4 text-left">
                    <h4 className="font-medium text-green-900 mb-2">Ready to Generate Graph</h4>
                    <p className="text-sm text-green-700 mb-3">
                      You have {stats.total_files} documents processed. Enable embeddings to see the knowledge graph.
                    </p>
                    <button className="bg-green-600 text-white px-4 py-2 rounded text-sm hover:bg-green-700">
                      Generate Knowledge Graph
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Mock Concept Connections */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h3 className="font-medium text-gray-900 mb-3">Concept Network Preview</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {mockNodes.map((node) => (
                <div
                  key={node.id}
                  className="p-3 border border-gray-200 rounded-lg hover:shadow-sm transition-shadow cursor-pointer"
                >
                  <div className="flex items-center space-x-2 mb-2">
                    <div className={`w-3 h-3 rounded-full ${node.color}`}></div>
                    <span className="font-medium text-sm text-gray-900">{node.label}</span>
                  </div>
                  <div className="text-xs text-gray-500">
                    {node.connections} connections
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Graph Stats */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h3 className="font-medium text-gray-900 mb-3">Graph Statistics</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Documents</span>
                <span className="text-sm font-medium">{stats.total_files}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Concepts</span>
                <span className="text-sm font-medium">{mockNodes.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Connections</span>
                <span className="text-sm font-medium">{mockConnections.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Clusters</span>
                <span className="text-sm font-medium">3</span>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h3 className="font-medium text-gray-900 mb-3">Quick Actions</h3>
            <div className="space-y-2">
              <button className="w-full flex items-center px-3 py-2 text-left text-sm bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors">
                <Brain className="w-4 h-4 mr-2 text-purple-500" />
                Find Related Concepts
              </button>
              <button className="w-full flex items-center px-3 py-2 text-left text-sm bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors">
                <Lightbulb className="w-4 h-4 mr-2 text-yellow-500" />
                Discover Patterns
              </button>
              <button className="w-full flex items-center px-3 py-2 text-left text-sm bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors">
                <BookOpen className="w-4 h-4 mr-2 text-blue-500" />
                Show Learning Path
              </button>
            </div>
          </div>

          {/* Recent Documents */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h3 className="font-medium text-gray-900 mb-3">Recent Documents</h3>
            <div className="space-y-2">
              {documents.slice(0, 5).map((doc: any, index) => (
                <div key={index} className="text-sm">
                  <p className="font-medium text-gray-900 truncate">{doc.filename}</p>
                  <p className="text-gray-500 text-xs">{doc.source}</p>
                </div>
              ))}
              {documents.length === 0 && (
                <p className="text-sm text-gray-500 text-center py-4">
                  No documents uploaded yet
                </p>
              )}
            </div>
          </div>

          {/* Legend */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h3 className="font-medium text-gray-900 mb-3">Legend</h3>
            <div className="space-y-2 text-xs">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span>Core Concept</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span>Related Topic</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-gray-300 rounded-full"></div>
                <span>Supporting Material</span>
              </div>
              <div className="mt-3">
                <div className="w-full h-0.5 bg-gradient-to-r from-purple-500 to-transparent"></div>
                <span className="text-xs text-gray-500">Connection Strength</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}