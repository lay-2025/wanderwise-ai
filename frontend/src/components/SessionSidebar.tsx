'use client'

import { useState, useRef, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Plus, Trash2, Pencil, Check, X, MessageSquare } from 'lucide-react'
import { useSession } from '@/context/SessionContext'
import { Session } from '@/lib/api'

// ---------------------------------------------------------------
// 日付グルーピング
// ---------------------------------------------------------------

type Group = { label: string; sessions: Session[] }

function groupSessions(sessions: Session[]): Group[] {
  const now = new Date()
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const startOfYesterday = new Date(startOfToday.getTime() - 86400000)
  const startOf7Days = new Date(startOfToday.getTime() - 6 * 86400000)
  const startOf30Days = new Date(startOfToday.getTime() - 29 * 86400000)

  const groups: Group[] = [
    { label: '今日', sessions: [] },
    { label: '昨日', sessions: [] },
    { label: '過去 7 日', sessions: [] },
    { label: '過去 30 日', sessions: [] },
    { label: 'それ以前', sessions: [] },
  ]

  for (const s of sessions) {
    const d = new Date(s.updated_at)
    if (d >= startOfToday) groups[0].sessions.push(s)
    else if (d >= startOfYesterday) groups[1].sessions.push(s)
    else if (d >= startOf7Days) groups[2].sessions.push(s)
    else if (d >= startOf30Days) groups[3].sessions.push(s)
    else groups[4].sessions.push(s)
  }

  return groups.filter((g) => g.sessions.length > 0)
}

// ---------------------------------------------------------------
// 個別セッションアイテム
// ---------------------------------------------------------------

function SessionItem({
  session,
  isActive,
}: {
  session: Session
  isActive: boolean
}) {
  const { removeSession, renameSessionItem } = useSession()
  const { sessionId } = useParams<{ sessionId: string }>()
  const router = useRouter()

  const [isEditing, setIsEditing] = useState(false)
  const [editTitle, setEditTitle] = useState(session.title ?? '')
  const [showActions, setShowActions] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (isEditing) inputRef.current?.focus()
  }, [isEditing])

  const displayTitle = session.title ?? '新しいチャット'

  const handleRenameCommit = async () => {
    const trimmed = editTitle.trim()
    if (trimmed && trimmed !== (session.title ?? '')) {
      await renameSessionItem(session.id, trimmed)
    }
    setIsEditing(false)
  }

  const handleRenameKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleRenameCommit()
    if (e.key === 'Escape') {
      setEditTitle(session.title ?? '')
      setIsEditing(false)
    }
  }

  const handleDelete = async () => {
    if (!confirmDelete) {
      setConfirmDelete(true)
      return
    }
    await removeSession(session.id, sessionId ?? '')
  }

  return (
    <div
      className={`group relative flex items-center gap-2 rounded-lg px-3 py-2 cursor-pointer transition-colors ${
        isActive
          ? 'bg-white/10 text-white'
          : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'
      }`}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => {
        setShowActions(false)
        setConfirmDelete(false)
      }}
      onClick={() => {
        if (!isEditing) router.push(`/chat/${session.id}`)
      }}
    >
      <MessageSquare className="h-4 w-4 flex-shrink-0 opacity-60" />

      {isEditing ? (
        <input
          ref={inputRef}
          value={editTitle}
          onChange={(e) => setEditTitle(e.target.value)}
          onKeyDown={handleRenameKeyDown}
          onBlur={handleRenameCommit}
          onClick={(e) => e.stopPropagation()}
          className="flex-1 bg-transparent text-sm text-white outline-none border-b border-blue-500"
        />
      ) : (
        <span className="flex-1 truncate text-sm">{displayTitle}</span>
      )}

      {(showActions || isEditing) && !isEditing && (
        <div
          className="flex items-center gap-1"
          onClick={(e) => e.stopPropagation()}
        >
          <button
            onClick={() => {
              setEditTitle(session.title ?? '')
              setIsEditing(true)
            }}
            className="p-1 rounded hover:bg-white/10 text-slate-500 hover:text-slate-200"
            title="名前を変更"
          >
            <Pencil className="h-3.5 w-3.5" />
          </button>
          <button
            onClick={handleDelete}
            className={`p-1 rounded hover:bg-white/10 ${
              confirmDelete ? 'text-red-400' : 'text-slate-500 hover:text-red-400'
            }`}
            title={confirmDelete ? 'クリックして確認' : '削除'}
          >
            <Trash2 className="h-3.5 w-3.5" />
          </button>
        </div>
      )}

      {isEditing && (
        <div
          className="flex items-center gap-1"
          onClick={(e) => e.stopPropagation()}
        >
          <button
            onClick={handleRenameCommit}
            className="p-1 rounded hover:bg-white/10 text-green-400"
          >
            <Check className="h-3.5 w-3.5" />
          </button>
          <button
            onClick={() => {
              setEditTitle(session.title ?? '')
              setIsEditing(false)
            }}
            className="p-1 rounded hover:bg-white/10 text-slate-400"
          >
            <X className="h-3.5 w-3.5" />
          </button>
        </div>
      )}
    </div>
  )
}

// ---------------------------------------------------------------
// サイドバー本体
// ---------------------------------------------------------------

export default function SessionSidebar() {
  const { sessions, sessionsLoading, createNewSession } = useSession()
  const { sessionId } = useParams<{ sessionId: string }>()

  const groups = groupSessions(sessions)

  return (
    <aside className="flex flex-col w-64 h-full bg-[#0d0d0d] border-r border-white/5 flex-shrink-0">
      {/* 新規チャットボタン */}
      <div className="p-3 border-b border-white/5">
        <button
          onClick={createNewSession}
          className="flex items-center gap-2 w-full rounded-lg px-3 py-2.5 text-sm text-slate-300 hover:bg-white/5 hover:text-white transition-colors border border-white/10 hover:border-white/20"
        >
          <Plus className="h-4 w-4" />
          新しいチャット
        </button>
      </div>

      {/* セッション一覧 */}
      <div className="flex-1 overflow-y-auto p-2 space-y-4">
        {sessionsLoading ? (
          <div className="space-y-2 p-2">
            {[...Array(4)].map((_, i) => (
              <div
                key={i}
                className="h-8 rounded-lg bg-white/5 animate-pulse"
              />
            ))}
          </div>
        ) : groups.length === 0 ? (
          <p className="text-xs text-slate-600 text-center pt-4">
            チャット履歴はありません
          </p>
        ) : (
          groups.map((group) => (
            <div key={group.label}>
              <p className="px-3 pb-1 text-xs font-medium text-slate-600 uppercase tracking-wider">
                {group.label}
              </p>
              <div className="space-y-0.5">
                {group.sessions.map((s) => (
                  <SessionItem
                    key={s.id}
                    session={s}
                    isActive={s.id === sessionId}
                  />
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </aside>
  )
}
