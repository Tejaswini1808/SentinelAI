from fastapi import APIRouter

from app.models import SearchRequest
from app.rag import retrieval

router = APIRouter(tags=["search"])


@router.post("/search")
def search(request: SearchRequest):
    return {"results": retrieval.search(request.query, top_k=request.top_k, source_filter=request.source_filter)}
