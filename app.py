from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
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
def home():
    return render_template('home.html')

#Chinalco comienzo

@app.route('/chinalco')
def Chinalco():
    return render_template('chinalco.html')

@app.route('/chinalco_checklist')
def Chinalco_checklist():
    return render_template('chinalco_checklist.html')

#Chinalco fin 

@app.route('/mantenimiento')
def mantenimiento():
    return render_template('index.html')

@app.route('/armado')
def armado():
    return render_template('armado.html')

@app.route('/resumen')
def resumen():
    return render_template('resumen.html')

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
                resultado = cloudinary.uploader.upload(
                    foto,
                    folder='protocolos',
                    transformation=[{'width': 800, 'height': 600, 'crop': 'limit', 'quality': 60}]
                )
                fotos_paths[f'foto_path_{key.replace("foto_", "")}'] = resultado['secure_url']
            except Exception as e:
                print(f'Error subiendo foto {key}: {e}')

    guardar_armado(datos)
    datos_word = dict(datos)
    datos_word.update(fotos_paths)
    ruta_word = generar_word_armado(datos_word)

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
            print(f'Error correo: {e}')
    flash('✅ Protocolo guardado y enviado por correo!')
    return redirect(url_for('mantenimiento'))

@app.route('/cambio')
def cambio():
    return render_template('cambio.html')



