from datetime import date, timedelta
from typing import List
from sqlalchemy import select, or_, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from src.database.models import Contact, User
from src.schemas import ContactCreate, ContactUpdate


# Функції для роботи з контактами в БД


# Отримати всі контакти
async def get_contacts(
    skip: int, limit: int, user: User, db: AsyncSession
) -> List[Contact]:
    result = await db.execute(
        select(Contact).where(Contact.user_id == user.id).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


# Отримати контакт по id
async def get_contact(contact_id: int, user: User, db: AsyncSession) -> Contact | None:
    result = await db.execute(
        select(Contact).where(
            and_(Contact.id == contact_id, Contact.user_id == user.id)
        )
    )
    return result.scalar_one_or_none()


# Створити новий контакт
async def create_contact(body: ContactCreate, user: User, db: AsyncSession) -> Contact:
    contact = Contact(**body.model_dump(), user_id=user.id)
    db.add(contact)
    try:
        await db.commit()
        await db.refresh(contact)
        return contact
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already exists"
        )


# Оновити контакт
async def update_contact(
    contact_id: int, body: ContactUpdate, user: User, db: AsyncSession
) -> Contact | None:
    result = await db.execute(
        select(Contact).where(
            and_(Contact.id == contact_id, Contact.user_id == user.id)
        )
    )
    contact = result.scalar_one_or_none()
    if contact:
        for field, value in body.model_dump(exclude_unset=True).items():
            setattr(contact, field, value)
        await db.commit()
        await db.refresh(contact)
    return contact


# Видалити контакт
async def delete_contact(contact_id: int, user: User, db: AsyncSession) -> bool:
    result = await db.execute(
        select(Contact).where(
            and_(Contact.id == contact_id, Contact.user_id == user.id)
        )
    )
    contact = result.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


# Пошук по імені, прізвищу та email
async def search_contacts(q: str, user: User, db: AsyncSession):
    like = f"%{q}%"
    res = await db.execute(
        select(Contact).where(
            and_(
                Contact.user_id == user.id,
                or_(
                    Contact.first_name.ilike(like),
                    Contact.last_name.ilike(like),
                    Contact.email.ilike(like),
                ),
            )
        )
    )
    return list(res.scalars().all())


# Список контактів з ДР в найбижчі N днів
async def get_upcoming_birthdays(days: int, user: User, db: AsyncSession):
    today = date.today()
    end_date = today + timedelta(days=days)

    today_md = today.strftime("%m-%d")
    end_md = end_date.strftime("%m-%d")

    if today_md <= end_md:
        # без переходу через Новий рік
        stmt = select(Contact).where(
            and_(
                Contact.user_id == user.id,
                func.to_char(Contact.birthday, "MM-DD").between(today_md, end_md),
            )
        )
    else:
        # з переходом через Новий рік (наприклад, 28.12 → 05.01)
        stmt = select(Contact).where(
            and_(
                Contact.user_id == user.id,
                or_(
                    func.to_char(Contact.birthday, "MM-DD") >= today_md,
                    func.to_char(Contact.birthday, "MM-DD") <= end_md,
                ),
            )
        )

    res = await db.execute(stmt)
    return list(res.scalars().all())
