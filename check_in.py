from datetime import datetime
import json
import os
import pytz
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from google.oauth2.service_account import Credentials
import gspread

load_dotenv()

# --- Google Sheets Setup ---
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

creds_env_string = os.environ["GOOGLE_CREDENTIALS"]
creds_dict = json.loads(creds_env_string)
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)

# Connect to the workbook and target the attendance worksheet
# Tip: Use a separate worksheet/tab (e.g., 'Asistencia') to avoid overwriting registration data
workbook = client.open("Registro_ES_Galilea_2026")

# Access the 'Asistencia' worksheet, or create it if it doesn't exist yet
try:
  attendance_sheet = workbook.worksheet("Asistencia")
except gspread.exceptions.WorksheetNotFound:
  attendance_sheet = workbook.add_worksheet(title="Asistencia", rows=1000, cols=3)
  attendance_sheet.append_row(["ID", "Fecha", "Hora"])  # Header row

# --- Flask App Setup ---
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super-secret-key")


@app.route("/", methods=["GET"])
def checkin_form():
  return render_template("checkin.html")


@app.route("/checkin", methods=["POST"])
def checkin():
  attendee_id = request.form.get("attendee_id", "").strip().upper()

  if not attendee_id:
    flash("Por favor, ingresa tu ID de asistente.")
    return redirect(url_for("checkin_form"))

  # Define local timezone (adjust timezone name if needed, e.g., 'America/Bogota')
  tz = pytz.timezone("America/Bogota")
  now = datetime.now(tz)

  fecha = now.strftime("%Y-%m-%d")  # YYYY-MM-DD
  hora = now.strftime("%H:%M:%S")  # HH:MM:SS

  # Append attendance record: [ID, Fecha, Hora]
  attendance_sheet.append_row([attendee_id, fecha, hora])

  return render_template(
      "checkin_success.html", attendee_id=attendee_id, fecha=fecha, hora=hora
  )


if __name__ == "__main__":
  app.run(
      host="0.0.0.0", port=int(os.environ.get("CHECKIN_PORT", 5001)), debug=True
  )