@app.route('/cambio/guardar', methods=['POST'])
def guardar_cambio_route():
    datos = {}
    campos = ['fecha_inicio','fecha_termino','supervisor_cliente','supervisor_metso','cliente','chancadora',
        'head_saliente','bowl_saliente','altura_bowl_saliente','hora_inicio_h','hora_inicio_m','correo_destino',
        'anillo_roscas_estado','anillo_roscas_obs','anillo_ndt_obs','anillo_gap_peineta',
        'anillo_cilindros_estado','anillo_cilindros_obs','hidraulico_nivel_estado','hidraulico_nivel_obs',
        'gap_aro_v1','gap_aro_v2','gap_aro_v3','clamping_fugas_estado','clamping_fugas_obs',
        'sl_ranuras_estado','sl_ranuras_obs','socket_B1','socket_A1','socket_B2','socket_A2',
        'socket_B3','socket_A3','socket_B4','socket_A4','socket_B5','socket_A5','socket_B6','socket_A6',
        'socket_med_a','socket_med_b','socket_med_c','socket_med_d',
        'sl_asentamiento_estado','sl_asentamiento_obs','sl_gap_interior','sl_gap_exterior',
        'sl_fisuras_estado','sl_fisuras_obs','sl_deformaciones_estado','sl_deformaciones_obs',
        'sl_canales_estado','sl_canales_obs','sl_cambio_ahora','sl_cambio_siguiente',
        'sl_ret_precalentar','sl_ret_precalentar_obs','sl_ret_tornillos','sl_ret_tornillos_obs',
        'sl_mont_precalentar','sl_mont_precalentar_obs','sl_mont_tornillos','sl_mont_tornillos_obs',
        'sl_mont_enfriamiento','sl_mont_enfriamiento_obs','sl_mont_asentamiento','sl_mont_asentamiento_obs',
        'sl_mont_gap_interno','sl_mont_gap_externo','socket_fisuras_estado','socket_fisuras_obs',
        'socket_pernos_estado','socket_pernos_obs','socket_ranuras_estado','socket_ranuras_obs',
        'socket_deform_estado','socket_deform_obs','socket_canales_estado','socket_canales_obs',
        'socket_gap_0','socket_gap_90','socket_gap_180','socket_gap_270',
        'socket_cambio_ahora','socket_cambio_siguiente','sk_ret_calentar_obs',
        'sk_sal_A1','sk_sal_A2','sk_sal_A3','sk_sal_A4','sk_sal_B1','sk_sal_B2','sk_sal_B3','sk_sal_B4',
        'sk_sal_C1','sk_sal_C2','sk_sal_C3','sk_sal_C4','sk_sal_D1','sk_sal_D2','sk_sal_D3','sk_sal_D4',
        'sk_mont_calentar_obs','sk_mont_enfriar_obs','sk_mont_gap_obs',
        'sk_new_A1','sk_new_A2','sk_new_A3','sk_new_A4','sk_new_B1','sk_new_B2','sk_new_B3','sk_new_B4',
        'sk_new_C1','sk_new_C2','sk_new_C3','sk_new_C4','sk_new_D1','sk_new_D2','sk_new_D3','sk_new_D4',
        'mainshaft_obs','ms_A1','ms_A2','ms_A3','ms_A4','ms_B1','ms_B2','ms_B3','ms_B4',
        'ms_C1','ms_C2','ms_C3','ms_C4','ms_D1','ms_D2','ms_D3','ms_D4','ms_F1','ms_F2','ms_F3','ms_F4',
        'mfl_pernos_estado','mfl_pernos_obs','mfl_medida',
        'mfl_med_A','mfl_med_B','mfl_med_C','mfl_med_D','mfl_med_E','mfl_med_F','mfl_med_G','mfl_med_H',
        'mfl_cambio_ahora','mfl_cambio_siguiente','mfl_mont_pernos','mfl_mont_pernos_obs',
        'mfl_wearing_estado','mfl_wearing_obs',
        'mfl_new_A','mfl_new_B','mfl_new_C','mfl_new_D','mfl_new_E','mfl_new_F','mfl_new_G','mfl_new_H',
        'montura_barras_estado','montura_barras_obs','montura_acumulacion_estado','montura_acumulacion_obs',
        'montura_chocky_estado','montura_chocky_obs','montura_cambio_ahora','montura_cambio_siguiente',
        'montura_brazos_estado','montura_brazos_obs','montura_caja_estado','montura_caja_obs',
        'gp1_cambio','gp1_medida','gp1_obs','gp2_cambio','gp2_medida','gp2_obs',
        'gp3_cambio','gp3_medida','gp3_obs','gp4_cambio','gp4_medida','gp4_obs',
        'gp5_cambio','gp5_medida','gp5_obs','gp6_cambio','gp6_medida','gp6_obs',
        'gp1_medida_nueva','gp2_medida_nueva','gp3_medida_nueva',
        'gp4_medida_nueva','gp5_medida_nueva','gp6_medida_nueva',
        'prot_estatico_estado','prot_estatico_obs','prot_estatico_espesor',
        'prot_dinamico_estado','prot_dinamico_obs','prot_din_fuga','prot_din_fuga_obs','prot_dinamico_desgaste',
        'contrapeso_estado','contrapeso_obs','sello_ut_estado','sello_ut_obs','excentrica_cambio',
        'exc_prot_din_estado','exc_prot_din_obs','exc_pernos_prot_estado','exc_pernos_prot_obs',
        'exc_sellos_estado','exc_sellos_obs','exc_distancia_vertical',
        'exc_bocina_estado','exc_bocina_obs',
        'exc_metro_a1','exc_metro_b1','exc_metro_c1','exc_metro_d1',
        'exc_metro_a2','exc_metro_b2','exc_metro_c2','exc_metro_d2',
        'exc_metro_a3','exc_metro_b3','exc_metro_c3','exc_metro_d3',
        'exc_lower_tb_estado','exc_lower_tb_obs','exc_pernos_lower_estado','exc_pernos_lower_obs',
        'exc_upper_tb_estado','exc_upper_tb_obs','exc_pernos_upper_estado','exc_pernos_upper_obs',
        'exc_rampas_estado','exc_rampas_obs','exc_tornillos_estado','exc_tornillos_obs',
        'exc_backlash','exc_lainas','chute_faldon_estado','chute_faldon_obs',
        'chute_liners_estado','chute_liners_obs','chute_placa_estado','chute_placa_obs',
        'mainshaft_cambio',
        'ms_sal_alt_a1','ms_sal_alt_a1_ver','ms_sal_alt_a2','ms_sal_alt_a2_ver',
        'ms_sal_alt_a3','ms_sal_alt_a3_ver','ms_sal_alt_a4','ms_sal_alt_a4_ver',
        'ms_sal_gap_sup','ms_sal_gap_sup_ver','ms_sal_gap_inf','ms_sal_gap_inf_ver',
        'ms_carga_grua','ms_presion_bomba','ms_tipo_aceite','ms_ent_serie',
        'ms_ent_metro_a1_0','ms_ent_metro_a1_90','ms_ent_metro_a1_180','ms_ent_metro_a1_270','ms_ent_metro_a1_ver',
        'ms_ent_metro_a2_0','ms_ent_metro_a2_90','ms_ent_metro_a2_180','ms_ent_metro_a2_270','ms_ent_metro_a2_ver',
        'ms_ent_metro_a3_0','ms_ent_metro_a3_90','ms_ent_metro_a3_180','ms_ent_metro_a3_270','ms_ent_metro_a3_ver',
        'ms_ent_metro_a4_0','ms_ent_metro_a4_90','ms_ent_metro_a4_180','ms_ent_metro_a4_270','ms_ent_metro_a4_ver',
        'ms_ent_metro_a5_0','ms_ent_metro_a5_90','ms_ent_metro_a5_180','ms_ent_metro_a5_270','ms_ent_metro_a5_ver',
        'ms_ent_metro_b_0','ms_ent_metro_b_90','ms_ent_metro_b_180','ms_ent_metro_b_270','ms_ent_metro_b_ver',
        'ms_ent_metro_a6_0','ms_ent_metro_a6_90','ms_ent_metro_a6_180','ms_ent_metro_a6_270','ms_ent_metro_a6_ver',
        'ms_ent_metro_a7_0','ms_ent_metro_a7_90','ms_ent_metro_a7_180','ms_ent_metro_a7_270','ms_ent_metro_a7_ver',
        'ms_ent_metro_a8_0','ms_ent_metro_a8_90','ms_ent_metro_a8_180','ms_ent_metro_a8_270','ms_ent_metro_a8_ver',
        'ms_ent_metro_c_0','ms_ent_metro_c_90','ms_ent_metro_c_180','ms_ent_metro_c_270','ms_ent_metro_c_ver',
        'ms_ent_alt_a1','ms_ent_alt_a1_ver','ms_ent_alt_a2','ms_ent_alt_a2_ver',
        'ms_ent_alt_a3','ms_ent_alt_a3_ver','ms_ent_alt_a4','ms_ent_alt_a4_ver',
        'ms_ent_alt_g1','ms_ent_alt_g1_ver','ms_ent_alt_g2','ms_ent_alt_g2_ver',
        'ms_ent_alt_g3','ms_ent_alt_g3_ver','ms_ent_alt_g4','ms_ent_alt_g4_ver',
        'ms_ent_gap_sup','ms_ent_gap_sup_ver','ms_ent_gap_inf','ms_ent_gap_inf_ver',
        'ms_ent_shims','ms_ent_contacto','ms_termas_cant','ms_termas_cap',
        'ms_diam_b_ini','ms_diam_b_fin','ms_contraccion',
        'ms_post_alt_a1','ms_post_alt_a1_ver','ms_post_alt_a2','ms_post_alt_a2_ver',
        'ms_post_alt_a3','ms_post_alt_a3_ver','ms_post_alt_a4','ms_post_alt_a4_ver',
        'ms_post_alt_g1','ms_post_alt_g1_ver','ms_post_alt_g2','ms_post_alt_g2_ver',
        'ms_post_alt_g3','ms_post_alt_g3_ver','ms_post_alt_g4','ms_post_alt_g4_ver',
        'ms_post_gap_sup','ms_post_gap_sup_ver','ms_post_gap_inf','ms_post_gap_inf_ver',
        'ms_terma1_ini','ms_terma1_fin','ms_terma2_ini','ms_terma2_fin',
        'ms_terma3_ini','ms_terma3_fin','ms_terma4_ini','ms_terma4_fin',
        'ms_terma5_ini','ms_terma5_fin','ms_terma6_ini','ms_terma6_fin',
        'ms_terma7_ini','ms_terma7_fin','ms_terma8_ini','ms_terma8_fin',
        'ms_terma9_ini','ms_terma9_fin','ms_terma10_ini','ms_terma10_fin',
        'ms_terma11_ini','ms_terma11_fin','ms_terma12_ini','ms_terma12_fin',
        'ms_terma13_ini','ms_terma13_fin','ms_terma14_ini','ms_terma14_fin',
        'ms_terma15_ini','ms_terma15_fin','ms_terma16_ini','ms_terma16_fin',
        'ms_terma17_ini','ms_terma17_fin','ms_terma18_ini','ms_terma18_fin',
        'ms_terma19_ini','ms_terma19_fin','ms_terma20_ini','ms_terma20_fin',
        'ms_terma21_ini','ms_terma21_fin','ms_terma22_ini','ms_terma22_fin',
        'ms_terma23_ini','ms_terma23_fin','ms_terma24_ini','ms_terma24_fin',
        'ms_terma25_ini','ms_terma25_fin','ms_terma26_ini','ms_terma26_fin',
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
        'lubri_cedazo_estado','lubri_cedazo_obs','lubri_junta_estado','lubri_junta_obs',
        'lubri_lineas_estado','lubri_lineas_obs','trans_inspeccion','hidra_inspeccion',
        'blower_inspeccion','lubri_inspeccion','lubri_presion_filtros']
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
            print(f'Error correo: {e}')
    flash('✅ Protocolo guardado y enviado por correo!')
    return redirect(url_for('mantenimiento'))

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
        upper_A1 = [r[1] for r in rows]; upper_B1 = [r[2] for r in rows]
        upper_A2 = [r[3] for r in rows]; upper_B2 = [r[4] for r in rows]
        upper_A3 = [r[5] for r in rows]; upper_B3 = [r[6] for r in rows]
        lower_A1 = [r[7] for r in rows]; lower_B1 = [r[8] for r in rows]
        lower_A2 = [r[9] for r in rows]; lower_B2 = [r[10] for r in rows]
        lower_A3 = [r[11] for r in rows]; lower_B3 = [r[12] for r in rows]
        lower_A4 = [r[13] for r in rows]; lower_B4 = [r[14] for r in rows]
        lower_A5 = [r[15] for r in rows]; lower_B5 = [r[16] for r in rows]
        lower_A6 = [r[17] for r in rows]; lower_B6 = [r[18] for r in rows]
        feed_medida = [r[19] for r in rows]

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
        sl_B1=[r[1] for r in rows]; sl_A1=[r[2] for r in rows]
        sl_B2=[r[3] for r in rows]; sl_A2=[r[4] for r in rows]
        sl_B3=[r[5] for r in rows]; sl_A3=[r[6] for r in rows]
        sl_B4=[r[7] for r in rows]; sl_A4=[r[8] for r in rows]
        sl_B5=[r[9] for r in rows]; sl_A5=[r[10] for r in rows]
        sl_B6=[r[11] for r in rows]; sl_A6=[r[12] for r in rows]
        gap_interior=[r[13] for r in rows]; gap_exterior=[r[14] for r in rows]
        gap_sk_0=[r[15] for r in rows]; gap_sk_90=[r[16] for r in rows]
        gap_sk_180=[r[17] for r in rows]; gap_sk_270=[r[18] for r in rows]
        mfl_A=[r[19] for r in rows]; mfl_B=[r[20] for r in rows]
        mfl_C=[r[21] for r in rows]; mfl_D=[r[22] for r in rows]
        mfl_E=[r[23] for r in rows]; mfl_F=[r[24] for r in rows]
        mfl_G=[r[25] for r in rows]
        gp1=[r[26] for r in rows]; gp2=[r[27] for r in rows]
        gp3=[r[28] for r in rows]; gp4=[r[29] for r in rows]
        gp5=[r[30] for r in rows]; gp6=[r[31] for r in rows]

    return render_template('tendencias.html',
        tab=tab, tipo_filtro=tipo_filtro, codigo=codigo, upper=upper,
        fechas_armado=fechas_armado,
        upper_A1=upper_A1, upper_B1=upper_B1, upper_A2=upper_A2, upper_B2=upper_B2,
        upper_A3=upper_A3, upper_B3=upper_B3,
        lower_A1=lower_A1, lower_B1=lower_B1, lower_A2=lower_A2, lower_B2=lower_B2,
        lower_A3=lower_A3, lower_B3=lower_B3, lower_A4=lower_A4, lower_B4=lower_B4,
        lower_A5=lower_A5, lower_B5=lower_B5, lower_A6=lower_A6, lower_B6=lower_B6,
        feed_medida=feed_medida, codigo_cambio=codigo_cambio, cambio_data=cambio_data,
        fechas_cambio=fechas_cambio,
        sl_B1=sl_B1, sl_A1=sl_A1, sl_B2=sl_B2, sl_A2=sl_A2,
        sl_B3=sl_B3, sl_A3=sl_A3, sl_B4=sl_B4, sl_A4=sl_A4,
        sl_B5=sl_B5, sl_A5=sl_A5, sl_B6=sl_B6, sl_A6=sl_A6,
        gap_interior=gap_interior, gap_exterior=gap_exterior,
        gap_sk_0=gap_sk_0, gap_sk_90=gap_sk_90, gap_sk_180=gap_sk_180, gap_sk_270=gap_sk_270,
        mfl_A=mfl_A, mfl_B=mfl_B, mfl_C=mfl_C, mfl_D=mfl_D, mfl_E=mfl_E, mfl_F=mfl_F, mfl_G=mfl_G,
        gp1=gp1, gp2=gp2, gp3=gp3, gp4=gp4, gp5=gp5, gp6=gp6)

