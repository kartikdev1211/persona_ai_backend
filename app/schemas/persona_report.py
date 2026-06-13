from pydantic import BaseModel
class RoadmapStepSchema(BaseModel):
    title: str
    description: str

class PersonaReportResponse(BaseModel):
    confidence_score: float
    discipline_score: float
    social_growth_score: float
    strengths: list[str]
    weaknesses: list[str]
    roadmap: list[RoadmapStepSchema]