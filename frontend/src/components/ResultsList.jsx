import { MapPin, Phone, Navigation, AlertTriangle, Heart, DollarSign, Syringe, Building2, Info } from 'lucide-react'

export default function ResultsList({ facilities }) {
  // Filtro de segurança: ocultar cards com nomes problemáticos que passaram pelo backend
  const shouldHideCard = (facility) => {
    const name = (facility.display_name || facility.fantasy_name || facility.name || '').toLowerCase()
    const blacklistTerms = [
      'drogaria', 'farma', 'farmácia', 'farmácias',
      'removale', 'ambulância', 'ambulancia',
      'transporte médico', 'clínica estética', 'estética'
    ]
    return blacklistTerms.some(term => name.includes(term))
  }

  const getCardColorClasses = (facility) => {
    // REGRA UX: Cores diferenciadas por tipo
    // HOSPITAL/UPA: Vermelho/Laranja (emergência)
    if (facility.isHospital || facility.type === 'UPA') {
      return 'border-l-4 border-red-500 bg-red-50'
    }
    // UBS/POSTO: Verde/Azul (atenção básica)
    if (facility.isVaccinationPoint || facility.type === 'UBS') {
      return 'border-l-4 border-blue-500 bg-blue-50'
    }
    // Fallback
    if (facility.tags.emergency_only) {
      return 'border-l-4 border-emergency-yellow bg-yellow-50'
    } else if (facility.tags.sus) {
      return 'border-l-4 border-sus-blue bg-blue-50'
    } else {
      return 'border-l-4 border-private-green bg-green-50'
    }
  }

  const getBadgeColor = (badge) => {
    const badgeUpper = badge.toUpperCase()
    if (badgeUpper.includes('SUS') || badgeUpper.includes('PÚBLICO') || badgeUpper.includes('PUBLICO')) return 'bg-sus-blue text-white'
    if (badgeUpper.includes('MATERNIDADE')) return 'bg-pink-600 text-white'
    if (badgeUpper.includes('PRIVADO')) return 'bg-amber-400 text-gray-900'
    if (badgeUpper.includes('EMERGÊNCIA') || badgeUpper.includes('EMERGENCIA')) return 'bg-emergency-yellow text-black'
    if (badgeUpper.includes('VACINA')) return 'bg-blue-500 text-white'
    return 'bg-gray-600 text-white'
  }

  const handleNavigate = (facility) => {
    const name = facility.display_name || facility.fantasy_name || facility.name || ''
    const address = facility.address || ''
    const full = [name, address].filter(Boolean).join(' ').trim()
    if (full) {
      const url = `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(full)}`
      window.open(url, '_blank')
    } else if (facility.lat && facility.long) {
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
        
        {facilities
          .filter(facility => !shouldHideCard(facility)) // Filtro de segurança no frontend
          .map((facility) => (
          <div
            key={facility.id}
            className={`${getCardColorClasses(facility)} rounded-lg p-4 shadow-sm`}
          >
            {/* Nome e Tipo */}
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  {/* Ícones diferenciados por tipo */}
                  {facility.isHospital || facility.type === 'UPA' ? (
                    <span className="text-2xl">🏥</span>
                  ) : facility.isVaccinationPoint || facility.type === 'UBS' ? (
                    <span className="text-2xl">💉</span>
                  ) : null}
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 text-base">
                      {facility.display_name || facility.fantasy_name || facility.name}
                    </h3>
                    {/* Subtítulo: Nome de pessoa/homenagem */}
                    {facility.display_subtitle && (
                      <p className="text-xs text-gray-500 mt-0.5 italic">
                        {facility.display_subtitle}
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2 mt-1">
                  <p className="text-xs text-gray-600 uppercase">{facility.type}</p>
                  {/* Texto de destaque por tipo */}
                  {facility.isHospital || facility.type === 'UPA' ? (
                    <span className="text-xs font-bold text-red-600">PRONTO SOCORRO / EMERGÊNCIA</span>
                  ) : facility.isVaccinationPoint || facility.type === 'UBS' ? (
                    <span className="text-xs font-bold text-blue-600">ATENÇÃO BÁSICA / VACINAÇÃO</span>
                  ) : null}
                </div>
              </div>
              
              {/* Distância com "Aprox." e tooltip */}
              <div className="text-right">
                <div className="flex items-center gap-1 justify-end">
                  <p className="text-lg font-bold text-gray-900">
                    Aprox. {facility.distance_km.toFixed(1)} km
                  </p>
                  {facility.distance_type === 'linear' && (
                    <div className="group relative">
                      <Info size={14} className="text-gray-400 cursor-help" />
                      <div className="absolute right-0 top-6 w-48 p-2 bg-gray-800 text-white text-xs rounded shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                        Distância em linha reta. Considere o trânsito ao planejar o trajeto.
                      </div>
                    </div>
                  )}
                </div>
                <p className="text-xs text-gray-500">distância</p>
              </div>
            </div>

            {/* Badges */}
            <div className="flex flex-wrap gap-1.5 mb-3">
              {/* Badge de Vacinação - Prioridade Visual */}
              {facility.isVaccinationPoint && (
                <span className="bg-blue-500 text-white text-xs font-medium px-2 py-1 rounded-full flex items-center gap-1">
                  <Syringe size={12} />
                  Ponto de Vacinação
                </span>
              )}
              
              {/* Badge de Hospital - Destaque */}
              {facility.isHospital && (
                <span className="bg-red-600 text-white text-xs font-medium px-2 py-1 rounded-full flex items-center gap-1">
                  <Building2 size={12} />
                  Hospital
                </span>
              )}
              
              {/* Outros badges - Filtrado para evitar duplicatas */}
              {facility.badges.length > 0 && (() => {
                // Filtrar badges duplicados: apenas um de emergência e um de SUS
                const seenBadges = new Set();
                const filteredBadges = [];
                let hasEmergencyBadge = false;
                let hasSusBadge = false;
                
                facility.badges.forEach((badge) => {
                  const badgeUpper = badge.toUpperCase();
                  
                  // Badge de Emergência (apenas um)
                  if ((badgeUpper.includes('EMERGÊNCIA') || badgeUpper.includes('EMERGENCIA')) && !hasEmergencyBadge) {
                    filteredBadges.push('EMERGÊNCIA');
                    hasEmergencyBadge = true;
                  }
                  // Badge SUS/Público (apenas um, unificado)
                  else if ((badgeUpper.includes('SUS') || badgeUpper.includes('PÚBLICO') || badgeUpper.includes('PUBLICO')) && !hasSusBadge) {
                    filteredBadges.push('ACEITA SUS/PÚBLICO');
                    hasSusBadge = true;
                  }
                  // Outros badges (maternidade, privado, etc) - sem duplicatas
                  else if (!badgeUpper.includes('SUS') && !badgeUpper.includes('PÚBLICO') && !badgeUpper.includes('PUBLICO') && !badgeUpper.includes('EMERGÊNCIA') && !badgeUpper.includes('EMERGENCIA')) {
                    if (!seenBadges.has(badgeUpper)) {
                      filteredBadges.push(badge);
                      seenBadges.add(badgeUpper);
                    }
                  }
                });
                
                return filteredBadges.length > 0 ? (
                  <>
                    {filteredBadges.map((badge, i) => (
                      <span
                        key={i}
                        className={`${getBadgeColor(badge)} text-xs font-medium px-2 py-1 rounded-full`}
                      >
                        {badge}
                      </span>
                    ))}
                  </>
                ) : null;
              })()}
            </div>

            {/* Tags visuais */}
            <div className="flex items-center gap-3 mb-3 text-sm flex-wrap">
              {facility.isVaccinationPoint && (
                <div className="flex items-center gap-1 text-blue-600">
                  <Syringe size={14} />
                  <span className="font-medium">Vacinação</span>
                </div>
              )}
              {facility.isHospital && (
                <div className="flex items-center gap-1 text-red-600">
                  <Building2 size={14} />
                  <span className="font-medium">Atendimento de Emergência/Alta Complexidade</span>
                </div>
              )}
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
              {facility.isSamuBase && (
                <span className="text-orange-600 font-medium">🚑 Base SAMU</span>
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
            
            {/* FASE 3: Avisos de Dados Incompletos */}
            {facility.data_validation && !facility.data_validation.is_complete && (
              <div className="bg-yellow-50 border border-yellow-300 rounded p-2 mb-3">
                <div className="flex items-start gap-2">
                  <AlertTriangle size={14} className="text-yellow-600 mt-0.5 flex-shrink-0" />
                  <div className="flex-1">
                    <p className="text-xs text-yellow-800 font-semibold mb-1">
                      ⚠️ Algumas informações podem estar desatualizadas
                    </p>
                    {facility.data_validation.warnings && facility.data_validation.warnings.length > 0 && (
                      <ul className="text-xs text-yellow-700 list-disc list-inside space-y-0.5">
                        {facility.data_validation.warnings.map((warning, idx) => (
                          <li key={idx}>{warning}</li>
                        ))}
                      </ul>
                    )}
                    <p className="text-xs text-yellow-700 mt-1 italic">
                      Recomendamos confirmar diretamente com a unidade antes de se deslocar.
                    </p>
                  </div>
                </div>
              </div>
            )}
            
            {/* Disclaimer Jurídico - CRÍTICO para Responsabilidade */}
            <div className="bg-blue-50 border border-blue-200 rounded p-2 mb-3 mt-3">
              <div className="flex items-start gap-2">
                <Info size={14} className="text-blue-600 mt-0.5 flex-shrink-0" />
                <p className="text-xs text-blue-800">
                  <strong>ℹ️ Informações baseadas em dados oficiais do CNES/DataSUS.</strong> 
                  {' '}Sempre confirme telefone, horário de atendimento e disponibilidade diretamente com a unidade antes de se deslocar.
                </p>
              </div>
            </div>

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
                  title={`Ligar para ${facility.phone}`}
                >
                  <Phone size={18} />
                  <span className="hidden sm:inline">{facility.phone}</span>
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
