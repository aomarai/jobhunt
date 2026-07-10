from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_session
from app.models.models import Application, Company, User
from app.routes.auth import get_current_user
from app.schemas.application import ApplicationCreate, ApplicationResponse, ApplicationUpdate


router = APIRouter(prefix="/applications", tags=["applications"])

@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    payload: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    company = db.query(Company).filter(Company.id == payload.company_id).one_or_none()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
        
    application = Application(
        user_id=current_user.id,
        company_id=payload.company_id,
        job_id=payload.job_id,
        job_title=payload.job_title,
        job_url=payload.job_url,
        status=payload.status,
        notes=payload.notes
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("", response_model=List[ApplicationResponse])
def list_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    return db.query(Application).filter(Application.user_id == current_user.id).order_by(Application.applied_at.desc).all()


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    return _get_owned_application(db, application_id, current_user.id)


@router.patch("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: UUID,
    payload: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session=Depends(get_session)
):
    application = _get_owned_application(db, application_id, current_user.id)
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(application, field, value)
    
    db.commit()
    db.refresh(application)
    return application


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    application = _get_owned_application(db, application_id, current_user.id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    if application.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this application"
        )
    return application


def _get_owned_application(
    db: Session,
    application_id: UUID,
    user_id: UUID
):
    application = db.query(Application).filter(Application.id == application_id).one()
    if not application:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Application not found"
        )
    if application.user_id != user_id:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to access this application"
        )
    return application