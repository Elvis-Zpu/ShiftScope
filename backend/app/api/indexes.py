from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.index import Index
from app.schemas.index import IndexRead

router = APIRouter(prefix="/indexes", tags=["indexes"])


@router.get("", response_model=list[IndexRead])
def list_indexes(db: Session = Depends(get_db)):
    return db.query(Index).order_by(Index.id.desc()).all()