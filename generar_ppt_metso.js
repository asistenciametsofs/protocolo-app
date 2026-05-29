// generar_ppt_metso.js
// Genera PPT estilo Metso (fondo negro, puntos decorativos, acento naranja)
// Uso: node generar_ppt_metso.js < datos.json → stdout base64

const pptxgen = require('pptxgenjs');
const fs = require('fs');

// ── Colores Metso ─────────────────────────────────────────────
const NEGRO    = '111111';
const BLANCO   = 'FFFFFF';
const NARANJA  = 'E97132';
const GRIS_OSC = '333333';
const GRIS_MED = '666666';
const VERDE    = '22C55E';
const AMARILLO = 'F59E0B';
const ROJO     = 'EF4444';
const GRIS_CLR = 'AAAAAA';

// ── Helpers ───────────────────────────────────────────────────
function safe(v, def = '-') {
    if (v === null || v === undefined || v === '') return def;
    return String(v);
}

function safeNum(v) {
    const n = parseFloat(v);
    return isNaN(n) ? null : n;
}

function promedio(arr) {
    const nums = arr.filter(v => v !== null && v !== undefined && !isNaN(parseFloat(v))).map(parseFloat);
    if (!nums.length) return null;
    return Math.round((nums.reduce((a, b) => a + b, 0) / nums.length) * 100) / 100;
}

function ultimoCambio(cambios, campo) {
    for (const c of cambios) {
        if (c[campo] === 'SI' && c.fecha_inicio) {
            return String(c.fecha_inicio).substring(0, 10);
        }
    }
    return null;
}

function calcProyeccion(alturas) {
    if (!alturas || alturas.length < 2) return null;
    const LIMITE = 9.0;
    const fechas = alturas.map(r => new Date(r.fecha));
    const vals   = alturas.map(r => parseFloat(r.altura));
    const dias   = fechas.map((f, i) => {
        const diff = (f - fechas[0]) / 86400000;
        const paradasAcum = alturas.slice(0, i + 1).reduce((s, r) => s + (parseInt(r.dias_parada) || 0), 0);
        return diff - paradasAcum;
    });
    const n = dias.length;
    const sx = dias.reduce((a, b) => a + b, 0);
    const sy = vals.reduce((a, b) => a + b, 0);
    const sxy = dias.reduce((s, x, i) => s + x * vals[i], 0);
    const sxx = dias.reduce((s, x) => s + x * x, 0);
    const denom = n * sxx - sx * sx;
    if (Math.abs(denom) < 1e-9) return null;
    const m = (n * sxy - sx * sy) / denom;
    const b = (sy - m * sx) / n;
    if (m >= 0) return null; // no hay desgaste
    const diaLimite = Math.floor((LIMITE - b) / m);
    const totalParadas = alturas.reduce((s, r) => s + (parseInt(r.dias_parada) || 0), 0);
    const fechaLimite = new Date(fechas[0].getTime() + (diaLimite + totalParadas) * 86400000);
    const semana = getWeek(fechaLimite);
    return { fecha: fechaLimite.toLocaleDateString('es-PE'), semana: `W${semana}`, m, b, dias, vals, fechas, diaLimite };
}

function getWeek(d) {
    const date = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
    date.setUTCDate(date.getUTCDate() + 4 - (date.getUTCDay() || 7));
    const yearStart = new Date(Date.UTC(date.getUTCFullYear(), 0, 1));
    return Math.ceil((((date - yearStart) / 86400000) + 1) / 7);
}

function estadoSemaforo(val, minimo, maximo) {
    if (val === null) return 'sin_dato';
    if (maximo !== null && val > maximo) return 'rojo';
    if (minimo !== null && val < minimo * 1.2) return 'amarillo';
    return 'verde';
}

function colorSemaforo(estado) {
    return estado === 'verde' ? VERDE : estado === 'amarillo' ? AMARILLO : estado === 'rojo' ? ROJO : GRIS_CLR;
}

// ── Puntos decorativos estilo Metso ───────────────────────────
function addDots(slide, x0, y0, cols, rows, spacing, color, size) {
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            slide.addShape('ellipse', {
                x: x0 + c * spacing, y: y0 + r * spacing,
                w: size, h: size,
                fill: { color },
                line: { color, width: 0 }
            });
        }
    }
}

