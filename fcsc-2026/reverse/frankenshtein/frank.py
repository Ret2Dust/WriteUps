from re import search as s
from traceback import format_exception as t
import subprocess

symbols = [58, 59, 60, 61, 62, 63, 64, 91, 92, 93, 94, 95, 96]

b = [
    "31242a330d1233242d381b2524223a037c3a1c3d28062d3a26333e3c2c28720d2138013d",
    "180615101818124f454f2f301c371922101912372e061f0e37351e211b3b",
    "21343731243731372e300f2f22062d1d7215223032722f3f28153d151d2027332b",
    "302d3527381b30221a2311271b392626300505331427263b016e6014263e1219263d3611320e12",
    "0c040337250a15153a1a0c27053f24380b22580c1c21040637190a211b2e1e1d0c19",
    "5e525e6770617654475958406a580079645e0754666a767559675b5d414357594376645a57",
    "051a160a170a2f1f2b0f18232618240c01590a1d1c1a0317081c3b2d24061407",
    "49595d7f4355500447457241505144766a4172677f4346435a495740577f644651634a5255595b465b",
    "1f00172523073328523601360230160811125f12330e053e003352122e17032712",
    "2f2c0e7b3e1f382f1c323b293e2d3a110d2c320225301a0e3c3a2318052b3c1f22093d7f02",
    "1b0e3c07053a3e0c015f3e0e230b0f1e1f002d3110191d031f1a1c313f1a070c5c02180906",
    "383319043e272135393d3a382e3b01033204223723013b230c3b3d37243d363a3b2c113f2636",
    "041800341c4b08063111023418041f20450715032b4b3c0b181319250437151c1a",
    "1c331e0c2b160e3625272e171c120e12150b2d123f2c1c2c161e3204133e5f2e04",
    "080e3f3b271d183500151a1435250404002b1c282001231939001f04090509541805",
    "3629193b0c3e13001331003e3d2e350f1b21370a29083f370a3f081b0a08283d0f13",
    "0d0b290e051135270b2f0e032a58140407110e2b0510102d1b2915550f310e340527",
    "30222b1a2309252e13733f252539240c7318222b3d0b281f3b29022d733f20793f1d",
    "0f04003900185d04003c262208070c0f360a5a28202314050139060f0f",
    "18040e120908090b352c2a21112c1137511a0718080830120f1529052f0c212a211a362c3b",
    "080f290c04140107001b1404033a18032a110c0f14140c0c2f30243000321a120c142c2f",
    "2a242032350b760c7234001528290d0b3537112378130035302a31230904780f391528",
    "1b0411010c31383a0c1e062207025f0d023a1a050e051f1c0d253a0a3106241c",
    "302172142f0d332229140d283f3e28292c321e372d272f3703217f12110c28311f3135",
    "0c1c040a0c282b1d15120802060d10021d0f1024373c240131160e3c1310331500",
    "1d0f03051d0b0a3009011b0f115c22301b07230b515c512d102503123f05",
    "1e1b3624090a1411120a181d39444032112a1b1d1b3e141c0b390309473805",
    "352933040707051105673608691b203b28052504023f33633405250524052013243631",
    "25293d2b112d2e71313e26272e0b0d1c3e3c00323e0e2d383c231c022d1a3e3e03291e",
    "180c0d0b070d1f3d123f08001b0b1c592013011e1f032c09181e10091f1d09120e05073d332c333a",
    "1c131c1d37001f0422420f121111381b0e17112f3a3307100e1e301b133a",
    "27282b3d75382314152d273f211e25211936782435363c3c38353615393a27"
]

all_candidates = []  # Tableau qui contiendra les candidats pour chaque position

for a in b:
    candidates = []
    for i in range(32, 127):
        word = []
        for x in bytes.fromhex(a):
            y = x ^ i
            if (y >= 48) and (y < 123) and (y not in symbols):
                word.append(y)
            else:
                word = []
                break
        if word != []:
            candidates.append(i)
            # print(i, a, "==>", bytes(word).decode())
    
    # Ajouter la liste des candidats de cette position au tableau principal
    all_candidates.append(candidates)
    
    # Si tu veux aussi les mots décodés :
    # all_words.append(bytes(word).decode())  # mais attention, word est écrasé

# Maintenant all_candidates est un tableau de tableaux
# print("\nTous les candidats trouvés :")
# for idx, cand_list in enumerate(all_candidates):
#    print(f"Position {idx}: {cand_list}")

from itertools import product # Pour générer toutes les combinaisons possibles

password_first_part = []

# Pour chaque position, on a une liste de candidats
# On veut essayer toutes les combinaisons
for combination in product(*all_candidates):
#    print(f"Combinaison possible : {bytes(combination).decode()}")

    result = subprocess.run(
        ['python', '/mnt/c/Users/shraf_vxsoy/Downloads/frankenshtein.py'], 
        input=bytes(combination).decode() + '\n', text=True, 
        capture_output=True
    )
    # print(result.stdout)
    if result.stdout == ">>> Nope!\n":
        password_first_part = bytes(combination).decode()
        break

print(password_first_part)
