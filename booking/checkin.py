import sqlite3

def check_in(passenger_id):
    conn = sqlite3.connect("flights.db")
    cursor = conn.cursor()

    # Yolcu var mı kontrolü
    cursor.execute("SELECT * FROM passengers WHERE passenger_id = ?", (passenger_id,))
    passenger = cursor.fetchone()

    if not passenger:
        print("Check-in başarısız: Yolcu bulunamadı.")
        conn.close()
        return False

    # Zaten check-in yapmış mı?
    cursor.execute("SELECT * FROM checkins WHERE passenger_id = ?", (passenger_id,))
    if cursor.fetchone():
        print("Bu yolcu zaten check-in yapmış.")
        conn.close()
        return False

    # Check-in kaydı ekleniyor
    cursor.execute("INSERT INTO checkins (passenger_id, flight_number) VALUES (?, ?)",
                   (passenger_id, passenger[1]))
    
    conn.commit()
    conn.close()

    print(f"{passenger[2]} {passenger[3]} için check-in işlemi tamamlandı.")
    return True