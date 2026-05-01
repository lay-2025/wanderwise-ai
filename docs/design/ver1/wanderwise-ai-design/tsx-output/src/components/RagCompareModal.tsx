'use client'

import { useState, useEffect } from 'react'
import { compareRag, RagCompareResponse } from '@/lib/api'

interface RagCompareModalProps {
  query: string
  sessionId: string
  onClose: () => void
}

/**
 * RAGあり・なしの回答を並列表示するモーダル
 * POST /api/chat with compare_mode=true を呼び出す
 *
 * 使用例:
 *   {compareQuery && (
 *     <RagCompareModal
 *       query={compareQuery}
 *       sessionId={sessionId}
 *       onClose={() => setCompareQuery(null)}
 *     />
 *   )}
 */
export default function RagCompareModal({ query, sessionId, onClose }: RagCompareModalProps) {
  const [loading, setLoading] = useState(true)
  const [result, setResult] = useState<RagCompareResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const run = async () => {
      try {
        const data = await compareRag(query, sessionId)
        setResult(data)
      } catch (e) {
        setError(e instanceof Error ? e.message : 'エラーが発生しました')
      } finally {
        setLoading(false)
      }
    }
    run()
  }, [query, sessionId])

  return (
    /* Backdrop */
    <div
      className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-6"
      onClick={onClose}
    >
      <div
        className="w-full max-w-3xl bg-[#0f0f0f] border border-white/10 rounded-2xl overflow-hidden flex flex-col max-h-[85vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 rounded-lg bg-blue-500/15 flex items-center justify-center">
              <svg className="w-4 h-4 text-blue-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 3h7a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-7m0-18H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h7m0-18v18" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-bold text-white">RAG 回答比較</p>
              <p className="text-xs text-slate-500">同じ質問に対するRAGあり・なしの違い</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-500 hover:text-white transition-colors p-1.5 rounded-lg hover:bg-white/5"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 6 6 18M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Query */}
        <div className="px-5 py-3 border-b border-white/5 bg-white/[0.01]">
          <p className="text-xs text-slate-500 mb-1 uppercase tracking-wider">質問</p>
          <p className="text-sm text-slate-400 italic">「{query}」</p>
        </div>

        {/* Content */}
        {loading && (
          <div className="flex flex-col items-center justify-center gap-4 py-16">
            <div className="flex gap-1.5">
              <div className="h-2 w-2 animate-bounce rounded-full bg-blue-500 [animation-delay:-0.3s]" />
              <div className="h-2 w-2 animate-bounce rounded-full bg-blue-500 [animation-delay:-0.15s]" />
              <div className="h-2 w-2 animate-bounce rounded-full bg-blue-500" />
            </div>
            <p className="text-sm text-slate-500">2つのモードで回答を生成中...</p>
          </div>
        )}

        {error && (
          <div className="p-6 text-center text-red-400 text-sm">{error}</div>
        )}

        {result && !loading && (
          <div className="flex-1 overflow-y-auto grid grid-cols-2 divide-x divide-white/5">
            {/* RAGなし */}
            <div className="p-5">
              <div className="flex items-center gap-2 mb-3">
                <span className="w-2 h-2 rounded-full bg-slate-500" />
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">RAGなし</span>
                <span className="ml-auto text-xs text-slate-700">LLMの知識のみ</span>
              </div>
              <div className="text-sm text-slate-500 leading-relaxed bg-white/[0.01] border border-white/5 rounded-xl p-4">
                {result.without_rag}
              </div>
            </div>

            {/* RAGあり */}
            <div className="p-5 bg-blue-500/[0.02]">
              <div className="flex items-center gap-2 mb-3">
                <span className="w-2 h-2 rounded-full bg-blue-500 shadow-[0_0_6px_#3b82f6]" />
                <span className="text-xs font-bold text-blue-400 uppercase tracking-wider">RAGあり</span>
                <span className="ml-auto text-xs text-blue-900">収集データを活用</span>
              </div>
              <div className="text-sm text-slate-300 leading-relaxed bg-blue-500/5 border border-blue-500/20 rounded-xl p-4">
                {result.with_rag}
              </div>
              {result.sources_used.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {result.sources_used.map((src) => (
                    <span
                      key={src}
                      className="text-[10px] px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20"
                    >
                      {src}
                    </span>
                  ))}
                </div>
              )}
              <div className="mt-3 flex gap-2 items-start p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/15">
                <svg className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
                  <path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z" />
                </svg>
                <p className="text-xs text-emerald-300 leading-relaxed">
                  収集データにより具体的な情報を含む回答が生成されました。データが増えるほど回答精度が向上します。
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
