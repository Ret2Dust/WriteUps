# Code Breaker (FCSC)

## TL;DR

Mon premier réflexe lorsque j'ai ouvert le fichier était d'aller me coucher ;) et j'ai eu raison. Donc pourquoi pas soigné mon writeup.

Sans transition ...

Le challenge chiffre un flag avec AES-256. La clé est construite bit par bit à partir de 256 matrices : un bit vaut `0` si la matrice est un code **GRS** (Generalized Reed-Solomon), `1` si elle est **aléatoire**. Il suffit de distinguer les deux types grâce au **produit de Schur** pour retrouver la clé et déchiffrer le flag.

---

## Description du challenge

### Ce que fait le code source

```
Pour i = 0 à 255 :
    Tirer un bit b aléatoire
    Si b = 0 → générer une matrice génératrice GRS (k×n)
    Si b = 1 → générer une matrice aléatoire (k×n)
    Appliquer un masquage S·G·P (McEliece-like)
    Stocker la matrice publique C dans output.txt
```

La **clé AES** est l'entier 256 bits formé par la concaténation des 256 bits `b`.

### Paramètres

| Paramètre | Valeur |
|-----------|--------|
| Corps fini | `GF(q)`, `q = 2³² − 5` |
| Dimension du code | `k = 20` |
| Longueur du code | `n = 64` |
| Nombre de matrices | 256 |
| Chiffrement | AES-256-CBC |

---

## Analyse de la vulnérabilité

### Qu'est-ce qu'un code GRS ?

Un **code GRS** `[n, k]` est engendré par une matrice de la forme :

```
G[i, j] = v[j] · a[j]^i    (i = 0..k-1, j = 0..n-1)
```

où `a` est un vecteur de *n* éléments distincts et `v` un vecteur de scalaires non nuls. C'est essentiellement une **matrice de Vandermonde pondérée**.

Les codes GRS ont des **propriétés algébriques très rigides** qui les distinguent des matrices aléatoires.

### Le produit de Schur

Le **produit de Schur** (ou produit étoile) de deux codes `C₁` et `C₂` est le code engendré par tous les produits terme à terme :

```
C₁ ⋆ C₂ = span{ c₁ ⊙ c₂  |  c₁ ∈ C₁, c₂ ∈ C₂ }
```

Pour un code `C` de dimension `k` et longueur `n`, on note `C² = C ⋆ C`.

En pratique, `C²` est engendré par les `k(k+1)/2` produits terme à terme de toutes les paires de lignes de la matrice génératrice.

### La propriété clé : le rang du produit de Schur

| Type de matrice | `dim(C²)` théorique | Rang observé (k=20, n=64) |
|-----------------|--------------------|-----------------------------|
| **GRS** | `min(2k − 1, n) = 39` | **39** ✅ |
| **Aléatoire** | `min(k², n) = 64` | **64** ✅ |

**Pourquoi ?**

- Un code GRS satisfait la propriété : `GRS(a, v)² = GRS(a, v⊙v)`, qui reste un code GRS de dimension `2k-1`. La dimension ne peut donc pas dépasser `2k-1`.
- Une matrice aléatoire n'a aucune structure : ses produits de Schur engendrent un espace de pleine dimension `min(k², n)`.

Ici `2k-1 = 39` et `k² = 400 > n = 64`, donc la séparation est **maximale et sans ambiguïté**.

---

## Construction de l'attaque

### Étape 1 – Calculer la matrice du produit de Schur

Pour chaque matrice `C` (de taille `k × n`), on forme la matrice `S` de taille `k(k+1)/2 × n` :

```python
rows = []
for i in range(k):
    for j in range(i, k):
        rows.append(C[i] * C[j])   # multiplication terme à terme dans GF(q)
S = Fq(rows)
```

### Étape 2 – Calculer le rang

On effectue une **élimination de Gauss** sur `S` dans `GF(q)` :

```python
M = S.row_reduce()
rank = sum(1 for row in M if np.any(row != 0))
```

### Étape 3 – Décider le bit

```
rank == 39  →  b = 0  (matrice GRS)
rank == 64  →  b = 1  (matrice aléatoire)
```

### Étape 4 – Reconstruire la clé et déchiffrer

```python
key_int = sum(b << i for i, b in enumerate(key_bits))
key = key_int.to_bytes(32)

E = AES.new(key, AES.MODE_CBC, iv=iv)
flag = unpad(E.decrypt(c), 16)
```

---

## Script de résolution complet

```python
import json
import numpy as np
from galois import GF
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def schur_rank(Fq, C_flat, k, n):
    C = Fq(np.array(C_flat, dtype=int).reshape(k, n))
    rows = []
    for i in range(k):
        for j in range(i, k):
            rows.append((C[i] * C[j]).tolist())
    S = Fq(rows)
    M = S.row_reduce()
    return sum(1 for row in M if np.any(row != 0))

with open("output.txt") as f:
    data = json.load(f)

q, k, n = data["params"]
Fq = GF(q)

key_bits = []
for i in range(256):
    r = schur_rank(Fq, data[str(i)], k, n)
    bit = 1 if r > 50 else 0   # seuil entre 39 et 64
    key_bits.append(bit)

key = sum(b << i for i, b in enumerate(key_bits)).to_bytes(32)

enc = data["enc"]
E   = AES.new(key, AES.MODE_CBC, iv=bytes.fromhex(enc["iv"]))
flag = unpad(E.decrypt(bytes.fromhex(enc["c"])), 16)
print(flag.decode())
```

```bash
$ time python code-breaker.py
FCSC{949f94d858ef6ad1333164d796a0d777fd82f9155ece7d6fad68c0b992f0e7af}

real    0m25.399s
user    0m26.588s
sys     0m0.127s
```

---

## Résultats

Tous les rangs observés sont soit **exactement 39** soit **exactement 64** :

```
[  0] rank=39 → bit=0   (GRS)
[  1] rank=39 → bit=0   (GRS)
[  2] rank=39 → bit=0   (GRS)
[  3] rank=64 → bit=1   (aléatoire)
...
[255] rank=64 → bit=1   (aléatoire)
```

Aucun cas ambigu. La clé est récupérée en totalité.

---

## Flag

```
FCSC{949f94d858ef6ad1333164d796a0d777fd82f9155ece7d6fad68c0b992f0e7af}
```

---

## Résumé

```
output.txt
    │
    ├─ 256 matrices C (k×n) dans GF(q)
    │
    ▼
Pour chaque C :
    Calculer C ⋆ C  →  matrice (k(k+1)/2 × n)
    Rang dans GF(q) via élimination de Gauss
         │
         ├── rang = 39  →  b = 0  (code GRS)
         └── rang = 64  →  b = 1  (matrice aléatoire)
    │
    ▼
Clé AES-256 reconstruite bit par bit
    │
    ▼
AES-256-CBC déchiffrement → FLAG
```

---

## Références

- **Sidelnikov & Shestakov (1992)** – Attaque originale sur McEliece basé sur GRS
- **Wieschebrink (2010)** – *Cryptanalysis of the Niederreiter public key scheme based on GRS subcodes*
- **Couvreur, Márquez-Corbella, Pellikaan (2014)** – *Cryptanalysis of McEliece over GRS codes via Schur product*