"""DeepWiki MCP endpoints — isolated AI assistance layer."""

import logging
from fastapi import APIRouter, HTTPException, status
from app.integrations.deepwiki import ask_question, get_wiki_contents, get_wiki_structure
from app.schemas.schemas import (
    DeepWikiAskRequest, DeepWikiAskResponse,
    DeepWikiContentsResponse, DeepWikiStructureResponse,
)

router = APIRouter(prefix="/deepwiki", tags=["DeepWiki AI"])
logger = logging.getLogger(__name__)

_UNAVAILABLE = {
    "code": "DEEPWIKI_UNAVAILABLE",
    "message": "DeepWiki is unavailable or has not indexed this repository. Try again later.",
}


@router.get("/{owner}/{repo}/structure", response_model=DeepWikiStructureResponse)
async def get_structure(owner: str, repo: str):
    """Retrieve repository documentation structure via DeepWiki."""
    result, error = await get_wiki_structure(owner, repo)
    if error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "DEEPWIKI_UNAVAILABLE", "message": error})
    return DeepWikiStructureResponse(owner=owner, repository=repo, structure=result)


@router.get("/{owner}/{repo}/contents", response_model=DeepWikiContentsResponse)
async def get_contents(owner: str, repo: str):
    """Retrieve full repository documentation via DeepWiki."""
    result, error = await get_wiki_contents(owner, repo)
    if error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "DEEPWIKI_UNAVAILABLE", "message": error})
    return DeepWikiContentsResponse(owner=owner, repository=repo, contents=result)


@router.post("/{owner}/{repo}/ask", response_model=DeepWikiAskResponse)
async def ask_repo_question(owner: str, repo: str, request: DeepWikiAskRequest):
    """Ask a natural-language question about a repository via DeepWiki."""
    result, error = await ask_question(owner, repo, request.question)
    if error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "DEEPWIKI_UNAVAILABLE", "message": error})
    return DeepWikiAskResponse(
        owner=owner,
        repository=repo,
        question=request.question,
        answer=str(result),
        source="DeepWiki",
    )
