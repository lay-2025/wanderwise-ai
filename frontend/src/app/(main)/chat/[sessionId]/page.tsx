'use client'

import { useState, useRef, useEffect, use } from 'react'
import { Brain, Send } from 'lucide-react'
import { getHistory, sendChat, ChatMessage } from '@/lib/api'
import { useSession } from '@/context/SessionContext'

interface UIMessage {
  role: 'user' | 'assistant'
  content: string
  time: string
}

function toUIMessage(msg: ChatMessage): UIMessage {
  return {
    role: msg.role,
    content: msg.content,
    time: new Date(msg.created_at).toLocaleTimeString('ja-JP', {
      hour: '2-digit',
      minute: '2-digit',
    }),
  }
}

const WELCOME: UIMessage = {
  role: 'assistant',
  content: 'こんにちは！旅行についてお話ししましょう。最近行った場所や、行きたい場所について教えてください。',
  time: '',
}

export default function ChatSessionPage({
  params,
}: {
  params: Promise<{ sessionId: string }>
}) {
  const { sessionId } = use(params)
  const { loadSessions } = useSession()

  const [messages, setMessages] = useState<UIMessage[]>([WELCOME])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [historyLoaded, setHistoryLoaded] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // input が変わるたびに textarea の高さを内容に合わせて自動調整する
  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`
  }, [input])

  // セッション切り替え時に履歴を読み込む
  useEffect(() => {
    setHistoryLoaded(false)
    setMessages([WELCOME])

    getHistory(sessionId)
      .then((data) => {
        if (data.messages.length > 0) {
          setMessages(data.messages.map(toUIMessage))
        }
      })
      .catch(() => {})
      .finally(() => setHistoryLoaded(true))
  }, [sessionId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMsg: UIMessage = {
      role: 'user',
      content: input,
      time: new Date().toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' }),
    }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
    setIsLoading(true)

    try {
      const data = await sendChat(userMsg.content, sessionId)
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.response,
          time: new Date().toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' }),
        },
      ])
      // タイトル自動生成・updated_at 更新をサイドバーに反映
      loadSessions()
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: '申し訳ありません。エラーが発生しました。しばらくしてからもう一度お試しください。',
          time: new Date().toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' }),
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* メッセージエリア */}
      <div className="flex-1 overflow-y-auto py-6 mt-4">
        <div className="max-w-3xl mx-auto px-4 space-y-6">
        {!historyLoaded ? (
          <div className="flex justify-center pt-8">
            <div className="flex gap-1.5">
              <div className="h-2 w-2 animate-bounce rounded-full bg-blue-500 [animation-delay:-0.3s]" />
              <div className="h-2 w-2 animate-bounce rounded-full bg-blue-500 [animation-delay:-0.15s]" />
              <div className="h-2 w-2 animate-bounce rounded-full bg-blue-500" />
            </div>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div
              key={index}
              className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
            >
              {msg.role === 'assistant' && (
                <div className="flex-shrink-0 mt-1">
                  <div className="w-9 h-9 bg-blue-600 rounded-xl flex items-center justify-center text-white shadow-[0_0_15px_rgba(37,99,235,0.4)]">
                    <Brain className="h-5 w-5" />
                  </div>
                </div>
              )}
              <div
                className={`border rounded-2xl p-4 max-w-[80%] text-slate-200 ${
                  msg.role === 'assistant'
                    ? 'bg-[#121212] border-white/5 rounded-tl-sm'
                    : 'bg-blue-600/10 border-blue-500/20 rounded-tr-sm'
                }`}
              >
                <p className="leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                {msg.time && (
                  <div className="text-xs text-slate-500 mt-3">{msg.time}</div>
                )}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex gap-3">
            <div className="flex-shrink-0 mt-1">
              <div className="w-9 h-9 bg-blue-600 rounded-xl flex items-center justify-center text-white">
                <Brain className="h-5 w-5" />
              </div>
            </div>
            <div className="border rounded-2xl p-4 bg-[#121212] border-white/5 rounded-tl-sm">
              <div className="flex gap-1">
                <div className="h-2 w-2 animate-bounce rounded-full bg-blue-500 [animation-delay:-0.3s]" />
                <div className="h-2 w-2 animate-bounce rounded-full bg-blue-500 [animation-delay:-0.15s]" />
                <div className="h-2 w-2 animate-bounce rounded-full bg-blue-500" />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
        </div>{/* /max-w-3xl */}
      </div>

      {/* 入力エリア */}
      <div className="p-4 md:p-6 pb-8 mt-auto">
        <div className="max-w-3xl mx-auto">
          <div className="relative flex items-end gap-2 bg-[#121212] border border-white/10 rounded-2xl p-2 focus-within:border-blue-500/50 shadow-lg transition-colors">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSend()
                }
              }}
              placeholder="旅行について話してください... (Shift+Enter で改行)"
              className="flex-1 bg-transparent text-white placeholder-slate-500 resize-none outline-none min-h-[44px] py-3 px-4 text-base leading-relaxed overflow-y-auto"
              style={{ maxHeight: '200px' }}
              rows={1}
              disabled={isLoading}
            />
            <button
              onClick={handleSend}
              className="p-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl transition-all shadow-md hover:shadow-[0_0_15px_rgba(37,99,235,0.5)] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-none mb-1 mr-1"
              disabled={!input.trim() || isLoading}
            >
              <Send className="h-5 w-5" />
            </button>
          </div>
          <div className="text-center text-xs text-slate-500 mt-4 font-medium tracking-wide">
            あなたの会話から旅行データを学習し、より良い回答を提供します
          </div>
        </div>
      </div>
    </div>
  )
}