@app.route('/descargar/<tipo>/<int:id>')
def descargar_reporte(tipo, id):
    import psycopg2
    from psycopg2.extras import RealDictCursor
    database_url = os.environ.get('DATABASE_URL')
    tabla = 'armado_hb' if tipo == 'armado' else 'cambio_hb'
    conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    c = conn.cursor()
    c.execute(f'SELECT * FROM {tabla} WHERE id = %s', (id,))
    registro = c.fetchone()
    conn.close()
    if not registro:
        return 'No encontrado', 404
    datos = dict(registro)
    datos_norm = {}
    for k, v in datos.items():
        datos_norm[k] = v
        datos_norm[k.lower()] = v
        partes = k.split('_')
        clave_mixed = partes[0] + '_' + '_'.join(p[0].upper() + p[1:] if len(p) > 1 else p.upper() for p in partes[1:]) if len(partes) > 1 else k
        datos_norm[clave_mixed] = v
    datos = datos_norm
    if tipo == 'armado':
        ruta = generar_word_armado(datos)
        fecha = str(datos.get('fecha_inicio','') or '').replace('-','')[:8]
        nombre = f"{fecha}_ArmadoHB_{datos.get('id_head','X')}_{datos.get('id_bowl','X')}.docx"
    else:
        ruta = generar_word_cambio(datos)
        fecha = str(datos.get('fecha_inicio','') or '').replace('-','')[:8]
        nombre = f"{fecha}_CambioHB_{datos.get('chancadora','X')}.docx"
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
        total_armado=total_armado, total_cambio=total_cambio,
        ub_cambio=ub_cambio, sl_cambio=sl_cambio,
        clientes=clientes, chancadoras=chancadoras)

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
    c.execute('SELECT * FROM cambio_hb WHERE chancadora = %s ORDER BY fecha_inicio DESC LIMIT 1', (chancadora,))
    cols = [desc[0] for desc in c.description]
    row = c.fetchone()
    c.execute('''SELECT fecha_inicio,
                 socket_b1, socket_a1, socket_b2, socket_a2, socket_b3, socket_a3,
                 socket_b4, socket_a4, socket_b5, socket_a5, socket_b6, socket_a6,
                 sl_gap_interior, sl_gap_exterior,
                 socket_gap_0, socket_gap_90, socket_gap_180, socket_gap_270,
                 mfl_med_a, mfl_med_b, mfl_med_c, mfl_med_d, mfl_med_e, mfl_med_f, mfl_med_g,
                 gp1_medida, gp2_medida, gp3_medida, gp4_medida, gp5_medida, gp6_medida,
                 altura_bowl_saliente, altura_bowl_entrante, altura_final_bowl,
                 sl_cambio_ahora, socket_cambio_ahora, mfl_cambio_ahora, montura_cambio_ahora
                 FROM cambio_hb WHERE chancadora = %s ORDER BY fecha_inicio ASC''', (chancadora,))
    historial = c.fetchall()
    conn.close()
    if not row:
        return f'No hay registros para {chancadora}', 404
    d = dict(zip(cols, row))
    fechas = [str(h[0])[:10] for h in historial]
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle('titulo', parent=styles['Heading1'], fontSize=16, fontName='Helvetica-Bold', spaceAfter=6)
    subtitulo_style = ParagraphStyle('subtitulo', parent=styles['Heading2'], fontSize=12, fontName='Helvetica-Bold', textColor=colors.HexColor('#0f5132'), spaceBefore=12, spaceAfter=6)
    normal_style = ParagraphStyle('normal', parent=styles['Normal'], fontSize=10, spaceAfter=4)

    def tabla_datos(datos_tabla):
        t = Table(datos_tabla, colWidths=[10*cm, 7*cm])
        t.setStyle(TableStyle([
            ('FONTSIZE', (0,0), (-1,-1), 9), ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('PADDING', (0,0), (-1,-1), 6), ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ]))
        return t

    story = []
    story.append(Paragraph('METSO', ParagraphStyle('metso', parent=styles['Normal'], fontSize=20, fontName='Helvetica-Bold', spaceAfter=4)))
    story.append(Paragraph(f'Informe Estado Chancadora {chancadora}', titulo_style))
    story.append(Paragraph(f'Ultima intervencion: {d.get("fecha_registro", "-")} | Supervisor: {d.get("supervisor_metso", "-")}', normal_style))
    story.append(tabla_datos([
        ['Altura Bowl Saliente', str(d.get('altura_bowl_saliente') or '-') + ' pulg'],
        ['Altura Final Bowl', str(d.get('altura_final_bowl') or '-') + ' pulg'],
    ]))
    story.append(Paragraph('Recomendaciones', subtitulo_style))
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
        c.execute('INSERT INTO altura_bowl (chancadora, fecha, altura, operador, dias_parada, fecha_registro) VALUES (%s, %s, %s, %s, %s, %s)',
                  (chancadora, fecha, altura, operador, dias_parada, fecha_registro))
        conn.commit()
    chancadoras = ['CR011','CR012','CR013','CR014','CR021','CR022','CR023','CR024']
    chancadora_sel = request.args.get('chancadora', request.form.get('chancadora', 'CR011'))
    c.execute('SELECT id, fecha, altura, operador, dias_parada FROM altura_bowl WHERE chancadora = %s AND (ciclo_cerrado = FALSE OR ciclo_cerrado IS NULL) ORDER BY fecha ASC', (chancadora_sel,))
    registros = c.fetchall()
    conn.close()
    return render_template('alturas.html', registros=registros, chancadora_sel=chancadora_sel, chancadoras=chancadoras)

