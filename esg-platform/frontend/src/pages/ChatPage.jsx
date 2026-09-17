import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Sparkles } from 'lucide-react'
import { supabase } from '../lib/supabase'

export default function ChatPage() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I am your AI ESG Assistant. I can help you analyze your carbon emissions, suggest emission reduction strategies, or explain compliance frameworks. How can I assist you today?' }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMessage = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setIsLoading(true)

    try {
      const { data: { session } } = await supabase.auth.getSession()
      const response = await fetch('/api/v1/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify({ message: userMessage })
      })
      
      if (response.ok) {
        const data = await response.json()
        setMessages(prev => [...prev, { role: 'assistant', content: data.response, sources: data.sources }])
      } else {
        setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error connecting to the intelligence engine.' }])
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, a network error occurred.' }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <div className="flex justify-between items-center mb-6 flex-shrink-0">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-2">
            ESG Assistant <Sparkles className="text-[#14b869]" size={24} />
          </h1>
          <p className="text-[#8b949e]">Your AI co-pilot for sustainability data and reporting.</p>
        </div>
      </div>

      <div className="flex-1 bg-[#161b22] border border-white/10 rounded-2xl overflow-hidden flex flex-col shadow-xl">
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-[#14b869]/20 flex items-center justify-center flex-shrink-0 mt-1">
                  <Bot size={16} className="text-[#14b869]" />
                </div>
              )}
              
              <div className={`max-w-[80%] rounded-2xl px-5 py-3.5 ${
                msg.role === 'user' 
                  ? 'bg-[#14b869] text-white rounded-tr-none' 
                  : 'bg-[#0d1117] border border-white/10 text-[#c9d1d9] rounded-tl-none'
              }`}>
                <p className="leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                {msg.sources && (
                  <div className="mt-3 pt-3 border-t border-white/10">
                    <p className="text-xs text-[#8b949e] font-medium mb-1.5">Referenced Data Context:</p>
                    <div className="flex gap-2 flex-wrap">
                      {msg.sources.map((src, i) => (
                        <span key={i} className="px-2 py-1 rounded-md bg-white/5 text-xs text-[#8b949e] border border-white/5">
                          {src}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center flex-shrink-0 mt-1">
                  <User size={16} className="text-white" />
                </div>
              )}
            </div>
          ))}
          {isLoading && (
            <div className="flex gap-4 justify-start">
              <div className="w-8 h-8 rounded-full bg-[#14b869]/20 flex items-center justify-center flex-shrink-0 mt-1">
                <Bot size={16} className="text-[#14b869]" />
              </div>
              <div className="bg-[#0d1117] border border-white/10 rounded-2xl rounded-tl-none px-5 py-3.5 flex items-center gap-1.5">
                <div className="w-2 h-2 rounded-full bg-[#8b949e] animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 rounded-full bg-[#8b949e] animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 rounded-full bg-[#8b949e] animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="p-4 bg-[#0d1117] border-t border-white/10">
          <form onSubmit={handleSend} className="relative max-w-4xl mx-auto">
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Ask about your emissions data or reporting requirements..."
              className="w-full bg-[#161b22] border border-white/10 rounded-xl pl-5 pr-12 py-4 text-white outline-none focus:border-[#14b869] transition-colors shadow-inner"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="absolute right-3 top-1/2 -translate-y-1/2 w-8 h-8 rounded-lg bg-[#14b869] text-white flex items-center justify-center disabled:opacity-50 disabled:bg-white/10 hover:bg-[#059669] transition-colors"
            >
              <Send size={16} />
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
