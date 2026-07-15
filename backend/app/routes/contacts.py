from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_session
from app.models.models import Contact, User
from app.routes.auth import get_current_user
from app.routes.applications import _get_owned_application
from app.schemas.contacts import ContactCreate, ContactUpdate, ContactResponse

router = APIRouter(tags=["contacts"])


@router.post(
    "/applications/{application_id}/contacts",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_contact(
    application_id: UUID,
    payload: ContactCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    application = _get_owned_application(db, application_id, current_user.id)

    contact = Contact(
        application_id=application_id,
        company_id=application.company_id,  # derived, not client-supplied
        name=payload.name,
        role=payload.role,
        email=payload.email,
        linkedin_url=payload.linkedin_url,
        notes=payload.notes,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@router.get(
    "/applications/{application_id}/contacts",
    response_model=List[ContactResponse],
)
def list_contacts(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    application = _get_owned_application(db, application_id, current_user.id)
    return application.contacts


@router.get("/contacts/{contact_id}", response_model=ContactResponse)
def get_contact(
    contact_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    return _get_owned_contact(db, contact_id, current_user.id)


@router.patch("/contacts/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: UUID,
    payload: ContactUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    contact = _get_owned_contact(db, contact_id, current_user.id)

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(contact, field, value)

    db.commit()
    db.refresh(contact)
    return contact


@router.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    contact = _get_owned_contact(db, contact_id, current_user.id)
    db.delete(contact)
    db.commit()


def _get_owned_contact(db: Session, contact_id: UUID, user_id: UUID) -> Contact:
    contact = db.query(Contact).filter(Contact.id == contact_id).one_or_none()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    if contact.application.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this contact",
        )
    return contact