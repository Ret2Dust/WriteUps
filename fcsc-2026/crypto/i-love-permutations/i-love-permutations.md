# i love permutations

## Contexte

On reçoit le code source d'un serveur Python et un flag chiffré. En se connectant, le serveur :

1. Génère une **clé secrète** `k` de 128 bits (`os.urandom(16)`)
2. Affiche le **flag chiffré** (hex)
3. Nous laisse chiffrer **6 messages** de notre choix, puis se termine

Le flag fait 32 octets. Il est chiffré en deux blocs de 16 octets avec le même algorithme et la même clé.

Pour ce challenge, j'ai du sortir une feuille et un style et ouvrie mes chakras !!!

---

## Comprendre le chiffrement

L'algorithme opère sur des **bits**, pas sur des octets directement. Un message de 16 octets est découpé en deux **branches** de 64 bits : `l` (left) et `r` (right).

On effectue ensuite **101 tours**. Chaque tour fait 4 opérations :

```
1. random.seed(bits_to_branch(l))  ;  random.shuffle(r)
2. random.seed(k)                  ;  random.shuffle(r)
3. random.seed(bits_to_branch(r))  ;  random.shuffle(l)   <== r modifié est utilisé ici
4. random.seed(k)                  ;  random.shuffle(l)
```

`random.shuffle` avec une graine fixe applique une **permutation déterministe** à la liste. Autrement dit, chaque `shuffle` réordonne les 64 bits dans un ordre fixé par la graine.

Notons :
- `P_x` = la permutation déterminée par `seed(x)`
- `Pk` = la permutation déterminée par `seed(k)` ==> **fixe mais inconnue**
- `P_l` = la permutation déterminée par `seed(bits_to_branch(l))` ==> **change selon l**

Un tour complet s'écrit :

```
r  <==  Pk( P_l(r) )
l  <==  Pk( P_r'(l) )    <== r' est le nouveau r, après la première moitié
```

---

## La faille : l = 0 est un point fixe

Voici l'observation clé :

**Mélanger une liste de zéros donne toujours une liste de zéros, quelle que soit la permutation.**

Si on envoie un message avec `l = 0x0000000000000000` (64 bits à zéro), alors :
- `shuffle(l)` ne change rien : l reste à zéro
- Au tour suivant, `l` est encore zéro ==> même permutation appliquée à `r`
- Et ainsi de suite pour les **101 tours**

**Conséquence directe :** avec `l = 0`, la branche `r` subit à chaque tour la même permutation composée :

```
Q₁  =  Pk ∘ P₀
```

où `P₀ = perm(seed = b'\x00'*8)` est entièrement connue (pas de secret), et `Pk` est la permutation secrète liée à la clé.

Après 101 tours :

```
r_final  =  Q₁¹⁰¹ ( r_initial )
```

C'est une **permutation unique Q** appliquée 101 fois au vecteur `r` initial.

---

## Apprendre Q en 6 requêtes

On veut reconstruire la permutation `Q` complète. Elle agit sur 64 positions : pour chaque position de sortie `i`, on veut savoir de quelle position d'entrée elle provient (un nombre entre 0 et 63, soit **6 bits**).

On envoie 6 requêtes avec `l = 0` et des patterns de `r` bien choisis :

| Requête | r[j] = 1 si… | Valeur hex |
|---------|--------------|------------|
| bit 0 | bit 0 de j vaut 1 (positions 1,3,5,…) | `0xaaaaaaaaaaaaaaaa` |
| bit 1 | bit 1 de j vaut 1 (positions 2,3,6,7,…) | `0xcccccccccccccccc` |
| bit 2 | bit 2 de j vaut 1 | `0xf0f0f0f0f0f0f0f0` |
| bit 3 | bit 3 de j vaut 1 | `0x00ff00ff00ff00ff` |
| bit 4 | bit 4 de j vaut 1 | `0x0000ffff0000ffff` |
| bit 5 | bit 5 de j vaut 1 | `0x00000000ffffffff` |

Pour chaque bit de sortie `i` :
- On lit la réponse des 6 requêtes à la position `i`
- On recompose : `source[i] = réponse_0[i] + réponse_1[i]×2 + réponse_2[i]×4 + ...`
- On obtient l'indice d'entrée qui a atterri en position `i`

---

## Retrouver Pk : la racine 101ème

On connaît `Q = Q₁¹⁰¹`. Il faut retrouver `Q₁`, c'est-à-dire calculer la **racine 101ème de la permutation Q**.

Cela marche grâce à une propriété mathématique :

> 101 est un nombre premier. Les permutations sur 64 éléments ont des cycles de longueur au plus 64 < 101. Donc **101 ne divise jamais l'ordre de Q**.

Formellement : `gcd(101, ord(Q)) = 1` est **toujours vrai** pour n = 64.

L'inverse de 101 modulo `ord(Q)` existe donc toujours, et :

```
Q₁  =  Q^( 101⁻¹  mod  ord(Q) )
```

On calcule `ord(Q)` (le ppcm des longueurs de cycles de Q), puis l'inverse modulaire, et enfin on élève Q à cette puissance.

Ensuite, comme `Q₁ = Pk ∘ P₀` (appliquer P₀ puis Pk), on en déduit :

```
Pk[i]  =  P₀⁻¹[ Q₁[i] ]
```

