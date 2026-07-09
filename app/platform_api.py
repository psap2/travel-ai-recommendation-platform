from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field

from app.repository import search_listings
from app.service import recommend
from app.suggestions import suggest
from app.resilient import generate_with_retry
from app.itinerary_schema import Itinerary
from app.events import record_interaction
from app.metrics import time_stage, metrics_text

app = FastAPI(title="AI Travel Platform")


class TripRequest(BaseModel):
    user_id: str
    query: str = Field(min_length=1)
    city: str
    days: int = Field(ge=1, le=14)
    max_price: float = Field(gt=0)
    liked_tags: list[str] = Field(default_factory=list)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/metrics")
async def metrics() -> Response:
    return Response(metrics_text(), media_type="text/plain")


@app.post("/trips/plan")
async def plan_trip(body: TripRequest) -> dict:
    """One call: discover → rank → suggest → plan. The product flow."""
    with time_stage("search"):
        discovery = search_listings(body.query, body.max_price, body.liked_tags)

    with time_stage("rank"):
        ranked = recommend(
            body.user_id, body.city, body.max_price, set(body.liked_tags), limit=8
        )
    if not ranked:
        raise HTTPException(status_code=404, detail="no stays to plan around")

    with time_stage("suggest"):
        pitch = suggest(body.city, body.liked_tags, ranked)

    try:
        with time_stage("llm"):
            itinerary: Itinerary | None = generate_with_retry(
                body.city, body.days, body.liked_tags, ranked
            )
    except RuntimeError:
        itinerary = None  # graceful degradation: still return ranked stays

    record_interaction(body.user_id, [r["id"] for r in ranked], action="view")
    return {
        "discovery": discovery[:10],
        "recommended_stays": ranked,
        "suggestion": pitch,
        "itinerary": itinerary.model_dump() if itinerary else None,
        "degraded": itinerary is None,
    }
