import os
import base64
import urllib.request
import urllib.parse
import json

def enviar_correo(destinatario, asunto, ruta_archivo):
    api_key = os.environ.get('SENDGRID_API_KEY', '')
    remitente = os.environ.get('EMAIL_USER', '')

    if not api_key or not remitente:
        print('⚠️ SendGrid no configurado')
        return False

    try:
        adjunto = None
        if ruta_archivo and os.path.exists(ruta_archivo):
            with open(ruta_archivo, 'rb') as f:
                adjunto = base64.b64encode(f.read()).decode()

        data = {
            "personalizations": [{"to": [{"email": destinatario}]}],
            "from": {"email": remitente},
            "subject": asunto,
            "content": [{"type": "text/plain", "value": f"Adjunto el {asunto} generado desde la app de protocolos MP1250."}]
        }

        if adjunto:
            nombre = os.path.basename(ruta_archivo)
            data["attachments"] = [{"content": adjunto, "filename": nombre, "type": "application/octet-stream"}]

        body = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(
            'https://api.sendgrid.com/v3/mail/send',
            data=body,
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
        )
        with urllib.request.urlopen(req) as response:
            print(f'✅ Correo enviado a {destinatario} - Status: {response.status}')
            return True

    except Exception as e:
        print(f'❌ Error enviando correo: {e}')
        return False