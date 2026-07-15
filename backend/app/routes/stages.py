from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_session
from app.models.models import Stage, User
from app.routes.auth import get_current_user
from app.routes.applications import _get_owned_application
from app.schemas.stages import StageCreate, StageResponse, StageUpdate


router = APIRouter(tags=["stages"])

@router.post(
    "/applications/{application_id}/stages",
    response_model=StageResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_stage(
    application_id: UUID,
    payload: StageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Confirm the application exists and belongs to the current user
    _get_owned_application(db, application_id, current_user.id)
    
    stage = Stage(
        application_id=application_id,
        type=payload.type,
        outcome=payload.outcome,
        notes=payload.notes,
        scheduled_at=payload.scheduled_at,
        completed_at=payload.completed_at
    )
    db.add(stage)
    db.commit()
    db.refresh(stage)
    return stage


@router.get(
    "/applications/{application_id}/stages",
    response_model=List[StageResponse]
)
def list_stages(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    application = _get_owned_application(db, application_id, current_user.id)
    return application.stages


@router.get("/stages/{stage_id}", response_model=StageResponse)
def get_stage(
    stage_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    return _get_owned_stage(db, stage_id, current_user.id)


@router.patch("/stages/{stage_id}", response_model=StageResponse)
def update_stage(
    stage_id: UUID,
    payload: StageUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    stage = _get_owned_stage(db, stage_id, current_user.id)
    
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(stage, field, value)
    
    db.commit()
    db.refresh(stage)
    return stage


@router.delete("/stages/{stage_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stage(
    stage_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    stage = _get_owned_stage(db, stage_id, current_user.id)
    db.delete(stage)
    db.commit()


def _get_owned_stage(db: Session, stage_id: UUID, user_id: UUID) -> Stage:
    """
    Returns a Stage that is owned by the provided user.

    Args:
        db (Session): Database session object.
        stage_id (UUID): ID of the application stage.
        user_id (UUID): ID of the user who owns the stage.

    Raises:
        HTTPException: Stage is not found or the stage is not owned by the user.

    Returns:
        Stage: The user-owned Stage.
    """
    stage = db.query(Stage).filter(Stage.id == stage_id).one_or_none()
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )
    if stage.application.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this stage",
        )
    return stage