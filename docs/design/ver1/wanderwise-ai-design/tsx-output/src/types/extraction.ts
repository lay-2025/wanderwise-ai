// ---------------------------------------------------------------
// 旅行データ抽出 — 共通型定義
// IMPLEMENTATION_PLAN.md の travel_extractions テーブルに対応
// ---------------------------------------------------------------

export type ExtractionCategory =
  | 'destination'
  | 'accommodation'
  | 'transportation'
  | 'food'
  | 'experience'
  | 'schedule'
  | 'budget'
  | 'tip'

// カテゴリ別 data の型
export interface DestinationData {
  name: string
  type: string
  country: string
  region?: string
}

export interface AccommodationData {
  name: string
  type: string
  location: string
}

export interface TransportationData {
  type: string
  from: string
  to: string
  duration_minutes?: number
}

export interface FoodData {
  name: string
  type: string
  location: string
}

export interface ExperienceData {
  name: string
  type: string
  location: string
}

export interface ScheduleData {
  start: string
  end: string
  duration_days: number
  season?: string
}

export interface BudgetData {
  amount: number
  currency: string
  type: string
}

export interface TipData {
  content: string
  target: string
}

export type ExtractionData =
  | DestinationData
  | AccommodationData
  | TransportationData
  | FoodData
  | ExperienceData
  | ScheduleData
  | BudgetData
  | TipData

// APIレスポンスの抽出アイテム
export interface TravelExtraction {
  id: string
  message_id: string
  session_id: string
  category: ExtractionCategory
  data: ExtractionData
  confidence: number
  created_at: string
}

// カテゴリ表示メタデータ
export interface CategoryMeta {
  label: string
  color: string
  bgColor: string        // Tailwind bg class
  borderColor: string    // Tailwind border class
  textColor: string      // Tailwind text class
  badgeBg: string        // Tailwind badge bg class
}

export const CATEGORY_META: Record<ExtractionCategory, CategoryMeta> = {
  destination:   { label: '旅行先', color: '#3b82f6', bgColor: 'bg-blue-500/10',    borderColor: 'border-blue-500/20',   textColor: 'text-blue-400',   badgeBg: 'bg-blue-500/15' },
  accommodation: { label: '宿泊',   color: '#8b5cf6', bgColor: 'bg-violet-500/10',  borderColor: 'border-violet-500/20', textColor: 'text-violet-400', badgeBg: 'bg-violet-500/15' },
  transportation:{ label: '交通',   color: '#06b6d4', bgColor: 'bg-cyan-500/10',    borderColor: 'border-cyan-500/20',   textColor: 'text-cyan-400',   badgeBg: 'bg-cyan-500/15' },
  food:          { label: 'グルメ', color: '#f59e0b', bgColor: 'bg-amber-500/10',   borderColor: 'border-amber-500/20',  textColor: 'text-amber-400',  badgeBg: 'bg-amber-500/15' },
  experience:    { label: '体験',   color: '#10b981', bgColor: 'bg-emerald-500/10', borderColor: 'border-emerald-500/20',textColor: 'text-emerald-400',badgeBg: 'bg-emerald-500/15' },
  schedule:      { label: '日程',   color: '#ec4899', bgColor: 'bg-pink-500/10',    borderColor: 'border-pink-500/20',   textColor: 'text-pink-400',   badgeBg: 'bg-pink-500/15' },
  budget:        { label: '予算',   color: '#f97316', bgColor: 'bg-orange-500/10',  borderColor: 'border-orange-500/20', textColor: 'text-orange-400', badgeBg: 'bg-orange-500/15' },
  tip:           { label: 'コツ',   color: '#a78bfa', bgColor: 'bg-purple-400/10',  borderColor: 'border-purple-400/20', textColor: 'text-purple-300', badgeBg: 'bg-purple-400/15' },
}

/** data から表示用の短いテキストを生成 */
export function formatExtractionData(category: ExtractionCategory, data: ExtractionData): string {
  switch (category) {
    case 'destination': {
      const d = data as DestinationData
      return [d.name, d.region, d.country].filter(Boolean).join(' · ')
    }
    case 'accommodation': {
      const d = data as AccommodationData
      return [d.name, d.location].filter(Boolean).join(' · ')
    }
    case 'transportation': {
      const d = data as TransportationData
      return `${d.type} ${d.from}→${d.to}`
    }
    case 'food': {
      const d = data as FoodData
      return [d.name, d.location].filter(Boolean).join(' · ')
    }
    case 'experience': {
      const d = data as ExperienceData
      return [d.name, d.location].filter(Boolean).join(' · ')
    }
    case 'schedule': {
      const d = data as ScheduleData
      return `${d.start} 〜 ${d.end}（${d.duration_days}泊）`
    }
    case 'budget': {
      const d = data as BudgetData
      return `¥${d.amount.toLocaleString()} (${d.type})`
    }
    case 'tip': {
      const d = data as TipData
      const text = d.content
      return text.length > 40 ? text.slice(0, 40) + '…' : text
    }
    default:
      return JSON.stringify(data).slice(0, 50)
  }
}
