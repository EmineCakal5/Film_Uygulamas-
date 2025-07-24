def faktoriyel_recursive(n, liste=None):
    if liste is None:
        liste = []
    if n == 0 or n == 1:
        liste.append(1)
        return 1, liste
    else :
        onceki, liste = faktoriyel_recursive(n - 1, liste)
        simdiki = n * onceki
        liste.append(simdiki)
        return simdiki, liste