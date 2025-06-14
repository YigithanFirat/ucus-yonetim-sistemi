import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

DB_NAME = "flights.db"

from datetime import datetime, timedelta

def calculate_flight_duration(departure, arrival):
    fmt = "%H:%M"
    departure_time = datetime.strptime(departure, fmt)
    arrival_time = datetime.strptime(arrival, fmt)

    if arrival_time < departure_time:
        arrival_time += timedelta(days=1)

    duration = arrival_time - departure_time
    return duration.seconds // 60  # dakika cinsinden

def calculate_duration_minutes(departure, arrival):
    fmt = "%H:%M"
    departure_time = datetime.strptime(departure, fmt)
    arrival_time = datetime.strptime(arrival, fmt)
    if arrival_time < departure_time:
        arrival_time += timedelta(days=1)
    return (arrival_time - departure_time).seconds // 60


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


def create_flight(
    flight_number, departure, arrival, date, capacity, eco_seats, bus_seats,
    departure_time=None, arrival_time=None,
    flight_type=None, transfer_point=None,
    first_departure_time=None, first_arrival_time=None,
    second_departure_time=None, second_arrival_time=None,
    duration=None
):
    # duration'ı hesapla ve güncelle
    if flight_type == "Direk Uçuş" and departure_time and arrival_time:
        duration = calculate_duration_between(departure_time, arrival_time)
    elif flight_type == "Aktarmalı Uçuş" and first_departure_time and second_arrival_time:
        duration = calculate_duration_between(first_departure_time, second_arrival_time)
    else:
        duration = None  # ya da "Bilinmiyor" gibi bir değer de atanabilir

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO flights (
                flight_number, departure, arrival, date, capacity,
                eco_seats, bus_seats, departure_time, arrival_time,
                duration, flight_type, transfer_point,
                first_departure_time, first_arrival_time,
                second_departure_time, second_arrival_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            flight_number, departure, arrival, date, capacity,
            eco_seats, bus_seats, departure_time, arrival_time,
            duration, flight_type, transfer_point,
            first_departure_time, first_arrival_time,
            second_departure_time, second_arrival_time
        ))
        conn.commit()
        return True, f"{flight_number} uçuşu başarıyla oluşturuldu."

    except sqlite3.IntegrityError:
        return False, "Bu uçuş numarası zaten mevcut!"

    except Exception as e:
        return False, f"Veritabanı hatası: {e}"

    finally:
        if conn:
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

    try:
        conn = sqlite3.connect("flights.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM flights WHERE date = ?", (date,))
        flights = cursor.fetchall()

        if flights:
            print(f"\n📅 {date} tarihli uçuşlar:")
            for flight in flights:
                print(f"""
🔹 Uçuş Numarası: {flight[0]}
   Kalkış: {flight[1]} ➜ Varış: {flight[2]}
   Uçuş Tipi: {flight[10]} | Tarih: {flight[3]} | Kapasite: {flight[4]}
   Ekonomi: {flight[5]} | Business: {flight[6]}
   Direkt Saatler: {flight[7]} ➜ {flight[8]} | Süre: {flight[9]}
   Aktarma Noktası: {flight[11] if flight[11] else 'Yok'}
   1. Uçuş: {flight[12]} ➜ {flight[13]}
   2. Uçuş: {flight[14]} ➜ {flight[15]}
                """)
        else:
            print(f"\n❌ {date} tarihindeki uçuşlar bulunamadı.")
    
    except Exception as e:
        print(f"⚠️ Hata oluştu: {e}")
    
    finally:
        if conn:
            conn.close()

def list_all_flights():

    conn = sqlite3.connect("flights.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM flights")
    flights = cursor.fetchall()
    conn.close()

    # Veritabanındaki sütun sıralamasıyla tam uyumlu olmalı!
    columns = [
        "Uçuş Numarası",         # 0
        "Kalkış Noktası",        # 1
        "Varış Noktası",         # 2
        "Uçuş Tarihi",           # 3
        "Toplam Kapasite",       # 4
        "Ekonomi Koltuk",        # 5
        "Business Koltuk",       # 6
        "Kalkış (Direkt)",       # 7
        "Varış (Direkt)",        # 8
        "Uçuş Süresi",           # 9 ← burası doğru konumda
        "Uçuş Tipi",             # 10
        "Aktarma Noktası",       # 11
        "Kalkış (1. Uçuş)",      # 12
        "Varış (1. Uçuş)",       # 13
        "Kalkış (2. Uçuş)",      # 14
        "Varış (2. Uçuş)"        # 15
    ]

    if flights:
        df = pd.DataFrame(flights, columns=columns)
        df.fillna("Yok", inplace=True)

        # Tip sıralama ve tarih sıralama
        df["Uçuş Tipi"] = pd.Categorical(df["Uçuş Tipi"], categories=["Direk Uçuş", "Aktarmalı Uçuş"])
        df.sort_values(by=["Uçuş Tarihi", "Uçuş Tipi", "Uçuş Numarası"], inplace=True)

        styled_df = df.style.set_properties(**{
            'text-align': 'center',
            'white-space': 'pre-wrap',
            'font-size': '14px'
        }).set_table_styles([
            {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f0f2f6')]}
        ])
    else:
        df = pd.DataFrame(columns=columns)
        styled_df = df.style.set_properties(**{
            'text-align': 'center'
        })

    st.subheader("📋 Tüm Uçuşlar")
    st.dataframe(styled_df, use_container_width=True)


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
