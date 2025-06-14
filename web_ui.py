import streamlit as st
import re
from datetime import datetime, date
from flight_crud.flight_manager import calculate_duration_minutes, calculate_flight_duration, calculate_duration_between, create_flight, list_flights_by_date, list_all_flights, delete_flight
from booking.checkin import check_in
from booking.pdf_ticket import generate_pdf_ticket
from booking.passenger_manager import add_passenger, list_passengers, delete_passenger
from flight_crud.database import create_tables
from utils.validation import is_valid_name, is_valid_phone, is_valid_date

st.set_page_config(page_title="Uçuş Yönetim Sistemi")
st.title("🛫 Uçuş Yönetim Sistemi")

create_tables()



menu =  st.sidebar.selectbox("İşlem Seçin", [
    "Uçuş Oluştur",
    "Tüm Uçuşları Listele",
    "Uçuş Tarihine Göre Listele",
    "Yolcu Ekle",
    "Yolcuları Listele",
    "Yolcu Sil",
    "Check-in Yap",
    "PDF Bilet Oluştur",
    "Uçuş Sil"
])

flight_type = None
departure_time = None
arrival_time = None
transfer_point = None
first_departure_time = None
first_arrival_time = None
second_departure_time = None
second_arrival_time = None
duration = None


if menu == "Uçuş Oluştur":
    flight_no = st.text_input("Uçuş Numarası")
    origin = st.text_input("Kalkış Noktası")
    destination = st.text_input("Varış Noktası")
    date_input = st.text_input("Tarih (GG.AA.YYYY)", placeholder="Örn: 30.05.2025")

    flight_type = None
    departure_time = None
    arrival_time = None
    transfer_point = None
    first_departure_time = None
    first_arrival_time = None
    second_departure_time = None
    second_arrival_time = None

    flight_type = st.radio("Uçuş Tipi Seçiniz:", ("Direk Uçuş", "Aktarmalı Uçuş"))

    if flight_type == "Direk Uçuş":
        departure_time = st.text_input("Kalkış Saati (SS:DD)", placeholder="Örn: 14:30")
        arrival_time = st.text_input("Varış Saati (SS:DD)", placeholder="Örn: 16:45")

        if departure_time and arrival_time:
            try:
                datetime.strptime(departure_time, "%H:%M")
                datetime.strptime(arrival_time, "%H:%M")
                
                duration_str = calculate_flight_duration(departure_time, arrival_time)
                st.success(f"Uçuş Süresi: {duration_str}")
            except ValueError:
                st.error("Lütfen saatleri 'SS:DD' formatında giriniz. Örn: 14:30")
            except Exception as e:
                st.error(f"Süre hesaplanamadı! Hata: {str(e)}")
    else:
        transfer_point = st.text_input("Aktarma Noktası")
        st.write("1. Uçuş için saatleri giriniz:")
        first_departure_time = st.text_input("1. Uçuş Kalkış Saati (SS:DD)")
        first_arrival_time = st.text_input("1. Uçuş Varış Saati (SS:DD)")
        st.write("2. Uçuş için saatleri giriniz:")
        second_departure_time = st.text_input("2. Uçuş Kalkış Saati (SS:DD)")
        second_arrival_time = st.text_input("2. Uçuş Varış Saati (SS:DD)")

        if all([first_departure_time, first_arrival_time, second_departure_time, second_arrival_time]):
            try:
                fmt = "%H:%M"
                from datetime import datetime, timedelta

                def get_minutes(t1, t2):
                    dt1 = datetime.strptime(t1, fmt)
                    dt2 = datetime.strptime(t2, fmt)
                    if dt2 < dt1:
                        dt2 += timedelta(days=1)
                        delta = dt2 - dt1
                        return delta.seconds // 60

                first_flight_min = calculate_flight_duration(first_departure_time, first_arrival_time)
                second_flight_min = calculate_flight_duration(second_departure_time, second_arrival_time)
                total_min = first_flight_min + second_flight_min

                total_hours = total_min // 60
                total_minutes = total_min % 60
                st.write(f"Toplam Uçuş Süresi: {total_hours} saat {total_minutes} dakika")
                duration = f"{total_hours} saat {total_minutes} dakika"
            except Exception:
                st.error("Toplam uçuş süresi hesaplanamadı!")
                duration = None
            else:
                duration = None

    plane_capacity_str = st.text_input("Uçak Kapasitesi")
    economy_seats_str = st.text_input("Ekonomi Koltuk Sayısı")
    business_seats_str = st.text_input("Business Koltuk Sayısı")

    if st.button("Uçuşu Oluştur"):
        if not flight_no or not origin or not destination or not date_input or not plane_capacity_str or not economy_seats_str or not business_seats_str:
            st.error("Lütfen tüm alanları doldurun!")
            st.stop()
        if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", date_input):
            st.error("Tarih formatı yanlış! Lütfen GG.AA.YYYY şeklinde girin.")
            st.stop()
        if not flight_type:
            st.error("Lütfen uçuş tipi seçin!")
            st.stop()

        time_pattern = r"^(?:[01]\d|2[0-3]):[0-5]\d$"
        if flight_type == "Direk Uçuş":
            if not departure_time or not arrival_time:
                st.error("Lütfen kalkış ve varış saatlerini girin!")
                st.stop()
            if not re.match(time_pattern, departure_time):
                st.error("Kalkış saati formatı yanlış! Lütfen SS:DD şeklinde girin.")
                st.stop()
            if not re.match(time_pattern, arrival_time):
                st.error("Varış saati formatı yanlış! Lütfen SS:DD şeklinde girin.")
                st.stop()
            duration = calculate_flight_duration(departure_time, arrival_time)
        else:
            if not transfer_point:
                st.error("Lütfen aktarma noktası girin!")
                st.stop()
            if not first_departure_time or not first_arrival_time or not second_departure_time or not second_arrival_time:
                st.error("Lütfen tüm aktarmalı uçuş saatlerini girin!")
                st.stop()
            for t in [first_departure_time, first_arrival_time, second_departure_time, second_arrival_time]:
                if not re.match(time_pattern, t):
                    st.error(f"'{t}' saat formatı yanlış! Lütfen SS:DD şeklinde girin.")
                    st.stop()
            try:
                duration = (
                    calculate_flight_duration(first_departure_time, first_arrival_time) +
                    calculate_flight_duration(second_departure_time, second_arrival_time)
                )
            except:
                st.error("Toplam uçuş süresi hesaplanamadı!")
                st.stop()

        try:
            plane_capacity = int(plane_capacity_str)
            economy_seats = int(economy_seats_str)
            business_seats = int(business_seats_str)

            if plane_capacity < 1:
                st.error("Uçak kapasitesi 1 veya daha fazla olmalıdır!")
                st.stop()
            if economy_seats < 0 or business_seats < 0:
                st.error("Koltuk sayıları negatif olamaz!")
                st.stop()
            if economy_seats == 0 and business_seats == 0:
                st.error("En az bir koltuk sayısı 1 veya daha fazla olmalıdır!")
                st.stop()
            if economy_seats > plane_capacity:
                st.error("Ekonomi koltuk sayısı, uçak kapasitesinden fazla olamaz!")
                st.stop()
            if business_seats > plane_capacity:
                st.error("Business koltuk sayısı, uçak kapasitesinden fazla olamaz!")
                st.stop()
            if economy_seats + business_seats > plane_capacity:
                st.error("Toplam koltuk sayısı, uçak kapasitesini aşamaz!")
                st.stop()

            date_obj = datetime.strptime(date_input, "%d.%m.%Y").date()
            today = date.today()
            if date_obj < today:
                st.error("Geçmiş tarih girilemez!")
                st.stop()

            formatted_date = date_obj.strftime("%Y-%m-%d")

            success, message = create_flight(
                flight_no, origin, destination, formatted_date,
                plane_capacity, economy_seats, business_seats,
                departure_time, arrival_time, duration,
                flight_type, transfer_point,
                first_departure_time, first_arrival_time,
                second_departure_time, second_arrival_time
            )
            if success:
                st.success(message)
            else:
                st.error(message)

        except ValueError:
            st.error("Kapasite ve koltuk sayıları pozitif tam sayı olmalıdır!")
        except Exception as e:
            st.error(f"Hata: {e}")


