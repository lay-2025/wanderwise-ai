'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { User, getMe, logout as apiLogout } from '@/lib/api'

interface AuthContextType {
  user: User | null
  loading: boolean
  logout: () => Promise<void>
  setUser: (user: User | null) => void
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getMe().then((u) => {
      setUser(u)
      setLoading(false)
    })
  }, [])

  const logout = async () => {
    await apiLogout()
    setUser(null)
    window.location.href = '/login'
  }

  return (
    <AuthContext.Provider value={{ user, loading, logout, setUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
