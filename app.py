from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from database import init_db, guardar_armado, guardar_cambio, obtener_registros, obtener_tendencias
from word_generator import generar_word_armado, generar_word_cambio
from email_sender import enviar_correo
import os
import uuid
import threading
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

app = Flask(__name__)
app.secret_key = 'metso1250secretkey'

with app.app_context():
    init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/armado')
def armado():
    return render_template('armado.html')

@app.route('/armado/guardar', methods=['POST'])
def guardar_armado_route():
    datos = {}
    campos = ['equipo','cliente','id_bowl','id_head','supervisor_metso','supervisor_cliente','fecha_inicio','fecha_termino','hora_inicio_h','hora_inicio_m','hora_fin_h','hora_fin_m','ub_paso1_estado','ub_paso1_obs','ub_paso2_obs','ub_paso3_estado','ub_paso3_obs','ub_paso4_estado','ub_paso4_obs','ub_paso5_estado','ub_paso5_obs','upper_bushing_cambio','upper_A1','upper_B1','upper_A2','upper_B2','upper_A3','upper_B3','ub_paso7_obs','ub_paso8_obs','ub_paso9_obs','ub_paso10_obs','ub_paso11_obs','ub_paso12_obs','ub_paso13_obs','ub_paso14_obs','ub_paso15_obs','upper_nuevo_A1','upper_nuevo_B1','upper_nuevo_A2','upper_nuevo_B2','upper_nuevo_A3','upper_nuevo_B3','lb_paso16_estado','lb_paso16_obs','lb_paso161_obs','lb_paso17_estado','lb_paso17_obs','lower_bushing_cambio','lower_A1','lower_B1','lower_A2','lower_B2','lower_A3','lower_B3','lower_A4','lower_B4','lower_A5','lower_B5','lower_A6','lower_B6','lb_paso21_obs','lb_paso22_obs','lb_paso221_obs','lb_paso24_obs','lb_paso25_obs','lb_paso26_obs','lower_nuevo_A1','lower_nuevo_B1','lower_nuevo_A2','lower_nuevo_B2','lower_nuevo_A3','lower_nuevo_B3','lower_nuevo_A4','lower_nuevo_B4','lower_nuevo_A5','lower_nuevo_B5','lower_nuevo_A6','lower_nuevo_B6','hb_paso28_estado','hb_paso28_obs','hb_paso29_estado','hb_paso29_obs','head_ball_cambio','hb_paso31_real','hb_paso31_obs','hb_paso32_real','hb_paso32_obs','hb_paso33_real','hb_paso33_obs','carter_sup_estado','carter_sup_obs','carter_inf_estado','carter_inf_obs','feed_plate_estado','fp_paso36_obs','feed_plate_cambio','feed_plate_altura','feed_plate_desgaste','fp_paso38_estado','fp_paso38_obs','fp_paso39_estado','fp_paso39_obs','fp_paso40_obs','ln_paso41_estado','ln_paso41_obs','ln_diametro','ln_espaciamiento','ln_torque50','ln_torque75','ln_torque100','ln_serial_torq','ln_gap1','ln_gap2','epoxi_cantidad','epoxi_venc_catalizador','epoxi_venc_epoxico','epoxi_temp_sin_cat','epoxi_temp_con_cat','bowl_paso54_estado','bowl_paso54_obs','bowl_medida_hooper','bowl_paso56_estado','bowl_paso56_obs','bowl_paso57_estado','bowl_paso57_obs','bowl_paso58_estado','bowl_paso58_obs','bowl_medida_fisuras','bowl_paso582_obs','bowl_paso60_estado','bowl_paso60_obs','bowl_paso61_estado','bowl_paso61_obs','bowl_paso62_estado','bowl_paso62_obs','bowl_medida_fisura62','bowl_paso622_obs','hora_fin_h','hora_fin_m','recomendaciones','correo_destino']
    for campo in campos:
        valor = request.form.get(campo, '')
        try:
            if valor == '':
                datos[campo] = None
            elif '.' in str(valor):
                datos[campo] = float(valor)
            else:
                try:
                    datos[campo] = int(valor)
                except:
                    datos[campo] = valor
        except:
            datos[campo] = valor
        
    fotos_paths = {}
    for key in request.files:
        foto = request.files[key]
        if foto and foto.filename:
            try:
                print(f'📸 Subiendo foto {key} a Cloudinary...')
                resultado = cloudinary.uploader.upload(
                    foto,
                    folder='protocolos',
                    transformation=[{'width': 800, 'height': 600, 'crop': 'limit', 'quality': 60}]
                )
                fotos_paths[f'foto_path_{key.replace("foto_", "")}'] = resultado['secure_url']
                print(f'✅ Foto subida: {resultado["secure_url"]}')
            except Exception as e:
                print(f'❌ Error subiendo foto {key}: {e}')

    guardar_armado(datos)
    datos_word = dict(datos)
    datos_word.update(fotos_paths)
    print(f'FOTOS: {list(fotos_paths.keys())}')
    ruta_word = generar_word_armado(datos_word)

    # Recopilar correos seleccionados
    correos = []
    for key in ['correo_raul', 'correo_jason', 'correo_joselyn', 'correo_mauricio', 'correo_miguel', 'correo_francisco', 'correo_edgar', 'correo_juan', 'correo_marco', 'correo_luis', 'correo_jorge', 'correo_richard', 'correo_jaime', 'correo_elvis', 'correo_gabriel']:
        val = request.form.get(key, '')
        if val:
            correos.append(val)
    correo_extra = request.form.get('correo_destino', '').strip()
    if correo_extra:
        correos.append(correo_extra)
    correo_destino = ', '.join(correos)

    if correo_destino:
        try:
            ruta_correo = generar_word_armado(datos_word)
            asunto = f"Protocolo Armado H&B | {str(datos.get('fecha_termino') or '')} | {str(datos.get('equipo') or '')} | {str(datos.get('supervisor_metso') or '')}"
            enviar_correo(correo_destino, asunto, ruta_correo)
        except Exception as e:
            print(f'❌ Error correo: {e}')
    flash('✅ Protocolo guardado y enviado por correo!')
    return redirect(url_for('index'))