elif menu == "Tüm Uçuşları Listele":
    flights_df = list_all_flights()
    if flights_df is not None and not flights_df.empty:
        st.table(flights_df)
    else:
        st.warning("Veritabanında hiç uçuş yok.")

elif menu == "Uçuş Tarihine Göre Listele":
    st.subheader("📅 Uçuş Tarihine Göre Listele")
    date_input = st.text_input("Tarih (YYYY-MM-DD)", placeholder="örn. 2025-06-01")

    if st.button("Listele"):
        if not date_input:
            st.error("Lütfen bir tarih girin.")
        else:
            try:
                from datetime import datetime
                parsed_date = datetime.strptime(date_input, "%Y-%m-%d").date()

                flights = list_flights_by_date(parsed_date.strftime("%Y-%m-%d"))

                if flights:
                    for flight in flights:
                        st.markdown(f"""
🚀 **Uçuş Numarası:** `{flight[0]}`
- 🛫 **Kalkış:** {flight[1]} ➜ **Varış:** {flight[2]}
- 🗓️ **Tarih:** {flight[3]} | 👥 **Kapasite:** {flight[4]}
- 💺 Ekonomi: {flight[5]} | 🛋️ Business: {flight[6]}
- 🕒 **Uçuş Tipi:** {flight[10]}
    - 📍 Aktarma Noktası: `{flight[11] if flight[11] else 'Yok'}`
    - Direkt Saatler: {flight[7] or '-'} ➜ {flight[8] or '-'}
    - Süre: ⏱️ {flight[9] or 'Hesaplanamadı'}
    - 1. Uçuş: {flight[12] or '-'} ➜ {flight[13] or '-'}
    - 2. Uçuş: {flight[14] or '-'} ➜ {flight[15] or '-'}
---
                        """)
                else:
                    st.warning(f"{date_input} tarihine ait herhangi bir uçuş bulunamadı.")
            except ValueError:
                st.error("Tarih formatı hatalı! Lütfen YYYY-MM-DD şeklinde girin.")


