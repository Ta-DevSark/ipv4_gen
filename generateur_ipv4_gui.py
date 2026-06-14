#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generateur d'exercices reseau - interface graphique (customtkinter)
===================================================================
Interface moderne basee sur customtkinter. Elle reutilise toute la logique de
calcul du fichier generateur_ipv4.py (qui doit se trouver dans le meme dossier)
et les questions de cours du fichier questions_cours.py. L'historique des
exercices notes est partage avec le CLI (historique_exercices.json).

Quatre sections (barre laterale) :
  * Sous-reseau IPv4   -> exercice principal (reseau, broadcast, classe, type...)
  * Masque <-> /N      -> conversion de masque dans les deux sens
  * Questions de cours -> 20 questions theoriques, reponse libre + correction
  * Conversion de bases -> convertisseur binaire / decimal / hexadecimal

Lancer avec :  python generateur_ipv4_gui.py

Dependance : customtkinter  ->  pip install customtkinter
(tkinter fait partie de la bibliotheque standard de Python.)
"""

import random
import sys
import tkinter as tk
from tkinter import messagebox

try:
    import customtkinter as ctk
except ImportError:
    # Message clair au lieu d'une fenetre qui s'ouvre et se ferme aussitot
    # (typiquement quand on lance le script avec un interpreteur Python ou
    # customtkinter n'est pas installe, par ex. en double-cliquant le fichier).
    _r = tk.Tk()
    _r.withdraw()
    messagebox.showerror(
        "Dependance manquante : customtkinter",
        "Le module « customtkinter » n'est pas installe pour cet interpreteur :\n\n"
        f"{sys.executable}\n\n"
        "Installe-le avec la commande :\n\n"
        f'    "{sys.executable}" -m pip install customtkinter\n\n'
        "puis relance l'application.")
    _r.destroy()
    sys.exit(1)

import generateur_ipv4 as core
import questions_cours

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

VERT = "#2fa572"    # succes
ROUGE = "#d9534f"   # erreur
GRIS = ("gray45", "gray60")
TEXTE = ("gray10", "gray90")

MODES = {"Base": "base", "Complet": "complet"}
DIFFS = {"4e octet (/25-/30)": "o4", "3e octet (/17-/24)": "o3", "Mixte (/16-/30)": "mix"}
BASES = {"Binaire (2)": 2, "Decimal (10)": 10, "Hexadecimal (16)": 16}


# ---------------------------------------------------------------------------
# Logique pure (testable sans interface graphique)
# ---------------------------------------------------------------------------
def construire_principal(mode, diff):
    complet = (mode == "complet")
    octets, pref = core.generer_exercice(diff, varier_role=complet)
    net, bc = core.reseau_et_broadcast(octets, pref)
    cls = core.classe_ip(octets[0])
    scope = core.type_adresse(octets)
    masque = core.prefixe_vers_masque(pref)
    premier, dernier, nb = core.hotes_utilisables(octets, pref)
    role = core.role_adresse(octets, pref)

    questions = [
        {"label": "Adresse reseau", "kind": "ip", "val": net, "str": core.fmt(net)},
        {"label": "Adresse broadcast", "kind": "ip", "val": bc, "str": core.fmt(bc)},
        {"label": "Classe (A/B/C/D/E)", "kind": "classe", "val": cls, "str": cls},
        {"label": "Type (publique/privee/particuliere)", "kind": "type", "val": scope, "str": scope},
    ]
    if complet:
        questions.append({"label": "Masque decimal", "kind": "ip", "val": masque, "str": core.fmt(masque)})
        if premier is not None:
            questions.append({"label": "1ere adresse hote", "kind": "ip", "val": premier, "str": core.fmt(premier)})
            questions.append({"label": "Derniere adresse hote", "kind": "ip", "val": dernier, "str": core.fmt(dernier)})
        questions.append({"label": "Nb hotes utilisables", "kind": "int", "val": nb, "str": str(nb)})
        questions.append({"label": "Role (reseau/broadcast/hote)", "kind": "role", "val": role, "str": role})

    explications = [
        core.expliquer_sous_reseau(octets, pref),
        core.expliquer_classe(octets[0], cls),
        core.expliquer_type(octets, scope),
    ]
    if complet:
        explications.append(core.expliquer_masque(pref))
        explications.append(core.expliquer_role(octets, pref))

    return {
        "type": "principal",
        "enonce": f"{core.fmt(octets)} /{pref}",
        "record_enonce": f"{core.fmt(octets)} /{pref}",
        "questions": questions,
        "explications": explications,
    }


def construire_masque():
    pref = core.r(8, 30)
    masque = core.prefixe_vers_masque(pref)
    sens = random.choice(["vers_decimal", "vers_prefixe"])
    if sens == "vers_decimal":
        enonce = f"Donne le masque decimal de  /{pref}"
        q = {"label": "Conversion /N -> decimal", "kind": "ip", "val": masque, "str": core.fmt(masque)}
        record = f"/{pref} -> masque decimal"
    else:
        enonce = f"Donne la notation /N du masque  {core.fmt(masque)}"
        q = {"label": "Conversion decimal -> /N", "kind": "prefixe", "val": pref, "str": f"/{pref}"}
        record = f"{core.fmt(masque)} -> /N"
    return {
        "type": "masque",
        "enonce": enonce,
        "record_enonce": record,
        "questions": [q],
        "explications": [core.expliquer_masque(pref, sens)],
    }


def evaluer_champ(kind, saisie, val):
    if kind == "ip":
        return core.parse_ip(saisie) == val
    if kind == "int":
        s = saisie.strip()
        return s.isdigit() and int(s) == val
    if kind == "prefixe":
        s = saisie.strip().lstrip("/")
        return s.isdigit() and int(s) == val
    if kind == "classe":
        return core.normaliser(saisie) == val.lower()
    if kind == "type":
        return core.normaliser(saisie) in core.EQUIV_TYPE[val]
    if kind == "role":
        return core.normaliser(saisie) in core.EQUIV_ROLE[val]
    return False


def agreger_statistiques(historique):
    """Renvoie (parfaits, total, [(libelle, bons, tot), ...])."""
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
    lignes = [(lib, totaux[lib][0], totaux[lib][1]) for lib in ordre]
    return parfaits, len(historique), lignes


# ---------------------------------------------------------------------------
# Sections "exercice note" (sous-reseau IPv4 et masque)
# ---------------------------------------------------------------------------
class CadreExercice(ctk.CTkFrame):
    """Base commune aux exercices notes : champs a remplir, verification,
    explications et enregistrement dans l'historique."""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.current = None
        self.entries = []
        self.recorded = False
        self._build()
        self.nouveau()

    # --- a redefinir par les sous-classes ---
    def _construire_controles(self, parent):
        pass

    def generer(self):
        raise NotImplementedError

    # --- construction commune ---
    def _build(self):
        self.controles = ctk.CTkFrame(self, fg_color="transparent")
        self.controles.pack(fill="x", padx=4, pady=(2, 0))
        self._construire_controles(self.controles)

        carte = ctk.CTkFrame(self)
        carte.pack(fill="x", padx=4, pady=10)
        self.lbl_enonce = ctk.CTkLabel(carte, text="", font=self.app.font_enonce)
        self.lbl_enonce.pack(anchor="w", padx=14, pady=(12, 8))
        self.cadre_champs = ctk.CTkFrame(carte, fg_color="transparent")
        self.cadre_champs.pack(fill="x", padx=14, pady=(0, 8))

        barre = ctk.CTkFrame(carte, fg_color="transparent")
        barre.pack(fill="x", padx=14, pady=(0, 12))
        self.btn_verifier = ctk.CTkButton(barre, text="Verifier", width=120, command=self.verifier)
        self.btn_verifier.pack(side="left")
        ctk.CTkButton(barre, text="Nouvel exercice", width=150, fg_color="transparent",
                      border_width=1, text_color=TEXTE, command=self.nouveau).pack(side="left", padx=8)
        self.lbl_score = ctk.CTkLabel(barre, text="", font=self.app.font_bold)
        self.lbl_score.pack(side="right")

        carte2 = ctk.CTkFrame(self)
        carte2.pack(fill="both", expand=True, padx=4, pady=(0, 4))
        ctk.CTkLabel(carte2, text="Explications", font=self.app.font_bold,
                     anchor="w").pack(anchor="w", padx=14, pady=(10, 0))
        self.txt_expl = ctk.CTkTextbox(carte2, wrap="word", font=self.app.font_mono)
        self.txt_expl.pack(fill="both", expand=True, padx=14, pady=12)
        self.txt_expl.configure(state="disabled")

    def nouveau(self):
        self.generer()
        self.afficher()

    def afficher(self):
        for w in self.cadre_champs.winfo_children():
            w.destroy()
        self.entries = []
        self.recorded = False
        self.lbl_enonce.configure(text=self.current["enonce"])
        self.lbl_score.configure(text="")
        self.btn_verifier.configure(state="normal")

        for i, q in enumerate(self.current["questions"]):
            ctk.CTkLabel(self.cadre_champs, text=q["label"] + " :", anchor="w",
                         font=self.app.font_label).grid(row=i, column=0, sticky="w", padx=(2, 10), pady=5)
            entry = ctk.CTkEntry(self.cadre_champs, width=200)
            entry.grid(row=i, column=1, padx=4, pady=5)
            statut = ctk.CTkLabel(self.cadre_champs, text="", anchor="w", font=self.app.font_label)
            statut.grid(row=i, column=2, sticky="w", padx=(10, 2))
            self.entries.append((q, entry, statut))

        for idx, (_, entry, _) in enumerate(self.entries):
            if idx < len(self.entries) - 1:
                entry.bind("<Return>", lambda e, n=idx + 1: self.entries[n][1].focus_set())
            else:
                entry.bind("<Return>", lambda e: self.verifier())

        self._ecrire_explications("")
        if self.entries:
            self.entries[0][1].focus_set()

    def _ecrire_explications(self, texte):
        self.txt_expl.configure(state="normal")
        self.txt_expl.delete("1.0", "end")
        if texte:
            self.txt_expl.insert("1.0", texte)
        self.txt_expl.configure(state="disabled")

    def verifier(self):
        if self.recorded or not self.current:
            return
        champs = []
        bons = 0
        for q, entry, statut in self.entries:
            ok = evaluer_champ(q["kind"], entry.get(), q["val"])
            if ok:
                statut.configure(text="OK", text_color=VERT)
                bons += 1
            else:
                statut.configure(text="X  attendu : " + q["str"], text_color=ROUGE)
            champs.append({"libelle": q["label"], "attendu": q["str"], "ok": ok})

        total = len(self.entries)
        self.lbl_score.configure(text=f"Score : {bons}/{total}",
                                 text_color=(VERT if bons == total else ROUGE))
        self._ecrire_explications("\n\n".join(self.current["explications"]))
        self.btn_verifier.configure(state="disabled")

        core.enregistrer(self.app.historique, self.current["type"],
                         self.current.get("record_enonce", self.current["enonce"]),
                         champs, self.current["explications"])
        self.recorded = True


