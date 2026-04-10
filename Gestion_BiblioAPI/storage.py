import json
import os
from typing import Optional, List
from threading import Lock


class StorageError(Exception):
    pass


class BibliothequeStorage:
    def __init__(self, json_path: str = "bibliotheque.json"):
        self.json_path = json_path
        self._lock = Lock()
        self._init_file()


    def _init_file(self) -> None:
        if not os.path.exists(self.json_path):
            try:
                with open(self.json_path, "w", encoding="utf-8") as f:
                    json.dump({"livres": []}, f, ensure_ascii=False, indent=2)
            except OSError as e:
                raise StorageError(f"Impossible de creer le fichier JSON: {e}")


    def _lire_donnees(self) -> dict:
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "livres" not in data or not isinstance(data["livres"], list):
                    return {"livres": []}
                return data
        except (OSError, json.JSONDecodeError) as e:
            raise StorageError(f"Erreur lecture JSON: {e}")


    def _ecrire_donnees(self, data: dict) -> None:
        try:
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError as e:
            raise StorageError(f"Erreur ecriture JSON: {e}")


    def ajouter(self, livre: dict) -> None:
        with self._lock:
            data = self._lire_donnees()
            for l in data["livres"]:
                if l["isbn"] == livre["isbn"]:
                    raise StorageError("Ce ISBN existe deja dans la base.")
            data["livres"].append(livre)
            self._ecrire_donnees(data)


    def get(self, isbn: str) -> Optional[dict]:
        with self._lock:
            data = self._lire_donnees()
            for l in data["livres"]:
                if l["isbn"] == isbn:
                    return l
            return None


    def maj(self, isbn: str, champs: dict) -> Optional[dict]:
        with self._lock:
            data = self._lire_donnees()
            for i, l in enumerate(data["livres"]):
                if l["isbn"] == isbn:
                    data["livres"][i].update(champs)
                    self._ecrire_donnees(data)
                    return data["livres"][i]
            return None


    def maj_disponible(self, isbn: str, disponible: bool) -> bool:
        with self._lock:
            data = self._lire_donnees()
            for i, l in enumerate(data["livres"]):
                if l["isbn"] == isbn:
                    data["livres"][i]["disponible"] = disponible
                    self._ecrire_donnees(data)
                    return True
            return False


    def supprimer(self, isbn: str) -> bool:
        with self._lock:
            data = self._lire_donnees()
            avant = len(data["livres"])
            data["livres"] = [l for l in data["livres"] if l["isbn"] != isbn]
            if len(data["livres"]) == avant:
                return False
            self._ecrire_donnees(data)
            return True


    def tous(self) -> List[dict]:
        with self._lock:
            data = self._lire_donnees()
            return sorted(data["livres"], key=lambda x: (x["auteur"].lower(), x["titre"].lower()))


    def rechercher_texte(self, query: str) -> List[dict]:
        with self._lock:
            data = self._lire_donnees()
            q = query.lower()
            resultats = [
                l for l in data["livres"]
                if q in l["titre"].lower() or q in l["auteur"].lower()
            ]
            return sorted(resultats, key=lambda x: (x["auteur"].lower(), x["titre"].lower()))