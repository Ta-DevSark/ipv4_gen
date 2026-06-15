// Questions de cours - Bases de reseau
// Donnees de l'onglet "Questions de cours".
// Chaque entree : { q: "<enonce>", r: "<reponse modele>" }
// Modifie / ajoute / supprime librement les entrees de ce tableau.

const QUESTIONS = [
  {
    q: `1. L'architecture dite de von Neumann decompose un ordinateur en quatre parties principales. Quelles sont ces quatre parties et quel est le role specifique de l'unite ALU ?`,
    r: `Les quatre parties : (1) l'unite de commande / controle, (2) l'unite arithmetique et logique (ALU), (3) la memoire centrale, (4) les dispositifs d'entree / sortie (E/S). L'unite de commande et l'ALU forment ensemble le processeur (CPU).\n\nRole de l'ALU : executer les operations arithmetiques (addition, soustraction, multiplication...) et logiques (ET, OU, NON, comparaisons) sur les donnees.`
  },
  {
    q: `2. Sur une carte mere, les ports d'extension PCIe (PCI Express) et les ports USB n'ont pas la meme utilite. Donnez un exemple de composant ou de peripherique qui se branche typiquement sur chacun de ces deux bus.`,
    r: `PCIe (bus interne d'extension, tres haut debit) : une carte graphique (GPU), une carte reseau, un SSD NVMe, une carte son.\n\nUSB (bus externe, branchement a chaud) : une cle USB, un clavier, une souris, une imprimante, une webcam, un disque dur externe.`
  },
  {
    q: `3. Quelle vitesse ira un bus PCIe 4.0 x8 ?`,
    r: `PCIe 4.0 fournit environ 2 Go/s par ligne (lane). En x8 (8 lignes) : 8 x 2 = environ 16 Go/s par sens (plus precisement ~15,75 Go/s).`
  },
  {
    q: `4. Le modele de reference OSI repartit les fonctionnalites necessaires a la communication en 7 couches. Enumerez ces couches dans l'ordre (de la couche 1 a la couche 7) et identifiez celle responsable de l'adressage physique (MAC).`,
    r: `1. Physique\n2. Liaison de donnees\n3. Reseau\n4. Transport\n5. Session\n6. Presentation\n7. Application\n\nL'adressage physique (MAC) se situe a la couche 2 (Liaison de donnees).`
  },
  {
    q: `5. Historiquement, le modele TCP/IP s'est impose face au modele OSI pour le developpement d'Internet. En combien de couches le modele TCP/IP classique est-il divise, et comment se nomment-elles ?`,
    r: `4 couches :\n1. Acces reseau (hote-a-reseau / liaison)\n2. Internet\n3. Transport\n4. Application.`
  },
  {
    q: `6. Dans un reseau Ethernet, un Hub (concentrateur) diffuse aveuglement les donnees recues a tous les autres hotes. Comment le Switch (commutateur) resout-il ce probleme de diffusion systematique pour optimiser la communication ?`,
    r: `Le switch lit l'adresse MAC source des trames qui le traversent et construit une table de correspondance MAC <-> port (table CAM). Il aiguille ensuite chaque trame uniquement vers le port ou se trouve le destinataire, au lieu de la diffuser a tous les ports. Cela reduit le trafic inutile et les collisions.`
  },
  {
    q: `7. Au sein des peripheriques reseau, on distingue clairement le « Switching » du « Routing ». Definissez brievement chacune de ces deux fonctions.`,
    r: `Switching (commutation) : aiguiller des trames a l'interieur d'un meme reseau local (LAN), a partir des adresses MAC (couche 2).\n\nRouting (routage) : faire transiter des paquets entre des reseaux differents, a partir des adresses IP (couche 3), en choisissant le meilleur chemin.`
  },
  {
    q: `8. Les cables Ethernet a paires torsadees peuvent utiliser les normes de cablage T568A et T568B. Dans quel cas d'utilisation technique precis devez-vous utiliser un cable croise, c'est-a-dire un cable utilisant une norme differente a chaque extremite ?`,
    r: `Pour relier directement deux equipements de meme type, qui emettent et recoivent sur les memes broches : par exemple PC <-> PC, switch <-> switch, ou routeur <-> routeur. (Aujourd'hui l'Auto-MDI/MDIX rend le plus souvent le cable croise inutile, l'equipement s'adaptant automatiquement.)`
  },
  {
    q: `9. Un cable a paires torsadees de Categorie 6 (Cat6) permet d'atteindre des debits allant jusqu'a 10 Gbit/s. Quelle est la limite theorique de longueur de cable pour pouvoir garantir ce debit maximal ?`,
    r: `55 metres pour le 10 Gbit/s (alors qu'en Gigabit on monte jusqu'a 100 m). Pour atteindre 100 m a 10 Gbit/s, il faut passer au Cat6a.`
  },
  {
    q: `10. Une adresse IPv4 est une adresse composee de 32 bits. Si l'on convertit ces 32 bits en 4 octets decimaux, quelle est la valeur maximale que peut prendre un octet ?`,
    r: `255. Un octet = 8 bits, soit 2^8 = 256 valeurs possibles, de 0 a 255 (11111111 en binaire).`
  },
  {
    q: `11. Une adresse IPv4 est logiquement divisee en deux parties : le « net id » et le « host id ». Expliquez comment le masque de sous-reseau permet a un equipement de determiner quelle partie de l'adresse correspond a l'identifiant du reseau.`,
    r: `Le masque est une suite de bits a 1 (partie reseau) suivie de bits a 0 (partie hote). En effectuant un ET logique (AND) bit a bit entre l'adresse IP et le masque, on isole le net id : les bits en face des 1 du masque sont conserves (identifiant reseau), ceux en face des 0 sont mis a zero (partie hote).`
  },
  {
    q: `12. Dans les annees 1990, le systeme de classes d'adresses (A, B, C) a ete remplace par le systeme CIDR (Classless Inter-Domain Routing). Quel est le principal avantage apporte par l'agregation des adresses et les masques de longueur variable (VLSM) permis par le CIDR ?`,
    r: `Une utilisation bien plus efficace de l'espace d'adressage IPv4 : on attribue des blocs de taille adaptee au besoin reel (masques de longueur variable, et plus seulement /8, /16, /24), ce qui evite le gaspillage d'adresses. De plus, l'agregation des routes (super-netting) reduit la taille des tables de routage.`
  },
  {
    q: `13. Les adresses privees sont utilisees exclusivement dans des reseaux locaux et ne sont pas routables sur Internet. Un poste est configure avec l'adresse IP 172.25.10.2. Appartient-il a une plage d'adresses privees, et si oui, a quelle classe historique correspond cette plage ?`,
    r: `Oui, c'est une adresse privee. La plage privee 172.16.0.0 - 172.31.255.255 correspond a la classe B historique ; comme 25 est compris entre 16 et 31, l'adresse 172.25.10.2 en fait partie.`
  },
  {
    q: `14. Les protocoles de la couche transport assurent la communication entre les processus. TCP garantit la fiabilite en etablissant une connexion en trois phases. Citez les trois segments echanges (les flags) lors de la phase d'etablissement de cette connexion (« 3-way handshake »).`,
    r: `SYN -> SYN-ACK -> ACK.\n(1) Le client envoie SYN, (2) le serveur repond SYN-ACK, (3) le client confirme avec ACK.`
  },
  {
    q: `15. Contrairement a TCP, le protocole UDP fonctionne sans connexion et ne requiert aucune communication prealable. Pour quel type de donnees ou d'application aborde au cours ce fonctionnement est-il particulierement indispensable ?`,
    r: `Pour les applications en temps reel, ou la rapidite prime sur la fiabilite et ou retransmettre une donnee en retard n'aurait pas de sens : la voix sur IP (VoIP), la diffusion audio/video en streaming, les jeux en ligne (et aussi le DNS).`
  },
  {
    q: `16. Le protocole DHCP permet l'attribution automatique des parametres IP. Lors de sa recherche initiale de configuration, le client envoie un message DHCP DISCOVER. Quel type d'envoi (Unicast, Multicast ou Broadcast) est utilise pour propager ce premier message sur le reseau ?`,
    r: `Un Broadcast. Le client n'a pas encore d'adresse IP et ne connait pas l'adresse du serveur DHCP : il diffuse donc le DISCOVER a tout le reseau (adresse de destination 255.255.255.255).`
  },
  {
    q: `17. La Voix sur IP (VoIP) utilise plusieurs protocoles pour fonctionner de concert. Expliquez la repartition des roles entre le protocole SIP et le protocole RTP.`,
    r: `SIP s'occupe de la signalisation : ouvrir, gerer et fermer la session d'appel (etablissement, sonnerie, raccrochage).\n\nRTP transporte le media lui-meme : le flux audio (et video) de la voix en temps reel, une fois la session etablie.`
  },
  {
    q: `18. Le protocole SIP s'inspire beaucoup de HTTP, utilisant des methodes textuelles claires. Quelle methode SIP est employee par un client pour demander l'ouverture d'une nouvelle session ?`,
    r: `La methode INVITE.`
  },
  {
    q: `19. Le DNS (Domain Name System) associe des noms de domaine a des adresses IP ou a d'autres informations. A quoi servent respectivement les enregistrements DNS de type « A » et les enregistrements de type « MX » ?`,
    r: `Un enregistrement A associe un nom de domaine a une adresse IPv4 (le « A » pour adresse ; l'equivalent IPv6 est l'enregistrement AAAA).\n\nUn enregistrement MX (Mail eXchange) indique le ou les serveurs de messagerie charges de recevoir les e-mails du domaine.`
  },
  {
    q: `20. Lors d'une seance de TP, vous constatez qu'un poste configure avec l'adresse IP 192.168.1.10 et le masque de sous-reseau 255.255.255.0 ne parvient pas a joindre Internet. Sa passerelle par defaut a ete configuree sur l'adresse 192.168.2.1. En vous basant sur la regle separant l'identifiant reseau (net id) et l'identifiant hote (host id) expliquee au cours, expliquez pourquoi cette configuration empeche techniquement la machine de communiquer avec la passerelle.`,
    r: `Avec le masque 255.255.255.0 (/24), le net id correspond aux 3 premiers octets. Le poste se trouve donc sur le reseau 192.168.1.0, tandis que la passerelle 192.168.2.1 appartient au reseau 192.168.2.0 : les net id sont differents.\n\nOr une machine ne peut communiquer directement (au niveau local) qu'avec des hotes partageant son net id. La passerelle etant hors du sous-reseau local, le poste ne peut meme pas l'atteindre, et n'a donc aucune sortie vers Internet.\n\nCorrectif : choisir une passerelle situee dans 192.168.1.0/24, par exemple 192.168.1.1.`
  }
];

if (typeof module !== "undefined") { module.exports = { QUESTIONS }; }
