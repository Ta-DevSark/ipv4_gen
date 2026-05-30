# Générateur d'exercices IPv4

Un outil d'entraînement en Python pour maîtriser les notions de **sous-réseau** : à partir d'une adresse IP et d'un préfixe CIDR (`/N`), on s'exerce à déterminer l'adresse réseau, l'adresse de broadcast, la classe, le type (publique / privée / particulière), le masque, la plage d'hôtes utilisables et le rôle d'une adresse.

L'outil existe en **deux versions interchangeables** qui partagent le même historique :

- une version **terminal** (menu en ligne de commande) ;
- une version **interface graphique** (fenêtre tkinter).

Chaque réponse est corrigée et accompagnée d'une **explication détaillée pas à pas**, et toute la progression est sauvegardée dans un fichier 'historique_exercices.json' pour relecture.

---

## Conseils pour un apprentissage optimal

1. **Commencer en difficulté « 4e octet »**, où tout se joue sur le dernier nombre : c'est le cas le plus simple à visualiser.
2. **Rester en mode `base`** au début (réseau, broadcast, classe, type), puis passer en mode `complet` une fois ces quatre champs maîtrisés.
3. **Adopter l'ordre de raisonnement** à chaque exercice : repérer l'octet qui bouge → calculer la taille du bloc → seulement ensuite chercher le début (réseau) et la fin (broadcast).
4. **Lire systématiquement les explications**, même quand la réponse est correcte : elles renforcent la méthode.
5. **Consulter les statistiques régulièrement** et concentrer l'entraînement sur le champ au taux de réussite le plus faible.
6. **Relire l'historique** des exercices ratés : les justifications y sont conservées, inutile de tout refaire.
7. **Progresser vers la difficulté « Mixte »** pour se rapprocher des conditions d'examen, puis ajouter l'exercice de conversion de masque, souvent demandé dans les deux sens.
8. **Mémoriser les puissances de 2** utiles : `2⁶ = 64`, `2⁷ = 128`, `2⁸ = 256`, `2⁹ = 512`, `2¹⁰ = 1024`.

