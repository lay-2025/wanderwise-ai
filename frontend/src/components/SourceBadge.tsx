import type { DocumentSource } from '@/lib/api'

interface SourceBadgeProps {
  source: DocumentSource
}

const SOURCE_META: Record<DocumentSource, { label: string; className: string }> = {
  chat:   { label: 'chat',   className: 'bg-violet-500/10 text-violet-400 border-violet-500/20' },
  upload: { label: 'upload', className: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20' },
  manual: { label: 'manual', className: 'bg-amber-500/10 text-amber-400 border-amber-500/20' },
}

export default function SourceBadge({ source }: SourceBadgeProps) {
  const meta = SOURCE_META[source] ?? SOURCE_META.manual
  return (
    <span
      className={`
        inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold
        uppercase tracking-wider border ${meta.className}
      `}
    >
      {meta.label}
    </span>
  )
}
