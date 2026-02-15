import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://unobstructive-ornamentally-arian.ngrok-free.dev'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const searchFacilities = async (params) => {
  try {
    const response = await api.post('/api/v1/facilities/search', params)
    return response.data
  } catch (error) {
    console.error('API Error:', error.response?.data || error.message)
    throw error
  }
}

/** GET /api/v1/emergency/search – Busca obstétrica em 3 camadas. min_results: 8 mobile, 12 desktop; limit=20. */
export const emergencySearch = async ({ lat, lon, radius_km = 25, expand = true, sus = null, limit = 20, min_results = null, debug = true }) => {
  const MIN_RESULTS = min_results != null ? min_results : (typeof window !== 'undefined' && window.innerWidth < 768 ? 8 : 12)
  const qs = new URLSearchParams({
    lat: String(lat),
    lon: String(lon),
    radius_km: String(radius_km),
    expand: String(expand),
    limit: String(limit),
    min_results: String(MIN_RESULTS),
    debug: String(debug)
  })
  if (sus !== null && sus !== undefined) qs.set('sus', String(sus))
  const path = `/api/v1/emergency/search?${qs.toString()}`
  console.debug('[EMERGENCY] GET', api.defaults.baseURL + path)
  try {
    const response = await api.get(path)
    return response.data
  } catch (error) {
    console.error('Emergency search API Error:', error.response?.data || error.message)
    throw error
  }
}

/** Fallback para rotas quando o backend não devolver rotas_url */
export function buildRoutesUrl(userLat, userLon, hLat, hLon) {
  if (hLat == null || hLon == null) return null
  return `https://www.google.com/maps/dir/?api=1&origin=${userLat},${userLon}&destination=${hLat},${hLon}`
}

export default api
