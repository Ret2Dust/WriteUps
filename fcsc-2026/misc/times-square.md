# Times Square

## Etape 1

En se connectant au serveur SSH :

```bash
ssh -o StrictHostKeyChecking=no -p 2051 challenges.fcsc.fr
```

On obtient un TUI qui affiche :

```
┌ FCSC ACCESS TERMINAL ──────────────────────────────────────┐
│You've been waiting 10 seconds for a flag to appear...      │
│Maybe your TTY is too small? 🦕                              │
│                                                            │
│uint16_t X = 209, Y = 51, t = 10                            │
└ Press q to exit ───────────────────────────────────────────┘
```

Trois observations importantes :

- **X** et **Y** correspondent à la taille réelle du terminal (colonnes × lignes), lue en temps réel.
- **t** est un compteur en secondes qui s'incrémente depuis la connexion (ce n'est pas un timeout).
- Les variables sont typées `uint16_t` (entier non signé 16 bits, valeur max = 65535).

---

## Etape 2 

Le message *"Maybe your TTY is too small?"* avec le dinosaure 🦕 suggère clairement d'agrandir le terminal. J'ai forcé taille avec la commande `stty` avant la connexion. J'ai doublé la taille:

```bash
(stty cols 418 rows 102 && ssh -o StrictHostKeyChecking=no -p 2051 challenges.fcsc.fr)
```

Le serveur détecte les nouvelles dimensions en live (X=418, Y=102) et change de message :

> *"Wow you have laaaaarge screen! Impressive!! 🤯  
> Maybe it is time to make me bit taller?"*

J'ai donc encore doublé la taille de Y

```bash
(stty cols 418 rows 204 && ssh -o StrictHostKeyChecking=no -p 2051 challenges.fcsc.fr)
```

Cette fois, le serveur affiche enfin la condition à satisfaire.

```bash
┌ FCSC ACCESS TERMINAL ────────────────────────────────────────┐                                                                                                                                                 │So much screen space, you seemserious                                                                                                                                                                                                          about                                                                                                                                                                                                            getting                                                                                                                                                                                                          the                                                                                                                                                                                                              flag!│                                                                                                                                                                            │Pass the following C conditionto                                                                                                                                                                                                               print                                                                                                                                                                                                            the                                                                                                                                                                                                              flag:                                                                                                                                                                             │X + Y + t = 42 && X > 300 && Y200                                                                                                                                                                               └uPress_q to=exit,─────────────────────────────────────────────┘
```

---

## Etape 3

Le TUI affiche la condition, mais le rendu est corrompu par le formatage du terminal (quoi que il y a pire). Après quelques tentatives de reconstruction, on obtient:

```c
X + Y + t == 42 && X > 300 && Y > 200
```

---

## Etape 4

Le type `uint16_t` affiché dans le challenge n'est pas un détail cosmétique. En C, l'arithmétique sur des `uint16_t` overflow à 65536 :

```c
(uint16_t)(65535 + 1) == 0
```

La condition **impossible** devient solvable :

```
(X + Y + t) % 65536 == 42
==> X + Y + t == 65536 + 42 == 65578
```

Il faut donc trouver X et Y tels que leur somme, plus t secondes d'attente, atteigne 65578.

---

## Etape 5

On veut maximiser X + Y pour minimiser le temps d'attente, en respectant toutes les contraintes :

```
X + Y < 65578      (pour que t > 0 complète)
X > 300            
Y > 200            
```

Solution choisie :

```
X = 32700
Y = 32870
X + Y = 65570
t nécessaire = 65578 - 65570 = 8 secondes
```

---

## Etape 6

Commande finale :

```bash
(stty cols 32700 rows 32870 && ssh -o StrictHostKeyChecking=no -p 2051 challenges.fcsc.fr)
```

Après connexion, attendre 
8 secondes sans rien faire. Le serveur évalue `(X + Y + t) % 65536` à chaque tick et vérifie toutes les contraintes. Quand tout est satisfait, le flag s'affiche :

```
FCSC{...}
```