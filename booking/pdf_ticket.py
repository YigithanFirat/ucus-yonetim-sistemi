from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os
import sqlite3

def generate_pdf_ticket(passenger_id):
    conn = sqlite3.connect("flights.db")
    cursor = conn.cursor()

    # Yolcuyu veritabanından al
    cursor.execute("SELECT * FROM passengers WHERE passenger_id = ?", (passenger_id,))
    passenger = cursor.fetchone()

    if not passenger:
        print("Geçersiz yolcu ID.")
        conn.close()
        return

    # Yolcu bilgileri
    passenger_name = passenger[2]
    passenger_surname = passenger[3]
    flight_number = passenger[1]
    tck = passenger[4]

    # Uçuş tarihini al
    cursor.execute("SELECT date FROM flights WHERE flight_number = ?", (flight_number,))
    flight_info = cursor.fetchone()
    flight_date = flight_info[0] if flight_info else "Tarih bulunamadı"

    # PDF dosyasının adı
    pdf_filename = f"{passenger_name}_{passenger_surname}_{flight_number}_ticket.pdf"

    # Font dosyasının yolu (aynı klasörde DejaVuSans.ttf olmalı)
    font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")

    # Türkçe karakter destekli fontu kayıt et
    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))

    # PDF oluşturma
    c = canvas.Canvas(pdf_filename, pagesize=letter)

    # Başlık
    c.setFont("DejaVuSans", 16)
    c.drawString(100, 750, "Uçuş Bileti")

    # Yolcu Bilgileri
    c.setFont("DejaVuSans", 12)
    c.drawString(100, 700, f"Yolcu: {passenger_name} {passenger_surname}")
    c.drawString(100, 680, f"Uçuş No: {flight_number}")
    c.drawString(100, 660, f"TCK: {tck}")

    # Bilet bilgileri
    c.drawString(100, 640, f"Uçuş Bilgisi: {flight_number} - {passenger_name} {passenger_surname}")
    c.drawString(100, 620, f"Tarih: {flight_date} - {flight_number} - Rezervasyon Başarıyla Gerçekleşti")

    # PDF'yi kaydet
    c.save()

    conn.close()
    print(f"Bilet PDF olarak kaydedildi: {pdf_filename}")