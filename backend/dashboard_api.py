
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from psycopg.rows import dict_row

from backend.database import get_connection

app = FastAPI(title="CareVoice Dashboard API")

frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        frontend_url,
        "http://localhost:5173"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "CareVoice Dashboard API is running"}


@app.get("/api/appointments")
def get_appointments():
    conn = get_connection()
    conn.row_factory = dict_row

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    a.id,
                    a.patient_name,
                    d.name AS doctor_name,
                    d.specialty,
                    s.slot_time,
                    a.status
                FROM appointments a
                LEFT JOIN doctors d ON a.doctor_id = d.id
                LEFT JOIN slots s ON a.slot_id = s.id
                ORDER BY a.id DESC
            """)

            return cursor.fetchall()

    finally:
        conn.close()


@app.get("/api/doctors")
def get_doctors():
    conn = get_connection()
    conn.row_factory = dict_row

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, name, specialty
                FROM doctors
                ORDER BY id
            """)

            return cursor.fetchall()

    finally:
        conn.close()
