from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.account import Account
from app.models.client import Client
from app.schemas.account import AccountCreate, AccountRead, AccountUpdate

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
def create_account(
    account_in: AccountCreate,
    db: Session = Depends(get_db),
) -> AccountRead:
    client = (
        db.query(Client).filter(Client.id == account_in.client_id, Client.deleted_at.is_(None)).first()
    )
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client ID {account_in.client_id} introuvable.",
        )

    existing_num = db.query(Account).filter(Account.account_number == account_in.account_number).first()
    if existing_num:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Le numero de compte {account_in.account_number} existe deja.",
        )

    account = Account(**account_in.model_dump())
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.get("", response_model=List[AccountRead])
def list_accounts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    client_id: Optional[int] = None,
    db: Session = Depends(get_db),
) -> List[AccountRead]:
    query = db.query(Account)
    if client_id is not None:
        query = query.filter(Account.client_id == client_id)

    return query.offset(skip).limit(limit).all()


@router.get("/{account_id}", response_model=AccountRead)
def get_account(
    account_id: int,
    db: Session = Depends(get_db),
) -> AccountRead:
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compte ID {account_id} introuvable.",
        )
    return account


@router.put("/{account_id}", response_model=AccountRead)
def update_account(
    account_id: int,
    account_in: AccountUpdate,
    db: Session = Depends(get_db),
) -> AccountRead:
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compte ID {account_id} introuvable.",
        )

    update_data = account_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(account, field, value)

    db.commit()
    db.refresh(account)
    return account
