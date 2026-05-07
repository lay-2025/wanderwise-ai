'use client'

import { useState, useEffect, useCallback } from 'react'
import {
  getDocuments,
  deleteDocument,
  toggleDocument,
  uploadDocumentFromUrl,
  searchDocuments,
  type Document,
  type SearchResult,
} from '@/lib/api'
import DocToggle from '@/components/DocToggle'
import SourceBadge from '@/components/SourceBadge'
import {
  Sparkles, Database, Layers, Search, Upload, Link, Trash2,
  File, MessageSquare, Info, RefreshCw,
} from 'lucide-react'

// ---------------------------------------------------------------
// ベクトル可視化（静的モック — /api/learning/visualize で後から差し替え）
// ---------------------------------------------------------------

const CLUSTERS = [
  { label: '京都',   color: '#3b82f6', cx: 115, cy: 88,  n: 14 },
  { label: '東京',   color: '#8b5cf6', cx: 220, cy: 145, n: 20 },
  { label: '北海道', color: '#06b6d4', cx: 68,  cy: 178, n: 11 },
  { label: 'バリ島', color: '#10b981', cx: 295, cy: 78,  n: 9  },
  { label: '欧州',   color: '#f59e0b', cx: 258, cy: 212, n: 16 },
]

function genPoints() {
  let s = 42
  const rnd = () => { s = ((s * 1664525 + 1013904223) >>> 0); return s / 4294967296 }
  return CLUSTERS.flatMap((cl) =>
    Array.from({ length: cl.n }, () => {
      const a = rnd() * Math.PI * 2
      const r = rnd() * 26 + 4
      return { x: cl.cx + Math.cos(a) * r, y: cl.cy + Math.sin(a) * r, color: cl.color, label: cl.label }
    })
  )
}
const VECTOR_POINTS = genPoints()

// ---------------------------------------------------------------
// タブ定義
// ---------------------------------------------------------------

type Tab = 'docs' | 'vectors' | 'search'

const TABS: { id: Tab; label: string; Icon: React.ElementType }[] = [
  { id: 'docs',    label: 'RAGデータ管理', Icon: Database },
  { id: 'vectors', label: 'ベクトル可視化', Icon: Layers },
  { id: 'search',  label: '検索テスト',    Icon: Search },
]

// ---------------------------------------------------------------
// StatusBadge
// ---------------------------------------------------------------