@app.route('/alturas/editar/<int:id>', methods=['POST'])
def alturas_editar(id):
    import psycopg2
    fecha = request.form.get('fecha')
    altura = request.form.get('altura')
    operador = request.form.get('operador')
    dias_parada = request.form.get('dias_parada', 0)
    chancadora = request.form.get('chancadora')
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    c = conn.cursor()
    c.execute('UPDATE altura_bowl SET fecha=%s, altura=%s, operador=%s, dias_parada=%s WHERE id=%s', (fecha, altura, operador, dias_parada, id))
    conn.commit()
    conn.close()
    return redirect(f'/alturas?chancadora={chancadora}')

@app.route('/alturas/eliminar/<int:id>', methods=['POST'])
def alturas_eliminar(id):
    import psycopg2
    chancadora = request.form.get('chancadora')
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    c = conn.cursor()
    c.execute('DELETE FROM altura_bowl WHERE id=%s', (id,))
    conn.commit()
    conn.close()
    return redirect(f'/alturas?chancadora={chancadora}')

@app.route('/alturas/nuevo_ciclo', methods=['POST'])
def alturas_nuevo_ciclo():
    import psycopg2
    chancadora = request.form.get('chancadora')
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    c = conn.cursor()
    c.execute('UPDATE altura_bowl SET ciclo_cerrado = TRUE WHERE chancadora = %s AND (ciclo_cerrado = FALSE OR ciclo_cerrado IS NULL)', (chancadora,))
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
        c.execute('SELECT fecha, altura FROM altura_bowl WHERE chancadora = %s AND (ciclo_cerrado = FALSE OR ciclo_cerrado IS NULL) ORDER BY fecha ASC', (ch,))
        registros = c.fetchall()
        if len(registros) >= 2:
            fechas = [r[0] for r in registros]
            alturas = [float(r[1]) for r in registros]
            t0 = datetime.strptime(str(fechas[0]), '%Y-%m-%d')
            dias = [(datetime.strptime(str(f), '%Y-%m-%d') - t0).days for f in fechas]
            n = len(dias)
            sumX = sum(dias); sumY = sum(alturas)
            sumXY = sum(dias[i]*alturas[i] for i in range(n))
            sumX2 = sum(x*x for x in dias)
            m = (n*sumXY - sumX*sumY) / (n*sumX2 - sumX*sumX)
            b_val = (sumY - m*sumX) / n
            if m < 0:
                import math
                dia_limite = (9.0 - b_val) / m
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
        c.execute('SELECT fecha_inicio FROM cambio_hb WHERE chancadora = %s AND fecha_inicio IS NOT NULL ORDER BY fecha_inicio ASC', (ch,))
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
        datos_plan[ch] = {'ultimo_cambio': str(ultimo_cambio) if ultimo_cambio else '-', 'duracion_promedio': duracion_promedio, 'fechas_cambio': fechas_cambio_proyectadas}
    conn.close()
    correcciones = {'CR021': '2026-07-01', 'CR024': '2026-07-06'}
    for ch, fecha_corr in correcciones.items():
        if ch in datos_plan and datos_plan[ch]['fechas_cambio']:
            datos_plan[ch]['fechas_cambio'][0] = fecha_corr
        elif ch in datos_plan:
            datos_plan[ch]['fechas_cambio'] = [fecha_corr]
    dias = {}
    for ch, d in datos_plan.items():
        for fecha_str in d['fechas_cambio']:
            if fecha_str not in dias:
                dias[fecha_str] = {'cambios': []}
            dias[fecha_str]['cambios'].append(ch)
    for fecha_str, data in dias.items():
        tiene_l1 = any(ch in L1 for ch in data['cambios'])
        tiene_l2 = any(ch in L2 for ch in data['cambios'])
        data['armados_lineas'] = []
        if tiene_l1: data['armados_lineas'].append('L1')
        if tiene_l2: data['armados_lineas'].append('L2')
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
        data['detalle_cambio'] = f"{n_c*3} soldadores, {n_c} riggers, {n_c} op. grua, {n_c*7} mecanicos" if n_c else '-'
        data['detalle_armado'] = f"{n_a*2} soldadores, {n_a} op. grua, {n_a} riggers, {n_a*5} mecanicos" if n_a else '-'
    semanas_sorted = dict(sorted(semanas.items()))
    dias_sorted = dict(sorted(dias.items()))
    return render_template('planificacion.html', datos_plan=datos_plan, chancadoras=chancadoras,
                           semanas=semanas_sorted, dias=dias_sorted, hoy=hoy.strftime('%Y-%m-%d'))

