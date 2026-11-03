"""Interview preparation endpoints — generate questions and evaluate answers."""

import logging
from fastapi import APIRouter, HTTPException, status
from app.integrations.deepwiki import ask_question
from app.schemas.schemas import (
    InterviewEvaluateRequest, InterviewEvaluateResponse,
    InterviewGenerateRequest, InterviewGenerateResponse,
)

router = APIRouter(prefix="/interview", tags=["Interview Preparation"])
logger = logging.getLogger(__name__)

# Pre-built question prompts by difficulty
_QUESTION_PROMPTS = {
    "easy": (
        "Generate {n} beginner-friendly technical interview questions for a developer "
        "who built the repository '{repo}'. Focus on basic architecture, purpose, and technology choices. "
        "Return only the questions as a numbered list."
    ),
    "medium": (
        "Generate {n} technical interview questions for a developer who built the repository '{repo}'. "
        "Include questions about architecture, design patterns, API design, database decisions, and trade-offs. "
        "Return only the questions as a numbered list."
    ),
    "hard": (
        "Generate {n} advanced technical interview questions for a developer who built the repository '{repo}'. "
        "Include scalability, performance, failure modes, security, and system design trade-offs. "
        "Return only the questions as a numbered list."
    ),
}


def _parse_questions(raw: str, expected: int) -> list:
    """Extract question lines from a numbered list response."""
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    questions = []
    for line in lines:
        # Remove numbering like "1.", "1)", "Q1:", etc.
        import re
        cleaned = re.sub(r"^[\d]+[.):\s]+", "", line).strip()
        if cleaned:
            questions.append(cleaned)
    return questions[:expected] if questions else [raw]


@router.post("/generate", response_model=InterviewGenerateResponse)
async def generate_questions(request: InterviewGenerateRequest):
    """Generate repository-specific technical interview questions via DeepWiki."""
    prompt = _QUESTION_PROMPTS[request.difficulty].format(
        n=request.number_of_questions,
        repo=request.repository,
    )
    result, error = await ask_question(request.username, request.repository, prompt)
    if error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "DEEPWIKI_UNAVAILABLE", "message": error},
        )
    questions = _parse_questions(str(result), request.number_of_questions)
    return InterviewGenerateResponse(repository=request.repository, questions=questions)


@router.post("/evaluate", response_model=InterviewEvaluateResponse)
async def evaluate_answer(request: InterviewEvaluateRequest):
    """Evaluate a developer's interview answer using DeepWiki repository context."""
    eval_prompt = (
        f"I am preparing for a technical interview about the repository '{request.repository}'. "
        f"The question was: '{request.question}'. "
        f"My answer was: '{request.answer}'. "
        "Please evaluate my answer. Identify: 1) What I got right (strengths), "
        "2) What I missed or could improve, 3) A suggested better answer. "
        "Ground your feedback in the actual repository documentation if available."
    )
    result, error = await ask_question(request.owner, request.repository, eval_prompt)

    if error:
        return InterviewEvaluateResponse(
            feedback="DeepWiki could not evaluate this answer: " + error,
            strengths=[],
            improvements=["Try again when DeepWiki has indexed this repository."],
            context_available=False,
        )

    raw_feedback = str(result)
    return InterviewEvaluateResponse(
        feedback=raw_feedback,
        strengths=["Answer received — see full feedback above."],
        improvements=["Review the detailed feedback for improvement areas."],
        context_available=True,
    )
