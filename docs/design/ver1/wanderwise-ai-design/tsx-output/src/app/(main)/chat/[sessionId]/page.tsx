'use client'

import { useState, useRef, useEffect, use } from 'react'
import { Brain, Send, Sparkles, Columns2 } from 'lucide-react'
import { getHistory, sendChat, getExtractions, ChatMessage, TravelExtraction } from '@/lib/api'
import { useSession } from '@/context/SessionContext'
import ExtractionBadge from '@/components/ExtractionBadge'
import ExtractionPanel from '@/components/ExtractionPanel'
import RagCompareModal from '@/components/RagCompareModal'

// ---------------------------------------------------------------
// 型定義
// ---------------------------------------------------------------

interface UIMessage {
  role: 'user' | 'assistant'
  content: string
  time: string
  /** このメッセージに紐づく抽出データのID一覧 */
  extraction_ids: string[]
}

function toUIMessage(msg: ChatMessage): UIMessage {
  return {
    role: msg.role,
    content: msg.content,
    time: new Date(msg.created_at).toLocaleTimeString('ja-JP', {
      hour: '2-digit',
      minute: '2-digit',
    }),
    extraction_ids: [],
  }
}

const WELCOME: UIMessage = {
  role: 'assistant',
  content: 'こんにちは！旅行についてお話ししましょう。最近行った場所や、行きたい場所について教えてください。',
  time: '',
  extraction_ids: [],
}

