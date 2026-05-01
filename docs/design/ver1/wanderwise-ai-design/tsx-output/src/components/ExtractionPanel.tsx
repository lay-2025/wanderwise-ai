import { TravelExtraction, ExtractionCategory, CATEGORY_META, formatExtractionData } from '@/types/extraction'

interface ExtractionPanelProps {
  extractions: TravelExtraction[]
}

/**
 * チャット画面右パネル — セッションの全抽出データをカテゴリ別に表示
 * chat/layout.tsx または chat/[sessionId]/page.tsx からマウントする
 */
export default function ExtractionPanel({ extractions }: ExtractionPanelProps) {
  if (extractions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-3 text-slate-600 px-4 py-12">
        <svg
          className="w-8 h-8 opacity-30"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={1.5}
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z" />
        </svg>
        <p className="text-xs text-center leading-relaxed">
          会話から旅行データを<br />自動抽出します
        </p>
      </div>
    )
  }

  // カテゴリ別にグループ化
  const byCategory = extractions.reduce<Record<ExtractionCategory, TravelExtraction[]>>(
    (acc, ex) => {
      if (!acc[ex.category]) acc[ex.category] = []
      acc[ex.category].push(ex)
      return acc
    },
    {} as Record<ExtractionCategory, TravelExtraction[]>
  )

  return (
    <div className="flex flex-col gap-2.5 p-2">
      {(Object.entries(byCategory) as [ExtractionCategory, TravelExtraction[]][]).map(
        ([category, items]) => {
          const meta = CATEGORY_META[category]
          return (
            <div
              key={category}
              className={`rounded-xl overflow-hidden border ${meta.borderColor} animate-in fade-in slide-in-from-right-2 duration-300`}
            >
              {/* カテゴリヘッダー */}
              <div className={`flex items-center gap-2 px-3 py-2 ${meta.bgColor}`}>
                <span className={`text-[11px] font-bold uppercase tracking-wide ${meta.textColor}`}>
                  {meta.label}
                </span>
                <span className={`ml-auto text-[10px] ${meta.textColor} opacity-60`}>
                  {items[0].confidence >= 0.9
                    ? '高信頼度'
                    : items[0].confidence >= 0.8
                    ? '中信頼度'
                    : '低信頼度'}
                </span>
              </div>

              {/* アイテム一覧 */}
              {items.map((ex) => (
                <div
                  key={ex.id}
                  className="px-3 py-2 border-t border-white/5 bg-black/30"
                >
                  <p className="text-xs text-slate-400 leading-relaxed">
                    {formatExtractionData(ex.category, ex.data)}
                  </p>
                  <p className="text-[10px] text-slate-600 mt-1">
                    信頼度 {Math.round(ex.confidence * 100)}%
                  </p>
                </div>
              ))}
            </div>
          )
        }
      )}
    </div>
  )
}