class CadreIPv4(CadreExercice):
    def _construire_controles(self, parent):
        ctk.CTkLabel(parent, text="Mode :", font=self.app.font_label).pack(side="left", padx=(2, 6))
        self.var_mode = tk.StringVar(value="Base")
        ctk.CTkOptionMenu(parent, variable=self.var_mode, values=list(MODES), width=120,
                          command=lambda _v: self.nouveau()).pack(side="left", padx=4)
        ctk.CTkLabel(parent, text="Difficulte :", font=self.app.font_label).pack(side="left", padx=(18, 6))
        self.var_diff = tk.StringVar(value="Mixte (/16-/30)")
        ctk.CTkOptionMenu(parent, variable=self.var_diff, values=list(DIFFS), width=180,
                          command=lambda _v: self.nouveau()).pack(side="left", padx=4)

    def generer(self):
        self.current = construire_principal(MODES.get(self.var_mode.get(), "base"),
                                            DIFFS.get(self.var_diff.get(), "mix"))


class CadreMasque(CadreExercice):
    def _construire_controles(self, parent):
        ctk.CTkLabel(parent, text="Conversion de masque   ( /N  <->  masque decimal )",
                     font=self.app.font_label, anchor="w").pack(side="left", padx=2)

    def generer(self):
        self.current = construire_masque()


