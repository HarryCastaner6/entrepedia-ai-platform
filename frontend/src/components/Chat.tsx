import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2, Sparkles, Brain } from 'lucide-react'

interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  agent?: string
  timestamp: Date
}

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: `Welcome to your AI Learning Assistant! 🎓

I'm here to help you with your educational journey. You can:

🧑‍🏫 **Chat with Coach** - Get personalized learning guidance, study tips, and motivation
🧠 **Chat with Strategist** - Create comprehensive learning plans and strategic approaches

What would you like help with today?`,
      agent: 'system',
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [selectedAgent, setSelectedAgent] = useState<'coach' | 'strategist'>('coach')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/query/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: input,
          agent_type: selectedAgent,
          include_knowledge_base: true
        })
      })

      if (response.ok) {
        const data = await response.json()

        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: data.response?.content || 'Sorry, I encountered an error processing your request.',
          agent: selectedAgent,
          timestamp: new Date()
        }

        setMessages(prev => [...prev, assistantMessage])
      } else {
        throw new Error('Failed to get response')
      }
    } catch (error) {
      console.error('Chat error:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        agent: 'system',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-200px)]">
      {/* Agent Selection */}
      <div className="mb-4 p-4 bg-white rounded-lg border border-gray-200">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Choose your AI Assistant:
        </label>
        <div className="flex space-x-4">
          <button
            onClick={() => setSelectedAgent('coach')}
            className={`flex items-center px-4 py-2 rounded-lg border transition-colors ${
              selectedAgent === 'coach'
                ? 'bg-blue-50 border-blue-200 text-blue-700'
                : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
            }`}
          >
            <Sparkles className="w-4 h-4 mr-2" />
            Coach Agent
          </button>
          <button
            onClick={() => setSelectedAgent('strategist')}
            className={`flex items-center px-4 py-2 rounded-lg border transition-colors ${
              selectedAgent === 'strategist'
                ? 'bg-purple-50 border-purple-200 text-purple-700'
                : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
            }`}
          >
            <Brain className="w-4 h-4 mr-2" />
            Strategist Agent
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          {selectedAgent === 'coach'
            ? 'Get personalized learning guidance, motivation, and study tips'
            : 'Create comprehensive learning strategies and tactical plans'
          }
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 p-4 bg-gray-50 rounded-lg">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-3xl px-4 py-3 rounded-lg ${
                message.type === 'user'
                  ? 'bg-blue-600 text-white ml-8'
                  : 'bg-white text-gray-900 border border-gray-200 mr-8'
              }`}
            >
              <div className="flex items-start space-x-2">
                {message.type === 'assistant' && (
                  <div className="flex-shrink-0 mt-1">
                    {message.agent === 'coach' ? (
                      <Sparkles className="w-4 h-4 text-blue-500" />
                    ) : message.agent === 'strategist' ? (
                      <Brain className="w-4 h-4 text-purple-500" />
                    ) : (
                      <Bot className="w-4 h-4 text-gray-400" />
                    )}
                  </div>
                )}
                <div className="flex-1">
                  <div className="whitespace-pre-wrap">{message.content}</div>
                  {message.agent && message.agent !== 'system' && (
                    <div className="text-xs opacity-70 mt-2">
                      {message.agent === 'coach' ? '🧑‍🏫 Coach Agent' : '🧠 Strategist Agent'}
                    </div>
                  )}
                </div>
                {message.type === 'user' && (
                  <div className="flex-shrink-0 mt-1">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white text-gray-900 border border-gray-200 px-4 py-3 rounded-lg mr-8">
              <div className="flex items-center space-x-2">
                <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
                <span>Thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="mt-4 p-4 bg-white rounded-lg border border-gray-200">
        <div className="flex space-x-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={`Ask the ${selectedAgent} agent anything about learning...`}
            rows={3}
            className="flex-1 resize-none border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
        <div className="text-xs text-gray-500 mt-2">
          Press Enter to send, Shift+Enter for new line
        </div>
      </div>
    </div>
  )
}