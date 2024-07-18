# Clair-connu-XOR

Le titre du challenge nous annoce dors et déjà la couleur. Le chiffrement utilisé ici est un simple XOR.

Le XOR étant involutif
```text
    c = a (+) b
<=> c (+) b = a
<=> a (+) c = b
```
Il suffit donc de connaitre deux éléments de notre équation pour retrouver le troisième.

En analysant un dump du fichier, j'ai remarqué que le caractère 'fallen' se répète assez souvent. J'en ai déduis qu'il s'agit de la clé. Mais pour être sur je fait un tour https://wiremask.eu/tools/xor-cracker/.
```shell
$ hexdump -C ch3.bmp | less
00000000  24 2c 9a e3 62 6e 66 61  6c 6c 53 6e 66 61 44 6c  |$,..bnfallSnfaDl|
00000010  65 6e a9 60 6c 6c 01 6f  66 61 6d 6c 7d 6e 66 61  |en.`ll.ofaml}nfa|
00000020  6c 6c a5 e1 61 61 7f 67  65 6e 75 6a 6c 6c 65 6e  |ll..aa.genujllen|
00000030  66 61 6c 6c 65 6e d6 de  ae 8c 8a 9c 88 9c 93 8e  |fallen..........|
00000040  94 9a 83 95 9b 8f 97 9b  bb 8d 83 8a 90 96 83 95  |................|
00000050  9b 89 91 99 83 95 9b 89  91 99 83 95 9b 89 91 99  |................|
00000060  83 95 9b 89 91 99 83 95  9b 89 91 99 83 95 9b 89  |................|
...
```
J'ai ensuite mis en application la propriété involutif du XOR: `python3 ch3.py`