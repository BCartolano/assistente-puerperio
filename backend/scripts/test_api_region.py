#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testa busca por estado/município (sem geolocalização)."""
import os
import sys
import json

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services.facility_service import FacilityService

def main():
    svc = FacilityService()
    # Busca só por state (SP), sem lat/lon
    results, data_source, _ = svc.search_facilities(
        latitude=None,
        longitude=None,
        radius_km=25,
        filter_type='MATERNITY',
        is_emergency=True,
        search_mode='all',
        state='SP',
        city=None
    )
    print('Busca state=SP, sem lat/lon:', len(results), 'resultados')
    for r in results[:5]:
        print(' ', r.get('display_name') or r.get('name'), r.get('city'), r.get('distance_km'))
    return 0

if __name__ == '__main__':
    sys.exit(main())
