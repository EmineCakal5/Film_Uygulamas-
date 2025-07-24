string = input("Bir sayı stringi giriniz: ")
sonuc = string[0]

for i in range(1,len(string)):
    if int(string[i-1]) % 2 == 1 and int(string[i]) % 2 == 1:
        sonuc += '-'
    sonuc += string[i]
    i += 1

print(sonuc)