@app.route('/cambio')
def cambio():
    return render_template('cambio.html')

@app.route('/cambio/guardar', methods=['POST'])
def guardar_cambio_route():
    datos = {}
    campos = ['fecha_inicio','fecha_termino','supervisor_cliente','supervisor_metso','cliente','chancadora',
        'head_saliente','bowl_saliente','altura_bowl_saliente','hora_inicio_h','hora_inicio_m','correo_destino',
        'anillo_roscas_estado','anillo_roscas_obs',
        'hidraulico_nivel_estado','hidraulico_nivel_obs',
        'gap_aro_v1','gap_aro_v2','gap_aro_v3',
        'clamping_fugas_estado','clamping_fugas_obs',
        'sl_ranuras_estado','sl_ranuras_obs',
        'socket_B1','socket_A1','socket_B2','socket_A2',
        'socket_B3','socket_A3','socket_B4','socket_A4',
        'socket_B5','socket_A5','socket_B6','socket_A6',
        'sl_asentamiento_estado','sl_asentamiento_obs',
        'sl_gap_interior','sl_gap_exterior',
        'sl_fisuras_estado','sl_fisuras_obs',
        'sl_deformaciones_estado','sl_deformaciones_obs',
        'sl_canales_estado','sl_canales_obs',
        'sl_cambio_ahora','sl_cambio_siguiente',
        'sl_ret_precalentar','sl_ret_precalentar_obs',
        'sl_ret_tornillos','sl_ret_tornillos_obs',
        'sl_mont_precalentar','sl_mont_precalentar_obs',
        'sl_mont_tornillos','sl_mont_tornillos_obs',
        'sl_mont_enfriamiento','sl_mont_enfriamiento_obs',
        'sl_mont_asentamiento','sl_mont_asentamiento_obs',
        'sl_mont_gap_interno','sl_mont_gap_externo',
        'socket_fisuras_estado','socket_fisuras_obs',
        'socket_pernos_estado','socket_pernos_obs',
        'socket_ranuras_estado','socket_ranuras_obs',
        'socket_deform_estado','socket_deform_obs',
        'socket_canales_estado','socket_canales_obs',
        'socket_gap_0','socket_gap_90','socket_gap_180','socket_gap_270',
        'socket_cambio_ahora','socket_cambio_siguiente',
        'sk_ret_calentar_obs',
        'sk_sal_A1','sk_sal_A2','sk_sal_A3','sk_sal_A4',
        'sk_sal_B1','sk_sal_B2','sk_sal_B3','sk_sal_B4',
        'sk_sal_C1','sk_sal_C2','sk_sal_C3','sk_sal_C4',
        'sk_sal_D1','sk_sal_D2','sk_sal_D3','sk_sal_D4',
        'sk_mont_calentar_obs','sk_mont_enfriar_obs','sk_mont_gap_obs',
        'sk_new_A1','sk_new_A2','sk_new_A3','sk_new_A4',
        'sk_new_B1','sk_new_B2','sk_new_B3','sk_new_B4',
        'sk_new_C1','sk_new_C2','sk_new_C3','sk_new_C4',
        'sk_new_D1','sk_new_D2','sk_new_D3','sk_new_D4',
        'mainshaft_obs',
        'ms_A1','ms_A2','ms_A3','ms_A4',
        'ms_B1','ms_B2','ms_B3','ms_B4',
        'ms_C1','ms_C2','ms_C3','ms_C4',
        'ms_D1','ms_D2','ms_D3','ms_D4',
        'mfl_pernos_estado','mfl_pernos_obs','mfl_medida',
        'mfl_med_A','mfl_med_B','mfl_med_C','mfl_med_D',
        'mfl_med_E','mfl_med_F','mfl_med_G',
        'mfl_cambio_ahora','mfl_cambio_siguiente',
        'mfl_mont_pernos','mfl_mont_pernos_obs',
        'mfl_new_A','mfl_new_B','mfl_new_C','mfl_new_D',
        'mfl_new_E','mfl_new_F','mfl_new_G',
        'montura_barras_estado','montura_barras_obs',
        'montura_acumulacion_estado','montura_acumulacion_obs',
        'montura_chocky_estado','montura_chocky_obs',
        'montura_cambio_ahora','montura_cambio_siguiente',
        'gp1_cambio','gp1_medida','gp1_obs',
        'gp2_cambio','gp2_medida','gp2_obs',
        'gp3_cambio','gp3_medida','gp3_obs',
        'gp4_cambio','gp4_medida','gp4_obs',
        'gp5_cambio','gp5_medida','gp5_obs',
        'gp6_cambio','gp6_medida','gp6_obs',
        'prot_estatico_estado','prot_estatico_obs',
        'prot_dinamico_estado','prot_dinamico_obs',
        'prot_din_fuga','prot_din_fuga_obs',
        'contrapeso_estado','contrapeso_obs',
        'sello_ut_estado','sello_ut_obs',
        'head_entrante','bowl_entrante','altura_bowl_entrante',
        'hora_fin_h','hora_fin_m','recomendaciones']
    for campo in campos:
        valor = request.form.get(campo, '')
        try:
            if valor == '':
                datos[campo] = None
            elif '.' in str(valor):
                datos[campo] = float(valor)
            else:
                try:
                    datos[campo] = int(valor)
                except:
                    datos[campo] = valor
        except:
            datos[campo] = valor
    
    fotos_paths = {}
    for key in request.files:
        foto = request.files[key]
        if foto and foto.filename:
            try:
                resultado = cloudinary.uploader.upload(
                    foto,
                    folder='protocolos',
                    transformation=[{'width': 800, 'height': 600, 'crop': 'limit', 'quality': 60}]
                )
                fotos_paths[f'foto_path_{key.replace("foto_", "")}'] = resultado['secure_url']
            except Exception as e:
                print(f'Error subiendo foto {key}: {e}')

    guardar_cambio(datos)
    datos_word = dict(datos)
    datos_word.update(fotos_paths)
    ruta_word = generar_word_cambio(datos_word)

    # Recopilar correos seleccionados
    correos = []
    for key in ['correo_raul', 'correo_jason', 'correo_joselyn', 'correo_mauricio', 'correo_miguel', 'correo_francisco', 'correo_edgar', 'correo_juan', 'correo_marco', 'correo_luis', 'correo_jorge', 'correo_richard', 'correo_jaime', 'correo_elvis', 'correo_gabriel']:
        val = request.form.get(key, '')
        if val:
            correos.append(val)
    correo_extra = request.form.get('correo_destino', '').strip()
    if correo_extra:
        correos.append(correo_extra)
    correo_destino = ', '.join(correos)

    if correo_destino:
        try:
            ruta_correo = generar_word_cambio(datos_word)
            asunto_cambio = f"Protocolo Cambio H&B | {str(datos.get('fecha_termino') or '')} | {str(datos.get('chancadora') or '')} | {str(datos.get('supervisor_metso') or '')}"
            enviar_correo(correo_destino, asunto_cambio, ruta_correo)
        except Exception as e:
            print(f'❌ Error correo: {e}')
    flash('✅ Protocolo guardado y enviado por correo!')
    return redirect(url_for('index'))

