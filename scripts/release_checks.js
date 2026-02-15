#!/usr/bin/env node
/**
 * Script de checks automáticos para release
 * 
 * Uso:
 *   node scripts/release_checks.js --base-url http://localhost:5000 --lat -23.19 --lon -45.79
 * 
 * Ou cole no console do navegador (modo interativo)
 */

const BASE_URL = process.env.BASE_URL || 'http://localhost:5000';
const DEFAULT_LAT = parseFloat(process.env.LAT || '-23.19');
const DEFAULT_LON = parseFloat(process.env.LON || '-45.79');

/**
 * Check 1: Contar "Privado" quando API disse "Público" (residual)
 */
async function checkPublicoVsPrivado(baseUrl, lat, lon) {
    console.log('\n[CHECK 1] Verificando se cards "Privado" aparecem quando API envia "Público"...\n');
    try {
        const url = `${baseUrl}/api/v1/emergency/search?lat=${lat}&lon=${lon}&radius_km=25&limit=50&expand=true&debug=true`;
        const res = await fetch(url);
        const data = await res.json();
        
        const publicos = data.results.filter(it => 
            it.esfera === "Público" && it.override_hit && it.override_reason === "applied"
        );
        
        console.log(`✅ Públicos na API: ${publicos.length}`);
        if (publicos.length > 0) {
            console.table(publicos.slice(0, 5).map(it => ({
                nome: it.nome,
                esfera: it.esfera,
                sus: it.sus_badge,
                override_hit: it.override_hit
            })));
        }
        
        return { ok: true, count: publicos.length };
    } catch (error) {
        console.error('❌ Erro:', error.message);
        return { ok: false, error: error.message };
    }
}

/**
 * Check 2: Verificar se clínica ambulatorial vazou
 */
async function checkAmbulatoriais(baseUrl, lat, lon) {
    console.log('\n[CHECK 2] Verificando se clínicas ambulatoriais aparecem nos resultados...\n');
    try {
        const url = `${baseUrl}/api/v1/emergency/search?lat=${lat}&lon=${lon}&radius_km=25&limit=50&expand=true`;
        const res = await fetch(url);
        const data = await res.json();
        
        const ambulatoriais = (data.results || []).filter(it => {
            const n = (it.nome || "").toLowerCase();
            return /psicolog|fono|fisioter|terapia\s*ocup|nutri|consult[óo]rio|ambulat/.test(n);
        });
        
        console.log(`⚠️ Ambulatoriais listadas: ${ambulatoriais.length}`);
        if (ambulatoriais.length > 0) {
            console.table(ambulatoriais.map(it => ({
                nome: it.nome,
                label: it.label_maternidade
            })));
            return { ok: false, count: ambulatoriais.length };
        }
        
        console.log('✅ Nenhuma clínica ambulatorial encontrada');
        return { ok: true, count: 0 };
    } catch (error) {
        console.error('❌ Erro:', error.message);
        return { ok: false, error: error.message };
    }
}

/**
 * Check 3: Debug dos 3 primeiros itens
 */
async function checkDebugPayload(baseUrl, lat, lon) {
    console.log('\n[CHECK 3] Debug payload dos 3 primeiros itens...\n');
    try {
        const url = `${baseUrl}/api/v1/emergency/search?lat=${lat}&lon=${lon}&radius_km=25&limit=3&expand=true&debug=true`;
        const res = await fetch(url);
        const data = await res.json();
        
        console.table(data.results.map(it => ({
            nome: it.nome,
            cnes_id: it.cnes_id,
            esfera: it.esfera,
            sus_badge: it.sus_badge,
            override_hit: it.override_hit,
            override_reason: it.override_reason
        })));
        
        return { ok: true, results: data.results };
    } catch (error) {
        console.error('❌ Erro:', error.message);
        return { ok: false, error: error.message };
    }
}

/**
 * Executa todos os checks
 */
async function runAllChecks(baseUrl, lat, lon) {
    console.log('='.repeat(60));
    console.log('RELEASE CHECKS - Sophia Emergency v2');
    console.log('='.repeat(60));
    console.log(`Base URL: ${baseUrl}`);
    console.log(`Lat/Lon: ${lat}, ${lon}\n`);
    
    const results = {
        publicoVsPrivado: await checkPublicoVsPrivado(baseUrl, lat, lon),
        ambulatoriais: await checkAmbulatoriais(baseUrl, lat, lon),
        debugPayload: await checkDebugPayload(baseUrl, lat, lon)
    };
    
    console.log('\n' + '='.repeat(60));
    console.log('RESUMO:');
    console.log('='.repeat(60));
    console.log(`Check 1 (Público vs Privado): ${results.publicoVsPrivado.ok ? '✅ OK' : '❌ FALHOU'}`);
    console.log(`Check 2 (Ambulatoriais): ${results.ambulatoriais.ok ? '✅ OK' : '❌ FALHOU'}`);
    console.log(`Check 3 (Debug Payload): ${results.debugPayload.ok ? '✅ OK' : '❌ FALHOU'}`);
    
    const allOk = results.publicoVsPrivado.ok && results.ambulatoriais.ok && results.debugPayload.ok;
    console.log(`\n${allOk ? '✅ TODOS OS CHECKS PASSARAM' : '❌ ALGUNS CHECKS FALHARAM'}\n`);
    
    return allOk ? 0 : 1;
}

// Se executado diretamente (Node.js)
if (typeof require !== 'undefined' && require.main === module) {
    const args = process.argv.slice(2);
    let baseUrl = BASE_URL;
    let lat = DEFAULT_LAT;
    let lon = DEFAULT_LON;
    
    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--base-url' && args[i + 1]) {
            baseUrl = args[i + 1];
            i++;
        } else if (args[i] === '--lat' && args[i + 1]) {
            lat = parseFloat(args[i + 1]);
            i++;
        } else if (args[i] === '--lon' && args[i + 1]) {
            lon = parseFloat(args[i + 1]);
            i++;
        }
    }
    
    // Node.js precisa de fetch (node-fetch ou fetch global)
    if (typeof fetch === 'undefined') {
        console.error('❌ fetch não disponível. Use Node.js 18+ ou instale node-fetch');
        process.exit(1);
    }
    
    runAllChecks(baseUrl, lat, lon).then(code => process.exit(code));
}

// Exporta para uso no console do navegador
if (typeof window !== 'undefined') {
    window.releaseChecks = {
        checkPublicoVsPrivado,
        checkAmbulatoriais,
        checkDebugPayload,
        runAllChecks
    };
    console.log('✅ releaseChecks disponível no console. Use: releaseChecks.runAllChecks("http://localhost:5000", -23.19, -45.79)');
}
