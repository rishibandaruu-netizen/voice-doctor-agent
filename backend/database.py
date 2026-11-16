
import sqlite3

DB_NAME = "appointments.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialty TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER,
            slot_time TEXT NOT NULL,
            is_available INTEGER DEFAULT 1,
            FOREIGN KEY (doctor_id) REFERENCES doctors(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            phone TEXT NOT NULL,
            doctor_id INTEGER,
            slot_id INTEGER,
            status TEXT DEFAULT 'booked',
            FOREIGN KEY (doctor_id) REFERENCES doctors(id),
            FOREIGN KEY (slot_id) REFERENCES slots(id)
        )
    """)

    conn.commit()
    conn.close()


def insert_sample_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM doctors")
    count = cursor.fetchone()[0]

    if count == 0:
        doctors = [
            ("Dr. Ananya", "Cardiologist"),
            ("Dr. Rahul", "Dermatologist"),
            ("Dr. Priya", "General Physician")
        ]

        cursor.executemany(
            "INSERT INTO doctors (name, specialty) VALUES (?, ?)",
            doctors
        )

        slots = [
            (1, "2026-11-17 10:00 AM"),
            (1, "2026-11-17 11:00 AM"),
            (2, "2026-11-17 12:00 PM"),
            (2, "2026-11-17 02:00 PM"),
            (3, "2026-11-17 03:00 PM"),
            (3, "2026-11-17 04:00 PM")
        ]

        cursor.executemany(
            "INSERT INTO slots (doctor_id, slot_time) VALUES (?, ?)",
            slots
        )

    conn.commit()
    conn.close()
    print("Sample doctors and slots inserted!")


if __name__ == "__main__":
    create_tables()
    insert_sample_data()

