#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
import sys
import os

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

conn = sqlite3.connect('backend/cnes_cache.db')
cursor = conn.cursor()

print("=" * 80)
print("📊 ESTATÍSTICAS DO BANCO DE DADOS")
print("=" * 80)

# Total
cursor.execute('SELECT COUNT(*) FROM hospitals_cache')
total = cursor.fetchone()[0]
print(f"\n📈 Total de estabelecimentos: {total:,}")

# Tipo de unidade
cursor.execute('SELECT COUNT(*) FROM hospitals_cache WHERE tipo_unidade IS NOT NULL')
com_tipo = cursor.fetchone()[0]
print(f"   Com tipo_unidade preenchido: {com_tipo:,} ({com_tipo/total*100:.1f}%)")

# Tipos distintos
cursor.execute('SELECT tipo_unidade, COUNT(*) as count FROM hospitals_cache WHERE tipo_unidade IS NOT NULL GROUP BY tipo_unidade ORDER BY count DESC')
rows = cursor.fetchall()
print(f"\n📋 Distribuição por tipo:")
for row in rows[:10]:
    print(f"   {row[0] or 'NULL'}: {row[1]:,}")

# Blacklist check
cursor.execute("SELECT COUNT(*) FROM hospitals_cache WHERE name LIKE '%ODONTO%' OR name LIKE '%DENTISTA%' OR name LIKE '%OTICA%' OR name LIKE '%ÓTICA%' OR name LIKE '%LABORATORIO%' OR name LIKE '%LABORATÓRIO%'")
blacklist_count = cursor.fetchone()[0]
print(f"\n🚫 Registros com termos da blacklist: {blacklist_count}")

# SUS vs Privado
cursor.execute('SELECT SUM(CASE WHEN is_sus = 1 THEN 1 ELSE 0 END) as sus, SUM(CASE WHEN is_sus = 0 THEN 1 ELSE 0 END) as privado FROM hospitals_cache')
row = cursor.fetchone()
sus_count = row[0]
privado_count = row[1]
print(f"\n💰 Classificação:")
print(f"   SUS: {sus_count:,} ({sus_count/total*100:.1f}%)")
print(f"   Privado: {privado_count:,} ({privado_count/total*100:.1f}%)")

# Maternidades e UPAs
cursor.execute('SELECT SUM(CASE WHEN has_maternity = 1 THEN 1 ELSE 0 END) as maternity, SUM(CASE WHEN is_emergency_only = 1 THEN 1 ELSE 0 END) as upa FROM hospitals_cache')
row = cursor.fetchone()
maternity_count = row[0]
upa_count = row[1]
print(f"\n👶 Maternidades: {maternity_count:,} ({maternity_count/total*100:.1f}%)")
print(f"🟡 UPAs: {upa_count:,} ({upa_count/total*100:.1f}%)")

conn.close()
print("\n" + "=" * 80)
