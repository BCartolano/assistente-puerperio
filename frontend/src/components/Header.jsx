import { AlertTriangle } from 'lucide-react'

export default function Header({ onEmergencyClick }) {
  return (
    <header className="bg-white shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900">
              🏥 Localizador Puerperal
            </h1>
            <p className="text-xs text-gray-500 mt-0.5">
              Encontre hospitais e maternidades próximas
            </p>
          </div>
          
          <button
            onClick={onEmergencyClick}
            className="panic-button bg-panic-red text-white px-4 py-2.5 rounded-lg font-semibold text-sm flex items-center gap-2 shadow-lg hover:bg-red-700 transition-colors"
          >
            <AlertTriangle size={20} />
            <span className="hidden sm:inline">EMERGÊNCIA</span>
            <span className="sm:hidden">192</span>
          </button>
        </div>
      </div>
    </header>
  )
}
