'use client'

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from 'react'
import { useRouter } from 'next/navigation'
import {
  Session,
  getSessions,
  createSession,
  deleteSession as apiDeleteSession,
  renameSession as apiRenameSession,
} from '@/lib/api'

interface SessionContextType {
  sessions: Session[]
  sessionsLoading: boolean
  loadSessions: () => Promise<void>
  createNewSession: () => Promise<void>
  removeSession: (id: string, currentSessionId: string) => Promise<void>
  renameSessionItem: (id: string, title: string) => Promise<void>
}

const SessionContext = createContext<SessionContextType | null>(null)

export function SessionProvider({ children }: { children: ReactNode }) {
  const [sessions, setSessions] = useState<Session[]>([])
  const [sessionsLoading, setSessionsLoading] = useState(true)
  const router = useRouter()

  const loadSessions = useCallback(async () => {
    try {
      const data = await getSessions()
      setSessions(data.sessions)
    } catch {
      // 認証エラー等はプロキシが処理
    } finally {
      setSessionsLoading(false)
    }
  }, [])

  useEffect(() => {
    loadSessions()
  }, [loadSessions])

  const createNewSession = async () => {
    const session = await createSession()
    await loadSessions()
    router.push(`/chat/${session.id}`)
  }

  const removeSession = async (id: string, currentSessionId: string) => {
    await apiDeleteSession(id)
    const updated = sessions.filter((s) => s.id !== id)
    setSessions(updated)
    if (currentSessionId === id) {
      if (updated.length > 0) {
        router.push(`/chat/${updated[0].id}`)
      } else {
        const newSession = await createSession()
        await loadSessions()
        router.push(`/chat/${newSession.id}`)
      }
    }
  }

  const renameSessionItem = async (id: string, title: string) => {
    await apiRenameSession(id, title)
    setSessions((prev) =>
      prev.map((s) => (s.id === id ? { ...s, title } : s)),
    )
  }

  return (
    <SessionContext.Provider
      value={{
        sessions,
        sessionsLoading,
        loadSessions,
        createNewSession,
        removeSession,
        renameSessionItem,
      }}
    >
      {children}
    </SessionContext.Provider>
  )
}

export function useSession() {
  const ctx = useContext(SessionContext)
  if (!ctx) throw new Error('useSession must be used within SessionProvider')
  return ctx
}
