import { useState, useEffect } from 'react'
import Header from './components/Header'
import FilterBar from './components/FilterBar'
import MapView from './components/MapView'
import ResultsList from './components/ResultsList'
import LegalDisclaimer from './components/LegalDisclaimer'
import EmergencyModal from './components/EmergencyModal'
import EmergencyObstetricDemo from './components/EmergencyObstetricDemo'
import { searchFacilities, emergencySearch, buildRoutesUrl } from './services/api'
import EmergencyObstetricCard from './components/EmergencyObstetricCard'
import { AlertCircle } from 'lucide-react'

function App() {
  const [showEmergencyDemo, setShowEmergencyDemo] = useState(false)
  const [userLocation, setUserLocation] = useState(null)
  const [facilities, setFacilities] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState({
    filterType: 'ALL',
    hasInsurance: false,
    maternityOnly: true,
    isEmergency: false
  })
  const [searchMode, setSearchMode] = useState('emergency') // 'emergency' ou 'basic'
  const [showEmergencyModal, setShowEmergencyModal] = useState(false)
  const [legalDisclaimer, setLegalDisclaimer] = useState('')
  const [banner192, setBanner192] = useState(false)
  const [emergencyDebug, setEmergencyDebug] = useState(null)

  // Solicitar geolocalização ao carregar
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude
          })
        },
        (err) => {
          console.error('Erro ao obter localização:', err)
          setError('Não foi possível obter sua localização. Por favor, ative a geolocalização.')
        }
      )
    } else {
      setError('Geolocalização não é suportada pelo seu navegador.')
    }
  }, [])

  // Buscar facilidades quando localização, filtros ou modo de busca mudarem
  useEffect(() => {
    if (userLocation && !loading) {
      fetchFacilities()
    }
  }, [userLocation, filters, searchMode])

  const fetchFacilities = async () => {
    if (!userLocation) return

    setLoading(true)
    setError(null)
    setBanner192(false)
    setEmergencyDebug(null)

    try {
      if (searchMode === 'emergency') {
        const { lat, lng } = userLocation
        const MIN_RESULTS = typeof window !== 'undefined' && window.innerWidth < 768 ? 8 : 12
        const response = await emergencySearch({
          lat,
          lon: lng,
          radius_km: 25,
          expand: true,
          sus: filters.maternityOnly ? null : null,
          limit: 20,
          min_results: MIN_RESULTS,
          debug: true
        })
        // NÃO filtrar por has_maternity — exibir Confirmados e Prováveis
        const itens = (response.results || []).map((it) => ({
          ...it,
          rotas_url: it.rotas_url || buildRoutesUrl(lat, lng, it.lat, it.lon)
        }))
        setFacilities(itens)
        setBanner192(!!response.banner_192)
        setEmergencyDebug(response.debug || null)
      } else {
        const response = await searchFacilities({
          latitude: userLocation.lat,
          longitude: userLocation.lng,
          radius_km: 10,
          filter_type: filters.isEmergency ? 'ALL' : (
            filters.maternityOnly ? 'MATERNITY' : filters.filterType
          ),
          is_emergency: filters.isEmergency,
          search_mode: searchMode
        })
        setFacilities(response.results || [])
        setLegalDisclaimer(response.meta?.legal_disclaimer || '')
      }
    } catch (err) {
      console.error('Erro ao buscar facilidades:', err)
      setError(
        'Não foi possível buscar hospitais. Verifique sua conexão ou ligue 192 em caso de emergência.'
      )
      setFacilities([])
    } finally {
      setLoading(false)
    }
  }

  const handleEmergencyClick = () => {
    setSearchMode('emergency') // Mudar para modo emergência
    setShowEmergencyModal(true)
    setFilters(prev => ({ ...prev, isEmergency: true }))
  }
  
  const handleSearchModeChange = (mode) => {
    setSearchMode(mode)
    // Se mudar para emergência, ativar flag de emergência
    if (mode === 'emergency') {
      setFilters(prev => ({ ...prev, isEmergency: true }))
    } else {
      setFilters(prev => ({ ...prev, isEmergency: false }))
    }
  }

  const handleEmergencyConfirm = () => {
    setShowEmergencyModal(false)
    fetchFacilities()
  }

  const handleEmergencyCancel = () => {
    setShowEmergencyModal(false)
    setFilters(prev => ({ ...prev, isEmergency: false }))
  }

  if (showEmergencyDemo) {
    return (
      <div className="min-h-screen flex flex-col">
        <div className="bg-white border-b px-4 py-2 flex items-center gap-2">
          <button
            type="button"
            onClick={() => setShowEmergencyDemo(false)}
            className="text-gray-600 hover:text-gray-900 font-medium"
          >
            ← Voltar ao app
          </button>
        </div>
        <EmergencyObstetricDemo />
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header onEmergencyClick={handleEmergencyClick} />
      
      <main className="flex-1 flex flex-col">
        {/* Abas de Modo de Busca - CRÍTICO PARA SEGURANÇA */}
        <div className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex flex-wrap gap-2 items-center">
              <button
                onClick={() => handleSearchModeChange('emergency')}
                className={`px-6 py-3 font-semibold text-sm rounded-t-lg transition-colors flex items-center gap-2 ${
                  searchMode === 'emergency'
                    ? 'bg-red-600 text-white border-b-2 border-red-700'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <span className="text-lg">🏥</span>
                Hospitais/UPA
              </button>
              <button
                onClick={() => handleSearchModeChange('basic')}
                className={`px-6 py-3 font-semibold text-sm rounded-t-lg transition-colors flex items-center gap-2 ${
                  searchMode === 'basic'
                    ? 'bg-blue-600 text-white border-b-2 border-blue-700'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <span className="text-lg">💉</span>
                Vacinas/UBS
              </button>
              <button
                type="button"
                onClick={() => setShowEmergencyDemo(true)}
                className="px-4 py-2 text-sm font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg"
              >
                Ver demo Card Emergência
              </button>
            </div>
          </div>
          
          {/* Disclaimer de Emergência */}
          {searchMode === 'emergency' && (
            <div className="bg-red-50 border-t border-red-200 px-4 py-2">
              <p className="text-sm text-red-800 font-semibold text-center">
                🚨 EMERGÊNCIA: Em caso de risco de morte, ligue 192 ou dirija-se ao Hospital mais próximo.
              </p>
            </div>
          )}
        </div>
        
        <FilterBar 
          filters={filters}
          onFiltersChange={setFilters}
        />

        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mx-4 mt-4 rounded">
            <div className="flex items-center">
              <AlertCircle className="text-red-500 mr-2" size={20} />
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          </div>
        )}

        {loading && (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Buscando hospitais próximos...</p>
            </div>
          </div>
        )}

        {!loading && userLocation && (
          <>
            {searchMode === 'emergency' && banner192 && (
              <div className="bg-red-100 border-l-4 border-red-500 p-4 mx-4 mt-4 rounded flex items-center gap-2 banner-192" role="alert">
                <AlertCircle className="text-red-600 shrink-0" size={20} />
                <p className="text-red-800 font-medium">Sintomas graves? Ligue 192 (SAMU) agora.</p>
              </div>
            )}

            <div className="flex-1 relative">
              <MapView 
                userLocation={userLocation}
                facilities={facilities}
              />
            </div>

            {facilities.length > 0 ? (
              searchMode === 'emergency' ? (
                <div className="bg-gray-50 border-t border-gray-200 max-h-[28rem] overflow-y-auto scroll-smooth">
                  <div className="max-w-7xl mx-auto px-4 py-4 space-y-4">
                    {emergencyDebug?.expanded && emergencyDebug?.radius_used != null && (
                      <div className="rounded-lg border-l-4 border-blue-500 bg-blue-50 px-3 py-2 text-sm text-blue-800" role="status">
                        Resultados em raio expandido para {Math.round(Number(emergencyDebug.radius_used))} km
                      </div>
                    )}
                    <h2 className="text-lg font-semibold text-gray-900">Maternidades próximas ({facilities.length})</h2>
                    {facilities.map((facility) => (
                      <EmergencyObstetricCard
                        key={facility.cnes_id || facility.nome}
                        facility={facility}
                        distanceKm={facility.distancia_km}
                        distanceLabel={facility.distancia_km != null ? `~${Number(facility.distancia_km).toFixed(1)} km` : null}
                        showDisclaimer={true}
                      />
                    ))}
                  </div>
                </div>
              ) : (
                <ResultsList facilities={facilities} />
              )
            ) : !error && (
              <div className="p-6 text-center bg-yellow-50 border-t border-yellow-200">
                <p className="text-gray-700 mb-2">
                  Nenhuma unidade validada encontrada na sua região.
                </p>
                <p className="text-red-600 font-semibold">
                  Em caso de emergência, ligue 192 ou dirija-se ao pronto socorro mais próximo.
                </p>
              </div>
            )}
          </>
        )}

        {!userLocation && !error && (
          <div className="flex-1 flex items-center justify-center p-6">
            <div className="text-center">
              <p className="text-gray-600 mb-2">
                Aguardando permissão de geolocalização...
              </p>
              <p className="text-sm text-gray-500">
                Por favor, permita o acesso à sua localização para encontrar hospitais próximos.
              </p>
            </div>
          </div>
        )}
      </main>

      {legalDisclaimer && (
        <LegalDisclaimer text={legalDisclaimer} />
      )}

      <EmergencyModal
        isOpen={showEmergencyModal}
        onConfirm={handleEmergencyConfirm}
        onCancel={handleEmergencyCancel}
      />
    </div>
  )
}

export default App