// ---------------------------------------------------------------
// ページ本体
// ---------------------------------------------------------------

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

  // 抽出データ: { [extraction_id]: TravelExtraction }
  const [extractionMap, setExtractionMap] = useState<Record<string, TravelExtraction>>({})
  const [showPanel, setShowPanel] = useState(true)
  const [compareQuery, setCompareQuery] = useState<string | null>(null)

  const bottomRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // textarea 高さの自動調整
  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`
  }, [input])

  // セッション切り替え時に履歴と抽出データを読み込む
  useEffect(() => {
    setHistoryLoaded(false)
    setMessages([WELCOME])
    setExtractionMap({})

    Promise.all([
      getHistory(sessionId),
      getExtractions(sessionId),
    ])
      .then(([histData, exData]) => {
        if (histData.messages.length > 0) {
          setMessages(histData.messages.map(toUIMessage))
        }
        // 抽出データをマップに変換して保持
        const map: Record<string, TravelExtraction> = {}
        exData.extractions.forEach((ex) => { map[ex.id] = ex })
        setExtractionMap(map)
      })
      .catch(() => {})
      .finally(() => setHistoryLoaded(true))
  }, [sessionId])

  // 新しいメッセージが来たら末尾へスクロール
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // セッション全体の抽出データ一覧（パネル用）
  const allExtractions = Object.values(extractionMap)

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMsg: UIMessage = {
      role: 'user',
      content: input,
      time: new Date().toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' }),
      extraction_ids: [],
    }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
    setIsLoading(true)

    try {
      const data = await sendChat(userMsg.content, sessionId)

      // バックエンドから返ってくる extractions を処理
      // ChatResponse.extractions が TravelExtraction[] になることを前提とする
      // (api.ts の ChatResponse.extractions: unknown[] を TravelExtraction[] に変更してください)
      const newExtractions = (data.extractions ?? []) as TravelExtraction[]
      const newIds: string[] = []
      const newMap: Record<string, TravelExtraction> = {}
      newExtractions.forEach((ex) => {
        newIds.push(ex.id)
        newMap[ex.id] = ex
      })
      setExtractionMap((prev) => ({ ...prev, ...newMap }))

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.response,
          time: new Date().toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' }),
          extraction_ids: newIds,
        },
      ])

      // サイドバーのタイトル・updated_at を更新
      loadSessions()
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: '申し訳ありません。エラーが発生しました。しばらくしてからもう一度お試しください。',
          time: new Date().toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' }),
          extraction_ids: [],
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* RAG比較モーダル */}
      {compareQuery && (
        <RagCompareModal
          query={compareQuery}
          sessionId={sessionId}
          onClose={() => setCompareQuery(null)}
        />
      )}

      {/* ツールバー */}
      <div className="flex items-center gap-2 justify-end px-4 py-2 border-b border-white/5">
        <button
          onClick={() => {
            const lastUserMsg = [...messages].reverse().find((m) => m.role === 'user')
            setCompareQuery(lastUserMsg?.content ?? '旅行について教えてください')
          }}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border border-blue-500/25 bg-blue-500/7 text-blue-400 hover:bg-blue-500/15 transition-colors"
        >
          <Columns2 className="h-3.5 w-3.5" />
          RAG比較
        </button>
        <button
          onClick={() => setShowPanel((v) => !v)}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-colors ${
            showPanel
              ? 'border-emerald-500/30 bg-emerald-500/8 text-emerald-400'
              : 'border-white/10 text-slate-500 hover:text-slate-300'
          }`}
        >
          <Sparkles className="h-3.5 w-3.5" />
          抽出データ {showPanel ? '非表示' : '表示'}
        </button>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* メッセージエリア */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto py-6">
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
                    <div className="max-w-[80%]">
                      <div
                        className={`border rounded-2xl p-4 text-slate-200 ${
                          msg.role === 'assistant'
                            ? 'bg-[#121212] border-white/5 rounded-tl-sm'
                            : 'bg-blue-600/10 border-blue-500/20 rounded-tr-sm'
                        }`}
                      >
                        <p className="leading-relaxed whitespace-pre-wrap text-sm">{msg.content}</p>
                        {msg.time && (
                          <div className="text-xs text-slate-500 mt-3">{msg.time}</div>
                        )}
                      </div>

                      {/* 抽出バッジ */}
                      {msg.role === 'assistant' && msg.extraction_ids.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 mt-2">
                          {msg.extraction_ids.map((id) => {
                            const ex = extractionMap[id]
                            return ex ? <ExtractionBadge key={id} extraction={ex} /> : null
                          })}
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}

              {/* ローディング中のドット */}
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
            </div>
          </div>

          {/* 入力エリア */}
          <div className="p-4 md:p-6 pb-8">
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
                  className="flex-1 bg-transparent text-white placeholder-slate-500 resize-none outline-none min-h-[44px] py-3 px-4 text-sm leading-relaxed overflow-y-auto"
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
              <div className="text-center text-xs text-slate-600 mt-3 tracking-wide">
                会話から旅行データを自動抽出し、RAGの精度を継続的に向上させます
              </div>
            </div>
          </div>
        </div>

        {/* 抽出データパネル（右サイド） */}
        {showPanel && (
          <aside className="w-60 flex-shrink-0 border-l border-white/5 bg-[#0c0c0c] flex flex-col overflow-hidden">
            <div className="flex items-center gap-2 px-3 py-3 border-b border-white/5">
              <Sparkles className="h-3.5 w-3.5 text-emerald-400" />
              <span className="text-xs font-bold text-slate-400">抽出データ</span>
              <div className="ml-auto text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400">
                {allExtractions.length}
              </div>
            </div>
            <div className="flex-1 overflow-y-auto">
              <ExtractionPanel extractions={allExtractions} />
            </div>
            <div className="p-2 border-t border-white/5">
              <button
                onClick={() => {
                  const lastUserMsg = [...messages].reverse().find((m) => m.role === 'user')
                  setCompareQuery(lastUserMsg?.content ?? '旅行について教えてください')
                }}
                className="w-full flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-semibold bg-blue-500/8 border border-blue-500/20 text-blue-400 hover:bg-blue-500/15 transition-colors"
              >
                <Columns2 className="h-3.5 w-3.5" />
                RAG効果を比較
              </button>
            </div>
          </aside>
        )}
      </div>
    </div>
  )
}
