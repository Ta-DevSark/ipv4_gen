/* Generateur d'exercices reseau - version web (mobile)
 * Logique portee depuis generateur_ipv4.py (meme calculs, memes explications).
 * Aucune dependance : JavaScript pur. Historique en localStorage.
 */
"use strict";

/* ============================================================
 * Constantes
 * ============================================================ */
const ORD = ["1er", "2e", "3e", "4e"];
const NOM_BASE = { 2: "binaire", 10: "decimal", 16: "hexadecimal" };
const CHIFFRES_BASE = { 2: "01", 10: "0123456789", 16: "0123456789abcdef" };
const EQUIV_TYPE = {
  privee: ["privee", "prive", "priv", "private"],
  publique: ["publique", "public", "pub"],
  particuliere: ["particuliere", "particulier", "part", "speciale",
    "special", "reservee", "reserve", "n/a", "na"],
};
const EQUIV_ROLE = {
  reseau: ["reseau", "network", "net", "r"],
  broadcast: ["broadcast", "diffusion", "bc", "b"],
  hote: ["hote", "host", "machine", "poste", "h"],
};
const STORAGE_HIST = "ipv4gen_historique";

/* ============================================================
 * Conversions adresse <-> entier (arithmetique, sans pieges de signe)
 * ============================================================ */
function octetsToInt(o) { return o[0] * 16777216 + o[1] * 65536 + o[2] * 256 + o[3]; }
function intToOctets(n) {
  return [Math.floor(n / 16777216) % 256, Math.floor(n / 65536) % 256,
  Math.floor(n / 256) % 256, n % 256];
}
function maskInt(prefixe) { return 4294967296 - Math.pow(2, 32 - prefixe); }
function prefixeVersMasque(prefixe) { return intToOctets(maskInt(prefixe)); }

function masqueVersPrefixe(octets) {
  let bits = 0, zeroVu = false;
  for (const o of octets) {
    for (let i = 7; i >= 0; i--) {
      if ((o >> i) & 1) { if (zeroVu) return null; bits++; }
      else { zeroVu = true; }
    }
  }
  return bits;
}

function reseauEtBroadcast(octets, prefixe) {
  const ip = octetsToInt(octets);
  const bloc = Math.pow(2, 32 - prefixe);
  const net = Math.floor(ip / bloc) * bloc;
  const bc = net + bloc - 1;
  return [intToOctets(net), intToOctets(bc)];
}

function hotesUtilisables(octets, prefixe) {
  const [net, bc] = reseauEtBroadcast(octets, prefixe);
  const total = Math.pow(2, 32 - prefixe);
  if (total < 4) return { premier: null, dernier: null, nb: Math.max(total - 2, 0) };
  return {
    premier: intToOctets(octetsToInt(net) + 1),
    dernier: intToOctets(octetsToInt(bc) - 1),
    nb: total - 2,
  };
}

function roleAdresse(octets, prefixe) {
  const [net, bc] = reseauEtBroadcast(octets, prefixe);
  if (fmt(octets) === fmt(net)) return "reseau";
  if (fmt(octets) === fmt(bc)) return "broadcast";
  return "hote";
}

function fmt(octets) { return octets.join("."); }

function parseIp(texte) {
  const parties = String(texte).trim().split(".");
  if (parties.length !== 4) return null;
  const res = [];
  for (const p of parties) {
    if (!/^\d+$/.test(p)) return null;
    const v = parseInt(p, 10);
    if (v < 0 || v > 255) return null;
    res.push(v);
  }
  return res;
}

function normaliser(texte) {
  return String(texte).trim().toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
}

/* ============================================================
 * Classe et type d'adresse
 * ============================================================ */
function classeIp(o1) {
  if (o1 <= 127) return "A";
  if (o1 <= 191) return "B";
  if (o1 <= 223) return "C";
  if (o1 <= 239) return "D";
  return "E";
}

