# calendar_utils.py

import datetime
import os
import pickle
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES      = ["https://www.googleapis.com/auth/calendar"]
CALENDAR_ID = "primary"

def obtener_credenciales():
    """
    Carga o renueva credenciales de Google Calendar desde 'credentials.json' y 'token.json'.
    """
    creds = None
    if os.path.exists("token.json"):
        with open("token.json", "rb") as token_file:
            creds = pickle.load(token_file)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            from google_auth_oauthlib.flow import InstalledAppFlow
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
            with open("token.json", "wb") as token_file:
                pickle.dump(creds, token_file)
    return creds

def get_free_busy(service, time_min, time_max):
    """
    Llama a la API FreeBusy para ver los bloques ocupados entre time_min y time_max.
    """
    body = {
        "timeMin": time_min.isoformat(),
        "timeMax": time_max.isoformat(),
        "items": [{"id": CALENDAR_ID}]
    }
    eventos = service.freebusy().query(body=body).execute()
    return eventos["calendars"][CALENDAR_ID]["busy"]

def get_available_slots():
    """
    Retorna hasta 10 horarios libres (50min + 30min descanso) en los próximos 7 días:
      - Lunes a sábado: 07:00 - 17:00
      - Domingo:         09:00 - 13:00
    """
    creds = obtener_credenciales()
    service = build("calendar", "v3", credentials=creds)

    now = datetime.datetime.now()
    end_period = now + datetime.timedelta(days=7)
    disponibles = []

    current_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    while current_day < end_period:
        weekday = current_day.weekday()  # 0=lun,...,6=dom
        if weekday < 6:
            day_start = current_day.replace(hour=7, minute=0)
            day_end   = current_day.replace(hour=17, minute=0)
        else:
            day_start = current_day.replace(hour=9, minute=0)
            day_end   = current_day.replace(hour=13, minute=0)

        busy_times = get_free_busy(service, day_start, day_end)
        slot_start = day_start
        while slot_start + datetime.timedelta(minutes=50) <= day_end:
            slot_end = slot_start + datetime.timedelta(minutes=50)
            ocupado = False
            for busy in busy_times:
                inicio = datetime.datetime.fromisoformat(busy["start"])
                fin    = datetime.datetime.fromisoformat(busy["end"])
                if slot_start < fin and slot_end > inicio:
                    ocupado = True
                    break
            if not ocupado:
                disponibles.append(slot_start.strftime("%Y-%m-%d %H:%M"))
            slot_start = slot_start + datetime.timedelta(minutes=80)
        current_day += datetime.timedelta(days=1)

    return disponibles[:10]

def crear_evento_google_calendar(numero, texto_horario, gratuito=False):
    """
    Crea un evento en Google Calendar. Si gratuito=True, agrega “(GRATIS)” al título.
    """
    creds = obtener_credenciales()
    service = build("calendar", "v3", credentials=creds)
    inicio = datetime.datetime.strptime(texto_horario, "%Y-%m-%d %H:%M")
    fin    = inicio + datetime.timedelta(minutes=50)
    summary = f"Cita Terapia {'(GRATIS)' if gratuito else ''} - {numero}"
    evento = {
        "summary": summary,
        "start": {"dateTime": inicio.isoformat()},
        "end":   {"dateTime": fin.isoformat()},
    }
    service.events().insert(calendarId=CALENDAR_ID, body=evento).execute()
