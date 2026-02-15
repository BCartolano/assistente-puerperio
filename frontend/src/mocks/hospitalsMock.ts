/**
 * Mock de hospitais para testes do Card de Emergência Obstétrica.
 * Formato GeoJSON Feature, simulando a saída do pipeline maternity_whitelist_pipeline.
 * Casos: 1) Público completo (SUS + UTI Neo), 2) Particular simples, 3) Maternidade mista.
 */

export interface HospitalFeatureMock {
  type: 'Feature'
  geometry: { type: 'Point'; coordinates: [number, number] }
  properties: {
    id: string
    name: string
    address?: string
    city?: string
    state?: string
    phone?: string
    accepts_sus: boolean
    private_only: boolean
    has_nicu: boolean
    confidence_score?: number
    data_version?: string
  }
}

export const hospitalsMock: HospitalFeatureMock[] = [
  {
    type: 'Feature',
    geometry: {
      type: 'Point',
      coordinates: [-46.6339, -23.5505],
    },
    properties: {
      id: 'MOCK_SUS_UTI_NEO',
      name: 'Hospital Materno Infantil Dr. Cândido Fontoura',
      address: 'Av. Celso Garcia, 4815 – Tatuapé',
      city: 'São Paulo',
      state: 'SP',
      phone: '(11) 3396-2000',
      accepts_sus: true,
      private_only: false,
      has_nicu: true,
      confidence_score: 100,
      data_version: '2025-02',
    },
  },
  {
    type: 'Feature',
    geometry: {
      type: 'Point',
      coordinates: [-43.2075, -22.9068],
    },
    properties: {
      id: 'MOCK_PARTICULAR',
      name: 'Maternidade São José – Particular',
      address: 'Rua do Ouvidor, 100 – Centro',
      city: 'Rio de Janeiro',
      state: 'RJ',
      phone: '(21) 2222-3333',
      accepts_sus: false,
      private_only: true,
      has_nicu: false,
      confidence_score: 100,
      data_version: '2025-02',
    },
  },
  {
    type: 'Feature',
    geometry: {
      type: 'Point',
      coordinates: [-46.6544, -23.5489],
    },
    properties: {
      id: 'MOCK_MISTO',
      name: 'Hospital e Maternidade Santa Maria (SUS + Convênio)',
      address: 'Rua Consolação, 3772 – Consolação',
      city: 'São Paulo',
      state: 'SP',
      phone: '(11) 3237-5000',
      accepts_sus: true,
      private_only: false,
      has_nicu: true,
      confidence_score: 100,
      data_version: '2025-02',
    },
  },
]