function typeAdresse(o) {
  const [a, b] = o;
  if (a === 10) return "privee";
  if (a === 172 && b >= 16 && b <= 31) return "privee";
  if (a === 192 && b === 168) return "privee";
  if (a === 0) return "particuliere";
  if (a === 127) return "particuliere";
  if (a === 169 && b === 254) return "particuliere";
  if (a === 100 && b >= 64 && b <= 127) return "particuliere";
  if (a >= 224) return "particuliere";
  return "publique";
}

function nomCasParticulier(o) {
  const [a, b] = o;
  if (a === 0) return 'le reseau 0.0.0.0/8 ("ce reseau")';
  if (a === 127) return "une adresse de bouclage (127.0.0.0/8, localhost)";
  if (a === 169 && b === 254) return "une adresse APIPA / liaison locale (169.254.0.0/16)";
  if (a === 100 && b >= 64 && b <= 127) return "un espace Carrier Grade NAT (100.64.0.0/10)";
  if (a >= 224 && a <= 239) return "une adresse multicast de classe D (224.0.0.0 a 239.255.255.255)";
  if (a >= 240) return "une adresse reservee de classe E (240.0.0.0 a 255.255.255.255)";
  return "une adresse a usage particulier";
}

/* ============================================================
 * Generation des exercices
 * ============================================================ */
function r(a, b) { return Math.floor(Math.random() * (b - a + 1)) + a; }
function choix(arr) { return arr[Math.floor(Math.random() * arr.length)]; }

function octetsPrives() {
  const c = choix(["A", "B", "C"]);
  if (c === "A") return [10, r(0, 255), r(0, 255), r(1, 254)];
  if (c === "B") return [172, r(16, 31), r(0, 255), r(1, 254)];
  return [192, 168, r(0, 255), r(1, 254)];
}

function octetsPublics() {
  while (true) {
    const plage = [];
    for (let i = 1; i < 127; i++) plage.push(i);
    for (let i = 128; i < 224; i++) plage.push(i);
    const o = [choix(plage), r(0, 255), r(0, 255), r(1, 254)];
    if (typeAdresse(o) === "publique") return o;
  }
}

function octetsParticuliers() {
  const genre = choix(["D", "E", "loop", "apipa"]);
  if (genre === "D") return [r(224, 239), r(0, 255), r(0, 255), r(1, 254)];
  if (genre === "E") return [r(240, 254), r(0, 255), r(0, 255), r(1, 254)];
  if (genre === "loop") return [127, r(0, 255), r(0, 255), r(1, 254)];
  return [169, 254, r(0, 255), r(1, 254)];
}

function choisirPrefixe(diff) {
  if (diff === "o4") return r(25, 30);
  if (diff === "o3") return r(17, 24);
  return r(16, 30);
}

function genererExercice(diff, varierRole) {
  const tirage = Math.random();
  let octets;
  if (tirage < 0.45) octets = octetsPrives();
  else if (tirage < 0.85) octets = octetsPublics();
  else octets = octetsParticuliers();
  const prefixe = choisirPrefixe(diff);
  if (varierRole) {
    const [net, bc] = reseauEtBroadcast(octets, prefixe);
    const c = Math.random();
    if (c < 0.30) octets = net.slice();
    else if (c < 0.55) octets = bc.slice();
  }
  return [octets, prefixe];
}

/* ============================================================
 * Explications (pas a pas)
 * ============================================================ */
