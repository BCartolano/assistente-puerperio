import { useEffect, useRef } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix para ícones padrão do Leaflet
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

// Componente para centrar mapa quando userLocation muda
function MapCenter({ center, zoom }) {
  const map = useMap()
  useEffect(() => {
    map.setView(center, zoom)
  }, [map, center, zoom])
  return null
}

// Ícones personalizados
const userIcon = L.icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
})

const createHospitalIcon = (isSus, hasMaternity, isEmergencyOnly) => {
  let color = 'green' // Default (Privado)
  
  if (isEmergencyOnly) {
    color = 'yellow' // UPA
  } else if (isSus) {
    color = 'blue' // SUS/Público
  }
  
  return L.icon({
    iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${color}.png`,
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  })
}

export default function MapView({ userLocation, facilities }) {
  const mapRef = useRef(null)

  if (!userLocation) {
    return (
      <div className="flex-1 bg-gray-200 flex items-center justify-center">
        <p className="text-gray-500">Carregando mapa...</p>
      </div>
    )
  }

  return (
    <div className="w-full h-full">
      <MapContainer
        center={[userLocation.lat, userLocation.lng]}
        zoom={13}
        style={{ height: '100%', width: '100%', zIndex: 0 }}
        ref={mapRef}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <MapCenter center={[userLocation.lat, userLocation.lng]} zoom={13} />
        
        {/* Marcador da usuária */}
        <Marker
          position={[userLocation.lat, userLocation.lng]}
          icon={userIcon}
        >
          <Popup>
            <strong>Sua localização</strong>
          </Popup>
        </Marker>

        {/* Marcadores dos hospitais */}
        {facilities.map((facility) => {
          if (!facility.lat || !facility.long) return null
          
          const icon = createHospitalIcon(
            facility.tags.sus,
            facility.tags.maternity,
            facility.tags.emergency_only
          )
          
          return (
            <Marker
              key={facility.id}
              position={[facility.lat, facility.long]}
              icon={icon}
            >
              <Popup>
                <div className="text-sm">
                  <strong className="font-semibold">{facility.name}</strong>
                  <p className="text-gray-600 mt-1">{facility.distance_km} km</p>
                  {facility.badges.length > 0 && (
                    <div className="mt-1 flex flex-wrap gap-1">
                      {facility.badges.map((badge, i) => (
                        <span
                          key={i}
                          className="text-xs bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded"
                        >
                          {badge}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </Popup>
            </Marker>
          )
        })}
      </MapContainer>
    </div>
  )
}
