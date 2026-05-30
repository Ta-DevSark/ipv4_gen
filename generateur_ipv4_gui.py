#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generateur d'exercices IPv4 - interface graphique (tkinter)
===========================================================
Version graphique du generateur. Elle reutilise toute la logique de calcul
du fichier generateur_ipv4.py (qui doit se trouver dans le meme dossier) et
partage le meme historique (historique_exercices.json).

Lancer avec :  python3 generateur_ipv4_gui.py

Remarque : tkinter fait partie de la bibliotheque standard de Python. Sous
Windows et macOS il est inclus par defaut. Sous Linux, si l'import echoue,
installer le paquet systeme :  sudo apt install python3-tk
"""

import random
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText

import generateur_ipv4 as core

VERT = "#198754"
ROUGE = "#c0392b"

MODES = {"Base": "base", "Complet": "complet"}
DIFFS = {"4e octet (/25-/30)": "o4", "3e octet (/17-/24)": "o3", "Mixte (/16-/30)": "mix"}


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
        "explications": [core.expliquer_masque(pref)],
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
# Interface graphique
# ---------------------------------------------------------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Generateur d'exercices IPv4")
        self.geometry("740x720")
        self.minsize(640, 600)

        self.historique = core.charger_historique()
        self.current = None
        self.entries = []
        self.recorded = False

        self._construire_interface()
        self.nouvel_principal()

    # --- construction de la fenetre ---
    def _construire_interface(self):
        tk.Label(self, text="Generateur d'exercices IPv4",
                 font=("Helvetica", 16, "bold")).pack(pady=(12, 4))

        reglages = ttk.LabelFrame(self, text="Reglages")
        reglages.pack(fill="x", padx=12, pady=6)
        ttk.Label(reglages, text="Mode :").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.var_mode = tk.StringVar(value="Base")
        ttk.Combobox(reglages, textvariable=self.var_mode, values=list(MODES),
                     state="readonly", width=12).grid(row=0, column=1, padx=6, pady=6)
        ttk.Label(reglages, text="Difficulte :").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        self.var_diff = tk.StringVar(value="Mixte (/16-/30)")
        ttk.Combobox(reglages, textvariable=self.var_diff, values=list(DIFFS),
                     state="readonly", width=18).grid(row=0, column=3, padx=6, pady=6)

        actions = ttk.Frame(self)
        actions.pack(fill="x", padx=12, pady=4)
        ttk.Button(actions, text="Exercice principal",
                   command=self.nouvel_principal).pack(side="left", padx=4)
        ttk.Button(actions, text="Conversion de masque",
                   command=self.nouvelle_conversion).pack(side="left", padx=4)
        ttk.Button(actions, text="Statistiques",
                   command=self.ouvrir_stats).pack(side="right", padx=4)
        ttk.Button(actions, text="Historique",
                   command=self.ouvrir_historique).pack(side="right", padx=4)

        self.cadre_exo = ttk.LabelFrame(self, text="Exercice")
        self.cadre_exo.pack(fill="x", padx=12, pady=6)

        self.lbl_enonce = tk.Label(self.cadre_exo, text="", font=("Courier", 14, "bold"))
        self.lbl_enonce.pack(anchor="w", padx=10, pady=(8, 6))

        self.cadre_champs = ttk.Frame(self.cadre_exo)
        self.cadre_champs.pack(fill="x", padx=10)

        barre = ttk.Frame(self.cadre_exo)
        barre.pack(fill="x", padx=10, pady=8)
        self.btn_verifier = ttk.Button(barre, text="Verifier", command=self.verifier)
        self.btn_verifier.pack(side="left")
        ttk.Button(barre, text="Nouvel exercice", command=self.regenerer).pack(side="left", padx=6)
        self.lbl_score = tk.Label(barre, text="", font=("Helvetica", 11, "bold"))
        self.lbl_score.pack(side="right")

        cadre_expl = ttk.LabelFrame(self, text="Explications")
        cadre_expl.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.txt_expl = ScrolledText(cadre_expl, height=12, font=("Courier", 10), wrap="word")
        self.txt_expl.pack(fill="both", expand=True, padx=6, pady=6)
        self.txt_expl.configure(state="disabled")

    # --- helpers reglages ---
    def _mode(self):
        return MODES.get(self.var_mode.get(), "base")

    def _diff(self):
        return DIFFS.get(self.var_diff.get(), "mix")

    # --- generation / affichage ---
    def nouvel_principal(self):
        self.current = construire_principal(self._mode(), self._diff())
        self.afficher_exercice()

    def nouvelle_conversion(self):
        self.current = construire_masque()
        self.afficher_exercice()

    def regenerer(self):
        if self.current and self.current["type"] == "masque":
            self.nouvelle_conversion()
        else:
            self.nouvel_principal()

    def afficher_exercice(self):
        for w in self.cadre_champs.winfo_children():
            w.destroy()
        self.entries = []
        self.recorded = False
        self.lbl_enonce.config(text=self.current["enonce"])
        self.lbl_score.config(text="")
        self.btn_verifier.config(state="normal")

        for i, q in enumerate(self.current["questions"]):
            tk.Label(self.cadre_champs, text=q["label"] + " :", anchor="w", width=34).grid(
                row=i, column=0, sticky="w", pady=3)
            entry = ttk.Entry(self.cadre_champs, width=22)
            entry.grid(row=i, column=1, padx=6, pady=3)
            statut = tk.Label(self.cadre_champs, text="", anchor="w")
            statut.grid(row=i, column=2, sticky="w")
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
        self.txt_expl.insert("1.0", texte)
        self.txt_expl.configure(state="disabled")

    # --- correction ---
    def verifier(self):
        if self.recorded or not self.current:
            return
        champs = []
        bons = 0
        for q, entry, statut in self.entries:
            ok = evaluer_champ(q["kind"], entry.get(), q["val"])
            if ok:
                statut.config(text="OK", fg=VERT)
                bons += 1
            else:
                statut.config(text="X  attendu : " + q["str"], fg=ROUGE)
            champs.append({"libelle": q["label"], "attendu": q["str"], "ok": ok})

        self.lbl_score.config(text=f"Score : {bons}/{len(self.entries)}",
                              fg=(VERT if bons == len(self.entries) else ROUGE))
        self._ecrire_explications("\n\n".join(self.current["explications"]))
        self.btn_verifier.config(state="disabled")

        core.enregistrer(self.historique, self.current["type"],
                         self.current.get("record_enonce", self.current["enonce"]),
                         champs, self.current["explications"])
        self.recorded = True

    # --- fenetres historique / stats ---
    def ouvrir_historique(self):
        win = tk.Toplevel(self)
        win.title("Historique")
        win.geometry("620x500")
        if not self.historique:
            tk.Label(win, text="Aucun exercice pour l'instant.", padx=20, pady=20).pack()
            return
        haut = ttk.Frame(win)
        haut.pack(fill="both", expand=True)
        arbre = ttk.Treeview(haut, columns=("date", "score"), show="tree headings")
        arbre.heading("#0", text="Exercice")
        arbre.heading("date", text="Date")
        arbre.heading("score", text="Score")
        arbre.column("#0", width=320)
        arbre.column("date", width=130, anchor="center")
        arbre.column("score", width=70, anchor="center")
        arbre.pack(fill="both", expand=True, side="left")
        defil = ttk.Scrollbar(haut, orient="vertical", command=arbre.yview)
        defil.pack(side="right", fill="y")
        arbre.configure(yscrollcommand=defil.set)

        item_vers_entree = {}
        for e in reversed(self.historique):
            champs = e.get("champs", [])
            b = sum(1 for c in champs if c["ok"])
            parent = arbre.insert("", "end",
                                  text=f"[{e.get('exercice', '?')}] {e.get('enonce', '')}",
                                  values=(e.get("date", ""), f"{b}/{len(champs)}"))
            item_vers_entree[parent] = e
            for c in champs:
                marque = "OK" if c["ok"] else "X"
                arbre.insert(parent, "end",
                             text=f"   {marque}  {c['libelle']}",
                             values=("", "attendu : " + c["attendu"]))

        ttk.Label(win, text="Explications de l'exercice selectionne :").pack(anchor="w", padx=8)
        panneau = ScrolledText(win, height=12, font=("Courier", 10), wrap="word")
        panneau.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        panneau.configure(state="disabled")

        def afficher_expl(_event=None):
            sel = arbre.selection()
            if not sel:
                return
            item = sel[0]
            entree = item_vers_entree.get(item) or item_vers_entree.get(arbre.parent(item))
            texte = "\n\n".join(entree.get("explications", [])) if entree else ""
            if not texte:
                texte = "(Aucune explication enregistree pour cet exercice.)"
            panneau.configure(state="normal")
            panneau.delete("1.0", "end")
            panneau.insert("1.0", texte)
            panneau.configure(state="disabled")

        arbre.bind("<<TreeviewSelect>>", afficher_expl)

        ttk.Button(win, text="Effacer l'historique",
                   command=lambda: self._effacer(win)).pack(side="bottom", pady=6)

    def _effacer(self, win):
        if messagebox.askyesno("Effacer", "Effacer tout l'historique ?"):
            self.historique.clear()
            core.sauver_historique(self.historique)
            win.destroy()

    def ouvrir_stats(self):
        win = tk.Toplevel(self)
        win.title("Statistiques")
        win.geometry("520x460")
        parfaits, total, lignes = agreger_statistiques(self.historique)
        if total == 0:
            tk.Label(win, text="Pas encore de statistiques.", padx=20, pady=20).pack()
            return
        tk.Label(win, text=f"Exercices entierement reussis : {parfaits}/{total}",
                 font=("Helvetica", 12, "bold")).pack(pady=10)
        arbre = ttk.Treeview(win, columns=("reussite", "pct"), show="tree headings")
        arbre.heading("#0", text="Type de question")
        arbre.heading("reussite", text="Reussite")
        arbre.heading("pct", text="%")
        arbre.column("#0", width=280)
        arbre.column("reussite", width=90, anchor="center")
        arbre.column("pct", width=70, anchor="center")
        arbre.pack(fill="both", expand=True, padx=10, pady=10)
        for lib, bons, tot in lignes:
            pct = round(100 * bons / tot)
            arbre.insert("", "end", text=lib, values=(f"{bons}/{tot}", f"{pct} %"))


def main():
    App().mainloop()


if __name__ == "__main__":
    main()