function StatusBadge({ status }: { status: Document['status'] }) {
  const map: Record<Document['status'], { label: string; className: string }> = {
    vectorized: { label: '完了',   className: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' },
    processing: { label: '処理中', className: 'bg-amber-500/10  text-amber-400  border-amber-500/20' },
    pending:    { label: '待機中', className: 'bg-slate-500/10  text-slate-400  border-slate-500/20' },
    failed:     { label: '失敗',   className: 'bg-red-500/10    text-red-400    border-red-500/20' },
  }
  const { label, className } = map[status] ?? map.pending
  return (
    <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border flex items-center gap-1 ${className}`}>
      {status === 'processing' && <RefreshCw className="h-2.5 w-2.5 animate-spin" />}
      {label}
    </span>
  )
}

// ---------------------------------------------------------------
// メインページ
// ---------------------------------------------------------------

export default function LearningPage() {
  const [tab, setTab]               = useState<Tab>('docs')
  const [docs, setDocs]             = useState<Document[]>([])
  const [docsLoading, setDocsLoading] = useState(true)
  const [togglingId, setTogglingId]   = useState<string | null>(null)

  const [showUrlForm, setShowUrlForm] = useState(false)
  const [urlTitle, setUrlTitle]       = useState('')
  const [urlInput, setUrlInput]       = useState('')
  const [urlLoading, setUrlLoading]   = useState(false)
  const [urlError, setUrlError]       = useState('')

  const [query, setQuery]         = useState('')
  const [results, setResults]     = useState<SearchResult[] | null>(null)
  const [searching, setSearching] = useState(false)

  const [hoverPt, setHoverPt] = useState<number | null>(null)

  // ---------------------------------------------------------------
  // データ取得
  // ---------------------------------------------------------------

  const loadDocs = useCallback(async () => {
    try {
      const data = await getDocuments()
      setDocs(data.documents)
    } catch {
      // 未実装APIは空一覧として表示
    } finally {
      setDocsLoading(false)
    }
  }, [])

  useEffect(() => { loadDocs() }, [loadDocs])

  // ---------------------------------------------------------------
  // ハンドラ
  // ---------------------------------------------------------------

  const handleToggle = async (id: string) => {
    setTogglingId(id)
    try {
      const updated = await toggleDocument(id)
      setDocs((prev) => prev.map((d) => (d.id === id ? { ...d, is_active: updated.is_active } : d)))
    } catch {
      // ignore
    } finally {
      setTogglingId(null)
    }
  }

  const handleDelete = async (id: string) => {
    try {
      await deleteDocument(id)
      setDocs((prev) => prev.filter((d) => d.id !== id))
    } catch {
      // ignore
    }
  }

  const handleAddUrl = async () => {
    if (!urlTitle.trim() || !urlInput.trim()) return
    setUrlLoading(true)
    setUrlError('')
    try {
      const doc = await uploadDocumentFromUrl(urlTitle.trim(), urlInput.trim())
      setDocs((prev) => [doc, ...prev])
      setUrlTitle('')
      setUrlInput('')
      setShowUrlForm(false)
    } catch (e) {
      setUrlError(e instanceof Error ? e.message : 'エラーが発生しました')
    } finally {
      setUrlLoading(false)
    }
  }

  const handleSearch = async () => {
    if (!query.trim()) return
    setSearching(true)
    setResults(null)
    try {
      const data = await searchDocuments(query)
      setResults(data.results)
    } catch {
      setResults([])
    } finally {
      setSearching(false)
    }
  }

  // ---------------------------------------------------------------
  // 統計
  // ---------------------------------------------------------------

  const activeCount = docs.filter((d) => d.is_active && d.status === 'vectorized').length
  const totalChunks = docs
    .filter((d) => d.is_active && d.status === 'vectorized')
    .reduce((s, d) => s + (d.chunks ?? 0), 0)

  // ---------------------------------------------------------------
  // UI
  // ---------------------------------------------------------------

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="max-w-4xl mx-auto px-6 py-8 pb-20">

        {/* ページヘッダー */}
        <div className="mb-7">
          <div className="flex items-center gap-3 mb-1.5">
            <div className="w-8 h-8 rounded-xl bg-blue-500/12 flex items-center justify-center text-blue-400">
              <Sparkles className="h-4 w-4" />
            </div>
            <h1 className="text-xl font-extrabold text-white tracking-tight">学習管理</h1>
          </div>
          <p className="text-sm text-slate-500">
            RAGデータの管理・ON/OFF切り替え、ベクトル可視化、検索テストができます
          </p>
        </div>

        {/* 統計カード */}
        <div className="grid grid-cols-4 gap-3 mb-7">
          {[
            { label: '全ドキュメント', value: docs.length,    sub: `${docs.filter((d) => d.status === 'vectorized').length} 完了`, color: 'text-blue-400' },
            { label: 'RAG有効',        value: activeCount,     sub: 'ベクトル検索対象',   color: 'text-emerald-400' },
            { label: '総チャンク数',   value: totalChunks,     sub: '有効ドキュメントのみ', color: 'text-violet-400' },
            { label: 'クラスター数',   value: CLUSTERS.length, sub: CLUSTERS.map((c) => c.label).join('・'), color: 'text-amber-400' },
          ].map((st) => (
            <div key={st.label} className="bg-white/[0.02] border border-white/8 rounded-2xl p-4">
              <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-1.5">{st.label}</p>
              <p className={`text-2xl font-extrabold leading-none ${st.color}`}>{st.value}</p>
              <p className="text-[11px] text-slate-600 mt-1.5">{st.sub}</p>
            </div>
          ))}
        </div>

        {/* タブ */}
        <div className="flex gap-1 p-1 mb-6 bg-white/[0.02] border border-white/8 rounded-xl w-fit">
          {TABS.map(({ id, label, Icon }) => (
            <button
              key={id}
              onClick={() => setTab(id)}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                tab === id
                  ? 'bg-blue-500/15 text-blue-400 border border-blue-500/25'
                  : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <Icon className="h-3.5 w-3.5" />
              {label}
            </button>
          ))}
        </div>

        {/* ── RAGデータ管理タブ ── */}
        {tab === 'docs' && (
          <div className="space-y-4">

            {/* URLドキュメント取り込み */}
            {!showUrlForm ? (
              <button
                onClick={() => setShowUrlForm(true)}
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold bg-blue-500/7 border border-blue-500/22 text-blue-400 hover:bg-blue-500/14 transition-colors"
              >
                <Link className="h-4 w-4" />
                URLからドキュメントを取り込む
              </button>
            ) : (
              <div className="p-4 rounded-2xl bg-blue-500/[0.04] border border-blue-500/20 space-y-3">
                <div className="flex items-center gap-2">
                  <Link className="h-4 w-4 text-blue-400" />
                  <span className="text-sm font-bold text-blue-400">URLからドキュメントを取り込む</span>
                  <button onClick={() => setShowUrlForm(false)} className="ml-auto text-slate-500 hover:text-slate-300">
                    ✕
                  </button>
                </div>
                <input
                  value={urlTitle}
                  onChange={(e) => setUrlTitle(e.target.value)}
                  placeholder="ドキュメント名（例: 嵐山観光ガイド 2026）"
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-slate-500 outline-none focus:border-blue-500/50 transition-colors"
                />
                <div className="flex gap-2">
                  <input
                    value={urlInput}
                    onChange={(e) => setUrlInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleAddUrl()}
                    placeholder="https://travel.example.com/arashiyama"
                    className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-slate-500 outline-none focus:border-blue-500/50 transition-colors"
                  />
                  <button
                    onClick={handleAddUrl}
                    disabled={urlLoading || !urlTitle.trim() || !urlInput.trim()}
                    className="px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-bold rounded-xl transition-all shadow-[0_0_12px_rgba(37,99,235,0.3)] disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {urlLoading ? '取り込み中...' : '取り込む'}
                  </button>
                </div>
                {urlError && <p className="text-xs text-red-400">{urlError}</p>}
                <p className="text-xs text-slate-500">
                  LangChain WebBaseLoaderでHTMLを取得・テキスト抽出 → ChromaDBにベクトル保存
                </p>
              </div>
            )}

            {/* ファイルアップロードゾーン */}
            <div className="border-2 border-dashed border-blue-500/22 rounded-2xl p-6 text-center bg-blue-500/[0.02] hover:bg-blue-500/[0.04] hover:border-blue-500/40 transition-all cursor-pointer">
              <div className="w-10 h-10 rounded-xl bg-blue-500/10 flex items-center justify-center mx-auto mb-3 text-blue-400">
                <Upload className="h-5 w-5" />
              </div>
              <p className="text-sm font-semibold text-white mb-1">ファイルをドロップ、またはクリックして選択</p>
              <p className="text-xs text-slate-500">PDF, TXT, MD — 最大 10MB</p>
            </div>

            {/* 凡例 */}
            <div className="flex items-center gap-3 px-1">
              <p className="text-[11px] text-slate-600 font-semibold uppercase tracking-wider">
                RAG ON/OFFで検索対象を制御
              </p>
              <div className="flex-1 h-px bg-white/5" />
              <div className="flex gap-2">
                {(['chat', 'upload', 'manual'] as const).map((s) => (
                  <SourceBadge key={s} source={s} />
                ))}
              </div>
            </div>

            {/* ドキュメント一覧 */}
            {docsLoading ? (
              <div className="space-y-2">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-16 rounded-xl bg-white/5 animate-pulse" />
                ))}
              </div>
            ) : docs.length === 0 ? (
              <div className="text-center py-16 border border-dashed border-white/6 rounded-2xl text-slate-700">
                <Database className="h-8 w-8 mx-auto mb-3 opacity-30" />
                <p className="text-sm">まだドキュメントがありません</p>
                <p className="text-xs mt-1">URLからドキュメントを取り込むか、チャットを行うと自動登録されます</p>
              </div>
            ) : (
              <div className="space-y-2">
                {docs.map((doc) => (
                  <div
                    key={doc.id}
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl border transition-all ${
                      doc.is_active
                        ? 'bg-white/[0.025] border-white/10 hover:border-white/18'
                        : 'bg-white/[0.01] border-white/5 hover:border-white/10 opacity-55'
                    }`}
                  >
                    <DocToggle
                      isActive={doc.is_active}
                      onChange={() => handleToggle(doc.id)}
                      disabled={togglingId === doc.id || doc.status !== 'vectorized'}
                    />

                    <div className={`text-sm ${doc.is_active ? 'text-blue-400' : 'text-slate-600'}`}>
                      {doc.source === 'chat'
                        ? <MessageSquare className="h-4 w-4" />
                        : <File className="h-4 w-4" />
                      }
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-0.5">
                        <span className={`text-sm font-medium truncate ${doc.is_active ? 'text-white' : 'text-slate-500'}`}>
                          {doc.title}
                        </span>
                        <SourceBadge source={doc.source} />
                      </div>
                      <p className="text-[11px] text-slate-600">
                        {doc.url && (
                          <span className="text-blue-500 mr-2">
                            <Link className="h-2.5 w-2.5 inline align-middle mr-0.5" />URL
                          </span>
                        )}
                        {doc.size && `${doc.size} · `}
                        {new Date(doc.updated_at).toLocaleDateString('ja-JP')}
                        {doc.chunks != null && (
                          <span className="ml-2">{doc.chunks} chunks</span>
                        )}
                      </p>
                    </div>

                    <StatusBadge status={doc.status} />

                    <button
                      onClick={() => handleDelete(doc.id)}
                      className="text-slate-700 hover:text-red-400 transition-colors p-1 rounded-lg hover:bg-red-500/10 flex-shrink-0"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* RAGフィルター説明 */}
            <div className="flex gap-3 items-start p-4 rounded-xl bg-blue-500/[0.04] border border-blue-500/12">
              <Info className="h-4 w-4 text-blue-400 flex-shrink-0 mt-0.5" />
              <p className="text-xs text-slate-400 leading-relaxed">
                RAGをONにしたドキュメントのみがChromaDB検索の対象になります。
                <code className="mx-1 text-[11px] bg-white/8 px-1.5 py-0.5 rounded text-indigo-300">
                  is_active=True
                </code>
                のドキュメントIDをフィルタとしてChromaDBに渡します。
              </p>
            </div>
          </div>
        )}

        {/* ── ベクトル可視化タブ ── */}
        {tab === 'vectors' && (
          <div className="grid grid-cols-[1fr_200px] gap-5">
            <div className="bg-white/[0.01] border border-white/8 rounded-2xl p-5">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">
                ベクトル空間 — t-SNE 2D投影
              </p>
              <svg width="100%" viewBox="0 0 380 280" className="block">
                {[0, 1, 2, 3, 4, 5].map((i) => (
                  <line key={`h${i}`} x1={0} y1={i * 47} x2={380} y2={i * 47} stroke="rgba(255,255,255,0.03)" strokeWidth={1} />
                ))}
                {[0, 1, 2, 3, 4, 5, 6].map((i) => (
                  <line key={`v${i}`} x1={i * 54} y1={0} x2={i * 54} y2={280} stroke="rgba(255,255,255,0.03)" strokeWidth={1} />
                ))}
                {CLUSTERS.map((cl) => (
                  <ellipse key={cl.label} cx={cl.cx} cy={cl.cy} rx={34} ry={27}
                    fill={cl.color} fillOpacity={0.06} stroke={cl.color} strokeOpacity={0.18} strokeWidth={1} />
                ))}
                {VECTOR_POINTS.map((pt, i) => (
                  <circle key={i} cx={pt.x} cy={pt.y} r={hoverPt === i ? 7 : 4.5}
                    fill={pt.color} fillOpacity={0.88}
                    stroke="#0a0a0a" strokeWidth={1}
                    className="cursor-pointer transition-all duration-100"
                    onMouseEnter={() => setHoverPt(i)}
                    onMouseLeave={() => setHoverPt(null)} />
                ))}
                {CLUSTERS.map((cl) => (
                  <text key={cl.label} x={cl.cx} y={cl.cy - 38} textAnchor="middle"
                    fill={cl.color} fontSize={11} fontWeight={700}>{cl.label}</text>
                ))}
                {hoverPt !== null && (() => {
                  const pt = VECTOR_POINTS[hoverPt]
                  return (
                    <g>
                      <rect x={pt.x + 12} y={pt.y - 22} width={50} height={18} rx={4} fill="#1e293b" stroke="rgba(255,255,255,0.1)" strokeWidth={1} />
                      <text x={pt.x + 37} y={pt.y - 9} textAnchor="middle" fill="#e2e8f0" fontSize={10}>{pt.label}</text>
                    </g>
                  )
                })()}
              </svg>
            </div>
            <div className="space-y-2">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">クラスター</p>
              {CLUSTERS.map((cl) => (
                <div key={cl.label} className="flex items-center gap-2.5 px-3 py-2.5 rounded-xl border border-white/8 bg-white/[0.02]">
                  <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: cl.color, boxShadow: `0 0 6px ${cl.color}` }} />
                  <div>
                    <p className="text-sm font-semibold text-white">{cl.label}</p>
                    <p className="text-[11px] text-slate-500">{cl.n} vectors</p>
                  </div>
                </div>
              ))}
              <div className="mt-3 p-3 rounded-xl bg-blue-500/[0.06] border border-blue-500/15 text-xs text-slate-400 leading-relaxed">
                <span className="text-blue-400 font-semibold">RAG検索</span>はクエリをベクトル化し、最も類似したクラスター内の文書を参照します。
              </div>
            </div>
          </div>
        )}

        {/* ── 検索テストタブ ── */}
        {tab === 'search' && (
          <div className="space-y-5">
            <div className="flex gap-2 items-center px-3 py-2.5 rounded-xl bg-emerald-500/[0.04] border border-emerald-500/15">
              <Database className="h-3.5 w-3.5 text-emerald-400 flex-shrink-0" />
              <p className="text-xs text-emerald-300">
                RAG ON のドキュメント:{' '}
                <strong>
                  {docs.filter((d) => d.is_active && d.status === 'vectorized').map((d) => d.title).join('・') || 'なし'}
                </strong>
              </p>
            </div>

            <div className="flex gap-2">
              <div className="flex-1 flex items-center gap-2.5 bg-white/[0.03] border border-white/10 rounded-xl px-4">
                <Search className="h-4 w-4 text-slate-500 flex-shrink-0" />
                <input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="例: 京都の混雑を避けるコツは？"
                  className="flex-1 bg-transparent text-white placeholder-slate-500 outline-none text-sm py-3"
                />
              </div>
              <button
                onClick={handleSearch}
                disabled={!query.trim() || searching}
                className="px-5 bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm rounded-xl transition-all shadow-[0_0_16px_rgba(37,99,235,0.3)] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                検索
              </button>
            </div>

            {searching && (
              <div className="flex flex-col items-center gap-3 py-12">
                <div className="flex gap-1.5">
                  <div className="h-2 w-2 animate-bounce rounded-full bg-blue-500 [animation-delay:-0.3s]" />
                  <div className="h-2 w-2 animate-bounce rounded-full bg-blue-500 [animation-delay:-0.15s]" />
                  <div className="h-2 w-2 animate-bounce rounded-full bg-blue-500" />
                </div>
                <p className="text-sm text-slate-500">ChromaDBをベクトル検索中...</p>
              </div>
            )}

            {results && !searching && (
              <div>
                <p className="text-sm text-slate-500 mb-4">
                  <span className="text-blue-400 font-bold">{results.length}</span> 件の類似チャンクが見つかりました
                </p>
                <div className="space-y-3">
                  {results.map((r, i) => (
                    <div key={i} className="p-4 rounded-2xl bg-white/[0.02] border border-white/8 hover:border-white/14 transition-colors">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <File className="h-3.5 w-3.5 text-blue-400" />
                          <span className="text-xs font-semibold text-blue-400">{r.document_title}</span>
                          <SourceBadge source={r.source} />
                        </div>
                        <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          {(r.score * 100).toFixed(0)}% 一致
                        </span>
                      </div>
                      <p className="text-sm text-slate-400 leading-relaxed">{r.chunk}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {!searching && results === null && (
              <div className="text-center py-16 border border-dashed border-white/6 rounded-2xl text-slate-700">
                <Search className="h-8 w-8 mx-auto mb-3 opacity-30" />
                <p className="text-sm">クエリを入力してRAG検索をテストできます</p>
              </div>
            )}

            {results && results.length === 0 && !searching && (
              <div className="text-center py-16 border border-dashed border-white/6 rounded-2xl text-slate-700">
                <Search className="h-8 w-8 mx-auto mb-3 opacity-30" />
                <p className="text-sm">該当するドキュメントが見つかりませんでした</p>
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  )
}
