# Writeup — Frankenshtein (FCSC)

## Premier contact

En ouvrant `frankenshtein.py`, on tombe sur un fichier de **625 lignes** dont environ les 570 premières sont des fonctions avec des noms qui ressemblent à des hashs aléatoires :

```python
def fcsc_qiLjdoEUA7gmHYxmJxmReh7icLYMpLrsiJM(L): return (65 + sum(a*x for a,x in zip(L,[75,213,67,...]))) % 256
def fcsc_hPcawhvjJ4hCcvErPWUMgKEoYzVEVVKUogL(L): return (90 + sum(a*x for a,x in zip(L,[66,130,20,...]))) % 256
...
```

Chacune prend une liste `L` et renvoie un résidu mod 256. À ce stade, on ne sait pas lesquelles vont être appelées ni pourquoi. On garde ça en tête et on continue.

Tout en bas, la logique de vérification :

```python
password = input(">>> ")
L = list(password.encode())
if {0} == set([
    _(bytes(x ^ L[0] for x in bytes.fromhex("31242a33...")), L[32:]),
    _(bytes(x ^ L[1] for x in bytes.fromhex("180615...")), L[32:]),
    ...
]):
    print("Congrats!")
else:
    print("Nope!")
```

Le mot de passe est attendu en deux blocs : `L[0:32]` et `L[32:]`. Pour valider, toutes les expressions dans le `set()` doivent renvoyer `0`.

## Le mécanisme d'appel `_()`

La fonction `_()` est le cœur de l'obfuscation :

```python
def _(f, *args):
    try:
        return eval("fcsc_" + f.decode())(*args)
    except NameError as e:
        z = s(r"[^:]+: ['\"](.+?)['\"]", t(e)[-1]).group(1)
        return eval(f"{z}({','.join(repr(_) for _ in args)})")
```

Elle reçoit `f` (un `bytes`) et essaie d'appeler `fcsc_` + `f.decode()`. Si la fonction n'existe pas, elle récupère le nom exact depuis le message d'erreur Python via regex sur le traceback, et l'appelle directement. C'est un dispatch dynamique qui exploite les exceptions comme mécanisme de routage.

Ce qui est crucial: **`f` est construit dynamiquement par XOR** avec `L[i]`:

```python
bytes(x ^ L[i] for x in bytes.fromhex(b[i]))
```

Donc `L[i]` est une clé XOR qui déchiffre `b[i]` en un nom de fonction. La bonne valeur de `L[i]` est celle qui produit un nom de fonction **valide et existant** parmi les 570 définies.

## Étape 1 - `L[0:32]` ET les fonctions appelées

Pour chaque position `i` l'objectif est de trouver une valeur `L[i]` telle que :

* le XOR avec `b[i]` donne une chaîne valide
* cette chaîne correspond à un nom de fonction existant

Le script `frank.py` brute-force les valeurs ASCII imprimables :

```python
for i in range(32, 127):          # k = candidat pour L[i]
    word = []
    for x in bytes.fromhex(a):    # a = b[i] (hex encodé)
        y = x ^ i
        if (y >= 48) and (y < 123) and (y not in symbols):
            word.append(y)
        else:
            word = []
            break
    if word != []:
        candidates.append(i)
```

Le filtrage est basé sur les contraintes des identifiants Python :

* caractères alphanumériques
* underscore autorisé implicitement

En pratique, chaque position n’admet qu’un seul candidat valide (ou très peu).

Une fois les candidats listés, on essaie les combinaisons avec `itertools.product` en lançant `frankenshtein.py`. La bonne combinaison est détectée quand la sortie est `">>> Nope!\n"`. Ce qui valide la première moitié (`L[0:32]`).

Une fois `L[0:32]` trouvé, on peut reconstruire:

```python
bytes(x ^ L[i] for x in bytes.fromhex(b[i]))
```

Ce qui donne directement le nom exact de la fonction appelée. On identifie ainsi les 32 fonctions réellement utilisées parmi les 570 disponibles.

## Étape 2 - résoudre le système linéaire

Maintenant qu'on sait quelles 32 fonctions sont appelées, on extrait leurs constantes et coefficients. Chacune a la forme :

```
(CONSTANTE + Σ coefficients[j] * L[32+j]) mod 256 == 0
```

`enshtein.py` modélise ce système avec **Z3** en utilisant l'arithmétique bit-vector sur 8 bits, ce qui gère nativement le modulo 256 :

```python
from z3 import *

L = [BitVec(f'x{i}', 8) for i in range(32)]
s = Solver()

for (cst, coeffs) in equations:
    expr = BitVecVal(cst, 8)
    for a, x in zip(coeffs, L):
        expr = expr + BitVecVal(a, 8) * x
    s.add(expr == BitVecVal(0, 8))

if s.check() == sat:
    m = s.model()
    solution = [m[L[i]].as_long() for i in range(32)]
    print(bytes(solution).decode())
```

Z3 trouve une assignation satisfaisante pour les 32 inconnues. La vérification intégrée confirme que chaque équation renvoie bien 0 mod 256.

## Résultat

```
L[0:32]  --> trouvé par frank.py  (XOR + brute-force + subprocess)
L[32:]   --> trouvé par test.py   (Z3, système linéaire mod 256)
flag     --> FCSC{L[0:32] + L[32:]}
```
