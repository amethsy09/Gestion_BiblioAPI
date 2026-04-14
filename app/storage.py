import os
from typing import Optional, List
from threading import Lock

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()


class StorageError(Exception):
    pass


class BibliothequeStorage:
    def __init__(self, _json_path: str = None):
        self._lock = Lock()
        self._db_url = os.getenv("DATABASE_URL")
        self._init_db()

    # ── connexion ──────────────────────────────────────────────────────────────

    def _connect(self):
        try:
            return psycopg2.connect(self._db_url, cursor_factory=psycopg2.extras.RealDictCursor)
        except psycopg2.OperationalError as e:
            raise StorageError(f"Connexion DB impossible : {e}")

    # ── initialisation de la table ─────────────────────────────────────────────

    def _init_db(self) -> None:
        sql = """
        CREATE TABLE IF NOT EXISTS livres (
            isbn            VARCHAR(20)      PRIMARY KEY,
            titre           VARCHAR(200)     NOT NULL,
            auteur          VARCHAR(100)     NOT NULL,
            disponible      BOOLEAN          NOT NULL DEFAULT TRUE,
            annee_publication INTEGER,
            editeur         VARCHAR(100),
            nombre_pages    INTEGER
        );
        """
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
                conn.commit()
        except psycopg2.Error as e:
            raise StorageError(f"Initialisation DB : {e}")

    # ── conversion ─────────────────────────────────────────────────────────────

    @staticmethod
    def _row_to_dict(row) -> dict:
        return dict(row)

    # ── CRUD ───────────────────────────────────────────────────────────────────

    def ajouter(self, livre: dict) -> None:
        sql = """
        INSERT INTO livres
            (isbn, titre, auteur, disponible, annee_publication, editeur, nombre_pages)
        VALUES
            (%(isbn)s, %(titre)s, %(auteur)s, %(disponible)s,
             %(annee_publication)s, %(editeur)s, %(nombre_pages)s)
        """
        params = {
            "isbn": livre["isbn"],
            "titre": livre["titre"],
            "auteur": livre["auteur"],
            "disponible": livre.get("disponible", True),
            "annee_publication": livre.get("annee_publication"),
            "editeur": livre.get("editeur"),
            "nombre_pages": livre.get("nombre_pages"),
        }
        with self._lock:
            try:
                with self._connect() as conn:
                    with conn.cursor() as cur:
                        cur.execute(sql, params)
                    conn.commit()
            except psycopg2.IntegrityError:
                raise StorageError("Cet ISBN existe déjà dans la base.")
            except psycopg2.Error as e:
                raise StorageError(f"Erreur insertion : {e}")

    def get(self, isbn: str) -> Optional[dict]:
        with self._lock:
            try:
                with self._connect() as conn:
                    with conn.cursor() as cur:
                        cur.execute("SELECT * FROM livres WHERE isbn = %s", (isbn,))
                        row = cur.fetchone()
                        return self._row_to_dict(row) if row else None
            except psycopg2.Error as e:
                raise StorageError(f"Erreur lecture : {e}")

    def maj(self, isbn: str, champs: dict) -> Optional[dict]:
        if not champs:
            return self.get(isbn)
        colonnes = ", ".join(f"{k} = %({k})s" for k in champs)
        sql = f"UPDATE livres SET {colonnes} WHERE isbn = %(isbn)s"
        params = {**champs, "isbn": isbn}
        with self._lock:
            try:
                with self._connect() as conn:
                    with conn.cursor() as cur:
                        cur.execute(sql, params)
                    conn.commit()
                return self.get(isbn)
            except psycopg2.Error as e:
                raise StorageError(f"Erreur mise à jour : {e}")

    def maj_disponible(self, isbn: str, disponible: bool) -> bool:
        with self._lock:
            try:
                with self._connect() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "UPDATE livres SET disponible = %s WHERE isbn = %s RETURNING isbn",
                            (disponible, isbn)
                        )
                        updated = cur.fetchone()
                    conn.commit()
                    return updated is not None
            except psycopg2.Error as e:
                raise StorageError(f"Erreur mise à jour disponibilité : {e}")

    def supprimer(self, isbn: str) -> bool:
        with self._lock:
            try:
                with self._connect() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "DELETE FROM livres WHERE isbn = %s RETURNING isbn",
                            (isbn,)
                        )
                        deleted = cur.fetchone()
                    conn.commit()
                    return deleted is not None
            except psycopg2.Error as e:
                raise StorageError(f"Erreur suppression : {e}")

    def tous(self) -> List[dict]:
        with self._lock:
            try:
                with self._connect() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "SELECT * FROM livres ORDER BY LOWER(auteur), LOWER(titre)"
                        )
                        return [self._row_to_dict(r) for r in cur.fetchall()]
            except psycopg2.Error as e:
                raise StorageError(f"Erreur lecture : {e}")

    def rechercher_texte(self, query: str) -> List[dict]:
        with self._lock:
            try:
                with self._connect() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """SELECT * FROM livres 
                               WHERE LOWER(titre) LIKE %s OR LOWER(auteur) LIKE %s
                               ORDER BY LOWER(auteur), LOWER(titre)""",
                            (f"%{query.lower()}%", f"%{query.lower()}%")
                        )
                        return [self._row_to_dict(r) for r in cur.fetchall()]
            except psycopg2.Error as e:
                raise StorageError(f"Erreur recherche : {e}")