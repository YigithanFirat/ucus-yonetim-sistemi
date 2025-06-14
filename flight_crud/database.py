import sqlite3

def connect_db():
    # Veritabanına bağlanma fonksiyonu
    return sqlite3.connect("flights.db")


def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flights (
            flight_number TEXT PRIMARY KEY,
            departure TEXT,
            arrival TEXT,
            date TEXT,
            capacity INTEGER,
            eco_seats INTEGER,
            bus_seats INTEGER,
            departure_time TEXT,
            arrival_time TEXT,
            duration INTEGER,
            flight_type TEXT,
            transfer_point TEXT,
            first_departure_time TEXT,
            first_arrival_time TEXT,
            second_departure_time TEXT,
            second_arrival_time TEXT
        )
    """)

    conn.commit()
    conn.close()


def add_new_columns():
    conn = connect_db()
    cursor = conn.cursor()

    # Zaten varsa eklenmeyecek, yoksa ekleniyor
    columns_to_add = [
        "flight_type TEXT",
        "transfer_point TEXT",
        "first_departure_time TEXT",
        "first_arrival_time TEXT",
        "second_departure_time TEXT",
        "second_arrival_time TEXT"
    ]

    for col_def in columns_to_add:
        col_name = col_def.split()[0]
        try:
            cursor.execute(f"ALTER TABLE flights ADD COLUMN {col_def};")
        except sqlite3.OperationalError:
            # Kolon zaten varsa hata verir, bunu yoksay
            pass

    conn.commit()
    conn.close()


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