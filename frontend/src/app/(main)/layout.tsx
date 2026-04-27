import Header from '@/components/Header'
import { AuthProvider } from '@/context/AuthContext'

export default function MainLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <Header />
      <main className="flex-1 mt-16 flex flex-col">
        {children}
      </main>
    </AuthProvider>
  )
}
