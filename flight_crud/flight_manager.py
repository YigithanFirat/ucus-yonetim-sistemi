import sqlite3
import pandas as pd

DB_NAME = "flights.db"

def create_flight(flight_number, departure, arrival, date, capacity, eco_seats, bus_seats):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO flights (flight_number, departure, arrival, date, capacity, eco_seats, bus_seats)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (flight_number, departure, arrival, date, capacity, eco_seats, bus_seats))
        conn.commit()
        print(f"{flight_number} uçuşu başarıyla oluşturuldu.")
    except sqlite3.IntegrityError:
        print("Bu uçuş numarası zaten mevcut!")
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
