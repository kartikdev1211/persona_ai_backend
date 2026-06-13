import json

from google import genai
from google.genai import types
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.assessment import Assessment
from app.models.persona_profile import PersonaProfile
from app.models.persona_report import PersonaReport

_client=genai.Client(api_key=settings.GEMINI_API_KEY)
_SYSTEM_PROMPT="""You are a professional personal development analyst. 
Your job is to analyze a user's persona profile and self-assessment data, 
then generate a structured personality growth report.

You MUST respond with ONLY a valid JSON object. No markdown, no explanation, no extra text.
The JSON must strictly follow this schema:
{
  "confidence_score": <float between 0.0 and 1.0>,
  "discipline_score": <float between 0.0 and 1.0>,
  "social_growth_score": <float between 0.0 and 1.0>,
  "strengths": [<string>, <string>, <string>],
  "weaknesses": [<string>, <string>, <string>],
  "roadmap": [
    {"title": <string>, "description": <string>},
    {"title": <string>, "description": <string>},
    {"title": <string>, "description": <string>}
  ]
}

Rules:
- strengths must contain exactly 3 short strings (2-5 words each)
- weaknesses must contain exactly 3 short strings (2-5 words each)
- roadmap must contain exactly 3 steps, each with a title (2-5 words) and description (1 sentence, max 15 words)
- All scores must be realistic floats derived from the user's data
- Return ONLY the JSON object, nothing else
"""

def _build_user_prompt(
    assessment: Assessment,
    persona: PersonaProfile,
) -> str:
    return f"""Generate a personality growth report for the following user:

Persona Profile:
- Persona Name: {persona.persona_name}
- Confidence Level: {persona.confidence_level}
- Focus Goal: {persona.focus_goal}

Self-Assessment:
- Social Situation: {assessment.social_situation}
- Current Goal: {assessment.current_goal}
- Self-Improvement Consistency: {assessment.self_improvement_consistency}
- Biggest Obstacle: {assessment.biggest_obstacle}

Analyze all of the above and return the JSON report."""

def _call_gemini(prompt: str)-> dict:
    response=_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=_SYSTEM_PROMPT,
            temperature=0.4,
            response_mime_type="application/json",
        ),
    )
    raw_text=response.text.strip()
    return json.loads(raw_text)

def generate_and_save_persona_report(
    user_id: int,
    db: Session,
) -> dict:
    assessment = (
        db.query(Assessment)
        .filter(Assessment.user_id == user_id)
        .first()
    )
    if not assessment:
        raise ValueError("assessment_not_found")

    persona = (
        db.query(PersonaProfile)
        .filter(PersonaProfile.user_id == user_id)
        .first()
    )
    if not persona:
        raise ValueError("persona_not_found")

    prompt = _build_user_prompt(assessment, persona)
    report_dict = _call_gemini(prompt)

    report_record = PersonaReport(
        user_id=user_id,
        report_data=json.dumps(report_dict),
    )
    db.add(report_record)
    db.commit()
    db.refresh(report_record)

    return report_dict


def get_persona_report(
    user_id: int,
    db: Session,
) -> dict | None:
    report = (
        db.query(PersonaReport)
        .filter(PersonaReport.user_id == user_id)
        .first()
    )
    if not report:
        return None
    return json.loads(report.report_data)