// ── Gráfico de línea nativo ────────────────────────────────────
function addLineChart(slide, labels, series, x, y, w, h, opts = {}) {
    const chartData = series.map(s => ({
        name: s.name,
        labels,
        values: s.values
    }));

    const chartOpts = {
        x, y, w, h,
        chartColors: series.map(s => s.color || NARANJA),
        chartArea: { fill: { color: '1A1A1A' } },
        catAxisLabelColor: '888888',
        valAxisLabelColor: '888888',
        catAxisLabelFontSize: 7,
        valAxisLabelFontSize: 7,
        valGridLine: { color: '333333', size: 0.3 },
        catGridLine: { style: 'none' },
        lineSize: series.map(s => s.lineSize || 2),
        lineDataSymbol: series.map(s => s.symbol || 'circle'),
        lineDataSymbolSize: series.map(s => s.symbolSize || 4),
        showLegend: opts.showLegend || false,
        legendPos: 'b',
        legendFontSize: 7,
        legendColor: BLANCO,
        showTitle: false,
        valAxisMinVal: opts.valMin,
        valAxisMaxVal: opts.valMax,
        ...opts.extra
    };

    // Líneas de referencia como series adicionales
    if (opts.refLines) {
        opts.refLines.forEach(ref => {
            chartData.push({ name: ref.label, labels, values: labels.map(() => ref.val) });
            chartOpts.chartColors.push(ref.color || ROJO);
            chartOpts.lineSize.push(1);
            chartOpts.lineDataSymbol.push('none');
            chartOpts.lineDataSymbolSize.push(0);
        });
    }

    slide.addChart('line', chartData, chartOpts);
}