On a retrouvé la permutation secrète `Pk`, qui encode entièrement la clé `k`.

---

## Déchiffrer le flag

Avec `Pk` en main, on peut déchiffrer en inversant les tours dans l'ordre inverse. Chaque tour à l'envers :

```
1. Annuler shuffle(l) avec graine k   ==>  appliquer Pk⁻¹ à l
2. Annuler shuffle(l) avec graine r'  ==>  appliquer P_{r'}⁻¹ à l    (r' = r actuel, post-tour)
3. Annuler shuffle(r) avec graine k   ==>  appliquer Pk⁻¹ à r
4. Annuler shuffle(r) avec graine l   ==>  appliquer P_{l}⁻¹ à r      (l = l restauré)
```

On répète 101 fois et on obtient le plaintext.

---

## Résumé de l'attaque (chosen-plaintext en 6 requêtes)

```
Étape 1 — 6 requêtes oracle
  Envoyer : l = 0x0000000000000000, r = 0xaa…, 0xcc…, 0xf0…, 0x00ff…, 0x0000ffff…, 0x00000000ffff…
  Récupérer : les 6 vecteurs r_chiffré

Étape 2 — Reconstruire Q
  Pour chaque position i (0..63) :
    source[i] = sum( réponse_bit[i] * 2^bit  for bit in 0..5 )
  → on obtient la permutation Q = Q₁¹⁰¹

Étape 3 — Racine 101ème
  ord_Q  = ordre de la permutation Q (ppcm des longueurs de cycles)
  inv101 = pow(101, -1, ord_Q)
  Q₁     = Q^inv101
  Pk     = [P₀⁻¹[Q₁[i]] for i in range(64)]

Étape 4 — Déchiffrement
  Appliquer 101 tours inverses avec Pk⁻¹ sur les deux blocs du flag
  → flag en clair
```

---

## Code complet du solver

Après réécriture j'ai un truc à peu près épuré et lisible.

```python
import random, socket
from math import gcd

N = 64

def bra(b): # bytes to array (of bits)
    bits = []
    for x in b:
        for i in range(8): bits.append((x >> i) & 1)
    return bits

def brb(bits): # bits to bytes
    return bytes(sum((bits[i+j] & 1) << j for j in range(8)) for i in range(0, N, 8))

def gp(s): # generate permutation
    lst = list(range(N)); random.seed(s); random.shuffle(lst); return lst

def cp(p, q): # compose permutation
    return [q[p[i]] for i in range(len(p))]

def pp(p, e):
    r = list(range(len(p))); b = p[:]
    while e:
        if e & 1: r = cp(r, b)
        b = cp(b, b); e >>= 1
    return r

def po(p): # permutation order
    vis = [False]*len(p); o = 1
    for i in range(len(p)):
        if not vis[i]:
            cl = 0; j = i
            while not vis[j]: vis[j] = True; j = p[j]; cl += 1
            o = o * cl // gcd(o, cl)
    return o

def ip(p): # inverse permutation
    inv = [0]*len(p)
    for i, x in enumerate(p): inv[x] = i
    return inv

def ap(p, l): # apply permutation
    return [l[p[i]] for i in range(len(l))]

def recover_Pk(resps):
    qo = [bra(ct[8:]) for ct in resps]
    Q  = [sum(qo[b][i] * (1 << b) for b in range(6)) for i in range(64)]
    P0 = gp(bytes(8)); oq = po(Q)
    Q1 = pp(Q, pow(101, -1, oq))
    P0i = ip(P0)
    return [P0i[Q1[i]] for i in range(64)]

def decrypt(ct, Pk):
    Pi = ip(Pk); l = bra(ct[:8]); r = bra(ct[8:])
    for _ in range(101):
        l = ap(Pi, l);  l = ap(ip(gp(brb(r))), l)
        r = ap(Pi, r);  r = ap(ip(gp(brb(l))), r)
    return brb(l) + brb(r)

# -- connexion --
HOST, PORT = "challenges.fcsc.fr", 2153
QUERIES = []
for bit in range(6):
    rb = [(1 if (j >> bit) & 1 else 0) for j in range(64)]
    QUERIES.append((bytes(8) + brb(rb)).hex())

def recv_until(s, marker, timeout=10):
    buf = b""
    s.settimeout(timeout)
    try:
        while marker not in buf:
            chunk = s.recv(4096)
            if not chunk: break
            buf += chunk
    except socket.timeout: pass
    return buf

s = socket.create_connection((HOST, PORT), timeout=15)
banner_raw = recv_until(s, b">>>")
flag_ct = None
for line in banner_raw.decode(errors="replace").splitlines():
    if "Flag hex" in line:
        flag_ct = bytes.fromhex(line.split()[-1])
        break

responses = []
for i, q in enumerate(QUERIES):
    s.sendall((q + "\n").encode())
    raw = recv_until(s, b">>>") if i < 5 else recv_until(s, b"Encryption:", timeout=5) + recv_until(s, b"\n", timeout=3)
    for line in raw.decode(errors="replace").splitlines():
        if line.startswith("Encryption:"):
            responses.append(bytes.fromhex(line.split()[-1]))
            break
s.close()

Pk   = recover_Pk(responses)
flag = bytes(decrypt(flag_ct[:16], Pk)) + bytes(decrypt(flag_ct[16:], Pk))
print(flag.decode())
```