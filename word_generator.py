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
    if bold:
      run.bold = True
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
        normal_cell(row.cells[1], str(a) if a is not None else '-', align=WD_ALIGN_PARAGRAPH.CENTER)
        normal_cell(row.cells[2], str(b) if b is not None else '-', align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph()

def add_metro_tabla_simple(doc, titulo, mediciones, header_color='E8F0FE', label_color=(0x0F,0x51,0x32)):
    p = doc.add_paragraph()
    run = p.add_run(titulo)
    run.bold = True
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(*label_color)
    tabla = doc.add_table(rows=1, cols=2)
    tabla.style = 'Table Grid'
    bold_cell(tabla.cell(0,0), 'Punto', bg=header_color, align=WD_ALIGN_PARAGRAPH.CENTER)
    bold_cell(tabla.cell(0,1), 'Medida (mm)', bg=header_color, align=WD_ALIGN_PARAGRAPH.CENTER)
    for punto, val in mediciones:
        row = tabla.add_row()
        normal_cell(row.cells[0], punto, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        normal_cell(row.cells[1], str(val) if (val is not None and val != '') else '-', align=WD_ALIGN_PARAGRAPH.CENTER)
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
    for letra in ['A','B','C','D','F']:
        row = tabla.add_row()
        normal_cell(row.cells[0], letra, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        for j in range(1,5):
            v = datos.get(f'{prefijo}_{letra}{j}','')
            normal_cell(row.cells[j], str(v) if v else '-', align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph()

def add_imagen(doc, ruta):
    if not ruta:
        return
    try:
        import io
        from PIL import Image
        if str(ruta).startswith('http'):
            import urllib.request
            with urllib.request.urlopen(ruta) as response:
                img_data = io.BytesIO(response.read())
            img = Image.open(img_data)
        elif os.path.exists(str(ruta)):
            img = Image.open(ruta)
        else:
            return
        img.thumbnail((600, 400))
        buffer = io.BytesIO()
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        img.save(buffer, format='JPEG', quality=60)
        buffer.seek(0)
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(buffer, width=Cm(8))
    except Exception as e:
        print(f'Error imagen {ruta}: {e}')
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
    bold_cell(tabla_enc.cell(0,0), 'Metso', size=18, color='000000', bg='FFFFFF', align=WD_ALIGN_PARAGRAPH.CENTER)
    bold_cell(tabla_enc.cell(0,1), 'PROTOCOLO ARMADO DE HEAD Y BOWL', size=12, color='FFFFFF', bg='1A3A5C', align=WD_ALIGN_PARAGRAPH.CENTER)
    fecha = str(datos.get('fecha_inicio','')).replace('-','') if datos.get('fecha_inicio') else ''
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
    add_section_title(doc, 'HEAD BALL')
    add_inspeccion_table(doc, [
        ('01. Inspección visual de la superficie del Head Ball (golpes, rayones, huellas, etc.)', datos.get('hb_paso28_estado',''), datos.get('hb_paso28_obs','')),
        ('02. Inspeccionar estado de la cabeza de pernos de sujeción cuando el Head esté desarmado', datos.get('hb_paso29_estado',''), datos.get('hb_paso29_obs','')),
        ('03. ¿Requiere cambio de Head Ball?', datos.get('head_ball_cambio','NO'), ''),
    ])
    if datos.get('head_ball_cambio','NO') == 'NO':
        add_banner(doc, 'NO REQUIERE CAMBIO', '28A745')
    else:
        add_banner(doc, 'SI REQUIERE CAMBIO (ENVIAR A REPARACIÓN)', 'FFC107')

    add_section_title(doc, 'INSPECCIÓN DE UPPER BUSHING')
    add_inspeccion_table(doc, [
        ('04. Realizar la inspección visual de la superficie del upper bushing (golpes, rayones, huellas, etc.)', datos.get('ub_paso1_estado',''), datos.get('ub_paso1_obs','')),
        ('04.1. De encontrar desprendimiento de material, fisuras u otro similar aplicar NDT y evidenciar mediante imágenes', '', datos.get('ub_paso2_obs','')),
        ('05.Inspeccionar el estado de las 4 chavetas y los 6 pernos M16 de fijación de cada una.', datos.get('ub_paso3_estado',''), datos.get('ub_paso3_obs','')),
        ('06.Verificar el Torque de los pernos a 260 N.m (192 Lb.ft), y evidenciar con el serial number de la herramienta.', datos.get('ub_paso4_estado',''), datos.get('ub_paso4_obs','')),
        ('07.Verificar el estado del seguro alambre de los pernos', datos.get('ub_paso5_estado',''), datos.get('ub_paso5_obs','')),
        ('¿Requiere cambio de Upper Bushing?', datos.get('upper_bushing_cambio','NO'), ''),
    ])
    if datos.get('upper_bushing_cambio','NO') == 'NO':
        add_banner(doc, 'NO REQUIERE CAMBIO (REALIZAR METROLOGÍA)', '28A745')
    else:
        add_banner(doc, 'SI REQUIERE CAMBIO (ENVIAR A REPARACIÓN)', 'FFC107')
    add_metro_tabla(doc, '08. Control de Mediciones Upper Bushing', [
        ('A1/B1', datos.get('upper_A1',''), datos.get('upper_B1','')),
        ('A2/B2', datos.get('upper_A2',''), datos.get('upper_B2','')),
        ('A3/B3', datos.get('upper_A3',''), datos.get('upper_B3','')),
    ])
    add_imagen(doc, 'static/imagenes/upper_bushing.png')
    if datos.get('upper_bushing_cambio','NO') == 'SI':
        add_inspeccion_table(doc, [
            ('08. Control dimensional del upper bushing  instalado', '', datos.get('ub_paso15_obs','')),
        ])
        add_metro_tabla(doc, '08.Control de Mediciones Upper Bushing Nuevo', [
            ('A1/B1', datos.get('upper_A1',''), datos.get('upper_B1','')),
            ('A2/B2', datos.get('upper_A2',''), datos.get('upper_B2','')),
            ('A3/B3', datos.get('upper_A3',''), datos.get('upper_B3','')),
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

        add_metro_tabla(doc, 'Control de Mediciones Lower Bushing Nuevo', [
            ('A1/B1', datos.get('lower_A1',''), datos.get('lower_B1','')),
            ('A2/B2', datos.get('lower_A2',''), datos.get('lower_B2','')),
            ('A3/B3', datos.get('lower_A3',''), datos.get('lower_B3','')),
            ('A4/B4', datos.get('lower_A4',''), datos.get('lower_B4','')),
            ('A5/B5', datos.get('lower_A5',''), datos.get('lower_B5','')),
            ('A6/B6', datos.get('lower_A6',''), datos.get('lower_B6','')),
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
            if ruta_foto:
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
    id_head = datos.get('id_head','') or 'X'
    id_bowl = datos.get('id_bowl','') or 'X'
    nombre = f'reportes/Armado_HB_{id_head}_{id_bowl}_{datetime.now().strftime("%Y%m%d_%H%M")}.docx'
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
    bold_cell(tabla_enc.cell(0,0), 'Metso', size=18, color='000000', bg='FFFFFF', align=WD_ALIGN_PARAGRAPH.CENTER)
    bold_cell(tabla_enc.cell(0,1), 'PROTOCOLO CAMBIO DE HEAD Y BOWL', size=12, color='FFFFFF', bg='0F5132', align=WD_ALIGN_PARAGRAPH.CENTER)
    fecha = datos.get('fecha_inicio','').replace('-','') if datos.get('fecha_inicio') else ''
    folio = f"CHB-{fecha}{str(hash(str(datos)))[-5:]}"
    normal_cell(tabla_enc.cell(0,2), folio, size=9, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph()

    # ── DATOS GENERALES ──────────────────────────────────────
    add_section_title_green(doc, '1. DATOS DEL EQUIPO')
    tabla_dg = doc.add_table(rows=5, cols=4)
    tabla_dg.style = 'Table Grid'
    campos_dg = [
        ('EQUIPO', 'MP1250'),
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
    add_section_title_green(doc, '2. INSPECCIÓN DE ANILLO DE AJUSTE Y ANILLO DE SUJECIÓN')
    add_section_title_green(doc, '2.1.Inspección de las roscas del conjunto del anillo de ajuste y sujeción')
    add_inspeccion_table(doc, [
        ('Realizar inspección del estado de las roscas del anillo de ajuste y anillo de sujeción',
         datos.get('anillo_roscas_estado',''), datos.get('anillo_roscas_obs','')),
        ('De encontrar algún defecto, aplicar NDT y mostrar evidencia fotográfica',
         '', datos.get('anillo_ndt_obs','')),
        ('Gap de los hilos del anillo de ajuste y anillo de sujeción - peineta (mm)',
         '', str(datos.get('anillo_gap_peineta','') or '-')),
        ('Inspección del estado y conexionado de los cilindros de sujeción',
         datos.get('anillo_cilindros_estado',''), datos.get('anillo_cilindros_obs','')),
    ], header_color='0F5132')

    add_section_title_green(doc, '2.3. Inspección de Clamping Cylinders')
    add_inspeccion_table(doc, [
        ('¿Se detectan fugas de aceite por el extremo del Clamping Cylinder?',
         datos.get('clamping_fugas_estado',''), datos.get('clamping_fugas_obs','')),
    ], header_color='0F5132')

    # ── SECCIÓN 3 - SOCKET LINER ─────────────────────────────
    add_section_title_green(doc, '3. INSPECCIÓN DE SOCKET LINER')
    add_inspeccion_table(doc, [
        ('Verificar el estado del socket liner',
         datos.get('sl_ranuras_estado',''), datos.get('sl_ranuras_obs','')),
    ], header_color='0F5132')

    add_inspeccion_table(doc, [
        ('Verificar presencia de fisuras en el socket liner', datos.get('sl_fisuras_estado',''), datos.get('sl_fisuras_obs','')),
        ('Verificar presencia de deformaciones en el socket liner', datos.get('sl_deformaciones_estado',''), datos.get('sl_deformaciones_obs','')),
        ('Verificar que los canales se encuentren libres sin obstrucción', datos.get('sl_canales_estado',''), datos.get('sl_canales_obs','')),
    ], header_color='0F5132')
    add_imagen(doc, 'static/imagenes/socket_liner1.png')

    add_metro_tabla_simple(doc, 'Metrología Socket Liner', [
        ('A', datos.get('socket_med_a','')),
        ('B', datos.get('socket_med_b','')),
        ('C', datos.get('socket_med_c','')),
        ('D', datos.get('socket_med_d','')),
    ], header_color='D1E7DD')

    add_imagen(doc, 'static/imagenes/gap_socket_liner1.png')

    add_inspeccion_table(doc, [
        ('¿Se cambiará en esta intervención el Socket Liner?', datos.get('sl_cambio_ahora','NO'), ''),
        ('¿Se requiere cambio en la siguiente intervención?', datos.get('sl_cambio_siguiente','NO'), ''),
    ], header_color='0F5132')

    if datos.get('sl_cambio_ahora','NO') == 'SI':
        add_banner(doc, 'SI REQUIERE CAMBIO DE SOCKET LINER', 'FFC107')
        add_section_title_green(doc, '4. RETIRO DE SOCKET LINER')
        add_inspeccion_table(doc, [
            ('Verificar la instalación los 4 tornillos extractores en los agujeros del revestimiento del socket liner', datos.get('sl_ret_tornillos',''), datos.get('sl_ret_tornillos_obs','')),
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
        ('Realizar inspección visual del socket (fisuras, golpes, rayones, sin obstrucciones, sin desprendimientos, sin deformaciones, etc)', datos.get('socket_fisuras_estado',''), datos.get('socket_fisuras_obs','')),
        ('Inspeccionar los pernos del Socket', datos.get('socket_pernos_estado',''), datos.get('socket_pernos_obs','')),
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
            ('1. Calentar el socket a 120°C por encima de la temperatura ambiente', '', datos.get('sk_mont_calentar_obs','')),
            ('2. Enfriar el socket a temperatura ambiente y ajustar los pernos a 2820 N.m', '', datos.get('sk_mont_enfriar_obs','')),
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
        ('¿Se aplicó wearing compound en las paredes de los MFL?', datos.get('mfl_wearing_estado',''), datos.get('mfl_wearing_obs','')),
        ('Medida de MFL promedio', '', str(datos.get('mfl_medida',''))),
        ('Medición A/B/C/D/E/F/G/H (mm)', '', f"A:{datos.get('mfl_med_A','-')} B:{datos.get('mfl_med_B','-')} C:{datos.get('mfl_med_C','-')} D:{datos.get('mfl_med_D','-')} E:{datos.get('mfl_med_E','-')} F:{datos.get('mfl_med_F','-')} G:{datos.get('mfl_med_G','-')} H:{datos.get('mfl_med_H','-')}"),
        ('¿Se cambiará en esta inspección los MFL?', datos.get('mfl_cambio_ahora','NO'), ''),
        ('¿Se requiere cambio en la siguiente intervención?', datos.get('mfl_cambio_siguiente','NO'), ''),
    ], header_color='0F5132')

    if datos.get('mfl_cambio_ahora','NO') == 'SI':
        add_banner(doc, 'SI REQUIERE CAMBIO DE MFL', 'FFC107')
        add_section_title_green(doc, '11. MONTAJE DE MAIN FRAME LINERS NUEVO')
        add_inspeccion_table(doc, [
            ('Inspección de 24 pernos de MFL pernos M24x40 Torque: 778 N.m', datos.get('mfl_mont_pernos',''), datos.get('mfl_mont_pernos_obs','')),
            ('Medición MFL Nuevos A/B/C/D/E/F/G/H (mm)', '', f"A:{datos.get('mfl_new_A','-')} B:{datos.get('mfl_new_B','-')} C:{datos.get('mfl_new_C','-')} D:{datos.get('mfl_new_D','-')} E:{datos.get('mfl_new_E','-')} F:{datos.get('mfl_new_F','-')} G:{datos.get('mfl_new_G','-')} H:{datos.get('mfl_new_H','-')}"),
        ], header_color='0F5132')

    # ── SECCIÓN 12 - MONTURAS ────────────────────────────────
    add_section_title_green(doc, '12. INSPECCIÓN DE MONTURAS')
    add_imagen(doc, 'static/imagenes/MonturasIns.png')
    add_inspeccion_table(doc, [
        ('Verificar estado de las barras de soporte de la montura del contraeje', datos.get('montura_barras_estado',''), datos.get('montura_barras_obs','')),
        ('Verificar que no se tenga acumulación de material en guarda de contraeje', datos.get('montura_acumulacion_estado',''), datos.get('montura_acumulacion_obs','')),
        ('Verificar el estado de los choky bar. ¿Necesitan refuerzo?', datos.get('montura_chocky_estado',''), datos.get('montura_chocky_obs','')),
        ('¿Se cambiará en esta inspección las monturas?', datos.get('montura_cambio_ahora','NO'), ''),
        ('¿Se requiere cambio en la siguiente intervención?', datos.get('montura_cambio_siguiente','NO'), ''),
    ], header_color='0F5132')

    if datos.get('montura_cambio_ahora','NO') == 'SI':
        add_banner(doc, 'SI SE CAMBIA MONTURAS', 'FFC107')
        add_inspeccion_table(doc, [
            ('Inspeccionar desgastes en los brazos de la chancadora', datos.get('montura_brazos_estado',''), datos.get('montura_brazos_obs','')),
            ('Inspeccionar desgastes en la caja de contraeje', datos.get('montura_caja_estado',''), datos.get('montura_caja_obs','')),
        ], header_color='0F5132')
    

    # ── SECCIÓN 13-15 - EXCÉNTRICA ───────────────────────────
    add_section_title_green(doc, 'INSPECCIÓN DE GUARDA ESTÁTICA / GUARDA DINÁMICA / GUARD PIN')
    
    add_section_title_green(doc, '13. INSPECCIÓN DE PROTECTOR ESTÁTICO')
    add_inspeccion_table(doc, [
        ('Verificar el estado de la protección estática', datos.get('prot_estatico_estado',''), datos.get('prot_estatico_obs','')),
        ('Medida promedio espesor protección estática (mm)', '', str(datos.get('prot_estatico_espesor','') or '-')),
    ], header_color='0F5132')

    add_section_title_green(doc, '14. INSPECCIÓN DE GUARD PIN')
    tabla_gp = doc.add_table(rows=1, cols=5)
    tabla_gp.style = 'Table Grid'
    bold_cell(tabla_gp.cell(0,0), 'Guard Pin', bg='0F5132', color='FFFFFF', align=WD_ALIGN_PARAGRAPH.CENTER)
    bold_cell(tabla_gp.cell(0,1), '¿Se cambió?', bg='0F5132', color='FFFFFF', align=WD_ALIGN_PARAGRAPH.CENTER)
    bold_cell(tabla_gp.cell(0,2), 'Medida (mm)', bg='0F5132', color='FFFFFF', align=WD_ALIGN_PARAGRAPH.CENTER)
    bold_cell(tabla_gp.cell(0,3), 'Medida Nueva (mm)', bg='0F5132', color='FFFFFF', align=WD_ALIGN_PARAGRAPH.CENTER)
    bold_cell(tabla_gp.cell(0,4), 'Observaciones', bg='0F5132', color='FFFFFF', align=WD_ALIGN_PARAGRAPH.CENTER)
    for i in range(1, 7):
        row = tabla_gp.add_row()
        normal_cell(row.cells[0], f'Guard Pin {i}', bold=True)
        normal_cell(row.cells[1], datos.get(f'gp{i}_cambio',''), align=WD_ALIGN_PARAGRAPH.CENTER)
        normal_cell(row.cells[2], str(datos.get(f'gp{i}_medida','')), align=WD_ALIGN_PARAGRAPH.CENTER)
        normal_cell(row.cells[3], str(datos.get(f'gp{i}_medida_nueva','') or '-'), align=WD_ALIGN_PARAGRAPH.CENTER)
        normal_cell(row.cells[4], datos.get(f'gp{i}_obs',''))
    doc.add_paragraph()

    add_section_title_green(doc, '15. INSPECCIÓN DE PROTECTOR DINÁMICO')
    add_inspeccion_table(doc, [
        ('Verificar el estado de la protección dinámica', datos.get('prot_dinamico_estado',''), datos.get('prot_dinamico_obs','')),
        ('Medida desgaste protección dinámica (mm)', '', str(datos.get('prot_dinamico_desgaste','') or '-')),
        ('¿Hay presencia de fuga de aceite?', datos.get('prot_din_fuga',''), datos.get('prot_din_fuga_obs','')),
    ], header_color='0F5132')

    if datos.get('prot_din_fuga','NO') == 'SI':
        add_section_title_green(doc, '16. INSPECCIÓN DE CONTRAPESO')
        add_inspeccion_table(doc, [
            ('Realizar inspección del contrapeso', datos.get('contrapeso_estado',''), datos.get('contrapeso_obs','')),
            ('Realizar inspección de sellos U-T', datos.get('sello_ut_estado',''), datos.get('sello_ut_obs','')),
        ], header_color='0F5132')
        add_imagen(doc, 'static/imagenes/SelloUT.png')
    
    # ── CAMBIO DE EXCÉNTRICA ─────────────────────────────────
    if datos.get('excentrica_cambio') == 'SI':
        add_section_title_green(doc, 'CAMBIO DE EXCÉNTRICA')
        add_banner(doc, 'SI SE CAMBIA EXCÉNTRICA', 'FFC107')
        add_inspeccion_table(doc, [
            ('Verificar el estado del protector dinámico', datos.get('exc_prot_din_estado',''), datos.get('exc_prot_din_obs','')),
            ('Verificar el estado de los 10 pernos M20 del protector dinámico', datos.get('exc_pernos_prot_estado',''), datos.get('exc_pernos_prot_obs','')),
            ('Verificar el estado de los sellos U-T', datos.get('exc_sellos_estado',''), datos.get('exc_sellos_obs','')),
            ('Distancia vertical entre caras superiores de la excéntrica y main shaft (mm)', '', str(datos.get('exc_distancia_vertical','') or '-')),
            ('Realizar inspección de la bocina de la excéntrica', datos.get('exc_bocina_estado',''), datos.get('exc_bocina_obs','')),
        ], header_color='0F5132')
        add_metro_tabla(doc, 'Metrología superficie interior excéntrica (mm) — cada 150mm o 6"', [
            ('1', f"A:{datos.get('exc_metro_a1','-')} C:{datos.get('exc_metro_c1','-')}", f"B:{datos.get('exc_metro_b1','-')} D:{datos.get('exc_metro_d1','-')}"),
            ('2', f"A:{datos.get('exc_metro_a2','-')} C:{datos.get('exc_metro_c2','-')}", f"B:{datos.get('exc_metro_b2','-')} D:{datos.get('exc_metro_d2','-')}"),
            ('3', f"A:{datos.get('exc_metro_a3','-')} C:{datos.get('exc_metro_c3','-')}", f"B:{datos.get('exc_metro_b3','-')} D:{datos.get('exc_metro_d3','-')}"),
        ])
        add_inspeccion_table(doc, [
            ('Realizar inspección del lower thrust bearing', datos.get('exc_lower_tb_estado',''), datos.get('exc_lower_tb_obs','')),
            ('Verificar estado de los 08 pernos M20 del lower thrust bearing', datos.get('exc_pernos_lower_estado',''), datos.get('exc_pernos_lower_obs','')),
            ('Realizar inspección del upper thrust bearing', datos.get('exc_upper_tb_estado',''), datos.get('exc_upper_tb_obs','')),
            ('Verificar estado de los 08 pernos M20 del upper thrust bearing', datos.get('exc_pernos_upper_estado',''), datos.get('exc_pernos_upper_obs','')),
            ('Verificar estado de las 08 rampas de lubricación del lower thrust bearing', datos.get('exc_rampas_estado',''), datos.get('exc_rampas_obs','')),
            ('Verificar estado de los 02 tornillos tensores M36 excéntrica-engranaje', datos.get('exc_tornillos_estado',''), datos.get('exc_tornillos_obs','')),
            ('Medición del back lash (mm)', '', str(datos.get('exc_backlash','') or '-')),
            ('Medidas de las lainas instaladas', '', datos.get('exc_lainas','')),
        ], header_color='0F5132')

    # ── SISTEMAS AUXILIARES ──────────────────────────────────
    if datos.get('sistemas_aux_inspeccion') == 'SI':
        add_section_title_green(doc, 'INSPECCIÓN DE SISTEMAS AUXILIARES')

        add_section_title_green(doc, 'Sistema de Transmisión')
        add_inspeccion_table(doc, [
            ('Frecuencia tensado de correas (Hz)', '', str(datos.get('trans_frecuencia') or '-')),
            ('Estado de polea conducida', datos.get('trans_polea_estado',''), datos.get('trans_polea_obs','')),
            ('Estado de radiador', datos.get('trans_radiador_estado',''), datos.get('trans_radiador_obs','')),
        ], header_color='0F5132')

        add_section_title_green(doc, 'Sistema Hidráulico — Presión de Acumuladores (950-1050 PSI)')
        tabla_ac = doc.add_table(rows=1, cols=3)
        tabla_ac.style = 'Table Grid'
        bold_cell(tabla_ac.cell(0,0), 'N°', bg='0F5132', color='FFFFFF', align=WD_ALIGN_PARAGRAPH.CENTER)
        bold_cell(tabla_ac.cell(0,1), 'Presión encontrada (PSI)', bg='0F5132', color='FFFFFF', align=WD_ALIGN_PARAGRAPH.CENTER)
        bold_cell(tabla_ac.cell(0,2), 'Presión final tras recarga N₂ (PSI)', bg='0F5132', color='FFFFFF', align=WD_ALIGN_PARAGRAPH.CENTER)
        for i in range(1, 9):
            row = tabla_ac.add_row()
            normal_cell(row.cells[0], str(i), align=WD_ALIGN_PARAGRAPH.CENTER)
            normal_cell(row.cells[1], str(datos.get(f'acum_pres_{i}') or '-'), align=WD_ALIGN_PARAGRAPH.CENTER)
            normal_cell(row.cells[2], str(datos.get(f'acum_final_{i}') or '-'), align=WD_ALIGN_PARAGRAPH.CENTER)
        row = tabla_ac.add_row()
        normal_cell(row.cells[0], 'Consola', bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        normal_cell(row.cells[1], str(datos.get('acum_pres_consola') or '-'), align=WD_ALIGN_PARAGRAPH.CENTER)
        normal_cell(row.cells[2], str(datos.get('acum_final_consola') or '-'), align=WD_ALIGN_PARAGRAPH.CENTER)
        doc.add_paragraph()

        add_inspeccion_table(doc, [
            ('Bloque hidráulico', datos.get('hidra_bloque_estado',''), datos.get('hidra_bloque_obs','')),
            ('Bomba y acople hidráulico', datos.get('hidra_bomba_estado',''), datos.get('hidra_bomba_obs','')),
            ('Motor hidráulico 1', datos.get('hidra_motor1_estado',''), datos.get('hidra_motor1_obs','')),
            ('Motor hidráulico 2', datos.get('hidra_motor2_estado',''), datos.get('hidra_motor2_obs','')),
            ('Motor hidráulico 3', datos.get('hidra_motor3_estado',''), datos.get('hidra_motor3_obs','')),
        ], header_color='0F5132')

        add_section_title_green(doc, 'Sistema Blower')
        add_inspeccion_table(doc, [
            ('Inspección / Limpieza de filtro', datos.get('blower_filtro_estado',''), datos.get('blower_filtro_obs','')),
            ('¿Se cambió el filtro?', datos.get('blower_cambio_filtro','NO'), datos.get('blower_cambio_obs','')),
        ], header_color='0F5132')

        add_section_title_green(doc, 'Sistema de Lubricación')
        add_inspeccion_table(doc, [
            ('Cedazo de tanque de lubricación', datos.get('lubri_cedazo_estado',''), datos.get('lubri_cedazo_obs','')),
            ('Inspección de la junta de expansión', datos.get('lubri_junta_estado',''), datos.get('lubri_junta_obs','')),
            ('Inspección de líneas de lubricación del motor hidráulico', datos.get('lubri_lineas_estado',''), datos.get('lubri_lineas_obs','')),
            ('Diferencia de presión del banco de filtros (psi)', '', str(datos.get('lubri_presion_filtros','') or '-')),
        ], header_color='0F5132')

        # ── CHUTE DE ALIMENTACIÓN ────────────────────────────────
        add_section_title_green(doc, 'INSPECCIÓN DE CHUTE DE ALIMENTACIÓN')
        add_inspeccion_table(doc, [
            ('Inspección del estado del faldón del chute', datos.get('chute_faldon_estado',''), datos.get('chute_faldon_obs','')),
            ('Inspección del estado de los liners del chute', datos.get('chute_liners_estado',''), datos.get('chute_liners_obs','')),
            ('Inspección del estado de la placa base del chute', datos.get('chute_placa_estado',''), datos.get('chute_placa_obs','')),
        ], header_color='0F5132')

    # ── FOTOS ────────────────────────────────────────────────
    fotos = [k for k in datos.keys() if k.startswith('foto_path_')]
    if fotos:
        add_section_title_green(doc, 'REGISTRO FOTOGRÁFICO')
        for foto_key in fotos:
            ruta_foto = datos[foto_key]
            if ruta_foto:
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

# ══════════════════════════════════════════════════════════════
# GENERADOR INFORME METSO (formato informe oficial)
# ══════════════════════════════════════════════════════════════
from docx.enum.section import WD_ORIENT

# ── Colores Metso ─────────────────────────────────────────────
NARANJA   = '000000'
GRIS_OSC  = '404040'
GRIS_CLAR = 'F2F2F2'
BLANCO    = 'FFFFFF'
GRIS_MED  = 'BFBFBF'

# ── Helpers ───────────────────────────────────────────────────
def set_cell_bg(cell, color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color)
    tcPr.append(shd)

def set_borders(cell, color='BFBFBF'):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcB = OxmlElement('w:tcBorders')
    for side in ['top','left','bottom','right']:
        b = OxmlElement(f'w:{side}')
        b.set(qn('w:val'), 'single')
        b.set(qn('w:sz'), '4')
        b.set(qn('w:color'), color)
        tcB.append(b)
    tcPr.append(tcB)

def cell_write(cell, text, bold=False, size=9, color=None, bg=None,
               align=WD_ALIGN_PARAGRAPH.LEFT, italic=False):
    cell.text = ''
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.space_before = Pt(0)
    run = p.add_run(str(text) if text is not None else '')
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    run.font.name = 'Arial'
    if color:
        run.font.color.rgb = RGBColor(*bytes.fromhex(color))
    if bg:
        set_cell_bg(cell, bg)
    set_borders(cell)

def add_para(doc, text='', bold=False, size=10, color=None,
             align=WD_ALIGN_PARAGRAPH.LEFT, space_before=4, space_after=4):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    if text:
        run = p.add_run(str(text))
        run.bold = bold
        run.font.size = Pt(size)
        run.font.name = 'Arial'
        if color:
            run.font.color.rgb = RGBColor(*bytes.fromhex(color))
    return p

def seccion_titulo(doc, numero, texto):
    """Título de sección con línea naranja abajo"""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '8')
    bottom.set(qn('w:color'), NARANJA)
    pBdr.append(bottom)
    pPr.append(pBdr)
    run = p.add_run(f'{numero}. {texto}')
    run.bold = True
    run.font.size = Pt(11)
    run.font.name = 'Arial'
    run.font.color.rgb = RGBColor(*bytes.fromhex(GRIS_OSC))
    return p

def tabla_2col(doc, filas, w1=8, w2=9):
    """Tabla simple 2 columnas label/valor"""
    t = doc.add_table(rows=0, cols=2)
    t.style = 'Table Grid'
    for i, (k, v) in enumerate(filas):
        row = t.add_row()
        bg = GRIS_CLAR if i % 2 == 0 else BLANCO
        cell_write(row.cells[0], k, bold=True, size=9, bg=bg)
        cell_write(row.cells[1], v, size=9, bg=BLANCO)
        row.cells[0].width = Cm(w1)
        row.cells[1].width = Cm(w2)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return t

def tabla_inspeccion(doc, filas, header_color=NARANJA):
    """Tabla inspección 3 cols: Componente | Estado | Observaciones"""
    t = doc.add_table(rows=1, cols=3)
    t.style = 'Table Grid'
    for i, h in enumerate(['Componente', 'Estado', 'Observaciones']):
        cell_write(t.cell(0, i), h, bold=True, size=9,
                   color=BLANCO, bg=header_color, align=WD_ALIGN_PARAGRAPH.CENTER)
    t.columns[0].width = Cm(8)
    t.columns[1].width = Cm(2.5)
    t.columns[2].width = Cm(7)
    for comp, estado, obs in filas:
        row = t.add_row()
        cell_write(row.cells[0], comp, size=9)
        est_bg = 'D1E7DD' if str(estado).upper() in ('BUENO','OK','NO','SIN OBSERVACIONES') else \
                 'FFEBEE' if str(estado).upper() in ('MALO','SI','CON OBSERVACIONES') else BLANCO
        cell_write(row.cells[1], estado, size=9, bg=est_bg, align=WD_ALIGN_PARAGRAPH.CENTER)
        cell_write(row.cells[2], obs, size=9)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def tabla_metrologia(doc, titulo, mediciones):
    """Tabla metrología con pares B/A"""
    add_para(doc, titulo, bold=True, size=9, color=GRIS_OSC, space_before=2, space_after=2)
    t = doc.add_table(rows=1, cols=3)
    t.style = 'Table Grid'
    for i, h in enumerate(['Punto', 'B (0°)', 'A (90°)']):
        cell_write(t.cell(0, i), h, bold=True, size=9,
                   color=GRIS_OSC, bg='E0E0E0', align=WD_ALIGN_PARAGRAPH.CENTER)
    for punto, b, a in mediciones:
        row = t.add_row()
        cell_write(row.cells[0], punto, bold=True, size=9, align=WD_ALIGN_PARAGRAPH.CENTER)
        cell_write(row.cells[1], str(b) if b else '-', size=9, align=WD_ALIGN_PARAGRAPH.CENTER)
        cell_write(row.cells[2], str(a) if a else '-', size=9, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def tabla_cotas(doc, titulo, datos, prefijo):
    """Tabla de cotas 4x4 A1-D4"""
    add_para(doc, titulo, bold=True, size=9, color=GRIS_OSC, space_before=2, space_after=2)
    t = doc.add_table(rows=1, cols=5)
    t.style = 'Table Grid'
    for i, h in enumerate(['COTA', '1 (0°)', '2 (45°)', '3 (90°)', '4 (135°)']):
        cell_write(t.cell(0, i), h, bold=True, size=9,
                   color=BLANCO, bg=NARANJA, align=WD_ALIGN_PARAGRAPH.CENTER)
    for letra in ['A','B','C','D','F']:
        row = t.add_row()
        cell_write(row.cells[0], letra, bold=True, size=9, align=WD_ALIGN_PARAGRAPH.CENTER)
        for j in range(1, 5):
            v = datos.get(f'{prefijo}_{letra}{j}', '')
            cell_write(row.cells[j], str(v) if v else '-', size=9, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def add_foto(doc, url):
    """Descarga foto de Cloudinary e inserta en el doc"""
    if not url:
        return
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=10) as r:
            data = io.BytesIO(r.read())
        from PIL import Image
        img = Image.open(data)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        img.thumbnail((600, 400))
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=70)
        buf.seek(0)
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(4)
        p.add_run().add_picture(buf, width=Cm(10))
    except Exception as e:
        print(f'⚠️ Foto no cargada: {e}')

def add_fotos_seccion(doc, datos, prefijos):
    """Agrega fotos de una sección específica"""
    fotos = []
    for pref in prefijos:
        for k, v in datos.items():
            if k.startswith(f'foto_path_{pref}') and v:
                fotos.append((k, v))
    if fotos:
        for key, url in fotos:
            nombre = key.replace('foto_path_','').replace('_',' ').upper()
            add_para(doc, nombre, bold=False, size=8, color=GRIS_MED,
                     align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=0)
            add_foto(doc, url)

# ══════════════════════════════════════════════════════════════
# GENERADOR PRINCIPAL
# ══════════════════════════════════════════════════════════════
def generar_informe_metso(datos):
    doc = Document()

    # Márgenes
    for section in doc.sections:
        section.top_margin    = Cm(1.8)
        section.bottom_margin = Cm(1.8)
        section.left_margin   = Cm(1.8)
        section.right_margin  = Cm(1.8)

    d = datos  # alias corto
    chancadora = str(d.get('chancadora','') or '')
    fecha_i    = str(d.get('fecha_inicio','') or '')
    fecha_t    = str(d.get('fecha_termino','') or '')
    hora_i     = f"{d.get('hora_inicio_h','') or ''}:{d.get('hora_inicio_m','') or ''}"
    hora_f     = f"{d.get('hora_fin_h','') or ''}:{d.get('hora_fin_m','') or ''}"

    # ── PORTADA ───────────────────────────────────────────────
    # Banda naranja superior
    t_port = doc.add_table(rows=1, cols=2)
    t_port.style = 'Table Grid'
    cell_write(t_port.cell(0,0), 'METSO', bold=True, size=28,
               color=BLANCO, bg=NARANJA, align=WD_ALIGN_PARAGRAPH.LEFT)
    cell_write(t_port.cell(0,1), 'RESTRICTED', bold=True, size=10,
               color=BLANCO, bg=NARANJA, align=WD_ALIGN_PARAGRAPH.RIGHT)
    t_port.cell(0,0).width = Cm(12)
    t_port.cell(0,1).width = Cm(5)

    add_para(doc, '', space_before=20, space_after=4)

    add_para(doc, 'INFORME DEL SERVICIO', bold=True, size=22,
             color=GRIS_OSC, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=6)

    add_para(doc, f'CAMBIO DE HEAD & BOWL – INSPECCIÓN SOCKET Y SOCKET LINER {chancadora}',
             bold=True, size=16, color=NARANJA,
             align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=20)

    # Tabla datos portada
    tabla_2col(doc, [
        ('CÓDIGO DE INFORME',  str(d.get('codigo_informe','') or 'IF-SE-XXXX')),
        ('SEMANA',             str(d.get('semana','') or '')),
        ('CLIENTE',            str(d.get('cliente','') or 'Sociedad Minera Cerro Verde')),
        ('FECHA DE SERVICIO',  f'{fecha_i}  –  {fecha_t}'),
        ('CHANCADORA',         chancadora),
        ('ORDEN DE SERVICIO',  str(d.get('orden_servicio','') or '')),
    ], w1=7, w2=10)

    add_para(doc, '', space_before=10, space_after=4)

    # Tabla firmas
    t_firma = doc.add_table(rows=2, cols=3)
    t_firma.style = 'Table Grid'
    for i, rol in enumerate(['Elaborado por', 'Revisado por', 'Aprobado por']):
        cell_write(t_firma.cell(0,i), rol, bold=True, size=9,
                   color=BLANCO, bg=GRIS_OSC, align=WD_ALIGN_PARAGRAPH.CENTER)
    nombres = [
        str(d.get('supervisor_metso','') or ''),
        str(d.get('revisado_por','') or ''),
        str(d.get('aprobado_por','') or 'Jason Pozo'),
    ]
    cargos = ['Supervisor de Servicios', 'Site Resident', 'Manager, Perú & North']
    for i in range(3):
        cell_write(t_firma.cell(1,i),
                   f'{nombres[i]}\n{cargos[i]}',
                   size=9, align=WD_ALIGN_PARAGRAPH.CENTER)

    # Salto de página
    doc.add_page_break()

    # ── 1. DATOS GENERALES ────────────────────────────────────
    seccion_titulo(doc, 1, 'DATOS GENERALES')
    tabla_2col(doc, [
        ('CLIENTE',           str(d.get('cliente','') or 'Sociedad Minera Cerro Verde')),
        ('SERVICIO',          f'CAMBIO DE HEAD & BOWL {chancadora}'),
        ('ORDEN DE SERVICIO', str(d.get('orden_servicio','') or '')),
        ('USUARIO DE TURNO',  str(d.get('supervisor_cliente','') or '')),
        ('FECHA DE SERVICIO', f'{fecha_i}  –  {fecha_t}'),
        ('HORA INICIO',       hora_i),
        ('HORA FIN',          hora_f),
        ('TAG EQUIPO',        chancadora),
        ('MODELO EQUIPO',     'METSO MP1250'),
        ('UBICACIÓN',         str(d.get('ubicacion','') or 'Chancado Secundario – C2')),
    ])

    # ── 2. RESUMEN EJECUTIVO ──────────────────────────────────
    seccion_titulo(doc, 2, 'RESUMEN EJECUTIVO')

    # Estado componentes desde protocolo
    def estado(val):
        return str(val) if val else 'Sin observaciones'

    tabla_inspeccion(doc, [
        ('SOCKET LINER',    estado(d.get('sl_fisuras_estado')),    estado(d.get('sl_fisuras_obs'))),
        ('SOCKET',          estado(d.get('socket_fisuras_estado')),estado(d.get('socket_fisuras_obs'))),
        ('EXCÉNTRICA',      estado(d.get('anillo_roscas_estado')), estado(d.get('anillo_roscas_obs'))),
        ('GUARDA ESTÁTICA', estado(d.get('prot_estatico_estado')), estado(d.get('prot_estatico_obs'))),
        ('MAIN FRAME',      estado(d.get('mfl_pernos_estado')),    f"Medida promedio: {d.get('mfl_medida') or '-'} mm"),
    ])

    # ── 3. OBJETIVO ───────────────────────────────────────────
    seccion_titulo(doc, 3, 'OBJETIVO')
    add_para(doc,
        'Realizar el mantenimiento de la chancadora MP1250, cumpliendo con los estándares '
        'de seguridad de SMCV y Metso, así como con las normas y especificaciones técnicas '
        'de Metso para el montaje e instalación de sus equipos como empresa OEM.',
        size=10, space_before=4, space_after=8)

    # ── 4. DESCRIPCIÓN DEL SERVICIO ───────────────────────────
    seccion_titulo(doc, 4, 'DESCRIPCIÓN DEL SERVICIO')

    # Actividades turno
    add_para(doc, f'Hora de bloqueo: {hora_i}', bold=True, size=10, color=GRIS_OSC)
    add_para(doc, f'Hora de desbloqueo: {hora_f}', bold=True, size=10, color=GRIS_OSC)

    # Bowl / Head
    tabla_2col(doc, [
        ('HEAD SALIENTE',            str(d.get('head_saliente','') or '-')),
        ('HEAD ENTRANTE',            str(d.get('head_entrante','') or '-')),
        ('BOWL SALIENTE',            str(d.get('bowl_saliente','') or '-')),
        ('BOWL ENTRANTE',            str(d.get('bowl_entrante','') or '-')),
        ('ALTURA BOWL SALIENTE',     str(d.get('altura_bowl_saliente','') or '-') + '"'),
        ('ALTURA BOWL ENTRANTE',     str(d.get('altura_bowl_entrante','') or '-') + '"'),
        ('ALTURA FINAL BOWL',        str(d.get('altura_final_bowl','') or '-') + '"'),
    ])

    # ── 5. INSPECCIÓN DE COMPONENTES ─────────────────────────
    seccion_titulo(doc, 5, 'INSPECCIÓN DE COMPONENTES')

    # 5.1 Socket Liner
    add_para(doc, 'Metrología Socket Liner (mm)', bold=True, size=9, color=GRIS_OSC, space_before=2, space_after=2)
    t = doc.add_table(rows=1, cols=2)
    t.style = 'Table Grid'
    cell_write(t.cell(0,0), 'Punto', bold=True, size=9, color=GRIS_OSC, bg='E0E0E0', align=WD_ALIGN_PARAGRAPH.CENTER)
    cell_write(t.cell(0,1), 'Medida (mm)', bold=True, size=9, color=GRIS_OSC, bg='E0E0E0', align=WD_ALIGN_PARAGRAPH.CENTER)
    for letra, campo in [('A','socket_med_a'),('B','socket_med_b'),('C','socket_med_c'),('D','socket_med_d')]:
        row = t.add_row()
        cell_write(row.cells[0], letra, bold=True, size=9, align=WD_ALIGN_PARAGRAPH.CENTER)
        cell_write(row.cells[1], str(d.get(campo,'') or '-'), size=9, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

    tabla_inspeccion(doc, [
        ('GAP Interior Socket Liner (mm)', str(d.get('sl_gap_interior','') or '-'), ''),
        ('GAP Exterior Socket Liner (mm)', str(d.get('sl_gap_exterior','') or '-'), ''),
        ('Fisuras en Socket Liner',        str(d.get('sl_fisuras_estado','') or '-'), str(d.get('sl_fisuras_obs','') or '')),
        ('Deformaciones',                  str(d.get('sl_deformaciones_estado','') or '-'), str(d.get('sl_deformaciones_obs','') or '')),
        ('Canales libres',                 str(d.get('sl_canales_estado','') or '-'), str(d.get('sl_canales_obs','') or '')),
        ('¿Se cambió en esta intervención?', str(d.get('sl_cambio_ahora','NO') or 'NO'), ''),
        ('¿Requiere cambio próxima intervención?', str(d.get('sl_cambio_siguiente','NO') or 'NO'), ''),
    ])
    add_fotos_seccion(doc, d, ['sl', 'socket_liner', 'sl1', 'sl2'])

    # 5.2 Socket
    add_para(doc, '5.2 SOCKET', bold=True, size=10, color=NARANJA, space_before=6)
    tabla_inspeccion(doc, [
        ('Fisuras en Socket',       str(d.get('socket_fisuras_estado','') or '-'), str(d.get('socket_fisuras_obs','') or '')),
        ('Pernos del Socket',       str(d.get('socket_pernos_estado','') or '-'),  str(d.get('socket_pernos_obs','') or '')),
        ('Ranuras',                 str(d.get('socket_ranuras_estado','') or '-'), str(d.get('socket_ranuras_obs','') or '')),
        ('Deformaciones',           str(d.get('socket_deform_estado','') or '-'),  str(d.get('socket_deform_obs','') or '')),
        ('Canales de lubricación',  str(d.get('socket_canales_estado','') or '-'), str(d.get('socket_canales_obs','') or '')),
        ('GAP Socket-Mainshaft 0°',   str(d.get('socket_gap_0','') or '-') + ' mm', ''),
        ('GAP Socket-Mainshaft 90°',  str(d.get('socket_gap_90','') or '-') + ' mm', ''),
        ('GAP Socket-Mainshaft 180°', str(d.get('socket_gap_180','') or '-') + ' mm', ''),
        ('GAP Socket-Mainshaft 270°', str(d.get('socket_gap_270','') or '-') + ' mm', ''),
        ('¿Se cambió en esta intervención?', str(d.get('socket_cambio_ahora','NO') or 'NO'), ''),
        ('¿Requiere cambio próxima intervención?', str(d.get('socket_cambio_siguiente','NO') or 'NO'), ''),
    ])
    if d.get('socket_cambio_ahora') == 'SI':
        add_para(doc, 'Cotas Socket Saliente:', bold=True, size=9)
        tabla_cotas(doc, 'Socket Saliente (mm)', d, 'sk_sal')
        add_para(doc, 'Cotas Socket Nuevo:', bold=True, size=9)
        tabla_cotas(doc, 'Socket Nuevo (mm)', d, 'sk_new')
        add_para(doc, 'Mainshaft:', bold=True, size=9)
        tabla_cotas(doc, 'Mainshaft (mm)', d, 'ms')
    add_fotos_seccion(doc, d, ['socket', 'sk', 'socket1', 'socket2'])

    # 5.3 MFL
    add_para(doc, '5.3 MAIN FRAME LINERS', bold=True, size=10, color=NARANJA, space_before=6)
    mfl_vals = [d.get(f'mfl_med_{x}') for x in ['A','B','C','D','E','F','G','H']]
    mfl_nums = [float(v) for v in mfl_vals if v is not None]
    prom_mfl = round(sum(mfl_nums)/len(mfl_nums), 2) if mfl_nums else '-'

    t_mfl = doc.add_table(rows=2, cols=9)
    t_mfl.style = 'Table Grid'
    for i, h in enumerate(['A','B','C','D','E','F','G','H','Promedio']):
        cell_write(t_mfl.cell(0,i), h, bold=True, size=9,
                   color=BLANCO, bg=NARANJA, align=WD_ALIGN_PARAGRAPH.CENTER)
    for i, x in enumerate(['A','B','C','D','E','F','G','H']):
        cell_write(t_mfl.cell(1,i), str(d.get(f'mfl_med_{x}','') or '-'),
                   size=9, align=WD_ALIGN_PARAGRAPH.CENTER)
    cell_write(t_mfl.cell(1,8), str(prom_mfl),
               bold=True, size=9, align=WD_ALIGN_PARAGRAPH.CENTER, bg='FFF3CD')
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

    tabla_inspeccion(doc, [
        ('Pernos MFL',    str(d.get('mfl_pernos_estado','') or '-'), str(d.get('mfl_pernos_obs','') or '')),
        ('Medida mínima', str(d.get('mfl_medida','') or '-') + ' mm (mín 9 mm)', ''),
        ('¿Se cambió en esta intervención?', str(d.get('mfl_cambio_ahora','NO') or 'NO'), ''),
        ('¿Requiere cambio próxima intervención?', str(d.get('mfl_cambio_siguiente','NO') or 'NO'), ''),
    ])
    add_fotos_seccion(doc, d, ['mfl', 'mfl1', 'mfl2', 'main_frame'])

    # 5.4 Monturas
    add_para(doc, '5.4 MONTURAS', bold=True, size=10, color=NARANJA, space_before=6)
    tabla_inspeccion(doc, [
        ('Barras de soporte', str(d.get('montura_barras_estado','') or '-'), str(d.get('montura_barras_obs','') or '')),
        ('Acumulación',       str(d.get('montura_acumulacion_estado','') or '-'), str(d.get('montura_acumulacion_obs','') or '')),
        ('Chocky Bar',        str(d.get('montura_chocky_estado','') or '-'), str(d.get('montura_chocky_obs','') or '')),
        ('¿Se cambió?',       str(d.get('montura_cambio_ahora','NO') or 'NO'), ''),
        ('¿Requiere cambio próxima?', str(d.get('montura_cambio_siguiente','NO') or 'NO'), ''),
    ])
    if d.get('montura_cambio_ahora') == 'SI':
        tabla_inspeccion(doc, [
            ('Desgastes en brazos de la chancadora', str(d.get('montura_brazos_estado','') or '-'), str(d.get('montura_brazos_obs','') or '')),
            ('Desgastes en caja de contraeje', str(d.get('montura_caja_estado','') or '-'), str(d.get('montura_caja_obs','') or '')),
        ])
    add_fotos_seccion(doc, d, ['montura', 'mont'])

    # 5.5 Guard Pins
    add_para(doc, '5.5 GUARD PINS', bold=True, size=10, color=NARANJA, space_before=6)
    t_gp = doc.add_table(rows=1, cols=5)
    t_gp.style = 'Table Grid'
    for i, h in enumerate(['Guard Pin','Medida','¿Se cambió?','Medida Nueva','Observaciones']):
        cell_write(t_gp.cell(0,i), h, bold=True, size=9,
                   color=BLANCO, bg=NARANJA, align=WD_ALIGN_PARAGRAPH.CENTER)
    for i in range(1, 7):
        row = t_gp.add_row()
        cell_write(row.cells[0], f'Guard Pin {i}', bold=True, size=9)
        cell_write(row.cells[1], str(d.get(f'gp{i}_medida','') or '-'), size=9, align=WD_ALIGN_PARAGRAPH.CENTER)
        cell_write(row.cells[2], str(d.get(f'gp{i}_cambio','') or '-'), size=9, align=WD_ALIGN_PARAGRAPH.CENTER)
        cell_write(row.cells[3], str(d.get(f'gp{i}_medida_nueva','') or '-'), size=9, align=WD_ALIGN_PARAGRAPH.CENTER)
        cell_write(row.cells[4], str(d.get(f'gp{i}_obs','') or ''), size=9)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    add_fotos_seccion(doc, d, ['gp', 'guard', 'gp1', 'gp2'])

    # 5.6 Protectores
    add_para(doc, '5.6 PROTECTORES', bold=True, size=10, color=NARANJA, space_before=6)
    tabla_inspeccion(doc, [
        ('Protector Estático', str(d.get('prot_estatico_estado','') or '-'), str(d.get('prot_estatico_obs','') or '')),
        ('Protector Dinámico', str(d.get('prot_dinamico_estado','') or '-'), str(d.get('prot_dinamico_obs','') or '')),
        ('Fuga de aceite',     str(d.get('prot_din_fuga','') or '-'),        str(d.get('prot_din_fuga_obs','') or '')),
    ])
    add_fotos_seccion(doc, d, ['prot', 'protector'])

    # 5.7 Anillo de Ajuste / Hidráulico
    add_para(doc, '5.7 ANILLO DE AJUSTE Y SISTEMA HIDRÁULICO', bold=True, size=10, color=NARANJA, space_before=6)
    tabla_inspeccion(doc, [
        ('Roscas anillo de fijación', str(d.get('anillo_roscas_estado','') or '-'), str(d.get('anillo_roscas_obs','') or '')),
        ('Nivel hidráulico',          str(d.get('hidraulico_nivel_estado','') or '-'), str(d.get('hidraulico_nivel_obs','') or '')),
        ('GAP aro V1/V2/V3 (mm)',     'Medición', f"{d.get('gap_aro_v1','-')} / {d.get('gap_aro_v2','-')} / {d.get('gap_aro_v3','-')}"),
        ('Fugas Clamping Cylinder',   str(d.get('clamping_fugas_estado','') or '-'), str(d.get('clamping_fugas_obs','') or '')),
    ])

    # ── 6. CONCLUSIONES ───────────────────────────────────────
    seccion_titulo(doc, 6, 'CONCLUSIONES')
    bowl_i_str = str(d.get('bowl_entrante','') or '')
    head_i_str = str(d.get('head_entrante','') or '')
    bowl_s_str = str(d.get('bowl_saliente','') or '')
    head_s_str = str(d.get('head_saliente','') or '')

    conclusiones = [
        f'Se realizó la inspección de los componentes internos, registrándose los hallazgos correspondientes y documentados con evidencias fotográficas.',
        f'HEAD SALIENTE: {head_s_str}  →  HEAD ENTRANTE: {head_i_str}',
        f'BOWL SALIENTE: {bowl_s_str}  →  BOWL ENTRANTE: {bowl_i_str}',
        f'Bowl {bowl_i_str} en buen estado.',
        f'Head {head_i_str} en buen estado.',
        f'Socket Liner: {d.get("sl_fisuras_estado","Sin observaciones") or "Sin observaciones"}.',
        f'Socket: {d.get("socket_fisuras_estado","Sin observaciones") or "Sin observaciones"}.',
        f'MFL: Medida promedio {prom_mfl} mm.',
    ]
    for c in conclusiones:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(c)
        run.font.size = Pt(10)
        run.font.name = 'Arial'

    # ── 7. RECOMENDACIONES ────────────────────────────────────
    seccion_titulo(doc, 7, 'RECOMENDACIONES GENERALES')
    rec = str(d.get('recomendaciones','') or 'Sin recomendaciones.')
    for linea in rec.split('\n'):
        if linea.strip():
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(linea.strip())
            run.font.size = Pt(10)
            run.font.name = 'Arial'

    # ── PIE DE PÁGINA ─────────────────────────────────────────
    add_para(doc, '', space_before=10, space_after=2)
    p_pie = add_para(doc, '© Metso 2025', size=8, color=GRIS_MED,
                     align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=0)

    # ── GUARDAR ───────────────────────────────────────────────
    os.makedirs('reportes', exist_ok=True)
    nombre = f'reportes/InformeMetso_{chancadora}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.docx'
    doc.save(nombre)
    return nombre