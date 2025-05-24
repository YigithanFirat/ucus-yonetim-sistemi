import streamlit as st
from flight_crud.flight_manager import create_flight, list_flights_by_date, list_all_flights, delete_flight
from booking.checkin import check_in
from booking.pdf_ticket import generate_pdf_ticket
from booking.passenger_manager import add_passenger, list_passengers, delete_passenger
from flight_crud.database import create_tables
from utils.validation import is_valid_name, is_valid_phone, is_valid_date

st.set_page_config(page_title="Uçuş Yönetim Sistemi")
st.title("🛫 Uçuş Yönetim Sistemi")

create_tables()


menu = st.sidebar.selectbox("İşlem Seçin", [
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

if menu == "Uçuş Oluştur":
    flight_no = st.text_input("Uçuş Numarası")
    origin = st.text_input("Kalkış Noktası")
    destination = st.text_input("Varış Noktası")
    date = st.text_input("Tarih (YYYY-MM-DD)")
    if st.button("Uçuşu Oluştur"):
        
            create_flight(flight_no, origin, destination, date,200,100,100)
            st.success("Uçuş oluşturuldu!")
        
      

elif menu == "Tüm Uçuşları Listele":
    flights_df = list_all_flights()
    if not flights_df.empty:
        st.table(flights_df)
    else:
        st.warning("Veritabanında hiç uçuş yok.")


elif menu == "Uçuş Tarihine Göre Listele":
    date = st.text_input("Tarih (YYYY-MM-DD)")
    if st.button("Listele"):
        if is_valid_date(date):
            flights = list_flights_by_date(date)
            st.table(flights)
        else:
            st.error("Geçersiz tarih")

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