function expliquerSousReseau(octets, prefixe) {
  const idx = Math.floor(prefixe / 8);
  const bits = 8 - (prefixe % 8);
  const bloc = Math.pow(2, bits);
  const valIp = octets[idx];
  const valDebut = Math.floor(valIp / bloc) * bloc;
  const [reseau, broadcast] = reseauEtBroadcast(octets, prefixe);
  const masque = prefixeVersMasque(prefixe);
  const total = Math.pow(2, 32 - prefixe);
  const { premier, dernier, nb } = hotesUtilisables(octets, prefixe);
  const lignes = [
    "  Methode (reseau / broadcast) :",
    `   1. Nombre d'adresses : 2^(32-${prefixe}) = ${total}`,
    `   2. C'est le ${ORD[idx]} octet qui bouge -> blocs de ${bloc} (il reste ${bits} bit(s) d'hote dans cet octet)`,
    `   3. L'octet ${valIp} tombe dans le bloc ${valDebut} -> ${valDebut + bloc - 1}`,
    `   4. Reseau = ${fmt(reseau)}  |  Broadcast = ${fmt(broadcast)}`,
    `      Masque = ${fmt(masque)}`,
  ];
  if (premier !== null) {
    lignes.push(`   5. Hotes utilisables : ${fmt(premier)} a ${fmt(dernier)} (soit ${nb} adresses = ${total} - 2)`);
  }
  return lignes.join("\n");
}

function expliquerClasse(o1, cls) {
  const infos = {
    A: ["0 a 127", "le 1er bit a 0", "1 octet reseau / 3 octets hotes"],
    B: ["128 a 191", "les 2 premiers bits a 10", "2 octets reseau / 2 octets hotes"],
    C: ["192 a 223", "les 3 premiers bits a 110", "3 octets reseau / 1 octet hote"],
    D: ["224 a 239", "les 4 premiers bits a 1110", "multicast (multidiffusion)"],
    E: ["240 a 255", "les 4 premiers bits a 1111", "reservee (usage non determine)"],
  };
  const [plage, b, repartition] = infos[cls];
  return `  Classe : le 1er octet vaut ${o1}, compris dans ${plage} -> classe ${cls}.\n   (${b} ; ${repartition})`;
}

function expliquerType(octets, scope) {
  if (scope === "privee") {
    return "  Type : adresse PRIVEE (plages reservees aux reseaux locaux) :\n" +
      "   A : 10.0.0.0 - 10.255.255.255\n" +
      "   B : 172.16.0.0 - 172.31.255.255\n" +
      "   C : 192.168.0.0 - 192.168.255.255\n" +
      "   -> non routable sur Internet.";
  }
  if (scope === "particuliere") {
    return `  Type : adresse PARTICULIERE -> c'est ${nomCasParticulier(octets)}.\n` +
      "   -> ni publique ni privee : reservee a un usage special.";
  }
  return "  Type : adresse PUBLIQUE (routable sur Internet).\n" +
    "   Hors des plages privees (RFC 1918) et des plages a usage particulier.";
}

function expliquerMasque(prefixe, sens) {
  const octs = prefixeVersMasque(prefixe);
  const decimal = fmt(octs);
  const pleins = Math.floor(prefixe / 8);
  const reste = prefixe % 8;

  const lignesA = ["  Masque -> /N : on compte les bits a 1, octet par octet."];
  const termes = [];
  for (const o of octs) {
    const n = o.toString(2).split("").filter(x => x === "1").length;
    termes.push(String(n));
    lignesA.push(`   ${String(o).padStart(3)} = ${o.toString(2).padStart(8, "0")}  ->  ${n} bit(s) a 1`);
  }
  lignesA.push(`   Total = ${termes.join(" + ")} = ${prefixe}   ->   /${prefixe}`);
  const blocA = lignesA.join("\n");

  const lignesB = [`  /N -> masque : /${prefixe} = ${prefixe} bits a 1 a gauche, le reste a 0.`];
  if (reste) {
    const val = 256 - Math.pow(2, 8 - reste);
    lignesB.push(`   ${pleins} octet(s) plein(s) a 255, puis un octet partiel de ${prefixe} - ${pleins * 8} = ${reste} bit(s) :`);
    lignesB.push(`   valeur de l'octet partiel = 256 - 2^(8-${reste}) = 256 - ${Math.pow(2, 8 - reste)} = ${val}`);
  } else {
    lignesB.push(`   ${pleins} octet(s) a 255, les octets restants a 0.`);
  }
  lignesB.push(`   Masque decimal = ${decimal}`);
  const blocB = lignesB.join("\n");

  const entete = `  Equivalence :  ${decimal}  <->  /${prefixe}`;
  const corps = sens === "vers_prefixe" ? [blocA, blocB] : [blocB, blocA];
  return entete + "\n" + corps.join("\n");
}

