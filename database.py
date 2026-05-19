import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

def get_db():
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    else:
        import sqlite3
        conn = sqlite3.connect('protocolos.db')
        conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    tipo_id = 'SERIAL PRIMARY KEY' if os.environ.get('DATABASE_URL') else 'INTEGER PRIMARY KEY AUTOINCREMENT'
    
    c.execute(f'''CREATE TABLE IF NOT EXISTS armado_hb (
        id {tipo_id},
        fecha_registro TEXT,
        equipo TEXT, cliente TEXT, id_bowl TEXT, id_head TEXT,
        supervisor_metso TEXT, supervisor_cliente TEXT,
        fecha_inicio TEXT, fecha_termino TEXT,
        hora_inicio_h TEXT, hora_inicio_m TEXT,
        hora_fin_h TEXT, hora_fin_m TEXT,
        ub_paso1_estado TEXT, ub_paso1_obs TEXT, ub_paso2_obs TEXT,
        ub_paso3_estado TEXT, ub_paso3_obs TEXT,
        ub_paso4_estado TEXT, ub_paso4_obs TEXT,
        ub_paso5_estado TEXT, ub_paso5_obs TEXT,
        upper_bushing_cambio TEXT,
        upper_A1 REAL, upper_B1 REAL, upper_A2 REAL, upper_B2 REAL,
        upper_A3 REAL, upper_B3 REAL,
        ub_paso7_obs TEXT, ub_paso8_obs TEXT, ub_paso9_obs TEXT,
        ub_paso10_obs TEXT, ub_paso11_obs TEXT, ub_paso12_obs TEXT,
        ub_paso13_obs TEXT, ub_paso14_obs TEXT, ub_paso15_obs TEXT,
        upper_nuevo_A1 REAL, upper_nuevo_B1 REAL,
        upper_nuevo_A2 REAL, upper_nuevo_B2 REAL,
        upper_nuevo_A3 REAL, upper_nuevo_B3 REAL,
        lb_paso16_estado TEXT, lb_paso16_obs TEXT, lb_paso161_obs TEXT,
        lb_paso17_estado TEXT, lb_paso17_obs TEXT,
        lower_bushing_cambio TEXT,
        lower_A1 REAL, lower_B1 REAL, lower_A2 REAL, lower_B2 REAL,
        lower_A3 REAL, lower_B3 REAL, lower_A4 REAL, lower_B4 REAL,
        lower_A5 REAL, lower_B5 REAL, lower_A6 REAL, lower_B6 REAL,
        lb_paso21_obs TEXT, lb_paso22_obs TEXT, lb_paso221_obs TEXT,
        lb_paso24_obs TEXT, lb_paso25_obs TEXT, lb_paso26_obs TEXT,
        lower_nuevo_A1 REAL, lower_nuevo_B1 REAL,
        lower_nuevo_A2 REAL, lower_nuevo_B2 REAL,
        lower_nuevo_A3 REAL, lower_nuevo_B3 REAL,
        lower_nuevo_A4 REAL, lower_nuevo_B4 REAL,
        lower_nuevo_A5 REAL, lower_nuevo_B5 REAL,
        lower_nuevo_A6 REAL, lower_nuevo_B6 REAL,
        hb_paso28_estado TEXT, hb_paso28_obs TEXT,
        hb_paso29_estado TEXT, hb_paso29_obs TEXT,
        head_ball_cambio TEXT,
        hb_paso31_real TEXT, hb_paso31_obs TEXT,
        hb_paso32_real TEXT, hb_paso32_obs TEXT,
        hb_paso33_real TEXT, hb_paso33_obs TEXT,
        carter_sup_estado TEXT, carter_sup_obs TEXT,
        carter_inf_estado TEXT, carter_inf_obs TEXT,
        feed_plate_estado TEXT, fp_paso36_obs TEXT,
        feed_plate_cambio TEXT, feed_plate_altura REAL,
        feed_plate_desgaste REAL,
        fp_paso38_estado TEXT, fp_paso38_obs TEXT,
        fp_paso39_estado TEXT, fp_paso39_obs TEXT, fp_paso40_obs TEXT,
        ln_paso41_estado TEXT, ln_paso41_obs TEXT,
        ln_diametro TEXT, ln_espaciamiento TEXT,
        ln_torque50 TEXT, ln_torque75 TEXT, ln_torque100 TEXT,
        ln_serial_torq TEXT, ln_gap1 TEXT, ln_gap2 TEXT,
        epoxi_cantidad TEXT, epoxi_venc_catalizador TEXT,
        epoxi_venc_epoxico TEXT, epoxi_temp_sin_cat TEXT,
        epoxi_temp_con_cat TEXT,
        bowl_paso54_estado TEXT, bowl_paso54_obs TEXT,
        bowl_medida_hooper TEXT,
        bowl_paso56_estado TEXT, bowl_paso56_obs TEXT,
        bowl_paso57_estado TEXT, bowl_paso57_obs TEXT,
        bowl_paso58_estado TEXT, bowl_paso58_obs TEXT,
        bowl_medida_fisuras TEXT, bowl_paso582_obs TEXT,
        bowl_paso60_estado TEXT, bowl_paso60_obs TEXT,
        bowl_paso61_estado TEXT, bowl_paso61_obs TEXT,
        bowl_paso62_estado TEXT, bowl_paso62_obs TEXT,
        bowl_medida_fisura62 TEXT, bowl_paso622_obs TEXT,
        recomendaciones TEXT, correo_destino TEXT
    )''')

    c.execute(f'''CREATE TABLE IF NOT EXISTS cambio_hb (
        id {tipo_id},
        fecha_registro TEXT,
        fecha_inicio TEXT, fecha_termino TEXT,
        supervisor_cliente TEXT, supervisor_metso TEXT,
        cliente TEXT, chancadora TEXT,
        head_saliente TEXT, bowl_saliente TEXT,
        altura_bowl_saliente REAL,
        hora_inicio_h TEXT, hora_inicio_m TEXT,
        correo_destino TEXT,
        anillo_roscas_estado TEXT, anillo_roscas_obs TEXT,
        hidraulico_nivel_estado TEXT, hidraulico_nivel_obs TEXT,
        gap_aro_v1 REAL, gap_aro_v2 REAL, gap_aro_v3 REAL,
        clamping_fugas_estado TEXT, clamping_fugas_obs TEXT,
        sl_ranuras_estado TEXT, sl_ranuras_obs TEXT,
        socket_B1 REAL, socket_A1 REAL, socket_B2 REAL, socket_A2 REAL,
        socket_B3 REAL, socket_A3 REAL, socket_B4 REAL, socket_A4 REAL,
        socket_B5 REAL, socket_A5 REAL, socket_B6 REAL, socket_A6 REAL,
        sl_asentamiento_estado TEXT, sl_asentamiento_obs TEXT,
        sl_gap_interior REAL, sl_gap_exterior REAL,
        sl_fisuras_estado TEXT, sl_fisuras_obs TEXT,
        sl_deformaciones_estado TEXT, sl_deformaciones_obs TEXT,
        sl_canales_estado TEXT, sl_canales_obs TEXT,
        sl_cambio_ahora TEXT, sl_cambio_siguiente TEXT,
        sl_ret_precalentar TEXT, sl_ret_precalentar_obs TEXT,
        sl_ret_tornillos TEXT, sl_ret_tornillos_obs TEXT,
        sl_mont_precalentar TEXT, sl_mont_precalentar_obs TEXT,
        sl_mont_tornillos TEXT, sl_mont_tornillos_obs TEXT,
        sl_mont_enfriamiento TEXT, sl_mont_enfriamiento_obs TEXT,
        sl_mont_asentamiento TEXT, sl_mont_asentamiento_obs TEXT,
        sl_mont_gap_interno REAL, sl_mont_gap_externo REAL,
        socket_fisuras_estado TEXT, socket_fisuras_obs TEXT,
        socket_pernos_estado TEXT, socket_pernos_obs TEXT,
        socket_ranuras_estado TEXT, socket_ranuras_obs TEXT,
        socket_deform_estado TEXT, socket_deform_obs TEXT,
        socket_canales_estado TEXT, socket_canales_obs TEXT,
        socket_gap_0 REAL, socket_gap_90 REAL,
        socket_gap_180 REAL, socket_gap_270 REAL,
        socket_cambio_ahora TEXT, socket_cambio_siguiente TEXT,
        sk_ret_calentar_obs TEXT,
        sk_sal_A1 REAL, sk_sal_A2 REAL, sk_sal_A3 REAL, sk_sal_A4 REAL,
        sk_sal_B1 REAL, sk_sal_B2 REAL, sk_sal_B3 REAL, sk_sal_B4 REAL,
        sk_sal_C1 REAL, sk_sal_C2 REAL, sk_sal_C3 REAL, sk_sal_C4 REAL,
        sk_sal_D1 REAL, sk_sal_D2 REAL, sk_sal_D3 REAL, sk_sal_D4 REAL,
        sk_mont_calentar_obs TEXT, sk_mont_enfriar_obs TEXT, sk_mont_gap_obs TEXT,
        sk_new_A1 REAL, sk_new_A2 REAL, sk_new_A3 REAL, sk_new_A4 REAL,
        sk_new_B1 REAL, sk_new_B2 REAL, sk_new_B3 REAL, sk_new_B4 REAL,
        sk_new_C1 REAL, sk_new_C2 REAL, sk_new_C3 REAL, sk_new_C4 REAL,
        sk_new_D1 REAL, sk_new_D2 REAL, sk_new_D3 REAL, sk_new_D4 REAL,
        mainshaft_obs TEXT,
        ms_A1 REAL, ms_A2 REAL, ms_A3 REAL, ms_A4 REAL,
        ms_B1 REAL, ms_B2 REAL, ms_B3 REAL, ms_B4 REAL,
        ms_C1 REAL, ms_C2 REAL, ms_C3 REAL, ms_C4 REAL,
        ms_D1 REAL, ms_D2 REAL, ms_D3 REAL, ms_D4 REAL,
        mfl_pernos_estado TEXT, mfl_pernos_obs TEXT,
        mfl_medida TEXT,
        mfl_med_A REAL, mfl_med_B REAL, mfl_med_C REAL, mfl_med_D REAL,
        mfl_med_E REAL, mfl_med_F REAL, mfl_med_G REAL,
        mfl_cambio_ahora TEXT, mfl_cambio_siguiente TEXT,
        mfl_mont_pernos TEXT, mfl_mont_pernos_obs TEXT,
        mfl_new_A REAL, mfl_new_B REAL, mfl_new_C REAL, mfl_new_D REAL,
        mfl_new_E REAL, mfl_new_F REAL, mfl_new_G REAL,
        montura_barras_estado TEXT, montura_barras_obs TEXT,
        montura_acumulacion_estado TEXT, montura_acumulacion_obs TEXT,
        montura_chocky_estado TEXT, montura_chocky_obs TEXT,
        montura_cambio_ahora TEXT, montura_cambio_siguiente TEXT,
        gp1_cambio TEXT, gp1_medida TEXT, gp1_obs TEXT,
        gp2_cambio TEXT, gp2_medida TEXT, gp2_obs TEXT,
        gp3_cambio TEXT, gp3_medida TEXT, gp3_obs TEXT,
        gp4_cambio TEXT, gp4_medida TEXT, gp4_obs TEXT,
        gp5_cambio TEXT, gp5_medida TEXT, gp5_obs TEXT,
        gp6_cambio TEXT, gp6_medida TEXT, gp6_obs TEXT,
        prot_estatico_estado TEXT, prot_estatico_obs TEXT,
        prot_dinamico_estado TEXT, prot_dinamico_obs TEXT,
        prot_din_fuga TEXT, prot_din_fuga_obs TEXT,
        contrapeso_estado TEXT, contrapeso_obs TEXT,
        sello_ut_estado TEXT, sello_ut_obs TEXT,
        head_entrante TEXT, bowl_entrante TEXT,
        altura_bowl_entrante REAL, altura_final_bowl REAL, hora_fin_h TEXT, hora_fin_m TEXT,
        recomendaciones TEXT
    )''')

    conn.commit()
    conn.close()

