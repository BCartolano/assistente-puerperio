import { AlertTriangle, X } from 'lucide-react'
import { useState } from 'react'

export default function LegalDisclaimer({ text }) {
  const [isVisible, setIsVisible] = useState(true)

  if (!isVisible || !text) return null

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-red-600 text-white p-4 shadow-lg z-50 border-t-4 border-red-800">
      <div className="max-w-7xl mx-auto relative">
        <button
          onClick={() => setIsVisible(false)}
          className="absolute top-0 right-0 text-white hover:text-red-200 transition-colors"
          aria-label="Fechar aviso"
        >
          <X size={20} />
        </button>
        
        <div className="flex items-start gap-3 pr-8">
          <AlertTriangle size={24} className="flex-shrink-0 mt-0.5" />
          <p className="text-sm leading-relaxed">
            {text}
          </p>
        </div>
      </div>
    </div>
  )
}
