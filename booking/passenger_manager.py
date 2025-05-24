import sqlite3
from booking.checkin import check_in
from booking.pdf_ticket import generate_pdf_ticket
from utils.validation import is_valid_tck
from flight_crud.database import connect_db  # Eğer varsa daha düzenli olur

def add_passenger(flight_number, name, surname, tck):
    if not is_valid_tck(tck):
        print("❌ Geçersiz TCK numarası!")
        return None

    conn = connect_db()
    cursor = conn.cursor()

    # ✅ Uçuş numarasının varlığını kontrol et
    cursor.execute("SELECT flight_number FROM flights WHERE flight_number = ?", (flight_number,))
    if cursor.fetchone() is None:
        print(f"❌ '{flight_number}' numaralı bir uçuş bulunamadı. Yolcu eklenemedi.")
        conn.close()
        return None

    # Yolcuyu passengers tablosuna ekle
    cursor.execute("""
        INSERT INTO passengers (flight_number, name, surname, tck)
        VALUES (?, ?, ?, ?)
    """, (flight_number, name, surname, tck))

    passenger_id = cursor.lastrowid

    conn.commit()
    conn.close()

    print(f"✅ {name} {surname} adlı yolcu için rezervasyon oluşturuldu. Yolcu ID: {passenger_id}")
    return passenger_id


def list_passengers(flight_number):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM passengers WHERE flight_number = ?", (flight_number,))
    passengers = cursor.fetchall()

    if passengers:
        print(f"📋 {flight_number} Uçuşundaki Yolcular:")
        for p in passengers:
            print(f"🆔 ID: {p[0]} | 👤 Ad: {p[2]} | Soyad: {p[3]} | 🪪 TCK: {p[4]}")
    else:
        print(f"ℹ️ {flight_number} uçuşunda kayıtlı yolcu bulunmuyor.")

    conn.close()

def delete_passenger(flight_number, passenger_id):
    conn = sqlite3.connect("flights.db")
    cursor = conn.cursor()
    
    # Önce yolcunun uçuş numarasını doğrula
    cursor.execute("SELECT * FROM passengers WHERE passenger_id = ? AND flight_number = ?", (passenger_id, flight_number))
    result = cursor.fetchone()
    if result:
        cursor.execute("DELETE FROM passengers WHERE passenger_id = ?", (passenger_id,))
        conn.commit()
        print(f"Yolcu ID {passenger_id}, uçuş {flight_number} kaydından silindi.")
    else:
        print("Belirtilen uçuşta böyle bir yolcu bulunamadı.")
    
    conn.close()