function expliquerRole(octets, prefixe) {
  const [net, bc] = reseauEtBroadcast(octets, prefixe);
  const role = roleAdresse(octets, prefixe);
  const base = `  Role : bloc ${fmt(net)} -> ${fmt(bc)}.\n`;
  if (role === "reseau") return base + "   L'adresse donnee EGALE l'adresse reseau (1ere du bloc, bits d'hote a 0).";
  if (role === "broadcast") return base + "   L'adresse donnee EGALE le broadcast (derniere du bloc, bits d'hote a 1).";
  return base + "   L'adresse donnee est entre les deux : c'est une adresse d'HOTE utilisable.";
}

/* ============================================================
 * Conversion entre bases (2 / 10 / 16)
 * ============================================================ */
function parseNombre(texte, base) {
  if (texte == null || !CHIFFRES_BASE[base]) return null;
  let t = String(texte).trim().toLowerCase().replace(/\s+/g, "");
  if (base === 2 && t.startsWith("0b")) t = t.slice(2);
  else if (base === 16 && t.startsWith("0x")) t = t.slice(2);
  if (t === "") return null;
  const chiffres = CHIFFRES_BASE[base];
  for (const c of t) if (!chiffres.includes(c)) return null;
  return parseInt(t, base);
}

function convertirBase(n, base) {
  if (base === 2) return n.toString(2);
  if (base === 16) return n.toString(16).toUpperCase();
  return String(n);
}

function _etapeVersDecimal(n, baseSource) {
  const chiffres = convertirBase(n, baseSource);
  const nb = chiffres.length;
  const sym = [], num = [];
  for (let i = 0; i < nb; i++) {
    const c = chiffres[i];
    const p = nb - 1 - i;
    sym.push(`${c}x${baseSource}^${p}`);
    num.push(String(parseInt(c, baseSource) * Math.pow(baseSource, p)));
  }
  const titre = `${NOM_BASE[baseSource]} -> decimal (somme des poids de chaque position)`;
  const detail = [
    `   ${chiffres} = ${sym.join(" + ")}`,
    `   ${" ".repeat(chiffres.length)} = ${num.join(" + ")} = ${n}`,
  ];
  return [titre, detail];
}

function _etapeDepuisDecimal(n, baseCible) {
  const titre = `decimal -> ${NOM_BASE[baseCible]} (divisions successives par ${baseCible}, restes lus du bas vers le haut)`;
  if (n === 0) return [titre, ["   0  ->  0"]];
  const detail = [];
  let q = n;
  const restes = [];
  while (q > 0) {
    const rem = q % baseCible;
    const symbole = convertirBase(rem, baseCible);
    const note = (baseCible === 16 && rem >= 10) ? ` (=${symbole})` : "";
    detail.push(`   ${q} / ${baseCible} = ${Math.floor(q / baseCible)} reste ${rem}${note}`);
    restes.push(symbole);
    q = Math.floor(q / baseCible);
  }
  detail.push(`   -> ${restes.reverse().join("")}`);
  return [titre, detail];
}

function _noteRaccourci(s, c) {
  const set = new Set([s, c]);
  if (set.has(2) && set.has(16) && set.size === 2) {
    return "  Astuce binaire <-> hexa : 1 chiffre hexa = 4 bits (A=1010, F=1111).\n" +
      "   On groupe les bits par 4 a partir de la droite.";
  }
  return null;
}

