# convolu-quoi — FCSC 2025

## Contexte

Le nom du challenge *convolu-quoi* donne déjà le ton: on va parler de codes convolutifs, un truc qui ressemble à de la magie noire au premier abord mais qui, spoiler, ne l'est pas vraiment.

Le code fait trois choses :
1. Il lit le flag et le convertit bit à bit (MSB en premier)
2. Il le passe dans un encodeur convolutif avec deux polynômes générateurs
3. Il affiche le résultat

Notre job: faire l'inverse.

---

## Ce que fait l'encodeur

Le cœur du challenge c'est la fonction `convolve`. Elle maintient un **registre à décalage de 5 bits** et pour chaque bit d'entrée, elle produit **2 bits de sortie** en calculant la parité du registre masqué par deux polynômes :

```go
var G0 uint8 = 0x19  // 11001 en binaire --> x⁴ + x³ + 1
var G1 uint8 = 0x1B  // 11011 en binaire --> x⁴ + x³ + x + 1

state = (state << 1) | bit
out0 = parity(state & G0)
out1 = parity(state & G1)
```

Pour 1 bit en entrée, on obtient 2 bits en sortie d'où la taille doublée de la sortie.

À la fin, 4 bits de "flush" sont ajoutés pour vider le registre à zéro. Ce détail est important.

---

## Résolution: algorithme de Viterbi

Pour inverser ça, on utilise l'**algorithme de Viterbi**: un algorithme de programmation dynamique classique qui trouve le chemin de coût minimum dans un treillis d'états.

L'idée: le registre a 4 bits de mémoire --> **16 états possibles**. À chaque instant, on sait que l'encodeur était dans un état, a lu un bit, et a émis 2 bits précis. Viterbi explore toutes les transitions possibles en accumulant la **distance de Hamming** entre les bits reçus et les bits qu'aurait émis chaque chemin hypothétique.

```python
encoded = "00110100110010011111100011111110010001001011000101000111111111100100100101011110100001001011000101000111111111100111110101000111110010101000111000001011011011111011100001010110011101001011111100001110011100110011100100101011000010100101001110111011000110100011010100100101011101110001010001001000101100010100010001010110011101111111110100000110101101001000100010001011110001110101011001110111111111100111110101110011001110010010011000111011100001101111100000011001011110100010101100001010101101001000100010001011111111100111000001000001011100110011100100100110001101011100111101110110001010110000011101010110011101111111111001000111000110010111011111000100111111100111110101111101010001001000100001010110010011010100011111001010100011100000100011000111100010000101011001110111000110100000001001110011001110101011011111000111010101100111010010001011110010010001111111001110010001111100011110001011110001110101011001110111001000111100111001000111110010101000111000001000110001001100101001100111011111111101111011111100"

bits = [int(b) for b in encoded]

G0, G1 = 0x19, 0x1B

def parity(x):
    x ^= x >> 4; x ^= x >> 2; x ^= x >> 1
    return x & 1

def encode_bit(state4, inp):
    reg = ((state4 << 1) | inp) & 0x1F
    return reg & 0xF, parity(reg & G0), parity(reg & G1)

# Viterbi
path_metric = [float('inf')] * 16
path_metric[0] = 0
paths = [[] for _ in range(16)]

for i in range(len(bits) // 2):
    b0, b1 = bits[2*i], bits[2*i+1]
    new_metric = [float('inf')] * 16
    new_paths = [None] * 16
    for state in range(16):
        if path_metric[state] == float('inf'):
            continue
        for inp in [0, 1]:
            ns, o0, o1 = encode_bit(state, inp)
            cost = path_metric[state] + (o0^b0) + (o1^b1)
            if cost < new_metric[ns]:
                new_metric[ns] = cost
                new_paths[ns] = paths[state] + [inp]
    path_metric, paths = new_metric, new_paths

# Retirer les 4 bits de flush, reconstruire les octets
decoded = paths[0][:-4]
flag = bytes(int(''.join(map(str, decoded[i:i+8])), 2) for i in range(0, len(decoded), 8))
print(flag)
```

---

## Résultat

```
b'FCSC{SC4rY_P0lyNoMS_BuT_C0nVOluT10nal_COD35_4rE_N0t_Th4T_H4rD}\n'
```