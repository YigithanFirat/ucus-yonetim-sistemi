import sqlite3
from datetime import datetime, timedelta

DB_NAME = "flights.db"

from datetime import datetime, timedelta

def calculate_duration_between(start_time, end_time):
    """
    İki saat arasındaki süreyi "X saat Y dakika" formatında hesaplar.
    Gece geçişini (23:00 - 01:00 gibi) de destekler.
    """
    fmt = "%H:%M"
    try:
        start = datetime.strptime(start_time, fmt)
        end = datetime.strptime(end_time, fmt)

        # Eğer bitiş zamanı başlama zamanından önceyse, gece geçişi demektir
        if end < start:
            end += timedelta(days=1)

        diff = end - start
        total_minutes = diff.seconds // 60
        hours = total_minutes // 60
        minutes = total_minutes % 60

        return f"{hours} saat {minutes} dakika"
    except Exception as e:
        return None


def create_flight(flight_number, departure, arrival, date, capacity, eco_seats, bus_seats,
                  departure_time=None, arrival_time=None,
                  flight_type=None, transfer_point=None,
                  first_departure_time=None, first_arrival_time=None,
                  second_departure_time=None, second_arrival_time=None):
    
    # Süreyi otomatik hesapla
    duration = None
    if flight_type == "Aktarmasız Uçuş" and departure_time and arrival_time:
        duration = calculate_duration_between(departure_time, arrival_time)
    elif flight_type == "Aktarmalı Uçuş" and first_departure_time and second_arrival_time:
        duration = calculate_duration_between(first_departure_time, second_arrival_time)
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO flights 
            (flight_number, departure, arrival, date, capacity, eco_seats, bus_seats,
             departure_time, arrival_time, duration, flight_type, transfer_point,
             first_departure_time, first_arrival_time, second_departure_time, second_arrival_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (flight_number, departure, arrival, date, capacity, eco_seats, bus_seats,
              departure_time, arrival_time, duration, flight_type, transfer_point,
              first_departure_time, first_arrival_time, second_departure_time, second_arrival_time))
        conn.commit()
        return True, f"{flight_number} uçuşu başarıyla oluşturuldu. Süre: {duration if duration else 'Hesaplanamadı'}"
    except sqlite3.IntegrityError:
        return False, "Bu uçuş numarası zaten mevcut!"
    finally:
        conn.close()



def delete_flight(flight_number):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM flights WHERE flight_number = ?", (flight_number,))
    conn.commit()
    if cursor.rowcount > 0:
        print(f"{flight_number} numaralı uçuş silindi.")
    else:
        print(f"{flight_number} numaralı uçuş bulunamadı.")
    conn.close()

def add_passenger(flight_number, name, surname, tck):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Uçuş var mı kontrol et
    cursor.execute("SELECT id FROM flights WHERE flight_number = ?", (flight_number,))
    flight = cursor.fetchone()
    if not flight:
        print("Uçuş bulunamadı!")
        conn.close()
        return
    
    flight_id = flight[0]

    # Yolcu ekle
    cursor.execute("""
        INSERT INTO passengers (flight_id, name, surname, tck)
        VALUES (?, ?, ?, ?)
    """, (flight_id, name, surname, tck))
    conn.commit()
    print(f"{name} {surname} uçuşa başarıyla eklendi.")
    conn.close()

def list_passengers(flight_number):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM flights WHERE flight_number = ?", (flight_number,))
    flight = cursor.fetchone()
    if not flight:
        print("Uçuş bulunamadı!")
        conn.close()
        return
    
    flight_id = flight[0]
    cursor.execute("SELECT id, name, surname, tck FROM passengers WHERE flight_id = ?", (flight_id,))
    passengers = cursor.fetchall()
    if not passengers:
        print("Bu uçuşa kayıtlı yolcu yok.")
    else:
        print(f"{flight_number} uçuşundaki yolcular:")
        for p in passengers:
            print(f"ID: {p[0]}, İsim: {p[1]} {p[2]}, TCK: {p[3]}")
    conn.close()


def list_flights_by_date(date):
    conn = sqlite3.connect("flights.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM flights WHERE date = ?", (date,))
    flights = cursor.fetchall()

    if flights:
        print(f"\n📅 {date} tarihli uçuşlar:")
        for flight in flights:
            print(f"Flight: {flight[0]} | Departure: {flight[1]} | Arrival: {flight[2]} | Date: {flight[3]} | Capacity: {flight[4]} | Eco: {flight[5]} | Bus: {flight[6]}")
    else:
        print(f"\n❌ {date} tarihindeki uçuşlar bulunamadı.")
    
    conn.close()




def list_all_flights():
    conn = sqlite3.connect("flights.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM flights")
    flights = cursor.fetchall()
    conn.close()

    # Eğer veri varsa DataFrame'e çevir, yoksa boş DataFrame döndür
    if flights:
        return pd.DataFrame(flights, columns=[
            "Uçuş No", "Kalkış", "Varış", "Tarih", "Kapasite", "Ekonomi", "Business"
        ])
    else:
        return pd.DataFrame(columns=[
            "Uçuş No", "Kalkış", "Varış", "Tarih", "Kapasite", "Ekonomi", "Business"
        ])


def list_flights_menu():
    print("\n✈️  Uçuşları Listele:")
    print("1. Tarihe Göre Listele")
    print("2. Tüm Uçuşları Listele")
    choice = input("Seçiminizi yapın (1/2): ")

    if choice == "1":
        date = input("Lütfen tarihi girin (YYYY-MM-DD): ")
        list_flights_by_date(date)
    elif choice == "2":
        list_all_flights()
    else:
        print("❗ Geçersiz seçim.")