function expliquerConversion(n, baseSource, baseCible) {
  const src = convertirBase(n, baseSource);
  const cible = convertirBase(n, baseCible);
  const entete = `  ${src} (base ${baseSource}, ${NOM_BASE[baseSource]})  =  ${cible} (base ${baseCible}, ${NOM_BASE[baseCible]})`;
  if (baseSource === baseCible) return entete + "\n  Meme base : aucune conversion necessaire.";
  const etapes = [];
  if (baseSource !== 10) etapes.push(_etapeVersDecimal(n, baseSource));
  if (baseCible !== 10) etapes.push(_etapeDepuisDecimal(n, baseCible));
  const lignes = [entete, ""];
  etapes.forEach(([titre, detail], i) => {
    lignes.push(`  Etape ${i + 1} : ${titre}`);
    for (const d of detail) lignes.push(d);
  });
  const note = _noteRaccourci(baseSource, baseCible);
  if (note) { lignes.push(""); lignes.push(note); }
  return lignes.join("\n");
}

/* ============================================================
 * Construction des exercices notes
 * ============================================================ */
function construirePrincipal(mode, diff) {
  const complet = mode === "complet";
  const [octets, pref] = genererExercice(diff, complet);
  const [net, bc] = reseauEtBroadcast(octets, pref);
  const cls = classeIp(octets[0]);
  const scope = typeAdresse(octets);
  const masque = prefixeVersMasque(pref);
  const { premier, dernier, nb } = hotesUtilisables(octets, pref);
  const role = roleAdresse(octets, pref);

  const questions = [
    { label: "Adresse reseau", kind: "ip", val: net, str: fmt(net) },
    { label: "Adresse broadcast", kind: "ip", val: bc, str: fmt(bc) },
    { label: "Classe (A/B/C/D/E)", kind: "classe", val: cls, str: cls },
    { label: "Type (publique/privee/particuliere)", kind: "type", val: scope, str: scope },
  ];
  if (complet) {
    questions.push({ label: "Masque decimal", kind: "ip", val: masque, str: fmt(masque) });
    if (premier !== null) {
      questions.push({ label: "1ere adresse hote", kind: "ip", val: premier, str: fmt(premier) });
      questions.push({ label: "Derniere adresse hote", kind: "ip", val: dernier, str: fmt(dernier) });
    }
    questions.push({ label: "Nb hotes utilisables", kind: "int", val: nb, str: String(nb) });
    questions.push({ label: "Role (reseau/broadcast/hote)", kind: "role", val: role, str: role });
  }

  const explications = [
    expliquerSousReseau(octets, pref),
    expliquerClasse(octets[0], cls),
    expliquerType(octets, scope),
  ];
  if (complet) {
    explications.push(expliquerMasque(pref));
    explications.push(expliquerRole(octets, pref));
  }

  return {
    type: "principal",
    enonce: `${fmt(octets)} /${pref}`,
    recordEnonce: `${fmt(octets)} /${pref}`,
    questions, explications,
  };
}

function construireMasque() {
  const pref = r(8, 30);
  const masque = prefixeVersMasque(pref);
  const sens = choix(["vers_decimal", "vers_prefixe"]);
  let enonce, q, record;
  if (sens === "vers_decimal") {
    enonce = `Donne le masque decimal de  /${pref}`;
    q = { label: "Conversion /N -> decimal", kind: "ip", val: masque, str: fmt(masque) };
    record = `/${pref} -> masque decimal`;
  } else {
    enonce = `Donne la notation /N du masque  ${fmt(masque)}`;
    q = { label: "Conversion decimal -> /N", kind: "prefixe", val: pref, str: `/${pref}` };
    record = `${fmt(masque)} -> /N`;
  }
  return {
    type: "masque", enonce, recordEnonce: record,
    questions: [q], explications: [expliquerMasque(pref, sens)],
  };
}

function evaluerChamp(kind, saisie, val) {
  if (kind === "ip") { const p = parseIp(saisie); return p !== null && fmt(p) === fmt(val); }
  if (kind === "int") { const s = String(saisie).trim(); return /^\d+$/.test(s) && parseInt(s, 10) === val; }
  if (kind === "prefixe") { const s = String(saisie).trim().replace(/^\/+/, ""); return /^\d+$/.test(s) && parseInt(s, 10) === val; }
  if (kind === "classe") return normaliser(saisie) === String(val).toLowerCase();
  if (kind === "type") return EQUIV_TYPE[val].includes(normaliser(saisie));
  if (kind === "role") return EQUIV_ROLE[val].includes(normaliser(saisie));
  return false;
}

