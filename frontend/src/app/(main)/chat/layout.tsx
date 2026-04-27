import { SessionProvider } from '@/context/SessionContext'
import SessionSidebar from '@/components/SessionSidebar'

export default function ChatLayout({ children }: { children: React.ReactNode }) {
  return (
    <SessionProvider>
      <div className="flex h-[calc(100vh-4rem)] overflow-hidden">
        <SessionSidebar />
        <div className="flex-1 overflow-hidden">
          {children}
        </div>
      </div>
    </SessionProvider>
  )
}
