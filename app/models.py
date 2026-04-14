from pydantic import BaseModel, Field
from typing import Optional

class LivreBase(BaseModel):
    isbn: str = Field(..., description="ISBN du livre (10 ou 13 chiffres)", example="9782070360248")
    titre: str = Field(..., description="Titre du livre", example="Le Petit Prince")
    auteur: str = Field(..., description="Auteur du livre", example="Antoine de Saint-Exupery")
    disponible: bool = Field(True, description="Disponibilite du livre", example=True)

class LivreCreate(LivreBase):
    pass
class LivreUpdate(BaseModel):
    titre: Optional[str] = Field(None, description="Nouveau titre")
    auteur: Optional[str] = Field(None, description="Nouvel auteur")
    disponible: Optional[bool] = Field(None, description="Nouvelle disponibilite")

class Livre(LivreBase):
    pass

class MessageResponse(BaseModel):
    message: str = Field(..., example="Operation reussie")

class ErrorResponse(BaseModel):
    detail: str = Field(..., example="Livre introuvable")