/* ============================================================
 * Historique / statistiques (localStorage)
 * ============================================================ */
function chargerHistorique() {
  try { return JSON.parse(localStorage.getItem(STORAGE_HIST) || "[]"); }
  catch (e) { return []; }
}
function sauverHistorique(h) {
  try { localStorage.setItem(STORAGE_HIST, JSON.stringify(h)); } catch (e) { /* quota / mode prive */ }
}
function maintenant() {
  const d = new Date(), p = x => String(x).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`;
}
function enregistrer(type, enonce, champs, explications) {
  const h = chargerHistorique();
  h.push({ date: maintenant(), exercice: type, enonce, champs, explications: explications || [] });
  if (h.length > 200) h.splice(0, h.length - 200); // garde les 200 plus recents
  sauverHistorique(h);
}
function agregerStatistiques(h) {
  const totaux = {}, ordre = [];
  let parfaits = 0;
  for (const e of h) {
    const champs = e.champs || [];
    if (champs.length && champs.every(c => c.ok)) parfaits++;
    for (const c of champs) {
      if (!(c.libelle in totaux)) { totaux[c.libelle] = [0, 0]; ordre.push(c.libelle); }
      totaux[c.libelle][1]++;
      if (c.ok) totaux[c.libelle][0]++;
    }
  }
  return { parfaits, total: h.length, lignes: ordre.map(l => [l, totaux[l][0], totaux[l][1]]) };
}

/* ============================================================
 * Interface (DOM) - executee uniquement dans le navigateur
 * ============================================================ */
function initApp() {
  const $ = sel => document.querySelector(sel);
  const elt = (tag, props, kids) => {
    const e = document.createElement(tag);
    if (props) for (const k in props) {
      if (k === "class") e.className = props[k];
      else if (k === "text") e.textContent = props[k];
      else if (k === "html") e.innerHTML = props[k];
      else if (k.startsWith("on") && typeof props[k] === "function") e.addEventListener(k.slice(2), props[k]);
      else e.setAttribute(k, props[k]);
    }
    for (const c of (kids || [])) if (c != null) e.append(c);
    return e;
  };

  /* --- theme --- */
  const root = document.documentElement;
  const savedTheme = localStorage.getItem("ipv4gen_theme");
  if (savedTheme) root.setAttribute("data-theme", savedTheme);
  function majThemeBtn() {
    const cur = root.getAttribute("data-theme");
    $("#theme-btn").textContent = cur === "dark" ? "☀️" : "🌙";
  }
  $("#theme-btn").addEventListener("click", () => {
    const cur = root.getAttribute("data-theme")
      || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    const next = cur === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    localStorage.setItem("ipv4gen_theme", next);
    majThemeBtn();
  });
  majThemeBtn();

  /* --- navigation --- */
  const vues = ["ipv4", "masque", "questions", "bases"];
  function afficherVue(nom) {
    for (const v of vues) {
      $("#vue-" + v).classList.toggle("active", v === nom);
      $("#nav-" + v).classList.toggle("active", v === nom);
    }
  }
  for (const v of vues) $("#nav-" + v).addEventListener("click", () => afficherVue(v));

  /* --- sections exercices (ipv4 + masque) --- */
  const state = { ipv4: { current: null }, masque: { current: null }, qIndex: 0 };

  function rendreExercice(vue) {
    const cur = state[vue].current;
    const box = $("#" + vue + "-champs");
    box.innerHTML = "";
    state[vue].inputs = [];
    $("#" + vue + "-enonce").textContent = cur.enonce;
    $("#" + vue + "-score").textContent = "";
    $("#" + vue + "-score").className = "score";
    const expl = $("#" + vue + "-expl");
    expl.textContent = ""; expl.classList.add("hidden");
    $("#" + vue + "-verifier").disabled = false;

    cur.questions.forEach(q => {
      const input = elt("input", { type: "text", autocomplete: "off", autocapitalize: "off", spellcheck: "false" });
      const statut = elt("span", { class: "statut" });
      const ligne = elt("div", { class: "champ" }, [
        elt("label", { text: q.label }),
        input, statut,
      ]);
      box.append(ligne);
      state[vue].inputs.push({ q, input, statut });
    });
  }

  function verifierExercice(vue) {
    const st = state[vue];
    if (!st.current || st.recorded) return;
    let bons = 0;
    const champs = [];
    for (const { q, input, statut } of st.inputs) {
      const ok = evaluerChamp(q.kind, input.value, q.val);
      if (ok) { statut.textContent = "✓"; statut.className = "statut ok"; bons++; }
      else { statut.textContent = "✗ attendu : " + q.str; statut.className = "statut err"; }
      champs.push({ libelle: q.label, attendu: q.str, ok });
    }
    const total = st.inputs.length;
    const sc = $("#" + vue + "-score");
    sc.textContent = `Score : ${bons}/${total}`;
    sc.className = "score " + (bons === total ? "ok" : "err");
    const expl = $("#" + vue + "-expl");
    expl.textContent = st.current.explications.join("\n\n");
    expl.classList.remove("hidden");
    $("#" + vue + "-verifier").disabled = true;
    enregistrer(st.current.type, st.current.recordEnonce, champs, st.current.explications);
    st.recorded = true;
  }

  function nouvelExercice(vue) {
    state[vue].recorded = false;
    state[vue].current = vue === "ipv4"
      ? construirePrincipal($("#ipv4-mode").value, $("#ipv4-diff").value)
      : construireMasque();
    rendreExercice(vue);
  }

  $("#ipv4-mode").addEventListener("change", () => nouvelExercice("ipv4"));
  $("#ipv4-diff").addEventListener("change", () => nouvelExercice("ipv4"));
  $("#ipv4-verifier").addEventListener("click", () => verifierExercice("ipv4"));
  $("#ipv4-nouveau").addEventListener("click", () => nouvelExercice("ipv4"));
  $("#masque-verifier").addEventListener("click", () => verifierExercice("masque"));
  $("#masque-nouveau").addEventListener("click", () => nouvelExercice("masque"));

  /* --- questions de cours --- */
  function rendreQuestion() {
    const item = QUESTIONS[state.qIndex];
    $("#q-compteur").textContent = `Question ${state.qIndex + 1} / ${QUESTIONS.length}`;
    $("#q-enonce").textContent = item.q;
    $("#q-reponse").value = "";
    const sol = $("#q-solution");
    sol.textContent = "";
    sol.classList.add("hidden");
    $("#q-montrer").disabled = false;
  }
  $("#q-montrer").addEventListener("click", () => {
    const sol = $("#q-solution");
    sol.textContent = QUESTIONS[state.qIndex].r;
    sol.classList.remove("hidden");
    $("#q-montrer").disabled = true;
  });
  $("#q-suivant").addEventListener("click", () => { state.qIndex = (state.qIndex + 1) % QUESTIONS.length; rendreQuestion(); });
  $("#q-precedent").addEventListener("click", () => { state.qIndex = (state.qIndex - 1 + QUESTIONS.length) % QUESTIONS.length; rendreQuestion(); });
  $("#q-aleatoire").addEventListener("click", () => {
    if (QUESTIONS.length > 1) { let n = state.qIndex; while (n === state.qIndex) n = Math.floor(Math.random() * QUESTIONS.length); state.qIndex = n; }
    rendreQuestion();
  });

  /* --- conversion de bases --- */
  function convertir() {
    const baseSrc = parseInt($("#conv-src").value, 10);
    const baseDst = parseInt($("#conv-dst").value, 10);
    const n = parseNombre($("#conv-nombre").value, baseSrc);
    const res = $("#conv-resultat");
    const met = $("#conv-methode");
    if (n === null) {
      res.textContent = "Saisie invalide";
      res.className = "resultat err";
      met.textContent = `« ${$("#conv-nombre").value.trim()} » n'est pas un nombre valide en base ${baseSrc} (${NOM_BASE[baseSrc]}).\nChiffres autorises : ${CHIFFRES_BASE[baseSrc]}`;
      met.classList.remove("hidden");
      return;
    }
    res.textContent = convertirBase(n, baseDst);
    res.className = "resultat ok";
    met.textContent = expliquerConversion(n, baseSrc, baseDst);
    met.classList.remove("hidden");
  }
  $("#conv-convertir").addEventListener("click", convertir);
  $("#conv-nombre").addEventListener("keydown", e => { if (e.key === "Enter") convertir(); });
  $("#conv-inverser").addEventListener("click", () => {
    const s = $("#conv-src").value; $("#conv-src").value = $("#conv-dst").value; $("#conv-dst").value = s;
    if ($("#conv-nombre").value.trim()) convertir();
  });

  /* --- statistiques / historique (overlay) --- */
  const overlay = $("#stats-overlay");
  $("#stats-btn").addEventListener("click", () => { rendreStats(); overlay.classList.remove("hidden"); });
  $("#stats-fermer").addEventListener("click", () => overlay.classList.add("hidden"));
  overlay.addEventListener("click", e => { if (e.target === overlay) overlay.classList.add("hidden"); });
  $("#stats-effacer").addEventListener("click", () => {
    if (confirm("Effacer tout l'historique ?")) { sauverHistorique([]); rendreStats(); }
  });

  function rendreStats() {
    const h = chargerHistorique();
    const { parfaits, total, lignes } = agregerStatistiques(h);
    const corps = $("#stats-corps");
    corps.innerHTML = "";
    if (total === 0) { corps.append(elt("p", { class: "muted", text: "Pas encore d'exercice note. Fais quelques exercices IPv4 ou de masque." })); return; }
    corps.append(elt("p", { class: "stats-resume", text: `Exercices entierement reussis : ${parfaits}/${total}` }));
    corps.append(elt("h3", { text: "Taux de reussite par type de question" }));
    for (const [lib, bons, tot] of lignes) {
      const pct = tot ? Math.round((bons / tot) * 100) : 0;
      const barre = elt("div", { class: "barre" }, [elt("span", { style: `width:${pct}%` })]);
      corps.append(elt("div", { class: "stat-ligne" }, [
        elt("div", { class: "stat-lib", text: lib }),
        barre,
        elt("div", { class: "stat-val", text: `${bons}/${tot} (${pct} %)` }),
      ]));
    }
    corps.append(elt("h3", { text: "Derniers exercices" }));
    const recents = h.slice().reverse().slice(0, 25);
    for (const e of recents) {
      const champs = e.champs || [];
      const b = champs.filter(c => c.ok).length;
      const parfait = champs.length && b === champs.length;
      corps.append(elt("div", { class: "hist-ligne" }, [
        elt("span", { class: "hist-score " + (parfait ? "ok" : "err"), text: `${b}/${champs.length}` }),
        elt("span", { class: "hist-enonce", text: `[${e.exercice}] ${e.enonce}` }),
        elt("span", { class: "hist-date muted", text: e.date }),
      ]));
    }
  }

  /* --- demarrage --- */
  nouvelExercice("ipv4");
  nouvelExercice("masque");
  rendreQuestion();
  afficherVue("ipv4");

  /* --- service worker (hors-ligne) --- */
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("./sw.js").catch(() => { /* hors-ligne non critique */ });
  }
}

if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", initApp);
}

/* --- export pour tests Node --- */
if (typeof module !== "undefined") {
  module.exports = {
    octetsToInt, intToOctets, prefixeVersMasque, masqueVersPrefixe, reseauEtBroadcast,
    hotesUtilisables, roleAdresse, fmt, parseIp, classeIp, typeAdresse,
    parseNombre, convertirBase, expliquerConversion, expliquerMasque,
    construirePrincipal, construireMasque, evaluerChamp, genererExercice,
  };
}
