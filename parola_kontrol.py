parola = input("Bir parola giriniz: ")
uzunluk = len(parola)

uzunluk_dogru = 7 < uzunluk < 31
buyuk_harf_var = any(harf.isupper() for harf in parola)
rakam_var = any(harf.isdigit() for harf in parola)
sembol_var = any(karakter in string.punctuation for karakter in parola)
parola_yok = "parola" not in parola.lower()

if uzunluk_dogru and parola_yok and sembol_var and rakam_var and buyuk_harf_var :
    print("parola geçerli ")
else :
    print("parola gecersiz ")
    if not uzunluk_dogru :
        print("Uzunluğu 7 karakterden fazla, 31 karakterden az olmalı.")
    if not buyuk_harf_var:
        print("En az bir buyuk harf icermeli")
    if not rakam_var:
        print("En az bir rakam icermeli")
    if not sembol_var:
        print("En az bir sembol/noktalama içermeli")
    if not parola_yok:
        print("parola kelimesi içermemeli")
        