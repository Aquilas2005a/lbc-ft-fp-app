from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.seed import seed_demo_data
from app.db.session import get_db

router = APIRouter(prefix="/seed", tags=["seed"])


@router.post("", status_code=status.HTTP_200_OK)
def trigger_seed(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    if settings.app_env != "development":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Le seed est disponible uniquement en environnement de developpement.",
        )

    counts = seed_demo_data(db)
    return {
        "message": "Donnees de demonstration injectees avec succes.",
        "entities_created": counts,
    }
