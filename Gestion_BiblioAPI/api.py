from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List


from .models import LivreCreate, LivreUpdate, Livre, MessageResponse, ErrorResponse
from .storage import BibliothequeStorage
from .services import BibliothequeService, ServiceError




app = FastAPI(
    title="API Gestion de Bibliotheque",
    description="API REST pour la gestion d'une bibliotheque de livres avec stockage JSON",
    version="1.0.0",
    contact={"name": "Equipe Bibliotheque", "email": "diouf@tioukh.coding"},
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


storage = BibliothequeStorage("bibliotheque.json")
service = BibliothequeService(storage)


@app.get("/", tags=["Racine"], summary="Page d'accueil de l'API")
def racine():
    return {
        "message": "Bienvenue sur l'API Gestion de Bibliotheque",
        "documentation": "/docs",
        "redoc": "/redoc",
        "version": "1.0.0",
    }



@app.get(
    "/livres",
    response_model=List[Livre],
    tags=["Livres"],
    summary="Lister tous les livres",
    description="Retourne la liste complete des livres tries par auteur puis titre.",
)
def lister_livres():
    try:
        return service.tous()
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.get(
    "/livres/disponibles",
    response_model=List[Livre],
    tags=["Livres"],
    summary="Lister uniquement les livres disponibles",
)
def lister_disponibles():
    try:
        return service.disponibles()
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.get(
    "/livres/recherche",
    response_model=List[Livre],
    tags=["Recherche"],
    summary="Rechercher des livres par texte",
    description="Recherche dans le titre et l'auteur (minimum 2 caracteres).",
)
def rechercher(q: str):
    try:
        return service.rechercher_texte(q)
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))




@app.get(
    "/livres/{isbn}",
    response_model=Livre,
    tags=["Livres"],
    summary="Recuperer un livre par ISBN",
    responses={404: {"model": ErrorResponse, "description": "Livre introuvable"}},
)
def obtenir_livre(isbn: str):
    livre = service.rechercher_isbn(isbn)
    if livre is None:
        raise HTTPException(status_code=404, detail="Livre introuvable.")
    return livre




@app.post(
    "/livres",
    response_model=Livre,
    status_code=status.HTTP_201_CREATED,
    tags=["Livres"],
    summary="Ajouter un nouveau livre",
    responses={400: {"model": ErrorResponse, "description": "Donnees invalides"}},
)
def creer_livre(livre: LivreCreate):
    try:
        return service.ajouter_livre(livre.isbn, livre.titre, livre.auteur, livre.disponible)
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))




@app.put(
    "/livres/{isbn}",
    response_model=Livre,
    tags=["Livres"],
    summary="Modifier un livre existant",
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse, "description": "Livre introuvable"},
    },
)
def modifier_livre(isbn: str, maj: LivreUpdate):
    try:
        return service.modifier(isbn, maj.titre, maj.auteur, maj.disponible)
    except ServiceError as e:
        if "introuvable" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))




@app.delete(
    "/livres/{isbn}",
    response_model=MessageResponse,
    tags=["Livres"],
    summary="Supprimer un livre",
    responses={
        400: {"model": ErrorResponse, "description": "Livre emprunte"},
        404: {"model": ErrorResponse, "description": "Livre introuvable"},
    },
)
def supprimer_livre(isbn: str):
    try:
        service.supprimer(isbn)
        return {"message": "Livre supprime avec succes."}
    except ServiceError as e:
        if "introuvable" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))




@app.post(
    "/livres/{isbn}/emprunter",
    response_model=Livre,
    tags=["Operations"],
    summary="Emprunter un livre",
    responses={
        400: {"model": ErrorResponse, "description": "Livre deja emprunte"},
        404: {"model": ErrorResponse, "description": "Livre introuvable"},
    },
)
def emprunter_livre(isbn: str):
    try:
        return service.emprunter(isbn)
    except ServiceError as e:
        if "introuvable" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))




@app.post(
    "/livres/{isbn}/rendre",
    response_model=Livre,
    tags=["Operations"],
    summary="Rendre un livre emprunte",
    responses={
        400: {"model": ErrorResponse, "description": "Livre deja disponible"},
        404: {"model": ErrorResponse, "description": "Livre introuvable"},
    },
)
def rendre_livre(isbn: str):
    try:
        return service.rendre(isbn)
    except ServiceError as e:
        if "introuvable" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))


