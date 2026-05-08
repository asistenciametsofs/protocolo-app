import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

def enviar_correo(destinatario, asunto, ruta_archivo):
    # Datos del remitente — los configuramos con variables de entorno
    remitente = os.environ.get('EMAIL_USER', '')
    password = os.environ.get('EMAIL_PASS', '')

    if not remitente or not password:
        print('⚠️ Correo no configurado, saltando envío')
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = destinatario
        msg['Subject'] = asunto

        cuerpo = f'''
Estimado equipo,

Se adjunta el {asunto} generado automáticamente desde la app de protocolos MP1250.

Este reporte fue generado el día de hoy y contiene todos los datos ingresados durante la inspección.

Saludos,
Sistema de Protocolos METSO MP1250
        '''
        msg.attach(MIMEText(cuerpo, 'plain'))

        # Adjuntar el Word
        if ruta_archivo and os.path.exists(ruta_archivo):
            with open(ruta_archivo, 'rb') as f:
                parte = MIMEBase('application', 'octet-stream')
                parte.set_payload(f.read())
                encoders.encode_base64(parte)
                nombre_archivo = os.path.basename(ruta_archivo)
                parte.add_header('Content-Disposition', f'attachment; filename={nombre_archivo}')
                msg.attach(parte)

        # Enviar via Outlook/Hotmail
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()
        servidor.login(remitente, password)
        servidor.sendmail(remitente, destinatario, msg.as_string())
        servidor.quit()
        print(f'✅ Correo enviado a {destinatario}')
        return True

    except Exception as e:
        print(f'❌ Error enviando correo: {e}')
        return False