// ── GENERADOR PRINCIPAL ───────────────────────────────────────
async function generarPPT(payload) {
    const { chancadoras, datos, semana, fecha } = payload;
    const pres = new pptxgen();
    pres.layout = 'LAYOUT_16x9';
    pres.title = `Metso - Estado Chancadoras MP1250 - ${fecha}`;

    // ═══════════════════════════════════════════════════════════
    // SLIDE 1 — PORTADA
    // ═══════════════════════════════════════════════════════════
    const s1 = pres.addSlide();
    s1.background = { color: NEGRO };

    // Puntos decorativos
    addDots(s1, 4.5, 0.3, 18, 14, 0.32, '333333', 0.04);

    // Logo Metso
    s1.addText('Metso', { x: 0.5, y: 0.4, w: 3, h: 0.6, fontSize: 28, bold: true, color: BLANCO, fontFace: 'Arial' });

    // Título
    s1.addText('Estado de Equipos MP1250', { x: 0.5, y: 1.4, w: 6, h: 0.8, fontSize: 32, bold: true, color: BLANCO, fontFace: 'Arial' });
    s1.addText('Sociedad Minera Cerro Verde', { x: 0.5, y: 2.2, w: 6, h: 0.5, fontSize: 16, color: '888888', fontFace: 'Arial' });
    s1.addText(semana, { x: 0.5, y: 2.7, w: 6, h: 0.4, fontSize: 13, color: NARANJA, fontFace: 'Arial' });

    // Stats resumen
    let totalNormal = 0, totalAtenc = 0, totalUrg = 0;
    chancadoras.forEach(ch => {
        const d = datos[ch];
        if (!d.ultimo) return;
        const u = d.ultimo;
        const mflProm = promedio(['a','b','c','d','e','f','g'].map(x => safeNum(u[`mfl_med_${x}`])));
        const slProm  = promedio([1,2,3,4,5,6].flatMap(i => [safeNum(u[`socket_b${i}`]), safeNum(u[`socket_a${i}`])]));
        const gapProm = promedio([safeNum(u.socket_gap_0), safeNum(u.socket_gap_90), safeNum(u.socket_gap_180), safeNum(u.socket_gap_270)]);
        const hayRojo = (mflProm !== null && mflProm < 12) || (slProm !== null && slProm < 5) || u.prot_estatico_estado === 'Malo';
        const hayAmar = (mflProm !== null && mflProm < 18) || (slProm !== null && (slProm < 6 || slProm > 9.5)) || (gapProm !== null && gapProm > 0.3) || u.montura_barras_estado === 'Malo';
        if (hayRojo) totalUrg++;
        else if (hayAmar) totalAtenc++;
        else totalNormal++;
    });

    const stats = [
        { val: '8', lbl: 'Chancadoras', col: BLANCO },
        { val: String(totalNormal), lbl: 'Estado normal', col: VERDE },
        { val: String(totalAtenc), lbl: 'Atención', col: AMARILLO },
        { val: String(totalUrg), lbl: 'Urgente', col: ROJO },
    ];
    stats.forEach((st, i) => {
        const bx = 0.5 + i * 2.35;
        s1.addShape('rect', { x: bx, y: 3.5, w: 2.1, h: 1.2, fill: { color: '1E1E1E' }, line: { color: '333333', width: 1 } });
        s1.addText(st.val, { x: bx, y: 3.55, w: 2.1, h: 0.65, fontSize: 28, bold: true, color: st.col, align: 'center', fontFace: 'Arial' });
        s1.addText(st.lbl, { x: bx, y: 4.15, w: 2.1, h: 0.35, fontSize: 10, color: '888888', align: 'center', fontFace: 'Arial' });
    });

    // Línea naranja bottom
    s1.addShape('rect', { x: 0, y: 5.3, w: 10, h: 0.07, fill: { color: NARANJA }, line: { color: NARANJA } });
    s1.addText(`Generado: ${fecha}`, { x: 7, y: 5.35, w: 2.8, h: 0.25, fontSize: 8, color: '666666', align: 'right', fontFace: 'Arial' });

    // ═══════════════════════════════════════════════════════════
    // SLIDES POR CHANCADORA
    // ═══════════════════════════════════════════════════════════
    for (const ch of chancadoras) {
        const d = datos[ch];
        const u = d.ultimo;
        const hist = d.historial;
        const cambios = d.cambios;

        const slide = pres.addSlide();
        slide.background = { color: NEGRO };

        // Puntos decorativos top-right
        addDots(slide, 7.5, 0.1, 10, 6, 0.28, '222222', 0.04);

        // ── HEADER ──────────────────────────────────────────────
        slide.addShape('rect', { x: 0, y: 0, w: 10, h: 0.85, fill: { color: '1A1A1A' }, line: { color: '1A1A1A' } });
        slide.addShape('rect', { x: 0, y: 0.85, w: 10, h: 0.04, fill: { color: NARANJA }, line: { color: NARANJA } });

        // Calcular estado general anticipado
        const _mflP = promedio(['a','b','c','d','e','f','g'].map(x => safeNum(u[`mfl_med_${x}`])));
        const _slP  = promedio([1,2,3,4,5,6].flatMap(i => [safeNum(u[`socket_b${i}`]), safeNum(u[`socket_a${i}`])]));
        const _gapP = promedio([safeNum(u.socket_gap_0), safeNum(u.socket_gap_90), safeNum(u.socket_gap_180), safeNum(u.socket_gap_270)]);
        const _hayAmar = (_mflP !== null && _mflP < 18) || (_slP !== null && (_slP < 6 || _slP > 9.5)) || (_gapP !== null && _gapP > 0.3) || u.montura_barras_estado === 'Malo' || u.prot_estatico_estado === 'Malo';
        const _hayRojo = (_mflP !== null && _mflP < 12) || (_slP !== null && _slP < 5) || u.prot_estatico_estado === 'Malo';
        const _estadoG = _hayRojo ? 'URGENTE' : _hayAmar ? 'ATENCIÓN' : 'BUEN ESTADO';
        const _colorG  = _hayRojo ? ROJO : _hayAmar ? AMARILLO : VERDE;

        slide.addText(ch, { x: 0.3, y: 0.05, w: 2, h: 0.5, fontSize: 24, bold: true, color: BLANCO, fontFace: 'Arial', margin: 0 });
        slide.addShape('rect', { x: 2.4, y: 0.12, w: 1.1, h: 0.28, fill: { color: _colorG }, line: { color: _colorG } });
        slide.addText(_estadoG, { x: 2.4, y: 0.12, w: 1.1, h: 0.28, fontSize: 8, bold: true, color: NEGRO, align: 'center', valign: 'middle', fontFace: 'Arial', margin: 0 });

        if (u) {
            const fechaI = safe(u.fecha_inicio).substring(0, 10);
            slide.addText(`Última intervención: ${fechaI}`, {
                x: 0.3, y: 0.52, w: 4, h: 0.28, fontSize: 11, bold: true, color: NARANJA, fontFace: 'Arial', margin: 0
            });
            slide.addText(`Supervisor: ${safe(u.supervisor_metso)}  ·  ${d.total} intervenciones registradas`, {
                x: 0.3, y: 0.52, w: 9.4, h: 0.28, fontSize: 10, color: '888888', fontFace: 'Arial', align: 'right', margin: 0
            });
        } else {
            slide.addText('Sin registros', { x: 0.3, y: 0.52, w: 6, h: 0.28, fontSize: 11, color: '666666', fontFace: 'Arial', margin: 0 });
        }

        // Head/Bowl/Altura
        if (u) {
            const infoItems = [
                { lbl: 'Head', val: safe(u.head_entrante) },
                { lbl: 'Bowl', val: safe(u.bowl_entrante) },
                { lbl: 'Altura', val: safe(u.altura_final_bowl) + '"' },
            ];
            infoItems.forEach((it, i) => {
                const bx = 7.0 + i * 1.0;
                slide.addText(it.val, { x: bx, y: 0.02, w: 0.95, h: 0.38, fontSize: 14, bold: true, color: BLANCO, align: 'center', fontFace: 'Arial', margin: 0 });
                slide.addText(it.lbl, { x: bx, y: 0.38, w: 0.95, h: 0.2, fontSize: 8, color: '666666', align: 'center', fontFace: 'Arial', margin: 0 });
            });
        }

        if (!u) {
            slide.addText('Sin datos de intervención', { x: 0.3, y: 1.5, w: 9.4, h: 1, fontSize: 16, color: '666666', align: 'center', fontFace: 'Arial' });
            // Footer
            slide.addShape('rect', { x: 0, y: 5.3, w: 10, h: 0.07, fill: { color: NARANJA }, line: { color: NARANJA } });
            slide.addText('Metso', { x: 8.5, y: 5.38, w: 1.3, h: 0.22, fontSize: 9, color: '666666', align: 'right', fontFace: 'Arial' });
            continue;
        }

        // ── COLUMNA IZQUIERDA: semáforo ──────────────────────────
        const colX = 0.15;
        const colY = 1.02;
        const colW = 3.1;

        // Calcular estados
        const mflVals = ['a','b','c','d','e','f','g'].map(x => safeNum(u[`mfl_med_${x}`]));
        const mflProm = promedio(mflVals);
        const slVals = [1,2,3,4,5,6].flatMap(i => [safeNum(u[`socket_b${i}`]), safeNum(u[`socket_a${i}`])]);
        const slProm = promedio(slVals);
        const gapVals = [safeNum(u.socket_gap_0), safeNum(u.socket_gap_90), safeNum(u.socket_gap_180), safeNum(u.socket_gap_270)];
        const gapProm = promedio(gapVals);

        const componentesInfo = [
            {
                nombre: 'Socket Liner',
                estado: estadoSemaforo(slProm, 5, 10),
                detalle: slProm !== null ? `${slProm}mm` : '-',
                cambio: u.sl_cambio_ahora === 'SI' ? `Cambiado ${safe(u.fecha_inicio).substring(0,10)}` : (ultimoCambio(cambios, 'sl_cambio_ahora') ? `Últ. cambio: ${ultimoCambio(cambios, 'sl_cambio_ahora')}` : 'Sin cambio reciente'),
            },
            {
                nombre: 'Socket',
                estado: estadoSemaforo(gapProm, 0, 0.5),
                detalle: gapProm !== null ? `GAP ${gapProm}mm` : '-',
                cambio: u.socket_cambio_ahora === 'SI' ? `Cambiado ${safe(u.fecha_inicio).substring(0,10)}` : (ultimoCambio(cambios, 'socket_cambio_ahora') ? `Últ. cambio: ${ultimoCambio(cambios, 'socket_cambio_ahora')}` : 'Sin cambio reciente'),
            },
            {
                nombre: 'MFL',
                estado: mflProm !== null ? (mflProm < 12 ? 'rojo' : mflProm < 18 ? 'amarillo' : 'verde') : 'sin_dato',
                detalle: mflProm !== null ? `${mflProm}mm` : '-',
                cambio: u.mfl_cambio_ahora === 'SI' ? `Cambiado ${safe(u.fecha_inicio).substring(0,10)}` : (ultimoCambio(cambios, 'mfl_cambio_ahora') ? `Últ. cambio: ${ultimoCambio(cambios, 'mfl_cambio_ahora')}` : 'Sin cambio reciente'),
            },
            {
                nombre: 'Monturas',
                estado: u.montura_barras_estado === 'Malo' ? 'rojo' : u.montura_barras_estado === 'Bueno' ? 'verde' : 'amarillo',
                detalle: safe(u.montura_barras_estado),
                cambio: u.montura_cambio_ahora === 'SI' ? `Cambiado ${safe(u.fecha_inicio).substring(0,10)}` : (ultimoCambio(cambios, 'montura_cambio_ahora') ? `Últ. cambio: ${ultimoCambio(cambios, 'montura_cambio_ahora')}` : 'Sin cambio reciente'),
            },
            {
                nombre: 'Guard Pins',
                estado: safe(u.gp1_cambio) === 'SI' ? 'amarillo' : 'verde',
                detalle: safe(u.gp1_medida) !== '-' ? String(u.gp1_medida) : '-',
                cambio: 'Inspección normal',
            },
            {
                nombre: 'Protectores',
                estado: safe(u.prot_estatico_estado) === 'Malo' ? 'rojo' : 'verde',
                detalle: safe(u.prot_estatico_estado),
                cambio: 'Sin observaciones',
            },
        ];

        componentesInfo.forEach((comp, i) => {
            const ry = colY + i * 0.7;
            const col = colorSemaforo(comp.estado);

            // Barra izquierda color
            slide.addShape('rect', { x: colX, y: ry, w: 0.06, h: 0.6, fill: { color: col }, line: { color: col } });
            // Fondo
            slide.addShape('rect', { x: colX + 0.06, y: ry, w: colW - 0.06, h: 0.6, fill: { color: '1A1A1A' }, line: { color: '2A2A2A', width: 0.5 } });

            slide.addText(comp.nombre, { x: colX + 0.14, y: ry + 0.04, w: 1.5, h: 0.28, fontSize: 11, bold: true, color: BLANCO, fontFace: 'Arial', margin: 0 });
            slide.addText(comp.detalle, { x: colX + 1.7, y: ry + 0.04, w: 1.4, h: 0.28, fontSize: 11, color: col, bold: true, align: 'right', fontFace: 'Arial', margin: 0 });
            slide.addText(comp.cambio, { x: colX + 0.14, y: ry + 0.34, w: 2.85, h: 0.22, fontSize: 8, color: '888888', fontFace: 'Arial', margin: 0 });
        });

        // Recomendación
        const recY = colY + componentesInfo.length * 0.7 + 0.05;
        slide.addShape('rect', { x: colX, y: recY, w: colW, h: 0.65, fill: { color: '1A0A00' }, line: { color: NARANJA, width: 0.5 } });
        slide.addText('RECOMENDACIÓN', { x: colX + 0.1, y: recY + 0.03, w: colW - 0.2, h: 0.18, fontSize: 8, bold: true, color: NARANJA, fontFace: 'Arial', margin: 0 });
        const recTexto = safe(u.recomendaciones, 'Sin recomendaciones').substring(0, 120);
        slide.addText(recTexto, { x: colX + 0.1, y: recY + 0.2, w: colW - 0.2, h: 0.4, fontSize: 8, color: BLANCO, fontFace: 'Arial', margin: 0 });

        // ── COLUMNA DERECHA: 4 gráficos ──────────────────────────
        const gx = 3.4;
        const gw = 3.1;
        const gh = 2.1;

        // Etiquetas de fechas del historial
        const fechasHist = hist.map(h => String(h.fecha_inicio || '').substring(5, 10));

        // Gráfico 1: MFL
        if (hist.length > 0) {
            const mflData = hist.map(h => {
                const vals = ['a','b','c','d','e','f','g'].map(x => safeNum(h[`mfl_med_${x}`]));
                return promedio(vals) || 0;
            });
            slide.addText('MFL promedio (mm)', { x: gx, y: 0.95, w: gw, h: 0.2, fontSize: 9, color: '888888', fontFace: 'Arial', margin: 0 });
            addLineChart(slide, fechasHist,
                [{ name: 'MFL', values: mflData, color: NARANJA }],
                gx, 1.12, gw, gh,
                { valMin: 0, valMax: Math.max(35, Math.max(...mflData) * 1.1), refLines: [{ val: 9, label: 'Mín 9mm', color: ROJO }] }
            );
        }

        // Gráfico 2: Socket Liner
        const slDataHist = hist.map(h => {
            const vals = [1,2,3,4,5,6].flatMap(i => [safeNum(h[`socket_b${i}`]), safeNum(h[`socket_a${i}`])]);
            return promedio(vals) || 0;
        });
        if (hist.length > 0) {
            slide.addText('Socket Liner promedio (mm)', { x: gx + gw + 0.2, y: 0.95, w: gw, h: 0.2, fontSize: 9, color: '888888', fontFace: 'Arial', margin: 0 });
            addLineChart(slide, fechasHist,
                [{ name: 'SL', values: slDataHist, color: NARANJA }],
                gx + gw + 0.2, 1.12, gw, gh,
                { valMin: 0, valMax: 15, refLines: [{ val: 5, label: 'Mín 5', color: ROJO }, { val: 10, label: 'Máx 10', color: AMARILLO }], showLegend: false }
            );
        }

        // Gráfico 3: GAP Socket
        const gapData = hist.map(h => {
            const gv = [safeNum(h.socket_gap_0), safeNum(h.socket_gap_90), safeNum(h.socket_gap_180), safeNum(h.socket_gap_270)];
            return promedio(gv) || 0;
        });
        if (hist.length > 0) {
            slide.addText('GAP Socket-Mainshaft (mm)', { x: gx, y: 3.35, w: gw, h: 0.2, fontSize: 9, color: '888888', fontFace: 'Arial', margin: 0 });
            addLineChart(slide, fechasHist,
                [{ name: 'GAP', values: gapData, color: NARANJA }],
                gx, 3.52, gw, gh - 0.3,
                { valMin: 0, valMax: Math.max(5, Math.max(...gapData) * 1.2), refLines: [{ val: 0, label: 'Óptimo 0', color: VERDE }] }
            );
        }

        // Gráfico 4: Altura Bowl + proyección
        const proy = calcProyeccion(d.alturas);
        if (proy && proy.dias.length > 1) {
            const altLabels = proy.fechas.map(f => f.toISOString().substring(5, 10));
            // Proyección: extender hasta diaLimite
            const extraDias = Math.min(30, Math.ceil(proy.diaLimite * 0.2));
            const proyLabels = [];
            const proyVals = [];
            for (let dd = proy.dias[proy.dias.length - 1]; dd <= proy.diaLimite + extraDias; dd += Math.ceil((proy.diaLimite - proy.dias[0]) / 10) || 1) {
                const f = new Date(proy.fechas[0].getTime() + dd * 86400000);
                proyLabels.push(f.toISOString().substring(5, 10));
                proyVals.push(Math.max(0, Math.round((proy.m * dd + proy.b) * 100) / 100));
            }

            const allLabels = [...new Set([...altLabels, ...proyLabels])].sort();
            const realMap = {};
            proy.fechas.forEach((f, i) => { realMap[f.toISOString().substring(5, 10)] = proy.vals[i]; });
            const proyMap = {};
            proyLabels.forEach((l, i) => { proyMap[l] = proyVals[i]; });

            const realSeries = allLabels.map(l => realMap[l] !== undefined ? realMap[l] : null);
            const proyeSeries = allLabels.map(l => proyMap[l] !== undefined ? proyMap[l] : null);
            
            const diasRest = Math.ceil((new Date(proy.fechas[0].getTime() + proy.diaLimite * 86400000) - new Date()) / 86400000);
            const colorDias = diasRest <= 3 ? ROJO : diasRest <= 7 ? AMARILLO : VERDE;
            slide.addText(`Altura Bowl — próx. cambio: ${proy.semana}  ·  ${proy.fecha}`, { x: gx + gw + 0.2, y: 3.35, w: gw - 0.8, h: 0.2, fontSize: 9, color: '888888', fontFace: 'Arial', margin: 0 });
            slide.addText(`${diasRest} días restantes`, { x: gx + gw + gw - 0.4, y: 3.35, w: 1.0, h: 0.2, fontSize: 9, bold: true, color: colorDias, fontFace: 'Arial', margin: 0, align: 'right' });
            
            addLineChart(slide, allLabels,
                [
                    { name: 'Real', values: realSeries, color: NARANJA, lineSize: 2, symbol: 'circle', symbolSize: 4 },
                    { name: 'Proyección', values: proyeSeries, color: '4488CC', lineSize: 1, symbol: 'none', symbolSize: 0 },
                ],
                gx + gw + 0.2, 3.52, gw, gh - 0.3,
                { valMin: 7, valMax: 23, showLegend: true, refLines: [{ val: 9, label: 'Límite 9"', color: ROJO }] }
            );
        } else {
            slide.addText('Altura Bowl', { x: gx + gw + 0.2, y: 3.35, w: gw, h: 0.2, fontSize: 9, color: '888888', fontFace: 'Arial', margin: 0 });
            slide.addShape('rect', { x: gx + gw + 0.2, y: 3.52, w: gw, h: gh - 0.3, fill: { color: '1A1A1A' }, line: { color: '333333', width: 0.5 } });
            slide.addText('Sin datos de altura', { x: gx + gw + 0.2, y: 3.52, w: gw, h: gh - 0.3, fontSize: 10, color: '555555', align: 'center', valign: 'middle', fontFace: 'Arial' });
        }

        // Footer
        slide.addShape('rect', { x: 0, y: 5.38, w: 10, h: 0.07, fill: { color: NARANJA }, line: { color: NARANJA } });
        slide.addText('Metso', { x: 8.5, y: 5.46, w: 1.3, h: 0.18, fontSize: 8, color: '666666', align: 'right', fontFace: 'Arial' });
        slide.addText(fecha, { x: 0.3, y: 5.46, w: 3, h: 0.18, fontSize: 8, color: '666666', fontFace: 'Arial' });
    }

    // ═══════════════════════════════════════════════════════════
    // SLIDE CIERRE
    // ═══════════════════════════════════════════════════════════
    const sc = pres.addSlide();
    sc.background = { color: NEGRO };
    addDots(sc, 4.0, 0.2, 20, 16, 0.30, '222222', 0.04);

    sc.addText('Metso', { x: 0.5, y: 0.5, w: 3, h: 0.6, fontSize: 28, bold: true, color: BLANCO, fontFace: 'Arial' });
    sc.addText('Partner for\npositive change', { x: 0.5, y: 1.4, w: 5, h: 1.2, fontSize: 26, bold: true, color: BLANCO, fontFace: 'Arial' });
    sc.addText('metso.com', { x: 0.5, y: 4.8, w: 3, h: 0.35, fontSize: 12, color: '666666', fontFace: 'Arial' });
    sc.addShape('rect', { x: 0, y: 5.32, w: 10, h: 0.07, fill: { color: NARANJA }, line: { color: NARANJA } });

    return pres.write({ outputType: 'base64' });
}

// ── Entrada/Salida ─────────────────────────────────────────────
let raw = '';
process.stdin.on('data', chunk => raw += chunk);
process.stdin.on('end', () => {
    const payload = JSON.parse(raw);
    generarPPT(payload).then(b64 => {
        process.stdout.write(b64);
    }).catch(err => {
        process.stderr.write(String(err));
        process.exit(1);
    });
});
