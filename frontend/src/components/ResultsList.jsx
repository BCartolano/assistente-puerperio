import { MapPin, Phone, Navigation, AlertTriangle, Heart, DollarSign } from 'lucide-react'

export default function ResultsList({ facilities }) {
  const getCardColorClasses = (facility) => {
    if (facility.tags.emergency_only) {
      return 'border-l-4 border-emergency-yellow bg-yellow-50'
    } else if (facility.tags.sus) {
      return 'border-l-4 border-sus-blue bg-blue-50'
    } else {
      return 'border-l-4 border-private-green bg-green-50'
    }
  }

  const getBadgeColor = (badge) => {
    if (badge.includes('SUS')) return 'bg-sus-blue text-white'
    if (badge.includes('MATERNIDADE')) return 'bg-pink-600 text-white'
    if (badge.includes('PRIVADO')) return 'bg-private-green text-white'
    if (badge.includes('EMERGÊNCIA')) return 'bg-emergency-yellow text-black'
    return 'bg-gray-600 text-white'
  }

  const handleNavigate = (facility) => {
    if (facility.lat && facility.long) {
      const url = `https://www.google.com/maps/dir/?api=1&destination=${facility.lat},${facility.long}`
      window.open(url, '_blank')
    }
  }

  const handleCall = (phone) => {
    if (phone) {
      window.location.href = `tel:${phone}`
    }
  }

  if (facilities.length === 0) {
    return null
  }

  return (
    <div className="bg-gray-50 border-t border-gray-200 max-h-96 overflow-y-auto scroll-smooth">
      <div className="max-w-7xl mx-auto px-4 py-4 space-y-3">
        <h2 className="text-lg font-semibold text-gray-900 mb-2">
          Resultados ({facilities.length})
        </h2>
        
        {facilities.map((facility) => (
          <div
            key={facility.id}
            className={`${getCardColorClasses(facility)} rounded-lg p-4 shadow-sm`}
          >
            {/* Nome e Tipo */}
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900 text-base mb-1">
                  {facility.fantasy_name || facility.name}
                </h3>
                <p className="text-xs text-gray-600 uppercase">{facility.type}</p>
              </div>
              
              {/* Distância */}
              <div className="text-right">
                <p className="text-lg font-bold text-gray-900">
                  {facility.distance_km.toFixed(1)} km
                </p>
                <p className="text-xs text-gray-500">distância</p>
              </div>
            </div>

            {/* Badges */}
            {facility.badges.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mb-3">
                {facility.badges.map((badge, i) => (
                  <span
                    key={i}
                    className={`${getBadgeColor(badge)} text-xs font-medium px-2 py-1 rounded-full`}
                  >
                    {badge}
                  </span>
                ))}
              </div>
            )}

            {/* Tags visuais */}
            <div className="flex items-center gap-3 mb-3 text-sm">
              {facility.tags.sus && (
                <div className="flex items-center gap-1 text-sus-blue">
                  <Heart size={14} />
                  <span className="font-medium">SUS</span>
                </div>
              )}
              {facility.tags.private && (
                <div className="flex items-center gap-1 text-private-green">
                  <DollarSign size={14} />
                  <span className="font-medium">Privado</span>
                </div>
              )}
              {facility.tags.maternity && (
                <span className="text-pink-600 font-medium">👶 Maternidade</span>
              )}
            </div>

            {/* Endereço */}
            {facility.address && (
              <div className="flex items-start gap-2 mb-3 text-sm text-gray-600">
                <MapPin size={16} className="mt-0.5 flex-shrink-0" />
                <span>{facility.address}</span>
              </div>
            )}

            {/* Warning Message (UX Expert) */}
            {facility.warning_message && (
              <div className="bg-red-100 border border-red-300 rounded p-2 mb-3">
                <div className="flex items-start gap-2">
                  <AlertTriangle size={16} className="text-red-600 mt-0.5 flex-shrink-0" />
                  <p className="text-xs text-red-700">{facility.warning_message}</p>
                </div>
              </div>
            )}

            {/* Ações */}
            <div className="flex gap-2 mt-3">
              {facility.lat && facility.long && (
                <button
                  onClick={() => handleNavigate(facility)}
                  className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg font-medium text-sm flex items-center justify-center gap-2 hover:bg-blue-700 transition-colors"
                >
                  <Navigation size={18} />
                  Navegar (Google Maps)
                </button>
              )}
              
              {facility.phone && (
                <button
                  onClick={() => handleCall(facility.phone)}
                  className="bg-green-600 text-white px-4 py-2 rounded-lg font-medium text-sm flex items-center justify-center gap-2 hover:bg-green-700 transition-colors"
                >
                  <Phone size={18} />
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
