from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.assessment import Assessment
from app.models.user import User
from app.schemas.assessment import AssessmentCreateRequest
from app.schemas.assessment import AssessmentResponse
from app.schemas.assessment import AssessmentStatusResponse
from app.schemas.assessment import AssessmentSubmitResponse

router=APIRouter(
    prefix="/assessment",
    tags=['Assessment'],
)
@router.post("/submit",response_model=AssessmentSubmitResponse,status_code=status.HTTP_201_CREATED,)
def submit_assessment(
    payload: AssessmentCreateRequest,
    current_user: User = Depends(get_current_user),
    db:Session=Depends(get_db),
):
    existing_assessment=(
        db.query(Assessment)
        .filter(Assessment.user_id==current_user.id)
        .first()
    )
    if existing_assessment:
        existing_assessment.social_situation=payload.social_situation
        existing_assessment.current_goal=payload.current_goal
        existing_assessment.self_improvement_consistency = (
            payload.self_improvement_consistency
        )
        existing_assessment.biggest_obstacle = (
            payload.biggest_obstacle
        )
        db.commit()
        return AssessmentSubmitResponse(
            message="Assessment updated successfully",
            assessment_completed=True,
        )
    assessment=Assessment(
        user_id=current_user.id,
        social_situation=payload.social_situation,
        current_goal=payload.current_goal,
        self_improvement_consistency=payload.self_improvement_consistency,
        biggest_obstacle=payload.biggest_obstacle,
    )
    db.add(assessment)
    db.commit()
    return AssessmentSubmitResponse(
        message="Assessment submitted successfully",
        assessment_completed=True
    )

@router.get("/status",response_model=AssessmentStatusResponse,)
def assessment_status(
    current_user:User=Depends(get_current_user),
    db:Session=Depends(get_db),
):
    assessment=(
        db.query(Assessment)
        .filter(Assessment.user_id==current_user.id)
        .first()
    )
    return AssessmentStatusResponse(assessment_completed=assessment is not None)

@router.get("/me",response_model=AssessmentResponse)
def get_my_assessment(current_user: User=Depends(get_current_user),db:Session=Depends(get_db)):
    assessment=(
        db.query(Assessment).filter(Assessment.user_id==current_user.id).first()
    )
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )
    return assessment