@app.route('/historial/<tipo>')
def historial(tipo):
    registros = obtener_registros(tipo)
    return render_template('historial.html', registros=registros, tipo=tipo)

@app.route('/tendencias')
def tendencias():
    tab = request.args.get('tab', 'armado')

    # ── ARMADO ──────────────────────────────────────────────
    tipo_filtro = request.args.get('tipo_filtro', 'id_bowl')
    codigo = request.args.get('codigo', '').strip()

    upper = []
    fechas_armado = []
    upper_A1 = upper_B1 = upper_A2 = upper_B2 = upper_A3 = upper_B3 = []
    lower_A1 = lower_B1 = lower_A2 = lower_B2 = lower_A3 = lower_B3 = []
    lower_A4 = lower_B4 = lower_A5 = lower_B5 = lower_A6 = lower_B6 = []
    feed_medida = []

    if tab == 'armado' and codigo:
        import psycopg2
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        c = conn.cursor()
        campo_filtro = 'id_bowl' if tipo_filtro == 'id_bowl' else 'id_head'        
        query_armado = "SELECT fecha_registro, upper_A1, upper_B1, upper_A2, upper_B2, upper_A3, upper_B3, lower_A1, lower_B1, lower_A2, lower_B2, lower_A3, lower_B3, lower_A4, lower_B4, lower_A5, lower_B5, lower_A6, lower_B6, feed_plate_altura FROM armado_hb WHERE " + campo_filtro + " = %s ORDER BY fecha_registro ASC"
        c.execute(query_armado, (codigo,))
        rows = c.fetchall()
        conn.close()
        upper = rows
        fechas_armado = [r[0] for r in rows]
        upper_A1 = [r[1] for r in rows]
        upper_B1 = [r[2] for r in rows]
        upper_A2 = [r[3] for r in rows]
        upper_B2 = [r[4] for r in rows]
        upper_A3 = [r[5] for r in rows]
        upper_B3 = [r[6] for r in rows]
        lower_A1 = [r[7] for r in rows]
        lower_B1 = [r[8] for r in rows]
        lower_A2 = [r[9] for r in rows]
        lower_B2 = [r[10] for r in rows]
        lower_A3 = [r[11] for r in rows]
        lower_B3 = [r[12] for r in rows]
        lower_A4 = [r[13] for r in rows]
        lower_B4 = [r[14] for r in rows]
        lower_A5 = [r[15] for r in rows]
        lower_B5 = [r[16] for r in rows]
        lower_A6 = [r[17] for r in rows]
        lower_B6 = [r[18] for r in rows]
        feed_medida = [r[19] for r in rows]

    # ── CAMBIO ──────────────────────────────────────────────
    codigo_cambio = request.args.get('codigo_cambio', '').strip()
    cambio_data = []
    fechas_cambio = []
    sl_B1 = sl_A1 = sl_B2 = sl_A2 = sl_B3 = sl_A3 = []
    sl_B4 = sl_A4 = sl_B5 = sl_A5 = sl_B6 = sl_A6 = []
    gap_interior = gap_exterior = []
    gap_sk_0 = gap_sk_90 = gap_sk_180 = gap_sk_270 = []
    mfl_A = mfl_B = mfl_C = mfl_D = mfl_E = mfl_F = mfl_G = []
    gp1 = gp2 = gp3 = gp4 = gp5 = gp6 = []

    if tab == 'cambio' and codigo_cambio:
        import psycopg2
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        c = conn.cursor()
        query_cambio = "SELECT fecha_registro, socket_B1, socket_A1, socket_B2, socket_A2, socket_B3, socket_A3, socket_B4, socket_A4, socket_B5, socket_A5, socket_B6, socket_A6, sl_gap_interior, sl_gap_exterior, socket_gap_0, socket_gap_90, socket_gap_180, socket_gap_270, mfl_med_A, mfl_med_B, mfl_med_C, mfl_med_D, mfl_med_E, mfl_med_F, mfl_med_G, gp1_medida, gp2_medida, gp3_medida, gp4_medida, gp5_medida, gp6_medida FROM cambio_hb WHERE chancadora = %s ORDER BY fecha_registro ASC"
        c.execute(query_cambio, (codigo_cambio,))
        rows = c.fetchall()
        conn.close()
        cambio_data = rows
        fechas_cambio = [r[0] for r in rows]
        sl_B1 = [r[1] for r in rows]
        sl_A1 = [r[2] for r in rows]
        sl_B2 = [r[3] for r in rows]
        sl_A2 = [r[4] for r in rows]
        sl_B3 = [r[5] for r in rows]
        sl_A3 = [r[6] for r in rows]
        sl_B4 = [r[7] for r in rows]
        sl_A4 = [r[8] for r in rows]
        sl_B5 = [r[9] for r in rows]
        sl_A5 = [r[10] for r in rows]
        sl_B6 = [r[11] for r in rows]
        sl_A6 = [r[12] for r in rows]
        gap_interior = [r[13] for r in rows]
        gap_exterior = [r[14] for r in rows]
        gap_sk_0 = [r[15] for r in rows]
        gap_sk_90 = [r[16] for r in rows]
        gap_sk_180 = [r[17] for r in rows]
        gap_sk_270 = [r[18] for r in rows]
        mfl_A = [r[19] for r in rows]
        mfl_B = [r[20] for r in rows]
        mfl_C = [r[21] for r in rows]
        mfl_D = [r[22] for r in rows]
        mfl_E = [r[23] for r in rows]
        mfl_F = [r[24] for r in rows]
        mfl_G = [r[25] for r in rows]
        gp1 = [r[26] for r in rows]
        gp2 = [r[27] for r in rows]
        gp3 = [r[28] for r in rows]
        gp4 = [r[29] for r in rows]
        gp5 = [r[30] for r in rows]
        gp6 = [r[31] for r in rows]

    return render_template('tendencias.html',
        tab=tab,
        tipo_filtro=tipo_filtro,
        codigo=codigo,
        upper=upper,
        fechas_armado=fechas_armado,
        upper_A1=upper_A1, upper_B1=upper_B1,
        upper_A2=upper_A2, upper_B2=upper_B2,
        upper_A3=upper_A3, upper_B3=upper_B3,
        lower_A1=lower_A1, lower_B1=lower_B1,
        lower_A2=lower_A2, lower_B2=lower_B2,
        lower_A3=lower_A3, lower_B3=lower_B3,
        lower_A4=lower_A4, lower_B4=lower_B4,
        lower_A5=lower_A5, lower_B5=lower_B5,
        lower_A6=lower_A6, lower_B6=lower_B6,
        feed_medida=feed_medida,
        codigo_cambio=codigo_cambio,
        cambio_data=cambio_data,
        fechas_cambio=fechas_cambio,
        sl_B1=sl_B1, sl_A1=sl_A1,
        sl_B2=sl_B2, sl_A2=sl_A2,
        sl_B3=sl_B3, sl_A3=sl_A3,
        sl_B4=sl_B4, sl_A4=sl_A4,
        sl_B5=sl_B5, sl_A5=sl_A5,
        sl_B6=sl_B6, sl_A6=sl_A6,
        gap_interior=gap_interior,
        gap_exterior=gap_exterior,
        gap_sk_0=gap_sk_0, gap_sk_90=gap_sk_90,
        gap_sk_180=gap_sk_180, gap_sk_270=gap_sk_270,
        mfl_A=mfl_A, mfl_B=mfl_B, mfl_C=mfl_C,
        mfl_D=mfl_D, mfl_E=mfl_E, mfl_F=mfl_F, mfl_G=mfl_G,
        gp1=gp1, gp2=gp2, gp3=gp3,
        gp4=gp4, gp5=gp5, gp6=gp6
    )
