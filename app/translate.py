from flask_babel import _
from app import app
from google.cloud import translate_v2 as translate

def translate(text, source_language, dest_language):
    if 'GOOGLE_APPLICATION_CREDENTIALS' not in app.config or \
            not app.config['GOOGLE_APPLICATION_CREDENTIALS']:
        return _('Error: the translation service is not configured.')
    
    try:
        translate_client = translate.Client()
        result = translate_client.translate(
            text, source_language=source_language, target_language=dest_language)
        return result['translatedText']
    except Exception as e:
        return _('Error: the translation service failed. {}').format(e)
