/**
 * Tela de demonstração: Mock + EmergencyObstetricCard para validar o visual.
 * Use esta tela para aprovar o design antes de conectar aos dados reais.
 */

import { useHospitalLocator } from '../hooks/useHospitalLocator'
import EmergencyObstetricCard from './EmergencyObstetricCard'
import { hospitalsMock } from '../mocks/hospitalsMock'

export default function EmergencyObstetricDemo() {
  const { hospitals, loading, error, refetch } = useHospitalLocator(hospitalsMock, {
    maxRadiusKm: 100,
    enabled: true,
  })

  const listToShow = hospitals.length > 0 ? hospitals : hospitalsMock.map((f) => ({ ...f, distanceKm: null }))

  return (
    <div className="min-h-screen bg-gray-100 py-6 px-4">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Demo – Emergência Obstétrica
        </h1>
        <p className="text-sm text-gray-600 mb-4">
          Cards de maternidades (mock). Permita a localização para ver distâncias reais.
        </p>

        {loading && (
          <p className="text-gray-600 mb-4">Obtendo sua localização...</p>
        )}

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-amber-50 border border-amber-200 text-amber-800 text-sm">
            {error.type === 'PERMISSION_DENIED' && (
              <span>Permissão de GPS negada. Use a busca por CEP ou visualize os cards sem distância.</span>
            )}
            {error.type !== 'PERMISSION_DENIED' && <span>{error.message}</span>}
            <button
              type="button"
              onClick={refetch}
              className="ml-2 underline font-medium"
            >
              Tentar novamente
            </button>
          </div>
        )}

        <div className="space-y-4">
          {listToShow.map((item) => (
            <EmergencyObstetricCard
              key={item.properties.id}
              facility={{
                ...item.properties,
                geometry: item.geometry,
              }}
              distance={Number.isFinite(item.distanceKm) ? item.distanceKm : null}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
