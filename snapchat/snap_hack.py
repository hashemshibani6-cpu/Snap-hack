#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SNAP HACK — DEGRADE JAUNE / BLANC
Outil OSINT Snapchat pour console Windows.

Palette en degrade : jaune pur vers blanc pur (truecolor).
Si un module manque, le programme propose de l'installer au lieu de quitter.

  python snap_hack.py                 -> installation automatique proposee
  python snap_hack.py --no-install    -> aucune installation, on continue comme on peut
"""

import os, sys, json, socket, re, datetime, subprocess, importlib, webbrowser

# ---------------------------------------------------------------- COULEURS

def _enable_vt():
    """Active les sequences ANSI natives (Windows 10+)."""
    if os.name != "nt":
        return True
    try:
        import ctypes
        from ctypes import wintypes
        k32 = ctypes.windll.kernel32
        h = k32.GetStdHandle(-11)
        mode = wintypes.DWORD()
        if not k32.GetConsoleMode(h, ctypes.byref(mode)):
            return False
        if mode.value & 0x0004:
            return True
        return bool(k32.SetConsoleMode(h, mode.value | 0x0004))
    except Exception:
        return False

COLOR = False
_HAVE_COLORAMA = False
try:
    from colorama import init as _cinit
    _cinit(autoreset=False)
    COLOR = True
    _HAVE_COLORAMA = True
except ImportError:
    COLOR = _enable_vt()

# bornes du degrade : jaune -> blanc
A = (255, 205, 0)
B = (255, 255, 255)

def _mix(t):
    """Renvoie la sequence de couleur pour t dans [0,1] (0 = jaune, 1 = blanc)."""
    if not COLOR:
        return ""
    t = 0.0 if t < 0 else (1.0 if t > 1 else t)
    r = int(round(A[0] + (B[0] - A[0]) * t))
    g = int(round(A[1] + (B[1] - A[1]) * t))
    b = int(round(A[2] + (B[2] - A[2]) * t))
    return "\033[38;2;%d;%d;%dm" % (r, g, b)

def _gtext(s, t0=0.0, t1=1.0):
    """Applique le degrade caractere par caractere entre t0 et t1."""
    if not COLOR:
        return s
    n = max(1, len(s) - 1)
    out = []
    for i, ch in enumerate(s):
        out.append(_mix(t0 + (t1 - t0) * (i / n)))
        out.append(ch)
    out.append(RS)
    return "".join(out)

def _build_palette():
    global YEL, LEMON, IVORY, WHITE, DIM, HOT, BOLD, ITAL, RS
    YEL   = _mix(0.00)   # jaune pur
    LEMON = _mix(0.30)   # jaune clair
    IVORY = _mix(0.62)   # blanc casse
    WHITE = _mix(1.00)   # blanc pur
    DIM   = "\033[38;2;148;128;52m" if COLOR else ""   # jaune eteint (aide)
    HOT   = "\033[38;2;255;160;40m" if COLOR else ""   # orange dore (erreurs)
    BOLD  = "\033[1m" if COLOR else ""
    ITAL  = "\033[3m" if COLOR else ""
    RS    = "\033[0m" if COLOR else ""

_build_palette()

# ------------------------------------------------------------ DEPENDANCES

REQUIRED = {
    "requests": "requetes HTTP (Snapchat, ip-api, HIBP)",
    "colorama": "couleurs console sous Windows",
}
NO_INSTALL = ("--no-install" in sys.argv) or ("--no-pip" in sys.argv)

def _try_import(name):
    try:
        return importlib.import_module(name)
    except Exception:
        return None

def _ask(question, default=True):
    try:
        a = input(question).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return default
    if not a:
        return default
    return a in ("o", "oui", "y", "yes")

def _pip(pkgs):
    base = [sys.executable, "-m", "pip", "install", "--disable-pip-version-check"]
    for extra in ([], ["--user"], ["--break-system-packages"]):
        try:
            if subprocess.call(base + extra + pkgs) == 0:
                return True
        except Exception:
            pass
    return False

_missing = [m for m in REQUIRED if _try_import(m) is None]
if _missing:
    print()
    print(DIM + "  +-- " + RS + BOLD + LEMON + "MODULES MANQUANTS" + RS)
    for _m in _missing:
        print("  " + YEL + "*" + RS + " " + WHITE + _m + RS + DIM + " -- " + REQUIRED[_m] + RS)
    _do = False
    if NO_INSTALL:
        print("  " + DIM + "mode --no-install : pas d'installation." + RS)
    else:
        _do = _ask("  " + LEMON + "Installer " + ", ".join(_missing) + " maintenant ?" + RS + DIM + " [O/n] " + RS, True)
    if _do:
        print("  " + DIM + "installation en cours, patiente..." + RS + "\n")
        if _pip(_missing):
            print("  " + WHITE + BOLD + "Installation terminee." + RS)
            if not _HAVE_COLORAMA and _try_import("colorama"):
                try:
                    from colorama import init as _cinit2
                    _cinit2(autoreset=False)
                    COLOR = True
                    _HAVE_COLORAMA = True
                    _build_palette()
                except Exception:
                    pass
        else:
            print("  " + HOT + "Echec de l'installation. A la main :" + RS)
            print("  " + WHITE + sys.executable + " -m pip install " + " ".join(_missing) + RS)
            print("  " + DIM + "Si pip manque : " + sys.executable + " -m ensurepip --upgrade" + RS)
    print()

try:
    import requests
except ImportError:
    requests = None

if requests is None:
    print(HOT + "  Impossible de continuer sans 'requests'." + RS)
    print(WHITE + "  " + sys.executable + " -m pip install requests" + RS)
    sys.exit(1)

# ------------------------------------------------------------------ BASE

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}
LAST = {}

ART = [
    "   ########## ##    ##   ####   ######      ##  ##   ####   ###### ##  ##",
    "   ##        ###   ##  ##  ##  ##  ##      ##  ##  ##  ## ##      ## ##",
    "   ######    ## ## ##  ######  ######      ######  ###### ##      ####",
    "       ##    ##  ####  ##  ##  ##          ##  ##  ##  ## ##      ## ##",
    "   ######    ##   ###  ##  ##  ##          ##  ##  ##  ##  ###### ##  ##",
]

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def banner():
    clear()
    print()
    total = max(1, len(ART) - 1)
    for i, line in enumerate(ART):
        t = i / total
        print(BOLD + _gtext(line, t * 0.80, min(1.0, t * 0.80 + 0.20)) + RS)
    print()
    print(_gtext("   " + "-" * 62, 0.0, 1.0))
    print(BOLD + _gtext("   [ OSINT Snapchat - profil / reseau / fuites / create by wardroque ]", 0.10, 0.85) + RS)
    print(_gtext("   " + "-" * 62, 1.0, 0.0))

def sep(t):
    print()
    print(_gtext("+-- ", 0.0, 0.15) + BOLD + _gtext(t, 0.10, 0.55) + RS +
          _gtext(" " + "-" * max(2, 55 - len(t)) + "+", 0.55, 1.0))

def deep_find(obj, keys):
    out, stack = {}, [obj]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            for k, v in cur.items():
                if k in keys and isinstance(v, (str, int, float)) and k not in out:
                    out[k] = v
                if isinstance(v, (dict, list)):
                    stack.append(v)
        elif isinstance(cur, list):
            stack.extend(cur)
    return out

def guesses(info):
    """Mots de passe probables (pas le vrai)."""
    base = (info.get("displayName") or info.get("username") or "user").replace(" ", "")
    y = datetime.datetime.now().year
    sufs = ["", "1", "123", "1234", "!", "@", str(y), str(y - 1), "2007", "2008", "2009"]
    return sorted({base + s for s in sufs} | {base.lower() + s for s in sufs})[:14]

def enquete(pseudo):
    global LAST
    user = pseudo.strip().lstrip("@").lower()
    res = {"username": user, "horodatage": datetime.datetime.now().isoformat(timespec="seconds")}
    sep("CIBLE : @" + user)

    try:
        r = requests.get("https://www.snapchat.com/add/" + user, headers=UA, timeout=15)
        if r.status_code == 404:
            print("  " + HOT + "[!] Ce pseudo n'existe pas (404)." + RS)
            res["existe"] = False
            LAST = res
            return res
        res["existe"] = True
        m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', r.text, re.S)
        if m:
            try:
                res.update(deep_find(json.loads(m.group(1)), {
                    "displayName", "subscriberCount", "bio", "address", "websiteUrl",
                    "snapcodeImageUrl", "bitmoji", "mutableName", "creationTimestamp", "category"}))
            except Exception:
                pass
        for pat, key in [(r'"displayName":"(.*?)"', "displayName"),
                         (r'"subscriberCount":(\d+)', "subscriberCount"),
                         (r'"bio":"(.*?)"', "bio"),
                         (r'"websiteUrl":"(.*?)"', "websiteUrl")]:
            if not res.get(key):
                m2 = re.search(pat, r.text)
                if m2:
                    res[key] = m2.group(1)
    except Exception as e:
        print("  " + LEMON + "[!] Page : " + str(e) + RS)

    if not res.get("displayName"):
        try:
            g = requests.get("https://app.snapchat.com/web_gateway/soap/userprofile/api/getUserProfile",
                             params={"username": user}, headers=UA, timeout=15)
            if g.ok and "data" in g.text:
                res.update(deep_find(g.json(), {"displayName", "snapcodeImageUrl", "bitmoji", "mutableName"}))
        except Exception:
            pass

    if not res.get("displayName") and not res.get("subscriberCount"):
        print("  " + LEMON + "[~] Profil prive / vide : pseudo valide mais rien de public." + RS)

    champs = [("displayName", "Nom affiche"), ("subscriberCount", "Abonnes"),
              ("bio", "Bio"), ("websiteUrl", "Site"), ("address", "Adresse"),
              ("category", "Categorie"), ("mutableName", "Nom modifiable")]
    for k, label in champs:
        if res.get(k):
            print("  " + LEMON + label.ljust(16) + RS + DIM + ":" + RS + " " + WHITE + str(res[k]) + RS)

    if res.get("snapcodeImageUrl"):
        print("  " + LEMON + "Snapcode".ljust(16) + RS + DIM + ":" + RS + " " + WHITE + res["snapcodeImageUrl"] + RS)
    if res.get("bitmoji"):
        print("  " + LEMON + "Bitmoji".ljust(16) + RS + DIM + ":" + RS + " " + WHITE + res["bitmoji"] + RS)

    print()
    print("  " + LEMON + "Profil" + RS + "    : " + WHITE + "https://www.snapchat.com/add/" + user + RS)
    print("  " + LEMON + "Recherche" + RS + " : " + WHITE + "https://www.google.com/search?q=%22" + user + "%22+snapchat" + RS)

    sep("MOTS DE PASSE PROBABLES")
    print("  " + DIM + "probabilites, pas certitude" + RS + "\n")
    for g_ in guesses(res):
        print("   " + _gtext(g_, 0.0, 0.75))

    LAST = res
    return res

def mon_ip():
    sep("MON IP PUBLIQUE")
    try:
        ip = requests.get("https://api.ipify.org?format=json", timeout=10).json()["ip"]
        print("  " + LEMON + "IP" + RS + " : " + WHITE + ip + RS)
        d = requests.get("http://ip-api.com/json/" + ip +
                         "?fields=status,country,regionName,city,zip,isp,org,as,timezone,query",
                         timeout=10).json()
        for k, v in d.items():
            if k != "status":
                print("  " + LEMON + k.ljust(10) + RS + DIM + ":" + RS + " " + WHITE + str(v) + RS)
    except Exception as e:
        print("  " + HOT + "[!] " + str(e) + RS)

def dns_snap():
    sep("DNS SNAPCHAT")
    for h in ["snapchat.com", "www.snapchat.com", "app.snapchat.com", "feelinsonice.appspot.com"]:
        try:
            print("  " + LEMON + h + RS)
            for ip in socket.gethostbyname_ex(h)[2]:
                print("     " + WHITE + ip + RS)
        except Exception:
            print("     " + HOT + "echec" + RS)

def hibp(email):
    sep("FUITE DE DONNEES (HIBP)")
    key = os.environ.get("HIBP_KEY") or input("  " + LEMON + "Cle API HIBP" + RS + DIM + " (vide = annuler) : " + RS).strip()
    if not key:
        return
    try:
        r = requests.get("https://haveibeenpwned.com/api/v3/breachedaccount/" + email,
                         headers={"hibp-api-key": key, "User-Agent": "snap-hack"}, timeout=20)
        if r.status_code == 404:
            print("  " + WHITE + BOLD + "Bonne nouvelle : aucune fuite connue." + RS)
        elif r.status_code == 401:
            print("  " + HOT + "Cle invalide." + RS)
        elif r.ok:
            for b in r.json():
                print("  " + HOT + BOLD + b["Name"] + RS + DIM + " (" + b.get("BreachDate", "?") + ") -> " + RS + WHITE + str(b.get("DataClasses")) + RS)
        else:
            print("  " + LEMON + "HTTP " + str(r.status_code) + RS)
    except Exception as e:
        print("  " + HOT + "[!] " + str(e) + RS)

def export():
    if not LAST:
        print("  " + LEMON + "Aucune enquete en memoire." + RS)
        return
    f = "snap_hack_" + LAST["username"] + ".json"
    with open(f, "w", encoding="utf-8") as fh:
        json.dump(LAST, fh, indent=2, ensure_ascii=False)
    print("  " + WHITE + "Ecrit : " + os.path.abspath(f) + RS)

def ouvrir():
    if not LAST:
        print("  " + LEMON + "Aucune enquete en memoire." + RS)
        return
    webbrowser.open("https://www.snapchat.com/add/" + LAST["username"])
    print("  " + WHITE + "Profil ouvert dans le navigateur." + RS)

def main():
    while True:
        banner()
        print()
        print("   " + BOLD + YEL + "[1]" + RS + " " + WHITE + "Enquete sur un pseudo Snap" + RS)
        print("   " + BOLD + _mix(0.12) + "[2]" + RS + " " + WHITE + "Mon IP publique + geoloc" + RS)
        print("   " + BOLD + _mix(0.24) + "[3]" + RS + " " + WHITE + "DNS / serveurs Snapchat" + RS)
        print("   " + BOLD + _mix(0.36) + "[4]" + RS + " " + WHITE + "Verifier un email dans les fuites" + RS)
        print("   " + BOLD + _mix(0.48) + "[5]" + RS + " " + WHITE + "Exporter la derniere enquete en JSON" + RS)
        print("   " + BOLD + _mix(0.60) + "[6]" + RS + " " + WHITE + "Ouvrir le dernier profil" + RS)
        print("   " + BOLD + _mix(0.85) + "[0]" + RS + " " + DIM + "Quitter" + RS)
        c = input("\n  " + BOLD + _gtext("jaune@snap >", 0.0, 1.0) + " ").strip()

        if c == "1":
            enquete(input("  " + LEMON + "Pseudo Snapchat : " + RS))
        elif c == "2":
            mon_ip()
        elif c == "3":
            dns_snap()
        elif c == "4":
            hibp(input("  " + LEMON + "Email : " + RS).strip())
        elif c == "5":
            export()
        elif c == "6":
            ouvrir()
        elif c == "0":
            print(_gtext("\n  A+.\n", 0.0, 1.0))
            break
        else:
            print("  " + LEMON + "Choix inconnu." + RS)
        input("\n  " + DIM + "Entree pour revenir au menu..." + RS)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(_gtext("\n  Interrompu.\n", 0.0, 1.0))
