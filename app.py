from flask import Flask, render_template, request, redirect, url_for, flash, send_file 
from database import init_db, guardar_armado, guardar_cambio, obtener_registros, obtener_tendencias
from word_generator import generar_word_armado, generar_word_cambio
from email_sender import enviar_correo
import os
import uuid
import threading
import cloudinary
import cloudinary.uploader
from reportlab.graphics.widgets.markers import makeMarker

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
    campos = ['equipo','cliente','id_bowl','id_head','id_bowl_turno','id_bowl_forro','id_head_turno','id_head_forro','supervisor_metso','supervisor_cliente','fecha_inicio','fecha_termino','hora_inicio_h','hora_inicio_m','hora_fin_h','hora_fin_m','ub_paso1_estado','ub_paso1_obs','ub_paso2_obs','ub_paso3_estado','ub_paso3_obs','ub_paso4_estado','ub_paso4_obs','ub_paso5_estado','ub_paso5_obs','upper_bushing_cambio','upper_A1','upper_B1','upper_A2','upper_B2','upper_A3','upper_B3','ub_paso7_obs','ub_paso8_obs','ub_paso9_obs','ub_paso10_obs','ub_paso11_obs','ub_paso12_obs','ub_paso13_obs','ub_paso14_obs','ub_paso15_obs','upper_nuevo_A1','upper_nuevo_B1','upper_nuevo_A2','upper_nuevo_B2','upper_nuevo_A3','upper_nuevo_B3','lb_paso16_estado','lb_paso16_obs','lb_paso161_obs','lb_paso17_estado','lb_paso17_obs','lower_bushing_cambio','lower_A1','lower_B1','lower_A2','lower_B2','lower_A3','lower_B3','lower_A4','lower_B4','lower_A5','lower_B5','lower_A6','lower_B6','lb_paso21_obs','lb_paso22_obs','lb_paso221_obs','lb_paso24_obs','lb_paso25_obs','lb_paso26_obs','lower_nuevo_A1','lower_nuevo_B1','lower_nuevo_A2','lower_nuevo_B2','lower_nuevo_A3','lower_nuevo_B3','lower_nuevo_A4','lower_nuevo_B4','lower_nuevo_A5','lower_nuevo_B5','lower_nuevo_A6','lower_nuevo_B6','hb_paso28_estado','hb_paso28_obs','hb_paso29_estado','hb_paso29_obs','head_ball_cambio','hb_paso31_real','hb_paso31_obs','hb_paso32_real','hb_paso32_obs','hb_paso33_real','hb_paso33_obs','carter_sup_estado','carter_sup_obs','carter_inf_estado','carter_inf_obs','feed_plate_estado','fp_paso36_obs','feed_plate_cambio','feed_plate_altura','feed_plate_desgaste','feed_plate_nueva_medida','fp_paso38_estado','fp_paso38_obs','fp_paso39_estado','fp_paso39_obs','fp_paso40_obs','ln_paso41_estado','ln_paso41_obs','ln_diametro','ln_espaciamiento','ln_torque50','ln_torque75','ln_torque100','ln_serial_torq','ln_gap1','ln_gap2','epoxi_cantidad','epoxi_cantidad_bowl','epoxi_venc_catalizador','epoxi_venc_epoxico','epoxi_temp_sin_cat','epoxi_temp_con_cat','gap_headcore_headliner','gap_bowl_bowlliner','bowl_paso54_estado','bowl_paso54_obs','bowl_medida_hooper','bowl_paso56_estado','bowl_paso56_obs','bowl_paso57_estado','bowl_paso57_obs','bowl_paso58_estado','bowl_paso58_obs','bowl_medida_fisuras','bowl_paso582_obs','bowl_paso60_estado','bowl_paso60_obs','bowl_paso61_estado','bowl_paso61_obs','bowl_paso62_estado','bowl_paso62_obs','bowl_medida_fisura62','bowl_paso63_estado','bowl_paso63_obs','bowl_paso64_estado','bowl_paso64_obs','bowl_paso65_obs','bowl_paso622_obs','hora_fin_h','hora_fin_m','hc_insp_estado','hc_insp_obs','hc_ndt_obs','hc_pernos_estado','hc_pernos_obs','hc_aceite_obs','hc_limpieza_estado','hc_limpieza_obs','hc_grasa_obs','hc_cambio','recomendaciones','correo_destino']
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
        'anillo_ndt_obs', 'anillo_gap_peineta',
        'anillo_cilindros_estado', 'anillo_cilindros_obs',
        'hidraulico_nivel_estado','hidraulico_nivel_obs',
        'gap_aro_v1','gap_aro_v2','gap_aro_v3',
        'clamping_fugas_estado','clamping_fugas_obs',
        'sl_ranuras_estado','sl_ranuras_obs',
        'socket_B1','socket_A1','socket_B2','socket_A2',
        'socket_B3','socket_A3','socket_B4','socket_A4',
        'socket_B5','socket_A5','socket_B6','socket_A6',
        'socket_med_a', 'socket_med_b', 'socket_med_c', 'socket_med_d',
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
        'ms_F1', 'ms_F2', 'ms_F3', 'ms_F4',
        'mfl_pernos_estado','mfl_pernos_obs','mfl_medida',
        'mfl_med_A','mfl_med_B','mfl_med_C','mfl_med_D',
        'mfl_med_E','mfl_med_F','mfl_med_G', 'mfl_med_H',
        'mfl_cambio_ahora','mfl_cambio_siguiente',
        'mfl_mont_pernos','mfl_mont_pernos_obs',
        'mfl_wearing_estado', 'mfl_wearing_obs',
        'mfl_new_A','mfl_new_B','mfl_new_C','mfl_new_D',
        'mfl_new_E','mfl_new_F','mfl_new_G', 'mfl_new_H',
        'montura_barras_estado','montura_barras_obs',
        'montura_acumulacion_estado','montura_acumulacion_obs',
        'montura_chocky_estado','montura_chocky_obs',
        'montura_cambio_ahora','montura_cambio_siguiente',
        'montura_brazos_estado', 'montura_brazos_obs',
        'montura_caja_estado', 'montura_caja_obs',
        'gp1_cambio','gp1_medida','gp1_obs',
        'gp2_cambio','gp2_medida','gp2_obs',
        'gp3_cambio','gp3_medida','gp3_obs',
        'gp4_cambio','gp4_medida','gp4_obs',
        'gp5_cambio','gp5_medida','gp5_obs',
        'gp6_cambio','gp6_medida','gp6_obs',
        'gp1_medida_nueva','gp2_medida_nueva','gp3_medida_nueva',
        'gp4_medida_nueva','gp5_medida_nueva','gp6_medida_nueva',
        'prot_estatico_estado','prot_estatico_obs', 'prot_estatico_espesor',
        'prot_dinamico_estado','prot_dinamico_obs',
        'prot_din_fuga','prot_din_fuga_obs', 'prot_dinamico_desgaste',
        'contrapeso_estado','contrapeso_obs',
        'sello_ut_estado','sello_ut_obs',
        'excentrica_cambio',
        'exc_prot_din_estado', 'exc_prot_din_obs',
        'exc_pernos_prot_estado', 'exc_pernos_prot_obs',
        'exc_sellos_estado', 'exc_sellos_obs',
        'exc_distancia_vertical',
        'exc_bocina_estado', 'exc_bocina_obs',
        'exc_metro_a1', 'exc_metro_b1', 'exc_metro_c1', 'exc_metro_d1',
        'exc_metro_a2', 'exc_metro_b2', 'exc_metro_c2', 'exc_metro_d2',
        'exc_metro_a3', 'exc_metro_b3', 'exc_metro_c3', 'exc_metro_d3',
        'exc_lower_tb_estado', 'exc_lower_tb_obs',
        'exc_pernos_lower_estado', 'exc_pernos_lower_obs',
        'exc_upper_tb_estado', 'exc_upper_tb_obs',
        'exc_pernos_upper_estado', 'exc_pernos_upper_obs',
        'exc_rampas_estado', 'exc_rampas_obs',
        'exc_tornillos_estado', 'exc_tornillos_obs',
        'exc_backlash', 'exc_lainas',
        'chute_faldon_estado', 'chute_faldon_obs',
        'chute_liners_estado', 'chute_liners_obs',
        'chute_placa_estado', 'chute_placa_obs',
        'head_entrante','bowl_entrante','altura_bowl_entrante','altura_final_bowl',
        'hora_fin_h','hora_fin_m','recomendaciones',
        'sistemas_aux_inspeccion','trans_frecuencia',
        'trans_polea_estado','trans_polea_obs','trans_radiador_estado','trans_radiador_obs',
        'acum_pres_1','acum_pres_2','acum_pres_3','acum_pres_4','acum_pres_5',
        'acum_pres_6','acum_pres_7','acum_pres_8','acum_pres_consola',
        'acum_final_1','acum_final_2','acum_final_3','acum_final_4','acum_final_5',
        'acum_final_6','acum_final_7','acum_final_8','acum_final_consola',
        'hidra_bloque_estado','hidra_bloque_obs','hidra_bomba_estado','hidra_bomba_obs',
        'hidra_motor1_estado','hidra_motor1_obs','hidra_motor2_estado','hidra_motor2_obs',
        'hidra_motor3_estado','hidra_motor3_obs',
        'blower_filtro_estado','blower_filtro_obs','blower_cambio_filtro','blower_cambio_obs',
        'lubri_cedazo_estado','lubri_cedazo_obs','lubri_junta_estado', 'lubri_junta_obs',
        'lubri_lineas_estado', 'lubri_lineas_obs', 'trans_inspeccion', 'hidra_inspeccion', 'blower_inspeccion', 'lubri_inspeccion',
        'lubri_presion_filtros']
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
    from flask import request as freq
    filtros = {}
    if tipo == 'cambio':
        filtros['chancadora'] = freq.args.get('chancadora', '')
        filtros['supervisor_metso'] = freq.args.get('supervisor_metso', '')
        filtros['fecha'] = freq.args.get('fecha', '')
    else:
        filtros['id_bowl'] = freq.args.get('id_bowl', '')
        filtros['id_head'] = freq.args.get('id_head', '')
        filtros['supervisor_metso'] = freq.args.get('supervisor_metso', '')
        filtros['fecha'] = freq.args.get('fecha', '')
    
    registros = obtener_registros(tipo, filtros)
    return render_template('historial.html', registros=registros, tipo=tipo, filtros=filtros)
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
    print(f'DEBUG epoxi: {datos.get("epoxi_venc_catalizador")} | {datos.get("epoxi_Venc_Catalizador")}')
    if tipo == 'armado':
        ruta = generar_word_armado(datos)
        fecha = str(datos.get('fecha_inicio','') or '').replace('-','')[:8]
        id_head = datos.get('id_head','') or 'X'
        id_bowl = datos.get('id_bowl','') or 'X'
        nombre = f"{fecha}_ArmadoHB_{id_head}_{id_bowl}.docx"
    else:
        ruta = generar_word_cambio(datos)
        fecha = str(datos.get('fecha_inicio','') or '').replace('-','')[:8]
        chancadora = datos.get('chancadora','') or 'X'
        nombre = f"{fecha}_CambioHB_{chancadora}.docx"
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
            print(f'📄 Texto extraído: {len(texto)} caracteres, páginas procesadas')
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
        return {'error': 'Falta configurar ANTHROPIC_API_KEY en Render'}, 500

    try:
        resp = http_requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json'
            },
            json={
                'model': 'claude-sonnet-4-5',
                'max_tokens': 1500,
                'system': system_prompt,
                'messages': messages
            },
            timeout=30
        )
        resultado = resp.json()
        respuesta = resultado['content'][0]['text']
        return {'respuesta': respuesta}
    except Exception as e:
        print(f'❌ Error API Claude: {e}')
        return {'error': f'Error al contactar la IA: {str(e)}'}, 500