def guardar_armado(datos):
    conn = get_db()
    c = conn.cursor()
    datos['fecha_registro'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    columnas = ', '.join(datos.keys())
    ph = '%s' if os.environ.get('DATABASE_URL') else '?'
    placeholders = ', '.join([ph for _ in datos])
    c.execute(f'INSERT INTO armado_hb ({columnas}) VALUES ({placeholders})',
              list(datos.values()))
    conn.commit()
    conn.close()

def guardar_cambio(datos):
    conn = get_db()
    c = conn.cursor()
    datos['fecha_registro'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    columnas = ', '.join(datos.keys())
    ph = '%s' if os.environ.get('DATABASE_URL') else '?'
    placeholders = ', '.join([ph for _ in datos])
    c.execute(f'INSERT INTO cambio_hb ({columnas}) VALUES ({placeholders})',
              list(datos.values()))
    conn.commit()
    conn.close()
    
def obtener_registros(tipo, filtros=None):
    conn = get_db()
    c = conn.cursor()
    tabla = 'armado_hb' if tipo == 'armado' else 'cambio_hb'
    
    where = []
    params = []
    
    if filtros:
        if filtros.get('chancadora'):
            where.append('chancadora = %s' if os.environ.get('DATABASE_URL') else 'chancadora = ?')
            params.append(filtros['chancadora'])
        if filtros.get('id_bowl'):
            where.append('id_bowl = %s' if os.environ.get('DATABASE_URL') else 'id_bowl = ?')
            params.append(filtros['id_bowl'])
        if filtros.get('id_head'):
            where.append('id_head = %s' if os.environ.get('DATABASE_URL') else 'id_head = ?')
            params.append(filtros['id_head'])
        if filtros.get('supervisor_metso'):
            where.append('supervisor_metso = %s' if os.environ.get('DATABASE_URL') else 'supervisor_metso = ?')
            params.append(filtros['supervisor_metso'])
        if filtros.get('fecha'):
            where.append('fecha_inicio = %s' if os.environ.get('DATABASE_URL') else 'fecha_inicio = ?')
            params.append(filtros['fecha'])
    
    query = f'SELECT * FROM {tabla}'
    if where:
        query += ' WHERE ' + ' AND '.join(where)
    query += ' ORDER BY fecha_registro DESC'
    
    c.execute(query, params)
    registros = c.fetchall()
    conn.close()
    return registros

def obtener_tendencias(tipo, campo):
    conn = get_db()
    c = conn.cursor()
    tabla = 'armado_hb' if tipo == 'armado' else 'cambio_hb'
    c.execute(f'SELECT fecha_registro, {campo} FROM {tabla} WHERE {campo} IS NOT NULL ORDER BY fecha_registro ASC')
    datos = c.fetchall()
    conn.close()
    return datos