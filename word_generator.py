from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os
from datetime import datetime

# ── Helpers de estilo ─────────────────────────────────────────

def set_cell_bg(cell, color_hex):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color_hex)
    tcPr.append(shd)

def set_cell_borders(cell):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for side in ['top','left','bottom','right']:
        border = OxmlElement(f'w:{side}')
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), '4')
        border.set(qn('w:color'), 'CCCCCC')
        tcBorders.append(border)
    tcPr.append(tcBorders)

def bold_cell(cell, text, size=10, color=None, bg=None, align=WD_ALIGN_PARAGRAPH.LEFT):
    cell.text = ''
    p = cell.paragraphs[0]
    p.alignment = align
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(size)
    if color:
        run.font.color.rgb = RGBColor(*bytes.fromhex(color))
    if bg:
        set_cell_bg(cell, bg)
    set_cell_borders(cell)

def normal_cell(cell, text, size=9, bold=False, align=WD_ALIGN_PARAGRAPH.LEFT, bg=None):
    cell.text = ''
    p = cell.paragraphs[0]
    p.alignment = align
    run = p.add_run(str(text) if text else '')
    run.font.size = Pt(size)
    run.bold = bold
    if bg:
        set_cell_bg(cell, bg)
    set_cell_borders(cell)

def add_section_title(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0x1A, 0x3A, 0x5C)

def add_section_title_green(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0x0F, 0x51, 0x32)

def add_subsection_title(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x1A, 0x3A, 0x5C)

def add_banner(doc, text, color='28A745'):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f'  {text}  ')
    run.bold = True
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color)
    pPr.append(shd)

def add_inspeccion_table(doc, filas, header_color='1A3A5C'):
    tabla = doc.add_table(rows=1, cols=3)
    tabla.style = 'Table Grid'
    tabla.columns[0].width = Cm(9)
    tabla.columns[1].width = Cm(2.5)
    tabla.columns[2].width = Cm(6)
    bold_cell(tabla.cell(0,0), 'Descripción', bg=header_color, color='FFFFFF', align=WD_ALIGN_PARAGRAPH.CENTER)
    bold_cell(tabla.cell(0,1), 'Estado', bg=header_color, color='FFFFFF', align=WD_ALIGN_PARAGRAPH.CENTER)
    bold_cell(tabla.cell(0,2), 'Observaciones', bg=header_color, color='FFFFFF', align=WD_ALIGN_PARAGRAPH.CENTER)
    for desc, estado, obs in filas:
        row = tabla.add_row()
        normal_cell(row.cells[0], desc)
        est_bg = 'E8F5E9' if estado == 'Bueno' else ('FFEBEE' if estado == 'Malo' else 'FFFFFF')
        normal_cell(row.cells[1], estado, align=WD_ALIGN_PARAGRAPH.CENTER, bg=est_bg)
        normal_cell(row.cells[2], obs)
    doc.add_paragraph()

