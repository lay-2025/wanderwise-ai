'use client'

import Link from 'next/link'
import { Brain, LogOut, User } from 'lucide-react'
import { useAuth } from '@/context/AuthContext'

export default function Header() {
  const { user, logout } = useAuth()

  return (
    <header className="fixed top-0 w-full border-b border-white/10 bg-[#0a0a0a]/80 backdrop-blur-md z-50">
      <div className="container mx-auto px-6 h-16 flex items-center justify-between max-w-7xl">
        <Link href="/" className="flex items-center gap-2 text-white hover:text-blue-400 transition-colors">
          <Brain className="h-6 w-6 text-blue-500" />
          <span className="font-semibold text-lg tracking-wide">Travel Chat Assistant</span>
        </Link>
        <nav className="flex items-center gap-6 text-sm font-medium text-slate-300">
          <Link href="/chat" className="hover:text-white transition-colors">
            チャット
          </Link>
          <Link href="/learning" className="hover:text-white transition-colors">
            学習管理
          </Link>
          {user && (
            <div className="flex items-center gap-4 border-l border-white/10 pl-6">
              <div className="flex items-center gap-1.5 text-slate-400">
                <User className="h-4 w-4" />
                <span className="text-slate-200">{user.name}</span>
              </div>
              <button
                onClick={logout}
                className="flex items-center gap-1.5 text-slate-400 hover:text-white transition-colors"
              >
                <LogOut className="h-4 w-4" />
                <span>ログアウト</span>
              </button>
            </div>
          )}
        </nav>
      </div>
    </header>
  )
}