# ---------------------------------------------------------------------------
# Section "Questions de cours"
# ---------------------------------------------------------------------------
class CadreQuestions(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.questions = questions_cours.QUESTIONS_COURS
        self.index = 0
        self._wrap_job = None
        self._build()
        self.bind("<Configure>", self._maj_wrap)
        self.afficher_question()

    def _build(self):
        haut = ctk.CTkFrame(self, fg_color="transparent")
        haut.pack(fill="x", padx=4, pady=(2, 0))
        self.lbl_compteur = ctk.CTkLabel(haut, text="", font=self.app.font_bold)
        self.lbl_compteur.pack(side="left", padx=2)
        ctk.CTkButton(haut, text="Suivant >", width=104, command=self.suivant).pack(side="right", padx=4)
        ctk.CTkButton(haut, text="Aleatoire", width=104, fg_color="transparent", border_width=1,
                      text_color=TEXTE, command=self.aleatoire).pack(side="right", padx=4)
        ctk.CTkButton(haut, text="< Precedent", width=104, fg_color="transparent", border_width=1,
                      text_color=TEXTE, command=self.precedent).pack(side="right", padx=4)

        carte_q = ctk.CTkFrame(self)
        carte_q.pack(fill="x", padx=4, pady=10)
        ctk.CTkLabel(carte_q, text="Question", font=self.app.font_h2,
                     anchor="w").pack(anchor="w", padx=14, pady=(12, 2))
        self.lbl_question = ctk.CTkLabel(carte_q, text="", justify="left", anchor="w",
                                         font=self.app.font_label, wraplength=620)
        self.lbl_question.pack(anchor="w", fill="x", padx=14, pady=(0, 14))

        carte_r = ctk.CTkFrame(self)
        carte_r.pack(fill="both", expand=True, padx=4, pady=(0, 4))
        ctk.CTkLabel(carte_r, text="Ta reponse", font=self.app.font_bold,
                     anchor="w").pack(anchor="w", padx=14, pady=(10, 2))
        self.txt_reponse = ctk.CTkTextbox(carte_r, wrap="word", height=120, font=self.app.font_label)
        self.txt_reponse.pack(fill="x", padx=14, pady=(0, 8))
        self.btn_montrer = ctk.CTkButton(carte_r, text="Montrer la reponse", command=self.montrer)
        self.btn_montrer.pack(anchor="w", padx=14, pady=(0, 10))
        ctk.CTkLabel(carte_r, text="Reponse modele", font=self.app.font_bold,
                     anchor="w").pack(anchor="w", padx=14, pady=(2, 2))
        self.lbl_solution = ctk.CTkLabel(carte_r, text="", justify="left", anchor="w",
                                         font=self.app.font_label, wraplength=620)
        self.lbl_solution.pack(anchor="w", fill="x", padx=14, pady=(0, 14))

    def _maj_wrap(self, _event=None):
        # Les evenements <Configure> arrivent par rafales pendant un
        # redimensionnement : on coalesce en une seule mise a jour differee.
        if self._wrap_job is not None:
            self.after_cancel(self._wrap_job)
        self._wrap_job = self.after(60, self._appliquer_wrap)

    def _appliquer_wrap(self):
        self._wrap_job = None
        largeur = max(self.winfo_width() - 70, 280)
        self.lbl_question.configure(wraplength=largeur)
        self.lbl_solution.configure(wraplength=largeur)

    def afficher_question(self):
        item = self.questions[self.index]
        self.lbl_compteur.configure(text=f"Question {self.index + 1} / {len(self.questions)}")
        self.lbl_question.configure(text=item["q"])
        self.txt_reponse.delete("1.0", "end")
        self.lbl_solution.configure(
            text="(Clique sur « Montrer la reponse » pour l'afficher.)", text_color=GRIS)
        self.btn_montrer.configure(state="normal")

    def montrer(self):
        self.lbl_solution.configure(text=self.questions[self.index]["r"], text_color=TEXTE)
        self.btn_montrer.configure(state="disabled")

    def suivant(self):
        self.index = (self.index + 1) % len(self.questions)
        self.afficher_question()

    def precedent(self):
        self.index = (self.index - 1) % len(self.questions)
        self.afficher_question()

    def aleatoire(self):
        n = len(self.questions)
        if n > 1:
            nouveau = self.index
            while nouveau == self.index:
                nouveau = random.randrange(n)
            self.index = nouveau
        self.afficher_question()


# ---------------------------------------------------------------------------
# Section "Conversion de bases"
# ---------------------------------------------------------------------------
class CadreConversion(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._build()

    def _build(self):
        carte = ctk.CTkFrame(self)
        carte.pack(fill="x", padx=4, pady=10)
        ctk.CTkLabel(carte, text="Conversion entre bases (binaire / decimal / hexadecimal)",
                     font=self.app.font_h2, anchor="w").pack(anchor="w", padx=14, pady=(12, 10))

        form = ctk.CTkFrame(carte, fg_color="transparent")
        form.pack(fill="x", padx=14, pady=(0, 8))
        ctk.CTkLabel(form, text="Nombre :", font=self.app.font_label).grid(
            row=0, column=0, sticky="w", padx=2, pady=6)
        self.entry = ctk.CTkEntry(form, width=260, placeholder_text="ex. 1010   255   FF")
        self.entry.grid(row=0, column=1, columnspan=3, sticky="w", padx=4, pady=6)
        self.entry.bind("<Return>", lambda e: self.convertir())

        ctk.CTkLabel(form, text="De la base :", font=self.app.font_label).grid(
            row=1, column=0, sticky="w", padx=2, pady=6)
        self.var_src = tk.StringVar(value="Decimal (10)")
        ctk.CTkOptionMenu(form, variable=self.var_src, values=list(BASES), width=170).grid(
            row=1, column=1, sticky="w", padx=4, pady=6)
        ctk.CTkLabel(form, text="vers la base :", font=self.app.font_label).grid(
            row=1, column=2, sticky="w", padx=(18, 4), pady=6)
        self.var_dst = tk.StringVar(value="Binaire (2)")
        ctk.CTkOptionMenu(form, variable=self.var_dst, values=list(BASES), width=170).grid(
            row=1, column=3, sticky="w", padx=4, pady=6)

        boutons = ctk.CTkFrame(carte, fg_color="transparent")
        boutons.pack(fill="x", padx=14, pady=(0, 12))
        ctk.CTkButton(boutons, text="Convertir", width=130, command=self.convertir).pack(side="left")
        ctk.CTkButton(boutons, text="Inverser les bases", width=170, fg_color="transparent",
                      border_width=1, text_color=TEXTE, command=self.inverser).pack(side="left", padx=8)

        carte_res = ctk.CTkFrame(self)
        carte_res.pack(fill="x", padx=4, pady=(0, 10))
        ctk.CTkLabel(carte_res, text="Resultat", font=self.app.font_bold,
                     anchor="w").pack(anchor="w", padx=14, pady=(10, 0))
        self.lbl_resultat = ctk.CTkLabel(carte_res, text="—",
                                         font=ctk.CTkFont(family="Consolas", size=26, weight="bold"))
        self.lbl_resultat.pack(anchor="w", padx=14, pady=(2, 12))

        carte_met = ctk.CTkFrame(self)
        carte_met.pack(fill="both", expand=True, padx=4, pady=(0, 4))
        ctk.CTkLabel(carte_met, text="Methode pas a pas", font=self.app.font_bold,
                     anchor="w").pack(anchor="w", padx=14, pady=(10, 0))
        self.txt_methode = ctk.CTkTextbox(carte_met, wrap="word", font=self.app.font_mono)
        self.txt_methode.pack(fill="both", expand=True, padx=14, pady=12)
        self.txt_methode.configure(state="disabled")

    def inverser(self):
        s, d = self.var_src.get(), self.var_dst.get()
        self.var_src.set(d)
        self.var_dst.set(s)
        self.convertir()

    def convertir(self):
        base_src = BASES[self.var_src.get()]
        base_dst = BASES[self.var_dst.get()]
        n = core.parse_nombre(self.entry.get(), base_src)
        if n is None:
            self.lbl_resultat.configure(text="Saisie invalide", text_color=ROUGE)
            self._ecrire_methode(
                f"« {self.entry.get().strip()} » n'est pas un nombre valide en base "
                f"{base_src} ({core.NOM_BASE[base_src]}).\n"
                f"Chiffres autorises : {core._CHIFFRES_BASE[base_src]}")
            return
        self.lbl_resultat.configure(text=core.convertir_base(n, base_dst), text_color=TEXTE)
        self._ecrire_methode(core.expliquer_conversion(n, base_src, base_dst))

    def _ecrire_methode(self, texte):
        self.txt_methode.configure(state="normal")
        self.txt_methode.delete("1.0", "end")
        self.txt_methode.insert("1.0", texte)
        self.txt_methode.configure(state="disabled")


# ---------------------------------------------------------------------------
# Fenetre principale
# ---------------------------------------------------------------------------
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Generateur d'exercices reseau")
        self.geometry("980x720")
        self.minsize(860, 620)

        self.historique = core.charger_historique()

        self.font_title = ctk.CTkFont(size=20, weight="bold")
        self.font_h2 = ctk.CTkFont(size=16, weight="bold")
        self.font_bold = ctk.CTkFont(size=14, weight="bold")
        self.font_label = ctk.CTkFont(size=13)
        self.font_enonce = ctk.CTkFont(family="Consolas", size=18, weight="bold")
        self.font_mono = ctk.CTkFont(family="Consolas", size=12)

        self._build()

    def _build(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- barre laterale ---
        side = ctk.CTkFrame(self, width=212, corner_radius=0)
        side.grid(row=0, column=0, sticky="nsew")
        side.grid_propagate(False)

        ctk.CTkLabel(side, text="Reseau IPv4", font=self.font_title).pack(padx=20, pady=(22, 0))
        ctk.CTkLabel(side, text="Entrainement", font=self.font_label,
                     text_color=GRIS).pack(padx=20, pady=(0, 18))

        self.nav_boutons = {}
        for nom in ("Sous-reseau IPv4", "Masque <-> /N", "Questions de cours", "Conversion de bases"):
            b = ctk.CTkButton(side, text=nom, anchor="w", fg_color="transparent",
                              text_color=TEXTE, command=lambda n=nom: self.afficher_section(n))
            b.pack(fill="x", padx=12, pady=3)
            self.nav_boutons[nom] = b

        ctk.CTkFrame(side, fg_color="transparent").pack(fill="both", expand=True)

        ctk.CTkButton(side, text="Historique", fg_color="transparent", border_width=1,
                      text_color=TEXTE, command=self.ouvrir_historique).pack(fill="x", padx=12, pady=3)
        ctk.CTkButton(side, text="Statistiques", fg_color="transparent", border_width=1,
                      text_color=TEXTE, command=self.ouvrir_stats).pack(fill="x", padx=12, pady=(3, 14))
        ctk.CTkLabel(side, text="Apparence", font=self.font_label,
                     anchor="w").pack(fill="x", padx=16)
        self.var_apparence = tk.StringVar(value="Systeme")
        ctk.CTkOptionMenu(side, variable=self.var_apparence, values=["Systeme", "Clair", "Sombre"],
                          command=self._changer_apparence).pack(fill="x", padx=12, pady=(2, 16))

        # --- zone de contenu (les sections se superposent, on en montre une) ---
        self.contenu = ctk.CTkFrame(self, fg_color="transparent")
        self.contenu.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)
        self.contenu.grid_rowconfigure(0, weight=1)
        self.contenu.grid_columnconfigure(0, weight=1)

        self.sections = {
            "Sous-reseau IPv4": CadreIPv4(self.contenu, self),
            "Masque <-> /N": CadreMasque(self.contenu, self),
            "Questions de cours": CadreQuestions(self.contenu, self),
            "Conversion de bases": CadreConversion(self.contenu, self),
        }
        for cadre in self.sections.values():
            cadre.grid(row=0, column=0, sticky="nsew")

        self.afficher_section("Sous-reseau IPv4")

    def afficher_section(self, nom):
        self.sections[nom].tkraise()
        for n, b in self.nav_boutons.items():
            b.configure(fg_color=("gray75", "gray25") if n == nom else "transparent")

    def _changer_apparence(self, choix):
        ctk.set_appearance_mode({"Systeme": "System", "Clair": "Light", "Sombre": "Dark"}[choix])

    # --- fenetre historique ---
    def ouvrir_historique(self):
        win = ctk.CTkToplevel(self)
        win.title("Historique")
        win.geometry("720x560")
        win.transient(self)
        win.after(120, win.lift)

        if not self.historique:
            ctk.CTkLabel(win, text="Aucun exercice pour l'instant.",
                         font=self.font_label).pack(padx=20, pady=20)
            return

        ctk.CTkLabel(win, text="Historique des exercices",
                     font=self.font_h2).pack(anchor="w", padx=16, pady=(14, 4))
        liste = ctk.CTkScrollableFrame(win)
        liste.pack(fill="both", expand=True, padx=12, pady=8)
        # On limite le rendu aux plus recents : chaque carte cree une dizaine de
        # widgets customtkinter, et l'historique grossit sans fin au fil des sessions.
        LIMITE = 100
        recents = list(reversed(self.historique))
        for e in recents[:LIMITE]:
            self._carte_historique(liste, e)
        if len(recents) > LIMITE:
            ctk.CTkLabel(liste, text=f"... {len(recents) - LIMITE} exercice(s) plus ancien(s) masque(s)",
                         text_color=GRIS).pack(pady=6)
        ctk.CTkButton(win, text="Effacer l'historique", fg_color=ROUGE, hover_color="#b34741",
                      command=lambda: self._effacer(win)).pack(pady=10)

    def _carte_historique(self, parent, e):
        champs = e.get("champs", [])
        bons = sum(1 for c in champs if c["ok"])
        total = len(champs)
        parfait = total > 0 and bons == total

        carte = ctk.CTkFrame(parent)
        carte.pack(fill="x", padx=4, pady=5)
        haut = ctk.CTkFrame(carte, fg_color="transparent")
        haut.pack(fill="x", padx=12, pady=(8, 0))
        ctk.CTkLabel(haut, text=f"[{e.get('exercice', '?')}]  {e.get('enonce', '')}",
                     font=self.font_bold, anchor="w").pack(side="left")
        ctk.CTkLabel(haut, text=f"{bons}/{total}", font=self.font_bold,
                     text_color=(VERT if parfait else ROUGE)).pack(side="right")
        ctk.CTkLabel(carte, text=e.get("date", ""), font=self.font_label,
                     text_color=GRIS, anchor="w").pack(anchor="w", padx=12)
        for c in champs:
            marque = "OK " if c["ok"] else "X  "
            ctk.CTkLabel(carte, text=f"  {marque}{c['libelle']}  ->  attendu : {c['attendu']}",
                         font=self.font_label, text_color=(VERT if c["ok"] else ROUGE),
                         anchor="w").pack(anchor="w", padx=12)
        if e.get("explications"):
            ctk.CTkButton(carte, text="Voir les explications", width=170, height=26,
                          fg_color="transparent", border_width=1, text_color=TEXTE,
                          command=lambda ex=e["explications"]: self._popup_explications(ex)
                          ).pack(anchor="w", padx=12, pady=(6, 10))
        else:
            ctk.CTkLabel(carte, text="").pack(pady=2)

    def _popup_explications(self, explications):
        win = ctk.CTkToplevel(self)
        win.title("Explications")
        win.geometry("660x470")
        win.transient(self)
        win.after(120, win.lift)
        txt = ctk.CTkTextbox(win, wrap="word", font=self.font_mono)
        txt.pack(fill="both", expand=True, padx=12, pady=12)
        txt.insert("1.0", "\n\n".join(explications))
        txt.configure(state="disabled")

    def _effacer(self, win):
        if messagebox.askyesno("Effacer", "Effacer tout l'historique ?", parent=win):
            self.historique.clear()
            core.sauver_historique(self.historique)
            win.destroy()

    # --- fenetre statistiques ---
    def ouvrir_stats(self):
        win = ctk.CTkToplevel(self)
        win.title("Statistiques")
        win.geometry("580x520")
        win.transient(self)
        win.after(120, win.lift)

        parfaits, total, lignes = agreger_statistiques(self.historique)
        if total == 0:
            ctk.CTkLabel(win, text="Pas encore de statistiques.",
                         font=self.font_label).pack(padx=20, pady=20)
            return

        ctk.CTkLabel(win, text="Statistiques", font=self.font_h2).pack(anchor="w", padx=16, pady=(14, 2))
        ctk.CTkLabel(win, text=f"Exercices entierement reussis : {parfaits}/{total}",
                     font=self.font_bold).pack(anchor="w", padx=16, pady=(0, 8))

        liste = ctk.CTkScrollableFrame(win, label_text="Taux de reussite par type de question")
        liste.pack(fill="both", expand=True, padx=12, pady=8)
        liste.grid_columnconfigure(1, weight=1)
        for i, (lib, bons, tot) in enumerate(lignes):
            pct = bons / tot if tot else 0
            ctk.CTkLabel(liste, text=lib, anchor="w", font=self.font_label).grid(
                row=i, column=0, sticky="w", padx=(4, 10), pady=7)
            barre = ctk.CTkProgressBar(liste)
            barre.set(pct)
            barre.grid(row=i, column=1, sticky="ew", padx=10, pady=7)
            ctk.CTkLabel(liste, text=f"{bons}/{tot}  ({round(pct * 100)} %)", anchor="e",
                         font=self.font_label).grid(row=i, column=2, sticky="e", padx=(10, 4), pady=7)


def main():
    App().mainloop()


if __name__ == "__main__":
    main()