---

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Lancement](#lancement)
- [Les types d'exercices](#les-types-dexercices)
- [Modes et difficulté](#modes-et-difficulté)
- [Formats de réponse acceptés](#formats-de-réponse-acceptés)
- [Historique et statistiques](#historique-et-statistiques)
- [Rappel de la méthode](#rappel-de-la-méthode)
- [Tableaux de référence](#tableaux-de-référence)
- [Structure du projet](#structure-du-projet)
- [Dépannage](#dépannage)
- [Pistes d'amélioration](#pistes-damélioration)
- [Licence](#licence)

---

## Fonctionnalités

- Génération aléatoire d'adresses IPv4 avec un préfixe `/N`.
- Correction champ par champ avec la **réponse attendue** affichée en cas d'erreur.
- **Explications détaillées** pour chaque champ (méthode de calcul, justification de la classe et du type, conversion de masque, rôle de l'adresse).
- **Historique persistant** (fichier JSON) conservant les exercices, les résultats et les explications.
- **Statistiques** de réussite par type de question, pour cibler ses points faibles.
- Deux **modes de questions** : `base` (4 questions) ou `complet` (toutes les questions).
- Trois niveaux de **difficulté**.
- Aucune dépendance externe : uniquement la bibliothèque standard de Python.

---

## Prérequis

- **Python 3.6 ou plus récent**.
- Pour la version graphique uniquement : **tkinter** (inclus par défaut avec Python sous Windows et macOS ; sous Linux voir la section [Dépannage](#dépannage)).

Vérifier la version de Python :

```bash
python3 --version
```

---

## Lancement

Cloner le dépôt (ou télécharger les fichiers) :

```bash
git clone https://github.com/<votre-compte>/<votre-depot>.git
cd <votre-depot>
```

> **Important :** les deux fichiers `generateur_ipv4.py` et `generateur_ipv4_gui.py` doivent rester **dans le même dossier**, car la version graphique importe la logique de calcul de la version terminal.

Aucune installation de paquet n'est nécessaire.

---

## Les types d'exercices

### 1. Exercice principal

On reçoit une adresse et un préfixe, par exemple `192.168.45.70 /23`, et on doit remplir les champs suivants.

**Questions de base** (mode `base`) :

| Champ | Description |
|-------|-------------|
| Adresse réseau | Première adresse du bloc (bits d'hôte à 0) |
| Adresse broadcast | Dernière adresse du bloc (bits d'hôte à 1) |
| Classe | A, B, C, D ou E |
| Type | publique, privée ou particulière |

**Questions supplémentaires** (mode `complet`) :

| Champ | Description |
|-------|-------------|
| Masque décimal | Le masque de sous-réseau correspondant au `/N` |
| 1ère adresse hôte | Première adresse utilisable (réseau + 1) |
| Dernière adresse hôte | Dernière adresse utilisable (broadcast − 1) |
| Nombre d'hôtes utilisables | `2^(32−N) − 2` |
| Rôle de l'adresse | L'adresse donnée est-elle le réseau, le broadcast, ou un hôte ? |

> En mode `complet`, l'adresse proposée est parfois volontairement l'adresse réseau ou le broadcast, afin que la question sur le rôle soit réellement variée.

### 2. Exercice de conversion de masque

Tiré au sort dans **les deux sens** :

- on donne `/N` → trouver le masque décimal (ex. `/26` → `255.255.255.192`) ;
- on donne le masque décimal → trouver la notation `/N` (ex. `255.255.254.0` → `/23`).

---

## Modes et difficulté

Le **mode** et la **difficulté** se règlent depuis le menu (option « Réglages » en terminal, menus déroulants en interface graphique).

| Difficulté | Préfixes | Octet qui « bouge » | Pour qui |
|------------|----------|---------------------|----------|
| 4e octet | `/25` à `/30` | dernier octet | débutant (le plus simple) |
| 3e octet | `/17` à `/24` | avant-dernier octet | intermédiaire |
| Mixte | `/16` à `/30` | variable | conditions d'examen |

---

## Formats de réponse acceptés

La casse et les accents sont ignorés. Plusieurs synonymes sont acceptés :

| Type de réponse | Saisies acceptées |
|-----------------|-------------------|
| Adresse IP / masque | `a.b.c.d` (ex. `192.168.44.0`) |
| Classe | `A`, `B`, `C`, `D`, `E` |
| Type publique | `publique`, `public`, `pub` |
| Type privée | `privee`, `prive`, `priv`, `private` |
| Type particulière | `particuliere`, `particulier`, `part`, `speciale`, `reservee`, `n/a` |
| Rôle réseau | `reseau`, `network`, `net`, `r` |
| Rôle broadcast | `broadcast`, `diffusion`, `bc`, `b` |
| Rôle hôte | `hote`, `host`, `machine`, `poste`, `h` |
| Préfixe | un nombre (ex. `26`) ou avec barre (ex. `/26`) |

> En version terminal, taper `q` à tout moment pendant un exercice permet de l'abandonner.

---

## Historique et statistiques

- Tous les exercices terminés sont enregistrés automatiquement dans le fichier **`historique_exercices.json`**, créé **dans le même dossier que les scripts**.
- L'enregistrement se fait **dès qu'un exercice est corrigé** (pas à la fermeture du programme).
- Les deux versions (terminal et graphique) partagent le **même fichier** d'historique.
- Chaque entrée contient l'énoncé, la date, les réponses attendues, le résultat de chaque champ **et les explications complètes** de l'exercice.
- Les **statistiques** indiquent le nombre d'exercices entièrement réussis et le taux de réussite **par type de question**, ce qui permet de repérer précisément ses points faibles (par exemple le broadcast, le masque ou le rôle).

En interface graphique, la fenêtre « Historique » propose un arbre des exercices (dépliable pour voir le détail des champs) ainsi qu'un panneau affichant les explications de l'exercice sélectionné.

---

## Rappel de la méthode

Pour trouver l'adresse réseau et le broadcast à partir d'une adresse + `/N` :

1. **Nombre d'adresses** dans le bloc : `2^(32 − N)`.
2. **Octet qui bouge** : selon la valeur de `N`
   - `/1`–`/8` → 1er octet
   - `/9`–`/16` → 2e octet
   - `/17`–`/24` → 3e octet
   - `/25`–`/32` → 4e octet
3. **Taille du bloc** dans cet octet : `2^(bits d'hôte restants dans l'octet)`.
4. **Bornes** : l'adresse réseau est le début du bloc qui contient l'octet, le broadcast en est la fin. Les octets à droite valent `0` pour le réseau et `255` pour le broadcast.

**Exemple — `192.168.45.70 /23`** : `2^(32−23) = 512` adresses ; le 3e octet bouge par blocs de 2 ; `45` tombe dans le bloc `44` → réseau `192.168.44.0`, broadcast `192.168.45.255`.

**Conversion de masque** : un `/N` a `N` bits à 1 à gauche. Pour l'octet partiel, la valeur est `256 − 2^(8 − reste)` où `reste = N mod 8`. Exemple : `/26` → reste 2 → `256 − 64 = 192` → `255.255.255.192`.

---

## Tableaux de référence

### Classes d'adresses

| Classe | 1er octet | Bits de tête | Répartition | Usage |
|--------|-----------|--------------|-------------|-------|
| A | 0–127 | `0` | 1 octet réseau / 3 hôtes | unicast |
| B | 128–191 | `10` | 2 octets / 2 octets | unicast |
| C | 192–223 | `110` | 3 octets / 1 octet | unicast |
| D | 224–239 | `1110` | — | multicast |
| E | 240–255 | `1111` | — | réservée |

### Plages privées (RFC 1918)

| Classe | Plage privée |
|--------|--------------|
| A | `10.0.0.0` – `10.255.255.255` |
| B | `172.16.0.0` – `172.31.255.255` |
| C | `192.168.0.0` – `192.168.255.255` |

### Quelques adresses particulières

| Plage | Usage |
|-------|-------|
| `127.0.0.0/8` | bouclage (localhost) |
| `169.254.0.0/16` | liaison locale automatique (APIPA) |
| `100.64.0.0/10` | Carrier Grade NAT |
| `224.0.0.0/4` | multicast (classe D) |
| `240.0.0.0/4` | réservée (classe E) |

---

## Structure du projet

```
.
├── generateur_ipv4.py        # Version terminal + logique de calcul (cœur réutilisable)
├── generateur_ipv4_gui.py    # Interface graphique (tkinter), importe le cœur
├── historique_exercices.json # Créé automatiquement après le 1er exercice
└── README.md
```

---

## Dépannage

**`ModuleNotFoundError: No module named 'tkinter'` (version graphique, sous Linux)**

tkinter n'est pas installé. Selon la distribution :

```bash
# Debian / Ubuntu
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

**`ModuleNotFoundError: No module named 'generateur_ipv4'` (version graphique)**

Les deux fichiers ne sont pas dans le même dossier. Placer `generateur_ipv4_gui.py` à côté de `generateur_ipv4.py`.

**Je ne retrouve pas le fichier d'historique**

Il est créé à côté des scripts (et non dans le dossier courant).

---

## Pistes d'amélioration

- Mode « examen » chronométré enchaînant plusieurs exercices avec une note finale sur 20.
- Champ supplémentaire : écriture binaire de l'adresse ou du masque.
- Export de l'historique au format CSV.
- Empaquetage en exécutable autonome.
