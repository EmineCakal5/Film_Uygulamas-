import re

isim = input("İsim girişi yapınız: ")
soyisim = input("Soyisim girişi yapınız: ")

isim_dogru = isim[0].isupper()
soyad_dogru = soyisim[0].isupper()

if isim_dogru and soyad_dogru:
    print("İsminiz geçerli")
else:
    print("İsminiz geçersiz")