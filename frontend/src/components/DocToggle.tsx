'use client'

interface DocToggleProps {
  isActive: boolean
  onChange: (next: boolean) => void
  disabled?: boolean
}

export default function DocToggle({ isActive, onChange, disabled = false }: DocToggleProps) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={isActive}
      disabled={disabled}
      onClick={() => onChange(!isActive)}
      className={`
        relative inline-flex h-5 w-9 flex-shrink-0 rounded-full border transition-all duration-200
        focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:ring-offset-1 focus:ring-offset-black
        ${isActive
          ? 'bg-blue-600 border-blue-500 shadow-[0_0_8px_rgba(37,99,235,0.4)]'
          : 'bg-white/10 border-white/10'
        }
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
      `}
    >
      <span
        className={`
          pointer-events-none inline-block h-3.5 w-3.5 rounded-full bg-white shadow
          transform transition-transform duration-200 mt-[2px]
          ${isActive ? 'translate-x-[18px]' : 'translate-x-[2px]'}
        `}
      />
    </button>
  )
}