def add_metro_tabla(doc, titulo, mediciones, header_color='E8F0FE', label_color=(0x1A,0x3A,0x5C)):
    p = doc.add_paragraph()
    run = p.add_run(titulo)
    run.bold = True
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(*label_color)
    tabla = doc.add_table(rows=1, cols=3)
    tabla.style = 'Table Grid'
    bold_cell(tabla.cell(0,0), 'Punto', bg=header_color, align=WD_ALIGN_PARAGRAPH.CENTER)
    bold_cell(tabla.cell(0,1), 'A (0°)', bg=header_color, align=WD_ALIGN_PARAGRAPH.CENTER)
    bold_cell(tabla.cell(0,2), 'B (90°)', bg=header_color, align=WD_ALIGN_PARAGRAPH.CENTER)
    for punto, a, b in mediciones:
        row = tabla.add_row()
        normal_cell(row.cells[0], punto, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        normal_cell(row.cells[1], str(a) if a else '-', align=WD_ALIGN_PARAGRAPH.CENTER)
        normal_cell(row.cells[2], str(b) if b else '-', align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph()

def add_cotas_tabla(doc, titulo, datos, prefijo):
    p = doc.add_paragraph()
    run = p.add_run(titulo)
    run.bold = True
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x0F, 0x51, 0x32)
    tabla = doc.add_table(rows=1, cols=5)
    tabla.style = 'Table Grid'
    for i, h in enumerate(['COTA REAL', '1 (0°)', '2 (45°)', '3 (90°)', '4 (135°)']):
        bold_cell(tabla.cell(0,i), h, bg='D1E7DD', align=WD_ALIGN_PARAGRAPH.CENTER)
    for letra in ['A','B','C','D']:
        row = tabla.add_row()
        normal_cell(row.cells[0], letra, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        for j in range(1,5):
            v = datos.get(f'{prefijo}_{letra}{j}','')
            normal_cell(row.cells[j], str(v) if v else '-', align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph()

def add_imagen(doc, ruta):
    if os.path.exists(ruta):
        try:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run()
            run.add_picture(ruta, width=Cm(8))
        except:
            pass

# ══════════════════════════════════════════════════════════════
# GENERADOR ARMADO
# ══════════════════════════════════════════════════════════════

def generar_word_armado(datos):
    doc = Document()
    for section in doc.sections:
        section.top_margin = Cm(1.5)
        section.bottom_margin = Cm(1.5)
        section.left_margin = Cm(2)
        section.right_margin = Cm(2)

    tabla_enc = doc.add_table(rows=1, cols=3)
    tabla_enc.style = 'Table Grid'
    bold_cell(tabla_enc.cell(0,0), 'Metso', size=18, color='FF6600', bg='FFFFFF', align=WD_ALIGN_PARAGRAPH.CENTER)
    bold_cell(tabla_enc.cell(0,1), 'PROTOCOLO ARMADO DE HEAD Y BOWL', size=12, color='FFFFFF', bg='1A3A5C', align=WD_ALIGN_PARAGRAPH.CENTER)
    fecha = datos.get('fecha_inicio','').replace('-','') if datos.get('fecha_inicio') else ''
    folio = f"HB-{fecha}{str(hash(str(datos)))[-5:]}"
    normal_cell(tabla_enc.cell(0,2), folio, size=9, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph()

    tabla_dg = doc.add_table(rows=5, cols=4)
    tabla_dg.style = 'Table Grid'
    campos_dg = [
        ('EQUIPO', datos.get('equipo','')),
        ('SUPERVISOR METSO', datos.get('supervisor_metso','')),
        ('CLIENTE', datos.get('cliente','')),
        ('SUPERVISOR CLIENTE', datos.get('supervisor_cliente','')),
        ('ID BOWL', datos.get('id_bowl','')),
        ('FECHA DE INICIO', datos.get('fecha_inicio','')),
        ('ID HEAD', datos.get('id_head','')),
        ('FECHA DE TERMINO', datos.get('fecha_termino','')),
        ('HORA INICIO', f"{datos.get('hora_inicio_h','')}: {datos.get('hora_inicio_m','')}"),
        ('HORA FIN', f"{datos.get('hora_fin_h','')}: {datos.get('hora_fin_m','')}"),
    ]
    for i, (label, valor) in enumerate(campos_dg):
        fila = i // 2
        col_l = (i % 2) * 2
        bold_cell(tabla_dg.cell(fila, col_l), label, size=9, bg='E8F0FE')
        normal_cell(tabla_dg.cell(fila, col_l+1), valor, size=9)
    doc.add_paragraph()

    add_section_title(doc, 'SECCIÓN 1 - HEAD')
    add_section_title(doc, 'INSPECCIÓN DE UPPER BUSHING')
    add_inspeccion_table(doc, [
        ('1. Realizar la inspección visual de la superficie del upper bushing (golpes, rayones, huellas, etc.)', datos.get('ub_paso1_estado',''), datos.get('ub_paso1_obs','')),
        ('1.1.1. De encontrar desprendimiento de material, fisuras u otro similar aplicar NDT y evidenciar mediante imágenes', '', datos.get('ub_paso2_obs','')),
        ('Inspeccionar el estado de las 4 chavetas y los 6 pernos M16 de fijación de cada una.', datos.get('ub_paso3_estado',''), datos.get('ub_paso3_obs','')),
        ('Verificar el Torque de los pernos a 260 N.m (192 Lb.ft), y evidenciar con el serial number de la herramienta.', datos.get('ub_paso4_estado',''), datos.get('ub_paso4_obs','')),
        ('Verificar el estado del seguro alambre de los pernos', datos.get('ub_paso5_estado',''), datos.get('ub_paso5_obs','')),
        ('¿Requiere cambio de Upper Bushing?', datos.get('upper_bushing_cambio','NO'), ''),
    ])
    if datos.get('upper_bushing_cambio','NO') == 'NO':
        add_banner(doc, 'NO REQUIERE CAMBIO (REALIZAR METROLOGÍA)', '28A745')
    else:
        add_banner(doc, 'SI REQUIERE CAMBIO (REALIZAR MONTAJE Y METROLOGÍA)', 'FFC107')
    add_metro_tabla(doc, 'Control de Mediciones Upper Bushing', [
        ('A1/B1', datos.get('upper_A1',''), datos.get('upper_B1','')),
        ('A2/B2', datos.get('upper_A2',''), datos.get('upper_B2','')),
        ('A3/B3', datos.get('upper_A3',''), datos.get('upper_B3','')),
    ])
    add_imagen(doc, 'static/imagenes/upper_bushing.png')
    if datos.get('upper_bushing_cambio','NO') == 'SI':
        add_subsection_title(doc, 'Montaje de Upper Bushing')
        add_inspeccion_table(doc, [
            ('7. Indicar si durante el retiro de la bocina se encontraron pernos cizallados u otros', '', datos.get('ub_paso7_obs','')),
            ('8. Inspección visual del estado de la superficie del alojamiento de la bocina - upper hd bsh', '', datos.get('ub_paso8_obs','')),
            ('9. De encontrar alguna anomalía como rajaduras aplicar NDT - líquidos penetrantes y evidenciar', '', datos.get('ub_paso9_obs','')),
            ('10. Control dimensional del alojamiento del upper bushing', '', datos.get('ub_paso10_obs','')),
            ('11. Enfriar la bocina al menos 20°C debajo de la T. ambiente', '', datos.get('ub_paso11_obs','')),
            ('12. Realizar el centrado de las 04 chavetas tipo "L" durante el montaje', '', datos.get('ub_paso12_obs','')),
            ('13. Ajustar 06 pernos M16x60 en cada chaveta tipo "L" — Torque 260 N.m', '', datos.get('ub_paso13_obs','')),
            ('14. Asegurar los pernos ajustados con el alambre de ajuste', '', datos.get('ub_paso14_obs','')),
            ('15. Control dimensional del upper bushing nuevo instalado', '', datos.get('ub_paso15_obs','')),
        ])
        add_imagen(doc, 'static/imagenes/chavetas.png')
        add_metro_tabla(doc, 'Control de Mediciones Upper Bushing Nuevo', [
            ('A1/B1', datos.get('upper_nuevo_A1',''), datos.get('upper_nuevo_B1','')),
            ('A2/B2', datos.get('upper_nuevo_A2',''), datos.get('upper_nuevo_B2','')),
            ('A3/B3', datos.get('upper_nuevo_A3',''), datos.get('upper_nuevo_B3','')),
        ])

    add_section_title(doc, 'INSPECCIÓN DE LOWER BUSHING')
    add_inspeccion_table(doc, [
        ('16. Realizar inspección visual de la superficie del lower bushing (golpes, rayones, huellas, etc.)', datos.get('lb_paso16_estado',''), datos.get('lb_paso16_obs','')),
        ('16.1. De encontrar desprendimiento de material, fisuras u otro similar aplicar NDT y evidenciar', '', datos.get('lb_paso161_obs','')),
        ('17. Inspeccionar el estado de los 16 pernos de fijación M20 x 70 — 325 N.m (240 Lb.ft)', datos.get('lb_paso17_estado',''), datos.get('lb_paso17_obs','')),
        ('18. ¿Requiere cambio de Lower Bushing?', datos.get('lower_bushing_cambio','NO'), ''),
    ])
    if datos.get('lower_bushing_cambio','NO') == 'NO':
        add_banner(doc, 'NO REQUIERE CAMBIO (REALIZAR METROLOGÍA)', '28A745')
    else:
        add_banner(doc, 'SI REQUIERE CAMBIO (REALIZAR MONTAJE Y METROLOGÍA)', 'FFC107')
    add_metro_tabla(doc, 'Control de Mediciones Bocina de la Excéntrica', [
        ('A1/B1', datos.get('lower_A1',''), datos.get('lower_B1','')),
        ('A2/B2', datos.get('lower_A2',''), datos.get('lower_B2','')),
        ('A3/B3', datos.get('lower_A3',''), datos.get('lower_B3','')),
        ('A4/B4', datos.get('lower_A4',''), datos.get('lower_B4','')),
        ('A5/B5', datos.get('lower_A5',''), datos.get('lower_B5','')),
        ('A6/B6', datos.get('lower_A6',''), datos.get('lower_B6','')),
    ])
    add_imagen(doc, 'static/imagenes/lower_bushing.png')
    if datos.get('lower_bushing_cambio','NO') == 'SI':
        add_subsection_title(doc, 'Montaje de Lower Bushing')
        add_inspeccion_table(doc, [
            ('21. Realizar el corte de la bocina durante su desmontaje', '', datos.get('lb_paso21_obs','')),
            ('22. Inspección visual del estado de la superficie del alojamiento de la bocina', '', datos.get('lb_paso22_obs','')),
            ('22.1. De encontrar anomalías como rajaduras aplicar NDT - líquidos penetrantes', '', datos.get('lb_paso221_obs','')),
            ('24. Enfriar la bocina al menos 18°C debajo de la T. ambiente', '', datos.get('lb_paso24_obs','')),
            ('25. Cambiar pernos y arandelas a instalar', '', datos.get('lb_paso25_obs','')),
            ('26. Reemplazar los 16 pernos M20x70 con sus arandelas y Loctite Threadlocker 325 N.m', '', datos.get('lb_paso26_obs','')),
        ])
        add_metro_tabla(doc, 'Control de Mediciones Lower Bushing Nuevo', [
            ('A1/B1', datos.get('lower_nuevo_A1',''), datos.get('lower_nuevo_B1','')),
            ('A2/B2', datos.get('lower_nuevo_A2',''), datos.get('lower_nuevo_B2','')),
            ('A3/B3', datos.get('lower_nuevo_A3',''), datos.get('lower_nuevo_B3','')),
            ('A4/B4', datos.get('lower_nuevo_A4',''), datos.get('lower_nuevo_B4','')),
            ('A5/B5', datos.get('lower_nuevo_A5',''), datos.get('lower_nuevo_B5','')),
            ('A6/B6', datos.get('lower_nuevo_A6',''), datos.get('lower_nuevo_B6','')),
        ])

    add_section_title(doc, 'HEAD BALL')
    add_inspeccion_table(doc, [
        ('28. Inspección visual de la superficie del Head Ball (golpes, rayones, huellas, etc.)', datos.get('hb_paso28_estado',''), datos.get('hb_paso28_obs','')),
        ('29. Inspeccionar estado de la cabeza de pernos de sujeción cuando el Head esté desarmado', datos.get('hb_paso29_estado',''), datos.get('hb_paso29_obs','')),
        ('30. ¿Requiere cambio de Head Ball?', datos.get('head_ball_cambio','NO'), ''),
    ])
    if datos.get('head_ball_cambio','NO') == 'NO':
        add_banner(doc, 'NO REQUIERE CAMBIO', '28A745')
    else:
        add_banner(doc, 'SI REQUIERE CAMBIO (REALIZAR SIGUIENTES PASOS)', 'FFC107')
        add_inspeccion_table(doc, [
            ('31. Enfriar Head Ball hasta diferencia de 47°C con el Head', datos.get('hb_paso31_real',''), datos.get('hb_paso31_obs','')),
            ('32. Ajuste de los 04 pernos M20 x 200 a 170 N.m (125 Lb.ft)', datos.get('hb_paso32_real',''), datos.get('hb_paso32_obs','')),
            ('33. Aplicar Silastic - Dow Corning 732 en el conjunto perno arandela', datos.get('hb_paso33_real',''), datos.get('hb_paso33_obs','')),
        ])

    add_section_title(doc, 'CARTER')
    add_inspeccion_table(doc, [
        ('34. Realizar inspección del carter superior (que no presente fisuras en su superficie)', datos.get('carter_sup_estado',''), datos.get('carter_sup_obs','')),
        ('35. Realizar inspección del carter inferior (que no presente fisuras en su superficie)', datos.get('carter_inf_estado',''), datos.get('carter_inf_obs','')),
    ])
    add_imagen(doc, 'static/imagenes/carter.png')

    add_section_title(doc, 'FEED PLATE')
    add_inspeccion_table(doc, [
        ('36. Inspeccionar el estado del feed plate', datos.get('feed_plate_estado',''), datos.get('fp_paso36_obs','')),
        ('37. ¿Requiere cambio Feed Plate?', datos.get('feed_plate_cambio','NO'), f"Medida: {datos.get('feed_plate_altura','')} mm | Desgaste: {datos.get('feed_plate_desgaste','')}% | Mín: 50mm | Nominal: 124mm"),
        ('38. Verificar estado de los asientos de los pernos cortados salientes del Feed Plate', datos.get('fp_paso38_estado',''), datos.get('fp_paso38_obs','')),
        ('39. Realizar limpieza de la superficie del Head (amoladora)', datos.get('fp_paso39_estado',''), datos.get('fp_paso39_obs','')),
        ('40. Aplicar una capa de aceite la parte superior del Head', '', datos.get('fp_paso40_obs','')),
    ])

    add_section_title(doc, 'LOCKING NUT')
    add_inspeccion_table(doc, [
        ('41. Inspeccionar el estado del Locking Nut', datos.get('ln_paso41_estado',''), datos.get('ln_paso41_obs','')),
        ('42. Diámetro del Locking Nut', '', datos.get('ln_diametro','')),
        ('43. Verificar espaciamiento homogéneo entre Torch Ring y Locking Nut', '', datos.get('ln_espaciamiento','')),
        ('44. Torque Inicial al 50%', '', datos.get('ln_torque50','')),
        ('45. Torque Inicial al 75%', '', datos.get('ln_torque75','')),
        ('46. Torque Inicial al 100%', '', datos.get('ln_torque100','')),
        ('46.1. Número de serie del torquímetro', '', datos.get('ln_serial_torq','')),
        ('47. GAP Final: 1.0 mm a 1.5 mm (Locking Nut - Torch Ring)', '', datos.get('ln_gap1','')),
        ('48. GAP Final: 0 a 0.25 mm (Manto Inferior y Head)', '', datos.get('ln_gap2','')),
    ])
    add_imagen(doc, 'static/imagenes/locking_nut.png')

    add_section_title(doc, 'EPÓXICO Y BACKING')
    add_inspeccion_table(doc, [
        ('49. Cantidad requerida de epóxico', '', datos.get('epoxi_cantidad','')),
        ('50. Fecha Vencimiento Catalizador', '', datos.get('epoxi_venc_catalizador','')),
        ('51. Fecha Vencimiento Epóxico', '', datos.get('epoxi_venc_epoxico','')),
        ('52. T° del batido sin catalizador (15°C - 20°C)', '', datos.get('epoxi_temp_sin_cat','')),
        ('53. T° del batido con catalizador (24°C - 28°C)', '', datos.get('epoxi_temp_con_cat','')),
    ])

    add_section_title(doc, 'SECCIÓN 2 - INSPECCIÓN DE BOWL')
    add_inspeccion_table(doc, [
        ('54. Inspeccionar el estado del Hooper', datos.get('bowl_paso54_estado',''), datos.get('bowl_paso54_obs','')),
        ('55. Medida tomada al Hooper (mm)', '', datos.get('bowl_medida_hooper','')),
        ('56. Verificar estado de las roscas con peineta', datos.get('bowl_paso56_estado',''), datos.get('bowl_paso56_obs','')),
        ('57. Inspeccionar estado de conjuntos cuñas, tuercas esféricas y placas de bloqueo', datos.get('bowl_paso57_estado',''), datos.get('bowl_paso57_obs','')),
        ('58. Verificar estado del asiento del Bowl - Bowl Liner (fisuras)', datos.get('bowl_paso58_estado',''), datos.get('bowl_paso58_obs','')),
        ('58.1. Indicar medida de fisuras', '', datos.get('bowl_medida_fisuras','')),
        ('58.2. Realizar prueba NDT e indicar observaciones', '', datos.get('bowl_paso582_obs','')),
        ('60. Verificar estado de anillo adaptador', datos.get('bowl_paso60_estado',''), datos.get('bowl_paso60_obs','')),
        ('61. Verificar el ajuste de las tuercas esféricas de los pernos cuña', datos.get('bowl_paso61_estado',''), datos.get('bowl_paso61_obs','')),
        ('62. Verificar estado de los hilos del Bowl (fisuras)', datos.get('bowl_paso62_estado',''), datos.get('bowl_paso62_obs','')),
        ('62.1. Medida de fisura', '', datos.get('bowl_medida_fisura62','')),
        ('62.2. Realizar NDT e indicar observaciones', '', datos.get('bowl_paso622_obs','')),
    ])

    fotos = [k for k in datos.keys() if k.startswith('foto_path_')]
    if fotos:
        add_section_title(doc, 'REGISTRO FOTOGRÁFICO')
        for foto_key in fotos:
            ruta_foto = datos[foto_key]
            if ruta_foto and os.path.exists(ruta_foto):
                nombre = foto_key.replace('foto_path_','').replace('_',' ').upper()
                doc.add_paragraph(nombre)
                add_imagen(doc, ruta_foto)

    add_section_title(doc, 'RECOMENDACIONES PARA LA SIGUIENTE INTERVENCIÓN')
    doc.add_paragraph(datos.get('recomendaciones',''))

    doc.add_paragraph()
    tabla_firma = doc.add_table(rows=2, cols=2)
    tabla_firma.style = 'Table Grid'
    bold_cell(tabla_firma.cell(0,0), 'SUPERVISOR METSO', bg='E8F0FE', align=WD_ALIGN_PARAGRAPH.CENTER)
    bold_cell(tabla_firma.cell(0,1), 'SUPERVISOR CLIENTE', bg='E8F0FE', align=WD_ALIGN_PARAGRAPH.CENTER)
    normal_cell(tabla_firma.cell(1,0), datos.get('supervisor_metso',''))
    normal_cell(tabla_firma.cell(1,1), datos.get('supervisor_cliente',''))

    doc.add_paragraph()
    p_fecha = doc.add_paragraph(f'Reporte generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}')
    p_fecha.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_fecha.runs[0].font.size = Pt(8)
    p_fecha.runs[0].font.color.rgb = RGBColor(0x99, 0x99, 0x99)

    os.makedirs('reportes', exist_ok=True)
    nombre = f'reportes/Armado_HB_{datos.get("equipo","X")}_{datetime.now().strftime("%Y%m%d_%H%M")}.docx'
    doc.save(nombre)
    return nombre


# ══════════════════════════════════════════════════════════════
# GENERADOR CAMBIO
# ══════════════════════════════════════════════════════════════

def generar_word_cambio(datos):
    doc = Document()
    for section in doc.sections:
        section.top_margin = Cm(1.5)
        section.bottom_margin = Cm(1.5)
        section.left_margin = Cm(2)
        section.right_margin = Cm(2)

    # ── ENCABEZADO ──────────────────────────────────────────
    tabla_enc = doc.add_table(rows=1, cols=3)
    tabla_enc.style = 'Table Grid'
    bold_cell(tabla_enc.cell(0,0), 'Metso', size=18, color='FF6600', bg='FFFFFF', align=WD_ALIGN_PARAGRAPH.CENTER)
    bold_cell(tabla_enc.cell(0,1), 'PROTOCOLO CAMBIO DE HEAD Y BOWL', size=12, color='FFFFFF', bg='0F5132', align=WD_ALIGN_PARAGRAPH.CENTER)
    fecha = datos.get('fecha_inicio','').replace('-','') if datos.get('fecha_inicio') else ''
    folio = f"CHB-{fecha}{str(hash(str(datos)))[-5:]}"
    normal_cell(tabla_enc.cell(0,2), folio, size=9, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph()

    # ── DATOS GENERALES ──────────────────────────────────────
    tabla_dg = doc.add_table(rows=4, cols=4)
    tabla_dg.style = 'Table Grid'
    campos_dg = [
        ('CHANCADORA', datos.get('chancadora','')),
        ('SUPERVISOR METSO', datos.get('supervisor_metso','')),
        ('CLIENTE', datos.get('cliente','')),
        ('SUPERVISOR CLIENTE', datos.get('supervisor_cliente','')),
        ('FECHA INICIO', datos.get('fecha_inicio','')),
        ('FECHA TERMINO', datos.get('fecha_termino','')),
        ('HORA INICIO', f"{datos.get('hora_inicio_h','')}: {datos.get('hora_inicio_m','')}"),
        ('HORA FIN', f"{datos.get('hora_fin_h','')}: {datos.get('hora_fin_m','')}"),
    ]
    for i, (label, valor) in enumerate(campos_dg):
        fila = i // 2
        col_l = (i % 2) * 2
        bold_cell(tabla_dg.cell(fila, col_l), label, size=9, bg='D1E7DD')
        normal_cell(tabla_dg.cell(fila, col_l+1), valor, size=9)
    doc.add_paragraph()

    # ── SECCIÓN 2 - ANILLO DE AJUSTE ────────────────────────
    add_section_title_green(doc, '2. INSPECCIÓN DE ANILLO DE AJUSTE')
    add_section_title_green(doc, 'Inspección de Bowl y Aro de Ajuste')
    add_inspeccion_table(doc, [
        ('Inspeccionar roscas del anillo de fijación, aro de ajuste verificando suciedad, óxido y grasa',
         datos.get('anillo_roscas_estado',''), datos.get('anillo_roscas_obs','')),
    ], header_color='0F5132')

    add_section_title_green(doc, 'Inspección de Unidad de Ajuste Hidráulico')
    add_inspeccion_table(doc, [
        ('Inspeccionar nivel de engrase y aceite en reductor del engranaje',
         datos.get('hidraulico_nivel_estado',''), datos.get('hidraulico_nivel_obs','')),
        ('Realizar medición de Gap entre Aro de transmisión y piñón (7-8 mm) — V1/V2/V3',
         '', f"{datos.get('gap_aro_v1','-')} / {datos.get('gap_aro_v2','-')} / {datos.get('gap_aro_v3','-')} mm"),
    ], header_color='0F5132')

    add_section_title_green(doc, 'Inspección de Clamping Cylinders')
    add_inspeccion_table(doc, [
        ('¿Se detectan fugas de aceite por el extremo del Clamping Cylinder?',
         datos.get('clamping_fugas_estado',''), datos.get('clamping_fugas_obs','')),
    ], header_color='0F5132')

    # ── SECCIÓN 3 - SOCKET LINER ─────────────────────────────
    add_section_title_green(doc, '3. INSPECCIÓN DE SOCKET LINER')
    add_inspeccion_table(doc, [
        ('Inspección de ranuras de aceite del Socket Liner',
         datos.get('sl_ranuras_estado',''), datos.get('sl_ranuras_obs','')),
    ], header_color='0F5132')
    add_imagen(doc, 'static/imagenes/socket_liner.png')

    add_metro_tabla(doc, 'Metrología Socket Liner', [
        ('B1/A1', datos.get('socket_B1',''), datos.get('socket_A1','')),
        ('B2/A2', datos.get('socket_B2',''), datos.get('socket_A2','')),
        ('B3/A3', datos.get('socket_B3',''), datos.get('socket_A3','')),
        ('B4/A4', datos.get('socket_B4',''), datos.get('socket_A4','')),
        ('B5/A5', datos.get('socket_B5',''), datos.get('socket_A5','')),
        ('B6/A6', datos.get('socket_B6',''), datos.get('socket_A6','')),
    ], header_color='D1E7DD', label_color=(0x0F,0x51,0x32))

    add_inspeccion_table(doc, [
        ('El asentamiento de la bola del Head en el socket liner es correcto',
         datos.get('sl_asentamiento_estado',''), datos.get('sl_asentamiento_obs','')),
        ('GAP Interior entre Socket y Socket Liner (mm)', '', str(datos.get('sl_gap_interior',''))),
        ('GAP Exterior entre Socket y Socket Liner (mm)', '', str(datos.get('sl_gap_exterior',''))),
    ], header_color='0F5132')

    add_imagen(doc, 'static/imagenes/gap_socket_liner.png')

    add_inspeccion_table(doc, [
        ('Verificar presencia de fisuras en el socket liner', datos.get('sl_fisuras_estado',''), datos.get('sl_fisuras_obs','')),
        ('Verificar presencia de deformaciones en el socket liner', datos.get('sl_deformaciones_estado',''), datos.get('sl_deformaciones_obs','')),
        ('Verificar que los canales se encuentren libres sin obstrucción', datos.get('sl_canales_estado',''), datos.get('sl_canales_obs','')),
        ('¿Se cambiará en esta intervención el Socket Liner?', datos.get('sl_cambio_ahora','NO'), ''),
        ('¿Se requiere cambio en la siguiente intervención?', datos.get('sl_cambio_siguiente','NO'), ''),
    ], header_color='0F5132')

    if datos.get('sl_cambio_ahora','NO') == 'SI':
        add_banner(doc, 'SI REQUIERE CAMBIO DE SOCKET LINER', 'FFC107')
        add_section_title_green(doc, '4. RETIRO DE SOCKET LINER')
        add_inspeccion_table(doc, [
            ('Precalentar la parte superior del socket de ser necesario para que el socket liner salga libremente', datos.get('sl_ret_precalentar',''), datos.get('sl_ret_precalentar_obs','')),
            ('Verificar la instalación los 4 tornillos extractores en los agujeros cónicos del revestimiento del socket liner', datos.get('sl_ret_tornillos',''), datos.get('sl_ret_tornillos_obs','')),
        ], header_color='0F5132')

        add_section_title_green(doc, '5. MONTAJE DE SOCKET LINER')
        add_inspeccion_table(doc, [
            ('Precalentar la parte superior del socket de ser necesario', datos.get('sl_mont_precalentar',''), datos.get('sl_mont_precalentar_obs','')),
            ('Verificar la instalación los 4 tornillos extractores', datos.get('sl_mont_tornillos',''), datos.get('sl_mont_tornillos_obs','')),
            ('Verificar enfriamiento del socket liner a menos 30°C debajo de la T. ambiente', datos.get('sl_mont_enfriamiento',''), datos.get('sl_mont_enfriamiento_obs','')),
            ('Verificar asentamiento correcto del socket liner en los 4 puntos', datos.get('sl_mont_asentamiento',''), datos.get('sl_mont_asentamiento_obs','')),
            ('GAP Interno nuevo (mm)', '', str(datos.get('sl_mont_gap_interno',''))),
            ('GAP Externo nuevo (mm)', '', str(datos.get('sl_mont_gap_externo',''))),
        ], header_color='0F5132')

    # ── SECCIÓN 6 - SOCKET ───────────────────────────────────
    add_section_title_green(doc, '6. INSPECCIÓN DE SOCKET')
    add_imagen(doc, 'static/imagenes/InspeccionSocket.png')
    add_inspeccion_table(doc, [
        ('Inspeccionar estado de socket (fisuras)', datos.get('socket_fisuras_estado',''), datos.get('socket_fisuras_obs','')),
        ('Inspeccionar los pernos del Socket', datos.get('socket_pernos_estado',''), datos.get('socket_pernos_obs','')),
        ('Inspeccionar ranuras sin obstrucciones', datos.get('socket_ranuras_estado',''), datos.get('socket_ranuras_obs','')),
        ('Inspeccionar si presenta deformaciones (zona de los pines)', datos.get('socket_deform_estado',''), datos.get('socket_deform_obs','')),
        ('Inspeccionar si presenta rotura en los canales de lubricación', datos.get('socket_canales_estado',''), datos.get('socket_canales_obs','')),
        ('GAP Socket-Mainshaft 0°', '', str(datos.get('socket_gap_0',''))),
        ('GAP Socket-Mainshaft 90°', '', str(datos.get('socket_gap_90',''))),
        ('GAP Socket-Mainshaft 180°', '', str(datos.get('socket_gap_180',''))),
        ('GAP Socket-Mainshaft 270°', '', str(datos.get('socket_gap_270',''))),
        ('¿Se cambiará en esta inspección el Socket?', datos.get('socket_cambio_ahora','NO'), ''),
        ('¿Se requiere cambio en la siguiente intervención?', datos.get('socket_cambio_siguiente','NO'), ''),
    ], header_color='0F5132')
    add_imagen(doc, 'static/imagenes/MedidaSocket.png')

    if datos.get('socket_cambio_ahora','NO') == 'SI':
        add_banner(doc, 'SI HAY CAMBIO DE SOCKET', 'FFC107')
        add_section_title_green(doc, '7. RETIRO DE SOCKET')
        add_inspeccion_table(doc, [
            ('1. Calentar el socket entre 120°C por encima de la temperatura ambiente', '', datos.get('sk_ret_calentar_obs','')),
        ], header_color='0F5132')
        add_cotas_tabla(doc, 'Posición de Cotas — Socket Saliente', datos, 'sk_sal')

        add_section_title_green(doc, '8. MONTAJE DE SOCKET')
        add_inspeccion_table(doc, [
            ('1. Calentar el socket entre 120°C por encima de la temperatura ambiente', '', datos.get('sk_mont_calentar_obs','')),
            ('2. Enfriar el socket a temperatura ambiente y volver a realizar el torque de los pernos a 2820 N.m', '', datos.get('sk_mont_enfriar_obs','')),
            ('3. GAP entre el socket y mainshaft (debe ser 0)', '', datos.get('sk_mont_gap_obs','')),
        ], header_color='0F5132')
        add_cotas_tabla(doc, 'Posición de Cotas — Socket Nuevo', datos, 'sk_new')

        add_section_title_green(doc, '9. INSPECCIÓN DE MAINSHAFT (Solo si se cambia Socket)')
        add_imagen(doc, 'static/imagenes/Mainshatins.png')
        add_inspeccion_table(doc, [
            ('Inspección visual del Mainshaft', '', datos.get('mainshaft_obs','')),
        ], header_color='0F5132')
        add_cotas_tabla(doc, 'Verificación Dimensiones Mainshaft (mm)', datos, 'ms')

    # ── SECCIÓN 10 - MFL ─────────────────────────────────────
    add_section_title_green(doc, '10. INSPECCIÓN DE MAIN FRAME LINERS')
    add_imagen(doc, 'static/imagenes/MFLIns.png')
    add_inspeccion_table(doc, [
        ('Inspección de 24 pernos de MFL pernos M24x40 Torque: 778 N.m', datos.get('mfl_pernos_estado',''), datos.get('mfl_pernos_obs','')),
        ('Medida de MFL promedio (Mínimo 9mm)', '', str(datos.get('mfl_medida',''))),
        ('Medición A/B/C/D/E/F/G (mm)', '', f"A:{datos.get('mfl_med_A','-')} B:{datos.get('mfl_med_B','-')} C:{datos.get('mfl_med_C','-')} D:{datos.get('mfl_med_D','-')} E:{datos.get('mfl_med_E','-')} F:{datos.get('mfl_med_F','-')} G:{datos.get('mfl_med_G','-')}"),
        ('¿Se cambiará en esta inspección los MFL?', datos.get('mfl_cambio_ahora','NO'), ''),
        ('¿Se requiere cambio en la siguiente intervención?', datos.get('mfl_cambio_siguiente','NO'), ''),
    ], header_color='0F5132')

    if datos.get('mfl_cambio_ahora','NO') == 'SI':
        add_banner(doc, 'SI REQUIERE CAMBIO DE MFL', 'FFC107')
        add_section_title_green(doc, '11. MONTAJE DE MAIN FRAME LINERS')
        add_inspeccion_table(doc, [
            ('Inspección de 24 pernos de MFL pernos M24x40 Torque: 778 N.m', datos.get('mfl_mont_pernos',''), datos.get('mfl_mont_pernos_obs','')),
            ('Medición MFL Nuevos A/B/C/D/E/F/G (mm)', '', f"A:{datos.get('mfl_new_A','-')} B:{datos.get('mfl_new_B','-')} C:{datos.get('mfl_new_C','-')} D:{datos.get('mfl_new_D','-')} E:{datos.get('mfl_new_E','-')} F:{datos.get('mfl_new_F','-')} G:{datos.get('mfl_new_G','-')}"),
        ], header_color='0F5132')

    # ── SECCIÓN 12 - MONTURAS ────────────────────────────────
    add_section_title_green(doc, '12. INSPECCIÓN DE MONTURAS')
    add_imagen(doc, 'static/imagenes/MonturasIns.png')
    add_inspeccion_table(doc, [
        ('Verificar estado de las barras de soporte de la montura del contraeje', datos.get('montura_barras_estado',''), datos.get('montura_barras_obs','')),
        ('Verificar que no se tenga acumulación en las monturas', datos.get('montura_acumulacion_estado',''), datos.get('montura_acumulacion_obs','')),
        ('Verificar si los chocky bar están en buen o realizar refuerzo', datos.get('montura_chocky_estado',''), datos.get('montura_chocky_obs','')),
        ('¿Se cambiará en esta inspección las monturas?', datos.get('montura_cambio_ahora','NO'), ''),
        ('¿Se requiere cambio en la siguiente intervención?', datos.get('montura_cambio_siguiente','NO'), ''),
    ], header_color='0F5132')

    # ── SECCIÓN 13-15 - EXCÉNTRICA ───────────────────────────
    add_section_title_green(doc, 'INSPECCIÓN DE CONJUNTO DE EXCÉNTRICA')
    add_section_title_green(doc, '13. INSPECCIÓN DE GUARD PIN')
    tabla_gp = doc.add_table(rows=1, cols=4)
    tabla_gp.style = 'Table Grid'
    bold_cell(tabla_gp.cell(0,0), 'Guard Pin', bg='0F5132', color='FFFFFF', align=WD_ALIGN_PARAGRAPH.CENTER)
    bold_cell(tabla_gp.cell(0,1), '¿Se cambió?', bg='0F5132', color='FFFFFF', align=WD_ALIGN_PARAGRAPH.CENTER)
    bold_cell(tabla_gp.cell(0,2), 'Medida', bg='0F5132', color='FFFFFF', align=WD_ALIGN_PARAGRAPH.CENTER)
    bold_cell(tabla_gp.cell(0,3), 'Observaciones', bg='0F5132', color='FFFFFF', align=WD_ALIGN_PARAGRAPH.CENTER)
    for i in range(1, 7):
        row = tabla_gp.add_row()
        normal_cell(row.cells[0], f'Guard Pin {i}', bold=True)
        normal_cell(row.cells[1], datos.get(f'gp{i}_cambio',''), align=WD_ALIGN_PARAGRAPH.CENTER)
        normal_cell(row.cells[2], str(datos.get(f'gp{i}_medida','')), align=WD_ALIGN_PARAGRAPH.CENTER)
        normal_cell(row.cells[3], datos.get(f'gp{i}_obs',''))
    doc.add_paragraph()

    add_section_title_green(doc, '14. MONTAJE DE PROTECTOR ESTÁTICO')
    add_inspeccion_table(doc, [
        ('Realizar inspección de protector estático', datos.get('prot_estatico_estado',''), datos.get('prot_estatico_obs','')),
    ], header_color='0F5132')

    add_section_title_green(doc, '15. MONTAJE DE PROTECTOR DINÁMICO')
    add_inspeccion_table(doc, [
        ('Realizar inspección de protector dinámico', datos.get('prot_dinamico_estado',''), datos.get('prot_dinamico_obs','')),
        ('¿Hay presencia de fuga de aceite?', datos.get('prot_din_fuga',''), datos.get('prot_din_fuga_obs','')),
    ], header_color='0F5132')

    if datos.get('prot_din_fuga','NO') == 'SI':
        add_section_title_green(doc, '16. INSPECCIÓN DE CONTRAPESO')
        add_inspeccion_table(doc, [
            ('Realizar inspección del contrapeso', datos.get('contrapeso_estado',''), datos.get('contrapeso_obs','')),
            ('Realizar inspección de sellos U-T', datos.get('sello_ut_estado',''), datos.get('sello_ut_obs','')),
            ('Altura Bowl Entrante (pulgadas)', '', str(datos.get('altura_bowl_entrante',''))),
        ], header_color='0F5132')

    # ── FOTOS ────────────────────────────────────────────────
    fotos = [k for k in datos.keys() if k.startswith('foto_path_')]
    if fotos:
        add_section_title_green(doc, 'REGISTRO FOTOGRÁFICO')
        for foto_key in fotos:
            ruta_foto = datos[foto_key]
            if ruta_foto and os.path.exists(ruta_foto):
                nombre = foto_key.replace('foto_path_','').replace('_',' ').upper()
                doc.add_paragraph(nombre)
                add_imagen(doc, ruta_foto)

    # ── RECOMENDACIONES Y CIERRE ─────────────────────────────
    add_section_title_green(doc, 'RECOMENDACIONES PARA LA SIGUIENTE INTERVENCIÓN')
    doc.add_paragraph(datos.get('recomendaciones',''))

    doc.add_paragraph()
    tabla_firma = doc.add_table(rows=2, cols=2)
    tabla_firma.style = 'Table Grid'
    bold_cell(tabla_firma.cell(0,0), 'SUPERVISOR METSO', bg='D1E7DD', align=WD_ALIGN_PARAGRAPH.CENTER)
    bold_cell(tabla_firma.cell(0,1), 'SUPERVISOR CLIENTE', bg='D1E7DD', align=WD_ALIGN_PARAGRAPH.CENTER)
    normal_cell(tabla_firma.cell(1,0), datos.get('supervisor_metso',''))
    normal_cell(tabla_firma.cell(1,1), datos.get('supervisor_cliente',''))

    doc.add_paragraph()
    p_fecha = doc.add_paragraph(f'Reporte generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}')
    p_fecha.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_fecha.runs[0].font.size = Pt(8)
    p_fecha.runs[0].font.color.rgb = RGBColor(0x99, 0x99, 0x99)

    os.makedirs('reportes', exist_ok=True)
    nombre = f'reportes/Cambio_HB_{datos.get("chancadora","X")}_{datetime.now().strftime("%Y%m%d_%H%M")}.docx'
    doc.save(nombre)
    return nombre