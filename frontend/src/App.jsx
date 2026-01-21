import { useState, useEffect } from 'react'
import Header from './components/Header'
import FilterBar from './components/FilterBar'
import MapView from './components/MapView'
import ResultsList from './components/ResultsList'
import LegalDisclaimer from './components/LegalDisclaimer'
import EmergencyModal from './components/EmergencyModal'
import { searchFacilities } from './services/api'
import { AlertCircle } from 'lucide-react'

function App() {
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
  const [showEmergencyModal, setShowEmergencyModal] = useState(false)
  const [legalDisclaimer, setLegalDisclaimer] = useState('')

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

  // Buscar facilidades quando localização ou filtros mudarem
  useEffect(() => {
    if (userLocation && !loading) {
      fetchFacilities()
    }
  }, [userLocation, filters])

  const fetchFacilities = async () => {
    if (!userLocation) return

    setLoading(true)
    setError(null)

    try {
      const response = await searchFacilities({
        latitude: userLocation.lat,
        longitude: userLocation.lng,
        radius_km: 10,
        filter_type: filters.isEmergency ? 'ALL' : (
          filters.maternityOnly ? 'MATERNITY' : filters.filterType
        ),
        is_emergency: filters.isEmergency
      })

      setFacilities(response.results || [])
      setLegalDisclaimer(response.meta?.legal_disclaimer || '')
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
    setShowEmergencyModal(true)
    setFilters(prev => ({ ...prev, isEmergency: true }))
  }

  const handleEmergencyConfirm = () => {
    setShowEmergencyModal(false)
    fetchFacilities()
  }

  const handleEmergencyCancel = () => {
    setShowEmergencyModal(false)
    setFilters(prev => ({ ...prev, isEmergency: false }))
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header onEmergencyClick={handleEmergencyClick} />
      
      <main className="flex-1 flex flex-col">
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
            <div className="flex-1 relative">
              <MapView 
                userLocation={userLocation}
                facilities={facilities}
              />
            </div>

            {facilities.length > 0 ? (
              <ResultsList facilities={facilities} />
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
