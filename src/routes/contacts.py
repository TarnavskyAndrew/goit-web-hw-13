from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_limiter.depends import RateLimiter

from src.database.db import get_db
from src.repository import contacts as repo_contacts
from src.schemas import ContactCreate, ContactUpdate, ContactResponse
from src.database.models import User
from src.services.auth import auth_service

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get(
    "/",
    response_model=List[ContactResponse],
    dependencies=[Depends(RateLimiter(times=50, seconds=60))],
)  # ≤100 запітів за хвилину
async def get_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    return await repo_contacts.get_contacts(skip, limit, current_user, db)


@router.get(
    "/search",
    response_model=List[ContactResponse],
    dependencies=[Depends(RateLimiter(times=50, seconds=60))],  # ≤50 запітів за хвилину
)
async def search_contacts(
    q: str = Query(..., description="Search by first name, last name, or email"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    return await repo_contacts.search_contacts(q, current_user, db)


@router.get("/upcoming-birthdays", response_model=List[ContactResponse])
async def get_upcoming_birthdays(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    return await repo_contacts.get_upcoming_birthdays(days, current_user, db)


@router.get(
    "/{contact_id}",
    response_model=ContactResponse,
    dependencies=[Depends(RateLimiter(times=50, seconds=60))],  # ≤50 запітів за хвилину
)
async def get_contact(
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    contact = await repo_contacts.get_contact(contact_id, current_user, db)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post(
    "/",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],  # ≤5 запитів за хвилину
)
# @router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    return await repo_contacts.create_contact(body, current_user, db)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactUpdate,
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    contact = await repo_contacts.update_contact(contact_id, body, current_user, db)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],  # ≤5 запитів за хвилину
)
async def delete_contact(
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    ok = await repo_contacts.delete_contact(contact_id, current_user, db)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return None