elif menu == "Yolcu Ekle":
    tckn = st.text_input("TCKN")
    name = st.text_input("Ad Soyad")
    phone = st.text_input("Telefon")
    flight_no = st.text_input("Uçuş Numarası")
    if st.button("Yolcu Ekle"):
        if is_valid_name(name) and is_valid_phone(phone):
            add_passenger(tckn, name, phone, flight_no)
            st.success("Yolcu eklendi!")
        else:
            st.error("Geçersiz isim veya telefon")

elif menu == "Yolcuları Listele":
    passengers = list_passengers()
    st.table(passengers)

elif menu == "Yolcu Sil":
    tckn = st.text_input("Silinecek Yolcunun TCKN'si")
    if st.button("Yolcuyu Sil"):
        delete_passenger(tckn)
        st.success("Yolcu silindi")

elif menu == "Check-in Yap":
    tckn = st.text_input("TCKN")
    if st.button("Check-in"):
        check_in(tckn)
        st.success("Check-in tamamlandı")

elif menu == "PDF Bilet Oluştur":
    tckn = st.text_input("TCKN")
    if st.button("Bileti Oluştur"):
        generate_pdf_ticket(tckn)
        st.success("PDF bilet oluşturuldu")

elif menu == "Uçuş Sil":
    flight_no = st.text_input("Silinecek Uçuş Numarası")
    if st.button("Uçuşu Sil"):
        delete_flight(flight_no)
        st.success("Uçuş silindi")