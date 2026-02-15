/**
 * useHospitalLocator – Hook para geolocalização e distância (Haversine)
 * Input: lista de hospitais (GeoJSON features).
 * Retorna: hospitais filtrados por raio, ordenados por distância; loading; error (ex.: GPS negado → CEP fallback).
 */

import { useState, useEffect, useCallback } from 'react'

export interface HospitalFeature {
  type: 'Feature'
  geometry: { type: 'Point'; coordinates: [number, number] }
  properties: {
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
  }
}

export interface HospitalWithDistance extends HospitalFeature {
  distanceKm: number
}

export interface UseHospitalLocatorOptions {
  maxRadiusKm?: number
  enabled?: boolean
}

export type HospitalLocatorError =
  | { type: 'PERMISSION_DENIED'; message: string }
  | { type: 'UNAVAILABLE'; message: string }
  | { type: 'TIMEOUT'; message: string }
  | { type: 'UNKNOWN'; message: string }

const EARTH_RADIUS_KM = 6371

function haversineKm(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  const toRad = (x: number) => (x * Math.PI) / 180
  const dLat = toRad(lat2 - lat1)
  const dLon = toRad(lon2 - lon1)
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) * Math.sin(dLon / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return EARTH_RADIUS_KM * c
}

function getCoords(feature: HospitalFeature): { lat: number; lon: number } | null {
  const coords = feature?.geometry?.coordinates
  if (!Array.isArray(coords) || coords.length < 2) return null
  const lon = Number(coords[0])
  const lat = Number(coords[1])
  if (Number.isNaN(lat) || Number.isNaN(lon)) return null
  return { lat, lon }
}

export function useHospitalLocator(
  features: HospitalFeature[] = [],
  options: UseHospitalLocatorOptions = {}
): {
  hospitals: HospitalWithDistance[]
  loading: boolean
  error: HospitalLocatorError | null
  userLocation: { lat: number; lon: number } | null
  refetch: () => void
} {
  const { maxRadiusKm = 50, enabled = true } = options
  const [userLocation, setUserLocation] = useState<{ lat: number; lon: number } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<HospitalLocatorError | null>(null)

  const fetchLocation = useCallback(() => {
    if (!enabled) {
      setLoading(false)
      return
    }
    setLoading(true)
    setError(null)
    if (!navigator?.geolocation) {
      setError({ type: 'UNAVAILABLE', message: 'Geolocalização não disponível.' })
      setLoading(false)
      return
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setUserLocation({ lat: pos.coords.latitude, lon: pos.coords.longitude })
        setError(null)
        setLoading(false)
      },
      (err) => {
        if (err.code === 1) {
          setError({
            type: 'PERMISSION_DENIED',
            message: 'Permissão de localização negada. Use a busca por CEP.',
          })
        } else if (err.code === 3) {
          setError({ type: 'TIMEOUT', message: 'Tempo esgotado ao obter localização.' })
        } else {
          setError({ type: 'UNKNOWN', message: err.message || 'Erro ao obter localização.' })
        }
        setLoading(false)
      },
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 60000 }
    )
  }, [enabled])

  useEffect(() => {
    fetchLocation()
  }, [fetchLocation])

  const hospitals: HospitalWithDistance[] = (() => {
    if (!Array.isArray(features) || features.length === 0) return []
    if (!userLocation) {
      return features.map((f) => ({ ...f, distanceKm: Infinity }))
    }
    const withDist = features
      .map((f) => {
        const c = getCoords(f)
        if (!c) return null
        const distanceKm = haversineKm(
          userLocation.lat,
          userLocation.lon,
          c.lat,
          c.lon
        )
        if (distanceKm > maxRadiusKm) return null
        return { ...f, distanceKm } as HospitalWithDistance
      })
      .filter((x): x is HospitalWithDistance => x != null)
    withDist.sort((a, b) => a.distanceKm - b.distanceKm)
    return withDist
  })()

  return {
    hospitals,
    loading,
    error,
    userLocation,
    refetch: fetchLocation,
  }
}
