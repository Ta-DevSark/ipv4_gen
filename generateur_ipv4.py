#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generateur d'exercices IPv4
===========================
S'entrainer sur le sous-reseau IPv4.

Deux types d'exercices :
  * Exercice principal (a partir d'une adresse IP + /N) :
      - questions de BASE   : adresse reseau, broadcast, classe, type (public/prive)
      - questions COMPLETES : en plus -> masque decimal, 1ere et derniere adresse
        d'hote utilisable, nombre d'hotes utilisables, et role de l'adresse donnee
        (reseau / broadcast / hote)
  * Exercice de conversion de masque (les deux sens : /N <-> masque decimal)

Autres fonctionnalites :
  - correction detaillee (methode pas a pas) pour chaque champ
  - historique sauvegarde automatiquement dans un fichier JSON
  - statistiques de reussite par type de question
  - reglages : mode (base / complet) et difficulte

Aucune dependance externe. Lancer avec :  python3 generateur_ipv4.py
"""

import random
import json
import os
import unicodedata
from datetime import datetime

DOSSIER_SCRIPT = os.path.dirname(os.path.abspath(__file__))
FICHIER_HISTORIQUE = os.path.join(DOSSIER_SCRIPT, "historique_exercices.json")
ORD = ["1er", "2e", "3e", "4e"]


class Abandon(Exception):
    """Levee quand l'utilisateur tape 'q' pendant un exercice."""
    pass


# ---------------------------------------------------------------------------
# Conversions de bas niveau (adresse <-> entier 32 bits)
# ---------------------------------------------------------------------------
def octets_vers_entier(octets):
    return (octets[0] << 24) | (octets[1] << 16) | (octets[2] << 8) | octets[3]


def entier_vers_octets(n):
    return [(n >> 24) & 255, (n >> 16) & 255, (n >> 8) & 255, n & 255]


def masque_entier(prefixe):
    if prefixe == 0:
        return 0
    return (0xFFFFFFFF << (32 - prefixe)) & 0xFFFFFFFF


def prefixe_vers_masque(prefixe):
    return entier_vers_octets(masque_entier(prefixe))


def masque_vers_prefixe(octets):
    """Compte les bits a 1. Renvoie None si le masque n'est pas contigu."""
    bits = 0
    zero_vu = False
    for o in octets:
        for i in range(7, -1, -1):
            if (o >> i) & 1:
                if zero_vu:
                    return None
                bits += 1
            else:
                zero_vu = True
    return bits


def reseau_et_broadcast(octets, prefixe):
    ip = octets_vers_entier(octets)
    m = masque_entier(prefixe)
    reseau = ip & m
    broadcast = reseau | (0xFFFFFFFF ^ m)
    return entier_vers_octets(reseau), entier_vers_octets(broadcast)


def hotes_utilisables(octets, prefixe):
    """Renvoie (premier_hote, dernier_hote, nombre). (None, None, 0) si pas de plage."""
    net, bc = reseau_et_broadcast(octets, prefixe)
    total = 2 ** (32 - prefixe)
    if total < 4:
        return None, None, max(total - 2, 0)
    premier = entier_vers_octets(octets_vers_entier(net) + 1)
    dernier = entier_vers_octets(octets_vers_entier(bc) - 1)
    return premier, dernier, total - 2


def role_adresse(octets, prefixe):
    net, bc = reseau_et_broadcast(octets, prefixe)
    if octets == net:
        return "reseau"
    if octets == bc:
        return "broadcast"
    return "hote"


def fmt(octets):
    return ".".join(str(x) for x in octets)


def parse_ip(texte):
    parties = texte.strip().split(".")
    if len(parties) != 4:
        return None
    resultat = []
    for p in parties:
        if not p.isdigit():
            return None
        v = int(p)
        if v < 0 or v > 255:
            return None
        resultat.append(v)
    return resultat


def normaliser(texte):
    t = unicodedata.normalize("NFD", texte.strip().lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


# ---------------------------------------------------------------------------
# Classe et type d'adresse
# ---------------------------------------------------------------------------
def classe_ip(premier_octet):
    if premier_octet <= 127:
        return "A"
    if premier_octet <= 191:
        return "B"
    if premier_octet <= 223:
        return "C"
    if premier_octet <= 239:
        return "D"
    return "E"


def type_adresse(octets):
    a, b, c, d = octets
    if a == 10:
        return "privee"
    if a == 172 and 16 <= b <= 31:
        return "privee"
    if a == 192 and b == 168:
        return "privee"
    if a == 0:
        return "particuliere"
    if a == 127:
        return "particuliere"
    if a == 169 and b == 254:
        return "particuliere"
    if a == 100 and 64 <= b <= 127:
        return "particuliere"
    if a >= 224:
        return "particuliere"
    return "publique"


def nom_cas_particulier(octets):
    a, b = octets[0], octets[1]
    if a == 0:
        return "le reseau 0.0.0.0/8 (\"ce reseau\")"
    if a == 127:
        return "une adresse de bouclage (127.0.0.0/8, localhost)"
    if a == 169 and b == 254:
        return "une adresse APIPA / liaison locale (169.254.0.0/16)"
    if a == 100 and 64 <= b <= 127:
        return "un espace Carrier Grade NAT (100.64.0.0/10)"
    if 224 <= a <= 239:
        return "une adresse multicast de classe D (224.0.0.0 a 239.255.255.255)"
    if a >= 240:
        return "une adresse reservee de classe E (240.0.0.0 a 255.255.255.255)"
    return "une adresse a usage particulier"


# ---------------------------------------------------------------------------
# Reponses acceptees (synonymes)
# ---------------------------------------------------------------------------
EQUIV_TYPE = {
    "privee": {"privee", "prive", "priv", "private"},
    "publique": {"publique", "public", "pub"},
    "particuliere": {"particuliere", "particulier", "part", "speciale",
                     "special", "reservee", "reserve", "n/a", "na"},
}
EQUIV_ROLE = {
    "reseau": {"reseau", "network", "net", "r"},
    "broadcast": {"broadcast", "diffusion", "bc", "b"},
    "hote": {"hote", "host", "machine", "poste", "h"},
}


# ---------------------------------------------------------------------------
# Generation des exercices
# ---------------------------------------------------------------------------
def r(a, b):
    return random.randint(a, b)


def octets_prives():
    choix = random.choice(["A", "B", "C"])
    if choix == "A":
        return [10, r(0, 255), r(0, 255), r(1, 254)]
    if choix == "B":
        return [172, r(16, 31), r(0, 255), r(1, 254)]
    return [192, 168, r(0, 255), r(1, 254)]


def octets_publics():
    while True:
        premier = random.choice(list(range(1, 127)) + list(range(128, 224)))
        oct_ = [premier, r(0, 255), r(0, 255), r(1, 254)]
        if type_adresse(oct_) == "publique":
            return oct_


def octets_particuliers():
    genre = random.choice(["D", "E", "loop", "apipa"])
    if genre == "D":
        return [r(224, 239), r(0, 255), r(0, 255), r(1, 254)]
    if genre == "E":
        return [r(240, 254), r(0, 255), r(0, 255), r(1, 254)]
    if genre == "loop":
        return [127, r(0, 255), r(0, 255), r(1, 254)]
    return [169, 254, r(0, 255), r(1, 254)]


def choisir_prefixe(difficulte):
    if difficulte == "o4":
        return r(25, 30)
    if difficulte == "o3":
        return r(17, 24)
    return r(16, 30)


def generer_exercice(difficulte, varier_role=False):
    tirage = random.random()
    if tirage < 0.45:
        octets = octets_prives()
    elif tirage < 0.85:
        octets = octets_publics()
    else:
        octets = octets_particuliers()
    prefixe = choisir_prefixe(difficulte)
    if varier_role:
        net, bc = reseau_et_broadcast(octets, prefixe)
        choix = random.random()
        if choix < 0.30:
            octets = net[:]
        elif choix < 0.55:
            octets = bc[:]
    return octets, prefixe


# ---------------------------------------------------------------------------
# Explications
# ---------------------------------------------------------------------------
def expliquer_sous_reseau(octets, prefixe):
    idx = prefixe // 8
    bits = 8 - (prefixe % 8)
    bloc = 2 ** bits
    val_ip = octets[idx]
    val_debut = (val_ip // bloc) * bloc
    reseau, broadcast = reseau_et_broadcast(octets, prefixe)
    masque = prefixe_vers_masque(prefixe)
    total = 2 ** (32 - prefixe)
    premier, dernier, nb = hotes_utilisables(octets, prefixe)
    lignes = [
        "  Methode (reseau / broadcast) :",
        f"   1. Nombre d'adresses : 2^(32-{prefixe}) = {total}",
        f"   2. C'est le {ORD[idx]} octet qui bouge -> blocs de {bloc} "
        f"(il reste {bits} bit(s) d'hote dans cet octet)",
        f"   3. L'octet {val_ip} tombe dans le bloc {val_debut} -> {val_debut + bloc - 1}",
        f"   4. Reseau = {fmt(reseau)}  |  Broadcast = {fmt(broadcast)}",
        f"      Masque = {fmt(masque)}",
    ]
    if premier is not None:
        lignes.append(f"   5. Hotes utilisables : {fmt(premier)} a {fmt(dernier)} "
                      f"(soit {nb} adresses = {total} - 2)")
    return "\n".join(lignes)


def expliquer_classe(premier_octet, cls):
    infos = {
        "A": ("0 a 127", "le 1er bit a 0", "1 octet reseau / 3 octets hotes"),
        "B": ("128 a 191", "les 2 premiers bits a 10", "2 octets reseau / 2 octets hotes"),
        "C": ("192 a 223", "les 3 premiers bits a 110", "3 octets reseau / 1 octet hote"),
        "D": ("224 a 239", "les 4 premiers bits a 1110", "multicast (multidiffusion)"),
        "E": ("240 a 255", "les 4 premiers bits a 1111", "reservee (usage non determine)"),
    }
    plage, bits, repartition = infos[cls]
    return (f"  Classe : le 1er octet vaut {premier_octet}, compris dans {plage} -> classe {cls}.\n"
            f"   ({bits} ; {repartition})")


def expliquer_type(octets, scope):
    if scope == "privee":
        return ("  Type : adresse PRIVEE (plages reservees aux reseaux locaux) :\n"
                "   A : 10.0.0.0 - 10.255.255.255\n"
                "   B : 172.16.0.0 - 172.31.255.255\n"
                "   C : 192.168.0.0 - 192.168.255.255\n"
                "   -> non routable sur Internet.")
    if scope == "particuliere":
        return (f"  Type : adresse PARTICULIERE -> c'est {nom_cas_particulier(octets)}.\n"
                "   -> ni publique ni privee : reservee a un usage special.")
    return ("  Type : adresse PUBLIQUE (routable sur Internet).\n"
            "   Hors des plages privees (RFC 1918) et des plages a usage particulier.")


def expliquer_masque(prefixe):
    pleins = prefixe // 8
    reste = prefixe % 8
    octs = [255] * pleins
    val = None
    if reste:
        val = 256 - 2 ** (8 - reste)
        octs.append(val)
    while len(octs) < 4:
        octs.append(0)
    decimal = fmt(octs[:4])
    lignes = [f"  /{prefixe} = {prefixe} bits a 1 (a gauche), le reste a 0."]
    if reste:
        lignes.append(f"   {pleins} octet(s) a 255, puis un octet partiel de {reste} bit(s) :")
        lignes.append(f"   256 - 2^(8-{reste}) = 256 - {2 ** (8 - reste)} = {val}")
    else:
        lignes.append(f"   {pleins} octet(s) a 255, le reste des octets a 0.")
    lignes.append(f"   Masque decimal = {decimal}")
    lignes.append("   Sens inverse : compte les bits a 1 (chaque 255 = 8 bits) pour retrouver /N.")
    return "\n".join(lignes)


def expliquer_role(octets, prefixe):
    net, bc = reseau_et_broadcast(octets, prefixe)
    role = role_adresse(octets, prefixe)
    base = f"  Role : bloc {fmt(net)} -> {fmt(bc)}.\n"
    if role == "reseau":
        return base + "   L'adresse donnee EGALE l'adresse reseau (1ere du bloc, bits d'hote a 0)."
    if role == "broadcast":
        return base + "   L'adresse donnee EGALE le broadcast (derniere du bloc, bits d'hote a 1)."
    return base + "   L'adresse donnee est entre les deux : c'est une adresse d'HOTE utilisable."


# ---------------------------------------------------------------------------
# Saisie et correction
# ---------------------------------------------------------------------------
def lire(prompt):
    s = input(prompt)
    if normaliser(s) == "q":
        raise Abandon()
    return s


def noter_ip(libelle, saisie_octets, attendu_octets):
    ok = saisie_octets is not None and saisie_octets == attendu_octets
    return {"libelle": libelle, "attendu": fmt(attendu_octets), "ok": ok}


def afficher_correction(champs):
    print("\n  --- Correction ---")
    for c in champs:
        symbole = "OK " if c["ok"] else "X  "
        suffixe = "" if c["ok"] else f"   -> attendu : {c['attendu']}"
        print(f"  {symbole}{c['libelle']}{suffixe}")
    bons = sum(1 for c in champs if c["ok"])
    print(f"\n  Score de l'exercice : {bons}/{len(champs)}")


def enregistrer(historique, exercice, enonce, champs, explications=None):
    historique.append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "exercice": exercice,
        "enonce": enonce,
        "champs": champs,
        "explications": explications or [],
    })
    sauver_historique(historique)


# ---------------------------------------------------------------------------
# Exercice principal
# ---------------------------------------------------------------------------
def poser_exercice_principal(difficulte, mode, historique):
    complet = (mode == "complet")
    octets, prefixe = generer_exercice(difficulte, varier_role=complet)
    net, bc = reseau_et_broadcast(octets, prefixe)
    cls = classe_ip(octets[0])
    scope = type_adresse(octets)
    masque = prefixe_vers_masque(prefixe)
    premier, dernier, nb = hotes_utilisables(octets, prefixe)
    role = role_adresse(octets, prefixe)
    enonce = f"{fmt(octets)} /{prefixe}"

    print("\n" + "-" * 56)
    print(f"  Adresse a analyser :  {enonce}")
    print(f"  (mode {'complet' if complet else 'base'} -- tape 'q' pour abandonner)")
    print("-" * 56 + "\n")

    champs = []

    s = lire("  Adresse reseau        : ")
    champs.append(noter_ip("Adresse reseau", parse_ip(s), net))
    s = lire("  Adresse broadcast     : ")
    champs.append(noter_ip("Adresse broadcast", parse_ip(s), bc))
    s = lire("  Classe (A/B/C/D/E)    : ")
    champs.append({"libelle": "Classe", "attendu": cls, "ok": normaliser(s) == cls.lower()})
    s = lire("  Type (publique/privee/particuliere) : ")
    champs.append({"libelle": "Type", "attendu": scope, "ok": normaliser(s) in EQUIV_TYPE[scope]})

    if complet:
        s = lire("  Masque en decimal     : ")
        champs.append(noter_ip("Masque", parse_ip(s), masque))
        if premier is not None:
            s = lire("  1ere adresse hote     : ")
            champs.append(noter_ip("Premiere adresse hote", parse_ip(s), premier))
            s = lire("  Derniere adresse hote : ")
            champs.append(noter_ip("Derniere adresse hote", parse_ip(s), dernier))
        s = lire("  Nb d'hotes utilisables: ")
        champs.append({"libelle": "Nb hotes utilisables", "attendu": str(nb),
                       "ok": s.strip().isdigit() and int(s.strip()) == nb})
        s = lire("  Role (reseau/broadcast/hote) : ")
        champs.append({"libelle": "Role de l'adresse", "attendu": role,
                       "ok": normaliser(s) in EQUIV_ROLE[role]})

    afficher_correction(champs)

    explications = [
        expliquer_sous_reseau(octets, prefixe),
        expliquer_classe(octets[0], cls),
        expliquer_type(octets, scope),
    ]
    if complet:
        explications.append(expliquer_masque(prefixe))
        explications.append(expliquer_role(octets, prefixe))

    print("\n  --- Explications ---")
    for bloc in explications:
        print(bloc)

    enregistrer(historique, "principal", enonce, champs, explications)


# ---------------------------------------------------------------------------
# Exercice de conversion de masque (les deux sens)
# ---------------------------------------------------------------------------
def poser_exercice_masque(historique):
    prefixe = r(8, 30)
    masque = fmt(prefixe_vers_masque(prefixe))
    sens = random.choice(["vers_decimal", "vers_prefixe"])

    print("\n" + "-" * 56)
    print("  Conversion de masque  (tape 'q' pour abandonner)")
    print("-" * 56 + "\n")

    champs = []
    if sens == "vers_decimal":
        print(f"  On te donne la notation CIDR :  /{prefixe}")
        s = lire("  Masque en decimal     : ")
        champs.append(noter_ip("Conversion /N -> decimal", parse_ip(s), prefixe_vers_masque(prefixe)))
        enonce = f"/{prefixe} -> masque decimal"
    else:
        print(f"  On te donne le masque decimal :  {masque}")
        s = lire("  Notation /N           : ")
        n = s.strip().lstrip("/")
        ok = n.isdigit() and int(n) == prefixe
        champs.append({"libelle": "Conversion decimal -> /N", "attendu": f"/{prefixe}", "ok": ok})
        enonce = f"{masque} -> /N"

    afficher_correction(champs)
    explications = [expliquer_masque(prefixe)]
    print("\n  --- Explications ---")
    for bloc in explications:
        print(bloc)
    enregistrer(historique, "masque", enonce, champs, explications)


# ---------------------------------------------------------------------------
# Historique et statistiques
# ---------------------------------------------------------------------------
def charger_historique():
    if not os.path.exists(FICHIER_HISTORIQUE):
        return []
    try:
        with open(FICHIER_HISTORIQUE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []
    sortie = []
    for e in data:
        if "champs" in e:
            sortie.append(e)
        elif "details" in e and "reponses" in e:
            libelles = {"reseau": "Adresse reseau", "broadcast": "Adresse broadcast",
                        "classe": "Classe", "type": "Type"}
            champs = [{"libelle": libelles.get(k, k),
                       "attendu": str(e["reponses"].get(k, "")), "ok": bool(v)}
                      for k, v in e["details"].items()]
            sortie.append({"date": e.get("date", ""), "exercice": "principal",
                           "enonce": f"{e.get('adresse', '')}/{e.get('prefixe', '')}",
                           "champs": champs})
    return sortie


def sauver_historique(historique):
    try:
        with open(FICHIER_HISTORIQUE, "w", encoding="utf-8") as f:
            json.dump(historique, f, ensure_ascii=False, indent=2)
    except OSError:
        print("  (Impossible d'enregistrer l'historique sur le disque.)")


def afficher_historique(historique):
    if not historique:
        print("\n  Aucun exercice dans l'historique pour l'instant.\n")
        return
    print(f"\n=== Historique ({len(historique)} exercice(s)) ===")
    for i, e in enumerate(historique, 1):
        champs = e.get("champs", [])
        bons = sum(1 for c in champs if c["ok"])
        total = len(champs) if champs else 1
        print(f"\n  #{i}  [{e.get('exercice', '?')}]  {e.get('enonce', '')}   "
              f"({e.get('date', '')})   score {bons}/{total}")
        for c in champs:
            symbole = "OK " if c["ok"] else "X  "
            print(f"       {symbole}{c['libelle']:<24} attendu : {c['attendu']}")
        explications = e.get("explications", [])
        if explications:
            print("     Explications :")
            for bloc in explications:
                for ligne in bloc.splitlines():
                    print(f"     {ligne}")
    print()


def afficher_statistiques(historique):
    if not historique:
        print("\n  Pas encore de statistiques (aucun exercice realise).\n")
        return
    totaux = {}
    ordre = []
    parfaits = 0
    for e in historique:
        champs = e.get("champs", [])
        if champs and all(c["ok"] for c in champs):
            parfaits += 1
        for c in champs:
            if c["libelle"] not in totaux:
                totaux[c["libelle"]] = [0, 0]
                ordre.append(c["libelle"])
            totaux[c["libelle"]][1] += 1
            if c["ok"]:
                totaux[c["libelle"]][0] += 1
    print(f"\n=== Statistiques ({len(historique)} exercice(s)) ===")
    print(f"  Exercices entierement reussis : {parfaits}/{len(historique)}")
    print("  Taux de reussite par type de question :")
    for libelle in ordre:
        bons, tot = totaux[libelle]
        pct = round(100 * bons / tot)
        print(f"    - {libelle:<24}: {bons}/{tot}  ({pct} %)")
    print()


# ---------------------------------------------------------------------------
# Reglages
# ---------------------------------------------------------------------------
LIBELLE_DIFF = {"o4": "4e octet (/25-/30)", "o3": "3e octet (/17-/24)", "mix": "mixte (/16-/30)"}
LIBELLE_MODE = {"base": "base (reseau, broadcast, classe, type)",
                "complet": "complet (toutes les questions)"}


def menu_reglages(reglages):
    while True:
        print("\n  --- Reglages ---")
        print(f"   1. Mode des questions   (actuel : {LIBELLE_MODE[reglages['mode']]})")
        print(f"   2. Difficulte           (actuel : {LIBELLE_DIFF[reglages['diff']]})")
        print("   3. Retour")
        choix = input("  Ton choix : ").strip()
        if choix == "1":
            print("\n   a. Base    -> reseau, broadcast, classe, type")
            print("   b. Complet -> base + masque, hotes utilisables, role")
            d = normaliser(input("  Choix : "))
            reglages["mode"] = {"a": "base", "b": "complet"}.get(d, reglages["mode"])
            print(f"  Mode regle sur : {LIBELLE_MODE[reglages['mode']]}")
        elif choix == "2":
            print("\n   a. 4e octet (/25-/30)  -- le plus simple")
            print("   b. 3e octet (/17-/24)")
            print("   c. Mixte (/16-/30)     -- conditions d'examen")
            d = normaliser(input("  Choix : "))
            reglages["diff"] = {"a": "o4", "b": "o3", "c": "mix"}.get(d, reglages["diff"])
            print(f"  Difficulte reglee sur : {LIBELLE_DIFF[reglages['diff']]}")
        elif choix in ("3", "q", "retour"):
            return


# ---------------------------------------------------------------------------
# Menu principal
# ---------------------------------------------------------------------------
def main():
    historique = charger_historique()
    reglages = {"mode": "base", "diff": "mix"}

    print("=" * 56)
    print("   GENERATEUR D'EXERCICES IPv4")
    print("=" * 56)

    while True:
        print("\n  Menu :")
        print(f"   1. Exercice principal        (mode : {reglages['mode']})")
        print("   2. Exercice conversion de masque (/N <-> decimal)")
        print("   3. Voir l'historique")
        print("   4. Statistiques")
        print("   5. Reglages (mode / difficulte)")
        print("   6. Effacer l'historique")
        print("   7. Quitter")
        choix = input("  Ton choix : ").strip()

        try:
            if choix == "1":
                poser_exercice_principal(reglages["diff"], reglages["mode"], historique)
            elif choix == "2":
                poser_exercice_masque(historique)
            elif choix == "3":
                afficher_historique(historique)
            elif choix == "4":
                afficher_statistiques(historique)
            elif choix == "5":
                menu_reglages(reglages)
            elif choix == "6":
                confirm = normaliser(input("  Confirmer l'effacement ? (o/n) : "))
                if confirm in ("o", "oui", "y", "yes"):
                    historique.clear()
                    sauver_historique(historique)
                    print("  Historique efface.")
            elif choix in ("7", "q", "quit", "quitter"):
                print("\n  A bientot, bon courage pour l'examen !\n")
                break
            else:
                print("  Choix non reconnu.")
        except Abandon:
            print("\n  Exercice abandonne.\n")


if __name__ == "__main__":
    main()