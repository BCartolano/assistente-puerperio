import { Heart, DollarSign } from 'lucide-react'

export default function FilterBar({ filters, onFiltersChange }) {
  const handleFilterChange = (key, value) => {
    onFiltersChange(prev => ({
      ...prev,
      [key]: value,
      // Auto-ajuste: se marcar SUS, desmarca Privado e vice-versa
      ...(key === 'filterType' && value === 'SUS' ? { filterType: 'SUS' } : {}),
      ...(key === 'filterType' && value === 'PRIVATE' ? { filterType: 'PRIVATE' } : {}),
    }))
  }

  return (
    <div className="bg-white border-b border-gray-200 px-4 py-3 space-y-3">
      {/* Segregação Financeira (PM) */}
      <div className="flex items-center gap-4">
        <span className="text-sm font-medium text-gray-700 min-w-[120px]">
          Tipo de Atendimento:
        </span>
        <div className="flex gap-2">
          <button
            onClick={() => handleFilterChange('filterType', 'SUS')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 ${
              filters.filterType === 'SUS'
                ? 'bg-sus-blue text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Heart size={16} />
            SUS
          </button>
          <button
            onClick={() => handleFilterChange('filterType', 'PRIVATE')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 ${
              filters.filterType === 'PRIVATE'
                ? 'bg-private-green text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <DollarSign size={16} />
            Privado/Convênio
          </button>
          <button
            onClick={() => handleFilterChange('filterType', 'ALL')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filters.filterType === 'ALL'
                ? 'bg-gray-800 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Todos
          </button>
        </div>
      </div>

      {/* Checkbox Maternidade */}
      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="maternityOnly"
          checked={filters.maternityOnly}
          onChange={(e) => handleFilterChange('maternityOnly', e.target.checked)}
          className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
        />
        <label 
          htmlFor="maternityOnly" 
          className="text-sm font-medium text-gray-700 cursor-pointer"
        >
          Apenas Maternidades
        </label>
      </div>

      {filters.isEmergency && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-2">
          <p className="text-sm text-red-700 font-semibold">
            ⚠️ MODO EMERGÊNCIA ATIVO: Mostrando unidades mais próximas (ignorando filtros de convênio)
          </p>
        </div>
      )}
    </div>
  )
}