@app.route('/informe')
def informe():
    return render_template('informe.html')

@app.route('/informe/descargar/<chancadora>')
def descargar_informe(chancadora):
    import psycopg2
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.graphics.shapes import Drawing, String, Line
    from reportlab.graphics.charts.lineplots import LinePlot
    from reportlab.lib.units import cm
    import io

    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    c = conn.cursor()
    c.execute('''SELECT * FROM cambio_hb WHERE chancadora = %s 
                 ORDER BY fecha_inicio DESC LIMIT 1''', (chancadora,))
    cols = [desc[0] for desc in c.description]
    row = c.fetchone()
    c.execute('''SELECT fecha_inicio, 
                 socket_b1, socket_a1, socket_b2, socket_a2,
                 socket_b3, socket_a3, socket_b4, socket_a4,
                 socket_b5, socket_a5, socket_b6, socket_a6,
                 sl_gap_interior, sl_gap_exterior,
                 socket_gap_0, socket_gap_90, socket_gap_180, socket_gap_270,
                 mfl_med_a, mfl_med_b, mfl_med_c, mfl_med_d, mfl_med_e, mfl_med_f, mfl_med_g,
                 gp1_medida, gp2_medida, gp3_medida, gp4_medida, gp5_medida, gp6_medida,
                 altura_bowl_saliente, altura_bowl_entrante, altura_final_bowl,
                 sl_cambio_ahora, socket_cambio_ahora, mfl_cambio_ahora, montura_cambio_ahora
                 FROM cambio_hb WHERE chancadora = %s 
                 ORDER BY fecha_inicio ASC''', (chancadora,))
    historial = c.fetchall()
    conn.close()

    if not row:
        return f'No hay registros para {chancadora}', 404

    d = dict(zip(cols, row))
    fechas = [str(h[0])[:10] for h in historial]

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()

    titulo_style = ParagraphStyle('titulo', parent=styles['Heading1'],
                                  fontSize=16, fontName='Helvetica-Bold',
                                  textColor=colors.black, spaceAfter=6)
    subtitulo_style = ParagraphStyle('subtitulo', parent=styles['Heading2'],
                                     fontSize=12, fontName='Helvetica-Bold',
                                     textColor=colors.HexColor('#0f5132'),
                                     spaceBefore=12, spaceAfter=6)
    normal_style = ParagraphStyle('normal', parent=styles['Normal'],
                                  fontSize=10, spaceAfter=4)

    def tabla_datos(datos_tabla):
        t = Table(datos_tabla, colWidths=[10*cm, 7*cm])
        t.setStyle(TableStyle([
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('PADDING', (0,0), (-1,-1), 6),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ]))
        return t

    def grafico_lineas(valores, etiquetas, titulo, vmin=None, vmax=None, limite_min=None, limite_max=None):
        ancho = 15*cm
        alto = 7*cm
        try:
            from reportlab.graphics.widgets.markers import makeMarker
            d_graf = Drawing(ancho, alto)
            vals_limpios = [float(v) if v is not None and v != 0 else None for v in valores]
            vals_num = [v for v in vals_limpios if v is not None]
            if not vals_num:
                return None
            lp = LinePlot()
            lp.x = 35
            lp.y = 25
            lp.width = ancho - 55
            lp.height = alto - 45
            data = [(i, v) for i, v in enumerate(vals_limpios) if v is not None]
            lp.data = [data]
            lp.lines[0].strokeColor = colors.HexColor('#1a3a5c')
            lp.lines[0].strokeWidth = 1.5
            lp.lines[0].symbol = makeMarker('FilledCircle')
            lp.lines[0].symbol.size = 4
            lp.lines[0].symbol.fillColor = colors.HexColor('#1a3a5c')
            auto_min = min(vals_num) * 0.9
            auto_max = max(vals_num) * 1.1
            lp.xValueAxis.valueMin = 0
            lp.xValueAxis.valueMax = max(len(vals_limpios) - 1, 1)
            lp.xValueAxis.valueSteps = list(range(len(vals_limpios)))
            lp.xValueAxis.labelTextFormat = lambda x: str(etiquetas[int(x)])[:7] if 0 <= int(x) < len(etiquetas) else ''
            lp.xValueAxis.labels.angle = 30
            lp.xValueAxis.labels.fontSize = 6
            y_min = vmin if vmin is not None else auto_min
            y_max = vmax if vmax is not None else auto_max
            if limite_min is not None: y_min = min(y_min, limite_min * 0.9)
            if limite_max is not None: y_max = max(y_max, limite_max * 1.1)
            if y_min == y_max: y_max = y_min + 1
            lp.yValueAxis.valueMin = y_min
            lp.yValueAxis.valueMax = y_max
            lp.yValueAxis.labels.fontSize = 7
            d_graf.add(lp)
            def y_to_px(val):
                return lp.y + (val - y_min) / (y_max - y_min) * lp.height
            if limite_min is not None:
                y_px = y_to_px(limite_min)
                d_graf.add(Line(lp.x, y_px, lp.x + lp.width, y_px,
                                strokeColor=colors.red, strokeWidth=1, strokeDashArray=[4,2]))
                d_graf.add(String(lp.x + lp.width + 2, y_px - 3,
                                  f'Min:{limite_min}', fontSize=6, fillColor=colors.red))
            if limite_max is not None:
                y_px = y_to_px(limite_max)
                d_graf.add(Line(lp.x, y_px, lp.x + lp.width, y_px,
                                strokeColor=colors.HexColor('#e67e00'), strokeWidth=1, strokeDashArray=[4,2]))
                d_graf.add(String(lp.x + lp.width + 2, y_px - 3,
                                  f'Max:{limite_max}', fontSize=6, fillColor=colors.HexColor('#e67e00')))
            d_graf.add(String(lp.x, alto - 10, titulo, fontSize=8,
                              fontName='Helvetica-Bold', fillColor=colors.HexColor('#1a3a5c')))
            return d_graf
        except Exception as e:
            print(f'Error grafico_lineas: {e}')
            return None

    story = []

    # Encabezado
    story.append(Paragraph('METSO', ParagraphStyle('metso', parent=styles['Normal'],
                            fontSize=20, fontName='Helvetica-Bold', spaceAfter=4)))
    story.append(Paragraph(f'Informe Estado Chancadora {chancadora}', titulo_style))
    story.append(Paragraph(f'Ultima intervencion: {d.get("fecha_registro", "-")} | Supervisor: {d.get("supervisor_metso", "-")} | Cliente: {d.get("cliente", "-")}', normal_style))
    story.append(tabla_datos([
        ['Altura Bowl Saliente', str(d.get('altura_bowl_saliente') or '-') + ' pulg'],
        ['Altura Final Bowl', str(d.get('altura_final_bowl') or '-') + ' pulg'],
    ]))
    story.append(Spacer(1, 0.5*cm))

    # 0. Anillo de ajuste
    story.append(Paragraph('0. Inspeccion Anillo de Ajuste', subtitulo_style))
    story.append(tabla_datos([
        ['Roscas anillo de fijacion', str(d.get('anillo_roscas_estado') or '-')],
        ['Observaciones', str(d.get('anillo_roscas_obs') or '-')],
    ]))

    # 1. Socket Liner
    story.append(Paragraph('1. Estado de Socket Liner', subtitulo_style))
    sl_vals = []
    for i in range(1, 7):
        b = d.get(f'socket_b{i}')
        a = d.get(f'socket_a{i}')
        if b: sl_vals.append(float(b))
        if a: sl_vals.append(float(a))
    promedio_sl = round(sum(sl_vals)/len(sl_vals), 2) if sl_vals else '-'
    story.append(tabla_datos([
        ['Promedio canales de lubricacion', str(promedio_sl) + ' mm'],
        ['GAP Interior', str(d.get('sl_gap_interior') or '-') + ' mm'],
        ['GAP Exterior', str(d.get('sl_gap_exterior') or '-') + ' mm'],
        ['Presencia de fisuras', str(d.get('sl_fisuras_estado') or '-')],
        ['Observaciones fisuras', str(d.get('sl_fisuras_obs') or '-')],
        ['Se cambio en esta intervencion?', str(d.get('sl_cambio_ahora') or '-')],
        ['Se recomienda cambio?', str(d.get('sl_cambio_siguiente') or '-')],
    ]))
    if len(historial) > 1:
        promedios_sl = []
        for h in historial:
            vals = [float(h[i+1]) for i in range(12) if h[i+1] is not None]
            promedios_sl.append(round(sum(vals)/len(vals), 2) if vals else 0)
        cambios_sl = [str(h[0])[:7] for h in historial if len(h) > 35 and h[35] == 'SI']
        texto_sl = f'Cambios: {", ".join(cambios_sl)}' if cambios_sl else 'Sin cambios registrados'
        g = grafico_lineas(promedios_sl, fechas, 'Promedio Socket Liner', limite_min=5, limite_max=10)
        if g:
            story.append(Paragraph('Historial promedio metrologia Socket Liner', normal_style))
            story.append(Paragraph(texto_sl, ParagraphStyle('sl', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#0f5132'), spaceAfter=4)))
            story.append(g)

    # 2. Socket
    story.append(Paragraph('2. Estado de Socket', subtitulo_style))
    gap_vals = [d.get('socket_gap_0'), d.get('socket_gap_90'), d.get('socket_gap_180'), d.get('socket_gap_270')]
    gap_nums = [float(v) for v in gap_vals if v is not None]
    promedio_gap = round(sum(gap_nums)/len(gap_nums), 2) if gap_nums else '-'
    story.append(tabla_datos([
        ['Observaciones fisuras', str(d.get('socket_fisuras_obs') or '-')],
        ['GAP 0', str(d.get('socket_gap_0') or '-') + ' mm'],
        ['GAP 90', str(d.get('socket_gap_90') or '-') + ' mm'],
        ['GAP 180', str(d.get('socket_gap_180') or '-') + ' mm'],
        ['GAP 270', str(d.get('socket_gap_270') or '-') + ' mm'],
        ['Promedio GAP', str(promedio_gap) + ' mm'],
        ['Se cambio?', str(d.get('socket_cambio_ahora') or '-')],
        ['Se recomienda cambio?', str(d.get('socket_cambio_siguiente') or '-')],
    ]))
    if len(historial) > 1:
        gaps_prom = []
        for h in historial:
            gv = [float(h[i]) for i in [15,16,17,18] if h[i] is not None]
            gaps_prom.append(round(sum(gv)/len(gv), 2) if gv else 0)
        cambios_socket = [str(h[0])[:7] for h in historial if len(h) > 36 and h[36] == 'SI']
        texto_socket = f'Cambios: {", ".join(cambios_socket)}' if cambios_socket else 'Sin cambios registrados'
        g = grafico_lineas(gaps_prom, fechas, 'GAP Socket Mainshaft', limite_min=0)
        if g:
            story.append(Paragraph('Historial promedio GAP Socket-Mainshaft', normal_style))
            story.append(Paragraph(texto_socket, ParagraphStyle('sk', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#0f5132'), spaceAfter=4)))
            story.append(g)

    # 3. MFL
    story.append(Paragraph('3. Main Frame Liners', subtitulo_style))
    mfl_vals = [d.get(f'mfl_med_{x}') for x in ['a','b','c','d','e','f','g','h']]
    mfl_nums = [float(v) for v in mfl_vals if v is not None]
    promedio_mfl = round(sum(mfl_nums)/len(mfl_nums), 2) if mfl_nums else '-'
    mfl_data = [['A','B','C','D','E','F','G','H','Promedio']]
    mfl_data.append([str(d.get(f'mfl_med_{x}') or '-') for x in ['a','b','c','d','e','f','g','h']] + [str(promedio_mfl)])
    t_mfl = Table(mfl_data, colWidths=[1.8*cm]*8 + [2.6*cm])
    t_mfl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f5132')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_mfl)
    story.append(Spacer(1, 0.3*cm))
    story.append(tabla_datos([
        ['Se cambio?', str(d.get('mfl_cambio_ahora') or '-')],
        ['Se recomienda cambio?', str(d.get('mfl_cambio_siguiente') or '-')],
    ]))
    if len(historial) > 1:
        promedios_mfl = []
        for h in historial:
            mv = [float(h[i+19]) for i in range(7) if h[i+19] is not None]
            promedios_mfl.append(round(sum(mv)/len(mv), 2) if mv else 0)
        cambios_mfl = [str(h[0])[:7] for h in historial if len(h) > 37 and h[37] == 'SI']
        texto_mfl = f'Cambios: {", ".join(cambios_mfl)}' if cambios_mfl else 'Sin cambios registrados'
        g = grafico_lineas(promedios_mfl, fechas, 'Promedio MFL', limite_min=9, limite_max=70)
        if g:
            story.append(Paragraph('Historial promedio MFL', normal_style))
            story.append(Paragraph(texto_mfl, ParagraphStyle('mfl', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#0f5132'), spaceAfter=4)))
            story.append(g)

    # 4. Monturas
    story.append(Paragraph('4. Monturas', subtitulo_style))
    cambios_montura = [str(h[0])[:7] for h in historial if len(h) > 38 and h[38] == 'SI']
    texto_montura = f'Cambios: {", ".join(cambios_montura)}' if cambios_montura else 'Sin cambios registrados'
    story.append(Paragraph(texto_montura, ParagraphStyle('mont', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#0f5132'), spaceAfter=4)))
    story.append(tabla_datos([
        ['Estado barras de soporte montura contraeje', str(d.get('montura_barras_estado') or '-')],
        ['Estado Chocky Bar', str(d.get('montura_chocky_estado') or '-')],
        ['Se cambio?', str(d.get('montura_cambio_ahora') or '-')],
        ['Se recomienda cambio?', str(d.get('montura_cambio_siguiente') or '-')],
    ]))

    # 5. Guard Pins
    story.append(Paragraph('5. Guard Pins', subtitulo_style))
    gp_data = [['Guard Pin', 'Medida', 'Se cambio?', 'Observaciones']]
    for i in range(1, 7):
        gp_data.append([f'GP {i}', str(d.get(f'gp{i}_medida') or '-'),
                        str(d.get(f'gp{i}_cambio') or '-'),
                        str(d.get(f'gp{i}_obs') or '-')])
    t_gp = Table(gp_data, colWidths=[3*cm, 3.5*cm, 3.5*cm, 7*cm])
    t_gp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f5132')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f9f9f9')]),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_gp)
    if len(historial) > 1:
        for gp_idx in range(1, 7):
            def safe_float(v):
                try: return float(str(v).replace('mm','').replace('cm','').strip())
                except: return 0
            gp_vals_hist = [safe_float(h[25+gp_idx]) if h[25+gp_idx] is not None else 0 for h in historial]
            if any(v > 0 for v in gp_vals_hist):
                g = grafico_lineas(gp_vals_hist, fechas, f'Guard Pin {gp_idx}')
                if g:
                    story.append(Paragraph(f'Historial Guard Pin {gp_idx}', normal_style))
                    story.append(g)

    # 6. Protector Estatico
    story.append(Paragraph('6. Protector Estatico', subtitulo_style))
    story.append(tabla_datos([
        ['Estado protector estatico', str(d.get('prot_estatico_estado') or '-')],
        ['Observaciones', str(d.get('prot_estatico_obs') or '-')],
    ]))

    # 7. Protector Dinamico
    story.append(Paragraph('7. Protector Dinamico', subtitulo_style))
    story.append(tabla_datos([
        ['Estado protector dinamico', str(d.get('prot_dinamico_estado') or '-')],
        ['Hay presencia de fuga de aceite?', str(d.get('prot_din_fuga') or '-')],
        ['Observaciones', str(d.get('prot_dinamico_obs') or '-')],
    ]))

    # 8. Recomendaciones
    story.append(Paragraph('8. Recomendaciones para la siguiente intervencion', subtitulo_style))
    story.append(Paragraph(str(d.get('recomendaciones') or 'Sin recomendaciones.'), normal_style))

    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True,
                     download_name=f'Informe_{chancadora}_{str(d.get("fecha_registro",""))[:10]}.pdf',
                     mimetype='application/pdf')

@app.route('/alturas', methods=['GET', 'POST'])
def alturas():
    import psycopg2
    from datetime import datetime
    
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    c = conn.cursor()
    
    if request.method == 'POST':
        chancadora = request.form.get('chancadora')
        fecha = request.form.get('fecha')
        altura = request.form.get('altura')
        operador = request.form.get('operador')
        dias_parada = int(request.form.get('dias_parada') or 0)
        fecha_registro = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute('''INSERT INTO altura_bowl (chancadora, fecha, altura, operador, dias_parada, fecha_registro)
                     VALUES (%s, %s, %s, %s, %s, %s)''',
                  (chancadora, fecha, altura, operador, dias_parada, fecha_registro))
        conn.commit()
    
    chancadoras = ['CR011','CR012','CR013','CR014','CR021','CR022','CR023','CR024']
    chancadora_sel = request.args.get('chancadora', request.form.get('chancadora', 'CR011'))
    
    c.execute('''SELECT fecha, altura, operador, dias_parada FROM altura_bowl
             WHERE chancadora = %s AND (ciclo_cerrado = FALSE OR ciclo_cerrado IS NULL)
             ORDER BY fecha ASC''', (chancadora_sel,))
    registros = c.fetchall()
    conn.close()
    
    return render_template('alturas.html',
                           registros=registros,
                           chancadora_sel=chancadora_sel,
                           chancadoras=chancadoras)


@app.route('/alturas/nuevo_ciclo', methods=['POST'])
def alturas_nuevo_ciclo():
    import psycopg2
    chancadora = request.form.get('chancadora')
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    c = conn.cursor()
    c.execute('''UPDATE altura_bowl SET ciclo_cerrado = TRUE
                 WHERE chancadora = %s AND (ciclo_cerrado = FALSE OR ciclo_cerrado IS NULL)''',
              (chancadora,))
    conn.commit()
    conn.close()
    return redirect(f'/alturas?chancadora={chancadora}')

@app.route('/proyecciones')
def proyecciones():
    import psycopg2
    from datetime import datetime
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    c = conn.cursor()
    
    chancadoras = ['CR011','CR012','CR013','CR014','CR021','CR022','CR023','CR024']
    proyecciones = {}
    
    for ch in chancadoras:
        c.execute('''SELECT fecha, altura FROM altura_bowl
                     WHERE chancadora = %s AND (ciclo_cerrado = FALSE OR ciclo_cerrado IS NULL)
                     ORDER BY fecha ASC''', (ch,))
        registros = c.fetchall()
        
        if len(registros) >= 2:
            fechas = [r[0] for r in registros]
            alturas = [float(r[1]) for r in registros]
            t0 = datetime.strptime(str(fechas[0]), '%Y-%m-%d')
            dias = [(datetime.strptime(str(f), '%Y-%m-%d') - t0).days for f in fechas]
            
            n = len(dias)
            sumX = sum(dias)
            sumY = sum(alturas)
            sumXY = sum(dias[i]*alturas[i] for i in range(n))
            sumX2 = sum(x*x for x in dias)
            m = (n*sumXY - sumX*sumY) / (n*sumX2 - sumX*sumX)
            b = (sumY - m*sumX) / n
            
            if m < 0:
                dia_limite = (9.0 - b) / m
                import math
                fecha_cambio = t0 + __import__('datetime').timedelta(days=math.floor(dia_limite))
                proyecciones[ch] = fecha_cambio.strftime('%Y-%m-%d')
    
    conn.close()
    return render_template('proyecciones.html', proyecciones=proyecciones)

@app.route('/informe/metso/<int:id>')
def descargar_informe_metso(id):
    import psycopg2
    from psycopg2.extras import RealDictCursor
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'), cursor_factory=RealDictCursor)
    c = conn.cursor()
    c.execute('SELECT * FROM cambio_hb WHERE id = %s', (id,))
    registro = c.fetchone()
    conn.close()
    if not registro:
        return 'No encontrado', 404
    datos = dict(registro)
    from word_generator import generar_informe_metso
    ruta = generar_informe_metso(datos)
    nombre = f"InformeMetso_{datos.get('chancadora','X')}_{datos.get('fecha_inicio','')}.docx"
    return send_file(ruta, as_attachment=True, download_name=nombre)

# ══════════════════════════════════════════════════════════════
# MÓDULO GANTT — pegar en app.py antes de: if __name__ == '__main__':
# ══════════════════════════════════════════════════════════════

# Actividades planificadas del Cronograma (del Excel)

ACTIVIDADES_GANTT = [
    {"id": 1,  "nombre": "Bloqueo",                                                                         "inicio_plan": "08:30", "fin_plan": "08:45", "duracion": 0.25, "recursos": "SMCV"},
    {"id": 2,  "nombre": "Retiro de pernos de segmento de feeder",                                         "inicio_plan": "08:45", "fin_plan": "09:15", "duracion": 0.5,  "recursos": ""},
    {"id": 3,  "nombre": "Retiro de Guardas y pines",                                                      "inicio_plan": "08:45", "fin_plan": "09:15", "duracion": 0.5,  "recursos": ""},
    {"id": 4,  "nombre": "Retiro de Ductos nivel Chancadora",                                              "inicio_plan": "08:45", "fin_plan": "09:45", "duracion": 1.0,  "recursos": ""},
    {"id": 5,  "nombre": "Retiro de sensores de Chancadora y Feeder",                                      "inicio_plan": "08:45", "fin_plan": "09:45", "duracion": 1.0,  "recursos": "SMCV"},
    {"id": 6,  "nombre": "Desmontaje de Segmento de Feeder",                                               "inicio_plan": "09:45", "fin_plan": "10:09", "duracion": 0.4,  "recursos": "Grúa"},
    {"id": 7,  "nombre": "Retracción de feeder, Limpieza y desmontaje de chute",                           "inicio_plan": "10:09", "fin_plan": "10:33", "duracion": 0.4,  "recursos": "Grúa"},
    {"id": 8,  "nombre": "Desbloqueo Sist. Hidráulico, Desenroscado de Bowl y Bloqueo Sist. Hidráulico",  "inicio_plan": "10:33", "fin_plan": "10:57", "duracion": 0.4,  "recursos": "SMCV"},
    {"id": 9,  "nombre": "Inspección y cambio de Liners de Chute",                                        "inicio_plan": "10:57", "fin_plan": "13:57", "duracion": 3.0,  "recursos": ""},
    {"id": 10, "nombre": "Retiro de Bowl",                                                                 "inicio_plan": "10:57", "fin_plan": "11:21", "duracion": 0.4,  "recursos": "Grúa"},
    {"id": 11, "nombre": "Retiro de Head",                                                                 "inicio_plan": "11:21", "fin_plan": "11:45", "duracion": 0.4,  "recursos": "Grúa"},
    {"id": 12, "nombre": "Limpieza de Componentes internos",                                               "inicio_plan": "11:45", "fin_plan": "12:15", "duracion": 0.5,  "recursos": ""},
    {"id": 13, "nombre": "Inspección y metrología de Componentes Internos",                               "inicio_plan": "12:15", "fin_plan": "12:45", "duracion": 0.5,  "recursos": ""},
    {"id": 14, "nombre": "Montaje de Head",                                                                "inicio_plan": "12:45", "fin_plan": "13:09", "duracion": 0.4,  "recursos": "Grúa"},
    {"id": 15, "nombre": "Montaje de Bowl",                                                                "inicio_plan": "13:09", "fin_plan": "13:33", "duracion": 0.4,  "recursos": "Grúa"},
    {"id": 16, "nombre": "Desbloqueo Sist. Hidráulico, Roscado de Bowl y Bloqueo Sist. Hidráulico",       "inicio_plan": "13:33", "fin_plan": "13:57", "duracion": 0.4,  "recursos": "SMCV"},
    {"id": 17, "nombre": "Montaje de Chute",                                                               "inicio_plan": "13:57", "fin_plan": "14:27", "duracion": 0.5,  "recursos": "Grúa"},
    {"id": 18, "nombre": "Instalación de Ductos",                                                          "inicio_plan": "14:27", "fin_plan": "15:27", "duracion": 1.0,  "recursos": ""},
    {"id": 19, "nombre": "Extensión de Feeder",                                                            "inicio_plan": "14:27", "fin_plan": "14:57", "duracion": 0.5,  "recursos": ""},
    {"id": 20, "nombre": "Instalación de sensores de Chancadora y Feeder",                                "inicio_plan": "14:27", "fin_plan": "15:27", "duracion": 1.0,  "recursos": "SMCV"},
    {"id": 21, "nombre": "Montaje de Segmento de Feeder y ajuste de pernos",                              "inicio_plan": "14:27", "fin_plan": "14:57", "duracion": 0.5,  "recursos": "Grúa"},
    {"id": 22, "nombre": "Instalación de Guardas y pines",                                                "inicio_plan": "15:27", "fin_plan": "15:57", "duracion": 0.5,  "recursos": ""},
    {"id": 23, "nombre": "Desbloqueo",                                                                     "inicio_plan": "15:57", "fin_plan": "16:12", "duracion": 0.25, "recursos": "SMCV"},
]

ACTIVIDADES_ARMADO = [
    {"id": 1,  "nombre": "Charla de seguridad y permisos de trabajo",                              "inicio_plan": "07:30", "fin_plan": "08:00", "duracion": 0.5,  "recursos": ""},
    {"id": 2,  "nombre": "Check list de herramientas y equipos / grúa semi pórtico",               "inicio_plan": "08:00", "fin_plan": "08:30", "duracion": 0.5,  "recursos": ""},
    {"id": 3,  "nombre": "Demarcación de áreas de trabajo",                                        "inicio_plan": "08:00", "fin_plan": "08:30", "duracion": 0.5,  "recursos": ""},
    {"id": 4,  "nombre": "Posicionamiento de Head y Bowl",                                         "inicio_plan": "08:30", "fin_plan": "09:00", "duracion": 0.5,  "recursos": "Grúa"},
    {"id": 5,  "nombre": "Instalación de plataformas y escaleras de acceso en Bowl",               "inicio_plan": "09:00", "fin_plan": "09:30", "duracion": 0.5,  "recursos": "Grúa"},
    {"id": 6,  "nombre": "Limpieza de Bowl y retiro pernos y cuñas",                               "inicio_plan": "09:30", "fin_plan": "10:30", "duracion": 1.0,  "recursos": ""},
    {"id": 7,  "nombre": "Instalación de maniobra",                                                "inicio_plan": "10:30", "fin_plan": "11:00", "duracion": 0.5,  "recursos": "Grúa"},
    {"id": 8,  "nombre": "Reubicación de Bowl y limpieza mecánica",                                "inicio_plan": "11:00", "fin_plan": "12:30", "duracion": 1.5,  "recursos": "Grúa"},
    {"id": 9,  "nombre": "Instalación de Bowl sobre Bowl liner",                                   "inicio_plan": "12:30", "fin_plan": "13:30", "duracion": 1.0,  "recursos": "Grúa"},
    {"id": 10, "nombre": "Instalación de pernos cuñas en Bowl",                                    "inicio_plan": "13:30", "fin_plan": "14:30", "duracion": 1.0,  "recursos": ""},
    {"id": 11, "nombre": "Ajuste de pernos",                                                       "inicio_plan": "14:30", "fin_plan": "15:15", "duracion": 0.75, "recursos": ""},
    {"id": 12, "nombre": "Aplicación de Backing",                                                  "inicio_plan": "15:15", "fin_plan": "16:45", "duracion": 1.5,  "recursos": ""},
    {"id": 13, "nombre": "Instalación de sellos de polvo en Bowl",                                 "inicio_plan": "16:45", "fin_plan": "17:30", "duracion": 0.75, "recursos": ""},
    {"id": 14, "nombre": "Inspección y metrología de Head",                                        "inicio_plan": "09:00", "fin_plan": "11:00", "duracion": 2.0,  "recursos": ""},
    {"id": 15, "nombre": "Instalación de Plataforma de armado",                                    "inicio_plan": "11:00", "fin_plan": "11:30", "duracion": 0.5,  "recursos": "Grúa"},
    {"id": 16, "nombre": "Corte de anillo de sacrificio, soldeo de orejas y corte pernos feed plate", "inicio_plan": "11:30", "fin_plan": "12:30", "duracion": 1.0,  "recursos": ""},
    {"id": 17, "nombre": "Desmontaje de Feed Plate",                                               "inicio_plan": "12:30", "fin_plan": "13:00", "duracion": 0.5,  "recursos": "Grúa"},
    {"id": 18, "nombre": "Retiro de Seguros, pernos y limpieza de Locking Nut",                    "inicio_plan": "13:00", "fin_plan": "14:30", "duracion": 1.5,  "recursos": ""},
    {"id": 19, "nombre": "Desmontaje de Locking Nut",                                              "inicio_plan": "13:00", "fin_plan": "13:30", "duracion": 0.5,  "recursos": "Grúa"},
    {"id": 20, "nombre": "Retiro de Plataforma",                                                   "inicio_plan": "13:30", "fin_plan": "14:00", "duracion": 0.5,  "recursos": "Grúa"},
    {"id": 21, "nombre": "Desmontaje de forro usado",                                              "inicio_plan": "14:00", "fin_plan": "14:30", "duracion": 0.5,  "recursos": "Grúa"},
    {"id": 22, "nombre": "Inspección y limpieza mecánica de Head",                                 "inicio_plan": "14:30", "fin_plan": "15:30", "duracion": 1.0,  "recursos": ""},
    {"id": 23, "nombre": "Montaje de Plataforma y forro nuevo",                                    "inicio_plan": "15:30", "fin_plan": "16:00", "duracion": 0.5,  "recursos": "Grúa"},
    {"id": 24, "nombre": "Instalación de anillo de sacrificio y Locking Nut",                      "inicio_plan": "16:00", "fin_plan": "16:24", "duracion": 0.4,  "recursos": "Grúa"},
    {"id": 25, "nombre": "Retorqueo de pernos de Locking Nut",                                     "inicio_plan": "16:24", "fin_plan": "17:24", "duracion": 1.0,  "recursos": ""},
    {"id": 26, "nombre": "Instalación de seguros y soldeo Locking Nut",                            "inicio_plan": "17:24", "fin_plan": "17:48", "duracion": 0.4,  "recursos": ""},
    {"id": 27, "nombre": "Montaje de Feed Plate",                                                   "inicio_plan": "17:48", "fin_plan": "18:12", "duracion": 0.4,  "recursos": "Grúa"},
    {"id": 28, "nombre": "Corte de Orejas",                                                        "inicio_plan": "18:12", "fin_plan": "18:36", "duracion": 0.4,  "recursos": ""},
    {"id": 29, "nombre": "Aplicación de Backing (Head)",                                           "inicio_plan": "18:36", "fin_plan": "19:00", "duracion": 0.4,  "recursos": ""},
] 

ACTIVIDADES_ESCANEO = [
    {"id": 1,  "nombre": "Bloqueo",                                                                              "inicio_plan": "08:30", "fin_plan": "08:45",   "duracion": 0.25, "recursos": "SMCV"},
    {"id": 2,  "nombre": "Retiro de pernos de segmento de feeder",                                              "inicio_plan": "08:45", "fin_plan": "09:15",   "duracion": 0.5,  "recursos": ""},
    {"id": 3,  "nombre": "Retiro de Guardas y pines",                                                           "inicio_plan": "08:45", "fin_plan": "09:15",   "duracion": 0.5,  "recursos": ""},
    {"id": 4,  "nombre": "Retiro de Ductos nivel Chancadora",                                                   "inicio_plan": "08:45", "fin_plan": "09:45",   "duracion": 1.0,  "recursos": ""},
    {"id": 5,  "nombre": "Retiro de sensores de Chancadora y Feeder",                                           "inicio_plan": "08:45", "fin_plan": "09:45",   "duracion": 1.0,  "recursos": "SMCV"},
    {"id": 6,  "nombre": "Desmontaje de Segmento de Feeder",                                                    "inicio_plan": "09:45", "fin_plan": "10:15",   "duracion": 0.5,  "recursos": "Grúa"},
    {"id": 7,  "nombre": "Retracción de feeder, Limpieza y desmontaje de chute",                                "inicio_plan": "10:15", "fin_plan": "10:45",   "duracion": 0.5,  "recursos": "Grúa"},
    {"id": 8,  "nombre": "Desbloqueo Sist. Hidráulico, Desenroscado de Bowl y Bloqueo Sist. Hidráulico",        "inicio_plan": "10:45", "fin_plan": "11:15",   "duracion": 0.4,  "recursos": "SMCV"},
    {"id": 9,  "nombre": "Retiro de Bowl",                                                                       "inicio_plan": "11:15", "fin_plan": "11:45",   "duracion": 0.4,  "recursos": "Grúa"},
    {"id": 10, "nombre": "Inspección y cambio de Liners de Chute",                                              "inicio_plan": "11:45", "fin_plan": "14:45",   "duracion": 7.0,  "recursos": ""},
    {"id": 11, "nombre": "Cambio de faldón de chute de alimentación",                                           "inicio_plan": "14:45", "fin_plan": "15:45",   "duracion": 1.0,  "recursos": ""},
    {"id": 12, "nombre": "Retiro de Head",                                                                       "inicio_plan": "11:45", "fin_plan": "12:30",   "duracion": 0.4,  "recursos": "Grúa"},
    {"id": 13, "nombre": "Limpieza de Componentes internos",                                                    "inicio_plan": "12:30", "fin_plan": "13:00",   "duracion": 0.4,  "recursos": ""},
    {"id": 14, "nombre": "Inspección y metrología de Componentes Internos",                                     "inicio_plan": "13:00", "fin_plan": "13:30",   "duracion": 0.4,  "recursos": ""},
    {"id": 15, "nombre": "Limpieza de monturas",                                                                 "inicio_plan": "14:00", "fin_plan": "14:30",   "duracion": 0.4,  "recursos": ""},
    {"id": 16, "nombre": "Retiro de protector estático",                                                        "inicio_plan": "14:30", "fin_plan": "15:00",   "duracion": 0.4,  "recursos": ""},
    {"id": 17, "nombre": "Soldeo de orejas en monturas y corte de barras (contraeje)",                          "inicio_plan": "15:00", "fin_plan": "16:30",   "duracion": 1.0,  "recursos": ""},
    {"id": 18, "nombre": "Pruebas NDT de orejas de izaje MFL / monturas de contraeje",                         "inicio_plan": "16:30", "fin_plan": "17:00",   "duracion": 0.5,  "recursos": ""},
    {"id": 19, "nombre": "Desmontaje de grapas y pernos de los MFLs",                                          "inicio_plan": "17:00", "fin_plan": "18:00",   "duracion": 1.0,  "recursos": ""},
    {"id": 20, "nombre": "Instalación de Sombrero (protector)",                                                 "inicio_plan": "13:30", "fin_plan": "14:00",   "duracion": 0.5,  "recursos": ""},
    {"id": 21, "nombre": "Instalación de araña y retiro de MFLs (YAHLE)",                                      "inicio_plan": "18:00", "fin_plan": "20:00",   "duracion": 1.6,  "recursos": ""},
    {"id": 22, "nombre": "Desmontaje de monturas de brazos",                                                    "inicio_plan": "20:00", "fin_plan": "21:30",   "duracion": 1.5,  "recursos": ""},
    {"id": 23, "nombre": "Limpieza previa para escaneo",                                                        "inicio_plan": "21:30", "fin_plan": "22:00",   "duracion": 0.5,  "recursos": ""},
    {"id": 24, "nombre": "Escaneo",                                                                             "inicio_plan": "22:00", "fin_plan": "23:30",   "duracion": 1.5,  "recursos": ""},
    {"id": 25, "nombre": "Cambio de guard pin (a condición)",                                                   "inicio_plan": "23:30", "fin_plan": "24:00",   "duracion": 0.5,  "recursos": ""},
    {"id": 26, "nombre": "Retiro de sombrero",                                                                  "inicio_plan": "23:30", "fin_plan": "23:45",   "duracion": 0.25, "recursos": ""},
    {"id": 27, "nombre": "Montaje de MFLs",                                                                     "inicio_plan": "23:45", "fin_plan": "25:45",   "duracion": 2.0,  "recursos": ""},
    {"id": 28, "nombre": "Montaje de monturas de brazos y contraeje",                                           "inicio_plan": "25:45", "fin_plan": "26:45",   "duracion": 1.0,  "recursos": ""},
    {"id": 29, "nombre": "Soldeo de Barras en Monturas de contraeje",                                           "inicio_plan": "26:45", "fin_plan": "27:45",   "duracion": 1.0,  "recursos": ""},
    {"id": 30, "nombre": "Reforzamiento con Wearing en MFL",                                                    "inicio_plan": "27:45", "fin_plan": "28:45",   "duracion": 1.0,  "recursos": ""},
    {"id": 31, "nombre": "Montaje de Head",                                                                     "inicio_plan": "28:45", "fin_plan": "29:15",   "duracion": 0.5,  "recursos": "Grúa"},
    {"id": 32, "nombre": "Montaje de Bowl",                                                                     "inicio_plan": "29:15", "fin_plan": "29:45",   "duracion": 0.5,  "recursos": "Grúa"},
    {"id": 33, "nombre": "Desbloqueo Sist. Hidráulico, Roscado de Bowl y Bloqueo Sist. Hidráulico",             "inicio_plan": "29:45", "fin_plan": "30:15",   "duracion": 0.5,  "recursos": "SMCV"},
    {"id": 34, "nombre": "Montaje de Chute",                                                                    "inicio_plan": "30:15", "fin_plan": "30:45",   "duracion": 0.5,  "recursos": "Grúa"},
    {"id": 35, "nombre": "Instalación de Ductos",                                                               "inicio_plan": "30:45", "fin_plan": "32:15",   "duracion": 1.5,  "recursos": ""},
    {"id": 36, "nombre": "Extensión de Feeder",                                                                 "inicio_plan": "30:45", "fin_plan": "31:15",   "duracion": 0.5,  "recursos": ""},
    {"id": 37, "nombre": "Instalación de sensores de Chancadora y Feeder",                                      "inicio_plan": "30:45", "fin_plan": "31:45",   "duracion": 1.0,  "recursos": "SMCV"},
    {"id": 38, "nombre": "Montaje de Segmento de Feeder y ajuste de pernos",                                   "inicio_plan": "30:45", "fin_plan": "31:15",   "duracion": 0.5,  "recursos": "Grúa"},
    {"id": 39, "nombre": "Instalación de Guardas y pines",                                                      "inicio_plan": "31:45", "fin_plan": "32:15",   "duracion": 0.5,  "recursos": ""},
    {"id": 40, "nombre": "Desbloqueo",                                                                          "inicio_plan": "32:15", "fin_plan": "32:30",   "duracion": 0.25, "recursos": "SMCV"},
]

def init_gantt_db():
    """Crea las tablas de gantt si no existen"""
    try:
        import psycopg2
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS gantt_cambio_hb (
                id SERIAL PRIMARY KEY,
                chancadora TEXT NOT NULL,
                fecha DATE NOT NULL,
                actividad_id INTEGER NOT NULL,
                inicio_real TEXT,
                fin_real TEXT,
                demora_minutos INTEGER DEFAULT 0,
                demora_motivo TEXT,
                completado BOOLEAN DEFAULT FALSE,
                fecha_registro TIMESTAMP DEFAULT NOW(),
                UNIQUE(chancadora, fecha, actividad_id)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS gantt_armado_hb (
                id SERIAL PRIMARY KEY,
                linea TEXT NOT NULL,
                fecha DATE NOT NULL,
                actividad_id INTEGER NOT NULL,
                inicio_real TEXT,
                fin_real TEXT,
                demora_minutos INTEGER DEFAULT 0,
                demora_motivo TEXT,
                completado BOOLEAN DEFAULT FALSE,
                fecha_registro TIMESTAMP DEFAULT NOW(),
                UNIQUE(linea, fecha, actividad_id)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS gantt_escaneo_hb (
                id SERIAL PRIMARY KEY,
                chancadora TEXT NOT NULL,
                fecha DATE NOT NULL,
                actividad_id INTEGER NOT NULL,
                inicio_real TEXT,
                fin_real TEXT,
                demora_minutos INTEGER DEFAULT 0,
                demora_motivo TEXT,
                completado BOOLEAN DEFAULT FALSE,
                fecha_registro TIMESTAMP DEFAULT NOW(),
                UNIQUE(chancadora, fecha, actividad_id)
            )
        ''')
        conn.commit()
        conn.close()
        print('✅ Tablas gantt listas')
    except Exception as e:
        print(f'❌ Error init_gantt_db: {e}')

with app.app_context():
    init_gantt_db()

@app.route('/gantt')
def gantt():
    tipo = request.args.get('tipo', 'cambio')
    chancadora = request.args.get('chancadora', '')
    linea = request.args.get('linea', '')
    fecha = request.args.get('fecha', '')
    avance = {}

    if fecha and (chancadora or linea):
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            conn = psycopg2.connect(os.environ.get('DATABASE_URL'), cursor_factory=RealDictCursor)
            c = conn.cursor()
            if tipo == 'armado':
                c.execute('SELECT * FROM gantt_armado_hb WHERE linea = %s AND fecha = %s', (linea, fecha))
            elif tipo == 'escaneo':
                c.execute('SELECT * FROM gantt_escaneo_hb WHERE chancadora = %s AND fecha = %s', (chancadora, fecha))
            else:
                c.execute('SELECT * FROM gantt_cambio_hb WHERE chancadora = %s AND fecha = %s', (chancadora, fecha))
            rows = c.fetchall()
            conn.close()
            avance = {int(r['actividad_id']): dict(r) for r in rows}
        except Exception as e:
            print(f'Error cargando gantt: {e}')

    actividades = ACTIVIDADES_ESCANEO if tipo == 'escaneo' else (ACTIVIDADES_ARMADO if tipo == 'armado' else ACTIVIDADES_GANTT)
    chancadoras = ['CR011','CR012','CR013','CR014','CR021','CR022','CR023','CR024']
    return render_template('gantt.html',
        tipo=tipo, chancadora=chancadora, linea=linea,
        fecha=fecha, actividades=actividades, avance=avance,
        chancadoras=chancadoras)
    
@app.route('/gantt/guardar', methods=['POST'])
def gantt_guardar():
    data = request.get_json()
    tipo = data.get('tipo', 'cambio')
    chancadora = data.get('chancadora')
    linea = data.get('linea')
    fecha = data.get('fecha')
    actividad_id = data.get('actividad_id')
    inicio_real = data.get('inicio_real') or None
    fin_real = data.get('fin_real') or None
    demora_minutos = int(data.get('demora_minutos') or 0)
    demora_motivo = data.get('demora_motivo') or None
    completado = bool(data.get('completado', False))
    if not (fecha and actividad_id):
        return {'error': 'Datos incompletos'}, 400
    try:
        import psycopg2
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        c = conn.cursor()
        if tipo == 'armado':
            c.execute('''
                INSERT INTO gantt_armado_hb
                    (linea, fecha, actividad_id, inicio_real, fin_real,
                     demora_minutos, demora_motivo, completado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (linea, fecha, actividad_id)
                DO UPDATE SET inicio_real=EXCLUDED.inicio_real,
                    fin_real=EXCLUDED.fin_real,
                    demora_minutos=EXCLUDED.demora_minutos,
                    demora_motivo=EXCLUDED.demora_motivo,
                    completado=EXCLUDED.completado,
                    fecha_registro=NOW()
            ''', (linea, fecha, actividad_id, inicio_real, fin_real,
                  demora_minutos, demora_motivo, completado))
        elif tipo == 'escaneo':
            c.execute('''
                INSERT INTO gantt_escaneo_hb
                    (chancadora, fecha, actividad_id, inicio_real, fin_real,
                     demora_minutos, demora_motivo, completado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (chancadora, fecha, actividad_id)
                DO UPDATE SET inicio_real=EXCLUDED.inicio_real,
                    fin_real=EXCLUDED.fin_real,
                    demora_minutos=EXCLUDED.demora_minutos,
                    demora_motivo=EXCLUDED.demora_motivo,
                    completado=EXCLUDED.completado,
                    fecha_registro=NOW()
            ''', (chancadora, fecha, actividad_id, inicio_real, fin_real,
                  demora_minutos, demora_motivo, completado))
        else:
            c.execute('''
                INSERT INTO gantt_cambio_hb
                    (chancadora, fecha, actividad_id, inicio_real, fin_real,
                     demora_minutos, demora_motivo, completado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (chancadora, fecha, actividad_id)
                DO UPDATE SET inicio_real=EXCLUDED.inicio_real,
                    fin_real=EXCLUDED.fin_real,
                    demora_minutos=EXCLUDED.demora_minutos,
                    demora_motivo=EXCLUDED.demora_motivo,
                    completado=EXCLUDED.completado,
                    fecha_registro=NOW()
            ''', (chancadora, fecha, actividad_id, inicio_real, fin_real,
                  demora_minutos, demora_motivo, completado))
        conn.commit()
        conn.close()
        return {'ok': True}
    except Exception as e:
        print(f'Error guardando gantt: {e}')
        return {'error': str(e)}, 500

# ══════════════════════════════════════════════════════════════
# MÓDULO RESUMEN SEMANAL — pegar en app.py antes de if __name__
# ══════════════════════════════════════════════════════════════

def init_resumen_db():
    """Crea tabla para Head/Bowl armados y sus observaciones editables"""
    try:
        import psycopg2
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS resumen_semanal (
                id SERIAL PRIMARY KEY,
                semana TEXT NOT NULL,
                linea TEXT NOT NULL,
                head TEXT,
                bowl TEXT,
                observaciones TEXT,
                fecha_registro TIMESTAMP DEFAULT NOW(),
                UNIQUE(semana, linea)
            )
        ''')
        conn.commit()
        conn.close()
        print('✅ Tabla resumen_semanal lista')
    except Exception as e:
        print(f'❌ Error init_resumen_db: {e}')

with app.app_context():
    init_resumen_db()


@app.route('/resumen')
def resumen_semanal():
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from datetime import datetime, timedelta

    # Semana seleccionada (default: semana actual)
    semana = request.args.get('semana', '')
    if not semana:
        hoy = datetime.now()
        semana = f"{hoy.year}-W{hoy.isocalendar()[1]:02d}"

    chancadoras = ['CR011', 'CR012', 'CR013', 'CR014', 'CR021', 'CR022', 'CR023', 'CR024']

    try:
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'), cursor_factory=RealDictCursor)
        c = conn.cursor()

        # Último protocolo de cambio por chancadora
        datos_chancadoras = {}
        for ch in chancadoras:
            c.execute('''
                SELECT chancadora, fecha_inicio, head_entrante, bowl_entrante,
                       recomendaciones, supervisor_metso
                FROM cambio_hb
                WHERE chancadora = %s
                ORDER BY fecha_inicio DESC
                LIMIT 1
            ''', (ch,))
            row = c.fetchone()
            datos_chancadoras[ch] = dict(row) if row else {
                'chancadora': ch,
                'fecha_inicio': None,
                'head_entrante': '-',
                'bowl_entrante': '-',
                'recomendaciones': '',
                'supervisor_metso': ''
            }

        # Head/Bowl armados (Línea 1 y 2) — editables por semana
        c.execute('''
            SELECT linea, head, bowl, observaciones
            FROM resumen_semanal
            WHERE semana = %s
        ''', (semana,))
        lineas_rows = c.fetchall()
        lineas = {r['linea']: dict(r) for r in lineas_rows}
        conn.close()

    except Exception as e:
        print(f'Error resumen: {e}')
        datos_chancadoras = {ch: {'chancadora': ch, 'head_entrante': '-', 'bowl_entrante': '-', 'recomendaciones': '', 'fecha_inicio': None} for ch in chancadoras}
        lineas = {}

    return render_template('resumen.html',
                           semana=semana,
                           chancadoras=chancadoras,
                           datos=datos_chancadoras,
                           lineas=lineas)


@app.route('/resumen/guardar', methods=['POST'])
def resumen_guardar():
    import psycopg2
    data = request.get_json()
    semana = data.get('semana')
    linea = data.get('linea')
    head = data.get('head') or None
    bowl = data.get('bowl') or None
    observaciones = data.get('observaciones') or None

    if not (semana and linea):
        return {'error': 'Datos incompletos'}, 400

    try:
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        c = conn.cursor()
        c.execute('''
            INSERT INTO resumen_semanal (semana, linea, head, bowl, observaciones)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (semana, linea)
            DO UPDATE SET head=EXCLUDED.head, bowl=EXCLUDED.bowl,
                observaciones=EXCLUDED.observaciones,
                fecha_registro=NOW()
        ''', (semana, linea, head, bowl, observaciones))
        conn.commit()
        conn.close()
        return {'ok': True}
    except Exception as e:
        print(f'Error guardando resumen: {e}')
        return {'error': str(e)}, 500

# ══════════════════════════════════════════════════════════════
# MÓDULO PPT GERENCIAL — pegar en app.py antes de if __name__
# ══════════════════════════════════════════════════════════════

@app.route('/informe/ppt')
def generar_ppt():
    """Genera PPT gerencial estilo Metso con estado de las 8 chancadoras"""
    import psycopg2
    from psycopg2.extras import RealDictCursor
    import subprocess, json, tempfile, os, io
    from datetime import datetime

    chancadoras = ['CR011','CR012','CR013','CR014','CR021','CR022','CR023','CR024']

    try:
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'), cursor_factory=RealDictCursor)
        c = conn.cursor()

        datos_ch = {}
        for ch in chancadoras:
            # Último registro
            c.execute('''SELECT * FROM cambio_hb WHERE chancadora = %s
                         ORDER BY fecha_inicio DESC LIMIT 1''', (ch,))
            ultimo = c.fetchone()

            # Historial para gráficos
            c.execute('''SELECT fecha_inicio,
                         socket_b1, socket_a1, socket_b2, socket_a2,
                         socket_b3, socket_a3, socket_b4, socket_a4,
                         socket_b5, socket_a5, socket_b6, socket_a6,
                         sl_gap_interior, sl_gap_exterior,
                         socket_gap_0, socket_gap_90, socket_gap_180, socket_gap_270,
                         mfl_med_a, mfl_med_b, mfl_med_c, mfl_med_d,
                         mfl_med_e, mfl_med_f, mfl_med_g,
                         sl_cambio_ahora, socket_cambio_ahora, mfl_cambio_ahora, montura_cambio_ahora,
                         head_entrante, bowl_entrante, altura_final_bowl
                         FROM cambio_hb WHERE chancadora = %s
                         ORDER BY fecha_inicio ASC''', (ch,))
            historial = c.fetchall()

            # Alturas de bowl para proyección
            c.execute('''SELECT fecha, altura, dias_parada FROM altura_bowl
                         WHERE chancadora = %s AND (ciclo_cerrado = FALSE OR ciclo_cerrado IS NULL)
                         ORDER BY fecha ASC''', (ch,))
            alturas = c.fetchall()

            # Último cambio por componente
            c.execute('''SELECT fecha_inicio, sl_cambio_ahora, socket_cambio_ahora,
                         mfl_cambio_ahora, montura_cambio_ahora
                         FROM cambio_hb WHERE chancadora = %s
                         AND (sl_cambio_ahora = 'SI' OR socket_cambio_ahora = 'SI'
                              OR mfl_cambio_ahora = 'SI' OR montura_cambio_ahora = 'SI')
                         ORDER BY fecha_inicio DESC LIMIT 10''', (ch,))
            cambios = c.fetchall()

            datos_ch[ch] = {
                'ultimo': dict(ultimo) if ultimo else None,
                'historial': [dict(r) for r in historial],
                'alturas': [dict(r) for r in alturas],
                'cambios': [dict(r) for r in cambios],
                'total': len(historial)
            }

        conn.close()
    except Exception as e:
        return f'Error BD: {e}', 500

    # Semana actual
    semana = f"W{datetime.now().isocalendar()[1]:02d} · {datetime.now().strftime('%B %Y')}"

    # Preparar datos para Node.js
    payload = {
        'chancadoras': chancadoras,
        'datos': datos_ch,
        'semana': semana,
        'fecha': datetime.now().strftime('%d/%m/%Y')
    }

    # Llamar al script Node.js
    # Instalar pptxgenjs si no está
    node_modules = os.path.join(os.path.dirname(__file__), 'node_modules', 'pptxgenjs')
    if not os.path.exists(node_modules):
        subprocess.run(['npm', 'install', 'pptxgenjs'], 
                   cwd=os.path.dirname(__file__), capture_output=True)
    script_path = os.path.join(os.path.dirname(__file__), 'generar_ppt_metso.js')
    env = os.environ.copy()
    env['NODE_PATH'] = '/opt/render/project/src/node_modules'
    result = subprocess.run(
        ['node', script_path],
        env=env,
        input=json.dumps(payload, ensure_ascii=False, default=str).encode('utf-8'),
        capture_output=True, timeout=60
    )

    if result.returncode != 0:
        return f'Error generando PPT: {result.stderr.decode()}', 500

    import base64
    pptx_bytes = base64.b64decode(result.stdout.decode().strip())
    buf = io.BytesIO(pptx_bytes)
    buf.seek(0)
    nombre = f'Metso_Estado_Chancadoras_{datetime.now().strftime("%Y%m%d")}.pptx'
    return send_file(buf, as_attachment=True, download_name=nombre,
                     mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation')

# ══════════════════════════════════════════════════════════════
# MÓDULO PLAN DE MANTENIMIENTO — pegar en app.py antes de if __name__
# ══════════════════════════════════════════════════════════════

@app.route('/plan')
def plan_mantenimiento():
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from datetime import datetime

    chancadoras = ['CR011','CR012','CR013','CR014','CR021','CR022','CR023','CR024']

    try:
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'), cursor_factory=RealDictCursor)
        c = conn.cursor()

        plan = {}
        for ch in chancadoras:
            c.execute('''
                SELECT id, fecha_inicio, fecha_registro,
                       sl_cambio_ahora, socket_cambio_ahora, mfl_cambio_ahora, montura_cambio_ahora,
                       sl_gap_interior, sl_gap_exterior,
                       socket_b1, socket_a1, socket_b2, socket_a2,
                       socket_b3, socket_a3, socket_b4, socket_a4,
                       socket_b5, socket_a5, socket_b6, socket_a6,
                       socket_med_a, socket_med_b, socket_med_c, socket_med_d,
                       socket_gap_0, socket_gap_90, socket_gap_180, socket_gap_270,
                       mfl_med_a, mfl_med_b, mfl_med_c, mfl_med_d,
                       mfl_med_e, mfl_med_f, mfl_med_g, mfl_cambio_ahora,
                       montura_barras_estado, montura_chocky_estado,
                       prot_estatico_estado, prot_dinamico_estado,
                       gp1_medida, gp2_medida, gp3_medida, gp4_medida, gp5_medida, gp6_medida, gp1_cambio,
                       recomendaciones, supervisor_metso,
                       head_entrante, bowl_entrante, altura_final_bowl
                FROM cambio_hb WHERE chancadora = %s
                ORDER BY fecha_inicio DESC
            ''', (ch,))
            historial = c.fetchall()

            if not historial:
                plan[ch] = {'sin_datos': True, 'total': 0}
                continue

            ultimo = dict(historial[0])
            total = len(historial)

            # ── Socket Liner: medir cada 3 intervenciones ──
            sl_ultima_medicion = None
            for idx, h in enumerate(historial):
                vals = [dict(h).get(f'socket_med_{x}') for x in ['a','b','c','d']]
                if any(v is not None for v in vals):
                    sl_ultima_medicion = idx
                    break

            if sl_ultima_medicion is None:
                sl_proxima = 'medir'
                sl_desde = None
            else:
                sl_proxima = 'medir' if sl_ultima_medicion >= 2 else 'omitir'
                sl_desde = sl_ultima_medicion

            sl_vals = [ultimo.get(f'socket_med_{x}') for x in ['a','b','c','d']]
            sl_nums = [float(v) for v in sl_vals if v is not None]
            sl_promedio = round(sum(sl_nums)/len(sl_nums), 2) if sl_nums else None

            # Fechas de último cambio MFL (históricas + BD)
            MFL_FECHA_BASE = {
                'CR011': '2025-08-01',
                'CR012': '2025-12-08',
                'CR013': '2025-12-10',
                'CR014': '2026-04-21',
                'CR021': '2026-01-08',
                'CR022': '2025-09-01',
                'CR023': '2025-09-11',
                'CR024': '2026-02-25',
            }

            # ── MFL: lógica por tipo de chancadora ──
            MFL_TIPO = {
                'CR011': {'tipo': 'Metso Full Solution', 'cada': 4, 'desde_siempre': 20},
                'CR012': {'tipo': 'Yahle',               'cada': 4, 'desde_siempre': 20},
                'CR013': {'tipo': 'Yahle',               'cada': 4, 'desde_siempre': 20},
                'CR014': {'tipo': 'Metálico',            'cada': 2, 'desde_siempre': None},
                'CR021': {'tipo': 'Metálico',            'cada': 2, 'desde_siempre': None},
                'CR022': {'tipo': 'Yahle Mejorado',      'cada': 4, 'desde_siempre': 20},
                'CR023': {'tipo': 'Yahle Mejorado',      'cada': 4, 'desde_siempre': 20},
                'CR024': {'tipo': 'Metálico',            'cada': 2, 'desde_siempre': None},
            }
            cfg = MFL_TIPO.get(ch, {'tipo': 'Desconocido', 'cada': 2, 'desde_siempre': None})

            interv_desde_nuevo = 0
            for h in historial:
                if dict(h).get('mfl_cambio_ahora') == 'SI':
                    break
                interv_desde_nuevo += 1

            cada = cfg['cada']
            desde_siempre = cfg['desde_siempre']

            if desde_siempre is not None and interv_desde_nuevo >= desde_siempre:
                mfl_proxima = 'medir'
                mfl_restriccion = f'{cfg["tipo"]} · intervención {interv_desde_nuevo} → siempre medir'
            elif interv_desde_nuevo % cada == 0:
                mfl_proxima = 'medir'
                mfl_restriccion = f'{cfg["tipo"]} · intervención {interv_desde_nuevo} → toca medir (cada {cada})'
            else:
                proxima_medicion = cada - (interv_desde_nuevo % cada)
                mfl_proxima = 'omitir'
                mfl_restriccion = f'{cfg["tipo"]} · próxima medición en {proxima_medicion} intervención{"es" if proxima_medicion > 1 else ""}'

            mfl_nuevo_fecha = None
            meses_mfl_nuevo = None
            # Primero buscar en BD
            for h in historial:
                if dict(h).get('mfl_cambio_ahora') == 'SI' and h.get('fecha_inicio'):
                    fecha_cambio = h['fecha_inicio']
                    if not hasattr(fecha_cambio, 'year'):
                        from datetime import date
                        fecha_cambio = date.fromisoformat(str(fecha_cambio)[:10])
                    hoy = datetime.now().date()
                    meses_mfl_nuevo = (hoy.year - fecha_cambio.year)*12 + (hoy.month - fecha_cambio.month)
                    mfl_nuevo_fecha = str(fecha_cambio)
                    break
            # Si no hay en BD, usar fecha histórica
            if mfl_nuevo_fecha is None and ch in MFL_FECHA_BASE:
                from datetime import date
                fecha_cambio = date.fromisoformat(MFL_FECHA_BASE[ch])
                hoy = datetime.now().date()
                meses_mfl_nuevo = (hoy.year - fecha_cambio.year)*12 + (hoy.month - fecha_cambio.month)
                mfl_nuevo_fecha = str(fecha_cambio) + ' (histórico)'

            # Promedio MFL último
            mfl_vals = [ultimo.get(f'mfl_med_{x}') for x in ['a','b','c','d','e','f','g']]
            mfl_nums = [float(v) for v in mfl_vals if v is not None]
            mfl_promedio = round(sum(mfl_nums)/len(mfl_nums), 2) if mfl_nums else None

            # GAP Socket último promedio
            gap_vals = [ultimo.get('socket_gap_0'), ultimo.get('socket_gap_90'),
                        ultimo.get('socket_gap_180'), ultimo.get('socket_gap_270')]
            gap_nums = [float(v) for v in gap_vals if v is not None]
            gap_promedio = round(sum(gap_nums)/len(gap_nums), 2) if gap_nums else None

            plan[ch] = {
                'sin_datos': False,
                'total': total,
                'fecha_ultimo': str(ultimo.get('fecha_inicio',''))[:10],
                'supervisor': ultimo.get('supervisor_metso',''),
                'head': ultimo.get('head_entrante',''),
                'bowl': ultimo.get('bowl_entrante',''),
                'altura': ultimo.get('altura_final_bowl',''),
                'recomendaciones': ultimo.get('recomendaciones',''),
                # Socket Liner
                'sl_proxima': sl_proxima,
                'sl_desde': sl_desde,
                'sl_promedio': sl_promedio,
                'sl_gap_interior': ultimo.get('sl_gap_interior'),
                'sl_gap_exterior': ultimo.get('sl_gap_exterior'),
                # Socket GAP
                'gap_promedio': gap_promedio,
                # MFL
                'mfl_proxima': mfl_proxima,
                'mfl_restriccion': mfl_restriccion,
                'mfl_tipo': cfg['tipo'],
                'mfl_promedio': mfl_promedio,
                'interv_desde_nuevo': interv_desde_nuevo,
                'meses_mfl_nuevo': meses_mfl_nuevo,
                'mfl_nuevo_fecha': mfl_nuevo_fecha,
                # Estado componentes
                'montura_estado': ultimo.get('montura_barras_estado',''),
                'prot_estatico': ultimo.get('prot_estatico_estado',''),
                'prot_dinamico': ultimo.get('prot_dinamico_estado',''),
                **{f'gp{i}_medida': ultimo.get(f'gp{i}_medida') for i in range(1,7)},
            }

        conn.close()
    except Exception as e:
        print(f'Error plan mantenimiento: {e}')
        plan = {ch: {'sin_datos': True, 'total': 0} for ch in chancadoras}

    return render_template('plan.html', chancadoras=chancadoras, plan=plan)

@app.route('/planificacion')
def planificacion():
    import psycopg2
    from datetime import datetime, timedelta
    
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    c = conn.cursor()
    
    chancadoras = ['CR011','CR012','CR013','CR014','CR021','CR022','CR023','CR024']
    L1 = ['CR011','CR012','CR013','CR014']
    L2 = ['CR021','CR022','CR023','CR024']
    datos_plan = {}
    hoy = datetime.now()
    fin = hoy + timedelta(days=150)
    
    for ch in chancadoras:
        c.execute('''SELECT fecha_inicio FROM cambio_hb 
                     WHERE chancadora = %s AND fecha_inicio IS NOT NULL
                     ORDER BY fecha_inicio ASC''', (ch,))
        fechas = [r[0] for r in c.fetchall()]
        
        ultimo_cambio = None
        duracion_promedio = None
        fechas_cambio_proyectadas = []
        
        if len(fechas) >= 2:
            duraciones = []
            for i in range(1, len(fechas)):
                d1 = datetime.combine(fechas[i-1], datetime.min.time()) if hasattr(fechas[i-1], 'year') else datetime.strptime(str(fechas[i-1]), '%Y-%m-%d')
                d2 = datetime.combine(fechas[i], datetime.min.time()) if hasattr(fechas[i], 'year') else datetime.strptime(str(fechas[i]), '%Y-%m-%d')
                duraciones.append((d2 - d1).days)
            duracion_promedio = round(sum(duraciones) / len(duraciones))
            ultimo_cambio = fechas[-1]
            ul = datetime.combine(ultimo_cambio, datetime.min.time()) if hasattr(ultimo_cambio, 'year') else datetime.strptime(str(ultimo_cambio), '%Y-%m-%d')
            proxima = ul + timedelta(days=duracion_promedio)
            while proxima <= fin:
                if proxima >= hoy:
                    fechas_cambio_proyectadas.append(proxima.strftime('%Y-%m-%d'))
                proxima += timedelta(days=duracion_promedio)
        elif len(fechas) == 1:
            ultimo_cambio = fechas[-1]

        datos_plan[ch] = {
            'ultimo_cambio': str(ultimo_cambio) if ultimo_cambio else '-',
            'duracion_promedio': duracion_promedio,
            'fechas_cambio': fechas_cambio_proyectadas,
        }
    
    conn.close()
    # Correcciones manuales de próxima fecha
    correcciones = {
        'CR021': '2026-07-01',
        'CR024': '2026-07-06',
    }
    for ch, fecha_corr in correcciones.items():
        if ch in datos_plan and datos_plan[ch]['fechas_cambio']:
            datos_plan[ch]['fechas_cambio'][0] = fecha_corr
        elif ch in datos_plan:
            datos_plan[ch]['fechas_cambio'] = [fecha_corr]
    
    # Agrupar por DÍA
    dias = {}
    for ch, d in datos_plan.items():
        for fecha_str in d['fechas_cambio']:
            if fecha_str not in dias:
                dias[fecha_str] = {'cambios': []}
            dias[fecha_str]['cambios'].append(ch)

    # Calcular armados_lineas por día
    for fecha_str, data in dias.items():
        tiene_l1 = any(ch in L1 for ch in data['cambios'])
        tiene_l2 = any(ch in L2 for ch in data['cambios'])
        data['armados_lineas'] = []
        if tiene_l1: data['armados_lineas'].append('L1')
        if tiene_l2: data['armados_lineas'].append('L2')

    # Agrupar por SEMANA
    semanas = {}
    for fecha_str, data in dias.items():
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
        semana = fecha.strftime('%Y-W%W')
        if semana not in semanas:
            semanas[semana] = {'cambios': [], 'dias': {}}
        for ch in data['cambios']:
            if ch not in semanas[semana]['cambios']:
                semanas[semana]['cambios'].append(ch)
        if fecha_str not in semanas[semana]['dias']:
            semanas[semana]['dias'][fecha_str] = {'cambios': [], 'armados_lineas': []}
        semanas[semana]['dias'][fecha_str]['cambios'] += data['cambios']
        semanas[semana]['dias'][fecha_str]['armados_lineas'] = data['armados_lineas']

    # Personal por semana
    for semana, data in semanas.items():
        n_c = len(data['cambios'])
        tiene_l1 = any(ch in L1 for ch in data['cambios'])
        tiene_l2 = any(ch in L2 for ch in data['cambios'])
        n_a = (1 if tiene_l1 else 0) + (1 if tiene_l2 else 0)
        data['armados_lineas'] = []
        if tiene_l1: data['armados_lineas'].append('L1')
        if tiene_l2: data['armados_lineas'].append('L2')
        data['personal_cambio'] = n_c * 12
        data['personal_armado'] = n_a * 9
        data['personal_total'] = data['personal_cambio'] + data['personal_armado']
        data['detalle_cambio'] = f"{n_c*3} soldadores, {n_c} riggers, {n_c} op. grúa, {n_c*7} mecánicos" if n_c else '-'
        data['detalle_armado'] = f"{n_a*2} soldadores, {n_a} op. grúa, {n_a} riggers, {n_a*5} mecánicos" if n_a else '-'

    semanas_sorted = dict(sorted(semanas.items()))
    dias_sorted = dict(sorted(dias.items()))

    return render_template('planificacion.html',
                           datos_plan=datos_plan,
                           chancadoras=chancadoras,
                           semanas=semanas_sorted,
                           dias=dias_sorted,
                           hoy=hoy.strftime('%Y-%m-%d'))

# ══════════════════════════════════════════════════════════════
# MÓDULO ASISTENCIA
# ══════════════════════════════════════════════════════════════

def init_asistencia_db():
    try:
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS personal (
                id SERIAL PRIMARY KEY,
                um TEXT DEFAULT 'SMCV',
                dni TEXT UNIQUE NOT NULL,
                nombres TEXT NOT NULL,
                perfil TEXT,
                dia_cero TEXT,
                gerencia TEXT,
                tipo_contrato TEXT,
                activo BOOLEAN DEFAULT TRUE
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS asistencia (
                id SERIAL PRIMARY KEY,
                dni TEXT NOT NULL,
                fecha DATE NOT NULL,
                turno TEXT DEFAULT 'DIA',
                hora_ingreso TIMESTAMP,
                hora_salida TIMESTAMP,
                horas_trabajadas REAL,
                horas_extras REAL,
                fecha_registro TIMESTAMP DEFAULT NOW()
            )
        ''')
        conn.commit()
        conn.close()
        print('✅ Tablas asistencia listas')
    except Exception as e:
        print(f'❌ Error init_asistencia_db: {e}')

with app.app_context():
    init_asistencia_db()

@app.route('/asistencia')
def asistencia():
    return render_template('asistencia.html')

@app.route('/asistencia/buscar')
def asistencia_buscar():
    import psycopg2
    dni = request.args.get('dni','').strip()
    if not dni:
        return {'error': 'DNI requerido'}, 400
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    c = conn.cursor()
    c.execute('SELECT dni, nombres, perfil, gerencia, tipo_contrato FROM personal WHERE dni = %s AND activo = TRUE', (dni,))
    p = c.fetchone()
    conn.close()
    if not p:
        return {'error': 'Personal no encontrado'}, 404
    return {'dni': p[0], 'nombres': p[1], 'perfil': p[2], 'gerencia': p[3], 'tipo_contrato': p[4]}

@app.route('/asistencia/registrar', methods=['POST'])
def asistencia_registrar():
    import psycopg2
    from datetime import datetime
    data = request.get_json()
    dni = data.get('dni')
    tipo = data.get('tipo')  # 'ingreso' o 'salida'
    turno = data.get('turno', 'DIA')
    from datetime import timezone, timedelta
    peru_tz = timezone(timedelta(hours=-5))
    ahora = datetime.now(peru_tz).replace(tzinfo=None)
    fecha = ahora.date()
    if turno == 'NOCHE' and tipo == 'salida':
        from datetime import timedelta
        fecha = (ahora - timedelta(days=1)).date()
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    c = conn.cursor()
    if tipo == 'ingreso':
        c.execute('''INSERT INTO asistencia (dni, fecha, turno, hora_ingreso)
                     VALUES (%s, %s, %s, %s)
                     ON CONFLICT DO NOTHING''', (dni, fecha, turno, ahora))
    else:
        c.execute('''SELECT id, hora_ingreso FROM asistencia 
                     WHERE dni = %s AND fecha = %s AND turno = %s AND hora_salida IS NULL
                     ORDER BY hora_ingreso DESC LIMIT 1''', (dni, fecha, turno))
        reg = c.fetchone()
        if reg:
            horas = (ahora - reg[1]).total_seconds() / 3600
            extras = max(0, horas - 9.58)
            c.execute('''UPDATE asistencia SET hora_salida = %s, horas_trabajadas = %s, horas_extras = %s
                         WHERE id = %s''', (ahora, round(horas,2), round(extras,2), reg[0]))
    conn.commit()
    conn.close()
    return {'ok': True, 'hora': ahora.strftime('%H:%M:%S')}

@app.route('/asistencia/reporte')
def asistencia_reporte():
    import psycopg2
    fecha_desde = request.args.get('desde', '')
    fecha_hasta = request.args.get('hasta', '')
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    c = conn.cursor()
    query = '''SELECT a.dni, p.nombres, p.perfil, p.gerencia, a.fecha, a.turno,
                      a.hora_ingreso, a.hora_salida, a.horas_trabajadas, a.horas_extras
               FROM asistencia a
               LEFT JOIN personal p ON a.dni = p.dni
               WHERE 1=1'''
    params = []
    if fecha_desde:
        query += ' AND a.fecha >= %s'
        params.append(fecha_desde)
    if fecha_hasta:
        query += ' AND a.fecha <= %s'
        params.append(fecha_hasta)
    query += ' ORDER BY a.fecha DESC, p.nombres ASC'
    c.execute(query, params)
    registros = c.fetchall()
    conn.close()
    return render_template('asistencia_reporte.html', registros=registros, desde=fecha_desde, hasta=fecha_hasta)

@app.route('/asistencia/exportar')
def asistencia_exportar():
    import psycopg2
    import io
    fecha_desde = request.args.get('desde', '')
    fecha_hasta = request.args.get('hasta', '')
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    c = conn.cursor()
    query = '''SELECT a.dni, p.nombres, p.perfil, p.gerencia, p.tipo_contrato,
                      a.fecha, a.turno, a.hora_ingreso, a.hora_salida, 
                      a.horas_trabajadas, a.horas_extras
               FROM asistencia a
               LEFT JOIN personal p ON a.dni = p.dni
               WHERE 1=1'''
    params = []
    if fecha_desde:
        query += ' AND a.fecha >= %s'
        params.append(fecha_desde)
    if fecha_hasta:
        query += ' AND a.fecha <= %s'
        params.append(fecha_hasta)
    query += ' ORDER BY a.fecha DESC, p.nombres ASC'
    c.execute(query, params)
    registros = c.fetchall()
    conn.close()
    output = io.StringIO()
    output.write('DNI,NOMBRES,PERFIL,GERENCIA,TIPO CONTRATO,FECHA,TURNO,HORA INGRESO,HORA SALIDA,HORAS TRABAJADAS,HORAS EXTRAS\n')
    for r in registros:
        output.write(f'{r[0]},{r[1]},{r[2]},{r[3]},{r[4]},{r[5]},{r[6]},{str(r[7])[:16] if r[7] else ""},{str(r[8])[:16] if r[8] else ""},{r[9] or ""},{r[10] or ""}\n')
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'asistencia_{fecha_desde}_{fecha_hasta}.csv'
    )

@app.route('/asistencia/admin', methods=['GET','POST'])
def asistencia_admin():
    import psycopg2
    admin_pass = os.environ.get('ADMIN_PASSWORD','admin123')
    if request.method == 'POST':
        accion = request.form.get('accion')
        clave = request.form.get('clave','')
        if clave != admin_pass:
            return render_template('asistencia_admin.html', error='Clave incorrecta', personal=[])
        if accion == 'agregar':
            dni = request.form.get('dni')
            nombres = request.form.get('nombres')
            perfil = request.form.get('perfil')
            gerencia = request.form.get('gerencia')
            tipo_contrato = request.form.get('tipo_contrato')
            conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
            c = conn.cursor()
            c.execute('INSERT INTO personal (dni, nombres, perfil, gerencia, tipo_contrato) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (dni) DO NOTHING',
                      (dni, nombres, perfil, gerencia, tipo_contrato))
            conn.commit()
            conn.close()
        elif accion == 'eliminar':
            dni = request.form.get('dni')
            conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
            c = conn.cursor()
            c.execute('UPDATE personal SET activo = FALSE WHERE dni = %s', (dni,))
            conn.commit()
            conn.close()
        elif accion == 'editar':
            dni = request.form.get('dni')
            nombres = request.form.get('nombres')
            perfil = request.form.get('perfil')
            gerencia = request.form.get('gerencia')
            tipo_contrato = request.form.get('tipo_contrato')
            conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
            c = conn.cursor()
            c.execute('UPDATE personal SET nombres=%s, perfil=%s, gerencia=%s, tipo_contrato=%s WHERE dni=%s',
                      (nombres, perfil, gerencia, tipo_contrato, dni))
            conn.commit()
            conn.close()
    clave_ok = request.args.get('clave') == admin_pass or request.form.get('clave') == admin_pass
    personal = []
    if clave_ok or request.method == 'GET':
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        c = conn.cursor()
        c.execute('SELECT dni, nombres, perfil, gerencia, tipo_contrato FROM personal WHERE activo = TRUE ORDER BY nombres')
        personal = c.fetchall()
        conn.close()
    return render_template('asistencia_admin.html', personal=personal, clave_ok=clave_ok, error=None)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)