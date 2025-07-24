sayi = int(input("Bir sayi giriniz: "))
faktoriyel = 1
sonuclar = []

for i in range(1,sayi + 1):
    faktoriyel *= i
    sonuclar.append(str(faktoriyel))
print(", ".join(sonuclar))
    

