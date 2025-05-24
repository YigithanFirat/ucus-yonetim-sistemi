import re

# İsim ve soyisim için doğrulama (Yalnızca harf ve boşluk kabul eder)
def is_valid_name(name):
    return bool(re.match("^[A-Za-zğüşöçıİĞÜŞÖÇ ]+$", name))

# TCK numarası doğrulama fonksiyonu (bu zaten `tck_validation.py` dosyasında vardı)
def is_valid_tck(tck):
    # TCK numarası sadece rakamlardan oluşmalı ve 11 haneli olmalı
    if not tck.isdigit() or len(tck) != 11:
        return False

    # İlk hane 0 olamaz
    if tck[0] == '0':
        return False

    # TCK numarasının doğruluğunu kontrol etmek için algoritma
    digits = [int(digit) for digit in tck]

    # 1. Adım: İlk 10 hanenin doğruluğunu kontrol et
    check1 = sum(digits[i] for i in range(0, 9, 2)) * 7
    check2 = sum(digits[i] for i in range(1, 8, 2)) * 9
    check_sum = check1 + check2
    if check_sum % 10 != digits[9]:
        return False

    # 2. Adım: Son haneyi kontrol et
    check3 = sum(digits[i] for i in range(0, 10)) % 10
    if check3 != digits[10]:
        return False

    return True

# Geçerli bir telefon numarası olup olmadığını kontrol et
def is_valid_phone(phone):
    return bool(re.match("^[0-9]{10}$", phone))

# Geçerli bir tarih formatı (gg.aa.yyyy) olup olmadığını kontrol et
def is_valid_date(date):
    return bool(re.match("^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.\d{4}$", date))
