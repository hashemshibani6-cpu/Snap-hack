[README.md](https://github.com/user-attachments/files/34811862/README.md)

# SNAP HACK — dégradé jaune / blanc

Petit outil OSINT Snapchat pour console Windows. Tu tapes un pseudo, il récupère
ce qui est **public** sur la page de profil Snapchat, génère une liste de mots de
passe probables, et te donne quelques commandes réseau utiles. Zéro compte, zéro
login, zéro clé API obligatoire.

L'interface est un dégradé jaune → blanc calculé caractère par caractère sur le
banner et les cadres. Ce n'est pas de la déco gratuite : le jaune marque les
libellés, le blanc les valeurs, et tu repères d'un coup d'œil ce qui a été
réellement récupéré.

---

## Sommaire

1. [Ce que fait l'outil](#1-ce-que-fait-loutil)
2. [Ce qu'il ne fait pas](#2-ce-quil-ne-fait-pas)
3. [Prérequis](#3-prérequis)
4. [Installation](#4-installation)
5. [Lancement](#5-lancement)
6. [Le menu, option par option](#6-le-menu-option-par-option)
7. [Changer les couleurs](#7-changer-les-couleurs)
8. [Fichiers produits](#8-fichiers-produits)
9. [Dépannage](#9-dépannage)
10. [Limites connues](#10-limites-connues)
11. [Cadre légal](#11-cadre-légal)
12. [FAQ](#12-faq)

---

## 1. Ce que fait l'outil

| Option | Action |
|---|---|
| `1` | Récupère les données publiques d'un pseudo : nom affiché, nombre d'abonnés, bio, site, adresse, catégorie, snapcode, bitmoji. Génère 14 variantes de mots de passe probables. |
| `2` | Affiche ton IP publique et sa géolocalisation approximative (pays, ville, FAI, AS). |
| `3` | Résout les domaines Snapchat en IPv4. |
| `4` | Vérifie un email contre la base Have I Been Pwned. Clé API requise. |
| `5` | Exporte la dernière enquête en JSON dans le dossier courant. |
| `6` | Ouvre le dernier profil enquêté dans ton navigateur. |
| `0` | Quitte. |

Tout ce qui remonte à l'écran est aussi stocké en mémoire pour l'export, y compris
le champ `existe` quand le pseudo renvoie un 404.

## 2. Ce qu'il ne fait pas

- Pas de connexion : aucune session Snapchat n'est créée, aucun cookie stocké.
- Pas de contournement de privacité : un profil verrouillé reste verrouillé.
- Pas de vraie résolution de mot de passe : les propositions sont des heuristiques
  (nom affiché + suffixes courants : `1`, `123`, `!`, année en cours, années de
  naissance typiques d'un compte ado). Aucune vérification en ligne.
- Pas de géoloc réelle de la cible : seul le FAI et la ville de l'IP sont visibles,
  et seulement pour toi-même via l'option 2.

## 3. Prérequis

- Windows 10 ou 11 (ou n'importe quel Linux/macOS, ça tourne aussi).
- Python 3.8 ou plus récent.
- Un terminal qui accepte le truecolor : **Windows Terminal** de préférence. Le
  vieux `cmd.exe` écrase les couleurs et retombe sur du texte simple.
- Accès réseau sortant vers `snapchat.com`, `ip-api.com`, `haveibeenpwned.com`.

## 4. Installation

Deux modules sont utilisés : `requests` (requêtes HTTP) et `colorama` (couleurs
sous Windows). **Tu n'as pas à les installer à la main.**

Au premier lancement, le script liste ce qui manque, à quoi ça sert, et demande :