@app.route('/descargar/<tipo>/<int:id>')
def descargar_reporte(tipo, id):
    import psycopg2
    from psycopg2.extras import RealDictCursor
    database_url = os.environ.get('DATABASE_URL')
    tabla = 'armado_hb' if tipo == 'armado' else 'cambio_hb'
    try:
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        c = conn.cursor()
        c.execute(f'SELECT * FROM {tabla} WHERE id = %s', (id,))
        registro = c.fetchone()
        conn.close()
    except Exception as e:
        import sqlite3
        conn = sqlite3.connect('protocolos.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(f'SELECT * FROM {tabla} WHERE id = ?', (id,))
        registro = c.fetchone()
        conn.close()
    if not registro:
        return 'No encontrado', 404
    datos = dict(registro)
    print(f'DEBUG socket_B1: {datos.get("socket_b1")} tipo: {type(datos.get("socket_b1"))}')
    # Normalizar claves para compatibilidad PostgreSQL
    datos_norm = {}
    for k, v in datos.items():
        datos_norm[k] = v
        datos_norm[k.lower()] = v
        # Reconstruir con mayúsculas para word_generator
        partes = k.split('_')
        clave_mixed = partes[0] + '_' + '_'.join(p[0].upper() + p[1:] if len(p) > 1 else p.upper() for p in partes[1:]) if len(partes) > 1 else k
        datos_norm[clave_mixed] = v    
    datos = datos_norm
    if tipo == 'armado':
        ruta = generar_word_armado(datos)
        nombre = f"Armado_{datos.get('equipo','X')}.docx"
    else:
        ruta = generar_word_cambio(datos)
        nombre = f"Cambio_{datos.get('chancadora','X')}.docx"
    return send_file(ruta, as_attachment=True, download_name=nombre)

@app.route('/dashboard')
def dashboard():
    import psycopg2
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM armado_hb")
    total_armado = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM cambio_hb")
    total_cambio = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM armado_hb WHERE upper_bushing_cambio = 'SI'")
    ub_cambio = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM cambio_hb WHERE sl_cambio_ahora = 'SI'")
    sl_cambio = c.fetchone()[0]
    
    c.execute("SELECT cliente, COUNT(*) as total FROM armado_hb GROUP BY cliente ORDER BY total DESC")
    clientes = c.fetchall()
    
    c.execute("SELECT chancadora, COUNT(*) as total FROM cambio_hb GROUP BY chancadora ORDER BY total DESC")
    chancadoras = c.fetchall()
    
    conn.close()
    
    return render_template('dashboard.html',
        total_armado=total_armado,
        total_cambio=total_cambio,
        ub_cambio=ub_cambio,
        sl_cambio=sl_cambio,
        clientes=clientes,
        chancadoras=chancadoras
    )

# ============================================================
# CHATBOT IA — pegar ANTES de la línea: if __name__ == '__main__':
# ============================================================
import psycopg2
from psycopg2.extras import RealDictCursor
import requests as http_requests

# ── Crear tabla de documentos si no existe ──────────────────
def init_chat_db():
    try:
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS chat_documentos (
                id SERIAL PRIMARY KEY,
                nombre TEXT NOT NULL,
                contenido TEXT NOT NULL,
                tipo TEXT DEFAULT 'texto',
                subido_por TEXT DEFAULT 'admin',
                fecha_subida TIMESTAMP DEFAULT NOW()
            )
        ''')
        conn.commit()
        conn.close()
        print('✅ Tabla chat_documentos lista')
    except Exception as e:
        print(f'❌ Error init_chat_db: {e}')

with app.app_context():
    init_chat_db()

# ── Página principal del chat ───────────────────────────────
@app.route('/chat')
def chat():
    try:
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        c = conn.cursor()
        c.execute('SELECT id, nombre, tipo, subido_por, fecha_subida FROM chat_documentos ORDER BY fecha_subida DESC')
        docs = c.fetchall()
        conn.close()
    except Exception as e:
        print(f'Error cargando docs: {e}')
        docs = []
    return render_template('chat.html', documentos=docs)

# ── Subir documento ─────────────────────────────────────────
@app.route('/chat/subir', methods=['POST'])
def chat_subir():
    archivo = request.files.get('documento')
    subido_por = request.form.get('subido_por', 'admin').strip() or 'admin'

    if not archivo or not archivo.filename:
        flash('❌ No se seleccionó ningún archivo')
        return redirect(url_for('chat'))

    nombre = archivo.filename
    ext = nombre.rsplit('.', 1)[-1].lower() if '.' in nombre else ''

    try:
        if ext == 'pdf':
            # Leer PDF con pdfplumber
            import pdfplumber, io
            contenido_bytes = archivo.read()
            texto = ''
            with pdfplumber.open(io.BytesIO(contenido_bytes)) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        texto += t + '\n'
            if not texto.strip():
                texto = '[PDF sin texto extraíble — puede ser imagen escaneada]'
            tipo = 'pdf'
        else:
            # TXT, MD, CSV, DOCX básico
            contenido_bytes = archivo.read()
            try:
                texto = contenido_bytes.decode('utf-8')
            except:
                texto = contenido_bytes.decode('latin-1', errors='ignore')
            tipo = ext or 'texto'

        # Truncar a 50.000 caracteres para no explotar la BD
        texto = texto[:50000]

        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        c = conn.cursor()
        c.execute(
            'INSERT INTO chat_documentos (nombre, contenido, tipo, subido_por) VALUES (%s, %s, %s, %s)',
            (nombre, texto, tipo, subido_por)
        )
        conn.commit()
        conn.close()
        flash(f'✅ Documento "{nombre}" subido correctamente')
    except Exception as e:
        print(f'❌ Error subiendo doc: {e}')
        flash(f'❌ Error al procesar el archivo: {str(e)}')

    return redirect(url_for('chat'))

# ── Eliminar documento ──────────────────────────────────────
@app.route('/chat/eliminar/<int:doc_id>', methods=['POST'])
def chat_eliminar(doc_id):
    try:
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        c = conn.cursor()
        c.execute('DELETE FROM chat_documentos WHERE id = %s', (doc_id,))
        conn.commit()
        conn.close()
        flash('🗑️ Documento eliminado')
    except Exception as e:
        flash(f'❌ Error: {e}')
    return redirect(url_for('chat'))

# ── Endpoint AJAX para el chat ──────────────────────────────
@app.route('/chat/preguntar', methods=['POST'])
def chat_preguntar():
    data = request.get_json()
    pregunta = (data.get('pregunta') or '').strip()
    historial = data.get('historial', [])   # lista de {role, content}

    if not pregunta:
        return {'error': 'Pregunta vacía'}, 400

    # Cargar todos los documentos de la BD
    try:
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        c = conn.cursor()
        c.execute('SELECT nombre, contenido FROM chat_documentos ORDER BY fecha_subida DESC')
        docs = c.fetchall()
        conn.close()
    except Exception as e:
        return {'error': f'Error BD: {e}'}, 500

    if not docs:
        return {'respuesta': '⚠️ No hay documentos cargados aún. Ve a la sección de Asistente IA y sube los procedimientos primero.'}, 200

    # Armar contexto con los documentos
    contexto = ''
    for nombre, contenido in docs:
        contexto += f'\n\n=== DOCUMENTO: {nombre} ===\n{contenido}\n=== FIN {nombre} ===\n'

    system_prompt = f"""Eres el Asistente IA de Metso para protocolos de chancadoras MP1250.
Tienes acceso a los siguientes documentos de procedimientos de trabajo:
{contexto}

INSTRUCCIONES:
- Responde SIEMPRE basándote en el contenido de los documentos.
- Si la respuesta está en los documentos, cítala con claridad.
- Si no está en los documentos, dilo explícitamente.
- Responde en español, de forma clara y estructurada.
- Si hay pasos numerados, mantenlos así.
- Sé conciso pero completo."""

    # Armar mensajes con historial
    messages = []
    for msg in historial[-10:]:   # últimos 10 mensajes para no pasar el límite
        if msg.get('role') in ('user', 'assistant') and msg.get('content'):
            messages.append({'role': msg['role'], 'content': msg['content']})
    messages.append({'role': 'user', 'content': pregunta})

    # Llamar a la API de Anthropic
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        return {'error': 'Falta configurar ANTHROPIC_API_KEY en las variables de entorno de Render'}, 500

    try:
        resp = http_requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json'
            },
            json={
                'model': 'claude-sonnet-4-20250514',
                'max_tokens': 1500,
                'system': system_prompt,
                'messages': messages
            },
            timeout=30
        )
        resultado = resp.json()
        print(f'🔍 Respuesta API: {resultado}')
        respuesta = resultado['content'][0]['text']
        return {'respuesta': respuesta}
    except Exception as e:
        print(f'❌ Error API Claude: {e}')
        return {'error': f'Error al contactar la IA: {str(e)}'}, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)