"""Career recommendation endpoint."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import CompatibilityAnalysis
from app.schemas.schemas import CareerRecommendationsResponse, Recommendation
from app.services.career_service import get_recommendations

router = APIRouter(prefix="/career", tags=["Career"])
logger = logging.getLogger(__name__)


@router.get("/recommendations/{analysis_id}", response_model=CareerRecommendationsResponse)
async def get_career_recommendations(analysis_id: int, db: Session = Depends(get_db)):
    """Return deterministic career recommendations for an analysis."""
    analysis = db.query(CompatibilityAnalysis).filter(CompatibilityAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "ANALYSIS_NOT_FOUND", "message": f"Analysis {analysis_id} not found."},
        )
    recommendations = get_recommendations(analysis)
    return CareerRecommendationsResponse(
        analysis_id=analysis_id,
        recommendations=[Recommendation(**r) for r in recommendations],
    )
