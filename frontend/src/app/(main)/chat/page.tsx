'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { getSessions, createSession } from '@/lib/api'

export default function ChatIndexPage() {
  const router = useRouter()

  useEffect(() => {
    const init = async () => {
      try {
        const { sessions } = await getSessions()
        if (sessions.length > 0) {
          router.replace(`/chat/${sessions[0].id}`)
        } else {
          const session = await createSession()
          router.replace(`/chat/${session.id}`)
        }
      } catch {
        // 認証エラーはプロキシが /login へリダイレクト
      }
    }
    init()
  }, [router])

  return (
    <div className="flex-1 flex items-center justify-center h-full">
      <div className="flex gap-1.5">
        <div className="h-2 w-2 animate-bounce rounded-full bg-blue-500 [animation-delay:-0.3s]" />
        <div className="h-2 w-2 animate-bounce rounded-full bg-blue-500 [animation-delay:-0.15s]" />
        <div className="h-2 w-2 animate-bounce rounded-full bg-blue-500" />
      </div>
    </div>
  )
}
