/**
 * Card de Emergência Obstétrica
 * Recebe facility (GeoJSON properties) e distance (do hook).
 * Badges: UTI Neonatal (roxo), Atende SUS (verde), Particular/Convênio (laranja).
 * Botões: Ligar Agora (primário), Traçar Rota (secundário).
 */

import { Phone, MapPin } from 'lucide-react'

export interface FacilityProperties {
  id: string
  name: string
  address?: string
  city?: string
  state?: string
  phone?: string
  accepts_sus?: boolean
  private_only?: boolean
  has_nicu?: boolean
  confidence_score?: number
  data_version?: string
  /** Opcional: coordenadas [lon, lat] do GeoJSON para Traçar Rota */
  geometry?: { type: 'Point'; coordinates: [number, number] }
}

export interface EmergencyObstetricCardProps {
  facility: FacilityProperties
  distance?: number | null
  className?: string
}

function shortenAddress(address?: string, city?: string, state?: string, maxLen = 50): string {
  const parts = [address, city, state].filter(Boolean) as string[]
  const full = parts.join(', ')
  if (full.length <= maxLen) return full
  return full.slice(0, maxLen).trim() + '…'
}

export default function EmergencyObstetricCard({
  facility,
  distance = null,
  className = '',
}: EmergencyObstetricCardProps) {
  const name = facility?.name ?? 'Estabelecimento'
  const addressShort = shortenAddress(
    facility?.address,
    facility?.city,
    facility?.state
  )
  const phone = facility?.phone ?? ''
  const hasNicu = facility?.has_nicu === true
  const acceptsSus = facility?.accepts_sus === true
  const privateOnly = facility?.private_only === true

  const handleRoute = () => {
    const coords = facility?.geometry?.coordinates
    if (coords?.length === 2) {
      const [lon, lat] = coords
      const url = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lon}`
      window.open(url, '_blank')
    } else {
      const dest = [name, facility?.address, facility?.city].filter(Boolean).join(', ')
      const url = `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(dest)}`
      window.open(url, '_blank')
    }
  }

  return (
    <article
      className={`rounded-xl border-2 border-gray-200 bg-white shadow-md overflow-hidden ${className}`}
      aria-label={`Maternidade: ${name}`}
    >
      {/* Cabeçalho: esquerda = distância (grande, bold); direita = badges */}
      <div className="flex items-center justify-between gap-3 px-4 py-3 bg-slate-50 border-b border-gray-100">
        <div className="flex-1 min-w-0">
          {distance != null && Number.isFinite(distance) && (
            <span className="text-2xl font-bold text-gray-900">
              {distance < 1 ? `${(distance * 1000).toFixed(0)} m` : `${distance.toFixed(1)} km`}
            </span>
          )}
        </div>
        <div className="flex flex-wrap gap-1.5 justify-end">
          {hasNicu && (
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-purple-600 text-white">
              UTI Neonatal
            </span>
          )}
          {acceptsSus && (
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-green-600 text-white">
              SUS
            </span>
          )}
          {privateOnly && (
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-orange-500 text-orange-950">
              Particular
            </span>
          )}
        </div>
      </div>

      {/* Corpo: nome e endereço encurtado */}
      <div className="px-4 py-3">
        <h3 className="text-lg font-semibold text-gray-900 mb-1">{name}</h3>
        {addressShort && (
          <p className="text-sm text-gray-600 flex items-start gap-1">
            <MapPin className="w-4 h-4 mt-0.5 shrink-0" aria-hidden />
            <span>{addressShort}</span>
          </p>
        )}
      </div>

      {/* Rodapé: botão primário (Ligar Agora) e secundário (Traçar Rota) */}
      <div className="px-4 pb-4 flex flex-col sm:flex-row gap-2">
        {phone ? (
          <a
            href={`tel:${phone.replace(/\D/g, '')}`}
            className="flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg bg-rose-600 hover:bg-rose-700 text-white font-semibold text-base shadow-sm transition"
            aria-label="Ligar agora"
          >
            <Phone className="w-5 h-5" aria-hidden />
            Ligar Agora
          </a>
        ) : (
          <span className="flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg bg-gray-300 text-gray-600 font-semibold text-base">
            <Phone className="w-5 h-5" aria-hidden />
            Ligar Agora
          </span>
        )}
        <button
          type="button"
          onClick={handleRoute}
          className="flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg border-2 border-gray-300 hover:border-gray-400 hover:bg-gray-50 text-gray-700 font-semibold text-base transition"
          aria-label="Traçar rota no Google Maps"
        >
          <MapPin className="w-5 h-5" aria-hidden />
          Traçar Rota
        </button>
      </div>

      {/* Rodapé: disclaimer */}
      <p className="px-4 py-2 text-xs text-gray-500 border-t border-gray-100">
        Dados do CNES. Confirme atendimento telefonicamente.
      </p>
    </article>
  )
}
