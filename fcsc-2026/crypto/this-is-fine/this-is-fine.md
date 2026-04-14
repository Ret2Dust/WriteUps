# This is fine

## Analyse du code
En ouvrant le fichier du challenge, le programme contient 38 polynômes de degré 16 avec d'énormes coefficients. Pour chaque polynôme de la liste, il demande deux entiers this et fine, puis vérifie :
```python
assert this == fine      # valeurs égales (trivial)
this = y(this)
fine = y(fine)
assert this is fine      # même OBJET Python
flag.append(this | fine)
```
    
Le piège réside dans la différence entre `is` (identité d'objet) et `==` (égalité de valeur). Ce qui semble impossible vu que `this` et `fine` sont défini séparément.

Et pourtant, c'est possible. En CPython, les petits entiers compris entre -5 et 256 sont pré-calculés et mis en cache. Ainsi, pour ces valeurs, `a is b` est vrai si et seulement si `a == b`.

Cela signifie que pour que l'assertion `this is fine` passe après l'évaluation des polynômes, il faut que `y(this)` (et donc `y(fine)`) soit également un entier dans l'intervalle `[-5, 256]`, afin que Python utilise le même objet en mémoire pour les deux résultats.

On en déduit qu'il faut trouver, pour chaque polynôme y, une valeur de x tel que `x ∈ N` et `y(x) ∈ [-5, 256]`

Comme `flag.append(this | fine)` et que `this == fine`, on a `(this | fine) = this = y(x)`. Donc la valeur ajoutée à flag est directement y(x), qui est un entier entre -5 et 256. Ensuite, la ligne `print(bytes(flag).decode())` nous indique que flag doit être une liste d'entiers convertibles en caractères ASCII. On peut donc réduire la recherche à `y(x) ∈ [32, 127]` (caractères imprimables).

En partant du fait que le flag commence par `FCSC{`, j'ai testé `k = 70` (F) pour le premier polynôme et bingo j'ai trouvé une solution entière. En procédant ainsi pour chaque polynôme, on obtient un unique `k` tel que l'équation `y(x) = k` admette une solution tel que `x ∈ N`.

Il suffit alors de collecter tous ces k et de les convertir pour obtenir le flag.

## Solution

En partant du fait que le flag commence par `FCSC{`, j'ai testé `k = 70` (F) pour le premier polynôme et bingo j'ai trouvé une solution entière. En procédant ainsi pour chaque polynôme, on obtient un unique `k` tel que l'équation `y(x) = k` admette une solution tel que `x ∈ N`.

Il suffit alors de collecter tous ces k et de les convertir pour obtenir le flag.

J'ai utiliser sage pour résoudre ce challenge
