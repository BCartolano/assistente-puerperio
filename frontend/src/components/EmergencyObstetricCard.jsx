/**
 * Card de Emergência Obstétrica
 * UX: Hierarquia = distância + aceita plano da usuária; tags de segurança; 2 botões de ação; disclaimer CNES.
 * Dados esperados: properties do GeoJSON (id, name, address, phone, accepts_sus, private_only, has_nicu).
 */

import { Phone, MapPin, AlertCircle, Shield, Baby } from 'lucide-react'
import { useState } from 'react'

const CNES_DISCLAIMER = 'Dados do Cadastro Nacional (CNES). Confirme atendimento telefonicamente.'

export default function EmergencyObstetricCard({
  facility,
  distanceKm = null,
  distanceLabel = null,
  onCepFallback = null,
  showDisclaimer = true,
  className = '',
}) {
  const [cepSearch, setCepSearch] = useState('')
  const name = facility?.name || facility?.display_name || facility?.fantasy_name || facility?.nome || 'Estabelecimento'
  const address = facility?.address || facility?.endereco || ''
  const phone = facility?.phone || facility?.telefone || facility?.phone_e164 || ''
  const phoneFormatted = facility?.telefone_formatado || phone
  const labelMaternidade = facility?.label_maternidade || (facility?.has_maternity ? 'Ala de Maternidade' : 'Provável maternidade (ligue para confirmar)')
  // Nunca forçar "Privado": só renderizar o que a API manda (esfera e sus_badge)
  const sus_badge = facility?.sus_badge ?? null
  const esfera = facility?.esfera ?? null
  const atendeSus = facility?.atende_sus ?? (sus_badge === 'Aceita Cartão SUS' ? 'Sim' : (facility?.accepts_sus === true ? 'Sim' : (facility?.private_only ? 'Não' : 'Desconhecido')))
  const acceptsSus = atendeSus === 'Sim' || sus_badge === 'Aceita Cartão SUS'
  const privateOnly = sus_badge === 'Não atende SUS' || atendeSus === 'Não'
  const hasNicu = facility?.has_nicu === true
  const city = facility?.city || ''
  const state = facility?.state || ''
  const rotasUrl = facility?.rotas_url
  // Linha de convênios: do CNES quando houver; senão "ligue para confirmar" se não for Público/SUS
  const convs = Array.isArray(facility?.convenios) ? facility.convenios.filter(Boolean) : []
  let conveniosLine = ''
  if (convs.length) {
    conveniosLine = `Convênios no CNES: ${convs.slice(0, 3).join(', ')} • ligue para confirmar.`
  } else if (esfera !== 'Público' && sus_badge !== 'Aceita Cartão SUS') {
    conveniosLine = 'Convênios: ligue para confirmar.'
  }

  const handleCall = () => {
    if (phone) window.location.href = `tel:${phone.replace(/\D/g, '')}`
  }

  const handleRoute = () => {
    if (rotasUrl) {
      window.open(rotasUrl, '_blank')
      return
    }
    const dest = address ? `${name} ${address}`.trim() : name
    const url = `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(dest)}`
    window.open(url, '_blank')
  }

  const handleWaze = () => {
    const dest = address ? `${name} ${address}`.trim() : name
    const url = `https://waze.com/ul?q=${encodeURIComponent(dest)}&navigate=yes`
    window.open(url, '_blank')
  }

  return (
    <article
      className={`rounded-xl border-2 border-gray-200 bg-white shadow-md overflow-hidden ${className}`}
      aria-label={`Maternidade: ${name}`}
    >
      {/* Hierarquia 1: Distância e tempo estimado */}
      {(distanceKm != null || distanceLabel || facility?.tempo_estimado_seg != null) && (
        <div className="bg-slate-800 text-white px-4 py-2 flex items-center gap-2 flex-wrap">
          <MapPin className="w-5 h-5 shrink-0" aria-hidden />
          <span className="font-bold text-lg">
            {distanceLabel != null ? distanceLabel : (distanceKm != null ? `~${Number(distanceKm).toFixed(1)} km` : '')}
          </span>
          {facility?.tempo_estimado_seg != null && (
            <span className="text-slate-200 text-sm">• ~{Math.round(Number(facility.tempo_estimado_seg) / 60)} min</span>
          )}
        </div>
      )}

      {/* Label maternidade: Ala de Maternidade / Provável maternidade (ligue para confirmar) */}
      <div className="px-4 pt-2 pb-1">
        <span className="text-sm font-medium text-gray-700">{labelMaternidade}</span>
      </div>
      {/* Badges: esfera e SUS só do payload (nunca forçar Privado) */}
      <div className="px-4 pt-3 pb-2 flex flex-wrap gap-2">
        {sus_badge && (
          <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-sm font-medium ${sus_badge === 'Aceita Cartão SUS' ? 'bg-green-600 text-white' : 'bg-slate-100 text-gray-800'}`}>
            {sus_badge}
          </span>
        )}
        {esfera && (
          <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-sm font-medium ${
            esfera === 'Público' ? 'bg-green-700 text-white' : esfera === 'Filantrópico' ? 'bg-blue-600 text-white' : 'bg-amber-500 text-black'
          }`}>
            {esfera}
          </span>
        )}
        {acceptsSus && !sus_badge && (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-sm font-medium bg-green-600 text-white">
            <Shield className="w-4 h-4" aria-hidden />
            Atende SUS
          </span>
        )}
        {!acceptsSus && !privateOnly && atendeSus === 'Desconhecido' && (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-sm font-medium bg-green-700 text-white">
            <Shield className="w-4 h-4" aria-hidden />
            Atende seu Convênio
          </span>
        )}
        {privateOnly && !sus_badge && (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-sm font-medium bg-amber-500 text-black">
            Verifique plano
          </span>
        )}
        {hasNicu && (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-sm font-medium bg-purple-600 text-white">
            <Baby className="w-4 h-4" aria-hidden />
            Possui UTI Neonatal
          </span>
        )}
      </div>
      {conveniosLine && (
        <p className="px-4 card-convenios text-gray-600 text-xs mt-1 mb-0" style={{ font: '12px system-ui', color: '#374151', marginTop: 4 }}>
          {conveniosLine}
        </p>
      )}

      {/* Nome e endereço (secundário na hierarquia) */}
      <div className="px-4 pb-3">
        <h3 className="text-lg font-semibold text-gray-900 mb-1">{name}</h3>
        {(address || city) && (
          <p className="text-sm text-gray-600 flex items-start gap-1">
            <MapPin className="w-4 h-4 mt-0.5 shrink-0" aria-hidden />
            <span>
              {[address, city, state].filter(Boolean).join(', ')}
            </span>
          </p>
        )}
      </div>

      {/* Botões de ação: apenas dois, grandes */}
      <div className="px-4 pb-4 flex flex-col sm:flex-row gap-3">
        <a
          href={phone ? `tel:${(phone.replace && phone.replace(/\D/g, '')) || phone}` : '#'}
          onClick={(e) => { if (!phone) e.preventDefault(); }}
          className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg font-semibold text-base shadow-sm transition no-underline ${phone ? 'bg-green-600 hover:bg-green-700 text-white cursor-pointer' : 'bg-gray-300 text-gray-500 cursor-not-allowed'}`}
          aria-label="Ligar para estabelecimento"
        >
          <Phone className="w-5 h-5" aria-hidden />
          {phoneFormatted || 'Telefone não informado'}
        </a>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={handleRoute}
            className="flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold text-base shadow-sm transition"
            aria-label="Rotas"
          >
            <MapPin className="w-5 h-5" aria-hidden />
            Rotas
          </button>
          <button
            type="button"
            onClick={handleWaze}
            className="flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg bg-cyan-600 hover:bg-cyan-700 text-white font-semibold text-base shadow-sm transition"
            aria-label="Traçar rota no Waze"
          >
            Waze
          </button>
        </div>
      </div>

      {/* Fallback: busca por CEP se geolocalização falhar */}
      {onCepFallback && (
        <div className="px-4 pb-3 border-t border-gray-100 pt-3">
          <p className="text-xs text-gray-500 mb-2">Sem sua localização? Busque por CEP:</p>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="00000-000"
              value={cepSearch}
              onChange={(e) => setCepSearch(e.target.value)}
              className="flex-1 rounded border border-gray-300 px-3 py-2 text-sm"
              aria-label="CEP para busca"
            />
            <button
              type="button"
              onClick={() => onCepFallback(cepSearch)}
              className="py-2 px-3 rounded bg-gray-200 hover:bg-gray-300 text-sm font-medium"
            >
              Buscar
            </button>
          </div>
        </div>
      )}

      {/* Disclaimer jurídico/segurança */}
      {showDisclaimer && (
        <p className="px-4 py-2 bg-gray-100 text-xs text-gray-600 flex items-start gap-1" role="note">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" aria-hidden />
          {CNES_DISCLAIMER}
        </p>
      )}
    </article>
  )
}
