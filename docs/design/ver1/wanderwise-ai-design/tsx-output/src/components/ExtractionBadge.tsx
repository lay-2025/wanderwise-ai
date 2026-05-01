import { TravelExtraction, CATEGORY_META, formatExtractionData } from '@/types/extraction'

interface ExtractionBadgeProps {
  extraction: TravelExtraction
}

/**
 * チャットメッセージ下に表示するカテゴリバッジ（小サイズ）
 * 使用例: AIメッセージの extractions をマップして並べる
 */
export default function ExtractionBadge({ extraction }: ExtractionBadgeProps) {
  const meta = CATEGORY_META[extraction.category]
  const displayText = formatExtractionData(extraction.category, extraction.data)

  return (
    <span
      className={`
        inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium
        ${meta.badgeBg} ${meta.textColor} border ${meta.borderColor}
        animate-in fade-in zoom-in-75 duration-200
      `}
      title={`${meta.label}: ${displayText} (信頼度 ${Math.round(extraction.confidence * 100)}%)`}
    >
      <span className="font-bold">{meta.label}</span>
      <span className="opacity-70 max-w-[80px] truncate">{displayText}</span>
    </span>
  )
}
