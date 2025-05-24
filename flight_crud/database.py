import sqlite3

def connect_db():
    # Veritabanına bağlanma fonksiyonu
    return sqlite3.connect("flights.db")


def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    # Uçuşlar tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flights (
            flight_number TEXT PRIMARY KEY,
            departure TEXT,
            arrival TEXT,
            date TEXT,
            capacity INTEGER,
            eco_seats INTEGER,
            bus_seats INTEGER
        )
    """)

    # Yolcular tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS passengers (
            passenger_id INTEGER PRIMARY KEY AUTOINCREMENT,
            flight_number TEXT,
            name TEXT,
            surname TEXT,
            tck TEXT,
            FOREIGN KEY (flight_number) REFERENCES flights(flight_number)
        )
    """)

    # Buraya checkins tablosunu ekle:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS checkins (
        checkin_id INTEGER PRIMARY KEY AUTOINCREMENT,
        passenger_id INTEGER,
        flight_number TEXT,
        checkin_time TEXT,
        FOREIGN KEY (passenger_id) REFERENCES passengers(passenger_id)
    )
    """)

    conn.commit()
    conn.close()
    print("Veritabanı ve tablolar başarıyla oluşturuldu.")


def drop_flights_table():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS passengers")  # passengers tablosu da varsa sil
    cursor.execute("DROP TABLE IF EXISTS flights")     # flights tablosunu sil

    conn.commit()
    conn.close()
    print("flights ve passengers tabloları başarıyla silindi.")