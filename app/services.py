from typing import List, Optional
from .storage import BibliothequeStorage, StorageError
from .validation import valider_isbn, valider_titre, valider_auteur, normaliser_texte




class ServiceError(Exception):
    pass




class BibliothequeService:
    def __init__(self, storage: BibliothequeStorage):
        self.storage = storage


    def ajouter_livre(self, raw_isbn: str, titre: str, auteur: str, disponible: bool) -> dict:
        isbn, err = valider_isbn(raw_isbn)
        if isbn is None:
            raise ServiceError(err)


        t, err_t = valider_titre(titre)
        if t is None:
            raise ServiceError(err_t)


        a, err_a = valider_auteur(auteur)
        if a is None:
            raise ServiceError(err_a)


        if self.storage.get(isbn) is not None:
            raise ServiceError("Ce ISBN existe deja.")


        livre = {"isbn": isbn, "titre": t, "auteur": a, "disponible": bool(disponible)}
        try:
            self.storage.ajouter(livre)
        except StorageError as e:
            raise ServiceError(str(e))
        return livre


    def emprunter(self, raw_isbn: str) -> dict:
        livre = self._trouver_isbn(raw_isbn)
        if livre is None:
            raise ServiceError("Livre introuvable.")
        if not livre["disponible"]:
            raise ServiceError("Le livre est deja emprunte.")
        try:
            self.storage.maj_disponible(livre["isbn"], False)
        except StorageError as e:
            raise ServiceError(str(e))
        livre["disponible"] = False
        return livre


    def rendre(self, raw_isbn: str) -> dict:
        livre = self._trouver_isbn(raw_isbn)
        if livre is None:
            raise ServiceError("Livre introuvable.")
        if livre["disponible"]:
            raise ServiceError("Le livre est deja disponible.")
        try:
            self.storage.maj_disponible(livre["isbn"], True)
        except StorageError as e:
            raise ServiceError(str(e))
        livre["disponible"] = True
        return livre


    def supprimer(self, raw_isbn: str) -> None:
        livre = self._trouver_isbn(raw_isbn)
        if livre is None:
            raise ServiceError("Livre introuvable.")
        if not livre["disponible"]:
            raise ServiceError("Suppression refusee: livre actuellement emprunte.")
        try:
            ok = self.storage.supprimer(livre["isbn"])
            if not ok:
                raise ServiceError("Livre introuvable.")
        except StorageError as e:
            raise ServiceError(str(e))


    def modifier(self, raw_isbn: str, titre: Optional[str], auteur: Optional[str], disponible: Optional[bool]) -> dict:
        livre = self._trouver_isbn(raw_isbn)
        if livre is None:
            raise ServiceError("Livre introuvable.")
        champs = {}
        if titre is not None:
            t, err_t = valider_titre(titre)
            if t is None:
                raise ServiceError(err_t)
            champs["titre"] = t
        if auteur is not None:
            a, err_a = valider_auteur(auteur)
            if a is None:
                raise ServiceError(err_a)
            champs["auteur"] = a
        if disponible is not None:
            champs["disponible"] = bool(disponible)
        if not champs:
            return livre
        try:
            updated = self.storage.maj(livre["isbn"], champs)
        except StorageError as e:
            raise ServiceError(str(e))
        return updated


    def tous(self) -> List[dict]:
        try:
            return self.storage.tous()
        except StorageError as e:
            raise ServiceError(str(e))


    def disponibles(self) -> List[dict]:
        return [l for l in self.tous() if l["disponible"]]


    def rechercher_isbn(self, raw_isbn: str) -> Optional[dict]:
        return self._trouver_isbn(raw_isbn)


    def rechercher_texte(self, query: str) -> List[dict]:
        q = normaliser_texte(query)
        if len(q) < 2:
            return []
        try:
            return self.storage.rechercher_texte(q)
        except StorageError as e:
            raise ServiceError(str(e))


    def _trouver_isbn(self, raw_isbn: str) -> Optional[dict]:
        isbn, _ = valider_isbn(raw_isbn)
        if isbn is None:
            return None
        return self.storage.get(isbn)


