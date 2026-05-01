import { AuthProvider } from '@/context/AuthContext'
import Header from '@/components/Header'

export default function LearningLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <Header />
      <main className="flex-1 mt-16 flex flex-col">
        {children}
      </main>
    </AuthProvider>
  )
}
