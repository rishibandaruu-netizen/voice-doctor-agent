
from backend.database import get_connection


def check_doctor_availability(specialty=None):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            doctors.id,
            doctors.name,
            doctors.specialty,
            slots.id,
            slots.slot_time
        FROM doctors
        JOIN slots
        ON doctors.id = slots.doctor_id
        WHERE slots.is_available = 1
    """

    params = []

    if specialty:
        query += " AND LOWER(doctors.specialty) = LOWER(?)"
        params.append(specialty)

    cursor.execute(query, params)

    results = cursor.fetchall()

    conn.close()

    available_slots = []

    for row in results:
        available_slots.append({
            "doctor_id": row[0],
            "doctor_name": row[1],
            "specialty": row[2],
            "slot_id": row[3],
            "slot_time": row[4]
        })

    return available_slots



def book_appointment(slot_id, phone, patient_name=None):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Start a database transaction
        cursor.execute("BEGIN IMMEDIATE")

        # Check whether the selected slot is available
        cursor.execute(
            "SELECT doctor_id, slot_time FROM slots "
            "WHERE id = ? AND is_available = 1",
            (slot_id,)
        )

        slot = cursor.fetchone()

        if slot is None:
            conn.rollback()
            return {
                "success": False,
                "message": "Sorry, this slot is not available."
            }

        doctor_id, slot_time = slot

        # Save the appointment
        cursor.execute("""
            INSERT INTO appointments
            (patient_name, phone, doctor_id, slot_id, status)
            VALUES (?, ?, ?, ?, 'booked')
        """, (patient_name, phone, doctor_id, slot_id))

        appointment_id = cursor.lastrowid

        # Mark the slot as unavailable
        cursor.execute("""
            UPDATE slots
            SET is_available = 0
            WHERE id = ? AND is_available = 1
        """, (slot_id,))

        if cursor.rowcount != 1:
            conn.rollback()
            return {
                "success": False,
                "message": "This slot is no longer available."
            }

        conn.commit()

        return {
            "success": True,
            "appointment_id": appointment_id,
            "doctor_id": doctor_id,
            "slot_time": slot_time,
            "phone": phone,
            "message": "Appointment booked successfully!"
        }

    except Exception as error:
        conn.rollback()
        return {
            "success": False,
            "message": str(error)
        }

    finally:
        conn.close()



def cancel_appointment(appointment_id, phone):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE")

        # Find the patient's booked appointment
        cursor.execute("""
            SELECT slot_id
            FROM appointments
            WHERE id = ?
            AND phone = ?
            AND status = 'booked'
        """, (appointment_id, phone))

        appointment = cursor.fetchone()

        if appointment is None:
            conn.rollback()
            return {
                "success": False,
                "message": "No matching active appointment found."
            }

        slot_id = appointment[0]

        # Change appointment status to cancelled
        cursor.execute("""
            UPDATE appointments
            SET status = 'cancelled'
            WHERE id = ?
            AND phone = ?
            AND status = 'booked'
        """, (appointment_id, phone))

        # Make the appointment slot available again
        cursor.execute("""
            UPDATE slots
            SET is_available = 1
            WHERE id = ?
        """, (slot_id,))

        conn.commit()

        return {
            "success": True,
            "appointment_id": appointment_id,
            "message": "Appointment cancelled successfully!"
        }

    except Exception as error:
        conn.rollback()
        return {
            "success": False,
            "message": str(error)
        }

    finally:
        conn.close()




if __name__ == "__main__":

    print("\n1. CHECKING DOCTOR AVAILABILITY")

    slots = check_doctor_availability("Cardiologist")

    for slot in slots:
        print(slot)

    print("\n2. BOOKING APPOINTMENT")

    booking = book_appointment(
        slot_id=1,
        phone="9876543210",
        patient_name="Test Patient"
    )

    print(booking)

    print("\n3. CHECKING AVAILABILITY AGAIN")

    slots = check_doctor_availability("Cardiologist")

    for slot in slots:
        print(slot)

    print("\n4. CANCELLING APPOINTMENT")

    if booking["success"]:
        cancellation = cancel_appointment(
            appointment_id=booking["appointment_id"],
            phone="9876543210"
        )

        print(cancellation)

    print("\n5. FINAL AVAILABILITY")

    slots = check_doctor_availability("Cardiologist")

    for slot in slots:
        print(slot)

