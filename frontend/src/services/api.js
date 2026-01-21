import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

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

export default api