@app.route('/editar/cambio/<int:id>', methods=['GET'])
def editar_cambio(id):
    import psycopg2
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    c = conn.cursor()
    c.execute('SELECT * FROM cambio_hb WHERE id = %s', (id,))
    registro = c.fetchone()
    cols = [desc[0] for desc in c.description]
    conn.close()
    datos = dict(zip(cols, registro))
    return render_template('editar_cambio.html', datos=datos)

@app.route('/editar/cambio/<int:id>/guardar', methods=['POST'])
def editar_cambio_guardar(id):
    import psycopg2
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    c = conn.cursor()
    campos = request.form.keys()
    sets = ', '.join([f'{campo} = %s' for campo in campos])
    valores = [request.form.get(campo) for campo in campos]
    valores.append(id)
    c.execute(f'UPDATE cambio_hb SET {sets} WHERE id = %s', valores)
    conn.commit()
    conn.close()
    return redirect('/historial/cambio')

@app.route('/editar/armado/<int:id>', methods=['GET'])
def editar_armado(id):
    import psycopg2
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    c = conn.cursor()
    c.execute('SELECT * FROM armado_hb WHERE id = %s', (id,))
    registro = c.fetchone()
    cols = [desc[0] for desc in c.description]
    conn.close()
    datos = dict(zip(cols, registro))
    return render_template('editar_armado.html', datos=datos)

@app.route('/editar/armado/<int:id>/guardar', methods=['POST'])
def editar_armado_guardar(id):
    import psycopg2
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    c = conn.cursor()
    campos = request.form.keys()
    sets = ', '.join([f'{campo} = %s' for campo in campos])
    valores = [request.form.get(campo) for campo in campos]
    valores.append(id)
    c.execute(f'UPDATE armado_hb SET {sets} WHERE id = %s', valores)
    conn.commit()
    conn.close()
    return redirect('/historial/armado')

if __name__ == '__main__':
    #port = int(os.environ.get('PORT', 5000))
    #app.run(host='0.0.0.0', port=port)
    app.run(debug=True)