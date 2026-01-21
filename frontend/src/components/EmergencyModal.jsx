import { AlertTriangle, Phone, Navigation } from 'lucide-react'

export default function EmergencyModal({ isOpen, onConfirm, onCancel }) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="bg-panic-red rounded-full p-2">
            <AlertTriangle className="text-white" size={24} />
          </div>
          <h2 className="text-xl font-bold text-gray-900">
            Emergência Médica
          </h2>
        </div>

        <div className="space-y-4">
          <p className="text-gray-700 leading-relaxed">
            Você está em uma <strong className="text-red-600">situação de emergência médica</strong>?
            (sangramento intenso, desmaio, dor extrema, convulsão)
          </p>

          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-sm text-red-800 font-semibold mb-2">
              ⚠️ IMPORTANTE:
            </p>
            <ul className="text-sm text-red-700 space-y-1 list-disc list-inside">
              <li>O sistema mostrará as unidades mais próximas</li>
              <li>Filtros de convênio serão ignorados</li>
              <li>Em risco imediato, ligue <strong>192</strong> ou vá ao PS mais próximo</li>
            </ul>
          </div>

          <div className="flex gap-3 pt-2">
            <button
              onClick={onConfirm}
              className="flex-1 bg-panic-red text-white px-4 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 hover:bg-red-700 transition-colors"
            >
              <Navigation size={20} />
              Sim, preciso de ajuda AGORA
            </button>
            <button
              onClick={onCancel}
              className="px-4 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
            >
              Cancelar
            </button>
          </div>

          <div className="border-t pt-4">
            <a
              href="tel:192"
              className="flex items-center justify-center gap-2 text-panic-red font-semibold hover:text-red-700 transition-colors"
            >
              <Phone size={20} />
              Ligar 192 (SAMU)
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
