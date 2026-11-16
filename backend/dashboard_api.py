
import sqlite3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="CareVoice Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/appointments")
def get_appointments():
    conn = sqlite3.connect("appointments.db")
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
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
    """).fetchall()

    conn.close()
    return [dict(row) for row in rows]


@app.get("/api/doctors")
def get_doctors():
    conn = sqlite3.connect("appointments.db")
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT id, name, specialty FROM doctors
    """).fetchall()

    conn.close()
    return [dict(row) for row in rows]
