from __future__ import print_function
import os.path
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Permisos que pediremos (solo Calendar)
SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    creds = None
    if os.path.exists('token.json'):
        # Si ya existe un token autorizado, lo usamos
        with open('token.json', 'rb') as token:
            creds = pickle.load(token)
    # Si no existe, pedimos al usuario que se loguee
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Guardamos el token para futuros accesos automáticos
        with open('token.json', 'wb') as token:
            pickle.dump(creds, token)

    # Prueba de conexión: listar los próximos 5 eventos
    service = build('calendar', 'v3', credentials=creds)

    print("Conexión exitosa. Estos son tus próximos eventos:")
    events_result = service.events().list(
        calendarId='primary', maxResults=5, singleEvents=True,
        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No hay eventos próximos.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

if __name__ == '__main__':
    main()
