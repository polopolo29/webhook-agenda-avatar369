from __future__ import print_function
import os.path
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Si modificas este alcance, elimina el archivo token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    creds = None
    # El archivo token.json almacena el token de acceso del usuario.
    if os.path.exists('token.json'):
        with open('token.json', 'rb') as token:
            creds = pickle.load(token)

    # Si no hay credenciales válidas disponibles, solicita al usuario que inicie sesión.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Guarda las credenciales para la próxima ejecución
        with open('token.json', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    print("✅ Google Calendar autorizado correctamente.")

if __name__ == '__main__':
    main()

