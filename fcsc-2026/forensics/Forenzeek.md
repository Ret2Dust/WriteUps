# Forenzeek

## Contexte

Des logs réseau au format Zeek ont été collectés sur un réseau d'entreprise.

## Partie 1 - Compromission initiale

### Objectif

Retrouver l'UID de la connexion associée au téléchargement d'un email malveillant volumineux sur la machine `192.168.1.42`.

### Etape 1 - Comprendre les protocoles mail

Les protocoles de récupération d'email sont :
```
IMAP → port 143 (clair) / 993 (SSL)
POP3 → port 110 (clair) / 995 (SSL)
HTTP/HTTPS → port 80/443 (webmail)
```

### Etape 2 - Filtrer les connexions de 192.168.1.42

On cherche une connexion volumineuse (l'énoncé précise que la charge utile est `assez volumineuse`) vers un port mail.
En triant par volume et en filtrant sur les ports mail, on trouve une connexion IMAP SSL (port 993) avec un volume significativement plus élevé que les autres.

### Réponse

UID: `1ac41a8ff0fd305679`

## Partie 2 - Latéralisation

### Objectif

Identifier l'UID de la connexion ayant permis à l'attaquant de compromettre la machine d'administration du parc depuis la machine déjà compromise (`192.168.1.42`).

### Etape 1 - Identifier la machine d'administration

Une machine d'administration réseau se distingue par son comportement: elle initie régulièrement des connexions vers de nombreuses autres machines via des protocoles d'administration à distance.

On cherche qui utilise le port 5986 (WinRM) ou le port 22 (SSH):

```bash
$ cat forenzeek.csv | awk '{if ($6 == 5986 || $6 == 22) print $0}'
1756306062.4874816      5ff38865328c68b2b5      192.168.1.38    54571   192.168.1.14    5986    25639
1756306105.8327703      113c558d71e976b473      192.168.1.38    59889   192.168.1.30    5986    33275
1756306141.4681919      9491dc6c715fc4b2f0      192.168.1.38    63944   192.168.1.49    5986    24685
1756306165.1853435      41f14723ec085028d0      192.168.1.38    62211   192.168.1.29    5986    21724
1756306209.8789678      6acf2cf84ca8228a2e      192.168.1.38    34206   192.168.1.46    5986    24976
1756306273.1965036      21301ad94d99b03e34      192.168.1.38    62806   192.168.1.40    5986    15799
1756306345.747027       2d4dc1bcd662dbabe1      192.168.1.38    59452   192.168.1.30    5986    37544
1756306440.2863076      488e9dd10fd63b4cd9      192.168.1.38    62479   192.168.1.25    5986    12300
1756306477.3044238      4471c61a804d3a7758      192.168.1.38    65410   192.168.1.15    5986    29149
...
```

`192.168.1.38` initie connexions WinRM vers presque toutes les machines du réseau → c'est la machine d'administration.

### Etape 2 -  Rechercher le mouvement latéral
On filtre toutes les connexions de 192.168.1.42 → 192.168.1.38:
```bash
$ awk '{if ($6 == 5986 && $3 == "192.168.1.42") print $0}' forenzeek.csv
1756308531.8534107      9a4fe41babf12d1bdf      192.168.1.42    53559   192.168.1.38    5986    34224
```

### Réponse

UID: `9a4fe41babf12d1bdf`
