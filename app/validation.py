import re


MIN_TITRE = 2
MAX_TITRE = 120
MIN_AUTEUR = 2
MAX_AUTEUR = 80


ISBN10_RE = re.compile(r"^\d{10}$")
ISBN13_RE = re.compile(r"^\d{13}$")


TITLE_RE = re.compile(r"^[A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u00FF0-9'\":,.;!?()\- ]{2,120}$")
AUTHOR_RE = re.compile(r"^[A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u00FF'.,\- ]{2,80}$")




def normaliser_texte(s: str) -> str:
    return " ".join((s or "").strip().split())




def normaliser_isbn(raw: str) -> str:
    return normaliser_texte(raw).replace("-", "").replace(" ", "")




def valider_isbn(raw: str):
    raw_n = normaliser_isbn(raw)
    if not raw_n:
        return None, "ISBN vide. Saisissez 10 ou 13 chiffres."
    if not raw_n.isdigit():
        return None, "ISBN invalide: seuls les chiffres sont autorises."
    if ISBN10_RE.match(raw_n):
        return raw_n, None
    if ISBN13_RE.match(raw_n):
        return raw_n, None
    return None, f"ISBN invalide: longueur {len(raw_n)} (attendu 10 ou 13 chiffres)."



def valider_titre(raw: str):
    raw = normaliser_texte(raw)
    if not raw:
        return None, "Titre vide."
    if len(raw) < MIN_TITRE:
        return None, f"Titre trop court (min {MIN_TITRE})."
    if len(raw) > MAX_TITRE:
        return None, f"Titre trop long (max {MAX_TITRE})."
    if not TITLE_RE.match(raw):
        return None, "Titre invalide: caracteres non autorises."
    return raw, None




def valider_auteur(raw: str):
    raw = normaliser_texte(raw)
    if not raw:
        return None, "Auteur vide."
    if len(raw) < MIN_AUTEUR:
        return None, f"Auteur trop court (min {MIN_AUTEUR})."
    if len(raw) > MAX_AUTEUR:
        return None, f"Auteur trop long (max {MAX_AUTEUR})."
    if not AUTHOR_RE.match(raw):
        return None, "Auteur invalide: caracteres non autorises."
    lettres = [c for c in raw if c.isalpha()]
    if len(lettres) < 2:
        return None, "Auteur invalide: doit contenir au moins 2 lettres."
    return raw, None
