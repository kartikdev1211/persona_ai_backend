from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.persona_report import PersonaReportResponse
from app.services.persona_report_service import generate_and_save_persona_report
from app.services.persona_report_service import get_persona_report

router=APIRouter(
    prefix="/persona",
    tags=['Persona Report'],
)
@router.post(
    "/report/generate",
    response_model=PersonaReportResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_report(current_user: User = Depends(get_current_user),db: Session = Depends(get_db),):
    existing=get_persona_report(user_id=current_user.id,db=db)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Persona report already exists for this user.",
        )
    try:
        report = generate_and_save_persona_report(
            user_id=current_user.id,
            db=db,
        )
    except ValueError as e:
        error=str(e)
        if error == "assessment_not_found":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assessment not completed. Please complete your assessment before generating a report.",
            )
        if error == "persona_not_found":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Persona setup not completed. Please complete your persona setup before generating a report.",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating the report.",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to generate report. Gemini API call failed.",
        )
    return report

@router.get(
    "/report",
    response_model=PersonaReportResponse,
)
def get_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = get_persona_report(user_id=current_user.id, db=db)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona report not found. Please generate your report first.",
        )
    return report
