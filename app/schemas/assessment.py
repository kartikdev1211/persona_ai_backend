from pydantic import BaseModel

class AssessmentCreateRequest(BaseModel):
    social_situation: str
    current_goal: str
    self_improvement_consistency: str
    biggest_obstacle: str

class AssessmentResponse(BaseModel):
    social_situation: str
    current_goal: str
    self_improvement_consistency: str
    biggest_obstacle: str

    model_config = {
        "from_attributes": True
    }

class AssessmentStatusResponse(BaseModel):
    assessment_completed: bool
    is_persona_completed: bool
    is_report_generated: bool

class AssessmentSubmitResponse(BaseModel):
    message: str
    assessment_completed: bool